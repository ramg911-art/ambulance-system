<template>
  <div class="start-trip">
    <header class="header">
      <button @click="$router.push('/')" class="back">← Back</button>
      <h1>Start Trip</h1>
    </header>
    <div class="content">
      <div class="mode-toggle">
        <button
          type="button"
          :class="{ active: useManualSelection }"
          @click="useManualSelection = true"
        >
          Select from presets
        </button>
        <button
          type="button"
          :class="{ active: !useManualSelection }"
          @click="useManualSelection = false"
        >
          Use my location
        </button>
      </div>
      <div v-if="useManualSelection" class="manual-select-section">
        <div class="form-section">
          <label>Pickup location</label>
          <select v-model="selectedPresetLocationFallback" @change="onPresetLocationSelected">
            <option value="">-- Select preset location --</option>
            <option v-for="pl in presetLocations" :key="pl.id" :value="pl.id">{{ pl.name }}</option>
          </select>
          <p v-if="!presetLocations.length" class="hint">No preset locations. Contact admin.</p>
        </div>
        <div v-if="presetLocation" class="pickup-summary">
          <p class="label">Pickup location</p>
          <p class="pickup-name">{{ presetLocation.name }}</p>
          <p class="coords">{{ presetLocation.latitude.toFixed(4) }}, {{ presetLocation.longitude.toFixed(4) }}</p>
        </div>
        <p v-if="presetLocation && !destinations.length" class="hint">No tariffs for this route. Admin must add tariff in Tariffs page.</p>
      </div>
      <div v-else-if="!presetLocation" class="status">
        <p v-if="locationError">{{ locationError }}</p>
        <p v-else-if="!locationRequested">Tap below to enable location (required for pickup detection)</p>
        <p v-else>Detecting pickup location...</p>
        <p class="coords" v-if="currentLat">📍 {{ currentLat.toFixed(5) }}, {{ currentLng.toFixed(5) }}</p>
        <button v-if="!currentLat && !isSecureContextError" class="location-btn" @click="requestLocation">
          {{ locationError ? 'Retry location' : 'Allow location access' }}
        </button>
        <div v-if="isSecureContextError" class="manual-coords">
          <p class="hint">Enter coordinates manually (location requires HTTPS):</p>
          <input v-model.number="manualLat" type="number" step="0.0001" placeholder="Latitude" />
          <input v-model.number="manualLng" type="number" step="0.0001" placeholder="Longitude" />
          <button class="location-btn" @click="applyManualCoords">Use coordinates</button>
        </div>
        <div v-if="(locationError || isSecureContextError) && presetLocations.length" class="fallback-preset">
          <p class="hint">Or select preset location above (Select from presets)</p>
        </div>
      </div>
      <div v-else class="preset-detected">
        <p class="label">Pickup location detected</p>
        <p class="pickup-name">{{ presetLocation.name }}</p>
        <p class="coords">{{ presetLocation.latitude.toFixed(4) }}, {{ presetLocation.longitude.toFixed(4) }}</p>
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
      <div v-if="presetLocation && (currentLat || presetLocation.latitude)" class="map-section">
        <h3>Route Preview</h3>
        <div class="map-box">
          <GoogleMap
            :markers="tripMapMarkers"
            :current-position="pickupPosition"
            readonly
          />
        </div>
      </div>
      <div class="form-section">
        <label>Vehicle</label>
        <select v-model="selectedVehicle" required>
          <option value="">-- Select vehicle --</option>
          <option v-for="v in vehicles" :key="v.id" :value="v.id">{{ v.registration_number }}</option>
        </select>
        <p v-if="vehiclesError" class="error">{{ vehiclesError }}</p>
        <p v-else-if="!vehicles.length" class="hint">No vehicles found.</p>
        <button v-if="vehiclesError || !vehicles.length" class="retry-btn" @click="loadVehicles">Retry load vehicles</button>
      </div>
      <p v-if="submitError" class="error">{{ submitError }}</p>
      <button
        class="start-btn"
        :disabled="loading || !selectedVehicle || !canStartTrip"
        @click="startTrip"
      >
        {{ loading ? 'Starting...' : 'Start Trip' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'
import { createTrip, startTrip as apiStartTrip } from '../services/tripService'
import GoogleMap from '../components/GoogleMap.vue'

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
const locationRequested = ref(false)
const isSecureContextError = ref(false)
const manualLat = ref(null)
const manualLng = ref(null)
const presetLocations = ref([])
const selectedPresetLocationFallback = ref('')
const useManualSelection = ref(true)
const submitError = ref('')
const vehiclesError = ref('')
const loading = ref(false)

const orgId = ref(1)
let watchId = null

function applyManualCoords() {
  if (manualLat.value != null && manualLng.value != null && !isNaN(manualLat.value) && !isNaN(manualLng.value)) {
    currentLat.value = manualLat.value
    currentLng.value = manualLng.value
  }
}

async function loadPresetLocationsForFallback() {
  try {
    const { data } = await api.get('/preset-locations/for-driver')
    presetLocations.value = Array.isArray(data) ? data : []
  } catch {
    presetLocations.value = []
  }
}

async function onPresetLocationSelected() {
  const id = selectedPresetLocationFallback.value
  if (!id) return
  const pl = presetLocations.value.find((p) => p.id === parseInt(id, 10))
  if (pl && pl.latitude != null && pl.longitude != null) {
    presetLocation.value = pl
    currentLat.value = pl.latitude
    currentLng.value = pl.longitude
    try {
      const { data: dests } = await api.get(`/preset-destinations/by-source/${pl.id}`, {
        params: { organization_id: orgId.value },
      })
      destinations.value = dests || []
      selectedDestination.value = dests?.[0]?.id || ''
    } catch {
      destinations.value = []
      selectedDestination.value = ''
    }
  }
}

const pickupPosition = computed(() => {
  if (currentLat.value != null && currentLng.value != null) {
    return { lat: currentLat.value, lng: currentLng.value }
  }
  if (presetLocation.value?.latitude != null && presetLocation.value?.longitude != null) {
    return { lat: presetLocation.value.latitude, lng: presetLocation.value.longitude }
  }
  return null
})

const canStartTrip = computed(() => {
  if (!selectedVehicle.value) return false
  if (presetLocation.value) {
    if (!selectedDestination.value) return false
    const hasCoords = (presetLocation.value.latitude != null && presetLocation.value.longitude != null) ||
      (currentLat.value != null && currentLng.value != null)
    return hasCoords
  }
  return currentLat.value != null && currentLng.value != null
})

const tripMapMarkers = computed(() => {
  if (!selectedDestination.value) return []
  const dest = destinations.value.find((d) => d.id === parseInt(selectedDestination.value, 10))
  if (!dest || dest.latitude == null || dest.longitude == null) return []
  return [{ lat: dest.latitude, lng: dest.longitude, name: dest.name }]
})

function requestLocation() {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocation not supported'
    return
  }
  locationRequested.value = true
  locationError.value = ''
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      currentLat.value = pos.coords.latitude
      currentLng.value = pos.coords.longitude
      if (!watchId) {
        watchId = navigator.geolocation.watchPosition(onLocation, onLocationError, {
          enableHighAccuracy: true,
          maximumAge: 5000,
        })
      }
    },
    onLocationError,
    { enableHighAccuracy: true }
  )
}

