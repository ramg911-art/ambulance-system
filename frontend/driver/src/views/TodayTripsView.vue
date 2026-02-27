<template>
  <div class="today-trips">
    <header class="header">
      <button class="back-btn" @click="$router.push('/')">← Back</button>
      <h1>Today's Trips</h1>
    </header>
    <div class="content">
      <p v-if="loading" class="hint">Loading...</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-else-if="!trips.length" class="empty">No trips today yet.</p>
      <div v-else class="trip-list">
        <div v-for="trip in trips" :key="trip.id" class="trip-card">
          <div class="trip-header">
            <span class="trip-id">Trip #{{ trip.id }}</span>
            <span :class="['status', trip.status]">{{ trip.status }}</span>
          </div>
          <p><strong>Pickup:</strong> {{ trip.pickup_location_name || formatCoords(trip.pickup_lat, trip.pickup_lng) || '—' }}</p>
          <p><strong>Destination:</strong> {{ trip.destination_name || formatCoords(trip.drop_lat, trip.drop_lng) || '—' }}</p>
          <p v-if="trip.distance_km != null"><strong>Distance:</strong> {{ trip.distance_km.toFixed(2) }} km</p>
          <p v-if="trip.start_time && trip.end_time"><strong>Duration:</strong> {{ formatDuration(trip.start_time, trip.end_time) }}</p>
          <p v-if="trip.total_amount != null" class="total-fare"><strong>Total:</strong> ₹{{ trip.total_amount.toFixed(2) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDriverTripsToday } from '../services/tripService'

const trips = ref([])
const loading = ref(true)
const error = ref('')

function formatCoords(lat, lng) {
  if (lat != null && lng != null) return `${lat.toFixed(4)}, ${lng.toFixed(4)}`
  return null
}

function formatDuration(startTime, endTime) {
  const start = new Date(startTime)
  const end = new Date(endTime)
  const ms = end - start
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  if (mins >= 60) {
    const hrs = Math.floor(mins / 60)
    return `${hrs}h ${mins % 60}m ${secs}s`
  }
  return `${mins}m ${secs}s`
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    trips.value = await getDriverTripsToday()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load trips'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.today-trips {
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
.back-btn {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
}
h1 { font-size: 1.25rem; margin: 0; }
.content { padding: 1.5rem; }
.hint, .error, .empty {
  color: #64748b;
  font-size: 0.95rem;
}
.error { color: #dc2626; }
.trip-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.trip-card {
  background: white;
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.trip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}
.trip-id { font-weight: 600; color: #1e293b; }
.status {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  text-transform: uppercase;
}
.status.completed { background: #dcfce7; color: #166534; }
.status.in_progress { background: #fef3c7; color: #92400e; }
.status.pending { background: #e2e8f0; color: #475569; }
.trip-card p {
  margin: 0.35rem 0;
  color: #475569;
  font-size: 0.9rem;
}
.trip-card .total-fare {
  color: #1e3a8a;
  font-weight: 600;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e2e8f0;
}
</style>
