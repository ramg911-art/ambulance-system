<template>
  <div class="tariffs">
    <h1>Fixed Tariffs</h1>
    <button class="btn-primary" @click="openCreate">+ Add Tariff</button>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Source (Location)</th>
            <th>Destination</th>
            <th>Amount</th>
            <th>Org</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tariffs" :key="t.id">
            <td>{{ t.id }}</td>
            <td>{{ sourceName(t.source_id) }}</td>
            <td>{{ destName(t.destination_id) }}</td>
            <td>₹{{ t.amount }}</td>
            <td>{{ t.organization_id }}</td>
            <td>
              <button class="btn-sm" @click="openEdit(t)">Edit</button>
              <button class="btn-sm btn-danger" @click="confirmDelete(t)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edit Tariff' : 'Add Tariff' }}</h3>
        <form @submit.prevent="save">
          <label>Organization ID</label>
          <input v-model.number="form.organization_id" type="number" required :disabled="!!editingId" />
          <label>Source (Preset Location ID)</label>
          <input v-model.number="form.source_id" type="number" required :disabled="!!editingId" />
          <label>Destination (Preset Destination ID)</label>
          <input v-model.number="form.destination_id" type="number" required :disabled="!!editingId" />
          <label>Amount (₹)</label>
          <input v-model.number="form.amount" type="number" step="0.01" required />
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

const tariffs = ref([])
const locations = ref([])
const destinations = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref({
  organization_id: 1,
  source_id: 1,
  destination_id: 1,
  amount: 0,
})

function toArray(val) {
  if (Array.isArray(val)) return val
  if (val?.data) return Array.isArray(val.data) ? val.data : []
  if (val?.items) return Array.isArray(val.items) ? val.items : []
  return []
}

function sourceName(id) {
  const arr = toArray(locations.value)
  const loc = arr.find(l => l.id === id)
  return loc ? loc.name : id
}

function destName(id) {
  const arr = toArray(destinations.value)
  const d = arr.find(x => x.id === id)
  return d ? d.name : id
}

async function load() {
  try {
    const [tRes, lRes, dRes] = await Promise.all([
      api.get('/tariffs'),
      api.get('/preset-locations'),
      api.get('/preset-destinations'),
    ])
    tariffs.value = toArray(tRes.data)
    locations.value = toArray(lRes.data)
    destinations.value = toArray(dRes.data)
  } catch (e) {
    console.error('Failed to load tariffs:', e)
    tariffs.value = []
    locations.value = []
    destinations.value = []
  }
}

function openCreate() {
  editingId.value = null
  form.value = { organization_id: 1, source_id: 1, destination_id: 1, amount: 0 }
  if (locations.value.length) form.value.source_id = locations.value[0].id
  if (destinations.value.length) form.value.destination_id = destinations.value[0].id
  showModal.value = true
}

function openEdit(t) {
  editingId.value = t.id
  form.value = { ...t }
  showModal.value = true
}

async function save() {
  try {
    if (editingId.value) {
      await api.patch(`/tariffs/${editingId.value}`, { amount: form.value.amount })
    } else {
      await api.post('/tariffs', form.value)
    }
    showModal.value = false
    load()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to save')
  }
}

async function confirmDelete(t) {
  if (!confirm('Delete this tariff?')) return
  try {
    await api.delete(`/tariffs/${t.id}`)
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
