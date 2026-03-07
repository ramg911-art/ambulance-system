<template>
  <div class="app">
    <InstallBanner v-if="!$route.meta.guest" />
    <main class="main-content">
      <router-view />
    </main>
    <footer class="footer" v-if="!$route.meta.guest">
      Developed by Dr Ram Gopal 2026 All rights reserved.
    </footer>
  </div>
</template>

<script setup>
import InstallBanner from './components/InstallBanner.vue'
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  background: #f1f5f9;
}
.app {
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.main-content {
  flex: 1;
  min-height: 0;
  overflow: auto;
}
.footer {
  padding: 0.75rem 1rem;
  background: #1e293b;
  color: #94a3b8;
  font-size: 0.8rem;
  text-align: center;
}
</style>
