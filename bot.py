import os
import urllib.parse
import requests
from datetime import datetime

# Base de datos interna de seguridad (Simplified Internal Database)
# Santos principales de cada día del mes de Julio para garantizar texto útil.
# Si el script funciona meses, habría que rellenar el resto del diccionario.
SANTORAL_JULIO = {
    1: "Sant Simetrio, Sant Aarón",
    2: "Sants Vidal i Vidal, Santa Marcia",
    3: "Sant Tomàs Apòstol, Sant Lleó II",
    4: "Santa Isabel de Portugal, Sant Andreu",
    5: "Sant Antoni Maria Zaccaria, Sant Domènec",
    6: "Santa Maria Goretti, Sant Esiqui",
    7: "Sant Fermí, Sant Apol·loni",
    8: "Sant Procopi, Santa Priscil·la",
    9: "Sant Anastasi, Santa Anatòlia",
    10: "Sant Cristòfol, Santa Amàlia",
    11: "Sant Benet d'Aniana, Sant Marc",
    12: "Sant Joan Gualbert, Sant Nabor",
    13: "Sant Enric, Sant Esdràs",
    14: "Sant Camil de Lellis, Sant Francesc",
    15: "Sant Bonaventura, Sant Vladimir",
    16: "Nostra Senyora del Carme, Sant Hilari",
    17: "Santes Justa i Rufina, Sant Marçal",
    18: "Sant Frederic, Sant Arnold",
    19: "Sant Just, Santa Rufina",
    20: "Santa Margarida d'Antioquia, Sant Elies",
    21: "Sant Llorenç de Brindisi, Sant Víctor",
    22: "Santa Maria Magdalena, Sant Teòfil",
    23: "Santa Brígida de Suècia, Sant Joan",
    24: "Sant Cristòfol, Santa Cristina",
    25: "Sant Jaume Apòstol, Sant Cristòfol",
    26: "Sant Joaquim i Santa Anna, pares de la Verge Maria",
    27: "Sant Pantaleó, Santa Natàlia de Còrdova",
    28: "Sant Nazari, Sant Cels",
    29: "Santa Marta, Sant Llàtzer",
    30: "Sant Pere Crisòleg, Sant Abdó",
    31: "Sant Ignasi de Loiola, Sant Germà"
}

def obtener_santoral_seguro():
    """Obtiene el texto del santoral de la base de datos interna o una fuente fiable."""
    ahora = datetime.now()
    dia = ahora.day
    mes = ahora.month
    
    # Solo tenemos Julio por ahora. Si no es Julio, usamos el fallback.
    if mes == 7:
        santos_hoy = SANTORAL_JULIO.get(dia)
        if santos_hoy:
            return f"Avui, {dia} de Julio, se celebra:\n\n{santos_hoy}"
    
    # Fallback si no hay datos internos o no es Julio
    fecha_hoy_corta = ahora.strftime("%d/%m")
    return f"Santoral d'avui ({fecha_hoy_corta})"

def enviar_notificacion():
    # Usamos la fuente segura interna para el texto
    santoral_texto = obtener_santoral_seguro()
    
    # Extraemos el primer nombre de santo principal para la imagen.
    # Buscamos 'Sant' o 'Santa' seguido del primer nombre.
    # Usamos un fallback genérico si no hay coincidencias claras.
    import re
    nombre_santo_para_ia = "Saint"
    match = re.search(r'(Sant[a-z]*\s+[A-ZÀ-Ú][a-zà-ú]+)', santoral_texto)
    if match:
        nombre_santo_para_ia = match.group(1)
    else:
        # Si falla la extracción, usamos el número del día.
        nombre_santo_para_ia = f"Saint of day {datetime.now().day}"

    # Generamos la imagen con Pollinations, usando el nombre específico y seed diaria
    seed_dia = datetime.now().strftime("%Y%m%d")
    prompt = f"Classical Catholic icon painting of {nombre_santo_para_ia}, holy icon art style, detailed"
    prompt_encoded = urllib.parse.quote(prompt)
    
    url_imagen = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=800&height=600&seed={seed_dia}&nologo=true"
    
    # Configuración de NTFY
    topic = os.getenv("TOPIC_NTFY", "santoral-diario-2026")
    url_ntfy = f"https://ntfy.sh/{topic}"
    fecha_hoy_corta = datetime.now().strftime("%d/%m")
    
    headers = {
        "Title": f"Santoral d'Avui ({fecha_hoy_corta})",
        "Attach": url_imagen, # Adjunta la imagen
        "Tags": "calendar,church"
    }
    
    # Enviamos la notificación
    print(f"Enviando notificación para: {nombre_santo_para_ia}...")
    try:
        response = requests.post(url_ntfy, data=santoral_texto.encode('utf-8'), headers=headers, timeout=10)
        print(f"Respuesta de ntfy: {response.status_code}")
    except Exception as e:
        print(f"Error al enviar notificación: {e}")

if __name__ == "__main__":
    enviar_notificacion()
    
