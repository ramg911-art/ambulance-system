<template>
  <div class="active-trip">
    <header class="header">
      <h1>Trip #{{ tripId }}</h1>
      <span class="status in-progress">In Progress</span>
    </header>
    <div class="content">
      <div class="trip-info" v-if="trip">
        <p v-if="trip.pickup_location_name || trip.pickup_lat != null" class="location-row">
          <strong>Pickup:</strong>
          <span v-if="trip.pickup_location_name">{{ trip.pickup_location_name }} (</span>{{ formatCoords(trip.pickup_lat, trip.pickup_lng) }}<span v-if="trip.pickup_location_name">)</span>
        </p>
        <p v-if="trip.destination_name || trip.drop_lat != null" class="location-row">
          <strong>Destination:</strong>
          <span v-if="trip.destination_name">{{ trip.destination_name }} (</span>{{ formatCoords(trip.drop_lat, trip.drop_lng) }}<span v-if="trip.destination_name">)</span>
        </p>
        <p class="location-row tracking-row">
          <strong>Tracking:</strong>
          <span v-if="trackingLocationName">{{ trackingLocationName }} (</span>{{ currentLat != null ? `${currentLat.toFixed(5)}, ${currentLng.toFixed(5)}` : '—' }}<span v-if="trackingLocationName">)</span>
        </p>
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
import { useAuthStore } from '../stores/auth'
import { endTrip as apiEndTrip } from '../services/tripService'
import { updateLocation } from '../services/gpsService'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const tripId = route.params.id

const trip = ref(null)
const currentLat = ref(null)
const currentLng = ref(null)
const trackingLocationName = ref('')
const ending = ref(false)
const error = ref('')

let gpsInterval = null
let watchId = null

function formatCoords(lat, lng) {
  if (lat != null && lng != null) return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
  return '—'
}

async function fetchTrackingLocationName(lat, lng) {
  const orgId = trip.value?.organization_id ?? auth.driver?.organization_id
  if (!orgId) return
  try {
    const { data } = await api.get('/preset-locations/nearby', { params: { lat, lng, organization_id: orgId } })
    trackingLocationName.value = data?.name || ''
  } catch {
    trackingLocationName.value = ''
  }
}

function onLocation(pos) {
  currentLat.value = pos.coords.latitude
  currentLng.value = pos.coords.longitude
  fetchTrackingLocationName(pos.coords.latitude, pos.coords.longitude)
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
.trip-info {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.location-row {
  margin: 0.5rem 0;
  color: #475569;
  font-size: 0.95rem;
}
.tracking-row { margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0; }
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
