<template>
  <div class="active-trip">
    <header class="header">
      <h1>Trip #{{ tripId }}</h1>
      <span class="status in-progress">In Progress</span>
    </header>
    <div class="content">
      <div class="map-placeholder" v-if="trip">
        <p>📍 Tracking: {{ currentLat?.toFixed(5) }}, {{ currentLng?.toFixed(5) }}</p>
      </div>
      <button class="end-btn" @click="endTrip" :disabled="ending">
        {{ ending ? 'Ending...' : 'End Trip' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { endTrip as apiEndTrip } from '../services/tripService'
import { updateLocation } from '../services/gpsService'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const tripId = route.params.id

const trip = ref(null)
const currentLat = ref(null)
const currentLng = ref(null)
const ending = ref(false)
const error = ref('')

let gpsInterval = null
let watchId = null

function onLocation(pos) {
  currentLat.value = pos.coords.latitude
  currentLng.value = pos.coords.longitude
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/trips/${tripId}`)
    trip.value = data
  } catch {
    error.value = 'Trip not found'
    return
  }
  if (navigator.geolocation) {
    watchId = navigator.geolocation.watchPosition(onLocation, () => {})
    gpsInterval = setInterval(async () => {
      if (currentLat.value && currentLng.value && trip.value) {
        await updateLocation(
          trip.value.vehicle_id,
          currentLat.value,
          currentLng.value,
          trip.value.id
        )
      }
    }, 5000)
  }
})

onUnmounted(() => {
  if (gpsInterval) clearInterval(gpsInterval)
  if (watchId) navigator.geolocation.clearWatch(watchId)
})

async function endTrip() {
  error.value = ''
  ending.value = true
  try {
    await apiEndTrip(tripId)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to end trip'
  } finally {
    ending.value = false
  }
}
</script>

<style scoped>
.active-trip {
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
.status {
  background: rgba(255,255,255,0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
}
.content { padding: 1.5rem; }
.map-placeholder {
  background: #e2e8f0;
  border-radius: 1rem;
  padding: 3rem;
  text-align: center;
  margin-bottom: 1.5rem;
  color: #64748b;
}
.end-btn {
  width: 100%;
  padding: 1rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
.end-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #dc2626; margin-top: 0.5rem; font-size: 0.875rem; }
</style>
