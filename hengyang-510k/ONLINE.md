# 衡阳 510K 在线模式

在线模式使用一个轻量 Node.js WebSocket 房间服务，房间最多 4 人。房主负责发牌和推进牌局，其他玩家的叫牌、出牌、不要操作会发送给房主，再由房主广播统一牌局状态。

当前仓库同时提供两种前端：

- `hengyang-510k/index.html`：浏览器/H5 版本。
- `hengyang-510k-miniprogram/`：原生微信小程序版本，使用 WXML、WXSS 和 `wx.connectSocket`，推荐按该目录导入微信开发者工具。

## 本地联调

在仓库根目录执行：

```bash
node hengyang-510k/online-server.js
```

然后让所有玩家打开：

```text
http://127.0.0.1:4173/hengyang-510k/index.html
```

房主点击“在线组局”创建房间，把 6 位房间码发给另外 3 位玩家；其他玩家填写昵称和房间码后加入。4 个座位坐满后，房主会自动发牌。

## 原生微信小程序

打开微信开发者工具，导入 `hengyang-510k-miniprogram/`，将 `project.config.json` 中的 `touristappid` 换成你的小程序 AppID。详细导入和发布步骤见 `hengyang-510k-miniprogram/README.md`。

## 部署提示

把 `online-server.js` 放到可被公网访问的 Node.js 服务上，并开放 WebSocket。H5 页面填写对应的 `ws://` 或 `wss://` 地址；小程序正式版必须填写 `wss://` 地址，并在小程序后台配置 socket 合法域名。
