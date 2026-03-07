import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

function getStoredToken() {
  return localStorage.getItem('driver_token') || sessionStorage.getItem('driver_token')
}

function getStoredDriver() {
  const raw = localStorage.getItem('driver') || sessionStorage.getItem('driver')
  return raw ? JSON.parse(raw) : null
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getStoredToken())
  const driver = ref(getStoredDriver())

  const isLoggedIn = computed(() => !!token.value)

  async function login(userId, password, rememberMe = true) {
    const { data } = await api.post('/auth/login', { user_id: userId, password })
    token.value = data.access_token
    driver.value = data.driver
      ? { id: data.driver.id, organization_id: data.driver.organization_id, name: data.driver.name }
      : { id: parseDriverId(data.access_token), name: 'Driver' }

    localStorage.removeItem('driver_token')
    localStorage.removeItem('driver')
    sessionStorage.removeItem('driver_token')
    sessionStorage.removeItem('driver')

    if (rememberMe) {
      localStorage.setItem('driver_token', data.access_token)
      localStorage.setItem('driver', JSON.stringify(driver.value))
      localStorage.setItem('driver_remembered_user_id', userId)
    } else {
      sessionStorage.setItem('driver_token', data.access_token)
      sessionStorage.setItem('driver', JSON.stringify(driver.value))
      localStorage.removeItem('driver_remembered_user_id')
    }
    return data
  }

  function parseDriverId(tokenStr) {
    try {
      const payload = JSON.parse(atob(tokenStr.split('.')[1]))
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
    localStorage.removeItem('driver_remembered_user_id')
    sessionStorage.removeItem('driver_token')
    sessionStorage.removeItem('driver')
  }

  return { token, driver, isLoggedIn, login, logout }
})
