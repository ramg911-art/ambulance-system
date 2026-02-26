import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue'), meta: { guest: true } },
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/live', name: 'LiveTracking', component: () => import('../views/LiveTrackingView.vue'), meta: { requiresAuth: true } },
  { path: '/trips', name: 'Trips', component: () => import('../views/TripsView.vue'), meta: { requiresAuth: true } },
  { path: '/organizations', name: 'Organizations', component: () => import('../views/OrganizationsView.vue'), meta: { requiresAuth: true } },
  { path: '/vehicles', name: 'Vehicles', component: () => import('../views/VehiclesView.vue'), meta: { requiresAuth: true } },
  { path: '/drivers', name: 'Drivers', component: () => import('../views/DriversView.vue'), meta: { requiresAuth: true } },
  { path: '/preset-locations', name: 'PresetLocations', component: () => import('../views/PresetLocationsView.vue'), meta: { requiresAuth: true } },
  { path: '/preset-destinations', name: 'PresetDestinations', component: () => import('../views/PresetDestinationsView.vue'), meta: { requiresAuth: true } },
  { path: '/tariffs', name: 'Tariffs', component: () => import('../views/TariffsView.vue'), meta: { requiresAuth: true } },
  { path: '/fallback-tariff', name: 'FallbackTariff', component: () => import('../views/FallbackTariffView.vue'), meta: { requiresAuth: true } },
  { path: '/billing', name: 'Billing', component: () => import('../views/BillingView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  const isLoggedIn = !!token
  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.meta.guest && isLoggedIn) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
