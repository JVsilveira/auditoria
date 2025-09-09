import re
from utils.validar_hostname import validar_hostname   

def validar_termo(dados: dict) -> bool:

    # --- Lista de modelos que dispensam validação de NF ---
    modelos_excecao_nf = [
        "OPTIPLEX 7070", "LATITUDE 7400", "LATITUDE 5400", "LATITUDE 5420",
        "7070", "7400", "5400", "5420"
    ]

    # --- Tipos de ativo ---
    tipos_validos = ["DESKTOP", "MINIDESK", "MINIDESKTOP", "NOTEBOOK"]

    # --- Marcas ---
    marcas_validas = ["DELL", "LENOVO", "HP", "ACER", "ASUS", "SAMSUNG", "POSITIVO", "APPLE"]

    modelo = str(dados.get("MODELO", "")).strip().upper()
    tipo = str(dados.get("TIPO", "")).strip().upper()
    marca = str(dados.get("MARCA", "")).strip().upper()
    
    # --- Valida NF ---
    nf = str(dados.get("NF", "")).strip()
    if modelo not in modelos_excecao_nf:
        if not nf or re.fullmatch(r"0+", nf):
            return False

    # --- Verifica assinatura ---
    if not dados.get("ASSINADO", False):
        return False

    # --- Verifica monitor ---
    modelo_monitor = str(dados.get("MODELO MONITOR", "")).strip()
    serial_monitor = str(dados.get("SERIAL MONITOR", "")).strip()

    if modelo_monitor and not re.fullmatch(r"-+", modelo_monitor):
        if not serial_monitor or re.fullmatch(r"-+", serial_monitor):
            return False

    # --- Verifica tipo ---
    if dados.get("TERMO") == "CONCESSÃO" or dados.get("TERMO") == "DEVOLUÇÃO":
        if  tipo not in tipos_validos:
            return False

    # --- Verifica marca ---
    if dados.get("TERMO") == "CONCESSÃO" or dados.get("TERMO") == "DEVOLUÇÃO":
        if marca not in marcas_validas:
            return False

    # --- Verifica hostname ---
    if dados.get("TERMO") == "CONCESSÃO":
        hostname = str(dados.get("HOSTNAME", "")).strip()
        matricula = str(dados.get("MATRICULA", "")).strip()
        if not validar_hostname(hostname, matricula if matricula else None):
            return False

    # --- Verifica chamados ---
    if dados.get("TERMO") == "CONCESSÃO":
        chamado = str(dados.get("CHAMADO", "")).strip().upper()

        if not chamado:
            return False

        if chamado in ["ROLLOUT", "ROLOUT"]:
            return True

        if re.match(r"^(REQ|INC)0*$", chamado):
            return False

        if re.match(r"^(REQ|INC)\d+$", chamado):
            return True

        return False
    
    return True
