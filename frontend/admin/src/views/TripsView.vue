<template>
  <div class="trips">
    <h1>Trips</h1>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Driver</th>
            <th>Vehicle</th>
            <th>Status</th>
            <th>Amount</th>
            <th>Distance</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in trips" :key="t.id">
            <td>{{ t.id }}</td>
            <td>{{ t.driver_id }}</td>
            <td>{{ t.vehicle_id }}</td>
            <td><span :class="['badge', t.status]">{{ t.status }}</span></td>
            <td>{{ t.total_amount != null ? `₹${t.total_amount}` : '-' }}</td>
            <td>{{ t.distance_km != null ? `${t.distance_km.toFixed(2)} km` : '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const trips = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/trips')
    trips.value = data
  } catch {}
})
</script>

<style scoped>
h1 { margin-bottom: 1rem; color: #1e293b; }
.table-wrap {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.75rem 1rem; text-align: left; }
th { background: #f8fafc; font-size: 0.875rem; color: #64748b; }
tr:not(:last-child) td { border-bottom: 1px solid #e2e8f0; }
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}
.badge.completed { background: #dcfce7; color: #166534; }
.badge.in_progress { background: #dbeafe; color: #1d4ed8; }
.badge.pending { background: #fef3c7; color: #92400e; }
</style>
