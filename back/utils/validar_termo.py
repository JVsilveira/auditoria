import re
# from utils.consult_hostname import validate_hostname

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

    # Se houver modelo de monitor, o serial também deve existir e não ser apenas "-"
    if modelo_monitor and not re.fullmatch(r"-+", modelo_monitor):
        if not serial_monitor or re.fullmatch(r"-+", serial_monitor):
            return False

    # --- Verifica chamado somente para concessão ---
    if dados.get("TERMO") == "CONCESSÃO":
        chamado = str(dados.get("CHAMADO", "")).strip().upper()

        # Chamado vazio → erro
        if not chamado:
            return False

        # ROLLOUT é válido
        if chamado in ["ROLLOUT", "ROLOUT"]:
            return True

        # REQ ou INC com zeros apenas → erro
        if re.match(r"^(REQ|INC)0*$", chamado):
            return False

        # REQ ou INC seguido de números → válido
        if re.match(r"^(REQ|INC)\d+$", chamado):
            return True

        # Qualquer outro valor → erro
        return False
    
    # if not validate_hostname(dados.get("serial_number", ""), dados.get("hostname", "")):
    #     return False

    # Para termos de devolução, RAT ou outros, apenas valida assinatura, monitor e NF
    return True
