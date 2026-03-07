import api from './api'

export async function updateLocation(vehicleId, lat, lng, tripId = null) {
  const body = {
    vehicle_id: vehicleId,
    latitude: lat,
    longitude: lng,
    trip_id: tripId,
  }
  const url = `${api.defaults.baseURL.replace(/\/$/, '')}/gps/update`
  const headers = {
    'Content-Type': 'application/json',
    ...(api.defaults.headers.common || {}),
  }
  const token = localStorage.getItem('driver_token') || sessionStorage.getItem('driver_token')
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    credentials: 'omit',
  })
  if (!res.ok) {
    const err = new Error(res.statusText || 'Failed to update location')
    err.response = { status: res.status, data: await res.json().catch(() => ({})) }
    throw err
  }
  return res.json()
}
