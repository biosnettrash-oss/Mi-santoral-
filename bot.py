import os
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

# Canal de ntfy
TOPIC_NTFY = os.environ.get("TOPIC_NTFY", "santoral-diario-2026")
URL_WEB = "https://www.ecampmany.com/cgi-bin/calendari.cgi"

def obtener_santo():
    try:
        req = urllib.request.Request(
            URL_WEB, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('iso-8859-1', errors='ignore')
        
        soup = BeautifulSoup(html, 'html.parser')
        texto_pagina = soup.get_text()
        
        lineas = [line.strip() for line in texto_pagina.split('\n') if line.strip()]
        mensaje = "\n".join(lineas[:6])
        return mensaje if mensaje else "No se pudo extraer el santoral de hoy."
    except Exception as e:
        return f"Error al conectar con la web: {e}"

def enviar_push(mensaje):
    url_ntfy = f"https://ntfy.sh/{TOPIC_NTFY}"
    cuerpo = f"Santoral de hoy:\n\n{mensaje}"
    
    datos = cuerpo.encode('utf-8')
    
    req = urllib.request.Request(
        url_ntfy,
        data=datos,
        headers={
            "Title": "Santoral de Hoy"
        },
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        print(f"Error al enviar push: {e}")

if __name__ == "__main__":
    santo = obtener_santo()
    enviar_push(santo)
    
