const CACHE='guangzhou-fob-cache-v16';
const ASSETS=['./','./index.html','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const key of await caches.keys()){if(key.startsWith('guangzhou-fob-cache-')&&key!==CACHE)await caches.delete(key)}await self.clients.claim()})()));
self.addEventListener('fetch',event=>{const req=event.request;if(req.method!=='GET')return;const url=new URL(req.url);if(url.origin!==self.location.origin)return;
 if(req.mode==='navigate'){event.respondWith(fetch(req).catch(async()=>await caches.match('./index.html')||Response.error()));return;}
 event.respondWith(caches.match(req).then(cached=>cached||fetch(req)));
});
