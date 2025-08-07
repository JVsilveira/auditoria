export function extractDevolucaoData(text) {
  // Regex para validar assinatura e CPF/RG
  const assinaturaRegex = /(?:assinatura|\/sign\/)/i
  const cpfRgRegex =
    /\b(\d{3}\.?\d{3}\.?\d{3}-?\d{2}|\d{7,10}|[A-Z]{2}-\d{2}\.?\d{3}\.?\d{3})\b/

  const validarAssinatura = textoExtraido => {
    const temAssinatura = assinaturaRegex.test(textoExtraido)
    const temCpfOuRg = cpfRgRegex.test(textoExtraido)
    return temAssinatura && temCpfOuRg
  }

  // Validação da assinatura
  const assinaturaValida = validarAssinatura(text)

  // Extração dados notebook
  const notebookTipoMatch = text.match(/tipo[^\w]+([A-Za-z0-9\s\-]+)/i)
  const notebookModelMatch = text.match(/modelo[^\w]+([A-Za-z0-9\s\-]+)/i)
  const notebookBrandMatch = text.match(/marca[^\w]+([A-Za-z0-9\s\-]+)/i)
  const serialNumberMatch = text.match(/nº de série\s*[:\-\s]*([A-Za-z0-9]+)/i)

  const notebookTipo = notebookTipoMatch ? notebookTipoMatch[1].trim() : ""
  const notebookModel = notebookModelMatch ? notebookModelMatch[1].trim() : ""
  const notebookBrand = notebookBrandMatch ? notebookBrandMatch[1].trim() : ""
  const serialNumber = serialNumberMatch
    ? serialNumberMatch[1].replace(/\s+/g, "")
    : ""

  // Função para capturar monitor de forma mais precisa
  const peripheralsList = []

  const monitorRegex =
    /Monitor\s*\(Marca\/Modelo:\s*([^\)]+?)\s*Nro Série\s*:\s*([^\)\s]+)[^\)]*\)\s*(Sim|Não)\s*(Sim|Não)/i
  const monitorMatch = text.match(monitorRegex)
  let modelMonitor = ""
  let serialMonitor = ""
  if (monitorMatch) {
    modelMonitor = monitorMatch[1].trim()
    serialMonitor = monitorMatch[2].trim()
    peripheralsList.push({
      item: "Monitor",
      status: `${monitorMatch[3]} ${monitorMatch[4]}`,
      model: modelMonitor,
      serial: serialMonitor,
    })
  }

  // Captura acessórios (com e sem info adicional)
  const captureSpecificAccessory = (item, text, peripheralsList) => {
    const escapedItem = item.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&")
    const regex = new RegExp(
      `(${escapedItem})\\s*\\(([^)]+)\\)\\s*(Sim\\s*Sim|Não\\s*Sim)`,
      "i"
    )
    const match = text.match(regex)
    if (match) {
      const name = match[1].trim()
      const additionalInfo = match[2].trim()
      const status = match[3].trim()
      if (status === "Sim Sim" || status === "Não Sim") {
        peripheralsList.push({ name, additionalInfo, status })
      }
    }
  }

  const captureAccessory = (item, text, peripheralsList) => {
    const escapedItem = item.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&")
    const regex = new RegExp(`(${escapedItem})\\s*(Sim\\s*Sim|Não\\s*Sim)`, "i")
    const match = text.match(regex)
    if (match) {
      const status = match[2] ? match[2].trim() : ""
      if (status === "Sim Sim" || status === "Não Sim") {
        peripheralsList.push({ item, status })
      }
    }
  }

  const peripheralsSectionMatch = text.match(
    /ACESSÓRIOS[\s\S]+?Docusign Envelope ID:/i
  )
  const accessories = []

  if (peripheralsSectionMatch) {
    const peripheralsText = peripheralsSectionMatch[0]
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
    ].map(item => item.trim())

    accessoryList.forEach(item => {
      if (
        item === "Headset" ||
        item === "Dock Station" ||
        item === "Cabo de Segurança Código chave - )"
      ) {
        captureSpecificAccessory(item, peripheralsText, peripheralsList)
      } else {
        captureAccessory(item, peripheralsText, peripheralsList)
      }
    })

    // Extra monitor já capturado acima, então não precisa chamar função separada aqui.

    const filteredPeripherals = peripheralsList.filter(
      peripheral =>
        peripheral.status === "Sim Sim" || peripheral.status === "Não Sim"
    )
    filteredPeripherals.forEach(peripheral => {
      accessories.push(peripheral.name || peripheral.item)
    })
  }

  return {
    assinaturaValida,
    notebookTipo,
    notebookModel,
    notebookBrand,
    serialNumber,
    modelMonitor,
    serialMonitor,
    accessories,
  }
}
