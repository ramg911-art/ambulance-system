<template>
  <div class="dashboard">
    <header class="header">
      <div class="header-top">
        <span class="greeting">Hello {{ driverName }}</span>
        <button @click="logout" class="logout">Logout</button>
      </div>
      <h1 class="sub-header">Ambulance fleet management system</h1>
    </header>
    <div class="content">
      <div class="map-card">
        <h3>Current Location</h3>
        <p v-if="locationError" class="location-error">{{ locationError }}</p>
        <p v-else-if="!currentPosition" class="location-hint">Detecting location...</p>
        <p v-else-if="currentPosition" class="location-info">
          <span v-if="locationName">{{ locationName }} (</span>{{ currentPosition.lat.toFixed(4) }}, {{ currentPosition.lng.toFixed(4) }}<span v-if="locationName">)</span>
        </p>
        <div class="map-box">
          <GoogleMap
            :current-position="currentPosition"
            readonly
          />
        </div>
      </div>
      <div class="cards">
        <div class="card" @click="$router.push('/start')">
          <span class="icon">🚑</span>
          <h2>Start New Trip</h2>
          <p>Begin a new ambulance trip</p>
        </div>
        <div class="card" @click="$router.push('/trips/today')">
          <span class="icon">📋</span>
          <h2>Today's Trips</h2>
          <p>View today's completed trips</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { reverseGeocode } from '../services/mapsService'
import GoogleMap from '../components/GoogleMap.vue'

const auth = useAuthStore()
const router = useRouter()

const driverName = computed(() => auth.driver?.name || 'Driver')

const currentPosition = ref(null)
const locationName = ref('')
const locationError = ref('')
let watchId = null
let intervalId = null

async function fetchLocationName(lat, lng) {
  try {
    const name = await reverseGeocode(lat, lng)
    locationName.value = name || ''
  } catch {
    locationName.value = ''
  }
}

function updatePosition(pos) {
  currentPosition.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
  locationError.value = ''
  fetchLocationName(pos.coords.latitude, pos.coords.longitude)
}

function onGeoError(err) {
  const isDenied = err?.code === 1
  locationError.value = isDenied
    ? 'Location access denied. Enable location for trip pickup detection.'
    : 'Could not get location. Check GPS or network.'
}

function startLocationTracking() {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocation not supported'
    return
  }
  navigator.geolocation.getCurrentPosition(updatePosition, onGeoError, { enableHighAccuracy: true })
  watchId = navigator.geolocation.watchPosition(updatePosition, onGeoError, {
    enableHighAccuracy: true,
    maximumAge: 5000,
  })
  intervalId = setInterval(() => {
    navigator.geolocation.getCurrentPosition(updatePosition, onGeoError, { enableHighAccuracy: true })
  }, 5000)
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(startLocationTracking)
onUnmounted(() => {
  if (watchId) navigator.geolocation.clearWatch(watchId)
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.dashboard {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}
.header {
  flex-shrink: 0;
  background: #1e3a8a;
  color: white;
  padding: 0.5rem 1rem;
}
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sub-header {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0.35rem 0 0;
  opacity: 0.95;
  line-height: 1.2;
}
.greeting {
  font-size: 0.9rem;
  opacity: 0.95;
}
.logout {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
}
.content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}
.map-card {
  flex-shrink: 1;
  min-height: 0;
  background: white;
  border-radius: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.map-card h3 {
  font-size: 1rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}
.location-error { color: #dc2626; font-size: 0.875rem; margin-bottom: 0.5rem; }
.location-hint { color: #64748b; font-size: 0.875rem; margin-bottom: 0.5rem; }
.location-info { color: #475569; font-size: 0.9rem; margin-bottom: 0.5rem; }
.map-box { height: 160px; border-radius: 0.5rem; overflow: hidden; }
.cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.25rem;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:active {
  transform: scale(0.98);
}
.icon { font-size: 2.25rem; display: block; margin-bottom: 0.35rem; }
.card h2 { font-size: 1rem; color: #1e293b; margin-bottom: 0.2rem; }
.card p { color: #64748b; font-size: 0.8rem; }
</style>
