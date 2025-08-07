import './App.css';
import axios from "axios";
import React, { useState } from "react";
import { getDocument, GlobalWorkerOptions } from "pdfjs-dist";

GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js";


function App() {
  const [error, setError] = useState("");
  const [notebookTipo, setNotebookTipo] = useState("");
  const [notebookModel, setNotebookModel] = useState("");
  const [notebookBrand, setNotebookBrand] = useState("");
  const [modelMonitor, setModelMonitor] = useState("");
  const [serialMonitor, setSerialMonitor] = useState("");
  const [serialNumber, setSerialNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [accessories, setAccessories] = useState([]);
  const [assinaturaValida, setAssinaturaValida] = useState(null);

  const extractPdfText = async (file) => {
    const typedArray = new Uint8Array(await file.arrayBuffer());
    const pdf = await getDocument(typedArray).promise;

    let text = "";
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      text += textContent.items.map(item => item.str).join(" ");
    }

    text = text.replace(/\s+/g, " ").trim();
    text = text.replace(/\n/g, " ");

    return text;
  };

  // Regex para assinatura e CPF/RG
  const assinaturaRegex = /(?:assinatura|\/sign\/)/i;
  const cpfRgRegex = /\b(\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{7,10}|[A-Z]{2}-\d{2}\.?\d{3}\.?\d{3})\b/;

  const validarAssinatura = (textoExtraido) => {
    const temAssinatura = assinaturaRegex.test(textoExtraido);
    const temCpfOuRg = cpfRgRegex.test(textoExtraido);
    return temAssinatura && temCpfOuRg;
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setError("");
      setNotebookTipo("");
      setNotebookModel("");
      setNotebookBrand("");
      setSerialNumber("");
      setModelMonitor("");
      setSerialMonitor("");
      setLoading(true);
      setAccessories([]);
      setAssinaturaValida(null);

      try {
        const text = await extractPdfText(file);
        console.log("Texto extraído do PDF:", text);

        // ✅ Validação de assinatura + CPF/RG
        const assinaturaEhValida = validarAssinatura(text);
        setAssinaturaValida(assinaturaEhValida);

        if (!assinaturaEhValida) {
          console.warn("Documento NÃO assinado ou sem CPF/RG válido.");
        } else {
          console.log("Documento assinado e CPF/RG válido encontrado.");
        }

        // --- Extração de dados do Notebook ---
        const notebookTipoMatch = text.match(/tipo[^\w]+([A-Za-z0-9\s\-]+)/i);
        const notebookModelMatch = text.match(/modelo[^\w]+([A-Za-z0-9\s\-]+)/i);
        const notebookBrandMatch = text.match(/marca[^\w]+([A-Za-z0-9\s\-]+)/i);
        const serialNumberMatch = text.match(/nº de série\s*[:\-\s]*([A-Za-z0-9]+)/i);

        if (notebookTipoMatch) setNotebookTipo(notebookTipoMatch[1]);
        if (notebookModelMatch) setNotebookModel(notebookModelMatch[1]);
        if (notebookBrandMatch) setNotebookBrand(notebookBrandMatch[1]);
        if (serialNumberMatch) {
          const cleanedSerialNumber = serialNumberMatch[1]?.replace(/\s+/g, "");
          setSerialNumber(cleanedSerialNumber || "");
        }

        // --- Função para extrair dados do monitor ---
        const monitorSectionMatch = (text, peripheralsList) => {
          const match = text.match(/Monitor.*?(Sim\s*Sim|Não\s*Não|Sim\s*Não|Não\s*Sim)/i);
          if (match) {
            console.log("Texto extraído da seção do Monitor:", match[0]);
            const sectionText = match[0];
            const secondTermMatch = sectionText.match(/(Sim|Não)\s*(Sim|Não)$/i);
            if (secondTermMatch && secondTermMatch[2] === "Sim") {
              const modelMatch = sectionText.match(/Marca\/Modelo:\s*([^\)]+?)\s*Nro Série\s*:/i);
              const serialMatch = sectionText.match(/Série\s*[:\-\s]*([A-Za-z0-9\-]+)/i);
              if (modelMatch) setModelMonitor(modelMatch[1].trim());
              if (serialMatch) setSerialMonitor(serialMatch[1].trim());
              peripheralsList.push({
                item: "Monitor",
                status: "Sim Sim",
                model: modelMatch ? modelMatch[1].trim() : "",
                serial: serialMatch ? serialMatch[1].trim() : "",
              });
            }
          }
        };

        // --- Extração de acessórios ---
        const peripheralsSectionMatch = text.match(/ACESSÓRIOS[\s\S]+?Docusign Envelope ID:/i);
        if (peripheralsSectionMatch) {
          const peripheralsText = peripheralsSectionMatch[0];
          console.log("Texto dos periféricos:", peripheralsText);

          const captureSpecificAccessory = (item, text) => {
            const escapedItem = item.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
            const regex = new RegExp(`(${escapedItem})\\s*\\(([^)]+)\\)\\s*(Sim\\s*Sim|Não\\s*Sim)`, "i");
            const match = text.match(regex);
            if (match) {
              const name = match[1].trim();
              const additionalInfo = match[2].trim();
              const status = match[3].trim();
              if (status === "Sim Sim" || status === "Não Sim") {
                peripheralsList.push({ name, additionalInfo, status });
              }
            }
          };

          const captureAccessory = (item, text) => {
            const escapedItem = item.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
            const regex = new RegExp(`(${escapedItem})\\s*(Sim\\s*Sim|Não\\s*Sim)`, "i");
            const match = text.match(regex);
            if (match) {
              const status = match[2] ? match[2].trim() : "";
              if (status === "Sim Sim" || status === "Não Sim") {
                peripheralsList.push({ item, status });
              }
            }
          };

          const accessoryList = [
            "Mouse",
            "Teclado",
            "Monitor",
            "Cabo RCA",
            "Cabo paralelo para unidade externa",
            "Maleta/Mochila para Notebook",
            "Suporte Ergonômico",
            "Cabo de Segurança Código chave - )",
            "Bateria Extra",
            "Carregador Extra",
            "Adaptador HDMI",
            "Dock Station",
            "Lacre de Segurança",
            "Headset",
            "Kit boas-vindas",
            "Webcam",
            "Hub USB",
            "Cabo de força do monitor",
          ].map((item) => item.trim());

          const peripheralsList = [];
          accessoryList.forEach((item) => {
            if (item === "Headset" || item === "Dock Station" || item === "Cabo de Segurança Código chave - )") {
              captureSpecificAccessory(item, peripheralsText);
            } else {
              captureAccessory(item, peripheralsText);
            }
          });

          monitorSectionMatch(text, peripheralsList);
          const filteredPeripherals = peripheralsList.filter(
            (peripheral) => peripheral.status === "Sim Sim" || peripheral.status === "Não Sim"
          );
          setAccessories(filteredPeripherals.map((peripheral) => peripheral.name || peripheral.item));
        }
      } catch (err) {
        setError("Falha ao ler PDF.");
        console.error("Error reading PDF:", err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleEnviarParaServidor = async () => {
    if (assinaturaValida === false) {
      alert("O documento não está assinado corretamente (falta CPF/RG ou assinatura).");
      return;
    }

    const token = localStorage.getItem("token");
    const linhasParaPlanilha = [];

    const accessoriesCounted = accessories.map((item) => ({
      name: item,
      quantidade: 1,
    }));

    accessoriesCounted.push({ name: notebookModel, quantidade: 1 });

    if (modelMonitor && serialMonitor) {
      accessoriesCounted.push({ name: modelMonitor, quantidade: 1, serialNumber: serialMonitor });
    }

    linhasParaPlanilha.push({
      tipo: notebookTipo || "N/A",
      serialNumber: serialNumber || "N/A",
      modelo: notebookModel || "N/A",
      marca: notebookBrand || "N/A",
      accessoriesCounted,
      disponibilidade: "Em estoque",
    });

    if (modelMonitor || serialMonitor) {
      linhasParaPlanilha.push({
        tipo: "Monitor",
        serialNumber: serialMonitor || "N/A",
        modelo: modelMonitor || "N/A",
        marca: "N/A",
        disponibilidade: "Em estoque",
      });
    }

    try {
      for (const linha of linhasParaPlanilha) {
        await axios.post("/api/entrada", linha, {
          headers: { Authorization: `Bearer ${token}` },
        });
      }
      alert("Dados enviados ao servidor com sucesso!");
    } catch (error) {
      alert("Erro ao enviar dados para o servidor.");
      console.error("Erro ao enviar:", error);
    }
  };

 return (
  <div className="container">
    {/* Botão estilizado para upload */}
    <input 
      type="file" 
      id="fileUpload" 
      accept="application/pdf" 
      onChange={handleFileChange} 
      style={{ display: "none" }} 
    />
    <label htmlFor="fileUpload" className="upload-btn">Selecionar PDF</label>

    {assinaturaValida !== null && (
      <p className={assinaturaValida ? "success-text" : "error-text"}>
        {assinaturaValida ? "✅ Documento assinado e válido" : "❌ Documento NÃO assinado corretamente"}
      </p>
    )}

    <button className="send-btn" onClick={handleEnviarParaServidor} disabled={loading}>
      {loading ? "Processando..." : "Enviar para o Servidor"}
    </button>

    {/* Exibição dos dados extraídos */}
    {notebookTipo && (
      <div className="info-section">
        <h3>Dados extraídos do PDF:</h3>
        <p><strong>Tipo:</strong> {notebookTipo}</p>
        <p><strong>Modelo:</strong> {notebookModel}</p>
        <p><strong>Marca:</strong> {notebookBrand}</p>
        <p><strong>Nº de Série:</strong> {serialNumber}</p>

        {modelMonitor && (
          <>
            <h4>Monitor</h4>
            <p><strong>Modelo:</strong> {modelMonitor}</p>
            <p><strong>Série:</strong> {serialMonitor}</p>
          </>
        )}

        {accessories.length > 0 && (
          <>
            <h4>Acessórios</h4>
            <ul>
              {accessories.map((acc, index) => (
                <li key={index}>{acc}</li>
              ))}
            </ul>
          </>
        )}
      </div>
    )}

    {error && <p className="error-text">{error}</p>}
  </div>
);
}

export default App;
