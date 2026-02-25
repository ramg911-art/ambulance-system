import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (!err.response) {
      console.error('API request failed (no response):', err.message)
    }
    return Promise.reject(err)
  }
)

export default api
