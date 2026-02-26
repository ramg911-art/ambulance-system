<template>
  <div class="preset-locations">
    <h1>Preset Locations</h1>
    <button class="btn-primary" @click="openCreate">+ Add Location</button>
    <div class="map-section" v-if="locations.length">
      <h3>All Locations</h3>
      <div class="map-box">
        <GoogleMap
          :markers="locationMarkers"
          readonly
        />
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Lat</th>
            <th>Lng</th>
            <th>Radius (m)</th>
            <th>Org</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in locations" :key="l.id">
            <td>{{ l.id ?? '-' }}</td>
            <td>{{ l.name || '-' }}</td>
            <td>{{ l.latitude != null ? Number(l.latitude).toFixed(4) : '-' }}</td>
            <td>{{ l.longitude != null ? Number(l.longitude).toFixed(4) : '-' }}</td>
            <td>{{ l.radius_meters ?? '-' }}</td>
            <td>{{ l.organization_id ?? '-' }}</td>
            <td>
              <button class="btn-sm" @click="openEdit(l)">Edit</button>
              <button class="btn-sm btn-danger" @click="confirmDelete(l)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal modal-wide">
        <h3>{{ editingId ? 'Edit Location' : 'Add Location' }}</h3>
        <p class="map-hint">Click on map to select location, or drag the marker</p>
        <div class="modal-map">
          <GoogleMap
            :model-value="formCoords"
            @update:model-value="onMapSelect"
            :readonly="false"
          />
        </div>
        <form @submit.prevent="save">
          <label>Organization ID</label>
          <input v-model.number="form.organization_id" type="number" required :disabled="!!editingId" />
          <label>Name</label>
          <input v-model="form.name" required />
          <label>Latitude</label>
          <input v-model.number="form.latitude" type="number" step="any" required />
          <label>Longitude</label>
          <input v-model.number="form.longitude" type="number" step="any" required />
          <label>Radius (meters)</label>
          <input v-model.number="form.radius_meters" type="number" required />
          <label><input type="checkbox" v-model="form.active" /> Active</label>
          <div class="modal-actions">
            <button type="button" @click="showModal = false">Cancel</button>
            <button type="submit">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'
import GoogleMap from '../components/GoogleMap.vue'

const locations = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref({
  organization_id: 1,
  name: '',
  latitude: 0,
  longitude: 0,
  radius_meters: 100,
  active: true,
})

const formCoords = computed(() =>
  form.value.latitude != null && form.value.longitude != null
    ? { lat: form.value.latitude, lng: form.value.longitude }
    : null
)

const locationMarkers = computed(() =>
  locations.value
    .filter((l) => l.latitude != null && l.longitude != null)
    .map((l) => ({ lat: l.latitude, lng: l.longitude, name: l.name }))
)

function onMapSelect(pos) {
  form.value.latitude = pos.lat
  form.value.longitude = pos.lng
}

async function load() {
  try {
    const res = await api.get('/preset-locations')
    const data = res.data
    locations.value = Array.isArray(data) ? data : (data?.data || data?.items || [])
  } catch (e) {
    console.error('Failed to load locations:', e)
    locations.value = []
  }
}

function openCreate() {
  editingId.value = null
  form.value = { organization_id: 1, name: '', latitude: 12.9716, longitude: 77.5946, radius_meters: 100, active: true }
  showModal.value = true
}

function openEdit(l) {
  editingId.value = l.id
  form.value = { ...l }
  showModal.value = true
}

async function save() {
  try {
    if (editingId.value) {
      await api.patch(`/preset-locations/${editingId.value}`, form.value)
    } else {
      await api.post('/preset-locations', form.value)
    }
    showModal.value = false
    load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to save')
  }
}

async function confirmDelete(l) {
  if (!confirm(`Delete location ${l.name}?`)) return
  try {
    await api.delete(`/preset-locations/${l.id}`)
    load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to delete')
  }
}

onMounted(load)
</script>

<style scoped>
h1 { margin-bottom: 1rem; color: #1e293b; }
.btn-primary { margin-bottom: 1rem; padding: 0.5rem 1rem; background: #2563eb; color: white; border: none; border-radius: 0.375rem; cursor: pointer; }
.btn-sm { margin-right: 0.25rem; padding: 0.25rem 0.5rem; font-size: 0.875rem; cursor: pointer; }
.btn-danger { background: #dc2626; color: white; border: none; border-radius: 0.25rem; }
.table-wrap { background: white; border-radius: 0.5rem; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.75rem 1rem; text-align: left; }
th { background: #f8fafc; font-size: 0.875rem; color: #64748b; }
tr:not(:last-child) td { border-bottom: 1px solid #e2e8f0; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: white; padding: 1.5rem; border-radius: 0.5rem; min-width: 320px; max-height: 90vh; overflow-y: auto; }
.modal-wide { min-width: 480px; max-width: 90vw; }
.map-section { margin-bottom: 1rem; }
.map-section h3 { margin-bottom: 0.5rem; font-size: 1rem; color: #64748b; }
.map-box { height: 320px; border-radius: 0.5rem; overflow: hidden; border: 1px solid #e2e8f0; }
.modal-map { height: 260px; margin-bottom: 1rem; border-radius: 0.5rem; overflow: hidden; }
.map-hint { font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem; }
.modal h3 { margin-bottom: 1rem; }
.modal label { display: block; margin-bottom: 0.25rem; font-size: 0.875rem; }
.modal input { width: 100%; padding: 0.5rem; margin-bottom: 0.75rem; }
.modal-actions { margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
