from typing import Dict, List
from fastapi import FastAPI, Form, Response
from app.services.twilio_service import twilio_service
from app.services.ai_service import ai_service

app = FastAPI(title="WhatsApp Hotel Reservation Bot")

# Memoria en RAM: guarda el historial de mensajes por cada número de teléfono
# Formato: { "whatsapp:+54911...": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}] }
sessions_memory: Dict[str, List[dict]] = {}

# Límite de mensajes a recordar por conversación (evita gastar tokens innecesarios)
MAX_HISTORY_MESSAGES = 10


@app.get("/")
def health_check():
    """Endpoint de comprobación de salud del servidor."""
    return {"status": "ok", "service": "Hotel Bot API con IA"}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(""),
    ProfileName: str = Form(None)
):
    """
    Webhook que recibe los mensajes de WhatsApp vía Twilio y los procesa con IA.
    """
    user_message = Body.strip()
    user_id = From  # El identificador único del usuario es su número de teléfono

    # 1. Obtener el historial previo del usuario (o crear una lista vacía si es nuevo)
    user_history = sessions_memory.get(user_id, [])

    # 2. Consultar al servicio de IA pasándole el mensaje actual y su historial
    bot_reply = ai_service.get_chat_response(
        user_message=user_message,
        conversation_history=user_history
    )

    # 3. Actualizar el historial en memoria con la nueva interacción
    user_history.append({"role": "user", "content": user_message})
    user_history.append({"role": "assistant", "content": bot_reply})

    # 4. Limitar el historial a los últimos N mensajes (Sliding Window)
    if len(user_history) > MAX_HISTORY_MESSAGES:
        user_history = user_history[-MAX_HISTORY_MESSAGES:]

    # Guardar el historial actualizado
    sessions_memory[user_id] = user_history

    # 5. Devolver la respuesta a Twilio en formato TwiML
    twiml_content = twilio_service.build_twiml_response(bot_reply)
    return Response(content=twiml_content, media_type="application/xml")
