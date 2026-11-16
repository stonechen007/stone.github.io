const CACHE_NAME = "pinyin-shop-v1";
const PAGE_URL = new URL("./", self.registration.scope).href;
const IMAGE_PLACEHOLDER =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="12" fill="#edf8f2"/><path d="M34 40h52v48H34zM44 40v-8h32v8M45 55h30M45 67h30M45 79h20" fill="none" stroke="#83bda9" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      const urls = [
        PAGE_URL,
        new URL("assets/shop-background.jpg", PAGE_URL).href,
        new URL("assets/basket.webp", PAGE_URL).href,
        new URL("assets/pinyin-font.woff", PAGE_URL).href,
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
          .filter((key) => key.startsWith("pinyin-shop-") && key !== CACHE_NAME)
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
