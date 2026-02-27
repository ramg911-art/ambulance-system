<template>
  <div class="live-tracking-map">
    <div v-if="loadError" class="map-error">{{ loadError }}</div>
    <div v-else ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { loadMap, createMarker, updateMarker } from '../services/mapsService'

const props = defineProps({
  locations: { type: Array, default: () => [] }, // [{ vehicle_id, latitude, longitude }]
})

const mapContainer = ref(null)
const loadError = ref('')
const mapRef = ref(null)
const markersByVehicle = ref({}) // vehicle_id -> Marker

async function initMap() {
  if (!mapContainer.value) return
  loadError.value = ''
  try {
    await loadMap()
    if (!window.google?.maps) {
      loadError.value = 'Google Maps failed to load'
      return
    }
    const map = new window.google.maps.Map(mapContainer.value, {
      center: { lat: 12.9716, lng: 77.5946 },
      zoom: 12,
      mapTypeControl: true,
      streetViewControl: false,
      fullscreenControl: true,
      zoomControl: true,
    })
    mapRef.value = map
    syncMarkers()
  } catch (e) {
    loadError.value = e.message || 'Failed to load map'
    console.error('Map load error:', e)
  }
}

function syncMarkers() {
  if (!mapRef.value) return
  const current = new Set(props.locations.map((l) => l.vehicle_id))
  for (const [vid, marker] of Object.entries(markersByVehicle.value)) {
    if (!current.has(parseInt(vid, 10))) {
      marker.setMap(null)
      delete markersByVehicle.value[vid]
    }
  }
  for (const loc of props.locations) {
    const vid = loc.vehicle_id
    const lat = loc.latitude ?? loc.lat
    const lng = loc.longitude ?? loc.lng
    if (lat == null || lng == null) continue
    const pos = { lat, lng }
    const label = loc.registration_number || `#${vid}`
    const labelText = String(label).slice(0, 8)
    const existing = markersByVehicle.value[vid]
    if (existing) {
      updateMarker(existing, pos)
      existing.setLabel({ text: labelText, color: '#fff', fontWeight: 'bold', fontSize: '11px' })
    } else {
      const marker = createMarker(mapRef.value, pos, {
        title: `Vehicle ${label}`,
        draggable: false,
        label: { text: labelText, color: '#fff', fontWeight: 'bold', fontSize: '11px' },
      })
      if (marker) markersByVehicle.value[vid] = marker
    }
  }
}

watch(() => props.locations, syncMarkers, { deep: true })

onMounted(initMap)
onUnmounted(() => {
  for (const m of Object.values(markersByVehicle.value)) {
    m?.setMap?.(null)
  }
  markersByVehicle.value = {}
  mapRef.value = null
})
</script>

<style scoped>
.live-tracking-map {
  width: 100%;
  height: 450px;
}
.map-container {
  width: 100%;
  height: 450px;
}
.map-error {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  text-align: center;
  border-radius: 0.5rem;
}
</style>
