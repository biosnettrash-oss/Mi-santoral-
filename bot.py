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
        
        # Eliminamos scripts y estilos para limpiar el DOM
        for element in soup(["script", "style", "nav", "header", "footer"]):
            element.extract()
            
        # Extraemos las líneas de texto
        lineas = [l.strip() for l in soup.get_text().splitlines() if l.strip()]
        
        # Buscamos la sección relevante del santoral
        lineas_santoral = []
        guardar = False
        
        for linea in lineas:
            # Empezamos a guardar cuando encontremos palabras clave de la fecha/santos
            if any(k in linea.lower() for k in ["sant ", "santa ", "sants ", "sol:", "lluna:"]) or re.search(r'^\d{1,2}\s+[A-Z]{5,}', linea):
                guardar = True
            
            # Cortamos al llegar al menú inferior o passatemps
            if any(k in linea for k in ["Passatemps", "Videojocs", "Inici", "Dades del", "Buscar"]):
                break
                
            if guardar:
                lineas_santoral.append(linea)
                
        if lineas_santoral:
            texto = "\n".join(lineas_santoral)
            # Limpiamos posibles caracteres corruptos de la web
            texto = texto.replace("Â·", "•").replace("Â", "")
            return texto
            
    except Exception as e:
        print(f"Error al raspar la web: {e}")
        
    return "Sant Joaquim i Santa Anna, pares de la Verge Maria"

def enviar_notificacion():
    santoral = obtener_santoral()
    
    # Buscamos el nombre del primer santo para enviárselo a la IA
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+(\s+[A-ZÀ-Úa-zà-ú]+)?)', santoral, re.IGNORECASE)
    nombre_santo = match.group(1) if match else "Saint Joachim and Saint Anne"

    # Generamos la imagen con Pollinations usando el santo exacto
    prompt = f"Classical Catholic icon painting of {nombre_santo}, holy icon art style, detailed"
    prompt_encoded = urllib.parse.quote(prompt)
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    
    headers = {
        "Title": "Santoral d'Avui",
        "Attach": url_imagen,
        "Tags": "calendar,church"
    }
    
    # Envío a ntfy
    requests.post(url_ntfy, data=santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
