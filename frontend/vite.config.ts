import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En développement (npm run dev), l'API est celle du serveur Python lancé à côté : python backend/launcher.py
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8090", "/health": "http://127.0.0.1:8090" },
  },
});
