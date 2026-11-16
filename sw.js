// P2P Chat service worker. It only shows notifications: Chrome on Android doesn't let
// a page show them by itself. It has no fetch handler, so it never caches anything
// and doesn't get in the way of the app's own update check.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(self.clients.claim()));

// Tapping a notification brings the app to the front and opens the chat (or the call).
self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  e.waitUntil((async () => {
    const wins = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    const win = wins.find((w) => w.focused) || wins[0];
    if (!win) return self.clients.openWindow(self.registration.scope);
    await win.focus();
    win.postMessage({ t: "notificationclick", data: e.notification.data });
  })());
});
