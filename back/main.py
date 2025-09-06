import os
import uuid
import pandas as pd
import asyncio

from fastapi import FastAPI, UploadFile, File, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from utils.format_excel import format_excel
from utils.process_pdf import process_pdf
from utils.renomear_excel import renomear_pdf
from utils.validar_termo import validar_termo



# --- Configuração do app ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Excel e colunas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAIDA_XLSX = os.path.join(BASE_DIR, "resultado.xlsx")
PASTA_TERMO = os.path.join(BASE_DIR, "termos auditados")  # nova pasta
os.makedirs(PASTA_TERMO, exist_ok=True)  # garante que exista

COLUNAS = [
    "NOME", "TERMO", "STATUS TERMO", "ASSINADO", "TIPO", "MODELO",
    "MARCA", "SERIAL", "MONITOR","MODELO MONITOR", "SERIAL MONITOR", "PATRIMÔNIO", "NF", "CHAMADO",
    "HOSTNAME", "RAM", "MEMÓRIA", "MOUSE", "TECLADO", "HEADSET", "KIT BOAS-VINDAS", "WEBCAM", "HUB USB",
    "SUPORTE ERGONÔMICO", "CABO DE SEGURANÇA", "MOCHILA", "DOCK STATION", "LACRE DE SEGURANÇA",
    "CABO RCA", "BATERIA EXTRA", "CARREGADOR EXTRA", 
    "CABO DE FORÇA DO MONITOR", "FONTE", "ADAPTADOR HDMI"
]

def ensure_excel_exists():
    if not os.path.exists(SAIDA_XLSX):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_excel(SAIDA_XLSX, index=False)
        format_excel(SAIDA_XLSX)
        print("Excel criado e formatado: resultado.xlsx")

def append_row_to_excel(dados: dict):
    ensure_excel_exists()
    try:
        df = pd.read_excel(SAIDA_XLSX)
        df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
        df.to_excel(SAIDA_XLSX, index=False)
        format_excel(SAIDA_XLSX)
        print(f"Linha adicionada: {dados.get('NOME', 'Desconhecido')}")
    except Exception as e:
        print(f"Erro ao escrever no Excel: {e}")



# --- WebSocket ---
connected_clients = []

@app.websocket("/ws/progresso")
async def websocket_progresso(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            await asyncio.sleep(1)
    except Exception:
        connected_clients.remove(ws)

async def broadcast_progress(progress: int):
    for ws in connected_clients:
        try:
            await ws.send_json({"progress": progress})
        except Exception:
            connected_clients.remove(ws)

# --- Upload PDFs ---
@app.post("/upload")
async def upload_pdfs(pdfs: List[UploadFile] = File(...)):
    ensure_excel_exists()
    resultados = []
    chart_data = {"ok": 0, "erro": 0, "concessao": 0, "devolucao": 0, "rat": 0, "desconhecido": 0}
    total = len(pdfs)

    TIPOS_MAP = {
        "CONCESSÃO": "concessao",
        "DEVOLUÇÃO": "devolucao",
        "RAT": "rat",
        "DESCONHECIDO": "desconhecido"
    }

    for idx, pdf in enumerate(pdfs):
        temp_path = f"temp_{uuid.uuid4().hex}_{pdf.filename}"
        contents = await pdf.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        try:
            novo_caminho = renomear_pdf(temp_path)
            novo_caminho_final = os.path.join(PASTA_TERMO, os.path.basename(novo_caminho))
            os.replace(novo_caminho, novo_caminho_final)
            novo_caminho = novo_caminho_final

            registros = process_pdf(novo_caminho)
            for dados in registros:
                dados["NOME"] = os.path.basename(novo_caminho)

                # Define status do termo
                if validar_termo(dados):
                    dados["STATUS TERMO"] = "OK"
                    status = "ok"
                else:
                    dados["STATUS TERMO"] = "ERRO"
                    status = "erro"

                append_row_to_excel(dados)

                resultados.append({
                    "NOME": os.path.basename(novo_caminho),
                    "status": status,
                    "tipo": dados.get("TIPO", "desconhecido")
                })

                # Atualiza estatísticas gerais
                if status == "erro":
                    chart_data["erro"] += 1
                else:
                    chart_data["ok"] += 1

                # Atualiza estatísticas por tipo de documento
                tipo_documento = TIPOS_MAP.get(dados.get("TERMO", "").upper(), "desconhecido")
                chart_data[tipo_documento] += 1

        except Exception as e:
            resultados.append({"NOME": pdf.filename, "status": "erro", "erro": str(e)})
            chart_data["erro"] += 1
        finally:
            if os.path.exists(temp_path) and temp_path != novo_caminho:
                os.remove(temp_path)

        await broadcast_progress(int((idx + 1) / total * 100))

    return {"resultados": resultados, "excelUrl": f"/download/{os.path.basename(SAIDA_XLSX)}", "chartData": chart_data}


# --- Processar pasta ---
@app.post("/processar-pasta")
async def processar_pasta(diretorio: str = Body(..., embed=True)):
    if not os.path.isdir(diretorio):
        return {"erro": f"O diretório '{diretorio}' não existe."}

    arquivos_pdf = [f for f in os.listdir(diretorio) if f.lower().endswith(".pdf")]
    if not arquivos_pdf:
        return {"erro": "Nenhum PDF encontrado no diretório."}

    resultados = []
    chart_data = {"ok": 0, "erro": 0, "concessao": 0, "devolucao": 0, "rat": 0, "desconhecido": 0}

    TIPOS_MAP = {
        "CONCESSÃO": "concessao",
        "DEVOLUÇÃO": "devolucao",
        "RAT": "rat",
        "DESCONHECIDO": "desconhecido"
    }

    total = len(arquivos_pdf)

    for idx, nome in enumerate(arquivos_pdf):
        path = os.path.join(diretorio, nome)
        try:
            novo_caminho = renomear_pdf(path)
            novo_caminho_final = os.path.join(PASTA_TERMO, os.path.basename(novo_caminho))
            os.replace(novo_caminho, novo_caminho_final)
            novo_caminho = novo_caminho_final

            registros = process_pdf(novo_caminho)
            for dados in registros:
                dados["NOME"] = os.path.basename(novo_caminho)

                if validar_termo(dados):
                    dados["STATUS TERMO"] = "OK"
                    status = "ok"
                else:
                    dados["STATUS TERMO"] = "ERRO"
                    status = "erro"

                append_row_to_excel(dados)

                resultados.append({
                    "NOME": os.path.basename(novo_caminho),
                    "status": status,
                    "tipo": dados.get("TIPO", "desconhecido")
                })

                if status == "erro":
                    chart_data["erro"] += 1
                else:
                    chart_data["ok"] += 1

                tipo_documento = TIPOS_MAP.get(dados.get("TERMO", "").upper(), "desconhecido")
                chart_data[tipo_documento] += 1

        except Exception as e:
            resultados.append({"NOME": nome, "status": "erro", "erro": str(e)})
            chart_data["erro"] += 1

        await broadcast_progress(int((idx + 1) / total * 100))

    return {"resultados": resultados, "excelUrl": f"/download/{os.path.basename(SAIDA_XLSX)}", "chartData": chart_data}

# --- Download Excel ---
@app.get("/download/{filename}")
def download_file(filename: str):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename
        )
    return {"erro": "Arquivo não encontrado."}
