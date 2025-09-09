import re

def validar_hostname(hostname: str, matricula: str = None) -> bool:

    if not hostname:
        return False

    hostname = hostname.strip().upper()

    padrao_escritorio = re.compile(
        r'^(NAK|DAK)'                # prefixo
        r'(5G)?'                     # opcional "5G" logo após prefixo
        r'[A-Z]{2}'                  # sigla do estado (duas letras)
        r'(5G)?'                     # opcional "5G" logo após estado
        r'(\d+)'                     # matrícula (um ou mais dígitos)
        r'([-_.]?\d+)?$'             # sufixo opcional (ex: -1, _2, .3)
    )

    m = padrao_escritorio.match(hostname)
    if m:
        matricula_extraida = m.group(4)  # matrícula é o quarto grupo
        if matricula and matricula_extraida != matricula:
            return False
        return True

    padrao_loja = re.compile(
        r'^(NAK|DAK)'                # prefixo
        r'C\d{3}'                    # código da loja (C + 3 números)
        r'(AV|PDV|GFA)'              # função da máquina
        r'\d{3}$'                    # número sequencial (3 dígitos)
    )

    if padrao_loja.match(hostname):
        return True

    return False
