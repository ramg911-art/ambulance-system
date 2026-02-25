<template>
  <div class="fallback-tariff">
    <h1>Fallback Tariff</h1>
    <p class="desc">Used when no fixed tariff applies (distance-based billing: ₹ per km)</p>
    <div class="card">
      <form @submit.prevent="save">
        <label>Rate per km (₹)</label>
        <input v-model.number="rate" type="number" step="0.01" min="0" required />
        <button type="submit" class="btn-primary">Save</button>
      </form>
      <p v-if="saved" class="success">Saved successfully.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const rate = ref(50)
const saved = ref(false)

async function load() {
  try {
    const { data } = await api.get('/tariffs/fallback')
    rate.value = data.rate_per_km
  } catch {
    rate.value = 50
  }
}

async function save() {
  try {
    await api.put('/tariffs/fallback', { rate_per_km: rate.value })
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to save')
  }
}

onMounted(load)
</script>

<style scoped>
h1 { margin-bottom: 0.5rem; color: #1e293b; }
.desc { color: #64748b; margin-bottom: 1rem; font-size: 0.9rem; }
.card { background: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); max-width: 400px; }
label { display: block; margin-bottom: 0.25rem; font-size: 0.875rem; }
input { width: 100%; padding: 0.5rem; margin-bottom: 1rem; font-size: 1rem; }
.btn-primary { padding: 0.5rem 1rem; background: #2563eb; color: white; border: none; border-radius: 0.375rem; cursor: pointer; }
.success { color: #16a34a; margin-top: 0.5rem; }
</style>
