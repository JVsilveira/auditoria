import re
from utils.extract_con import extract_concessao_data
from utils.extract_dev import extract_devolucao_data

# padrões tolerantes
PAT_CON = re.compile(r"(termo\s*de\s*concess(?:a|ã)o|entrego\s*para\s*uso)", re.I)
PAT_DEV = re.compile(r"(termo\s*de\s*devolu(?:c|ç)(?:a|ã)o|devolu(?:c|ç)(?:a|ã)o\s*de\s*equipamento)", re.I)

def extract_rat_data(text: str) -> list:

    resultados = []

    m_con = PAT_CON.search(text)
    m_dev = PAT_DEV.search(text)

    texto_con = texto_dev = ""

    if m_con and m_dev:
        if m_con.start() < m_dev.start():
            texto_con = text[m_con.start():m_dev.start()]
            texto_dev = text[m_dev.start():]
        else:
            texto_dev = text[m_dev.start():m_con.start()]
            texto_con = text[m_con.start():]
    elif m_con:
        texto_con = text[m_con.start():]
    elif m_dev:
        texto_dev = text[m_dev.start():]

    # extrai concessão
    if texto_con:
        dados_con = extract_concessao_data(texto_con)
        resultados.append(dados_con)

    # extrai devolução
    if texto_dev:
        dados_dev = extract_devolucao_data(texto_dev)
        resultados.append(dados_dev)

    return resultados
