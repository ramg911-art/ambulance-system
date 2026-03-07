import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'
import { clientsClaim } from 'workbox-core'
import { BackgroundSyncPlugin } from 'workbox-background-sync'
import { registerRoute } from 'workbox-routing'
import { NetworkOnly, StaleWhileRevalidate } from 'workbox-strategies'

self.skipWaiting()
clientsClaim()
cleanupOutdatedCaches()
precacheAndRoute(self.__WB_MANIFEST)

const bgSyncPlugin = new BackgroundSyncPlugin('gps-updates', {
  maxRetentionTime: 24 * 60,
})

registerRoute(
  ({ request, url }) => request.method === 'POST' && url.pathname.endsWith('/gps/update'),
  new NetworkOnly({ plugins: [bgSyncPlugin] }),
  'POST'
)

registerRoute(
  ({ url }) => url.pathname === '/config.json',
  new StaleWhileRevalidate({ cacheName: 'config-cache' })
)
