import React, { useState, useEffect, useRef } from "react";
import { uploadPdfs } from "../utils/api.js";
import "./App.css";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
} from "chart.js";
import ProgressBar from "../components/ProgressBar.jsx";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export default function App() {
  const [files, setFiles] = useState([]);
  const [progresso, setProgresso] = useState(0);
  const [resultados, setResultados] = useState([]);
  const [excelUrl, setExcelUrl] = useState("");
  const [chartData, setChartData] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const wsRef = useRef(null);

  // --- WebSocket ---
  useEffect(() => {
  const connectWS = () => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/progresso");
    wsRef.current = ws;

    ws.onopen = () => console.log("WebSocket conectado");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.progress !== undefined) {
        setProgresso(data.progress);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket desconectado. Tentando reconectar...");
      setTimeout(connectWS, 3000);
    };

    ws.onerror = (err) => {
      console.error("WebSocket erro:", err);
      ws.close();
    };
  };

  connectWS();
  return () => wsRef.current?.close();
}, []);

  const handleFileChange = (e) => setFiles(Array.from(e.target.files));

  const handleUpload = async () => {
    if (files.length === 0) return alert("Selecione os PDFs");
    setProcessing(true);
    setProgresso(0);

    try {
      const data = await uploadPdfs(files);
      setResultados(data.resultados || []);
      setExcelUrl(data.excelUrl || "");
      if (data.chartData) {
        setChartData({
          pie: {
            labels: ["OK", "Erro"],
            datasets: [
              {
                data: [data.chartData.ok || 0, data.chartData.erro || 0],
                backgroundColor: ["#4caf50", "#f44336"],
              },
            ],
          },
          bar: {
            labels: ["Concessão", "Devolução"],
            datasets: [
              {
                label: "Documentos",
                data: [
                  data.chartData.concessao || 0,
                  data.chartData.devolucao || 0,
                  data.chartData.desconhecido || 0,
                ],
                backgroundColor: ["#2196f3", "#ff9800", "#9c27b0"],
              },
            ],
          },
        });
      }
    } catch (error) {
      console.error(error);
      alert("Erro ao processar PDFs");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className={`container ${darkMode ? "dark" : "light"}`}>
     <header className="header">
  <h1>Processador de PDFs</h1>
 <div 
  className={`theme-switch ${darkMode ? "dark" : "light"}`} 
  onClick={() => setDarkMode(!darkMode)}
>
  <span className="icon sun">☀️</span>
  <span className="icon moon">🌙</span>
  <div className="switch-handle"></div>
</div>
</header>

      <main className="main">
        <input
          type="file"
          multiple
          accept="application/pdf"
          onChange={handleFileChange}
        />
        <button
          onClick={handleUpload}
          disabled={processing || files.length === 0}
        >
          {processing ? "Processando..." : "Processar PDFs"}
        </button>

        {processing && <ProgressBar progress={progresso} />}

        {excelUrl && (
          <a href={excelUrl} download className="download-btn">
            ⬇ Baixar Excel
          </a>
        )}

        {chartData && (
          <div className="charts">
            <div className="chart">
              <h3>Documentos corretos x incorretos</h3>
              <Pie data={chartData.pie} />
            </div>
            <div className="chart">
              <h3>Tipos de documentos</h3>
              <Bar data={chartData.bar} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
