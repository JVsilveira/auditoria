import { getDocument, GlobalWorkerOptions } from "pdfjs-dist"

GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js"

export const extractPdfText = async file => {
  const typedArray = new Uint8Array(await file.arrayBuffer())
  const pdf = await getDocument(typedArray).promise

  let text = ""
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i)
    const textContent = await page.getTextContent()
    text += textContent.items.map(item => item.str).join(" ")
  }

  text = text.replace(/\s+/g, " ").trim()
  text = text.replace(/\n/g, " ")

  return text
}
