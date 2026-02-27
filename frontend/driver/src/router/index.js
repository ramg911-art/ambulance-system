import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue'), meta: { guest: true } },
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/start', name: 'StartTrip', component: () => import('../views/StartTripView.vue'), meta: { requiresAuth: true } },
  { path: '/trip/:id', name: 'ActiveTrip', component: () => import('../views/ActiveTripView.vue'), meta: { requiresAuth: true } },
  { path: '/trips/today', name: 'TodayTrips', component: () => import('../views/TodayTripsView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.meta.guest && auth.isLoggedIn) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
