import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import api from './services/api'

async function init() {
  try {
    const r = await fetch('/config.json?t=' + Date.now())
    const c = await r.json()
    if (c?.apiUrl && typeof c.apiUrl === 'string') {
      api.defaults.baseURL = c.apiUrl.replace(/\/$/, '')
      console.info('[API] Using runtime config.apiUrl:', api.defaults.baseURL)
    }
  } catch (_) {}
  const app = createApp(App)
  app.use(createPinia())
  app.use(router)
  app.mount('#app')
}
init()
