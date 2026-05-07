import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    server: {
      port: 3000,
      // Proxy only used in development mode
      // In production (Vercel), frontend calls API directly using VITE_API_BASE_URL
      proxy: mode === 'development' ? {
        '/api': {
          target: env.VITE_DEV_API_URL || 'http://localhost:8000',
          changeOrigin: true,
        }
      } : undefined
    },
    build: {
      outDir: 'dist',
      sourcemap: true
    }
  }
})