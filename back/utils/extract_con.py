import re
from utils.extract_sign import validar_assinatura

def extract_primeiro_termo(item_name: str, text: str) -> str:
    match = re.search(re.escape(item_name), text, re.I)
    if not match:
        return "----------"
    substring = text[match.end():]
    termo = re.search(r"(Sim|Não)", substring, re.I)
    if termo:
        return termo.group(1).strip()
    return "----------"

def extract_valor_especial(item_name: str, text: str) -> str:
    match = re.search(re.escape(item_name), text, re.I)
    if not match:
        return "----------"
    substring = text[match.end():]
    termo = re.search(r"(\S+)", substring)  # pega a primeira palavra após o item
    if termo:
        valor = termo.group(1).strip()
        if valor.lower() in ["sim", "não", "nao"]:
            return "Sim" if valor.lower() == "sim" else "Não"
    return "----------"

def extract_concessao_data(text: str) -> dict:
    assinatura_valida = validar_assinatura(text)
    
    notebook_tipo = notebook_model = notebook_brand = serial_number = ""
    model_monitor = serial_monitor = ""
    asset_number = nf_number = numero_chamado = hostname = memoria = disco_rigido = ""

    # --- Informações principais ---
    notebook_tipo_match = re.search(r"um[^\w]+(\S[\w\s-]+)", text, re.I)
    notebook_model_match = re.search(r"modelo[^\w]+(\S[\w\s-]+)", text, re.I)
    notebook_brand_match = re.search(r"marca[^\w]+(\S[\w\s-]+)", text, re.I)
    serial_number_match = re.search(r"nº de série\s*[:\-\s]*([A-Za-z0-9\-]+)", text, re.I)
    nf_number_match = re.search(r"NF\s*nº?\s*(\d+)", text, re.I)
    asset_number_match = re.search(r"NÚMERO DO ATIVO\s*(\d+)", text, re.I)
    numero_chamado_match = re.search(r"NÚMERO DO CHAMADO\s*([A-Z0-9]+)", text, re.I)
    hostname_match = re.search(r"HOSTNAME\s*([A-Z0-9]+)", text, re.I)

    # --- Memória RAM ---
    memoria_match = re.search(r"MEMÓRIA\s*:\s*([\d]+\s*[Gg][Bb](?:\s*DDR[234])?)", text, re.I | re.S)
    if memoria_match:
        memoria = memoria_match.group(1).strip()

    # --- Disco Rígido (todos os discos) ---
    discos_match = re.findall(
        r"DISCO RÍGIDO\s*:\s*([A-Za-z0-9.\s-]*[\d]+\s*[Gg][Bb])",
        text,
        re.I
    )
    disco_rigido = ", ".join(discos_match) if discos_match else "----------"

    # --- Atribuindo valores principais ---
    if notebook_tipo_match:
        notebook_tipo = notebook_tipo_match.group(1).strip()
    if notebook_model_match:
        notebook_model = notebook_model_match.group(1).strip()
    if notebook_brand_match:
        notebook_brand = notebook_brand_match.group(1).strip()
    if serial_number_match:
        serial_number = serial_number_match.group(1).strip()
    if nf_number_match:
        nf_number = nf_number_match.group(1).strip()
    if asset_number_match:
        asset_number = asset_number_match.group(1).strip()
    if numero_chamado_match:
        numero_chamado = numero_chamado_match.group(1).strip()
    if hostname_match:
        hostname = hostname_match.group(1).strip()
    if not model_monitor or model_monitor.strip() == "-":
     model_monitor = "----------"    
    if not serial_monitor or serial_monitor.strip() == "-":
     serial_monitor = "----------"    

    # --- Periféricos ---
    mouse = extract_primeiro_termo("Mouse", text)
    teclado = extract_primeiro_termo("Teclado", text)
    headset = extract_primeiro_termo("Headset", text)
    kit = extract_primeiro_termo("Kit boas-vindas", text)
    webcam = extract_primeiro_termo("Webcam", text)
    hub = extract_valor_especial("Hub USB", text)
    suporte = extract_primeiro_termo("Suporte Ergonômico", text)
    caboSeguranca = extract_primeiro_termo("Cabo de Segurança", text)
    mochila = extract_primeiro_termo("Maleta/Mochila para Notebook", text)
    dockstation = extract_primeiro_termo("Dock Station", text)
    lacre = extract_primeiro_termo("Lacre de Segurança", text)
    caboRCA = extract_primeiro_termo("Cabo RCA / Cabo paralelo para unidade externa", text)
    bateria = extract_primeiro_termo("Bateria Extra", text)
    carregadorExtra = extract_primeiro_termo("Carregador Extra", text)
    caboMonitor = extract_valor_especial("Cabo de força do monitor", text)
    fonte = extract_valor_especial("Fonte", text)
    adaptadorHdmi = extract_primeiro_termo("Adaptador HDMI", text)

    return {
        "TERMO": "CONCESSÃO",
        "ASSINADO": assinatura_valida,
        "TIPO": notebook_tipo,
        "MODELO": notebook_model,
        "MARCA": notebook_brand,
        "SERIAL": serial_number,
        "MONITOR": model_monitor,
        "SERIAL MONITOR": serial_monitor,
        "PATRIMÔNIO": asset_number,
        "NF": nf_number,
        "CHAMADO": numero_chamado,
        "HOSTNAME": hostname,
        "RAM": memoria,
        "MEMÓRIA": disco_rigido,
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
