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
    
    # Extraemos el texto
    texto = soup.get_text()
    
    # Cortamos a partir de Passatemps o Menú para eliminar la basura final
    for palabra_corte in ["Passatemps", "Videojocs", "Inici"]:
        if palabra_corte in texto:
            texto = texto.split(palabra_corte)[0]
            
    # Limpiamos líneas vacías repetidas
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    
    # Arreglamos caracteres extraños comunes de la web si aparecieran
    texto_final = "\n".join(lineas)
    texto_final = texto_final.replace("Â·", "•").replace("Â", "")
    
    return texto_final if texto_final else "Santoral d'avui"

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Buscamos el nombre del primer santo (ej: "Sant Joaquim", "Santa Anna")
    santo_match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+)', santoral, re.IGNORECASE)
    
    if santo_match:
        nombre_santo = santo_match.group(1)
    else:
        nombre_santo = "Saint"

    # Generamos la imagen con Pollinations
    prompt = f"Catholic saint painting of {nombre_santo}, holy icon art style"
    prompt_encoded = urllib.parse.quote(prompt)
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "Santoral d'Avui",
        "Attach": url_imagen,
        "Tags": "calendar,church"
    }
    
    # Enviamos el mensaje en UTF-8
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
    
    
    
