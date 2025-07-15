from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from heyoo import WhatsApp
from dotenv import load_dotenv
from app.chatbot.tools import get_tool
from app.chatbot.agent import get_agent
load_dotenv()

app = FastAPI()
whatsapp = WhatsApp(token=os.getenv('WHATSAPP_TOKEN'), phone_number_id=os.getenv('PNID'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the WSRPA API!"}
  


@app.get("/chat", response_class=PlainTextResponse)
async def read_chat(request: Request):
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    if request.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        return request.query_params.get("hub.challenge")
    return 'Verification failed', 403

@app.post("/chat")
async def post_chat(request: Request):
    data = await request.json()
    try:
        changed_field = whatsapp.changed_field(data)
    except Exception as e:
        return {'message': 'Error processing message'}, 500

    if changed_field != 'messages':
        return 'OK', 201

    is_new_message = whatsapp.is_message(data)

    if not is_new_message:
        delivery = whatsapp.get_delivery(data)
        if not delivery:
            return "Bad Request", 400

        return "OK", 200

    mobile = whatsapp.get_mobile(data)
    name = whatsapp.get_name(data)
    if not mobile or not name:
        return "Bad Request", 400
    message_type = whatsapp.get_message_type(data)
    if message_type == 'text':
        message_text = whatsapp.get_message(data)
        if not message_text:
            return "Bad Request", 400
        
    else:
        whatsapp.send_message(
            message="El mensaje que has enviado no está en un formato válido.",
            recipient_id=mobile,
        )
        
    tool = get_tool(mobile)
    agent = get_agent(tools=[tool])
    
    response = await agent.run(message_text)
    
    whatsapp.send_message(
        message=str(response),
        recipient_id=mobile,
    )
    return "OK", 200