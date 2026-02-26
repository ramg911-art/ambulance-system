import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'
const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Log API base URL on first use (helps debug production save failures)
if (typeof window !== 'undefined') {
  console.info('[API] baseURL:', baseURL, '(set VITE_API_URL when building for production if API is on different host)')
}

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    }
    const url = err.config?.baseURL && err.config?.url ? `${err.config.baseURL.replace(/\/$/, '')}${err.config.url}` : 'unknown'
    if (!err.response) {
      const hint = err.message === 'Network Error' ? ' (connection refused/timed out - is backend running on that host:port?)' : ''
      console.error('[API] No response' + hint + '. URL:', url, err.message)
    } else {
      console.error('[API] Error', err.response?.status, url, err.response?.data)
    }
    return Promise.reject(err)
  }
)

export default api
