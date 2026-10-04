from fastapi import FastAPI, Form, Response
from app.services.twilio_service import twilio_service

app = FastAPI(title="WhatsApp Hotel Reservation Bot")

@app.get("/")
def health_check():
    """Endpoint para verificar que el servidor esté activo."""
    return {"status": "ok", "service": "Hotel Bot API"}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(""),
    ProfileName: str = Form(None)
):
    """
    Endpoint principal que recibe los mensajes entrantes de WhatsApp vía Twilio.
    - From: Número del remitente (ej: 'whatsapp:+54911xxxxxxxx')
    - Body: Texto que escribió el usuario
    - ProfileName: Nombre visible del contacto en WhatsApp
    """
    user_text = Body.strip().lower()
    user_name = ProfileName or "Huésped"

    # Lógica de respuesta inicial de prueba
    if user_text in ["hola", "buenas", "start", "menu"]:
        reply_text = (
            f"¡Hola {user_name}! 👋 Bienvenido al Hotel Paraíso.\n\n"
            "¿En qué puedo ayudarte hoy?\n"
            "1. 🏨 Consultar habitaciones y precios\n"
            "2. 📅 Hacer una reserva\n"
            "3. 🔍 Ver mis reservas\n\n"
            "Responde con el número de la opción que deseas."
        )
    elif user_text == "1":
        reply_text = (
            "🏨 *Nuestras Habitaciones:*\n"
            "- Simple: $50/noche\n"
            "- Doble: $80/noche\n"
            "- Suite Familiar: $120/noche\n\n"
            "Escribe '2' para iniciar tu reserva."
        )
    elif user_text == "2":
        reply_text = "📅 Para iniciar la reserva, ¿en qué fecha deseas ingresar? (Ejemplo: 2025-05-10)"
    else:
        reply_text = f"Recibí: \"{Body}\".\nEscribe *hola* para ver el menú de opciones."

    # Devolvemos la respuesta en formato TwiML (XML) a Twilio
    twiml_content = twilio_service.build_twiml_response(reply_text)
    return Response(content=twiml_content, media_type="application/xml")
