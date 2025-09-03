import re

assinatura_regex = re.compile(r"(?:assinatura|/sign/)", re.I)
cpf_rg_regex = re.compile(r"\b(\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{7,10}|[A-Z]{2}-\d{2}\.?\d{3}\.?\d{3})\b")

def validar_assinatura(texto):
        return bool(assinatura_regex.search(texto)) and bool(cpf_rg_regex.search(texto))