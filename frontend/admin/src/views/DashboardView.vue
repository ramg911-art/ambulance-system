<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <div class="grid">
      <div class="card">
        <h3>Organizations</h3>
        <p class="stat">{{ orgs }}</p>
      </div>
      <div class="card">
        <h3>Vehicles</h3>
        <p class="stat">{{ vehicles }}</p>
      </div>
      <div class="card">
        <h3>Live Vehicles</h3>
        <p class="stat">{{ liveCount }}</p>
      </div>
      <div class="card">
        <h3>Trips Today</h3>
        <p class="stat">{{ trips }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const orgs = ref(0)
const vehicles = ref(0)
const liveCount = ref(0)
const trips = ref(0)

onMounted(async () => {
  try {
    const [o, v, l, t] = await Promise.all([
      api.get('/organizations'),
      api.get('/vehicles'),
      api.get('/gps/vehicles/live'),
      api.get('/trips', { params: { status: 'completed' } }),
    ])
    orgs.value = o.data?.length ?? 0
    vehicles.value = v.data?.length ?? 0
    liveCount.value = l.data?.length ?? 0
    trips.value = t.data?.length ?? 0
  } catch {}
})
</script>

<style scoped>
h1 { margin-bottom: 1.5rem; color: #1e293b; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.card {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.card h3 { font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem; }
.stat { font-size: 2rem; font-weight: 700; color: #1e293b; }
</style>
