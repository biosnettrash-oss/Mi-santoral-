import os
import re
import urllib.parse
import requests
from datetime import datetime

MESES_CA = {
    1: "gener", 2: "febrer", 3: "març", 4: "abril",
    5: "maig", 6: "juny", 7: "juliol", 8: "agost",
    9: "setembre", 10: "octubre", 11: "novembre", 12: "desembre"
}

def obtener_santoral_wikipedia_api():
    ahora = datetime.now()
    dia = ahora.day
    mes_nombre = MESES_CA[ahora.month]
    
    # Usamos la API oficial de MediaWiki para obtener el wikitexto puro
    page_title = f"{dia}_de_{mes_nombre}"
    api_url = "https://ca.wikipedia.org/w/api.php"
    
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext",
        "format": "json"
    }
    
    headers = {
        "User-Agent": "SantoralBot/1.0 (https://github.com/biosnettrash-oss)"
    }
    
    try:
        res = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = res.json()
        wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
        
        # Buscamos la sección de Festes / Commemoracions / Santoral
        seccion_match = re.search(r'==\s*(?:Festes|Commemoracions|Santoral).*?==\n(.*?)(?=\n==|\Z)', wikitext, re.DOTALL | re.IGNORECASE)
        
        santos = []
        if seccion_match:
            bloque = seccion_match.group(1)
            # Extraemos las líneas con viñetas (*)
            for linea in bloque.splitlines():
                if linea.startswith("*"):
                    # Limpiamos el formato de enlaces de Wikipedia [[Texto|Nombre]] -> Nombre
                    texto_limpio = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', linea)
                    # Limpiamos plantillas tipo {{...}}, comillas o formatos extras
                    texto_limpio = re.sub(r'\{\{[^}]+\}\}', '', texto_limpio)
                    texto_limpio = texto_limpio.replace('*', '').replace("'''", "").replace("''", "").strip()
                    
                    if texto_limpio and any(k in texto_limpio.lower() for k in ["sant", "santa", "sants", "santes", "festa", "mare de déu"]):
                        santos.append(texto_limpio)
                        
        if santos:
            # Seleccionamos hasta 4 santos principales para mantenerlo conciso
            santos_formateados = "\n• " + "\n• ".join(santos[:4])
            return f"Santoral del {dia} de {mes_nombre}:{santos_formateados}"
            
    except Exception as e:
        print(f"Error cargando API de Wikipedia: {e}")
        
    return f"Santoral d'avui ({dia}/{ahora.month})"

def enviar_notificacion():
    texto_santoral = obtener_santoral_wikipedia_api()
    
    # Extraemos el primer nombre de santo para generar la imagen
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Úa-zà-ú]+)', texto_santoral, re.IGNORECASE)
    nombre_santo = match.group(1) if match else f"Saint of day {datetime.now().day}"

    # Semilla única para cambiar imagen a diario
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
    
