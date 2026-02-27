<template>
  <div class="live-tracking-map">
    <div v-if="loadError" class="map-error">{{ loadError }}</div>
    <div v-else ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { loadMap, createMarker, updateMarker, fitMapToBounds } from '../services/mapsService'

const ANIMATION_DURATION_MS = 20000

const props = defineProps({
  locations: { type: Array, default: () => [] }, // [{ vehicle_id, latitude, longitude }]
})

const mapContainer = ref(null)
const loadError = ref('')
const mapRef = ref(null)
const markersByVehicle = ref({}) // vehicle_id -> Marker
const animationFrameIds = ref({}) // vehicle_id -> raf id

/**
 * Smoothly animate marker from start to end position using requestAnimationFrame.
 * Cancels any existing animation for the same vehicle.
 */
function animateMarker(marker, start, end, duration, vehicleId) {
  if (animationFrameIds.value[vehicleId] != null) {
    cancelAnimationFrame(animationFrameIds.value[vehicleId])
    animationFrameIds.value[vehicleId] = null
  }
  const startTime = performance.now()

  function tick(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)

    const lat = start.lat + (end.lat - start.lat) * progress
    const lng = start.lng + (end.lng - start.lng) * progress

    if (marker?.setPosition) {
      marker.setPosition({ lat, lng })
    }

    if (progress < 1) {
      animationFrameIds.value[vehicleId] = requestAnimationFrame(tick)
    } else {
      delete animationFrameIds.value[vehicleId]
    }
  }

  animationFrameIds.value[vehicleId] = requestAnimationFrame(tick)
}

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

function getMarkerLabel(loc) {
  const regNo = loc.registration_number || `#${loc.vehicle_id}`
  const driver = loc.driver_name || ''
  if (driver) {
    return `${regNo} - ${driver}`.slice(0, 20)
  }
  return String(regNo).slice(0, 12)
}

function syncMarkers() {
  if (!mapRef.value || !window.google?.maps) return
  const current = new Set(props.locations.map((l) => l.vehicle_id))
  for (const [vid, marker] of Object.entries(markersByVehicle.value)) {
    if (!current.has(parseInt(vid, 10))) {
      if (animationFrameIds.value[vid] != null) {
        cancelAnimationFrame(animationFrameIds.value[vid])
        delete animationFrameIds.value[vid]
      }
      marker.setMap(null)
      delete markersByVehicle.value[vid]
    }
  }
  const g = window.google.maps
  const iconConfig = {
    url: '/ambulance-marker.svg',
    scaledSize: new g.Size(40, 40),
    anchor: new g.Point(20, 40),
    labelOrigin: new g.Point(20, -4),
  }
  for (const loc of props.locations) {
    const vid = loc.vehicle_id
    const lat = loc.latitude ?? loc.lat
    const lng = loc.longitude ?? loc.lng
    if (lat == null || lng == null) continue
    const pos = { lat, lng }
    const labelText = getMarkerLabel(loc)
    const title = `${loc.registration_number || 'Vehicle #' + vid}${loc.driver_name ? ' - ' + loc.driver_name : ''}`
    const existing = markersByVehicle.value[vid]
    if (existing) {
      const currentPos = existing.getPosition()
      const start = currentPos
        ? { lat: currentPos.lat(), lng: currentPos.lng() }
        : pos
      const end = { lat, lng }
      const needsAnimation = Math.abs(start.lat - end.lat) > 1e-6 || Math.abs(start.lng - end.lng) > 1e-6

      existing.setLabel({ text: labelText, color: '#1e293b', fontWeight: 'bold', fontSize: '10px' })
      existing.setIcon(iconConfig)
      existing.setTitle(title)

      if (needsAnimation) {
        animateMarker(existing, start, end, ANIMATION_DURATION_MS, vid)
      } else {
        updateMarker(existing, pos)
      }
    } else {
      const marker = createMarker(mapRef.value, pos, {
        title,
        draggable: false,
        icon: iconConfig,
        label: { text: labelText, color: '#1e293b', fontWeight: 'bold', fontSize: '10px' },
      })
      if (marker) markersByVehicle.value[vid] = marker
    }
  }
  const positions = props.locations
    .filter((l) => (l.latitude ?? l.lat) != null && (l.longitude ?? l.lng) != null)
    .map((l) => ({ lat: l.latitude ?? l.lat, lng: l.longitude ?? l.lng }))
  if (positions.length > 0) {
    fitMapToBounds(mapRef.value, positions)
  }
}

watch(() => props.locations, syncMarkers, { deep: true })

onMounted(initMap)
onUnmounted(() => {
  for (const vid of Object.keys(animationFrameIds.value)) {
    if (animationFrameIds.value[vid] != null) {
      cancelAnimationFrame(animationFrameIds.value[vid])
    }
  }
  animationFrameIds.value = {}
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
