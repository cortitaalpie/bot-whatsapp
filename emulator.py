import sys
import requests
import xmltodict

# Asegura compatibilidad con emojis en cualquier terminal de Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WEBHOOK_URL = "http://127.0.0.1:8000/webhook/whatsapp"
PHONE_NUMBER = "whatsapp:+5491112345678"
USER_NAME = "Jeremias"


def parse_bot_response(xml_content):
    try:
        data = xmltodict.parse(xml_content)
        return data["Response"]["Message"]
    except Exception:
        return xml_content



def start_chat():
    print("=" * 50)
    print("SIMULADOR DE WHATSAPP - HOTEL PARAISO")
    print("Escribe 'salir' para terminar")
    print("=" * 50)

    while True:
        user_message = input("\nTu: ")

        if user_message.strip().lower() == "salir":
            print("\nSimulador finalizado.")
            break

        if not user_message.strip():
            continue

        payload = {
            "From": PHONE_NUMBER,
            "Body": user_message,
            "ProfileName": USER_NAME,
        }

        try:
            response = requests.post(WEBHOOK_URL, data=payload)
            if response.status_code == 200:
                reply = parse_bot_response(response.text)
                print(f"\nBot:\n{reply}")
            else:
                print(f"\nError {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            print("\nError: No hay conexion con el servidor FastAPI.")
            print("Verifica que 'uvicorn app.main:app --reload' este corriendo.")


if __name__ == "__main__":
    start_chat()
