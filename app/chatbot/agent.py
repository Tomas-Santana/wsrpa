from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.google_genai import GoogleGenAI
from dotenv import load_dotenv

load_dotenv()

llm = GoogleGenAI(model="gemini-1.5-flash")

def get_agent(tools: list[callable]):
    return FunctionAgent(
      llm=llm, tools=tools, system_prompt="Eres un agente de IA que ayuda a generar reportes de ventas de carros. Tiene una herramienta llamada 'obtener_reporte' que puede usar para generar reportes. Puedes usar esta herramienta para obtener un reporte de ventas en un rango de fechas específico. El reporte se enviará por WhatsApp al destinatario especificado.",
    )