import re
from utils.extract_sign import validar_assinatura

def extract_segundo_termo(item_name: str, text: str) -> str:

    match = re.search(re.escape(item_name), text, re.I)
    if not match:
        return "----------" 

    substring = text[match.end():]

    termos = re.findall(r"(Sim|Não)", substring, re.I)
    if len(termos) >= 2:
        return termos[1].strip()  

    return "---------"

def extract_devolucao_data(text: str) -> dict:
    assinatura_valida = validar_assinatura(text)
    
    # Inicialização de variáveis principais
    notebook_tipo = notebook_model = notebook_brand = serial_number = ""
    model_monitor = serial_monitor = ""

    # --- Dados do notebook ---
    notebook_tipo_match = re.search(r"tipo[^\w]+([A-Za-z0-9\s\-]+)", text, re.I)
    notebook_model_match = re.search(r"modelo[^\w]+([A-Za-z0-9\s\-]+)", text, re.I)
    notebook_brand_match = re.search(r"marca[^\w]+([A-Za-z0-9\s\-]+)", text, re.I)
    serial_number_match = re.search(r"nº de série\s*[:\-\s]*([A-Za-z0-9]+)", text, re.I)

    if notebook_tipo_match:
        notebook_tipo = notebook_tipo_match.group(1).strip()
    if notebook_model_match:
        notebook_model = notebook_model_match.group(1).strip()
    if notebook_brand_match:
        notebook_brand = notebook_brand_match.group(1).strip()
    if serial_number_match:
        serial_number = serial_number_match.group(1).replace(" ", "").strip()

    # --- Dados do monitor ---
    monitor_match = re.search(
    r"Monitor\s*\(Marca\/Modelo:\s*([^\)]*?)\s*Nro Série\s*:\s*([A-Za-z0-9\-]+)\)", 
    text, re.I
    )
    if monitor_match:
        model_monitor = monitor_match.group(1).strip()
        serial_monitor = monitor_match.group(2).strip()
    if not model_monitor or model_monitor.strip() == "-":
     model_monitor = "----------"        
    if not serial_monitor or serial_monitor.strip() == "-":
     serial_monitor = "----------"    
           

    # --- Acessórios ---
    monitor = extract_segundo_termo("Monitor", text)
    mouse = extract_segundo_termo("Mouse", text)
    teclado = extract_segundo_termo("Teclado", text)
    headset = extract_segundo_termo("Headset", text)
    kit = extract_segundo_termo("Kit boas-vindas", text)
    webcam = extract_segundo_termo("Webcam", text)
    hub = extract_segundo_termo("Hub USB", text)
    suporte = extract_segundo_termo("Suporte Ergonômico", text)
    caboSeguranca = extract_segundo_termo("Cabo de Segurança", text)
    mochila = extract_segundo_termo("Maleta/Mochila para Notebook", text)
    dockstation = extract_segundo_termo("Dock Station", text)
    lacre = extract_segundo_termo("Lacre de Segurança", text)
    caboRCA = extract_segundo_termo("Cabo RCA / Cabo paralelo para unidade externa", text)
    bateria = extract_segundo_termo("Bateria Extra", text)
    carregadorExtra = extract_segundo_termo("Carregador Extra", text)
    caboMonitor = extract_segundo_termo("Cabo de Força do Monitor", text)
    fonte = extract_segundo_termo("Fonte", text)
    adaptadorHdmi = extract_segundo_termo("Adaptador HDMI", text)

    return {
        "TERMO": "DEVOLUÇÃO",
        "ASSINADO": assinatura_valida,
        "TIPO": notebook_tipo,
        "MODELO": notebook_model,
        "MARCA": notebook_brand,
        "SERIAL": serial_number,
        "MONITOR": monitor,
        "MODELO MONITOR": model_monitor,
        "SERIAL MONITOR": serial_monitor,
        "PATRIMÔNIO": "----------",
        "NF": "----------",
        "CHAMADO": "----------",
        "HOSTNAME": "----------",
        "RAM": "----------",
        "MEMÓRIA": "----------",
        "MOUSE": mouse, 
        "TECLADO": teclado,
        "HEADSET": headset,
        "KIT BOAS-VINDAS": kit,
        "WEBCAM": webcam,    
        "HUB USB": hub,
        "SUPORTE ERGONÔMICO": suporte,
        "CABO DE SEGURANÇA": caboSeguranca,
        "MOCHILA": mochila,
        "DOCK STATION": dockstation,
        "LACRE DE SEGURANÇA": lacre,
        "CABO RCA": caboRCA,
        "BATERIA EXTRA": bateria,
        "CARREGADOR EXTRA": carregadorExtra, 
        "CABO DE FORÇA DO MONITOR": caboMonitor,
        "FONTE": fonte,
        "ADAPTADOR HDMI": adaptadorHdmi
    }
