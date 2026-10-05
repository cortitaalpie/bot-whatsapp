import os
import requests
from dotenv import load_dotenv

load_dotenv()

class MetaService:
    def _get_argentine_alternatives(self, phone: str):
        """Genera variantes de formato para números de Argentina (con/sin 9, con/sin 15)."""
        alts = []
        if phone.startswith("549"):
            alts.append("54" + phone[3:])  # Sin el 9
            for num_len in [6, 7, 8]:      # Con el 15 local
                if len(phone[3:]) > num_len:
                    area = phone[3:-num_len]
                    num = phone[-num_len:]
                    alts.append(f"54{area}15{num}")
        elif phone.startswith("54"):
            alts.append("549" + phone[2:]) # Con el 9
        return list(dict.fromkeys(alts))

    def send_message(self, to_phone: str, text: str):
        """Envía un mensaje de texto por WhatsApp usando la API oficial de Meta."""
        access_token = os.getenv("META_ACCESS_TOKEN", "").strip()
        phone_number_id = os.getenv("META_PHONE_NUMBER_ID", "").strip()

        if not access_token or not phone_number_id:
            print("[ERROR META] Faltan META_ACCESS_TOKEN o META_PHONE_NUMBER_ID en .env", flush=True)
            return None

        api_url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        clean_phone = to_phone.replace("+", "").replace(" ", "").replace("-", "").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {"body": text}
        }

        try:
            print(f">>> [ENVIANDO A META] -> Destinatario: {clean_phone}", flush=True)
            response = requests.post(api_url, headers=headers, json=payload)
            res_json = response.json()

            # Si Meta rechaza por error 131030 (número no en lista autorizada), probamos variantes de formato de Argentina
            if response.status_code != 200 and res_json.get("error", {}).get("code") == 131030:
                alternatives = self._get_argentine_alternatives(clean_phone)
                for alt_phone in alternatives:
                    print(f">>> [REINTENTO CON FORMATO ALTERNATIVO] -> {alt_phone}", flush=True)
                    payload["to"] = alt_phone
                    retry_resp = requests.post(api_url, headers=headers, json=payload)
                    retry_json = retry_resp.json()
                    if retry_resp.status_code == 200:
                        msg_id = retry_json.get("messages", [{}])[0].get("id", "OK")
                        print(f">>> [ENVIADO CON ÉXITO TRAS REINTENTO] Message ID: {msg_id}", flush=True)
                        return retry_json

            if response.status_code == 200:
                msg_id = res_json.get("messages", [{}])[0].get("id", "OK")
                print(f">>> [ENVIADO CON ÉXITO] WhatsApp Message ID: {msg_id}", flush=True)
            else:
                print(f">>> [ERROR RESPUESTA DE META HTTP {response.status_code}]:\n{res_json}", flush=True)

            return res_json

        except Exception as e:
            print(f">>> [ERROR DE CONEXIÓN CON META]: {e}", flush=True)
            return None

meta_service = MetaService()
