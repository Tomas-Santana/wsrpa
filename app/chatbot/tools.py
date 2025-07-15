
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
from heyoo import WhatsApp
import logging
from dotenv import load_dotenv
import tempfile
from typing import Optional

load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # --- 5. Create PDF (fpdf2) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Reporte de Ventas Detallado', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body_text):
        self.set_font('Helvetica', '', 10)
        self.multi_cell(0, 5, body_text)
        self.ln(5)

def generar_reporte_ventas(
    excel_file='files/ventas.csv',
    output_pdf='sales_report.pdf',
    start_date=None,
    end_date=None
):
    """
    Genera un reporte de ventas en PDF a partir de un archivo CSV, con opción de filtrar por rango de fechas.
    Parámetros:
        excel_file: str, ruta al archivo CSV
        output_pdf: str, nombre del archivo PDF de salida
        start_date: str o None, fecha inicial en formato 'YYYY-MM-DD' o None para no filtrar
        end_date: str o None, fecha final en formato 'YYYY-MM-DD' o None para no filtrar
    """
    tmp = tempfile.mkdtemp()
    try:
        df = pd.read_csv(excel_file)
        
    except FileNotFoundError:
        logging.error(f"File {excel_file} not found.")
        raise FileNotFoundError(f"File {excel_file} not found. Please check the path and filename.")

    df.columns = [col.strip() for col in df.columns]
    df = df.rename(columns={'Precio Venta sin IGV': 'Precio_Venta_sin_IGV',
                            'Precio Venta Real': 'Precio_Venta_Real',
                            'Costo Vehículo': 'Costo_Vehiculo',
                            'ID_Vehículo': 'ID_Vehiculo'})
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    numeric_cols = ['Costo_Vehiculo', 'Precio_Venta_sin_IGV', 'IGV', 'Precio_Venta_Real']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['Precio_Venta_Real'], inplace=True)

    if start_date:
        df = df[df['Fecha'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Fecha'] <= pd.to_datetime(end_date)]
    if df.empty:
        raise ValueError("No data available for the specified date range.")

    total_sales = df['Precio_Venta_Real'].sum()
    sales_by_seller = df.groupby('Vendedor')['Precio_Venta_Real'].sum().sort_values(ascending=False).head(10)
    sales_by_location = df.groupby('Sede')['Precio_Venta_Real'].sum().sort_values(ascending=False).head(10)
    sales_count_by_channel = df['Canal'].value_counts().sort_values(ascending=False)
    average_sale_value = df['Precio_Venta_Real'].mean()
    num_sales = len(df)
    avg_vehicle_cost = df['Costo_Vehiculo'].mean()

    
    get_sales_chart(sales_by_seller, 'skyblue', 'Recaudado Total por Vendedor', 'Vendedor', 'Recaudado (USD)', os.path.join(tmp, 'recaudado_vendedor.png'))
    
    get_sales_chart(sales_by_location, 'lightcoral', 'Recaudado Total por Sede', 'Sede', 'Recaudado (USD)', os.path.join(tmp, 'recaudado_sede.png'))

    get_sales_chart(sales_count_by_channel, 'lightgreen', 'Cantidad de Ventas por Canal', 'Canal', 'Cantidad de Ventas', os.path.join(tmp, 'ventas_por_canal.png'))    
    


    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Análisis de Ventas', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, "Este reporte presenta un análisis detallado de las ventas, incluyendo el rendimiento por vendedor, sede y canal de adquisición. Los datos provienen cubren el período de "
                    f"{df['Fecha'].min().strftime('%d/%m/%Y')} a {df['Fecha'].max().strftime('%d/%m/%Y')}.")
    pdf.ln(10)

    pdf.chapter_title('Resumen Ejecutivo')
    pdf.chapter_body(f"Total de ventas registradas: {num_sales} transacciones.\n"
                     f"Recaudación total: ${total_sales:,.2f}\n"
                     f"Valor promedio por venta: ${average_sale_value:,.2f}\n"
                     f"Costo promedio del vehículo: ${avg_vehicle_cost:,.2f}")
    pdf.ln(5)

    pdf.chapter_title('Gráficos de Recaudación')

    if os.path.exists(os.path.join(tmp, 'recaudado_vendedor.png')):
        pdf.chapter_body('Recaudación por Vendedor:')
        pdf.image(os.path.join(tmp, 'recaudado_vendedor.png'), x=10, w=pdf.w - 20)
        pdf.ln(5)
    else:
        pdf.chapter_body('No se pudo generar el gráfico de recaudación por vendedor.')

    if os.path.exists(os.path.join(tmp, 'recaudado_sede.png')):
        pdf.add_page()
        pdf.chapter_body('Recaudación por Sede:')
        pdf.image(os.path.join(tmp, 'recaudado_sede.png'), x=10, w=pdf.w - 20)
        pdf.ln(5)
    else:
        pdf.chapter_body('No se pudo generar el gráfico de recaudación por sede.')

    if os.path.exists(os.path.join(tmp, 'ventas_por_canal.png')):
        pdf.add_page()
        pdf.chapter_body('Ventas por Canal:')
        pdf.image(os.path.join(tmp, 'ventas_por_canal.png'), x=10, w=pdf.w - 20)
        pdf.ln(5)
    else:
        pdf.chapter_body('No se pudo generar el gráfico de ventas por canal.')

    pdf.add_page()
    pdf.chapter_title('Detalle de Ventas')

    pdf.chapter_body('Detalle por Vendedor:')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(90, 7, 'Vendedor', 1)
    pdf.cell(60, 7, 'Recaudado (USD)', 1, 1)
    pdf.set_font('Helvetica', '', 10)
    for index, value in sales_by_seller.items():
        pdf.cell(90, 7, index, 1)
        pdf.cell(60, 7, f'{value:,.2f}', 1, 1)
    pdf.ln(10)

    pdf.chapter_body('Detalle por Sede:')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(90, 7, 'Sede', 1)
    pdf.cell(60, 7, 'Recaudado (USD)', 1, 1)
    pdf.set_font('Helvetica', '', 10)
    for index, value in sales_by_location.items():
        pdf.cell(90, 7, index, 1)
        pdf.cell(60, 7, f'{value:,.2f}', 1, 1)
    pdf.ln(10)

    pdf.output(os.path.join(tmp, output_pdf))
    logging.info(f"\nReporte de ventas generado exitosamente: {os.path.join(tmp, output_pdf)}")

    for img_file in ['recaudado_vendedor.png', 'recaudado_sede.png', 'ventas_por_canal.png']:
        if os.path.exists(os.path.join(tmp, img_file)):
            os.remove(os.path.join(tmp, img_file))
            
    return os.path.join(tmp, output_pdf)

def get_sales_chart(sales_by_channel, color, title, xlabel, ylabel, output_file):
    plt.figure(figsize=(10, 6))
    sales_by_channel.plot(kind='bar', color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
            
def enviar_reporte_whatsapp(pdf_file: str, recipient_id: str, filename:str="reporte_ventas.pdf"):
    """
    Envia el reporte de ventas generado por WhatsApp.
    Parámetros:
        pdf_file: str, ruta al archivo PDF del reporte
        recipient_id: str, ID del destinatario en WhatsApp
    """
    whatsapp = WhatsApp(
      os.getenv('WHATSAPP_TOKEN'),
      phone_number_id=os.getenv('PNID')
    )
    try:
        res = whatsapp.upload_media(pdf_file)
        print(f"Archivo PDF subido exitosamente: {res}")
        whatsapp.send_document(res['id'], recipient_id, link=False, filename=filename)
        print(f"Reporte enviado a {recipient_id} exitosamente.")
    except Exception as e:
        print(f"Error al enviar el reporte: {e}")

def get_tool(recipient_id: str):
    def obtener_reporte(start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Obtiene el reporte de ventas y lo envía por WhatsApp. Los parámetros son opcionales.
        Si no se especifican, se generará un reporte completo.
        Parámetros:
            start_date: str o None, fecha inicial en formato 'YYYY-MM-DD' o None para no filtrar
            end_date: str o None, fecha final en formato 'YYYY-MM-DD' o None para no filtrar
        """
        report_name = 'sales_report.pdf'
        try:
            report_path = generar_reporte_ventas(
                excel_file='https://firebasestorage.googleapis.com/v0/b/test-cervant.firebasestorage.app/o/tenants%2Fpublic%2Fcervant%2Fventas.csv?alt=media&token=f7ed9274-175b-49d5-a8e7-90eb92803ad2',
                output_pdf=report_name,
                start_date=start_date,
                end_date=end_date
            )
        except Exception as e:
            return f"Error al generar el reporte: {e}"
        
        filename = f"reporte_ventas_{start_date}_{end_date}.pdf" if start_date and end_date else "reporte_ventas.pdf"
        enviar_reporte_whatsapp(
            pdf_file=report_path,
            recipient_id=recipient_id,
            filename=filename
        )
        
        return f"Aquí tienes el reporte de ventas."
        
    return obtener_reporte
    
            
            
            
            
if __name__ == "__main__":
  generar_reporte_ventas(
    excel_file='https://firebasestorage.googleapis.com/v0/b/test-cervant.firebasestorage.app/o/tenants%2Fpublic%2Fcervant%2Fventas.csv?alt=media&token=f7ed9274-175b-49d5-a8e7-90eb92803ad2',
    output_pdf='sales_report.pdf',
    start_date="2017-01-01",
    end_date="2017-12-31"
  )