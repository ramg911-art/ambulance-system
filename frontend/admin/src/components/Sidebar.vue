<template>
  <aside class="sidebar">
    <h1 class="logo">Ambulance Admin</h1>
    <nav class="nav">
      <router-link to="/">Dashboard</router-link>
      <router-link to="/live">Live Tracking</router-link>
      <router-link to="/trips">Trips</router-link>
      <router-link to="/vehicles">Vehicles</router-link>
      <router-link to="/drivers">Drivers</router-link>
      <router-link to="/preset-locations">Preset Locations</router-link>
      <router-link to="/preset-destinations">Preset Destinations</router-link>
      <router-link to="/tariffs">Tariffs</router-link>
      <router-link to="/fallback-tariff">Fallback Tariff</router-link>
      <router-link to="/billing">Billing</router-link>
    </nav>
    <button class="logout" @click="logout">Logout</button>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function logout() {
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: #1e293b;
  color: white;
  padding: 1.5rem 0;
  min-height: 100vh;
  position: relative;
}
.logo {
  font-size: 1.125rem;
  padding: 0 1.5rem;
  margin-bottom: 1.5rem;
}
.nav {
  display: flex;
  flex-direction: column;
}
.nav a {
  color: #94a3b8;
  padding: 0.5rem 1.5rem;
  text-decoration: none;
  transition: color 0.2s, background 0.2s;
}
.nav a:hover { color: white; background: rgba(255,255,255,0.05); }
.nav a.router-link-active { color: white; background: rgba(255,255,255,0.1); }
.logout {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  padding: 0.5rem;
  background: rgba(255,255,255,0.1);
  color: #94a3b8;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}
.logout:hover { background: rgba(255,255,255,0.15); color: white; }
</style>
