import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8096,
    proxy: {
      // Proxy API requests to backend with DEBUG logging
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, _options) => {
          proxy.on('error', (err, req, _res) => {
            const timestamp = new Date().toISOString();
            console.error(`[${timestamp}] 🔥 PROXY ERROR: ${req.method} ${req.url}`, err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            const timestamp = new Date().toISOString();
            console.log(`[${timestamp}] 🔌 PROXY REQUEST: ${req.method} ${req.url} -> ${proxyReq.getHeader('host')}`);
            if (req.method === 'POST' || req.method === 'PUT') {
              console.log(`[${timestamp}] 📦 Request Headers:`, req.headers);
            }
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            const timestamp = new Date().toISOString();
            const duration = req.headers['x-request-start'] ? 
              Date.now() - parseInt(req.headers['x-request-start'] as string) : 'unknown';
            const statusCode = proxyRes.statusCode || 0;
            console.log(`[${timestamp}] ✅ PROXY RESPONSE: ${req.method} ${req.url} - ${statusCode} (${duration}ms)`);
            if (statusCode >= 400) {
              console.warn(`[${timestamp}] ⚠️ Response Headers:`, proxyRes.headers);
            }
          });
        },
      }
    }
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
