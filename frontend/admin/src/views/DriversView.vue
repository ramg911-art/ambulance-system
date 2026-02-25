<template>
  <div class="drivers">
    <h1>Drivers</h1>
    <button class="btn-primary" @click="openCreate">+ Add Driver</button>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Phone</th>
            <th>Org</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in drivers" :key="d.id || d">
            <td>{{ d.id ?? '-' }}</td>
            <td>{{ d.name || '-' }}</td>
            <td>{{ d.phone || '-' }}</td>
            <td>{{ d.organization_id ?? '-' }}</td>
            <td>{{ d.active ? 'Yes' : 'No' }}</td>
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
        <h3>{{ editingId ? 'Edit Driver' : 'Add Driver' }}</h3>
        <form @submit.prevent="save">
          <label>Organization ID</label>
          <input v-model.number="form.organization_id" type="number" required :disabled="!!editingId" />
          <label>Name</label>
          <input v-model="form.name" required />
          <label>Phone</label>
          <input v-model="form.phone" required :disabled="!!editingId" />
          <label>Password {{ editingId ? '(leave blank to keep)' : '' }}</label>
          <input v-model="form.password" type="password" :required="!editingId" :placeholder="editingId ? 'Leave blank to keep' : ''" />
          <label>License Number</label>
          <input v-model="form.license_number" />
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

const drivers = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref({
  organization_id: 1,
  name: '',
  phone: '',
  password: '',
  license_number: '',
  active: true,
})

async function load() {
  try {
    const res = await api.get('/drivers', { params: { active_only: false } })
    drivers.value = Array.isArray(res.data) ? res.data : (res.data?.data || res.data?.items || [])
  } catch (e) {
    console.error('Failed to load drivers:', e)
    drivers.value = []
  }
}

function openCreate() {
  editingId.value = null
  form.value = { organization_id: 1, name: '', phone: '', password: '', license_number: '', active: true }
  showModal.value = true
}

function openEdit(d) {
  editingId.value = d.id
  form.value = { ...d, password: '' }
  showModal.value = true
}

async function save() {
  const name = (form.value.name || '').trim()
  const phone = (form.value.phone || '').trim()
  if (!name || !phone) {
    alert('Name and phone are required')
    return
  }
  if (!editingId.value && !(form.value.password || '').trim()) {
    alert('Password is required for new drivers')
    return
  }
  try {
    if (editingId.value) {
      const payload = { name, license_number: (form.value.license_number || '').trim() || null, active: form.value.active }
      if (form.value.password?.trim()) payload.password = form.value.password.trim()
      await api.patch(`/drivers/${editingId.value}`, payload)
    } else {
      await api.post('/drivers', {
        organization_id: form.value.organization_id,
        name,
        phone,
        password: form.value.password.trim(),
        license_number: (form.value.license_number || '').trim() || null,
        active: form.value.active,
      })
    }
    showModal.value = false
    await load()
  } catch (e) {
    const err = e.response?.data
    const status = e.response?.status
    const url = e.config?.baseURL && e.config?.url ? `${e.config.baseURL.replace(/\/$/, '')}${e.config.url}` : ''
    let msg = 'Failed to save driver'
    if (!e.response) {
      msg = 'Network error - request did not reach server. Check: (1) Backend running, (2) API URL correct (see console), (3) CORS/proxy allows POST'
    } else if (err?.detail) {
      msg = typeof err.detail === 'string' ? err.detail : (Array.isArray(err.detail) ? err.detail.map(d => d.msg || d).join(', ') : String(err.detail))
    } else if (status) {
      msg = `Error ${status}: ${msg}`
    }
    if (url) msg += `\n\nURL: ${url}`
    msg += '\n\nOpen Console (F12) for details.'
    console.error('[DriversView] save failed', { status, url, error: e })
    alert(msg)
  }
}

async function confirmDelete(d) {
  if (!confirm(`Delete driver ${d.name}?`)) return
  try {
    await api.delete(`/drivers/${d.id}`)
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
.modal h3 { margin-bottom: 1rem; }
.modal label { display: block; margin-bottom: 0.25rem; font-size: 0.875rem; }
.modal input[type="text"], .modal input[type="number"], .modal input[type="password"] { width: 100%; padding: 0.5rem; margin-bottom: 0.75rem; }
.modal-actions { margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
