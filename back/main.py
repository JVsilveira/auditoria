import os
import uuid
import pandas as pd
import asyncio

from fastapi import FastAPI, UploadFile, File, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from utils.format_excel import format_excel
from utils.extract_text import extract_text_from_pdf
from utils.extract_con import extract_concessao_data
from utils.extract_dev import extract_devolucao_data
from utils.renomear_excel import renomear_pdf

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
    "NOME", "TERMO", "ASSINADO", "TIPO", "MODELO",
    "MARCA", "SERIAL", "MONITOR", "SERIAL MONITOR", "PATRIMÔNIO", "NF", "CHAMADO",
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

# --- Processamento de PDF ---
def process_pdf(path: str) -> dict:
    texto = extract_text_from_pdf(path)
    texto_lower = texto.lower()
    if "termo de concessão" in texto_lower or "entrego para uso" in texto_lower:
        return extract_concessao_data(texto)
    elif "termo de devolução" in texto_lower or "devolução de equipamento" in texto_lower:
        return extract_devolucao_data(texto)
    else:
        return {"tipo": "desconhecido"}

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
    chart_data = {"ok": 0, "erro": 0, "concessao": 0, "devolucao": 0, "desconhecido": 0}
    total = len(pdfs)

    for idx, pdf in enumerate(pdfs):
        temp_path = f"temp_{uuid.uuid4().hex}_{pdf.filename}"
        contents = await pdf.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        try:
            # Renomeia PDF
            novo_caminho = renomear_pdf(temp_path)

            # Move para a pasta "termos auditados"
            novo_caminho_final = os.path.join(PASTA_TERMO, os.path.basename(novo_caminho))
            os.replace(novo_caminho, novo_caminho_final)
            novo_caminho = novo_caminho_final

            # Processa PDF
            dados = process_pdf(novo_caminho)
            dados["NOME"] = os.path.basename(novo_caminho)
            
            append_row_to_excel(dados)

            resultados.append({
                "NOME": os.path.basename(novo_caminho),
                "status": "ok",
                "tipo": dados.get("tipo")
            })

            chart_data["ok"] += 1
            if dados.get("tipo") in chart_data:
                chart_data[dados.get("tipo")] += 1
            else:
                chart_data["desconhecido"] += 1

        except Exception as e:
            resultados.append({"NOME": pdf.filename, "status": "erro", "erro": str(e)})
            chart_data["erro"] += 1
        finally:
            # Remove temporário se ainda existir
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
    chart_data = {"ok": 0, "erro": 0, "concessao": 0, "devolucao": 0, "desconhecido": 0}
    total = len(arquivos_pdf)

    for idx, nome in enumerate(arquivos_pdf):
        path = os.path.join(diretorio, nome)
        try:
            # Renomeia PDF
            novo_caminho = renomear_pdf(path)

            # Move para a pasta "termos auditados"
            novo_caminho_final = os.path.join(PASTA_TERMO, os.path.basename(novo_caminho))
            os.replace(novo_caminho, novo_caminho_final)
            novo_caminho = novo_caminho_final

            # Processa PDF
            dados = process_pdf(novo_caminho)
            dados["NOME"] = os.path.basename(novo_caminho)
            
            append_row_to_excel(dados)

            resultados.append({"NOME": os.path.basename(novo_caminho), "status": "ok", "tipo": dados.get("tipo")})
            chart_data["ok"] += 1
            if dados.get("tipo") in chart_data:
                chart_data[dados.get("tipo")] += 1
            else:
                chart_data["desconhecido"] += 1

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
