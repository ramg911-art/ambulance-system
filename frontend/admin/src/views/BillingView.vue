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
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in invoices" :key="i.id">
            <td>{{ i.id }}</td>
            <td>{{ i.trip_id }}</td>
            <td>₹{{ i.amount }}</td>
            <td>{{ i.invoice_number }}</td>
            <td>{{ i.status }}</td>
            <td>{{ new Date(i.created_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const invoices = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/billing/invoices')
    invoices.value = data
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
