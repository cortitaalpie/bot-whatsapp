import sys
import os
from typing import Dict, List
from fastapi import FastAPI, Request, Query, HTTPException, Form, Response
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

# Forzar salida en UTF-8 y sin buffer en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

app = FastAPI(title="WhatsApp Hotel Reservation Bot")

# Memoria de conversación
sessions_memory: Dict[str, List[dict]] = {}
MAX_HISTORY_MESSAGES = 10

from app.services.twilio_service import twilio_service
from app.services.ai_service import ai_service
from app.services.meta_service import meta_service


@app.get("/")
def health_check():
    return {"status": "ok", "service": "Hotel Bot API"}


# =====================================================================
# SECCIÓN 1: WEBHOOK PARA META WHATSAPP CLOUD API (Oficial)
# =====================================================================

@app.get("/webhook/meta")
def verify_meta_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    verify_token = os.getenv("META_VERIFY_TOKEN", "hotel_secreto_123")
    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        print("\n>>> [META WEBHOOK] Verificado exitosamente con Meta! (GET 200)", flush=True)
        return PlainTextResponse(content=hub_challenge, status_code=200)

    print("\n>>> [META WEBHOOK ERROR] Token no coincide.", flush=True)
    raise HTTPException(status_code=403, detail="Token inválido")


@app.post("/webhook/meta")
async def receive_meta_webhook(request: Request):
    data = await request.json()
    print(f"\n[EVENTO RECIBIDO DE META]: {data}", flush=True)

    try:
        entries = data.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})

                # 1. Si es un mensaje nuevo de WhatsApp
                if "messages" in value:
                    for msg in value["messages"]:
                        user_phone = msg.get("from")
                        msg_type = msg.get("type")

                        if msg_type == "text":
                            user_message = msg.get("text", {}).get("body", "").strip()
                            print(f"\n==================================================", flush=True)
                            print(f">>> [MENSAJE RECIBIDO DE WHATSAPP]", flush=True)
                            print(f"    De: {user_phone}", flush=True)
                            print(f"    Texto: {user_message}", flush=True)
                            print(f"==================================================", flush=True)

                            # Historial de conversación
                            user_history = sessions_memory.get(user_phone, [])

                            # Consultar a la IA (Groq)
                            bot_reply = ai_service.get_chat_response(
                                user_message=user_message,
                                conversation_history=user_history
                            )
                            print(f">>> [IA RESPUESTA]:\n{bot_reply}\n", flush=True)

                            # Guardar en memoria
                            user_history.append({"role": "user", "content": user_message})
                            user_history.append({"role": "assistant", "content": bot_reply})
                            if len(user_history) > MAX_HISTORY_MESSAGES:
                                user_history = user_history[-MAX_HISTORY_MESSAGES:]
                            sessions_memory[user_phone] = user_history

                            # Enviar respuesta de vuelta a WhatsApp
                            meta_service.send_message(to_phone=user_phone, text=bot_reply)

                # 2. Si es un estado (entregado, leído, etc.)
                elif "statuses" in value:
                    status_info = value["statuses"][0]
                    status_name = status_info.get("status")
                    recipient = status_info.get("recipient_id")
                    print(f">>> [ESTADO WHATSAPP]: Mensaje para {recipient} -> {status_name}", flush=True)

    except Exception as e:
        print(f">>> [ERROR PROCESANDO WEBHOOK]: {e}", flush=True)

    return {"status": "success"}


# =====================================================================
# SECCIÓN 2: WEBHOOK PARA TWILIO / EMULADOR LOCAL
# =====================================================================

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(""),
    ProfileName: str = Form(None)
):
    user_message = Body.strip()
    user_history = sessions_memory.get(From, [])

    bot_reply = ai_service.get_chat_response(
        user_message=user_message,
        conversation_history=user_history
    )

    user_history.append({"role": "user", "content": user_message})
    user_history.append({"role": "assistant", "content": bot_reply})
    if len(user_history) > MAX_HISTORY_MESSAGES:
        user_history = user_history[-MAX_HISTORY_MESSAGES:]
    sessions_memory[From] = user_history

    twiml_content = twilio_service.build_twiml_response(bot_reply)
    return Response(content=twiml_content, media_type="application/xml")
