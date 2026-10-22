const CACHE='guangzhou-fob-cache-v27';
const CORE=['./index.html','./manifest.webmanifest','./icon.svg','./'];
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const cache=await caches.open(CACHE);
 await cache.addAll(CORE);
 await self.skipWaiting();
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{
 const keys=await caches.keys();
 await Promise.all(keys.filter(x=>x.startsWith('guangzhou-fob-cache-')&&x!==CACHE).map(x=>caches.delete(x)));
 await self.clients.claim();
})()));
self.addEventListener('fetch',event=>{
 const req=event.request;
 if(req.method!=='GET')return;
 const url=new URL(req.url);
 if(url.origin!==self.location.origin)return;
 if(req.mode==='navigate'){
  event.respondWith((async()=>{
   const cache=await caches.open(CACHE);
   try{const response=await fetch(req);
    if(response.ok)await cache.put('./index.html',response.clone());
    return response;
   }catch(e){return await cache.match('./index.html') || await cache.match('./') || Response.error()}
  })());
  return;
 }
 event.respondWith((async()=>{
  const cached=await caches.match(req);
  if(cached)return cached;
  return fetch(req);
 })());
});
