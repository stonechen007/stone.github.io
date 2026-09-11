# 衡阳 510K · 原生微信小程序

这是原生 WXML/WXSS/JS 版本，在线协议与网页版本共用 `hengyang-510k/online-server.js`。

## 导入开发者工具

1. 打开微信开发者工具，导入本目录 `hengyang-510k-miniprogram/`。
2. 将 `project.config.json` 中的 `touristappid` 替换成你的小程序 AppID；没有 AppID 时可先使用测试号或开发者工具的本地预览能力。
3. 在首页填写 WebSocket 地址：开发工具本地联调可填 `ws://127.0.0.1:4173`，正式环境必须填公网 `wss://你的域名/ws`。
4. 创建房间，把 6 位房间码发给另外 3 位玩家。

## 本地联调

在仓库根目录启动服务：

```bash
node hengyang-510k/online-server.js
```

开发者工具中，开发阶段可以临时勾选“不校验合法域名、TLS 版本及 HTTPS 证书”。真机和正式版不能依赖这个选项，必须使用有效公网域名和 WSS。

## 正式部署

- 给 Node 服务配置公网域名、HTTPS/WSS 证书，并让反向代理透传 WebSocket Upgrade。
- 在小程序后台“开发管理 → 开发设置 → 服务器域名”配置 socket 合法域名；如果增加 HTTP API 或微信登录，再配置 request 合法域名。
- 当前服务器的房间状态在内存中，适合 MVP 联调。正式运营建议将房间、断线重连和战绩放进 Redis/数据库，并把洗牌、牌型校验和结算移到服务端。

## 目录

- `pages/index/index.wxml`：原生牌桌、房间和结算界面
- `pages/index/index.wxss`：牌桌样式
- `pages/index/index.js`：房间连接、牌局状态和操作同步
- `utils/rules.js`：牌型、炸弹、三带二和分数规则
