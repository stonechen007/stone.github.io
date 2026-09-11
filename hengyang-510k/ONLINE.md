# 衡阳 510K 在线模式部署与使用

在线模式由一个无第三方依赖的 Node.js 服务提供静态页面和 WebSocket 房间服务。每桌最多 4 人，房间由房主创建；4 位玩家全部入座并点击“开始游戏”后，服务器才广播开局，房主负责发牌和同步牌局。

## 一、在线模式的实际流程

1. 房主打开 H5 页面，点击“在线组局”，填写昵称并创建房间。
2. 房间卡片会显示 6 位房间码和“分享链接”。房主点击“分享链接”，手机支持系统分享，其他浏览器会自动复制链接。
3. 其他 3 位玩家打开链接，链接会自动带上房间码；填写自己的昵称后点击“加入房间”。也可以手动输入房间码加入。
4. 4 个座位坐满后，所有玩家分别点击“开始游戏”。房间卡片显示“已准备 N/4”。
5. 4 人全部准备后，服务器向全桌广播开局；房主发牌，其他玩家收到自己的私有手牌和统一牌局状态。
6. 小程序中使用页面右上角分享能力，分享路径会自动携带 `room` 参数；朋友打开小程序后输入服务地址即可加入该房间。

## 二、本地联调

要求 Node.js 18 或更高版本。在仓库根目录执行：

```bash
node hengyang-510k/online-server.js
```

浏览器打开：

```text
http://127.0.0.1:4173/hengyang-510k/index.html
```

本地联调时，H5 默认服务地址为 `ws://127.0.0.1:4173`。多人测试可以打开 4 个浏览器窗口，或使用局域网 IP，例如：

```text
http://192.168.1.20:4173/hengyang-510k/index.html
```

手机访问局域网地址时，手机和电脑必须在同一个 Wi-Fi。局域网分享链接只能用于测试，不能作为正式线上邀请链接。

## 三、推荐的公网部署结构

正式环境建议使用一台 Linux 云服务器，并让同一个 HTTPS 域名同时承载 H5 页面和 WebSocket：

```text
玩家手机/浏览器/微信小程序
          │ HTTPS / WSS
          ▼
      Nginx + TLS 证书
          │ HTTP / WS
          ▼
  Node.js online-server.js :4173
```

例如使用域名 `game.example.com`：

- H5 页面：`https://game.example.com/hengyang-510k/index.html`
- H5 WebSocket：`wss://game.example.com`
- 微信小程序 WebSocket：`wss://game.example.com`

## 四、Linux 云服务器部署步骤

### 1. 准备域名和服务器

1. 购买一台有公网 IP 的 Linux 云服务器，推荐 Ubuntu 22.04/24.04。
2. 将 `game.example.com` 的 DNS A 记录指向服务器公网 IP。
3. 在云厂商安全组放行 `80` 和 `443` 端口；Node 的 `4173` 端口只允许本机访问，不需要对公网开放。

### 2. 安装运行环境并上传代码

```bash
sudo apt update
sudo apt install -y nginx nodejs npm
sudo mkdir -p /opt/hengyang-510k
sudo chown -R $USER:$USER /opt/hengyang-510k
```

将仓库中的以下文件上传到 `/opt/hengyang-510k/`：

- `hengyang-510k/index.html`
- `hengyang-510k/online-server.js`
- 其他 H5 页面依赖的静态文件（如果后续新增）

如果整个仓库已上传，也可以直接把服务工作目录配置为仓库根目录。

### 3. 先直接启动验证 Node 服务

```bash
cd /opt/hengyang-510k
node hengyang-510k/online-server.js
```

另开一个终端验证静态页面：

```bash
curl -I http://127.0.0.1:4173/hengyang-510k/index.html
```

看到 `200 OK` 后按 `Ctrl+C` 停止临时进程，继续配置 Nginx 和进程守护。

### 4. 配置 Nginx 反向代理和 WebSocket

创建 `/etc/nginx/sites-available/hengyang-510k`：

```nginx
server {
    listen 80;
    server_name game.example.com;

    location / {
        proxy_pass http://127.0.0.1:4173;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

启用配置并检查：

```bash
sudo ln -s /etc/nginx/sites-available/hengyang-510k /etc/nginx/sites-enabled/hengyang-510k
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 配置 HTTPS/WSS 证书

确认 DNS 已生效后安装证书工具：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d game.example.com
```

按提示完成邮箱和 HTTPS 配置。证书成功后，使用：

```text
https://game.example.com/hengyang-510k/index.html
```

H5 在线地址填写 `wss://game.example.com`。正式微信小程序只能使用 `wss://`，不能使用 `ws://`、`127.0.0.1` 或内网 IP。

### 6. 使用 systemd 常驻运行 Node 服务

创建 `/etc/systemd/system/hengyang-510k.service`：

```ini
[Unit]
Description=Hengyang 510K Online Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/hengyang-510k
ExecStart=/usr/bin/node /opt/hengyang-510k/hengyang-510k/online-server.js
Restart=always
RestartSec=3
Environment=PORT=4173

[Install]
WantedBy=multi-user.target
```

将 `User` 和路径替换为实际值，然后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hengyang-510k
sudo systemctl status hengyang-510k
sudo journalctl -u hengyang-510k -f
```

## 五、微信小程序发布配置

1. 在微信开发者工具导入 `hengyang-510k-miniprogram/`。
2. 将 `project.config.json` 中的 `touristappid` 替换为真实 AppID。
3. 在小程序后台进入“开发管理 → 开发设置 → 服务器域名”。
4. 在“socket 合法域名”中配置 `wss://game.example.com` 对应的域名。
5. 小程序页面中的 WebSocket 服务地址填写 `wss://game.example.com`。
6. 真机测试分享：创建房间后点击分享，朋友打开小程序会自动带上房间码；朋友输入昵称后点击加入，再由 4 人分别点击开始游戏。
7. 提交审核前关闭开发者工具中的“不校验合法域名、TLS 版本及 HTTPS 证书”选项，重新进行真机测试。

`pages/index/index.json` 已配置：

```json
{
  "pageOrientation": "landscape"
}
```

## 六、上线前检查清单

- H5 页面能通过 `https://` 打开，不能只通过 `file://` 分享。
- 浏览器开发者工具中 WebSocket 状态为 `101 Switching Protocols`。
- 4 人都能加入同一房间，未满 4 人不能开始。
- 4 人全部点击开始后才发牌，4 端手牌数量分别为 14、14、13、13。
- 其中一端叫牌、出牌、不要后，其他端状态一致。
- 手机横屏后手牌完整，H5 右侧牌局看板隐藏。
- 微信小程序后台已配置 socket 合法域名，证书链完整且未过期。
- 服务器重启后确认服务能自动恢复：`systemctl status hengyang-510k`。

## 七、当前服务的生产注意事项

当前 `online-server.js` 是适合 MVP 和小规模联调的单进程服务：房间和牌局状态保存在内存中，服务重启后房间会消失；牌局核心状态由房主客户端计算，服务端尚未独立执行完整牌型和结算校验。

正式运营前建议补充：Redis 房间状态、断线重连、登录鉴权、服务端洗牌/牌型/结算校验、操作超时、限流、日志和监控。扩容多台 Node 服务时，还需要 Redis 或其他共享状态及 WebSocket 粘性/网关方案。
