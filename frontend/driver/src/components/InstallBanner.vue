<template>
  <div v-if="showBanner" class="install-banner">
    <span class="install-text">Install app for quick access</span>
    <div class="install-actions">
      <button type="button" class="install-btn" @click="handleInstall">
        Install
      </button>
      <button type="button" class="dismiss-btn" @click="dismiss" aria-label="Dismiss">
        &times;
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const deferredPrompt = ref(null)
const showBanner = ref(false)
const DISMISS_KEY = 'pwa-install-dismissed'

onMounted(() => {
  if (window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true) {
    return
  }
  try {
    if (sessionStorage.getItem(DISMISS_KEY)) return
  } catch {
    /* ignore */
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt.value = e
    showBanner.value = true
  })
})

function handleInstall() {
  if (!deferredPrompt.value) return
  deferredPrompt.value.prompt()
  deferredPrompt.value.userChoice.then(({ outcome }) => {
    if (outcome === 'accepted') showBanner.value = false
    deferredPrompt.value = null
  })
}

function dismiss() {
  showBanner.value = false
  try {
    sessionStorage.setItem(DISMISS_KEY, '1')
  } catch {
    /* ignore */
  }
}
</script>

<style scoped>
.install-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #1e3a8a;
  color: white;
  font-size: 0.9rem;
}
.install-text {
  flex: 1;
}
.install-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.install-btn {
  padding: 0.4rem 0.8rem;
  background: white;
  color: #1e3a8a;
  border: none;
  border-radius: 0.375rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
}
.dismiss-btn {
  padding: 0.25rem 0.5rem;
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}
</style>
