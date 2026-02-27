<template>
  <div class="live-tracking">
    <h1>Live Tracking</h1>
    <div class="map-wrapper">
      <LiveTrackingMap :locations="locations" />
    </div>
    <div v-if="locations.length > 0" class="vehicle-list">
      <div v-for="loc in locationsWithNames" :key="loc.vehicle_id" class="vehicle">
        <div class="vehicle-header">
          <span class="vehicle-num">Vehicle {{ loc.registration_number || '#' + loc.vehicle_id }}</span>
          <span class="coords">
            <span v-if="loc.geo_current">{{ loc.geo_current }} (</span>{{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }}<span v-if="loc.geo_current">)</span>
          </span>
        </div>
        <div v-if="loc.pickup_lat != null || loc.destination_lat != null" class="trip-details">
          <p v-if="loc.pickup_lat != null" class="location-row">
            <strong>Pickup:</strong>
            <span v-if="loc.geo_pickup">{{ loc.geo_pickup }} (</span>{{ loc.pickup_lat.toFixed(4) }}, {{ loc.pickup_lng.toFixed(4) }}<span v-if="loc.geo_pickup">)</span>
          </p>
          <p v-if="loc.destination_lat != null" class="location-row">
            <strong>Destination:</strong>
            <span v-if="loc.geo_dest">{{ loc.geo_dest }} (</span>{{ loc.destination_lat.toFixed(4) }}, {{ loc.destination_lng.toFixed(4) }}<span v-if="loc.geo_dest">)</span>
          </p>
        </div>
        <p v-else class="vehicle-pos">
          <strong>Current:</strong>
          <span v-if="loc.geo_current">{{ loc.geo_current }} (</span>{{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }}<span v-if="loc.geo_current">)</span>
        </p>
      </div>
    </div>
    <div v-else class="empty">No vehicles online</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import { reverseGeocode } from '../services/mapsService'
import LiveTrackingMap from '../components/LiveTrackingMap.vue'

const locations = ref([])
const geocodedNames = ref({})

async function geocodeLocations(newLocations) {
  const toFetch = []
  for (const loc of newLocations) {
    const vid = loc.vehicle_id
    if (loc.latitude != null && loc.longitude != null) {
      const key = `${vid}_current`
      if (!geocodedNames.value[key]) toFetch.push({ key, lat: loc.latitude, lng: loc.longitude })
    }
    if (loc.pickup_lat != null && loc.pickup_lng != null) {
      const key = `${vid}_pickup`
      if (!geocodedNames.value[key]) toFetch.push({ key, lat: loc.pickup_lat, lng: loc.pickup_lng })
    }
    if (loc.destination_lat != null && loc.destination_lng != null) {
      const key = `${vid}_dest`
      if (!geocodedNames.value[key]) toFetch.push({ key, lat: loc.destination_lat, lng: loc.destination_lng })
    }
  }
  for (const { key, lat, lng } of toFetch) {
    try {
      const name = await reverseGeocode(lat, lng)
      if (name) geocodedNames.value[key] = name
    } catch {}
  }
}

const locationsWithNames = computed(() => {
  return locations.value.map((loc) => ({
    ...loc,
    geo_current: geocodedNames.value[`${loc.vehicle_id}_current`] || null,
    geo_pickup: geocodedNames.value[`${loc.vehicle_id}_pickup`] || null,
    geo_dest: geocodedNames.value[`${loc.vehicle_id}_dest`] || null,
  }))
})

async function fetchLocations() {
  try {
    const { data } = await api.get('/gps/vehicles/live')
    locations.value = data
    geocodeLocations(data)
  } catch {}
}

onMounted(() => {
  fetchLocations()
  setInterval(fetchLocations, 5000)
})
</script>

<style scoped>
h1 { margin-bottom: 1rem; color: #1e293b; }
.map-wrapper {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  min-height: 450px;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.empty { color: #64748b; text-align: center; padding: 2rem; }
.vehicle-list { display: flex; flex-direction: column; gap: 0.75rem; }
.vehicle {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 0.5rem;
}
.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.vehicle-num { font-weight: 600; color: #1e293b; }
.coords { font-size: 0.875rem; color: #64748b; }
.trip-details { font-size: 0.9rem; }
.location-row { margin: 0.25rem 0; }
.vehicle-pos { margin: 0; font-size: 0.9rem; }
</style>
