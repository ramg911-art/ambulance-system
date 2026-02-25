import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/live', name: 'LiveTracking', component: () => import('../views/LiveTrackingView.vue') },
  { path: '/trips', name: 'Trips', component: () => import('../views/TripsView.vue') },
  { path: '/preset-locations', name: 'PresetLocations', component: () => import('../views/PresetLocationsView.vue') },
  { path: '/preset-destinations', name: 'PresetDestinations', component: () => import('../views/PresetDestinationsView.vue') },
  { path: '/tariffs', name: 'Tariffs', component: () => import('../views/TariffsView.vue') },
  { path: '/billing', name: 'Billing', component: () => import('../views/BillingView.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
