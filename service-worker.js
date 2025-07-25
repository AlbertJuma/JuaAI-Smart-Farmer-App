// Service Worker for JuaAI Smart Farmer App
const CACHE_NAME = 'juaai-farmer-v1.0.0';
const urlsToCache = [
  '/',
  '/index.html',
  '/styles/styles.css',
  '/scripts/app.js',
  '/scripts/weather.js',
  '/scripts/cropAI.js',
  '/scripts/storage.js',
  '/data/diseases.json',
  '/data/localTips.json',
  '/data/swahili-translation.json',
  '/images/sample-leaf.svg',
  '/icons/app-icon.svg',
  '/manifest.json'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker: Activation complete');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version or fetch from network
        if (response) {
          console.log('Service Worker: Serving from cache', event.request.url);
          return response;
        }

        // Clone the request because it's a stream
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then((response) => {
          // Check if response is valid
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response because it's a stream
          const responseToCache = response.clone();

          // Only cache GET requests for same origin
          if (event.request.method === 'GET' && event.request.url.startsWith(self.location.origin)) {
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
          }

          return response;
        }).catch(() => {
          // If fetch fails, try to serve offline page or return a custom offline response
          if (event.request.destination === 'document') {
            return caches.match('/index.html');
          }
          
          // For API requests, return a custom offline response
          if (event.request.url.includes('/api/')) {
            return new Response(
              JSON.stringify({
                message: 'You are offline. Please check your internet connection.',
                offline: true
              }),
              {
                headers: { 'Content-Type': 'application/json' }
              }
            );
          }

          // For other requests, return a generic offline response
          return new Response('Offline - Please check your internet connection', {
            status: 503,
            statusText: 'Service Unavailable'
          });
        });
      })
  );
});

// Background sync event (for future implementation)
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background sync triggered');
    event.waitUntil(
      // Sync offline data when connection is restored
      syncOfflineData()
    );
  }
});

// Push notification event (for future implementation)
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New farming tip available!',
    icon: '/icons/app-icon.svg',
    badge: '/icons/app-icon.svg',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: '1'
    },
    actions: [
      {
        action: 'explore',
        title: 'View Tips',
        icon: '/icons/app-icon.svg'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/app-icon.svg'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('JuaAI Smart Farmer', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked');
  event.notification.close();

  if (event.action === 'explore') {
    // Open the app and navigate to tips section
    event.waitUntil(
      clients.openWindow('/?tab=tips')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    event.notification.close();
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Helper function to sync offline data
async function syncOfflineData() {
  try {
    // Get offline analysis data and sync to server
    const cache = await caches.open(CACHE_NAME);
    // Implementation for syncing offline data would go here
    console.log('Service Worker: Offline data sync completed');
  } catch (error) {
    console.error('Service Worker: Offline data sync failed', error);
  }
}

// Message event for communication with main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(event.data.urls);
      })
    );
  }
});

// Error event
self.addEventListener('error', (event) => {
  console.error('Service Worker: Error occurred', event.error);
});

// Unhandled rejection event
self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker: Unhandled promise rejection', event.reason);
});

console.log('Service Worker: Script loaded');