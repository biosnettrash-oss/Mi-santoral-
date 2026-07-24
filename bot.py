import os
import requests
from bs4 import BeautifulSoup

# Canal de ntfy
TOPIC_NTFY = os.environ.get("TOPIC_NTFY", "santoral-diario-2026")
URL_WEB = "https://www.ecampmany.com/cgi-bin/calendari.cgi"

def obtener_santo():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL_WEB, headers=headers, timeout=15)
        response.encoding = 'iso-8859-1'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        texto_pagina = soup.get_text()
        
        lineas = [line.strip() for line in texto_pagina.split('\n') if line.strip()]
        mensaje = "\n".join(lineas[:6])
        return mensaje if mensaje else "No se pudo extraer el santoral de hoy."
    except Exception as e:
        return f"Error al conectar con la web: {e}"

def enviar_push(mensaje):
    url_ntfy = f"https://ntfy.sh/{TOPIC_NTFY}"
    
    # Construimos todo el cuerpo del mensaje (título + contenido)
    cuerpo_mensaje = f"📅 Santoral de hoy:\n\n{mensaje}"
    
    # Hacemos la petición POST sin cabeceras complejas para evitar fallos de codificacion
    requests.post(
        url_ntfy,
        data=cuerpo_mensaje.encode('utf-8')
    )

if __name__ == "__main__":
    santo = obtener_santo()
    enviar_push(santo)
