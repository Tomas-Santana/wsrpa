# WSRPA: Reportes de Ventas y Envío por WhatsApp

Este proyecto permite generar reportes de ventas en PDF a partir de un archivo CSV y enviarlos automáticamente por WhatsApp usando la API de WhatsApp Cloud de Meta.

## ¿Qué hace este proyecto?

- Lee un archivo de ventas (CSV)
- Genera un PDF con gráficos y resumen de ventas
- Envía el PDF por WhatsApp a través de la API Cloud

## ¿Cómo correrlo con Docker?

1. Asegúrate de tener Docker instalado.
2. Crea un archivo `.env` con tus credenciales (ver abajo).
3. Construye la imagen:
   ```sh
   docker build -t wsrpa .
   ```
4. Ejecuta el contenedor:
   ```sh
   docker run -d -p 8080:8080 --env-file .env --name wsrpa wsrpa
   ```

El backend quedará disponible en el puerto 8080.

## Conexión con WhatsApp Cloud API

Para enviar mensajes y archivos por WhatsApp necesitas:

- Crear una app en el [Meta for Developers](https://developers.facebook.com/)
- Configurar el producto "WhatsApp Cloud API"
- Obtener el `WHATSAPP_TOKEN`, `PNID` y configurar el webhook
- Colocar estos datos en tu archivo `.env`

Ejemplo de `.env`:

```
GOOGLE_API_KEY=tu_api_key_de_google
WHATSAPP_TOKEN=tu_token_de_whatsapp
PNID=tu_phone_number_id
VERIFY_TOKEN=tu_token_de_verificacion
FILE_URL=url_opcional_del_csv
```

