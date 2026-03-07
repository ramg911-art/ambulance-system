<template>
  <div class="billing">
    <h1>Billing</h1>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Trip ID</th>
            <th>Amount</th>
            <th>Invoice #</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in invoices" :key="i.id">
            <td>{{ i.id }}</td>
            <td>{{ i.trip_id }}</td>
            <td>₹{{ (i.amount || 0).toFixed(2) }}</td>
            <td>{{ i.invoice_number }}</td>
            <td><span :class="['badge', i.status]">{{ i.status }}</span></td>
            <td>{{ formatDate(i.created_at) }}</td>
            <td>
              <button class="btn-pdf" @click="generatePdf(i.id)" :disabled="generatingId === i.id">
                {{ generatingId === i.id ? 'Generating...' : 'PDF' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { generateInvoicePdf } from '../utils/invoicePdf'

const invoices = ref([])
const generatingId = ref(null)

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('en-IN')
}

async function generatePdf(invoiceId) {
  generatingId.value = invoiceId
  try {
    const { data } = await api.get(`/billing/invoices/${invoiceId}/details`)
    generateInvoicePdf(data)
  } catch (e) {
    console.error('Failed to generate PDF:', e)
  } finally {
    generatingId.value = null
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/billing/invoices')
    invoices.value = data || []
  } catch {
    invoices.value = []
  }
})
</script>

<style scoped>
h1 { margin-bottom: 1rem; color: #1e293b; }
.table-wrap {
  background: white;
  border-radius: 0.5rem;
  overflow-x: auto;
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
  text-transform: capitalize;
}
.badge.paid { background: #dcfce7; color: #166534; }
.badge.pending { background: #fef3c7; color: #92400e; }
.btn-pdf {
  padding: 0.4rem 0.75rem;
  background: #1e3a8a;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8rem;
  cursor: pointer;
  font-weight: 500;
}
.btn-pdf:hover:not(:disabled) { background: #1e40af; }
.btn-pdf:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
