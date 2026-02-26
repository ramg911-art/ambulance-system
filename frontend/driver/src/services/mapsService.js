import { setOptions, importLibrary } from '@googlemaps/js-api-loader'
import { GOOGLE_MAPS_API_KEY } from '../config/maps'

let loadPromise = null

/**
 * Load Google Maps API once. Returns when google.maps is ready.
 * @returns {Promise<void>}
 */
export async function loadMap() {
  if (!GOOGLE_MAPS_API_KEY) {
    throw new Error('Google Maps API key is missing. Set VITE_GOOGLE_MAPS_API_KEY in .env')
  }
  if (loadPromise) return loadPromise
  setOptions({ key: GOOGLE_MAPS_API_KEY })
  loadPromise = importLibrary('maps')
  await loadPromise
  return loadPromise
}

/**
 * Create a marker on the map.
 * @param {google.maps.Map} map
 * @param {{lat: number, lng: number}} position
 * @param {{title?: string, draggable?: boolean}} options
 * @returns {google.maps.Marker}
 */
export function createMarker(map, position, options = {}) {
  if (!map || !window.google?.maps) return null
  const marker = new window.google.maps.Marker({
    map,
    position: { lat: position.lat, lng: position.lng },
    title: options.title || '',
    draggable: options.draggable ?? false,
  })
  return marker
}

/**
 * Update an existing marker position.
 * @param {google.maps.Marker} marker
 * @param {{lat: number, lng: number}} position
 */
export function updateMarker(marker, position) {
  if (marker && position) {
    marker.setPosition({ lat: position.lat, lng: position.lng })
  }
}

/**
 * Center the map on a position with optional zoom.
 * @param {google.maps.Map} map
 * @param {{lat: number, lng: number}} position
 * @param {number} [zoom]
 */
export function centerMap(map, position, zoom) {
  if (!map || !position) return
  map.panTo({ lat: position.lat, lng: position.lng })
  if (zoom != null) map.setZoom(zoom)
}
