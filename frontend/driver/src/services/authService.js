import api from './api'

export async function login(phone, password) {
  const { data } = await api.post('/auth/login', { phone, password })
  return data
}
