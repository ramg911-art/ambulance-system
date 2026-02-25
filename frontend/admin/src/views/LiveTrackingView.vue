<template>
  <div class="live-tracking">
    <h1>Live Tracking</h1>
    <div class="map-placeholder">
      <div v-if="locations.length === 0" class="empty">No vehicles online</div>
      <div v-else class="list">
        <div v-for="loc in locations" :key="loc.vehicle_id" class="vehicle">
          <span>Vehicle #{{ loc.vehicle_id }}</span>
          <span class="coords">{{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

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
.map-placeholder {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  min-height: 400px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.empty { color: #64748b; text-align: center; padding: 4rem; }
.list { display: flex; flex-direction: column; gap: 0.5rem; }
.vehicle {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 0.375rem;
}
.coords { font-size: 0.875rem; color: #64748b; }
</style>
