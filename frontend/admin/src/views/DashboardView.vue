<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="date-filter">
        <label>Period</label>
        <select v-model="datePreset" @change="onDatePresetChange">
          <option value="today">Today</option>
          <option value="yesterday">Yesterday</option>
          <option value="week">Last 7 days</option>
          <option value="month">This month</option>
          <option value="custom">Custom</option>
        </select>
        <template v-if="datePreset === 'custom'">
          <input v-model="dateFrom" type="date" class="date-input" />
          <span class="date-sep">to</span>
          <input v-model="dateTo" type="date" class="date-input" />
        </template>
        <button class="btn-apply" @click="loadData">Apply</button>
      </div>
    </header>

    <div class="tiles-grid">
      <!-- Live tracking tile -->
      <div class="tile tile-map">
        <div class="tile-header">
          <h3>Live Tracking</h3>
          <router-link to="/live" class="tile-link">View full →</router-link>
        </div>
        <div class="map-tile-wrap">
          <LiveTrackingMap :locations="liveLocations" :height="320" />
        </div>
        <p v-if="liveLocations.length === 0" class="tile-empty">No vehicles online</p>
        <div v-else class="live-count">{{ liveLocations.length }} vehicle(s) active</div>
      </div>

      <!-- Stats row -->
      <div class="tile tile-stat">
        <h3>Trips</h3>
        <p class="stat-value">{{ tripsCount }}</p>
        <p class="stat-label">in selected period</p>
      </div>
      <div class="tile tile-stat">
        <h3>Collection</h3>
        <p class="stat-value">{{ collectionFormatted }}</p>
        <p class="stat-label">total fare</p>
      </div>
      <div class="tile tile-stat">
        <h3>Organizations</h3>
        <p class="stat-value">{{ orgs }}</p>
      </div>
      <div class="tile tile-stat">
        <h3>Vehicles</h3>
        <p class="stat-value">{{ vehiclesTotal }}</p>
      </div>

      <!-- Top drivers tile -->
      <div class="tile tile-list">
        <h3>Top Drivers</h3>
        <p v-if="topDrivers.length === 0" class="tile-empty">No trips in period</p>
        <ul v-else class="tile-list-items">
          <li v-for="(d, i) in topDrivers" :key="d.id">
            <span class="rank">{{ i + 1 }}</span>
            <span class="name">{{ d.name }}</span>
            <span class="value">{{ d.count }} trips</span>
          </li>
        </ul>
      </div>

      <!-- Top locations tile -->
      <div class="tile tile-list">
        <h3>Top Locations</h3>
        <p v-if="topLocations.length === 0" class="tile-empty">No trips in period</p>
        <ul v-else class="tile-list-items">
          <li v-for="(loc, i) in topLocations" :key="loc.name + (loc.type || '')">
            <span class="rank">{{ i + 1 }}</span>
            <span class="name">{{ loc.name }}</span>
            <span class="value">{{ loc.count }} {{ loc.type === 'origin' ? 'pickups' : 'dropoffs' }}</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../services/api'
import LiveTrackingMap from '../components/LiveTrackingMap.vue'

const datePreset = ref('today')
const dateFrom = ref('')
const dateTo = ref('')
const orgs = ref(0)
const vehiclesTotal = ref(0)
const liveLocations = ref([])
const tripsData = ref([])

function getDateRange() {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  let from, to
  if (datePreset.value === 'today') {
    from = new Date(today)
    to = new Date(today)
  } else if (datePreset.value === 'yesterday') {
    from = new Date(today)
    from.setDate(from.getDate() - 1)
    to = new Date(from)
  } else if (datePreset.value === 'week') {
    from = new Date(today)
    from.setDate(from.getDate() - 7)
    to = new Date(today)
  } else if (datePreset.value === 'month') {
    from = new Date(today.getFullYear(), today.getMonth(), 1)
    to = new Date(today)
  } else {
    from = dateFrom.value ? new Date(dateFrom.value) : null
    to = dateTo.value ? new Date(dateTo.value) : null
  }
  return {
    from: from ? from.toISOString().slice(0, 10) : null,
    to: to ? to.toISOString().slice(0, 10) : null,
  }
}

function onDatePresetChange() {
  if (datePreset.value === 'custom') {
    const t = new Date()
    t.setHours(0, 0, 0, 0)
    const f = new Date(t)
    f.setDate(f.getDate() - 7)
    dateFrom.value = f.toISOString().slice(0, 10)
    dateTo.value = t.toISOString().slice(0, 10)
  }
}

const tripsCount = computed(() => tripsData.value.length)

