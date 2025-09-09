import re
from utils.validar_hostname import validar_hostname   

def validar_termo(dados: dict) -> bool:
    # --- Lista de modelos que dispensam validação de NF ---
    modelos_excecao_nf = [
        "OPTIPLEX 7070", "LATITUDE 7400", "LATITUDE 5400", "LATITUDE 5420",
        "7070", "7400", "5400", "5420"
    ]

    modelo = str(dados.get("MODELO", "")).strip().upper()
    
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

    # --- Verifica hostname ---
    if dados.get("TERMO") == "CONCESSÃO":
        hostname = str(dados.get("HOSTNAME", "")).strip()
        matricula = str(dados.get("MATRICULA", "")).strip()
        if not validar_hostname(hostname, matricula if matricula else None):
            return False

    # --- Verifica chamado somente para concessão ---
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
