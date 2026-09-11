'use strict';

// Minimal dependency-free WebSocket room server for Hengyang 510K.
// It serves the static page and relays the authoritative host state to a
// maximum of four players per room.
const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const path = require('path');

const PORT = Number(process.env.PORT) || 4173;
const ROOT = path.resolve(__dirname, '..');
const rooms = new Map();
const clients = new Set();
const WS_GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';
const ROOM_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const MIME_TYPES = {
    '.css': 'text/css; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon'
};

function sendFrame(socket, payload, opcode = 0x1) {
    if (!socket || socket.destroyed) return;
    const body = Buffer.isBuffer(payload) ? payload : Buffer.from(payload);
    let header;
    if (body.length < 126) {
        header = Buffer.from([0x80 | opcode, body.length]);
    } else if (body.length < 65536) {
        header = Buffer.alloc(4);
        header[0] = 0x80 | opcode;
        header[1] = 126;
        header.writeUInt16BE(body.length, 2);
    } else {
        header = Buffer.alloc(10);
        header[0] = 0x80 | opcode;
        header[1] = 127;
        header.writeBigUInt64BE(BigInt(body.length), 2);
    }
    socket.write(Buffer.concat([header, body]));
}

function sendJson(client, payload) {
    sendFrame(client.socket, JSON.stringify(payload));
}

function parseFrames(client) {
    while (client.buffer.length >= 2) {
        const first = client.buffer[0];
        const second = client.buffer[1];
        const opcode = first & 0x0f;
        const masked = Boolean(second & 0x80);
        let length = second & 0x7f;
        let offset = 2;
        if (length === 126) {
            if (client.buffer.length < 4) return;
            length = client.buffer.readUInt16BE(2);
            offset = 4;
        } else if (length === 127) {
            if (client.buffer.length < 10) return;
            const largeLength = client.buffer.readBigUInt64BE(2);
            if (largeLength > BigInt(Number.MAX_SAFE_INTEGER)) { client.socket.destroy(); return; }
            length = Number(largeLength);
            offset = 10;
        }
        const frameLength = offset + (masked ? 4 : 0) + length;
        if (client.buffer.length < frameLength) return;
        if (masked && client.buffer.length < offset + 4) return;
        const mask = masked ? client.buffer.subarray(offset, offset + 4) : null;
        const payloadStart = offset + (masked ? 4 : 0);
        const payload = Buffer.from(client.buffer.subarray(payloadStart, payloadStart + length));
        client.buffer = client.buffer.subarray(frameLength);
        if (mask) for (let i = 0; i < payload.length; i++) payload[i] ^= mask[i % 4];

        if (opcode === 0x1) {
            try { handleMessage(client, JSON.parse(payload.toString('utf8'))); } catch (error) { sendJson(client, { type: 'error', message: '无法解析客户端消息。' }); }
        } else if (opcode === 0x8) {
            client.socket.end();
            return;
        } else if (opcode === 0x9) {
            sendFrame(client.socket, payload, 0xA);
        }
    }
}

function makeRoomCode() {
    let code = '';
    do {
        code = Array.from({ length: 6 }, () => ROOM_ALPHABET[crypto.randomInt(ROOM_ALPHABET.length)]).join('');
    } while (rooms.has(code));
    return code;
}

function safeName(name) {
    const normalized = String(name || '').replace(/[\u0000-\u001f<>]/g, '').trim();
    return (normalized || '玩家').slice(0, 12);
}

function roomView(room) {
    return {
        code: room.code,
        hostId: room.hostId,
        started: room.started,
        ready: Array.from({ length: 4 }, (_, id) => room.ready.has(id)),
        players: room.players.map(player => ({ id: player.id, name: player.name, connected: true }))
    };
}

function broadcastRoom(room) {
    for (const player of room.players) {
        const client = room.clients.get(player.id);
        if (client) sendJson(client, { type: 'room', room: roomView(room), selfId: player.id, hostId: room.hostId });
    }
}

function privateSnapshot(snapshot, playerId) {
    if (!snapshot) return null;
    const safeSnapshot = JSON.parse(JSON.stringify(snapshot));
    safeSnapshot.players = safeSnapshot.players.map((player, id) => {
        if (id === playerId) return player;
        return { ...player, hand: Array.from({ length: player.hand.length }, () => ({ hidden: true })) };
    });
    return safeSnapshot;
}

function removeFromRoom(client) {
    if (!client.roomCode) return;
    const room = rooms.get(client.roomCode);
    client.roomCode = null;
    const playerId = client.playerId;
    client.playerId = null;
    if (!room) return;
    room.clients.delete(playerId);
    if (playerId === room.hostId) {
        for (const other of room.clients.values()) {
            sendJson(other, { type: 'error', message: '房主已离开，本桌结束。' });
            other.roomCode = null;
            other.playerId = null;
        }
        room.clients.clear();
        rooms.delete(room.code);
        return;
    }
    room.ready.delete(playerId);
    room.players = room.players.filter(player => player.id !== playerId);
    if (!room.players.length) rooms.delete(room.code);
    else broadcastRoom(room);
}

