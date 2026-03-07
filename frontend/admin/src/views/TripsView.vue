<template>
  <div class="trips">
    <h1>Trips</h1>
    <div class="filters">
      <div class="filter-row">
        <label>Date range</label>
        <select v-model="datePreset" @change="onDatePresetChange">
          <option value="7d">Last 7 days</option>
          <option value="month">This month</option>
          <option value="6m">Last 6 months</option>
          <option value="custom">Custom</option>
        </select>
        <template v-if="datePreset === 'custom'">
          <input v-model="dateFrom" type="date" class="date-input" />
          <span>to</span>
          <input v-model="dateTo" type="date" class="date-input" />
        </template>
      </div>
      <div class="filter-row">
        <label>Driver</label>
        <select v-model="filterDriverId" class="filter-select">
          <option value="">All drivers</option>
          <option v-for="d in drivers" :key="d.id" :value="d.id">{{ d.name }} ({{ d.phone }})</option>
        </select>
      </div>
      <div class="filter-row">
        <label>Vehicle</label>
        <select v-model="filterVehicleId" class="filter-select">
          <option value="">All vehicles</option>
          <option v-for="v in vehicles" :key="v.id" :value="v.id">{{ v.registration_number }}</option>
        </select>
      </div>
      <button class="btn-apply" @click="loadTrips">Apply</button>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date & Time</th>
            <th>Driver</th>
            <th>Vehicle</th>
            <th>Origin</th>
            <th>Destination</th>
            <th>Elapsed</th>
            <th>Distance</th>
            <th>Amount</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in trips" :key="t.id">
            <td>{{ formatDateTime(t.start_time) }}</td>
            <td>{{ t.driver_name || '-' }}</td>
            <td>{{ t.vehicle_registration_number || '-' }}</td>
            <td>{{ originDisplay(t) }}</td>
            <td>{{ destinationDisplay(t) }}</td>
            <td>{{ formatElapsed(t.start_time, t.end_time) }}</td>
            <td>{{ t.distance_km != null ? `${t.distance_km.toFixed(2)} km` : '-' }}</td>
            <td>{{ t.total_amount != null ? `₹${t.total_amount.toFixed(2)}` : '-' }}</td>
            <td><span :class="['badge', t.status]">{{ t.status }}</span></td>
          </tr>
        </tbody>
      </table>
      <p v-if="trips.length === 0" class="empty">No trips match the filters.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const trips = ref([])
const drivers = ref([])
const vehicles = ref([])
const datePreset = ref('7d')
const dateFrom = ref('')
const dateTo = ref('')
const filterDriverId = ref('')
const filterVehicleId = ref('')

function getDefaultDateRange() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const from = new Date(today)
  if (datePreset.value === '7d') {
    from.setDate(from.getDate() - 7)
  } else if (datePreset.value === 'month') {
    from.setDate(1)
  } else if (datePreset.value === '6m') {
    from.setMonth(from.getMonth() - 6)
  }
  return {
    from: from.toISOString().slice(0, 10),
    to: today.toISOString().slice(0, 10),
  }
}

function onDatePresetChange() {
  const range = datePreset.value === 'custom'
    ? (() => {
        const t = new Date()
        t.setHours(0, 0, 0, 0)
        const f = new Date(t)
        f.setDate(f.getDate() - 7)
        return { from: f.toISOString().slice(0, 10), to: t.toISOString().slice(0, 10) }
      })()
    : getDefaultDateRange()
  dateFrom.value = range.from
  dateTo.value = range.to
}

function applyDefaultDates() {
  const { from, to } = getDefaultDateRange()
  dateFrom.value = from
  dateTo.value = to
}

function formatDateTime(dt) {
  if (!dt) return '—'
  const d = new Date(dt)
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatElapsed(startTime, endTime) {
  if (!startTime || !endTime) return '—'
  const start = new Date(startTime)
  const end = new Date(endTime)
  const ms = end - start
  const mins = Math.floor(ms / 60000)
  const secs = Math.floor((ms % 60000) / 1000)
  if (mins >= 60) {
    const hrs = Math.floor(mins / 60)
    return `${hrs}h ${mins % 60}m`
  }
  return `${mins}m ${secs}s`
}

function originDisplay(t) {
  return t.pickup_location_name || (t.pickup_lat != null && t.pickup_lng != null ? `${t.pickup_lat.toFixed(4)}, ${t.pickup_lng.toFixed(4)}` : null) || '—'
}

function destinationDisplay(t) {
  return t.destination_name || (t.drop_lat != null && t.drop_lng != null ? `${t.drop_lat.toFixed(4)}, ${t.drop_lng.toFixed(4)}` : null) || '—'
}

async function loadTrips() {
  try {
    const params = {}
    if (filterDriverId.value) params.driver_id = filterDriverId.value
    if (filterVehicleId.value) params.vehicle_id = filterVehicleId.value
    const from = datePreset.value === 'custom' ? dateFrom.value : getDefaultDateRange().from
    const to = datePreset.value === 'custom' ? dateTo.value : getDefaultDateRange().to
    if (from) params.date_from = from
    if (to) params.date_to = to
    const { data } = await api.get('/trips', { params })
    trips.value = data || []
  } catch (e) {
    console.error('Failed to load trips:', e)
    trips.value = []
  }
}

async function loadDrivers() {
  try {
    const { data } = await api.get('/drivers', { params: { active_only: false } })
    drivers.value = data || []
  } catch {
    drivers.value = []
  }
}

async function loadVehicles() {
  try {
    const { data } = await api.get('/vehicles', { params: { active_only: false } })
    vehicles.value = data || []
  } catch {
    vehicles.value = []
  }
}

onMounted(() => {
  applyDefaultDates()
  loadDrivers()
  loadVehicles()
  loadTrips()
})
</script>

<style scoped>
h1 { margin-bottom: 1rem; color: #1e293b; }
.filters {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
}
.filter-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.filter-row label {
  font-size: 0.875rem;
  color: #64748b;
  white-space: nowrap;
}
.filter-row select {
  padding: 0.4rem 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  min-width: 140px;
}
.filter-select { min-width: 180px; }
.date-input {
  padding: 0.4rem 0.6rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.375rem;
  font-size: 0.9rem;
}
.btn-apply {
  padding: 0.5rem 1rem;
  background: #1e3a8a;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.9rem;
  cursor: pointer;
}
.btn-apply:hover { background: #1e40af; }
.table-wrap {
  background: white;
  border-radius: 0.5rem;
  overflow-x: auto;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
table { width: 100%; border-collapse: collapse; min-width: 900px; }
th, td { padding: 0.75rem 1rem; text-align: left; }
th { background: #f8fafc; font-size: 0.875rem; color: #64748b; white-space: nowrap; }
tr:not(:last-child) td { border-bottom: 1px solid #e2e8f0; }
td { font-size: 0.9rem; color: #334155; }
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}
.badge.completed { background: #dcfce7; color: #166534; }
.badge.in_progress { background: #dbeafe; color: #1d4ed8; }
.badge.pending { background: #fef3c7; color: #92400e; }
.empty {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}
</style>
