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
    icon: options.icon ?? undefined,
    label: options.label ?? undefined,
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

/**
 * Fit map bounds to include all positions, with padding.
 * @param {google.maps.Map} map
 * @param {Array<{lat: number, lng: number}>} positions
 * @param {number} [padding] Padding in pixels
 */
export function fitMapToBounds(map, positions, padding = 50) {
  if (!map || !positions?.length) return
  const valid = positions.filter((p) => p?.lat != null && p?.lng != null)
  if (valid.length === 0) return
  if (valid.length === 1) {
    map.setCenter({ lat: valid[0].lat, lng: valid[0].lng })
    map.setZoom(14)
  } else {
    const bounds = new window.google.maps.LatLngBounds()
    valid.forEach((p) => bounds.extend({ lat: p.lat, lng: p.lng }))
    map.fitBounds(bounds, padding)
  }
}

const geocodeCache = new Map()
const CACHE_KEY_PRECISION = 4
const CACHE_TTL_MS = 5 * 60 * 1000

function cacheKey(lat, lng) {
  const r = 10 ** CACHE_KEY_PRECISION
  return `${Math.round(lat * r) / r},${Math.round(lng * r) / r}`
}

/**
 * Reverse geocode lat/lng to address using Google Maps Geocoding API.
 * @param {number} lat
 * @param {number} lng
 * @returns {Promise<string|null>} Formatted address or null
 */
export async function reverseGeocode(lat, lng) {
  if (lat == null || lng == null) return null
  const key = cacheKey(lat, lng)
  const cached = geocodeCache.get(key)
  if (cached && Date.now() - cached.ts < CACHE_TTL_MS) return cached.address

  try {
    await loadMap()
    let Geocoder = window.google?.maps?.Geocoder
    if (!Geocoder && window.google?.maps?.importLibrary) {
      const lib = await window.google.maps.importLibrary('geocoding')
      Geocoder = lib?.Geocoder
    }
    if (!Geocoder) return null
    return new Promise((resolve) => {
      const geocoder = new Geocoder()
      geocoder.geocode({ location: { lat, lng } }, (results, status) => {
        if (status === 'OK' && results?.[0]) {
          const address = results[0].formatted_address
          geocodeCache.set(key, { address, ts: Date.now() })
          resolve(address)
        } else {
          resolve(null)
        }
      })
    })
  } catch {
    return null
  }
}
