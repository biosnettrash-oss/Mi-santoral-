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
    response.encoding = 'utf-8' # Arreglamos los acentos y caracteres raros
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Buscamos el contenedor principal de texto de la web
    # Esta web suele usar un div con clase 'content' o similar.
    contenedor = soup.find('div', class_='content')
    if not contenedor:
        contenedor = soup.find('main') # Si no, probamos con la etiqueta main

    if contenedor:
        texto = contenedor.get_text()
    else:
        # Si no encontramos contenedor, cogemos todo el body pero es más sucio
        texto = soup.body.get_text()

    # Limpiamos el texto
    # Cortamos a partir de Passatemps o Menú para eliminar la basura final
    for palabra_corte in ["Passatemps", "Videojocs", "Inici", "Dades del", "Propòsit"]:
        if palabra_corte in texto:
            texto = texto.split(palabra_corte)[0]
            
    # Limpiamos líneas vacías repetidas y espacios
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    
    # Arreglamos caracteres extraños comunes si aparecieran
    texto_final = "\n".join(lineas)
    texto_final = texto_final.replace("Â·", "•").replace("Â", "")
    
    return texto_final if texto_final else "Santoral d'avui"

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Intentamos buscar el nombre del primer santo principal (ej: "Sant Joaquim", "Santa Anna")
    # Buscamos 'Sant' o 'Santa' seguido de una mayúscula y palabras.
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+(\s+[A-ZÀ-Úa-zà-ú]+)?)', santoral, re.IGNORECASE)
    
    if match:
        nombre_santo = match.group(1)
        print(f"Santo principal identificado: {nombre_santo}")
    else:
        # Fallback si no encontramos nombre
        nombre_santo = "Saint"
        print("No se ha identificado un santo específico.")

    # Generamos la imagen con Pollinations, usando el nombre específico
    prompt = f"Classical Catholic icon painting of {nombre_santo}, holy icon art style, detailed face"
    prompt_encoded = urllib.parse.quote(prompt)
    
    # URL de Pollinations para generar la imagen
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "Santoral d'Avui",
        "Attach": url_imagen, # Adjunta la imagen
        "Tags": "calendar,church"
    }
    
    # Enviamos el mensaje en UTF-8
    print("Enviando notificación...")
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)
    print("Notificación enviada.")

if __name__ == "__main__":
    enviar_notificacion()
    
