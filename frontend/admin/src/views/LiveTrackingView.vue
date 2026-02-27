<template>
  <div class="live-tracking">
    <h1>Live Tracking</h1>
    <div class="map-wrapper">
      <LiveTrackingMap :locations="locations" />
    </div>
    <div v-if="locations.length > 0" class="vehicle-list">
      <div v-for="loc in locations" :key="loc.vehicle_id" class="vehicle">
        <div class="vehicle-header">
          <span class="vehicle-num">Vehicle {{ loc.registration_number || '#' + loc.vehicle_id }}</span>
          <span class="coords">{{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }}</span>
        </div>
        <div v-if="loc.pickup_location_name || loc.destination_name" class="trip-details">
          <p v-if="loc.pickup_location_name" class="location-row">
            <strong>Pickup:</strong> {{ loc.pickup_location_name }}
            <span v-if="loc.pickup_lat != null" class="coords"
              >({{ loc.pickup_lat.toFixed(4) }}, {{ loc.pickup_lng.toFixed(4) }})</span
            >
          </p>
          <p v-if="loc.destination_name" class="location-row">
            <strong>Destination:</strong> {{ loc.destination_name }}
            <span v-if="loc.destination_lat != null" class="coords"
              >({{ loc.destination_lat.toFixed(4) }}, {{ loc.destination_lng.toFixed(4) }})</span
            >
          </p>
        </div>
        <p v-else class="vehicle-pos">
          <strong>Current:</strong>
          <span v-if="loc.current_location_name">{{ loc.current_location_name }} (</span>{{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }}<span v-if="loc.current_location_name">)</span>
        </p>
      </div>
    </div>
    <div v-else class="empty">No vehicles online</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import LiveTrackingMap from '../components/LiveTrackingMap.vue'

const locations = ref([])

async function fetchLocations() {
  try {
    const { data } = await api.get('/gps/vehicles/live')
    locations.value = data
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
