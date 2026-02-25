<template>
  <div class="app">
    <Sidebar v-if="!$route.meta.hideLayout" />
    <main class="main">
      <router-view />
    </main>
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
.main {
  flex: 1;
  padding: 1.5rem;
  background: #f1f5f9;
}
</style>
