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
              <button class="btn-sm btn-expenses" @click="openExpenses(v)">Expenses</button>
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

    <!-- Expenses modal -->
    <div v-if="expensesModalVisible" class="modal-overlay" @click.self="closeExpensesModal">
      <div class="modal modal-expenses">
        <div class="expenses-header">
          <h3>Expenses – {{ selectedVehicle?.registration_number || '' }}</h3>
          <button type="button" class="btn-close" @click="closeExpensesModal">×</button>
        </div>
        <div class="expenses-add">
          <h4>Add Expense</h4>
          <form @submit.prevent="addExpense" class="expense-form">
            <div class="form-row">
              <label>Type</label>
              <select v-model="expenseForm.expense_type" required>
                <option value="fuel">Fuel</option>
                <option value="service_maintenance">Service and Maintenance</option>
                <option value="accident_repair">Accident Repair</option>
              </select>
            </div>
            <div class="form-row">
              <label>Bill Number <span class="req">*</span></label>
              <input v-model="expenseForm.bill_number" required placeholder="Bill/invoice number" />
            </div>
            <div class="form-row">
              <label>Description <span class="req">*</span></label>
              <input v-model="expenseForm.description" :required="expenseForm.expense_type !== ''" placeholder="Brief description" />
            </div>
            <div class="form-row">
              <label>Amount (₹) <span class="req">*</span></label>
              <input v-model.number="expenseForm.amount" type="number" step="0.01" min="0" required />
            </div>
            <template v-if="expenseForm.expense_type === 'fuel'">
              <div class="form-row">
                <label>Odometer Reading (km) <span class="req">*</span></label>
                <input v-model.number="expenseForm.odometer_reading" type="number" step="0.1" required />
              </div>
              <div class="form-row">
                <label>Qty Refueled (L) <span class="req">*</span></label>
                <input v-model.number="expenseForm.qty_refueled" type="number" step="0.01" min="0" required />
              </div>
            </template>
            <div class="modal-actions">
              <button type="button" @click="resetExpenseForm">Clear</button>
              <button type="submit" :disabled="addingExpense">Add</button>
            </div>
          </form>
        </div>
        <div class="expenses-list">
          <h4>Recent Expenses</h4>
          <p v-if="expenses.length === 0" class="empty">No expenses yet.</p>
          <table v-else class="exp-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Bill #</th>
                <th>Description</th>
                <th>Odometer</th>
                <th>Qty (L)</th>
                <th>Amount</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in expenses" :key="e.id">
                <td>{{ formatDate(e.created_at) }}</td>
                <td><span :class="['badge', e.expense_type]">{{ expenseTypeLabel(e.expense_type) }}</span></td>
                <td>{{ e.bill_number }}</td>
                <td>{{ e.description || '—' }}</td>
                <td>{{ e.odometer_reading != null ? e.odometer_reading : '—' }}</td>
                <td>{{ e.qty_refueled != null ? e.qty_refueled.toFixed(2) : '—' }}</td>
                <td>₹{{ (e.amount || 0).toFixed(2) }}</td>
                <td><button type="button" class="btn-sm btn-danger" @click="deleteExpense(e)">Delete</button></td>
              </tr>
            </tbody>
          </table>
        </div>
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

const expensesModalVisible = ref(false)
const selectedVehicle = ref(null)
const expenses = ref([])
const addingExpense = ref(false)
const expenseForm = ref({
  expense_type: 'fuel',
  bill_number: '',
  description: '',
  amount: '',
  odometer_reading: '',
  qty_refueled: '',
})

function expenseTypeLabel(t) {
  const map = { fuel: 'Fuel', service_maintenance: 'Service', accident_repair: 'Accident' }
  return map[t] || t
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN')
}

function resetExpenseForm() {
  expenseForm.value = {
    expense_type: 'fuel',
    bill_number: '',
    description: '',
    amount: '',
    odometer_reading: '',
    qty_refueled: '',
  }
}

async function openExpenses(v) {
  selectedVehicle.value = v
  expensesModalVisible.value = true
  resetExpenseForm()
  await loadExpenses()
}

function closeExpensesModal() {
  expensesModalVisible.value = false
  selectedVehicle.value = null
}

async function loadExpenses() {
  if (!selectedVehicle.value?.id) return
  try {
    const { data } = await api.get('/vehicle-expenses', { params: { vehicle_id: selectedVehicle.value.id } })
    expenses.value = data || []
  } catch {
    expenses.value = []
  }
}

async function addExpense() {
  if (!selectedVehicle.value?.id) return
  const f = expenseForm.value
  const payload = {
    vehicle_id: selectedVehicle.value.id,
    expense_type: f.expense_type,
    bill_number: (f.bill_number || '').trim(),
    description: (f.description || '').trim() || null,
    amount: Number(f.amount) || 0,
  }
  if (f.expense_type === 'fuel') {
    payload.odometer_reading = Number(f.odometer_reading)
    payload.qty_refueled = Number(f.qty_refueled) || 0
  }
  addingExpense.value = true
  try {
    await api.post('/vehicle-expenses', payload)
    resetExpenseForm()
    await loadExpenses()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to add expense')
  } finally {
    addingExpense.value = false
  }
}

async function deleteExpense(e) {
  if (!confirm('Delete this expense?')) return
  try {
    await api.delete(`/vehicle-expenses/${e.id}`)
    loadExpenses()
  } catch {
    alert('Failed to delete')
  }
}

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
.btn-expenses { background: #059669; color: white; border: none; border-radius: 0.25rem; }
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
.modal input[type="text"], .modal input[type="number"], .modal select { width: 100%; padding: 0.5rem; margin-bottom: 0.75rem; box-sizing: border-box; }
.modal-actions { margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end; }

.modal-expenses { max-width: 720px; max-height: 90vh; overflow-y: auto; }
.expenses-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.btn-close { font-size: 1.5rem; background: none; border: none; cursor: pointer; color: #64748b; padding: 0; line-height: 1; }
.expenses-add { margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px solid #e2e8f0; }
.expenses-add h4, .expenses-list h4 { font-size: 0.95rem; margin-bottom: 0.75rem; color: #334155; }
.form-row { margin-bottom: 0.75rem; }
.form-row label { display: block; margin-bottom: 0.25rem; }
.req { color: #dc2626; }
.expenses-list .empty { color: #94a3b8; font-size: 0.9rem; }
.exp-table { font-size: 0.85rem; }
.badge { padding: 0.2rem 0.4rem; border-radius: 0.25rem; font-size: 0.75rem; }
.badge.fuel { background: #dbeafe; color: #1d4ed8; }
.badge.service_maintenance { background: #fef3c7; color: #92400e; }
.badge.accident_repair { background: #fee2e2; color: #b91c1c; }
</style>
