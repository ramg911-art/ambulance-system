import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import api from './services/api'

async function init() {
  // Runtime config: set config.json "apiUrl" to override API base URL (no rebuild needed)
  try {
    const r = await fetch('/config.json?t=' + Date.now())
    const c = await r.json()
    if (c?.apiUrl && typeof c.apiUrl === 'string') {
      api.defaults.baseURL = c.apiUrl.replace(/\/$/, '')
      console.info('[API] Using runtime config.apiUrl:', api.defaults.baseURL)
    }
  } catch (_) {}
  createApp(App).use(router).mount('#app')
}
init()
