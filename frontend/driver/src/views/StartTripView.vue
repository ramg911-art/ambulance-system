<template>
  <div class="start-trip">
    <header class="header">
      <button @click="$router.push('/')" class="back">← Back</button>
      <h1>Start Trip</h1>
    </header>
    <div class="content">
      <div v-if="!presetLocation" class="status">
        <p v-if="locationError">{{ locationError }}</p>
        <p v-else>Detecting pickup location...</p>
        <p class="coords" v-if="currentLat">📍 {{ currentLat.toFixed(5) }}, {{ currentLng.toFixed(5) }}</p>
      </div>
      <div v-else class="preset-detected">
        <p class="label">Pickup location detected</p>
        <h2>{{ presetLocation.name }}</h2>
      </div>
      <div v-if="presetLocation" class="form-section">
        <label>Destination</label>
        <select v-model="selectedDestination" :disabled="!destinations.length">
          <option value="">-- Select destination --</option>
          <option v-for="d in destinations" :key="d.id" :value="d.id">
            {{ d.name }} {{ fixedAmount ? `(₹${fixedAmount})` : '' }}
          </option>
        </select>
      </div>
      <div class="form-section">
        <label>Vehicle</label>
        <select v-model="selectedVehicle" required>
          <option value="">-- Select vehicle --</option>
          <option v-for="v in vehicles" :key="v.id" :value="v.id">{{ v.registration_number }}</option>
        </select>
      </div>
      <p v-if="submitError" class="error">{{ submitError }}</p>
      <button
        class="start-btn"
        :disabled="loading || !selectedVehicle || (presetLocation && !selectedDestination)"
        @click="startTrip"
      >
        {{ loading ? 'Starting...' : 'Start Trip' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { createTrip, startTrip as apiStartTrip } from '../services/tripService'

const router = useRouter()
const auth = useAuthStore()

const presetLocation = ref(null)
const destinations = ref([])
const selectedDestination = ref('')
const vehicles = ref([])
const selectedVehicle = ref('')
const fixedAmount = ref(null)
const currentLat = ref(null)
const currentLng = ref(null)
const locationError = ref('')
const submitError = ref('')
const loading = ref(false)

const ORG_ID = 1
let watchId = null

async function detectPresetLocation() {
  if (!currentLat.value || !currentLng.value) return
  try {
    const { data } = await api.get('/preset-locations/nearby', {
      params: { lat: currentLat.value, lng: currentLng.value, organization_id: ORG_ID },
    })
    presetLocation.value = data
    if (data) {
      const { data: dests } = await api.get(`/preset-destinations/by-source/${data.id}`, {
        params: { organization_id: ORG_ID },
      })
      destinations.value = dests
      selectedDestination.value = dests[0]?.id || ''
    } else {
      destinations.value = []
      selectedDestination.value = ''
    }
  } catch {
    presetLocation.value = null
    destinations.value = []
  }
}

async function fetchFixedTariff() {
  if (!presetLocation.value || !selectedDestination.value) {
    fixedAmount.value = null
    return
  }
  try {
    const { data } = await api.get('/tariffs/fixed', {
      params: {
        organization_id: ORG_ID,
        source_id: presetLocation.value.id,
        destination_id: selectedDestination.value,
      },
    })
    fixedAmount.value = data?.amount ?? null
  } catch {
    fixedAmount.value = null
  }
}

watch(selectedDestination, fetchFixedTariff)

function onLocation(pos) {
  currentLat.value = pos.coords.latitude
  currentLng.value = pos.coords.longitude
}

function onLocationError(err) {
  locationError.value = 'Enable location access to detect pickup'
  console.error(err)
}

onMounted(async () => {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocation not supported'
    return
  }
  watchId = navigator.geolocation.watchPosition(onLocation, onLocationError, {
    enableHighAccuracy: true,
    maximumAge: 5000,
  })
  try {
    const { data } = await api.get('/vehicles', { params: { organization_id: ORG_ID } })
    vehicles.value = data
    if (data.length) selectedVehicle.value = data[0].id
  } catch {
    vehicles.value = []
  }
})

watch([currentLat, currentLng], () => {
  if (currentLat.value && currentLng.value) detectPresetLocation()
}, { immediate: true })

onUnmounted(() => {
  if (watchId) navigator.geolocation.clearWatch(watchId)
})

async function startTrip() {
  submitError.value = ''
  loading.value = true
  try {
    const isFixed = !!presetLocation.value && !!selectedDestination.value
    const trip = await createTrip({
      organization_id: ORG_ID,
      driver_id: auth.driver.id,
      vehicle_id: parseInt(selectedVehicle.value, 10),
      source_preset_id: presetLocation.value?.id || null,
      destination_preset_id: selectedDestination.value ? parseInt(selectedDestination.value, 10) : null,
      pickup_lat: currentLat.value,
      pickup_lng: currentLng.value,
      is_fixed_tariff: isFixed,
    })
    await apiStartTrip(trip.id)
    router.push(`/trip/${trip.id}`)
  } catch (e) {
    submitError.value = e.response?.data?.detail || 'Failed to start trip'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.start-trip {
  min-height: 100vh;
  background: #f8fafc;
}
.header {
  background: #1e3a8a;
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}
.back {
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}
h1 { font-size: 1.25rem; }
.content { padding: 1.5rem; }
.status, .preset-detected {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
  text-align: center;
}
.label { color: #64748b; font-size: 0.9rem; margin-bottom: 0.25rem; }
h2 { font-size: 1.25rem; color: #1e293b; }
.coords { font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; }
.form-section {
  margin-bottom: 1rem;
}
.form-section label {
  display: block;
  font-size: 0.875rem;
  color: #475569;
  margin-bottom: 0.25rem;
}
.form-section select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
}
.start-btn {
  width: 100%;
  padding: 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 0.5rem;
}
.start-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #dc2626; font-size: 0.875rem; margin-bottom: 0.5rem; }
</style>
