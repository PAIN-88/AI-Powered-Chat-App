const CACHE_NAME = 'pain-chat-v1';
const urlsToCache = [
    '/',
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener('push', function(event) {
    let data = {};
    try {
        data = event.data.json();
    } catch (e) {
        data = { title: 'PAIN Chat', body: event.data ? event.data.text() : 'New notification' };
    }

    const title = data.title || 'PAIN Chat';
    const options = {
        body: data.body || '',
        icon: '/static/images/icon-192.png',
        data: { link: data.link || '/' },
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const link = event.notification.data && event.notification.data.link ? event.notification.data.link : '/';
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(clientList) {
            for (const client of clientList) {
                if (client.url.indexOf(link) !== -1 && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(link);
            }
        })
    );
});