async function detectPresetLocation() {
  if (!currentLat.value || !currentLng.value) return
  try {
    const { data } = await api.get('/preset-locations/nearby', {
      params: { lat: currentLat.value, lng: currentLng.value, organization_id: orgId.value },
    })
    presetLocation.value = data
    if (data) {
      const { data: dests } = await api.get(`/preset-destinations/by-source/${data.id}`, {
        params: { organization_id: orgId.value },
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
        organization_id: orgId.value,
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
  const isSecureOrigin = err?.code === 1 && err?.message?.toLowerCase().includes('secure')
  if (isSecureOrigin) {
    locationError.value = 'Location requires HTTPS. Serve app over HTTPS, or enter coordinates manually below.'
    isSecureContextError.value = true
  } else {
    locationError.value = 'Enable location access to detect pickup'
  }
  console.error('Geolocation error:', err)
}

async function loadVehicles() {
  vehiclesError.value = ''
  try {
    const { data } = await api.get('/vehicles/for-driver', { params: { active_only: false } })
    const list = Array.isArray(data) ? data : (data?.data ?? data?.vehicles ?? [])
    vehicles.value = list
    if (list.length) selectedVehicle.value = list[0].id
  } catch (e) {
    vehicles.value = []
    let msg = e.response?.data?.detail || e.message || 'Failed to load vehicles'
    if (e.response?.status === 401) {
      msg = 'Session expired. Please log out and log in again.'
    }
    vehiclesError.value = msg
    console.error('Failed to load vehicles:', e)
  }
}

onMounted(async () => {
  if (!navigator.geolocation) {
    locationError.value = 'Geolocation not supported'
  }
  orgId.value = auth.driver?.organization_id ?? 1
  await loadPresetLocationsForFallback()
  if (!orgId.value && auth.driver?.id) {
    try {
      const { data } = await api.get('/auth/me')
      orgId.value = data.organization_id ?? 1
    } catch {
      orgId.value = 1
    }
  }
  await loadVehicles()
})

watch([currentLat, currentLng], () => {
  if (currentLat.value && currentLng.value && !selectedPresetLocationFallback.value) detectPresetLocation()
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
      organization_id: orgId.value,
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
.pickup-summary { margin-top: 0.75rem; padding: 0.75rem; background: #f8fafc; border-radius: 0.375rem; }
.pickup-name { font-weight: 600; color: #1e293b; font-size: 1rem; margin: 0.25rem 0; }
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
.hint { color: #64748b; font-size: 0.875rem; margin-top: 0.25rem; }
.location-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
}
.location-btn:active { opacity: 0.9; }
.manual-coords {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.manual-coords input {
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
}
.retry-btn {
  margin-top: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
}
.retry-btn:hover { background: #e2e8f0; }
.fallback-preset { margin-top: 1rem; }
.fallback-preset select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
}
.map-section { margin-top: 1rem; }
.map-section h3 { font-size: 0.875rem; color: #475569; margin-bottom: 0.5rem; }
.map-box { height: 220px; border-radius: 0.5rem; overflow: hidden; }
.mode-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.25rem;
  background: #e2e8f0;
  border-radius: 0.5rem;
}
.mode-toggle button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  color: #64748b;
}
.mode-toggle button.active {
  background: #1e3a8a;
  color: white;
}
.manual-select-section {
  margin-bottom: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}
</style>
