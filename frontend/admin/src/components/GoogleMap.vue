<template>
  <div class="google-map-wrap">
    <div v-if="loadError" class="map-error">
      {{ loadError }}
    </div>
    <div v-else ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { loadMap, createMarker, updateMarker, centerMap } from '../services/mapsService'

const props = defineProps({
  modelValue: { type: Object, default: null }, // { lat, lng }
  markers: { type: Array, default: () => [] }, // [{ id?, lat, lng, title? }]
  readonly: { type: Boolean, default: false },
  showCurrentLocation: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

const mapContainer = ref(null)
const loadError = ref('')
const mapRef = ref(null)
const selectedMarker = ref(null)
const currentLocationMarker = ref(null)
const propMarkers = ref([]) // Map of id -> Marker

async function initMap() {
  if (!mapContainer.value) return
  loadError.value = ''
  try {
    await loadMap()
    if (!window.google?.maps) {
      loadError.value = 'Google Maps failed to load'
      return
    }
    const center = props.modelValue || { lat: 12.9716, lng: 77.5946 }
    const map = new window.google.maps.Map(mapContainer.value, {
      center: { lat: center.lat, lng: center.lng },
      zoom: 14,
      mapTypeControl: true,
      streetViewControl: false,
      fullscreenControl: true,
      zoomControl: true,
    })
    mapRef.value = map

    if (!props.readonly) {
      map.addListener('click', (e) => {
        const lat = e.latLng.lat()
        const lng = e.latLng.lng()
        emit('update:modelValue', { lat, lng })
      })
    }

    syncMarkers()
    syncSelectedMarker()
    syncCurrentLocation()
  } catch (e) {
    loadError.value = e.message || 'Failed to load map'
    console.error('Map load error:', e)
  }
}

function syncSelectedMarker() {
  if (!mapRef.value) return
  if (selectedMarker.value) {
    selectedMarker.value.setMap(null)
    selectedMarker.value = null
  }
  if (props.modelValue) {
    selectedMarker.value = createMarker(mapRef.value, props.modelValue, {
      draggable: !props.readonly,
      title: 'Selected',
    })
    if (selectedMarker.value && !props.readonly) {
      selectedMarker.value.addListener('dragend', () => {
        const pos = selectedMarker.value.getPosition()
        emit('update:modelValue', { lat: pos.lat(), lng: pos.lng() })
      })
    }
  }
}

function syncMarkers() {
  if (!mapRef.value) return
  propMarkers.value.forEach((m) => {
    if (m && m.setMap) m.setMap(null)
  })
  propMarkers.value = []
  props.markers.forEach((item) => {
    const lat = item.lat ?? item.latitude
    const lng = item.lng ?? item.longitude
    if (lat == null || lng == null) return
    const marker = createMarker(mapRef.value, { lat, lng }, {
      title: item.title || item.name || '',
      draggable: false,
    })
    if (marker) propMarkers.value.push(marker)
  })
}

function syncCurrentLocation() {
  if (!mapRef.value || !props.showCurrentLocation) {
    if (currentLocationMarker.value) {
      currentLocationMarker.value.setMap(null)
      currentLocationMarker.value = null
    }
    return
  }
  if (!navigator.geolocation) return
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude
      const lng = pos.coords.longitude
      if (currentLocationMarker.value) {
        updateMarker(currentLocationMarker.value, { lat, lng })
      } else if (mapRef.value) {
        currentLocationMarker.value = createMarker(mapRef.value, { lat, lng }, {
          title: 'Current location',
          draggable: false,
        })
        if (currentLocationMarker.value) {
          currentLocationMarker.value.setIcon({
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#4285f4',
            fillOpacity: 1,
            strokeColor: 'white',
            strokeWeight: 2,
          })
        }
      }
    },
    () => {}
  )
}

watch(() => props.modelValue, syncSelectedMarker, { deep: true })
watch(() => props.markers, syncMarkers, { deep: true })
watch(() => props.showCurrentLocation, syncCurrentLocation)

onMounted(initMap)
onUnmounted(() => {
  if (selectedMarker.value) selectedMarker.value.setMap(null)
  propMarkers.value.forEach((m) => m?.setMap?.(null))
  if (currentLocationMarker.value) currentLocationMarker.value.setMap(null)
  mapRef.value = null
})
</script>

<style scoped>
.google-map-wrap {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
.map-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
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
