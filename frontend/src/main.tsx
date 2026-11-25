import React from "react";
import ReactDOM from "react-dom/client";
// Bascule clair / sombre de Night Navy, chargée avant l'affichage pour éviter un flash de couleur
import "night-navy/theme-toggle";
import "./index.css";
import { App } from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
