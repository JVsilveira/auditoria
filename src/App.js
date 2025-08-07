import React, { useState } from "react"
import axios from "axios"
import "./App.css"
import { extractPdfText } from "./utils/ExtractText"
import { extractDevolucaoData } from "./utils/ExtractDev"
import { extractConcessaoData } from "./utils/ExtractCon"

export default function App() {
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [tipoTermo, setTipoTermo] = useState("") // "concessao" ou "devolucao"

  const [dados, setDados] = useState({
    assinaturaValida: null,
    notebookTipo: "",
    notebookModel: "",
    notebookBrand: "",
    serialNumber: "",
    modelMonitor: "",
    serialMonitor: "",
    accessories: [],
    assetNumber: "",
    nfNumber: "",
  })

  const handleFileChange = async event => {
    const file = event.target.files[0]
    if (file) {
      setError("")
      setLoading(true)
      setTipoTermo("")
      setDados({
        assinaturaValida: null,
        notebookTipo: "",
        notebookModel: "",
        notebookBrand: "",
        serialNumber: "",
        modelMonitor: "",
        serialMonitor: "",
        accessories: [],
        assetNumber: "",
        nfNumber: "",
      })

      try {
        const text = await extractPdfText(file)
        console.log("Texto extraído:", text)

        // Detecta automaticamente se é termo de concessão ou devolução
        const textoMinusculo = text.toLowerCase()
        const isConcessao =
          textoMinusculo.includes("termo de concessão") ||
          textoMinusculo.includes("entrego para uso")
        const isDevolucao =
          textoMinusculo.includes("termo de devolução") ||
          textoMinusculo.includes("devolução de equipamento")

        if (isConcessao) {
          const extraidos = extractConcessaoData(text)
          setDados(extraidos)
          setTipoTermo("concessao")
        } else if (isDevolucao) {
          const extraidos = extractDevolucaoData(text)
          setDados(extraidos)
          setTipoTermo("devolucao")
        } else {
          setError("Tipo de termo não reconhecido.")
          return
        }

        if (!dados.assinaturaValida) {
          console.warn("Documento NÃO assinado ou sem CPF/RG válido.")
        } else {
          console.log("Documento assinado e válido.")
        }
      } catch (err) {
        setError("Falha ao ler PDF.")
        console.error("Erro ao processar o PDF:", err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleEnviarParaServidor = async () => {
    if (dados.assinaturaValida === false) {
      alert("O documento não está assinado corretamente.")
      return
    }

    const token = localStorage.getItem("token")
    const linhasParaPlanilha = []

    const accessoriesCounted = dados.accessories.map(item => ({
      name: item,
      quantidade: 1,
    }))

    accessoriesCounted.push({ name: dados.notebookModel, quantidade: 1 })

    if (dados.modelMonitor && dados.serialMonitor) {
      accessoriesCounted.push({
        name: dados.modelMonitor,
        quantidade: 1,
        serialNumber: dados.serialMonitor,
      })
    }

    const linhaNotebook = {
      tipo: dados.notebookTipo || "N/A",
      serialNumber: dados.serialNumber || "N/A",
      modelo: dados.notebookModel || "N/A",
      marca: dados.notebookBrand || "N/A",
      accessoriesCounted,
      disponibilidade: tipoTermo === "concessao" ? "Em uso" : "Em estoque",
      assetNumber: dados.assetNumber || "",
      nfNumber: dados.nfNumber || "",
    }

    linhasParaPlanilha.push(linhaNotebook)

    if (dados.modelMonitor || dados.serialMonitor) {
      linhasParaPlanilha.push({
        tipo: "Monitor",
        serialNumber: dados.serialMonitor || "N/A",
        modelo: dados.modelMonitor || "N/A",
        marca: "N/A",
        disponibilidade: tipoTermo === "concessao" ? "Em uso" : "Em estoque",
      })
    }

    try {
      for (const linha of linhasParaPlanilha) {
        const rota = tipoTermo === "concessao" ? "/api/saida" : "/api/entrada"
        await axios.post(rota, linha, {
          headers: { Authorization: `Bearer ${token}` },
        })
      }
      alert("Dados enviados ao servidor com sucesso!")
    } catch (error) {
      alert("Erro ao enviar dados para o servidor.")
      console.error("Erro ao enviar:", error)
    }
  }

  return (
    <div className="container">
      <input
        type="file"
        id="fileUpload"
        accept="application/pdf"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      <label htmlFor="fileUpload" className="upload-btn">
        Selecionar PDF
      </label>

      {dados.assinaturaValida !== null && (
        <p className={dados.assinaturaValida ? "success-text" : "error-text"}>
          {dados.assinaturaValida
            ? "✅ Documento assinado e válido"
            : "❌ Documento NÃO assinado corretamente"}
        </p>
      )}

      <button
        className="send-btn"
        onClick={handleEnviarParaServidor}
        disabled={loading || !tipoTermo}
      >
        {loading
          ? "Processando..."
          : tipoTermo === "concessao"
          ? "Enviar saída para o servidor"
          : tipoTermo === "devolucao"
          ? "Enviar entrada para o servidor"
          : "Enviar"}
      </button>

      {(dados.notebookTipo ||
        dados.notebookModel ||
        dados.notebookBrand ||
        dados.serialNumber ||
        dados.modelMonitor ||
        dados.accessories.length > 0) && (
        <div className="info-section">
          <h3>Tipo de termo detectado: {tipoTermo.toUpperCase()}</h3>

          <h3>Dados extraídos:</h3>

          <h4>Notebook</h4>
          <p>
            <strong>Tipo:</strong> {dados.notebookTipo || "Não encontrado"}
          </p>
          <p>
            <strong>Modelo:</strong> {dados.notebookModel || "Não encontrado"}
          </p>
          <p>
            <strong>Marca:</strong> {dados.notebookBrand || "Não encontrado"}
          </p>
          <p>
            <strong>Nº de Série:</strong>{" "}
            {dados.serialNumber || "Não encontrado"}
          </p>
          <p>
            <strong>Número do Ativo:</strong>{" "}
            {dados.assetNumber || "Não encontrado"}
          </p>
          <p>
            <strong>Nota Fiscal:</strong> {dados.nfNumber || "Não encontrado"}
          </p>

          <h4>Monitor</h4>
          <p>
            <strong>Modelo:</strong> {dados.modelMonitor || "Não encontrado"}
          </p>
          <p>
            <strong>Série:</strong> {dados.serialMonitor || "Não encontrado"}
          </p>

          <h4>Acessórios</h4>
          {dados.accessories.length > 0 ? (
            <ul>
              {dados.accessories.map((acc, idx) => (
                <li key={idx}>{acc}</li>
              ))}
            </ul>
          ) : (
            <p>Nenhum acessório encontrado</p>
          )}
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
    </div>
  )
}
