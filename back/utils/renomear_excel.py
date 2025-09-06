import os
import re
from utils.extract_text import extract_text_from_pdf  # função que retorna o texto do PDF

def renomear_pdf(caminho_antigo: str) -> str:
    """
    Renomeia o PDF de acordo com o tipo de termo, nome, matrícula e serial do ativo.
    Captura automaticamente os dados essenciais do texto.
    Retorna o novo caminho do arquivo.
    """

    # --- Extrair texto do PDF ---
    texto = extract_text_from_pdf(caminho_antigo)
    texto_lower = texto.lower()

    # --- Tipo de termo ---
    if "recebendo para o uso" in texto_lower:
        tipo = "concessao"
    elif "declaro ter devolvido" in texto_lower or "devolvido o equipamento" in texto_lower:
        tipo = "devolucao"
    else:
        tipo = "desconhecido"

    # --- Capturar nome e matrícula ---
    if tipo == "concessao":
        # Concessão: "Eu, Nome do Colaborador,"
        nome_match = re.search(r"eu,\s*([A-Za-zÀ-ú\s]+?),", texto, re.IGNORECASE)
        nome = nome_match.group(1).strip() if nome_match else "Desconhecido"
        matricula_match = re.search(r"matricul[ai]\s*[:]?[\s]*([A-Za-z0-9]+)", texto, re.IGNORECASE)
        matricula = matricula_match.group(1).strip() if matricula_match else "0000"
    elif tipo == "devolucao":
        # Devolução: "Eu, NomeSobrenomeMatricula F8054687,"
        nome_match = re.search(r"eu,\s*([A-Za-zÀ-ú\s]+?)matr[ií]cula", texto, re.IGNORECASE)
        nome = nome_match.group(1).strip() if nome_match else "Desconhecido"
        matricula_match = re.search(r"matr[ií]cula\s*([A-Za-z0-9]+)", texto, re.IGNORECASE)
        matricula = matricula_match.group(1).strip() if matricula_match else "0000"
    else:
        nome = "Desconhecido"
        matricula = "0000"

    # --- Limpar múltiplos espaços do nome ---
    nome = re.sub(r"\s+", " ", nome)

    # --- Capturar serial do ativo ---
    serial_match = re.search(r"n[ºo] de s[ée]rie\s*[:]?[\s]*([A-Za-z0-9]+)", texto, re.IGNORECASE)
    serial = serial_match.group(1).strip() if serial_match else "XXXX"

    # --- Criar prefixo ---
    prefixo = "TR" if tipo.lower() == "concessao" else "TD" if tipo.lower() == "devolucao" else "UNK"

    # --- Montar novo nome com espaços ---
    novo_nome = f"{prefixo} {nome} {matricula} {serial}.pdf"
    novo_caminho = os.path.join(os.path.dirname(caminho_antigo), novo_nome)

    # --- Renomear arquivo ---
    try:
        os.rename(caminho_antigo, novo_caminho)
    except Exception as e:
        print(f"Erro ao renomear {caminho_antigo}: {e}")
        novo_caminho = caminho_antigo  # mantém o nome original em caso de erro

    return novo_caminho
