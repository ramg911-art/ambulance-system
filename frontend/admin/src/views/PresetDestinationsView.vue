<template>
  <div class="preset-destinations">
    <h1>Preset Destinations</h1>
    <button class="btn-primary" @click="openCreate">+ Add Destination</button>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Lat</th>
            <th>Lng</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in destinations" :key="d.id">
            <td>{{ d.id }}</td>
            <td>{{ d.name }}</td>
            <td>{{ d.latitude.toFixed(4) }}</td>
            <td>{{ d.longitude.toFixed(4) }}</td>
            <td>
              <button class="btn-sm" @click="openEdit(d)">Edit</button>
              <button class="btn-sm btn-danger" @click="confirmDelete(d)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edit Destination' : 'Add Destination' }}</h3>
        <form @submit.prevent="save">
          <label>Name</label>
          <input v-model="form.name" required />
          <label>Latitude</label>
          <input v-model.number="form.latitude" type="number" step="any" required />
          <label>Longitude</label>
          <input v-model.number="form.longitude" type="number" step="any" required />
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
import { ref, onMounted } from 'vue'
import api from '../services/api'

const destinations = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref({ name: '', latitude: 0, longitude: 0 })

async function load() {
  const { data } = await api.get('/preset-destinations')
  destinations.value = data
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', latitude: 0, longitude: 0 }
  showModal.value = true
}

function openEdit(d) {
  editingId.value = d.id
  form.value = { ...d }
  showModal.value = true
}

async function save() {
  try {
    if (editingId.value) {
      await api.patch(`/preset-destinations/${editingId.value}`, form.value)
    } else {
      await api.post('/preset-destinations', form.value)
    }
    showModal.value = false
    load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to save')
  }
}

async function confirmDelete(d) {
  if (!confirm(`Delete destination ${d.name}?`)) return
  try {
    await api.delete(`/preset-destinations/${d.id}`)
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
.modal { background: white; padding: 1.5rem; border-radius: 0.5rem; min-width: 320px; }
.modal h3 { margin-bottom: 1rem; }
.modal label { display: block; margin-bottom: 0.25rem; font-size: 0.875rem; }
.modal input { width: 100%; padding: 0.5rem; margin-bottom: 0.75rem; }
.modal-actions { margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
