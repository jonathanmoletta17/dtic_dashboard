import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import App from "./App.tsx";
import "./index.css";
import "./overflow-hotfix.css";


createRoot(document.getElementById("root")!).render(
  <BrowserRouter basename="/dashboard">
    <Routes>
      {/** Entrada canônica do dashboard da DTIC */}
      <Route path="/" element={<App />} />
      {/** Mantém compatibilidade com /dashboard/dtic */}
      <Route path="/dtic/*" element={<App />} />
      {/** Fallback para a raiz do dashboard */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);
