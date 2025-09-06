import requests
from utils.process_pdf import process_pdf
from typing import List

# --- Configurações do Automatus ---
AUTOMATUS_BASE_URL = "https://environment-smartcenter.almaden.app"
USERNAME = ''
PASSWORD = ''
DOMAIN = "AUTOMATOS"

# --- Função para gerar o token Bearer ---
def get_token() -> str:
    url = f"{AUTOMATUS_BASE_URL}/api/authenticate"
    print(f"[DEBUG] Solicitando token em: {url}")
    try:
        resp = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token")
        if not token:
            raise Exception("Não foi possível obter token")
        print("[DEBUG] Token obtido com sucesso")
        return token
    except Exception as e:
        print(f"[ERROR] Falha ao obter token: {e}")
        raise

# --- Função para validar hostname do ativo ---
def validate_hostname(token: str, serial_number: str, hostname: str) -> bool:
    url = f"{AUTOMATUS_BASE_URL}/api/distribution/api/express/distribution"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "machineId": serial_number,
        "package": "",
        "domain": DOMAIN,
        "user": USERNAME,
        "password": PASSWORD,
        "irradiadora": hostname
    }
    print(f"[DEBUG] Validando hostname para serial '{serial_number}' e hostname '{hostname}'")
    try:
        resp = requests.post(url, headers=headers, json=body)
        if resp.status_code == 200:
            data = resp.json()
            status = data.get("status", False)
            print(f"[DEBUG] Resultado da validação: {status}")
            return status
        else:
            print(f"[ERROR] Erro HTTP {resp.status_code} ao validar hostname: {resp.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Exceção ao validar hostname: {e}")
        return False

# --- Função principal de processamento ---
def process_and_validate(files: List[str]) -> List[dict]:
    print("[INFO] Iniciando processamento dos PDFs...")
    
    # 1️⃣ Gera token
    token = get_token()
    
    all_records = []

    for pdf_path in files:
        print(f"[INFO] Processando PDF: {pdf_path}")
        try:
            registros = process_pdf(pdf_path)
            print(f"[DEBUG] {len(registros)} registros extraídos do PDF")
        except Exception as e:
            print(f"[ERROR] Falha ao processar PDF {pdf_path}: {e}")
            continue

        for registro in registros:
            serial = registro.get("serialNumber")
            host = registro.get("hostname")
            if serial and host:
                try:
                    registro["hostname_valid"] = validate_hostname(token, serial, host)
                except Exception as e:
                    registro["hostname_valid"] = False
                    registro["hostname_error"] = str(e)
                    print(f"[ERROR] Falha ao validar hostname: {e}")
            else:
                registro["hostname_valid"] = None
                print(f"[DEBUG] Serial ou hostname ausente: serial={serial}, hostname={host}")

        all_records.extend(registros)

    print(f"[INFO] Processamento finalizado. Total de registros: {len(all_records)}")
    return all_records
