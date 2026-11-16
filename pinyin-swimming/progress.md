Original prompt: 优化 pinyin-swimming 的网络连接，改善弱网环境打开体验。

## 2026-11-16

- Baseline: `index.html` is about 14 MB, including the pool background, four swimmer illustrations, a Pinyin font, and 318 embedded voice clips.
- Extracted 318 MP3 clips into individual assets, replacing eager inline audio with per-clip URLs. The HTML is about 110 KB, down from 14 MB.
- Converted the pool background and 900 px transparent swimmer images to WebP; visual assets are about 0.5 MB, while the complete assets directory is about 5.2 MB.
- Added a same-origin Service Worker cache for the page, font, and assets, including an offline pool preview and swimmer placeholder. Added online/offline status and up to two retries for failed network audio.
- Kept the downloaded game self-contained by embedding all assets during export in small batches.

## Verification

- At 35 KB/s with 400 ms latency on a mobile viewport, the page reached DOM-ready in about 3.6 seconds. Only the Pinyin font was requested; no pool artwork or audio was downloaded on the setup screen.
- Confirmed an audio request retries after a transient failure and succeeds. When all three attempts fail, the game shows a retry message without leaving a stuck loading status.
- Played a round and confirmed the score updates. After using resources once, the page, pool image, swimmer image, and audio returned from cache offline; the page also reopened offline.
- Exported an approximately 6.5 MB standalone HTML with all 318 audio clips and no unresolved asset paths; opened it with `file://`, started a game, rendered swimmers, and played audio.
- The game screenshot was visually inspected. Inline script and Service Worker syntax checks and `git diff --check` passed.

## Follow-up

- The service worker improves repeat visits and access to previously loaded resources. It cannot fix DNS, TLS, or carrier/CDN routing failures that prevent reaching the host.
