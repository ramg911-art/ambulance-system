<template>
  <div class="app">
    <router-view />
    <footer class="footer" v-if="!$route.meta.guest">
      Developed by Dr Ram Gopal 2026 All rights reserved.
    </footer>
  </div>
</template>

<script setup>
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.app > :first-child {
  flex: 1;
}
.footer {
  padding: 0.75rem 1rem;
  background: #1e293b;
  color: #94a3b8;
  font-size: 0.8rem;
  text-align: center;
}
</style>
