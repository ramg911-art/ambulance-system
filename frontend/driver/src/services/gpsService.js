import api from './api'

export async function updateLocation(vehicleId, lat, lng, tripId = null) {
  const { data } = await api.post('/gps/update', {
    vehicle_id: vehicleId,
    latitude: lat,
    longitude: lng,
    trip_id: tripId,
  })
  return data
}
