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
    # Forzamos la codificación UTF-8 para arreglar los acentos (tradició, Â·)
    response.encoding = 'utf-8' 
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extraemos el texto
    texto_completo = soup.get_text()
    
    # Limpiamos el texto cortando antes de la basura del menú
    if "Passatemps" in texto_completo:
        texto_completo = texto_completo.split("Passatemps")[0]
        
    lineas = [linea.strip() for linea in texto_completo.splitlines() if linea.strip()]
    
    # Buscamos las líneas relevantes del santoral
    texto_limpio = []
    for linea in lineas:
        if any(palabra in linea.lower() for palabra in ["sant", "santa", "sants", "santes", "sol:", "lluna:"]):
            texto_limpio.append(linea)
            
    resultado = "\n".join(texto_limpio) if texto_limpio else "Santoral d'avui"
    return resultado

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Extraemos el primer santo principal para la imagen
    # Ej: "Sant Joaquim i santa Anna..." -> "Sant Joaquim"
    santo_principal = "Santoral"
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+)', santoral, re.IGNORECASE)
    if match:
        santo_principal = match.group(1)

    # Creamos el prompt para la IA de Pollinations (Gratis y sin API key)
    prompt_ia = f"Catholic saint illustration of {santo_principal}, holy art style, detailed, detailed face, vintage painting"
    prompt_encoded = urllib.parse.quote(prompt_ia)
    
    # URL de la imagen generada por IA
    url_imagen = f"https://pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed=42&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "Santoral d'Avui 📅",
        "Attach": url_imagen,  # Adjunta la imagen generada por la IA
        "Tags": "calendar,church"
    }
    
    # Enviamos la notificación a ntfy
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
    
