<template>
  <div class="active-trip">
    <header class="header">
      <h1>Trip #{{ tripId }}</h1>
      <span class="status in-progress">In Progress</span>
    </header>
    <div class="content">
      <div class="trip-info" v-if="trip">
        <p v-if="trip.pickup_lat != null" class="location-row">
          <strong>Pickup:</strong>
          <span v-if="geoPickup">{{ geoPickup }} (</span>{{ formatCoords(trip.pickup_lat, trip.pickup_lng) }}<span v-if="geoPickup">)</span>
        </p>
        <p v-if="trip.drop_lat != null" class="location-row">
          <strong>Destination:</strong>
          <span v-if="geoDest">{{ geoDest }} (</span>{{ formatCoords(trip.drop_lat, trip.drop_lng) }}<span v-if="geoDest">)</span>
        </p>
        <p class="location-row tracking-row">
          <strong>Tracking:</strong>
          <span v-if="geoTracking">{{ geoTracking }} (</span>{{ currentLat != null ? `${currentLat.toFixed(5)}, ${currentLng.toFixed(5)}` : '—' }}<span v-if="geoTracking">)</span>
        </p>
      </div>
      <button class="end-btn" @click="endTrip" :disabled="ending">
        {{ ending ? 'Ending...' : 'End Trip' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <!-- Trip summary popup after ending -->
    <Teleport to="body">
      <div v-if="summaryModalVisible" class="modal-overlay" @click.self="closeSummaryModal">
        <div class="summary-modal">
          <h2>Trip Complete</h2>
          <div v-if="tripSummary" class="summary-content">
            <p><strong>Pickup:</strong> {{ tripSummary.pickup_location_name || formatCoords(tripSummary.pickup_lat, tripSummary.pickup_lng) || '—' }}</p>
            <p><strong>Destination:</strong> {{ tripSummary.destination_name || formatCoords(tripSummary.drop_lat, tripSummary.drop_lng) || '—' }}</p>
            <p><strong>Distance:</strong> {{ tripSummary.distance_km != null ? `${tripSummary.distance_km.toFixed(2)} km` : '—' }}</p>
            <p><strong>Elapsed time:</strong> {{ elapsedTimeFormatted }}</p>
            <p class="total-fare"><strong>Total fare:</strong> {{ totalFareFormatted }}</p>
          </div>
          <button class="close-btn" @click="closeSummaryModal">Close</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { endTrip as apiEndTrip } from '../services/tripService'
import { updateLocation } from '../services/gpsService'
import { reverseGeocode } from '../services/mapsService'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const tripId = route.params.id

const trip = ref(null)
const currentLat = ref(null)
const currentLng = ref(null)
const geoPickup = ref('')
const geoDest = ref('')
const geoTracking = ref('')
const ending = ref(false)
const error = ref('')
const summaryModalVisible = ref(false)
const tripSummary = ref(null)

let gpsInterval = null
let watchId = null

function formatCoords(lat, lng) {
  if (lat != null && lng != null) return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
  return '—'
}

async function fetchGeoName(lat, lng) {
  try {
    return await reverseGeocode(lat, lng) || ''
  } catch {
    return ''
  }
}

function onLocation(pos) {
  currentLat.value = pos.coords.latitude
  currentLng.value = pos.coords.longitude
  fetchGeoName(pos.coords.latitude, pos.coords.longitude).then((n) => { geoTracking.value = n })
}

watch(trip, async (t) => {
  if (!t) return
  if (t.pickup_lat != null && t.pickup_lng != null) {
    geoPickup.value = await fetchGeoName(t.pickup_lat, t.pickup_lng)
  }
  if (t.drop_lat != null && t.drop_lng != null) {
    geoDest.value = await fetchGeoName(t.drop_lat, t.drop_lng)
  }
}, { immediate: true })

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

const elapsedTimeFormatted = computed(() => {
  const s = tripSummary.value
  if (!s?.start_time || !s?.end_time) return '—'
  const start = new Date(s.start_time)
  const end = new Date(s.end_time)
  const ms = end - start
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  if (mins >= 60) {
    const hrs = Math.floor(mins / 60)
    return `${hrs}h ${mins % 60}m ${secs}s`
  }
  return `${mins}m ${secs}s`
})

const totalFareFormatted = computed(() => {
  const s = tripSummary.value
  if (s?.total_amount != null) return `₹${s.total_amount.toFixed(2)}`
  return '—'
})

function closeSummaryModal() {
  summaryModalVisible.value = false
  tripSummary.value = null
  router.push('/trips/today')
}

async function endTrip() {
  error.value = ''
  ending.value = true
  try {
    const summary = await apiEndTrip(tripId)
    tripSummary.value = summary
    summaryModalVisible.value = true
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

/* Trip summary modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.summary-modal {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  max-width: 400px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}
.summary-modal h2 {
  font-size: 1.25rem;
  color: #1e293b;
  margin-bottom: 1rem;
}
.summary-content p {
  margin: 0.5rem 0;
  color: #475569;
  font-size: 0.95rem;
}
.summary-content .total-fare {
  font-size: 1.1rem;
  color: #1e3a8a;
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}
.close-btn {
  width: 100%;
  margin-top: 1.25rem;
  padding: 0.75rem;
  background: #1e3a8a;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}
</style>
