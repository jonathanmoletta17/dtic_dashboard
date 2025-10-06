import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import App from "./App.tsx";
import MaintenanceDashboard from "./MaintenanceDashboard.tsx";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <BrowserRouter>
    <Routes>
      <Route path="/dtic" element={<App />} />
      <Route path="/manutencao" element={<MaintenanceDashboard />} />
      <Route path="/" element={<Navigate to="/dtic" replace />} />
    </Routes>
  </BrowserRouter>
);
