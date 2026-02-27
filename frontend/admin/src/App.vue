<template>
  <div class="app">
    <Sidebar v-if="!$route.meta.guest" />
    <div class="main-wrap">
      <main class="main">
        <router-view />
      </main>
      <footer class="footer" v-if="!$route.meta.guest">
        Developed by Dr Ram Gopal 2026 All rights reserved.
      </footer>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/Sidebar.vue'
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; font-family: system-ui, sans-serif; }
.app {
  display: flex;
  min-height: 100vh;
}
.main-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.main {
  flex: 1;
  padding: 1.5rem;
  background: #f1f5f9;
}
.footer {
  padding: 0.75rem 1.5rem;
  background: #1e293b;
  color: #94a3b8;
  font-size: 0.8rem;
  text-align: center;
}
</style>
