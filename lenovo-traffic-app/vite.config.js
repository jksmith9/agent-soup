import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      '/api/events': {
        target: 'https://www.lenovocenter.com/events/rss',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/events/, '')
      }
    }
  }
})
