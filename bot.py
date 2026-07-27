import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def obtener_santoral():
    # Añadimos un parámetro de tiempo para obligar a la web a dar el contenido fresco de hoy
    timestamp = int(datetime.now().timestamp())
    url = f"https://www.ecampmany.com/santoral?t={timestamp}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.extract()
            
        lineas = [l.strip() for l in soup.get_text().splitlines() if l.strip()]
        
        lineas_santoral = []
        guardar = False
        
        for linea in lineas:
            # Detectar inicio del bloque
            if any(k in linea.lower() for k in ["sant ", "santa ", "sants ", "sol:", "lluna:"]) or re.search(r'^\d{1,2}\s+[A-Z]{5,}', linea):
                guardar = True
            
            if any(k in linea for k in ["Passatemps", "Videojocs", "Inici", "Dades del", "Buscar"]):
                break
                
            if guardar:
                lineas_santoral.append(linea)
                
        if lineas_santoral:
            texto = "\n".join(lineas_santoral)
            texto = texto.replace("Â·", "•").replace("Â", "")
            return texto
            
    except Exception as e:
        print(f"Error al raspar la web: {e}")
        
    # Mensaje dinámico si falla el scraping para que NUNCA repita el día anterior
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    return f"Santoral d'avui ({fecha_hoy})"

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Extraer el primer santo del texto capturado
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+(\s+[A-ZÀ-Úa-zà-ú]+)?)', santoral, re.IGNORECASE)
    nombre_santo = match.group(1) if match else f"Saint of day {datetime.now().day}"

    # Usar la fecha como semilla (seed) para asegurar imagen diferente cada día
    seed_dia = datetime.now().strftime("%Y%m%d")
    prompt = f"Classical Catholic icon painting of {nombre_santo}, holy icon art style, detailed"
    prompt_encoded = urllib.parse.quote(prompt)
    
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed={seed_dia}&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": f"Santoral d'Avui ({datetime.now().strftime('%d/%m')})",
        "Attach": url_imagen,
        "Tags": "calendar,church"
    }
    
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
