import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'
const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

// Log API base URL on first use (helps debug production save failures)
if (typeof window !== 'undefined') {
  console.info('[API] baseURL:', baseURL, '(set VITE_API_URL when building for production if API is on different host)')
}

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const url = err.config?.baseURL && err.config?.url ? `${err.config.baseURL.replace(/\/$/, '')}${err.config.url}` : 'unknown'
    if (!err.response) {
      console.error('[API] No response - request may be blocked (CORS/proxy). URL:', url, err.message)
    } else {
      console.error('[API] Error', err.response?.status, url, err.response?.data)
    }
    return Promise.reject(err)
  }
)

export default api
