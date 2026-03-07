import api from './api'

export async function login(userId, password) {
  const { data } = await api.post('/auth/login', { user_id: userId, password })
  return data
}
