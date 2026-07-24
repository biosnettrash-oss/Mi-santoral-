import os
import requests
from bs4 import BeautifulSoup

# Canal de ntfy configurado en tu app
TOPIC_NTFY = os.environ.get("TOPIC_NTFY", "santoral-diario-2026")
URL_WEB = "https://www.ecampmany.com/cgi-bin/calendari.cgi"

def obtener_santo():
    try:
        response = requests.get(URL_WEB, timeout=10)
        response.encoding = 'iso-8859-1'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        texto_pagina = soup.get_text()
        
        lineas = [line.strip() for line in texto_pagina.split('\n') if line.strip()]
        mensaje = "\n".join(lineas[:8])
        return mensaje
    except Exception as e:
        return f"Error al obtener el santoral: {e}"

def enviar_push(mensaje):
    url_ntfy = f"https://ntfy.sh/{TOPIC_NTFY}"
    requests.post(
        url_ntfy,
        data=mensaje.encode('utf-8'),
        headers={
            "Title": "📅 Santoral de Hoy",
            "Priority": "default",
            "Tags": "pray,calendar"
        }
    )

if __name__ == "__main__":
    santo = obtener_santo()
    enviar_push(santo)
  
