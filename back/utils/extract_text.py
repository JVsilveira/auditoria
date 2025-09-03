import fitz
import re

def extract_text_from_pdf(path: str) -> str:
    try:
        doc = fitz.open(path)
        texto = ""
        for page in doc:
            texto += page.get_text()
        print (texto)         
        return re.sub(r"\s+", " ", texto).strip()
    except Exception as e:
        print(f"Erro ao abrir PDF {path}: {e}")
        return ""