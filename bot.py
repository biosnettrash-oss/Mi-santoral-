import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

def obtener_santoral():
    url = "https://www.ecampmany.com/santoral"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    
    soup = BeautifulSoup(response.text, "html.parser")
    texto_completo = soup.get_text()
    
    # Cortamos antes del menú
    if "Passatemps" in texto_completo:
        texto_completo = texto_completo.split("Passatemps")[0]
        
    lineas = [linea.strip() for linea in texto_completo.splitlines() if linea.strip()]
    
    texto_limpio = []
    for linea in lineas:
        if any(palabra in linea.lower() for palabra in ["sant", "santa", "sants", "santes", "sol:", "lluna:"]):
            texto_limpio.append(linea)
            
    resultado = "\n".join(texto_limpio) if texto_limpio else "Santoral d'avui"
    return resultado

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Extraemos el santo para la imagen
    santo_principal = "Santoral"
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+)', santoral, re.IGNORECASE)
    if match:
        santo_principal = match.group(1)

    # Prompt para Pollinations.ai
    prompt_ia = f"Catholic saint illustration of {santo_principal}, holy art style, detailed, vintage painting"
    prompt_encoded = urllib.parse.quote(prompt_ia)
    
    url_imagen = f"https://pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed=42&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    # Cabeceras sin emojis para evitar errores de codificación latin-1
    headers = {
        "Title": "Santoral d'Avui",
        "Attach": url_imagen,
        "Tags": "calendar,church"
    }
    
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
    
    
