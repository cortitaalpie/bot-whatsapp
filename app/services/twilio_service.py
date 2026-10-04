from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from app.config import settings

class TwilioService:
    def __init__(self):
        # Cliente REST de Twilio para enviar mensajes de forma activa
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        else:
            self.client = None

    @staticmethod
    def build_twiml_response(message_body: str) -> str:
        """
        Genera una respuesta síncrona en formato TwiML (XML).
        Es la forma más rápida y económica de responder al webhook de Twilio.
        """
        response = MessagingResponse()
        response.message(message_body)
        return str(response)

    def send_message_rest(self, to_number: str, message_body: str):
        """
        Envía un mensaje de forma activa usando la API REST de Twilio.
        Útil para recordatorios, alertas o mensajes fuera del flujo inmediato.
        """
        if not self.client:
            raise ValueError("Las credenciales de Twilio no están configuradas en el archivo .env")

        return self.client.messages.create(
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=to_number,
            body=message_body
        )

twilio_service = TwilioService()
