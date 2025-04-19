self.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open('locallearn-cache').then((cache) => {
        return cache.addAll([
          '/',
          '/static/css/style.css',
          '/static/js/main.js',
          // Add other assets you want to cache
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', (event) => {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return cachedResponse || fetch(event.request);
      })
    );
  });
  