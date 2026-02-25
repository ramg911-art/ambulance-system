<template>
  <div class="dashboard">
    <header class="header">
      <h1>Driver Dashboard</h1>
      <button @click="logout" class="logout">Logout</button>
    </header>
    <div class="content">
      <div class="card" @click="$router.push('/start')">
        <span class="icon">🚑</span>
        <h2>Start New Trip</h2>
        <p>Begin a new ambulance trip</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f8fafc;
}
.header {
  background: #1e3a8a;
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
h1 { font-size: 1.25rem; }
.logout {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
}
.content {
  padding: 1.5rem;
}
.card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:active {
  transform: scale(0.98);
}
.icon { font-size: 3rem; display: block; margin-bottom: 0.5rem; }
h2 { font-size: 1.25rem; color: #1e293b; margin-bottom: 0.25rem; }
p { color: #64748b; font-size: 0.9rem; }
</style>
