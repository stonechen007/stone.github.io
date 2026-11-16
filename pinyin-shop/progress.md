Original prompt: 优化一下网络连接，弱网环境打开等问题

## 2026-11-16

- Baseline: `index.html` was 12.46 MB because it embedded 80 product images, a full Chinese font, and the storefront background.
- Externalized the 80 product images and interface assets. The HTML is about 141 KB; the storefront background is 1440 x 810 at about 399 KB, with a small inline preview for slow loads.
- Subset the Pinyin teaching font to about 14 KB and use device fonts for Chinese UI text.
- Added direct lazy-loading markup so product images are requested only when a catalog is opened or an item is selected. The initial page requests only the background, basket, and teaching font.
- Added a service worker that caches the page and critical assets, caches product images as they are used, and provides an image placeholder when an uncached image is requested offline.
- Kept “下载带设置的游戏” self-contained by inlining external assets during export.
- Verified desktop rendering, product selection/purchase/checkout, offline navigation and selection, self-contained export, and weak-network loading at 35 KB/s. No browser console errors or failed HTTP responses.

## Follow-up

- The service worker can help after one successful online visit. If some phones still cannot reach the production domain at all, check DNS, TLS, and CDN/carrier routing separately; page-level changes cannot repair those connection failures.