const collectionFormatted = computed(() => {
  const sum = tripsData.value.reduce((a, t) => a + (t.total_amount || 0), 0)
  return `₹${sum.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`
})

const topDrivers = computed(() => {
  const byDriver = {}
  for (const t of tripsData.value) {
    const id = t.driver_id
    const name = t.driver_name || `Driver #${id}`
    if (!byDriver[id]) byDriver[id] = { id, name, count: 0 }
    byDriver[id].count++
  }
  return Object.values(byDriver).sort((a, b) => b.count - a.count).slice(0, 5)
})

const topLocations = computed(() => {
  const byOrigin = {}
  const byDest = {}
  for (const t of tripsData.value) {
    const o = t.pickup_location_name || (t.pickup_lat != null ? `GPS pickup` : null)
    const d = t.destination_name || (t.drop_lat != null ? `GPS destination` : null)
    if (o) {
      byOrigin[o] = (byOrigin[o] || 0) + 1
    }
    if (d) {
      byDest[d] = (byDest[d] || 0) + 1
    }
  }
  const items = [
    ...Object.entries(byOrigin).map(([name, count]) => ({ name, count, type: 'origin' })),
    ...Object.entries(byDest).map(([name, count]) => ({ name, count, type: 'dest' })),
  ].sort((a, b) => b.count - a.count).slice(0, 5)
  return items
})

async function loadData() {
  const { from, to } = getDateRange()
  try {
    const [oRes, vRes, liveRes, tripsRes] = await Promise.all([
      api.get('/organizations'),
      api.get('/vehicles', { params: { active_only: false } }),
      api.get('/gps/vehicles/live'),
      api.get('/trips', {
        params: { ...(from && { date_from: from }), ...(to && { date_to: to }) },
      }),
    ])
    orgs.value = oRes.data?.length ?? 0
    vehiclesTotal.value = vRes.data?.length ?? 0
    liveLocations.value = liveRes.data ?? []
    tripsData.value = tripsRes.data ?? []
  } catch (e) {
    console.error('Dashboard load error:', e)
  }
}

let liveInterval = null
onMounted(() => {
  onDatePresetChange()
  loadData()
  liveInterval = setInterval(() => {
    api.get('/gps/vehicles/live').then((r) => { liveLocations.value = r.data ?? [] }).catch(() => {})
  }, 60 * 1000)
})
onUnmounted(() => {
  if (liveInterval) clearInterval(liveInterval)
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}
.dashboard-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.dashboard-header h1 {
  font-size: 1.5rem;
  color: #0f172a;
  font-weight: 700;
}
.date-filter {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.date-filter label {
  font-size: 0.875rem;
  color: #64748b;
  margin-right: 0.25rem;
}
.date-filter select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
}
.date-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 0.9rem;
}
.date-sep { font-size: 0.875rem; color: #64748b; }
.btn-apply {
  padding: 0.5rem 1rem;
  background: #1e3a8a;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: 500;
}
.btn-apply:hover { background: #1e40af; }

.tiles-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}
@media (max-width: 1200px) {
  .tiles-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .tiles-grid { grid-template-columns: 1fr; }
}

.tile {
  background: white;
  border-radius: 1rem;
  padding: 1.25rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid #f1f5f9;
  transition: box-shadow 0.2s;
}
.tile:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.tile h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.tile-map {
  grid-column: span 2;
  grid-row: span 1;
}
@media (max-width: 768px) {
  .tile-map { grid-column: span 1; }
}
.tile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}
.tile-link {
  font-size: 0.875rem;
  color: #2563eb;
  text-decoration: none;
  font-weight: 500;
}
.tile-link:hover { text-decoration: underline; }
.map-tile-wrap {
  border-radius: 0.75rem;
  overflow: hidden;
  min-height: 320px;
  background: #f8fafc;
}
.live-count {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #64748b;
}
.tile-empty {
  color: #94a3b8;
  font-size: 0.9rem;
  padding: 1rem 0;
  margin: 0;
}

.tile-stat {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.tile-stat .stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.2;
}
.tile-stat .stat-label {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0.25rem 0 0;
}

.tile-list { }
.tile-list-items {
  list-style: none;
  margin: 0;
  padding: 0;
}
.tile-list-items li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.9rem;
}
.tile-list-items li:last-child { border-bottom: none; }
.tile-list-items .rank {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  background: #e2e8f0;
  color: #64748b;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}
.tile-list-items .name {
  flex: 1;
  color: #334155;
  font-weight: 500;
}
.tile-list-items .value {
  font-size: 0.8rem;
  color: #64748b;
}
</style>
