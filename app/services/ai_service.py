import os
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # Lee cualquier clave que esté presente en el archivo .env
        self.api_key = (
            os.getenv("GROQ_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or ""
        ).strip()

        self.provider = "unknown"
        self.client = None

        # Detectar el proveedor automáticamente según el formato de la clave
        if self.api_key.startswith("gsk_"):
            from groq import Groq
            self.provider = "groq"
            self.client = Groq(api_key=self.api_key)
            self.model = "openai/gpt-oss-120b"
            print(f"[IA] Conectado a GROQ ({self.model}) exitosamente.")

        elif self.api_key.startswith("AIzaSy"):
            from google import genai
            self.provider = "gemini"
            self.client = genai.Client(api_key=self.api_key)
            self.model = "gemini-2.5-flash"
            print(f"[IA] Conectado a GOOGLE GEMINI ({self.model}) exitosamente.")

        elif self.api_key.startswith("sk-"):
            from openai import OpenAI
            self.provider = "openai"
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"
            print(f"[IA] Conectado a OPENAI ({self.model}) exitosamente.")

        else:
            print(
                "\n[ERROR DE CONFIGURACIÓN] La clave en el archivo .env no tiene un formato válido:\n"
                "- Si es Groq: debe empezar con 'gsk_...'\n"
                "- Si es Google Gemini: debe empezar con 'AIzaSy...'\n"
                "- Si es OpenAI: debe empezar con 'sk-...'\n"
            )

        self.system_prompt = (
            "Eres el recepcionista virtual del 'Hotel Paraíso'. Tu trato es cordial, profesional y conciso.\n"
            "Estás atendiendo por WhatsApp, así que responde con mensajes directos, usando emojis y formato legible.\n\n"
            "Información del Hotel:\n"
            "- Habitación Simple: $50 USD por noche (1 persona, cama individual, baño privado, WiFi).\n"
            "- Habitación Doble: $80 USD por noche (2 personas, cama matrimonial o 2 individuales, desayuno incluido).\n"
            "- Suite Familiar: $120 USD por noche (hasta 4 personas, 2 ambientes, hidromasaje, desayuno incluido).\n"
            "- Check-in: 14:00 hs | Check-out: 11:00 hs.\n\n"
            "Tu objetivo es:\n"
            "1. Responder dudas sobre servicios, precios y horarios.\n"
            "2. Guiar al cliente para reservar solicitando: Nombre, Fecha de Entrada (Check-in), Fecha de Salida (Check-out) y Tipo de Habitación.\n"
            "3. Si el usuario confirma todos los datos, dale un resumen final de su reserva."
        )

    def get_chat_response(self, user_message: str, conversation_history: list = None) -> str:
        if conversation_history is None:
            conversation_history = []

        if not self.client:
            return (
                "Error: No hay una API Key válida configurada en el archivo .env.\n"
                "Verifica que empiece con 'gsk_' (Groq), 'AIzaSy' (Gemini) o 'sk-' (OpenAI)."
            )

        try:
            # 1. Caso GROQ / OPENAI (Formato estándar de OpenAI)
            if self.provider in ["groq", "openai"]:
                messages = [{"role": "system", "content": self.system_prompt}]
                messages.extend(conversation_history)
                messages.append({"role": "user", "content": user_message})

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=350,
                )
                return response.choices[0].message.content.strip()

            # 2. Caso GEMINI
            elif self.provider == "gemini":
                from google.genai import types

                contents = []
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg["content"])],
                        )
                    )
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=user_message)],
                    )
                )

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        temperature=0.7,
                        max_output_tokens=350,
                    ),
                )
                return response.text.strip()

        except Exception as e:
            print(f"[Error en {self.provider.upper()} API]: {e}")
            return (
                "Lo siento, en este momento tengo un problema técnico para responder. "
                "Por favor, intenta nuevamente en unos instantes."
            )

ai_service = AIService()
