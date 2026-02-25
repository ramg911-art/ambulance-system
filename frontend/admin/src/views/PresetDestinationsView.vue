<template>
  <div class="preset-destinations">
    <h1>Preset Destinations</h1>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Lat</th>
            <th>Lng</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in destinations" :key="d.id">
            <td>{{ d.id }}</td>
            <td>{{ d.name }}</td>
            <td>{{ d.latitude.toFixed(4) }}</td>
            <td>{{ d.longitude.toFixed(4) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const destinations = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/preset-destinations')
    destinations.value = data
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
</style>
