<template>
  <div class="app">
    <router-view />
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
#app {
  min-height: 100vh;
  padding-bottom: env(safe-area-inset-bottom);
}
</style>
