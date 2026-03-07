<template>
  <div class="login">
    <div class="login-card">
      <h1>Ambulance Driver</h1>
      <p class="subtitle">Sign in to continue</p>
      <form @submit.prevent="handleLogin" class="form">
        <input
          v-model="userId"
          type="tel"
          placeholder="User ID"
          autocapitalize="off"
          autocomplete="tel"
          required
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          autocomplete="current-password"
          required
        />
        <label class="remember-row">
          <input v-model="rememberMe" type="checkbox" />
          Remember me (stay logged in until logout)
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">Sign In</button>
      </form>
      <p class="hint">Default: +1234567890 / driver123 (User ID / password - run seed_data.py first)</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const userId = ref('')
const password = ref('')
const rememberMe = ref(true)

onMounted(() => {
  const saved = localStorage.getItem('driver_remembered_user_id')
  if (saved) userId.value = saved
})
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(userId.value, password.value, rememberMe.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || (e.response ? `Error ${e.response.status}` : 'Network error - check API URL and backend')
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
  background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
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
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
}
.form button {
  width: 100%;
  padding: 0.875rem;
  background: #2563eb;
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
.remember-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #475569;
  margin-bottom: 1rem;
  cursor: pointer;
}
.remember-row input { width: auto; margin: 0; }
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
