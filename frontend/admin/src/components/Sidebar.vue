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
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  background: #1e293b;
  color: white;
  padding: 1.5rem 0;
  min-height: 100vh;
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
</style>
