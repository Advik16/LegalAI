import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // proxies requests from /api/* to http://127.0.0.1:8080/*
      // adjust to your API paths; here we proxy `/query/stream` path.
      "/query/stream": {
        target: "http://127.0.0.1:8080",
        changeOrigin: true,
        secure: false,
        ws: false,
      },
    },
  },
});
