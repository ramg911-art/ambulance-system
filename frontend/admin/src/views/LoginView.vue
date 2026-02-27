<template>
  <div class="login">
    <div class="login-card">
      <h1>Ambulance Admin</h1>
      <p class="subtitle">Sign in to continue</p>
      <form @submit.prevent="handleLogin" class="form">
        <input
          v-model="username"
          type="text"
          placeholder="Username"
          autocapitalize="off"
          autocomplete="username"
          required
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          autocomplete="current-password"
          required
        />
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">Sign In</button>
      </form>
      <p class="hint">Default: admin / admin123 (run seed_data.py first)</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/admin-login', { username: username.value, password: password.value })
    localStorage.setItem('admin_token', data.access_token)
    if (data.username) localStorage.setItem('admin_username', data.username)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
.login-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}
h1 {
  font-size: 1.5rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
}
.subtitle {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}
.form input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  margin-bottom: 1rem;
}
.form input:focus {
  outline: none;
  border-color: #1e293b;
  box-shadow: 0 0 0 3px rgba(30, 41, 59, 0.2);
}
.form button {
  width: 100%;
  padding: 0.875rem;
  background: #1e293b;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
.form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #dc2626;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}
.hint {
  margin-top: 1rem;
  font-size: 0.75rem;
  color: #94a3b8;
}
</style>
