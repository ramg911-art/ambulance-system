<template>
  <div class="organizations">
    <h1>Organizations</h1>
    <button class="btn-primary" @click="openCreate">+ Add Organization</button>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Code</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in organizations" :key="o.id || o">
            <td>{{ o.id ?? '-' }}</td>
            <td>{{ o.name || '-' }}</td>
            <td>{{ o.code || '-' }}</td>
            <td>{{ o.active ? 'Yes' : 'No' }}</td>
            <td>
              <button class="btn-sm" @click="openEdit(o)">Edit</button>
              <button class="btn-sm btn-danger" @click="confirmDelete(o)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edit Organization' : 'Add Organization' }}</h3>
        <form @submit.prevent="save">
          <label>Name</label>
          <input v-model="form.name" type="text" required placeholder="e.g. City Ambulance Service" />
          <label>Code</label>
          <input v-model="form.code" type="text" required placeholder="e.g. CAS" :disabled="!!editingId" />
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

const organizations = ref([])
const showModal = ref(false)
const editingId = ref(null)
const form = ref({
  name: '',
  code: '',
  active: true,
})

async function load() {
  try {
    const res = await api.get('/organizations', { params: { active_only: false } })
    organizations.value = Array.isArray(res.data) ? res.data : (res.data?.data || res.data?.items || [])
  } catch (e) {
    console.error('Failed to load organizations:', e)
    organizations.value = []
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', code: '', active: true }
  showModal.value = true
}

function openEdit(o) {
  editingId.value = o.id
  form.value = { ...o }
  showModal.value = true
}

async function save() {
  const name = (form.value.name || '').trim()
  const code = (form.value.code || '').trim()
  if (!name) {
    alert('Name is required')
    return
  }
  if (!code) {
    alert('Code is required')
    return
  }
  try {
    if (editingId.value) {
      await api.patch(`/organizations/${editingId.value}`, {
        name,
        code: code.toUpperCase(),
        active: form.value.active,
      })
    } else {
      await api.post('/organizations', {
        name,
        code: code.toUpperCase(),
        active: form.value.active,
      })
    }
    showModal.value = false
    await load()
  } catch (e) {
    const err = e.response?.data
    let msg = 'Failed to save organization'
    if (err?.detail) {
      msg = typeof err.detail === 'string' ? err.detail : (Array.isArray(err.detail) ? err.detail.map(d => d.msg || d).join(', ') : String(err.detail))
    }
    alert(msg)
  }
}

async function confirmDelete(o) {
  if (!confirm(`Delete organization "${o.name}"? This may fail if it has vehicles, drivers, or other linked data.`)) return
  try {
    await api.delete(`/organizations/${o.id}`)
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
.modal input[type="text"] { width: 100%; padding: 0.5rem; margin-bottom: 0.75rem; }
.modal-actions { margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; }
</style>
