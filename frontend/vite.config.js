import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'icons.svg', 'og-image.svg'],
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,jpg,gif,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https?:\/\/.*\/api\/words.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-words',
              expiration: { maxEntries: 50, maxAgeSeconds: 7 * 24 * 60 * 60 },
              networkTimeoutSeconds: 3,
            },
          },
          {
            urlPattern: /^https?:\/\/.*\/api\/.*/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 30, maxAgeSeconds: 24 * 60 * 60 },
              networkTimeoutSeconds: 3,
            },
          },
        ],
      },
      manifest: {
        name: 'CET-4 词汇学习',
        short_name: 'CET-4词汇',
        description: 'CET-4 英语四级词汇学习平台，4417 个核心词汇，三种测验模式',
        theme_color: '#2563EB',
        background_color: '#FFFFFF',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        lang: 'zh-CN',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: '/favicon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
