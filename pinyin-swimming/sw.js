const CACHE_NAME = "pinyin-swimming-v1";
const PAGE_URL = new URL("./", self.registration.scope).href;
const IMAGE_PLACEHOLDER =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 80"><rect width="120" height="80" fill="#dff6ff"/><path d="M8 50q14-12 28 0t28 0t28 0t28 0M8 65q14-12 28 0t28 0t28 0t28 0" fill="none" stroke="#54b9d6" stroke-width="6" stroke-linecap="round"/></svg>';

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      const urls = [
        PAGE_URL,
        new URL("assets/class-pinyin.ttf", PAGE_URL).href,
      ];
      await Promise.all(
        urls.map(async (url) => {
          try {
            const response = await fetch(url);
            if (response.ok) await cache.put(url, response);
          } catch {}
        }),
      );
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter(
            (key) => key.startsWith("pinyin-swimming-") && key !== CACHE_NAME,
          )
          .map((key) => caches.delete(key)),
      );
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  const inScope = url.href.startsWith(PAGE_URL);
  const isPage = request.mode === "navigate" && inScope;
  const isAsset = inScope && url.pathname.includes("/assets/");
  if (!isPage && !isAsset) return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      const cached =
        (await cache.match(request, { ignoreSearch: true })) ||
        (isPage ? await cache.match(PAGE_URL) : null);
      const refresh = fetch(request)
        .then((response) => {
          if (!response.ok) return response;
          return cache.put(request, response.clone()).then(() => response);
        })
        .catch(() => cached);

      if (cached) {
        event.waitUntil(refresh.then(() => undefined));
        return cached;
      }

      const response = await refresh;
      if (response) return response;
      if (request.destination === "image") {
        if (url.pathname.endsWith("/swim-background.webp"))
          return new Response("", { status: 503 });
        return new Response(IMAGE_PLACEHOLDER, {
          status: 200,
          headers: { "Content-Type": "image/svg+xml; charset=utf-8" },
        });
      }
      return new Response("资源暂不可用，请联网后重试。", {
        status: 503,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      });
    })(),
  );
});
