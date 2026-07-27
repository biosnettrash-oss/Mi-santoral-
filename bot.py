import os
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Traducción de meses al catalán para construir la URL de Wikipedia
MESES_CA = {
    1: "gener", 2: "febrer", 3: "març", 4: "abril",
    5: "maig", 6: "juny", 7: "juliol", 8: "agost",
    9: "setembre", 10: "octubre", 11: "novembre", 12: "desembre"
}

def obtener_santoral_wikipedia():
    ahora = datetime.now()
    dia = ahora.day
    mes_nombre = MESES_CA[ahora.month]
    
    # URL de Wikipedia del día (ej: https://ca.wikipedia.org/wiki/27_de_juliol)
    url = f"https://ca.wikipedia.org/wiki/{dia}_de_{mes_nombre}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SantoralBot/1.0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscamos la sección de Santoral en Wikipedia
        santos = []
        encabezado = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'Santoral' in tag.text)
        
        if encabezado:
            # Extraemos los elementos de lista (<li>) que le siguen
            siguiente = encabezado.find_next_sibling()
            while siguiente and siguiente.name not in ['h2', 'h3']:
                if siguiente.name in ['ul', 'ol']:
                    for li in siguiente.find_all('li'):
                        texto_li = li.get_text().strip()
                        # Limpiamos notas entre corchetes tipo [1]
                        texto_li = re.sub(r'\[\d+\]', '', texto_li)
                        if texto_li:
                            santos.append(texto_li)
                siguiente = siguiente.find_next_sibling()
                
        if santos:
            # Cogemos hasta los 4 santos principales para no saturar la notificación
            lista_santos = "\n• " + "\n• ".join(santos[:4])
            return f"Santoral del {dia} de {mes_nombre}:{lista_santos}"
            
    except Exception as e:
        print(f"Error al consultar Wikipedia: {e}")
        
    return f"Santoral d'avui ({dia}/{ahora.month})"

def enviar_notificacion():
    texto_santoral = obtener_santoral_wikipedia()
    
    # Extraemos el primer santo de la lista para enviarlo como prompt a la IA
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+)', texto_santoral, re.IGNORECASE)
    nombre_santo = match.group(1) if match else f"Saint of day {datetime.now().day}"

    # Semilla única según el día
    seed_dia = datetime.now().strftime("%Y%m%d")
    prompt = f"Classical Catholic icon painting of {nombre_santo}, holy icon art style, detailed"
    prompt_encoded = urllib.parse.quote(prompt)
    
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed={seed_dia}&nologo=true"
    
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    fecha_corta = datetime.now().strftime("%d/%m")
    
    headers = {
        "Title": f"Santoral d'Avui ({fecha_corta})",
        "Attach": url_imagen,
        "Tags": "calendar,church"
    }
    
    requests.post(url_ntfy, data=texto_santoral.encode('utf-8'), headers=headers)

if __name__ == "__main__":
    enviar_notificacion()
    
