import re
from utils.extract_text import extract_text_from_pdf    
from utils.extract_con import extract_concessao_data
from utils.extract_dev import extract_devolucao_data
from utils.extract_rat import extract_rat_data
import unidecode

PAT_CON = re.compile(r"(termo\s*de\s*concess(?:a|ã)o|entrego\s*para\s*uso)", re.I)
PAT_DEV = re.compile(r"(termo\s*de\s*devolu(?:c|ç)(?:a|ã)o|devolu(?:c|ç)(?:a|ã)o\s*de\s*equipamento)", re.I)
PAT_RAT = re.compile(r"relatorio de ativacao tecnica", re.I)

def process_pdf(path: str) -> list:
    texto = extract_text_from_pdf(path)
    texto_lower = texto.lower()
    texto_normalizado = unidecode.unidecode(texto_lower)

    m_con = PAT_CON.search(texto_lower)
    m_dev = PAT_DEV.search(texto_lower)

    registros = []

    # --- Concessão e Devolução ---
    if m_con and m_dev:
        if m_con.start() < m_dev.start():
            trecho_con = texto[m_con.start():m_dev.start()]
            trecho_dev = texto[m_dev.start():]
        else:
            trecho_dev = texto[m_dev.start():m_con.start()]
            trecho_con = texto[m_con.start():]

        registro_con = extract_concessao_data(trecho_con)
        registro_con["TERMO"] = "CONCESSÃO"
        registros.append(registro_con)

        registro_dev = extract_devolucao_data(trecho_dev)
        registro_dev["TERMO"] = "DEVOLUÇÃO"
        registros.append(registro_dev)

    elif m_con:
        registro_con = extract_concessao_data(texto[m_con.start():])
        registro_con["TERMO"] = "CONCESSÃO"
        registros.append(registro_con)

    elif m_dev:
        registro_dev = extract_devolucao_data(texto[m_dev.start():])
        registro_dev["TERMO"] = "DEVOLUÇÃO"
        registros.append(registro_dev)

    # --- RAT independente ---
    for m_rat in PAT_RAT.finditer(texto_normalizado):
        registro_rat = extract_rat_data(texto[m_rat.start():])
        # Garante que seja lista
        if isinstance(registro_rat, dict):
            registro_rat = [registro_rat]
        for r in registro_rat:
            r["TERMO"] = "RAT"
            registros.append(r)

    # --- Se não houver nenhum tipo identificado ---
    if not registros:
        registros.append({"TERMO": "DESCONHECIDO"})

    return registros
