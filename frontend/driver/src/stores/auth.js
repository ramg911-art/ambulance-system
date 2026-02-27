import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('driver_token'))
  const driver = ref(JSON.parse(localStorage.getItem('driver') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(phone, password) {
    const { data } = await api.post('/auth/login', { phone, password })
    token.value = data.access_token
    driver.value = data.driver
      ? { id: data.driver.id, organization_id: data.driver.organization_id, name: data.driver.name }
      : { id: parseDriverId(data.access_token), name: 'Driver' }
    localStorage.setItem('driver_token', data.access_token)
    localStorage.setItem('driver', JSON.stringify(driver.value))
    return data
  }

  function parseDriverId(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return parseInt(payload.sub, 10)
    } catch {
      return null
    }
  }

  function logout() {
    token.value = null
    driver.value = null
    localStorage.removeItem('driver_token')
    localStorage.removeItem('driver')
  }

  return { token, driver, isLoggedIn, login, logout }
})
