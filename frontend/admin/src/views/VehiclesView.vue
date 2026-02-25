<template>
  <div class="vehicles">
    <h1>Vehicles</h1>
    <button class="btn-primary" @click="openCreate">+ Add Vehicle</button>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Registration</th>
            <th>Make/Model</th>
            <th>Org</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="v in vehicles" :key="v.id || v">
            <td>{{ v.id ?? '-' }}</td>
            <td>{{ v.registration_number || '-' }}</td>
            <td>{{ v.make_model || '-' }}</td>
            <td>{{ v.organization_id ?? '-' }}</td>
            <td>{{ v.active ? 'Yes' : 'No' }}</td>
            <td>
              <button class="btn-sm" @click="openEdit(v)">Edit</button>
              <button class="btn-sm btn-danger" @click="confirmDelete(v)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edit Vehicle' : 'Add Vehicle' }}</h3>
        <form @submit.prevent="save">
          <label>Organization ID</label>
          <input v-model.number="form.organization_id" type="number" required :disabled="!!editingId" />
          <label>Registration Number</label>
          <input v-model="form.registration_number" required />
          <label>Make/Model</label>
          <input v-model="form.make_model" />
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
import { ref, onMounted } from 'vue'
import api from '../services/api'

const vehicles = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref({
  organization_id: 1,
  registration_number: '',
  make_model: '',
  active: true,
})

async function load() {
  try {
    const res = await api.get('/vehicles', { params: { active_only: false } })
    vehicles.value = Array.isArray(res.data) ? res.data : (res.data?.data || res.data?.items || [])
  } catch (e) {
    console.error('Failed to load vehicles:', e)
    vehicles.value = []
  }
}

function openCreate() {
  editingId.value = null
  form.value = { organization_id: 1, registration_number: '', make_model: '', active: true }
  showModal.value = true
}

function openEdit(v) {
  editingId.value = v.id
  form.value = { ...v }
  showModal.value = true
}

async function save() {
  const reg = (form.value.registration_number || '').trim()
  if (!reg) {
    alert('Registration number is required')
    return
  }
  try {
    if (editingId.value) {
      await api.patch(`/vehicles/${editingId.value}`, {
        registration_number: reg,
        make_model: (form.value.make_model || '').trim() || null,
        active: form.value.active,
      })
    } else {
      await api.post('/vehicles', {
        organization_id: form.value.organization_id,
        registration_number: reg,
        make_model: (form.value.make_model || '').trim() || null,
        active: form.value.active,
      })
    }
    showModal.value = false
    await load()
  } catch (e) {
    const err = e.response?.data
    const status = e.response?.status
    const url = e.config?.baseURL && e.config?.url ? `${e.config.baseURL.replace(/\/$/, '')}${e.config.url}` : ''
    let msg = 'Failed to save vehicle'
    if (!e.response) {
      msg = 'Network error - request did not reach server. Check: (1) Backend running, (2) API URL correct (see console), (3) CORS/proxy allows POST'
    } else if (err?.detail) {
      msg = typeof err.detail === 'string' ? err.detail : (Array.isArray(err.detail) ? err.detail.map(d => d.msg || d).join(', ') : String(err.detail))
    } else if (status) {
      msg = `Error ${status}: ${msg}`
    }
    if (url) msg += `\n\nURL: ${url}`
    msg += '\n\nOpen Console (F12) for details.'
    console.error('[VehiclesView] save failed', { status, url, error: e })
    alert(msg)
  }
}

async function confirmDelete(v) {
  if (!confirm(`Delete vehicle ${v.registration_number}?`)) return
  try {
    await api.delete(`/vehicles/${v.id}`)
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
.modal input[type="text"], .modal input[type="number"] { width: 100%; padding: 0.5rem; margin-bottom: 0.75rem; }
.modal-actions { margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
