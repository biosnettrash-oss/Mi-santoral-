import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

def obtener_santoral():
    url = "https://www.ecampmany.com/santoral"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Obtenemos todo el texto y lo dividimos por líneas
        lineas = [l.strip() for l in soup.text.splitlines() if l.strip()]
        
        lineas_validas = []
        capturar = False
        
        for linea in lineas:
            # Empezamos a capturar cuando aparece el número del día o palabras clave
            if any(palabra in linea.lower() for palabra in ["sant", "santa", "sants", "sol:", "lluna:"]):
                capturar = True
            
            # Cortamos si llegamos al menú/pie de página
            if any(corte in linea for corte in ["Passatemps", "Videojocs", "Inici", "Dades del"]):
                break
                
            if capturar:
                lineas_validas.append(linea)
                
        texto_final = "\n".join(lineas_validas)
        # Limpieza de tildes/caracteres corruptos
        texto_final = texto_final.replace("Â·", "•").replace("Â", "")
        
        if texto_final:
            return texto_final
    except Exception as e:
        print(f"Error al obtener santoral: {e}")
        
    return "Santoral d'avui"

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Buscamos el primer santo para la imagen (ej: Sant Joaquim)
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+)', santoral, re.IGNORECASE)
    santo_nombre = match.group(1) if match else "Saint"

    # Generamos la imagen
    prompt = f"Catholic saint illustration of {santo_nombre}, holy art style, vintage painting"
    prompt_encoded = urllib.parse.quote(prompt)
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "Santoral d'Avui",
        "Attach": url_imagen,
        "Tags": "calendar,church"
    }
    
    # Envío en UTF-8 puro
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
