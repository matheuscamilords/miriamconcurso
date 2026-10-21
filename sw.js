const CACHE='miriam-estudos-v2026-10-reconstrucao-47';
const FILES=['./','./index.html','./src/app.js','./src/styles.css','./src/data/course.js','./manifest.webmanifest','./public/fontes/edital-02-2026.pdf','./public/fontes/anexo-i.pdf','./public/fontes/retificacao-01.pdf','./public/fontes/anexo-iii.pdf','./public/fontes/anexo-iv-retificado.pdf','./public/fontes/edital-verticalizado.pdf','./public/fontes/codigo-tributario-municipal-lei-4012-2006.pdf','./public/fontes/estatuto-servidores-lei-5038-2014.pdf','./public/fontes/lei-organica-sao-joao-del-rei.pdf'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
// Network-first for versioned lesson/code assets: publication updates are visible.
// For offline use fall back to previously cached material after the first visit.
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;
 const url=new URL(e.request.url);if(url.origin!==self.location.origin)return;
 e.respondWith(fetch(e.request).then(resp=>{if(resp.ok){const clone=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,clone))}return resp}).catch(()=>caches.match(e.request)));});