function joinRoom(client, room, name, playerId) {
    const player = { id: playerId, name: safeName(name) };
    room.players.push(player);
    room.players.sort((left, right) => left.id - right.id);
    room.clients.set(player.id, client);
    client.roomCode = room.code;
    client.playerId = player.id;
    sendJson(client, { type: 'room', room: roomView(room), selfId: player.id, hostId: room.hostId });
    broadcastRoom(room);
    if (room.snapshot) sendJson(client, { type: 'state', roomCode: room.code, snapshot: privateSnapshot(room.snapshot, player.id) });
}

function createRoom(client, message) {
    removeFromRoom(client);
    const room = { code: makeRoomCode(), hostId: 0, players: [], clients: new Map(), ready: new Set(), started: false, snapshot: null };
    rooms.set(room.code, room);
    joinRoom(client, room, message.name, 0);
}

function joinExistingRoom(client, message) {
    removeFromRoom(client);
    const code = String(message.roomCode || '').trim().toUpperCase();
    const room = rooms.get(code);
    if (!room) { sendJson(client, { type: 'error', message: '房间不存在或已关闭。' }); return; }
    if (room.started) { sendJson(client, { type: 'error', message: '本桌已经开始，请等待下一桌。' }); return; }
    if (room.players.length >= 4) { sendJson(client, { type: 'error', message: '房间已满，当前只支持 4 人一桌。' }); return; }
    const playerId = [0, 1, 2, 3].find(id => !room.clients.has(id));
    joinRoom(client, room, message.name, playerId);
}

function handleMessage(client, message) {
    if (!message || typeof message !== 'object') return;
    if (message.type === 'create') { createRoom(client, message); return; }
    if (message.type === 'join') { joinExistingRoom(client, message); return; }
    if (message.type === 'leave') { removeFromRoom(client); return; }
    if (!client.roomCode) { sendJson(client, { type: 'error', message: '请先创建或加入房间。' }); return; }
    const room = rooms.get(client.roomCode);
    if (!room) { sendJson(client, { type: 'error', message: '房间已关闭。' }); return; }
    if (message.type === 'ready') {
        if (room.started) { sendJson(client, { type: 'error', message: '本桌已经开始。' }); return; }
        if (room.players.length < 4) { sendJson(client, { type: 'error', message: '需要 4 位玩家入座后才能开始。' }); return; }
        room.ready.add(client.playerId);
        broadcastRoom(room);
        if (room.players.length === 4 && room.players.every(player => room.ready.has(player.id))) {
            room.started = true;
            for (const player of room.players) {
                const playerClient = room.clients.get(player.id);
                if (playerClient) sendJson(playerClient, { type: 'start', roomCode: room.code });
            }
        }
        return;
    }
    if (message.type === 'state' && client.playerId === room.hostId) {
        room.snapshot = message.snapshot || null;
        for (const [id, playerClient] of room.clients) if (id !== room.hostId) sendJson(playerClient, { type: 'state', roomCode: room.code, snapshot: privateSnapshot(room.snapshot, id) });
    } else if (message.type === 'action') {
        const host = room.clients.get(room.hostId);
        if (host) sendJson(host, { type: 'action', from: client.playerId, action: message.action || {} });
    }
}

function serveFile(request, response) {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const relativePath = pathname === '/' ? 'hengyang-510k/index.html' : pathname.replace(/^\/+/, '');
    const filePath = path.resolve(ROOT, relativePath);
    if (filePath !== ROOT && !filePath.startsWith(`${ROOT}${path.sep}`)) {
        response.writeHead(403); response.end('Forbidden'); return;
    }
    fs.stat(filePath, (error, stats) => {
        if (error || !stats.isFile()) { response.writeHead(404); response.end('Not found'); return; }
        response.writeHead(200, { 'Content-Type': MIME_TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream', 'Cache-Control': 'no-store' });
        fs.createReadStream(filePath).pipe(response);
    });
}

const server = http.createServer(serveFile);
server.on('upgrade', (request, socket) => {
    const key = request.headers['sec-websocket-key'];
    if (!key) { socket.destroy(); return; }
    const accept = crypto.createHash('sha1').update(`${key}${WS_GUID}`).digest('base64');
    socket.write(`HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: ${accept}\r\n\r\n`);
    const client = { socket, buffer: Buffer.alloc(0), roomCode: null, playerId: null };
    clients.add(client);
    socket.on('data', chunk => { client.buffer = Buffer.concat([client.buffer, chunk]); parseFrames(client); });
    socket.on('error', () => removeFromRoom(client));
    socket.on('close', () => { removeFromRoom(client); clients.delete(client); });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`衡阳 510K online server listening on http://127.0.0.1:${PORT}/hengyang-510k/index.html`);
});
