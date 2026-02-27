import api from './api'

export async function createTrip(payload) {
  const { data } = await api.post('/trips', payload)
  return data
}

export async function startTrip(tripId) {
  const { data } = await api.post(`/trips/${tripId}/start`)
  return data
}

export async function endTrip(tripId) {
  const { data } = await api.post(`/trips/${tripId}/end`)
  return data
}

export async function getTrip(tripId) {
  const { data } = await api.get(`/trips/${tripId}`)
  return data
}

export async function getDriverTripsToday() {
  const { data } = await api.get('/trips/driver/today')
  return data
}
