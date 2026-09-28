// Service Worker for MotionStoryLab PWA
const CACHE_NAME = 'msl-pwa-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Pass through fetch requests for fresh data
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
