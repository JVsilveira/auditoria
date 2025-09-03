import React from "react";
import "./ProgressBar.css"; // arquivo CSS separado para estilização

export default function ProgressBar({ progress }) {
  return (
    <div className="progress-container">
      <div className="progress-bar" style={{ width: `${progress}%` }}></div>
      <span className="progress-text">{progress}%</span>
    </div>
  );
}
