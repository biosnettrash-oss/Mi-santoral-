import os
import urllib.request
from bs4 import BeautifulSoup

TOPIC_NTFY = os.environ.get("TOPIC_NTFY", "santoral-diario-2026")
URL_WEB = "https://www.ecampmany.com/cgi-bin/calendari.cgi"

def obtener_santo():
    try:
        req = urllib.request.Request(
            URL_WEB, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            # Leemos los datos en bytes
            raw_data = response.read()
            # La web ecampmany usa iso-8859-1 (latin1)
            html = raw_data.decode('iso-8859-1', errors='ignore')
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Filtramos todas las líneas de texto no vacías
        lineas = [line.strip() for line in soup.get_text().split('\n') if line.strip()]
        
        # Buscamos dónde aparecen las líneas con la fecha/día y nos quedamos con las líneas siguientes (que contienen el santoral)
        # Cogemos desde la línea 5 hasta la 20 para asegurarnos de capturar los santos
         lineas_santo = lineas[5:22]
        
        mensaje = "\n".join(lineas_santo)
        return mensaje if mensaje else "No se pudo extraer el santoral."
    except Exception as e:
        return f"Error al conectar con la web: {e}"

def enviar_push(mensaje):
    url_ntfy = f"https://ntfy.sh/{TOPIC_NTFY}"
    cuerpo = f"📅 Santoral de hoy:\n\n{mensaje}"
    
    # Enviamos en UTF-8 para que los acentos y caracteres catalanes se vean perfectos
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
    
