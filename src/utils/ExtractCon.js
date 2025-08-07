export function extractConcessaoData(text) {
  const assinaturaRegex = /(?:assinatura|\/sign\/)/i
  const cpfRgRegex =
    /\b(\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{7,10}|[A-Z]{2}-\d{2}\.?\d{3}\.?\d{3})\b/

  const validarAssinatura = textoExtraido => {
    const temAssinatura = assinaturaRegex.test(textoExtraido)
    const temCpfOuRg = cpfRgRegex.test(textoExtraido)
    return temAssinatura && temCpfOuRg
  }

  const assinaturaValida = validarAssinatura(text)

  let notebookModel = ""
  let notebookBrand = ""
  let notebookTipo = ""
  let accessories = []
  let serialNumber = ""
  let assetNumber = ""
  let nfNumber = ""
  let modelMonitor = ""
  let serialMonitor = ""

  // Funções auxiliares para capturar acessórios específicos
  const captureHeadset = (text, peripheralsList) => {
    const headsetRegex = /Headset\s*\(.*?\)\s*(Sim|Não)/i
    const match = text.match(headsetRegex)
    if (match && match[1] === "Sim") {
      peripheralsList.push({ name: "Headset", status: "Sim" })
    }
  }

  const captureDockStation = (text, peripheralsList) => {
    const dockStationRegex = /Dock Station\s*\(.*?\)\s*(Sim|Não)/i
    const match = text.match(dockStationRegex)
    if (match && match[1] === "Sim") {
      peripheralsList.push({ name: "Dock Station", status: "Sim" })
    }
  }

  const captureCaboSeguranca = (text, peripheralsList) => {
    const caboSegurancaRegex = /Cabo de Segurança(.*?)\s*(Sim|Não)/i
    const match = text.match(caboSegurancaRegex)
    if (match && match[2] === "Sim") {
      peripheralsList.push({ name: "Cabo de Segurança", status: "Sim" })
    }
  }

  const monitorMatch = (text, peripheralsList) => {
    const monitorRegex =
      /Monitor\s*\(Marca\/Modelo\s*:\s*([^\)]+?)\s*Nro\s*Série\s*[:\-\s]*([A-Za-z0-9\-]+)\s*\)\s*(Sim|Não)/i
    const match = text.match(monitorRegex)

    if (match && match[3] === "Sim") {
      modelMonitor = match[1].trim()
      serialMonitor = match[2].trim()
      peripheralsList.push({
        name: "Monitor",
        status: "Sim",
        additionalInfo: `Modelo: ${modelMonitor}, Nº Série: ${serialMonitor}`,
      })
    }
  }

  const captureAccessory = (item, text, peripheralsList) => {
    const escapedItem = item.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&")
    const regex = new RegExp(
      `(${escapedItem})\\s*(\\(Marca/Modelo\\s*:\\s*[^)]+?\\s*Nro\\s*Série\\s*:\\s*[^)]+?\\))?\\s*(Sim|Não)`,
      "i"
    )
    const match = text.match(regex)
    if (match && match[3] === "Sim") {
      peripheralsList.push({
        name: match[1].trim(),
        additionalInfo: match[2] ? match[2].trim() : "",
        status: "Sim",
      })
    }
  }

  try {
    // Extrai notebook
    const notebookTipoMatch = text.match(/um[^\w]+(\S[\w\s-]+)/i)
    const notebookModelMatch = text.match(/modelo[^\w]+(\S[\w\s-]+)/i)
    const notebookBrandMatch = text.match(/marca[^\w]+(\S[\w\s-]+)/i)
    const nfNumberMatch = text.match(/NF\s*nº?\s*(\d+)/i)
    const assetNumberMatch = text.match(/NÚMERO DO ATIVO\s*(\d+)/i)
    const serialNumberMatch = text.match(
      /nº de série\s*[:\-\s]*([A-Za-z0-9\-]+\s*[A-Za-z0-9\-]*)+/i
    )

    if (notebookTipoMatch) notebookTipo = notebookTipoMatch[1].trim()
    if (notebookModelMatch) notebookModel = notebookModelMatch[1].trim()
    if (notebookBrandMatch) notebookBrand = notebookBrandMatch[1].trim()
    if (nfNumberMatch) nfNumber = nfNumberMatch[1].trim()
    if (assetNumberMatch) assetNumber = assetNumberMatch[1].trim()
    if (serialNumberMatch)
      serialNumber = serialNumberMatch[1].replace(/\s+/g, "").trim()

    // Extrai acessórios
    const peripheralsSectionMatch = text.match(
      /ACESSÓRIOS[\s\S]+?Docusign Envelope ID:/i
    )
    accessories = []

    if (peripheralsSectionMatch) {
      const peripheralsText = peripheralsSectionMatch[0]
      const peripheralsList = []

      // Captura acessórios com funções específicas
      captureHeadset(peripheralsText, peripheralsList)
      captureDockStation(peripheralsText, peripheralsList)
      captureCaboSeguranca(peripheralsText, peripheralsList)
      monitorMatch(peripheralsText, peripheralsList)

      // Lista genérica de acessórios para captura
      const accessoryList = [
        "Mouse",
        "Teclado",
        "Cabo RCA",
        "Cabo paralelo para unidade externa",
        "Maleta/Mochila para Notebook",
        "Suporte Ergonômico",
        "Bateria Extra",
        "Carregador Extra",
        "Adaptador HDMI",
        "Lacre de Segurança",
        "Kit boas - vindas",
        "Webcam",
        "Hub USB",
        "Cabo de força do monitor",
      ].map(item => item.trim())

      accessoryList.forEach(item => {
        captureAccessory(item, peripheralsText, peripheralsList)
      })

      // Filtra só os que estão marcados como 'Sim'
      accessories = peripheralsList
        .filter(p => p.status === "Sim")
        .map(p => p.name)
    }
  } catch (error) {
    console.error("Erro ao extrair dados do termo de concessão:", error)
  }

  return {
    assinaturaValida,
    notebookModel,
    notebookBrand,
    notebookTipo,
    accessories,
    serialNumber,
    assetNumber,
    nfNumber,
    modelMonitor,
    serialMonitor,
  }
}
