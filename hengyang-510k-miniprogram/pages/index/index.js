const rules = require('../../utils/rules');

const DEFAULT_SOCKET_URL = 'wss://example.com/ws';
const DEFAULT_NAMES = ['你', '湘江客', '岳阳楼', '回雁峰'];
const SEAT_POSITIONS = ['seat-bottom', 'seat-left', 'seat-top', 'seat-right'];

Page({
  data: {
    screen: 'welcome',
    showRules: false,
    name: '南家',
    serverUrl: DEFAULT_SOCKET_URL,
    roomCodeInput: '',
    roomCode: '',
    readyCount: 0,
    roomReady: false,
    roomFull: false,
    selfId: -1,
    hostId: 0,
    status: '请输入在线服务器地址，然后创建或加入房间。',
    statusError: false,
    roomSeats: Array.from({ length: 4 }, (_, id) => ({ id, empty: true, seatNo: id + 1 })),
    gameView: null
  },

  onLoad(options = {}) {
    this.socket = null;
    this.socketOpen = false;
    this.pending = null;
    this.onlineRoom = null;
    this.game = null;
    this.selected = new Set();
    const sharedRoomCode = (options.room || '').trim().toUpperCase();
    if (/^[A-Z0-9]{6}$/.test(sharedRoomCode)) {
      this.setData({ screen: 'lobby', roomCodeInput: sharedRoomCode, status: `已读取房间码 ${sharedRoomCode}，请输入昵称和服务地址后加入房间。` });
    }
  },

  onUnload() {
    if (this.socket) this.socket.close();
  },

  setStatus(message, error = false) {
    this.setData({ status: message, statusError: error });
  },

  showRuleError(message) {
    wx.showModal({
      title: '错误牌型',
      content: message,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  onNameInput(event) { this.setData({ name: (event.detail.value || '').slice(0, 12) }); },
  onServerInput(event) { this.setData({ serverUrl: event.detail.value || '' }); },
  onRoomCodeInput(event) { this.setData({ roomCodeInput: (event.detail.value || '').toUpperCase().slice(0, 6) }); },
  openRules() { this.setData({ showRules: true }); },
  closeRules() { this.setData({ showRules: false }); },
  closeRulesByMask(event) { if (event.target === event.currentTarget) this.closeRules(); },

  openLobby() {
    this.setData({ screen: 'lobby' });
    this.setStatus('请输入服务器地址，创建房间或加入朋友的房间。');
  },

  connect(kind, roomCode = '') {
    const url = (this.data.serverUrl || '').trim();
    const name = (this.data.name || '玩家').trim().slice(0, 12) || '玩家';
    if (!url || /example\.com/.test(url)) {
      this.setStatus('请先把服务地址改成你的公网 wss:// 地址。开发工具本地联调可填写 ws://127.0.0.1:4173。', true);
      return;
    }
    this.pending = { type: kind, name, roomCode: (roomCode || '').trim().toUpperCase() };
    this.setData({ screen: 'lobby' });
    if (this.socket && this.socketOpen) {
      this.sendPending();
      return;
    }
    if (this.socket) this.socket.close();
    this.setStatus(`正在连接 ${url} …`);
    try {
      const socket = wx.connectSocket({ url, timeout: 10000 });
      this.socket = socket;
      socket.onOpen(() => {
        this.socketOpen = true;
        this.setStatus('服务器已连接，正在进入房间…');
        this.sendPending();
      });
      socket.onMessage(message => this.receiveSocketMessage(message));
      socket.onError(() => this.setStatus('无法连接在线服务器，请检查 WSS 地址和合法域名配置。', true));
      socket.onClose(() => {
        this.socketOpen = false;
        if (!this.onlineRoom) this.setStatus('连接已断开。', true);
        this.socket = null;
      });
    } catch (error) {
      this.setStatus(`连接地址无效：${error.message || error}`, true);
    }
  },

  createRoom() { this.connect('create'); },

    joinRoom() {
    const code = (this.data.roomCodeInput || '').trim().toUpperCase();
    if (code.length !== 6) {
      this.setStatus('请输入 6 位房间码。', true);
      return;
    }
    this.connect('join', code);
    },

  readyOnline() {
    if (!this.onlineRoom || this.onlineRoom.started || this.onlineRoom.players.length < 4 || this.onlineRoom.ready?.[this.onlineRoom.selfId]) return;
    if (!this.sendMessage({ type: 'ready', roomCode: this.onlineRoom.code })) return;
    this.setData({ roomReady: true });
    this.setStatus('你已点击开始，等待其他玩家准备。');
  },

  sendPending() {
    if (!this.socket || !this.pending) return;
    const pending = this.pending;
    this.pending = null;
    this.socket.send({ data: JSON.stringify(pending) });
  },

  sendMessage(payload) {
    if (!this.socket || !this.socketOpen) {
      this.setStatus('网络连接已断开，请重新连接。', true);
      return false;
    }
    this.socket.send({ data: JSON.stringify(payload) });
    return true;
  },

  sendAction(action) {
    if (!this.onlineRoom) return false;
    return this.sendMessage({ type: 'action', roomCode: this.onlineRoom.code, action });
  },

  receiveSocketMessage(message) {
    try {
      const payload = typeof message.data === 'string' ? JSON.parse(message.data) : JSON.parse(String(message.data));
      this.handleServerMessage(payload);
    } catch (error) {
      this.setStatus('服务器返回了无法识别的数据。', true);
    }
  },

  handleServerMessage(message) {
    if (message.type === 'error') {
      this.setStatus(message.message || '在线服务发生错误。', true);
      return;
    }
    if (message.type === 'room') {
      this.onlineRoom = { ...message.room, selfId: message.selfId, hostId: message.hostId };
      const ready = Array.isArray(this.onlineRoom.ready) ? this.onlineRoom.ready : [];
      const readyCount = ready.filter(Boolean).length;
      this.setData({ roomCode: this.onlineRoom.code, selfId: this.onlineRoom.selfId, hostId: this.onlineRoom.hostId, readyCount, roomReady: Boolean(ready[this.onlineRoom.selfId]), roomFull: this.onlineRoom.players.length === 4, roomSeats: this.makeRoomSeats() });
      this.setStatus(this.onlineRoom.started ? '四人已准备，房主正在发牌。' : this.onlineRoom.players.length >= 4 ? `4 人已到齐 · 已准备 ${readyCount}/4，请全部点击开始游戏。` : `房间 ${this.onlineRoom.code} · 已入座 ${this.onlineRoom.players.length}/4，等待其他玩家加入。`);
      return;
    }
    if (message.type === 'start') {
      this.setStatus('4 位玩家已准备，房主正在发牌。');
      if (this.onlineRoom?.selfId === 0) this.startOnlineHostGame();
      return;
    }
    if (message.type === 'state') {
      this.loadOnlineState(message.snapshot);
      return;
    }
    if (message.type === 'action') this.handleHostAction(message);
  },

  makeRoomSeats() {
    const players = this.onlineRoom?.players || [];
    const ready = Array.isArray(this.onlineRoom?.ready) ? this.onlineRoom.ready : [];
    return Array.from({ length: 4 }, (_, id) => {
      const player = players.find(item => item.id === id);
      const readyText = ready[id] ? '已准备' : id === this.onlineRoom.hostId ? '房主' : id === this.onlineRoom.selfId ? '你' : '已加入';
      return player ? { id, name: player.name, avatar: (player.name || '玩家').slice(0, 1), host: id === this.onlineRoom.hostId, self: id === this.onlineRoom.selfId, ready: Boolean(ready[id]), statusText: `${readyText}${id === this.onlineRoom.selfId && ready[id] ? ' · 你' : ''}`, empty: false, seatNo: id + 1 } : { id, empty: true, seatNo: id + 1 };
    });
  },

  startOnlineHostGame() {
    if (!this.onlineRoom || this.onlineRoom.selfId !== 0 || this.onlineRoom.players.length < 4 || this.game?.online) return;
    const names = Array.from({ length: 4 }, (_, id) => this.onlineRoom.players.find(player => player.id === id)?.name || `玩家${id + 1}`);
    this.newGame({ online: true, playerNames: names, roomCode: this.onlineRoom.code, localPlayerId: 0, hostId: 0 });
    this.setStatus('4 人已入座，房主已发牌。');
    this.broadcastState();
  },

  startOnlineNextGame() {
    if (!this.game?.online || !this.onlineRoom || this.onlineRoom.selfId !== 0) return;
    this.newGame({ online: true, playerNames: this.game.players.map(player => player.name), roomCode: this.onlineRoom.code, localPlayerId: 0, hostId: 0 });
    this.setStatus('房主已开始下一局，等待四人完成叫牌。');
    this.broadcastState();
  },

  requestNextGame() {
    if (!this.game?.online) return;
    if (this.onlineRoom?.selfId === 0) this.startOnlineNextGame();
    else this.sendAction({ type: 'next' });
  },

  serializeState() {
    const snapshot = JSON.parse(JSON.stringify(this.game));
    delete snapshot.deck;
    delete snapshot.localPlayerId;
    delete snapshot.hostId;
    return snapshot;
  },

  broadcastState() {
    if (!this.game?.online || !this.onlineRoom || this.onlineRoom.selfId !== 0) return;
    this.sendMessage({ type: 'state', roomCode: this.onlineRoom.code, snapshot: this.serializeState() });
  },

  loadOnlineState(snapshot) {
    if (!snapshot || !this.onlineRoom || this.onlineRoom.selfId === 0) return;
    this.game = snapshot;
    this.game.online = true;
    this.game.localPlayerId = this.onlineRoom.selfId;
    this.game.hostId = 0;
    this.selected.clear();
    this.setData({ screen: 'game' });
    this.refreshView();
  },

  getLocalId() { return this.game?.online ? this.game.localPlayerId : 0; },
  getTeamOf(id) { return this.game?.players?.[id]?.team ?? -1; },
  getMyTeamId() { const team = this.getTeamOf(this.getLocalId()); return team >= 0 ? team : 0; },
  getOpponentTeamId() { return this.getMyTeamId() === 0 ? 1 : 0; },
  teamMembers(teamId) { return this.game?.teams?.[teamId] || []; },
  areJokersRevealed() {
    const played = new Set((this.game?.players || []).flatMap(player => player.playedJokers || []));
    return played.has('大王') && played.has('小王');
  },
  getVisibleRelation(id) {
    if (!this.game) return '';
    const declarations = this.game.declarations || [];
    if (declarations.length >= 2) {
      if (id === declarations[0]) return '宣起';
      if (id === declarations[1]) return '加宣';
      return '弃牌';
    }
    if (declarations.length === 1) return id === declarations[0] ? '宣起' : '队友';
    if (!this.areJokersRevealed() || !this.game.teams) return '';
    return this.game.players[id].team === this.getMyTeamId() ? '我方' : '对手';
  },
  isRelationshipVisible() { return (this.game?.declarations || []).length > 0 || this.areJokersRevealed(); },

  refreshView() {
    if (!this.game) return;
    const localId = this.getLocalId();
    const myTeamId = this.getMyTeamId();
    const opponentTeamId = this.getOpponentTeamId();
    const relationshipVisible = this.isRelationshipVisible();
    const finishLabels = ['上游', '二游', '三游', '末游'];
    const players = this.game.players.map((player, id) => ({
      ...player,
      position: SEAT_POSITIONS[id],
      avatar: (player.name || '玩家').slice(0, 1),
      captureText: `抓分 ${player.captured ?? 0}`,
      isTurn: this.game.mode === 'playing' && this.game.turn === id,
      finishText: this.game.finishOrder.indexOf(id) >= 0 ? finishLabels[this.game.finishOrder.indexOf(id)] : '',
      jokerText: (player.playedJokers || []).length ? ((player.playedJokers || []).includes('大王') && (player.playedJokers || []).includes('小王') ? '大小王' : (player.playedJokers || []).join(' · ')) : '',
      stateText: this.game.finishOrder.indexOf(id) >= 0 ? finishLabels[this.game.finishOrder.indexOf(id)] : player.hand.length === 0 ? '已出完' : !player.active && this.game.mode === 'playing' ? '本轮不出' : this.game.mode === 'call' ? '叫牌中' : this.game.mode === 'result' ? '本局结束' : this.game.turn === id ? '出牌中' : '等待',
      callText: (this.game.declarations || []).length >= 2 && id === this.game.declarations[1] ? '加宣' : (this.game.declarations || []).includes(id) ? '宣起' : '',
      relationText: this.getVisibleRelation(id),
      teamText: this.getVisibleRelation(id) || '身份未明',
      isMine: id === localId
    }));
    const hand = (this.game.players[localId]?.hand || []).map(card => ({ ...card, selected: this.selected.has(card.id), red: card.color === 'red' }));
    const played = (this.game.trick || []).map(entry => ({ ...entry.card, byName: this.game.players[entry.player]?.name || '玩家', byAvatar: (this.game.players[entry.player]?.name || '玩家').slice(0, 1), red: entry.card.color === 'red' }));
    const myTotal = this.teamMembers(myTeamId).reduce((sum, id) => sum + this.game.players[id].score, 0);
    const opponentTotal = this.teamMembers(opponentTeamId).reduce((sum, id) => sum + this.game.players[id].score, 0);
    const callChoice = this.game.callChoices?.[localId];
    const result = this.game.result ? {
      ...this.game.result,
      label: this.game.result.light === 3 ? '大光' : this.game.result.light === 2 ? '小光' : '小赢',
      callText: this.game.result.callMultiplier === 4 ? '加宣 ×4' : this.game.result.callMultiplier === 2 ? '宣起 ×2' : '未宣 ×1',
      myTotal,
      opponentTotal,
      winnerText: this.game.result.winningTeam === myTeamId ? `${this.game.players[localId].name}一方拿下本局` : '对手赢下本局',
      ratingText: `本局个人积分：${this.game.players.map(player => `${player.name} ${player.ratingDelta >= 0 ? '+' : ''}${player.ratingDelta ?? 0} → ${player.rating}`).join(' · ')}`,
      penaltyText: this.game.result.penalty ? `${this.game.players[this.game.result.penalty.to]?.name || ''} 获得 25 分罚分。` : ''
    } : null;
    this.setData({ gameView: {
      ...this.game,
      players,
      hand,
      played,
      localName: this.game.players[localId]?.name || '你',
      myTeamLabel: relationshipVisible ? (this.game.teams?.[myTeamId]?.length === 1 ? '我方总分 · 单打' : '我方总分') : '队伍未知',
      opponentTeamLabel: relationshipVisible ? (this.game.teams?.[opponentTeamId]?.length === 1 ? '对手总分 · 单打' : '对手总分') : '队伍未知',
      myTotal: relationshipVisible ? myTotal : '—',
      opponentTotal: relationshipVisible ? opponentTotal : '—',
      myTeamMembers: relationshipVisible ? this.teamMembers(myTeamId).map(id => this.game.players[id].name).join(' · ') : '双王未出 · 队友未知',
      opponentTeamMembers: relationshipVisible ? this.teamMembers(opponentTeamId).map(id => this.game.players[id].name).join(' · ') : '双王未出 · 队友未知',
      turnName: this.game.turn === null ? '叫牌阶段' : this.game.mode === 'result' ? '本局结束' : this.game.players[this.game.turn]?.name || '—',
      roundStatus: `${this.game.online ? `在线房间 ${this.game.onlineRoomCode || ''} · ` : ''}${this.game.mode === 'call' ? '发牌完成 · 朋友未知 · 叫牌阶段' : this.game.mode === 'result' ? '本局结算完成' : `第 ${this.game.trickNumber || 1} 轮 · ${this.game.lastPlay ? '跟牌中' : '等待领出'}`}`,
      roundStatusText: this.game.mode === 'call' ? '叫牌阶段' : this.game.mode === 'result' ? '已结束' : '进行中',
      trickTitle: this.game.mode === 'call' ? '先决定要不要宣起' : this.game.mode === 'result' ? '本局分数已落袋' : this.game.turn === localId ? (this.game.lastPlay ? '到你跟牌' : '到你领出') : `${this.game.players[this.game.turn]?.name || '玩家'} 正在出牌`,
      trickSubtitle: this.game.mode === 'result' ? '下一局庄家为本局最先出完牌的人' : this.game.lastPlay ? `${this.game.players[this.game.lastPlay.player]?.name || '玩家'} 的 ${rules.TYPE_NAMES[this.game.lastPlay.combo.type]} · 其余玩家可选择不要` : '黑桃 3 先出；宣起或加宣后由喊牌者先出',
      trickPointsText: `${rules.cardsPoints((this.game.trick || []).map(entry => entry.card))} 分`,
      lastTypeText: this.game.lastPlay ? rules.TYPE_NAMES[this.game.lastPlay.combo.type] : '自由领出',
      callStateText: this.game.mode === 'call' ? '待决定' : this.game.declarations.length === 2 ? '宣起 + 加宣 · ×4' : this.game.declarations.length === 1 ? '宣起 · ×2' : '未宣',
      callChoice,
      canCall: this.game.mode === 'call' && callChoice == null,
      pendingCalls: this.game.callChoices ? this.game.callChoices.filter(choice => choice !== null).length : 0,
      canPlay: this.game.mode === 'playing' && this.game.turn === localId && this.game.players[localId]?.active && this.selected.size > 0,
      canPass: this.game.mode === 'playing' && this.game.turn === localId && this.game.players[localId]?.active && this.game.lastPlay && this.game.lastPlay.player !== localId,
      actionText: this.game.mode === 'call' ? '先完成叫牌，再进入出牌阶段' : this.game.mode === 'result' ? '本局已结束，点击再来一局' : this.game.turn === localId ? (this.game.lastPlay ? `轮到你：选择能压过 ${rules.TYPE_NAMES[this.game.lastPlay.combo.type]} 的牌，或选择不要` : '轮到你领出：可以出任意合法牌型') : `${this.game.players[this.game.turn]?.name || '玩家'} 思考中…`,
      result
    } });
  },

  newGame(options = {}) {
    const previous = this.game;
    const dealer = previous?.finishOrder?.length ? previous.finishOrder[0] : previous ? (previous.dealer + 1) % 4 : 0;
    const previousRatings = previous?.players?.map(player => player.rating) || [100, 100, 100, 100];
    const names = options.playerNames || DEFAULT_NAMES;
    const players = names.map((name, id) => ({ id, name, short: name.slice(0, 1), hand: [], active: true, score: 0, captured: 0, rating: previousRatings[id] ?? 100, ratingDelta: 0, playedJokers: [], finishAt: null }));
    const deck = rules.shuffle(rules.makeDeck());
    const handSizes = [14, 13, 14, 13].map((_, id) => id === dealer || id === (dealer + 1) % 4 ? 14 : 13);
    let cursor = 0;
    for (let round = 0; round < 14; round++) for (let offset = 0; offset < 4; offset++) {
      const id = (dealer + offset) % 4;
      if (players[id].hand.length < handSizes[id]) players[id].hand.push(deck[cursor++]);
    }
    players.forEach(player => rules.sortHandCards(player.hand));
    this.game = {
      mode: 'call', round: previous ? previous.round + 1 : 1, dealer, players, deck,
      declarations: [], callChoices: options.online ? [null, null, null, null] : null, callMultiplier: 1, teams: null, lead: null, turn: null,
      lastPlay: null, trick: [], passCount: 0, trickNumber: 0, totalCaptured: [0, 0, 0, 0], finishOrder: [], penalties: [], log: [], clock: 0, autoClock: 0,
      hintId: null, online: !!options.online, localPlayerId: options.localPlayerId ?? 0, hostId: options.hostId ?? 0, onlineRoomCode: options.roomCode || null
    };
    this.selected.clear();
    this.addLog(`第 ${this.game.round} 局发牌完成，${players[dealer].name} 坐庄。`);
    this.addLog('朋友未知，先决定是否宣起。');
    this.setData({ screen: 'game' });
    this.refreshView();
  },

  addLog(message) {
    if (!this.game) return;
    this.game.log.unshift({ message, time: this.game.log.length + 1 });
    this.game.log = this.game.log.slice(0, 12);
  },

  submitCall(playerId, call) {
    if (!this.game?.online || this.game.mode !== 'call' || this.game.callChoices[playerId] !== null) return;
    this.game.callChoices[playerId] = call ? 'call' : 'skip';
    this.addLog(`${this.game.players[playerId].name}${call ? ' 宣起了。' : ' 选择不宣。'}`);
    if (this.game.callChoices.every(Boolean)) {
      const callers = this.game.callChoices.map((choice, id) => choice === 'call' ? id : null).filter(id => id !== null);
      this.game.declarations = callers.slice(0, 2);
      this.game.callMultiplier = this.game.declarations.length >= 2 ? 4 : this.game.declarations.length === 1 ? 2 : 1;
      if (!this.game.declarations.length) this.addLog('无人宣起，按黑桃 3 先出。');
      else if (this.game.declarations.length === 1) this.addLog(`${this.game.players[this.game.declarations[0]].name} 宣起，本局积分翻倍。`);
      else this.addLog(`${this.game.players[this.game.declarations[0]].name} 宣起，${this.game.players[this.game.declarations[1]].name} 加宣，进入单挑。`);
      this.finishCall();
    } else {
      this.refreshView();
    }
    this.broadcastState();
  },

  handleCall(event) {
    if (!this.game || this.game.mode !== 'call' || !this.game.callChoices || this.game.callChoices[this.getLocalId()] !== null) return;
    const call = event.currentTarget.dataset.call === 'true';
    const localId = this.getLocalId();
    if (localId === this.game.hostId) this.submitCall(localId, call);
    else this.sendAction({ type: 'call', call });
  },

  finishCall() {
    this.game.mode = 'playing';
    if (this.game.declarations.length === 2) {
      this.game.players.forEach((player, id) => { player.active = this.game.declarations.includes(id); });
      this.game.teams = [[this.game.declarations[0]], [this.game.declarations[1]]];
      this.game.lead = this.game.declarations[1];
    } else if (this.game.declarations.length === 1) {
      const solo = this.game.declarations[0];
      this.game.teams = [[solo], [0, 1, 2, 3].filter(id => id !== solo)];
      this.game.lead = solo;
    } else {
      const big = this.game.players.findIndex(player => player.hand.some(card => card.rank === 17));
      const small = this.game.players.findIndex(player => player.hand.some(card => card.rank === 16));
      this.game.teams = big === small ? [[big], [0, 1, 2, 3].filter(id => id !== big)] : [[big, small], [0, 1, 2, 3].filter(id => id !== big && id !== small)];
      this.game.lead = this.game.players.findIndex(player => player.hand.some(card => card.suit === 3 && card.rank === 3));
    }
    if (!this.game.teams[0].includes(this.getLocalId())) this.game.teams.reverse();
    this.game.turn = this.game.lead;
    this.game.players.forEach(player => { player.team = this.game.teams.findIndex(team => team.includes(player.id)); });
    this.addLog(`本局 ${this.game.teams[0].length} 对 ${this.game.teams[1].length}，${this.game.players[this.game.lead].name} 先出牌。`);
    this.refreshView();
    this.broadcastState();
  },

  pointsFor(card) { return rules.pointsFor(card); },
  cardsPoints(cards) { return rules.cardsPoints(cards); },

  collectTrick(winner) {
    const points = this.cardsPoints(this.game.trick.map(entry => entry.card));
    this.game.totalCaptured[winner] += points;
    this.game.players[winner].captured += points;
    this.game.players[winner].score += points;
    this.addLog(`${this.game.players[winner].name} 收走本轮 ${points} 分，继续出牌。`);
    this.game.lastPlay = null;
    this.game.trick = [];
    this.game.passCount = 0;
    return points;
  },

  nextActive(from) {
    for (let step = 1; step <= 4; step++) {
      const id = (from + step) % 4;
      if (this.game.players[id].active && this.game.players[id].hand.length) return id;
    }
    return from;
  },

  submitPlay(playerId, cards) {
    const combo = rules.evaluate(cards);
    if (!combo || (this.game.lastPlay && !rules.canBeat(combo, this.game.lastPlay.combo))) return false;
    const player = this.game.players[playerId];
    const ids = new Set(cards.map(card => card.id));
    player.hand = player.hand.filter(card => !ids.has(card.id));
    const jokerLabels = cards
      .filter(card => card.joker)
      .map(card => card.rank === 17 ? '大王' : '小王');
    if (jokerLabels.length) {
      player.playedJokers = [...new Set([...(player.playedJokers || []), ...jokerLabels])];
    }
    this.game.lastPlay = { player: playerId, combo };
    this.game.trick.push(...cards.map(card => ({ card, player: playerId })));
    this.game.passCount = 0;
    this.game.trickNumber++;
    if (!this.game.finishOrder.includes(playerId) && player.hand.length === 0) this.game.finishOrder.push(playerId);
    this.addLog(`${player.name} 出 ${rules.TYPE_NAMES[combo.type]}${combo.type === 'four' ? ' · 炸弹' : ''}。`);
    if (['rocket', 'four', 'straight510', 'mixed510'].includes(combo.type)) this.addLog(`⚡ ${player.name} 打出${rules.TYPE_NAMES[combo.type]}。`);
    if (this.checkGameEnd()) return true;
    this.game.turn = this.nextActive(playerId);
    return true;
  },

  pass(playerId) {
    if (!this.game.lastPlay || this.game.lastPlay.player === playerId) return false;
    this.game.passCount++;
    this.addLog(`${this.game.players[playerId].name} 不要。`);
    const remainingPlayers = this.game.players.filter(player => player.active && player.hand.length > 0).length;
    const winner = this.game.lastPlay.player;
    const requiredPasses = this.game.players[winner].hand.length ? Math.max(1, remainingPlayers - 1) : Math.max(1, remainingPlayers);
    if (this.game.passCount >= requiredPasses) {
      this.collectTrick(winner);
      this.game.turn = this.game.players[winner].hand.length ? winner : this.nextActive(winner);
      this.game.trickNumber = Math.max(0, this.game.trickNumber - 1);
    } else this.game.turn = this.nextActive(playerId);
    return true;
  },

  checkGameEnd() {
    if (!this.game.teams) return false;
    const endedTeam = this.game.teams.findIndex(team => team.every(id => this.game.players[id].hand.length === 0));
    if (endedTeam < 0) return false;
    if (this.game.trick.length && this.game.lastPlay) this.collectTrick(this.game.lastPlay.player);
    this.finishRound(endedTeam);
    return true;
  },

  applyRatingChanges(winningTeam, light, multiplier) {
    const unit = light * multiplier;
    const winners = this.teamMembers(winningTeam);
    const losers = this.teamMembers(winningTeam === 0 ? 1 : 0);
    const delta = [0, 0, 0, 0];
    if (winners.length === 1 && losers.length === 1 && this.game.declarations.length === 2) {
      // 加宣为 1 对 1：赢家通吃三家的积分，输家独自承担三份。
      delta[winners[0]] = unit * 3;
      delta[losers[0]] = -unit * 3;
    } else if (winners.length === 1) {
      delta[winners[0]] = unit * losers.length;
      losers.forEach(id => { delta[id] = -unit; });
    } else if (losers.length === 1) {
      winners.forEach(id => { delta[id] = unit; });
      delta[losers[0]] = -unit * winners.length;
    } else {
      winners.forEach(id => { delta[id] = unit; });
      losers.forEach(id => { delta[id] = -unit; });
    }
    this.game.players.forEach((player, id) => { player.ratingDelta = delta[id]; player.rating += delta[id]; });
    return delta;
  },

  finishRound(endedTeam) {
    if (this.game.mode === 'result') return;
    const firstFinisher = this.game.finishOrder[0];
    const firstTeam = firstFinisher === undefined ? endedTeam : this.getTeamOf(firstFinisher);
    const firstMembers = this.teamMembers(firstTeam);
    const firstTeammate = firstMembers.find(id => id !== firstFinisher);
    const teamFinishers = this.game.finishOrder.filter(id => firstMembers.includes(id));
    const teammateWasLast = firstTeammate !== undefined && teamFinishers[teamFinishers.length - 1] === firstTeammate;
    if (firstFinisher !== undefined && !teammateWasLast) {
      const payingTeam = firstTeam === 0 ? 1 : 0;
      const payers = this.teamMembers(payingTeam);
      const payer = [...payers].sort((a, b) => this.game.players[b].score - this.game.players[a].score)[0];
      if (payer !== undefined) this.game.players[payer].score -= 25;
      this.game.players[firstFinisher].score += 25;
      this.game.penalties.push({ from: payers, payer, to: firstFinisher, amount: 25 });
      this.addLog(`${this.game.players[firstFinisher].name} 首个出完，队友未压轴，触发 25 分罚分。`);
    }
    const myTotal = this.teamMembers(0).reduce((sum, id) => sum + this.game.players[id].score, 0);
    const theirTotal = this.teamMembers(1).reduce((sum, id) => sum + this.game.players[id].score, 0);
    const winningTeam = myTotal >= theirTotal ? 0 : 1;
    const opponents = this.teamMembers(winningTeam === 0 ? 1 : 0);
    const loserCapturedTotal = opponents.reduce((sum, id) => sum + this.game.players[id].captured, 0);
    const loserFinalTotal = opponents.reduce((sum, id) => sum + this.game.players[id].score, 0);
    const light = loserCapturedTotal === 0 && this.game.penalties.length > 0 ? 3 : loserFinalTotal <= 0 ? 2 : 1;
    const multiplier = this.game.callMultiplier;
    const points = light * multiplier;
    const ratingDelta = this.applyRatingChanges(winningTeam, light, multiplier);
    this.game.result = { winningTeam, myTotal, theirTotal, light, points, callMultiplier: multiplier, endedTeam, lastFinisher: this.game.finishOrder[this.game.finishOrder.length - 1], penalty: this.game.penalties[0] || null, ratingDelta, ratings: this.game.players.map(player => player.rating) };
    this.game.mode = 'result';
    this.addLog(`${winningTeam === 0 ? '我方拿下本局' : '对手赢下本局'} · ${light === 3 ? '大光' : light === 2 ? '小光' : '小赢'}，积分结算 ${points}。`);
  },

  handleHostAction(message) {
    if (!this.game?.online || !this.onlineRoom || this.onlineRoom.selfId !== 0 || message.from === 0) return;
    const playerId = message.from;
    const action = message.action || {};
    if (this.game.mode === 'call' && action.type === 'call') {
      this.submitCall(playerId, action.call === true);
      return;
    }
    if (this.game.mode === 'result' && action.type === 'next') {
      this.startOnlineNextGame();
      return;
    }
    if (this.game.mode !== 'playing' || this.game.turn !== playerId || !this.game.players[playerId]?.active) return;
    if (action.type === 'play') {
      const ids = new Set(Array.isArray(action.cardIds) ? action.cardIds : []);
      const cards = this.game.players[playerId].hand.filter(card => ids.has(card.id));
      if (cards.length && this.submitPlay(playerId, cards)) { this.refreshView(); this.broadcastState(); }
    } else if (action.type === 'pass' && this.game.lastPlay && this.game.lastPlay.player !== playerId) {
      this.pass(playerId);
      this.refreshView();
      this.broadcastState();
    }
  },

  playSelected() {
    const localId = this.getLocalId();
    if (!this.game || this.game.mode !== 'playing' || this.game.turn !== localId || !this.selected.size) return;
    const cards = this.game.players[localId].hand.filter(card => this.selected.has(card.id));
    const combo = rules.evaluate(cards);
    if (!combo) { const message = '这组牌无法组成合法牌型，请重新选择。'; this.addLog(`错误牌型：${message}`); this.showRuleError(message); this.refreshView(); return; }
    if (this.game.lastPlay && !rules.canBeat(combo, this.game.lastPlay.combo)) { const message = `当前牌型不能压过桌面的${rules.TYPE_NAMES[this.game.lastPlay.combo.type]}，请选择更大的同牌型或炸弹。`; this.addLog(`出牌无效：${message}`); this.showRuleError(message); this.refreshView(); return; }
    if (this.game.online && localId !== this.game.hostId) {
      this.sendAction({ type: 'play', cardIds: cards.map(card => card.id) });
      this.selected.clear();
      this.refreshView();
      return;
    }
    if (this.submitPlay(localId, cards)) {
      this.selected.clear();
      this.refreshView();
      this.broadcastState();
    }
  },

  passSelected() {
    const localId = this.getLocalId();
    if (!this.game || this.game.mode !== 'playing' || this.game.turn !== localId || !this.game.lastPlay || this.game.lastPlay.player === localId) return;
    this.selected.clear();
    if (this.game.online && localId !== this.game.hostId) {
      this.sendAction({ type: 'pass' });
      this.refreshView();
      return;
    }
    this.pass(localId);
    this.refreshView();
    this.broadcastState();
  },

  toggleCard(event) {
    const localId = this.getLocalId();
    if (!this.game || this.game.mode !== 'playing' || this.game.turn !== localId) return;
    const id = event.currentTarget.dataset.cardId;
    if (this.selected.has(id)) this.selected.delete(id); else this.selected.add(id);
    this.refreshView();
  },

  sortHand() {
    if (!this.game) return;
    rules.sortHandCards(this.game.players[this.getLocalId()].hand);
    this.selected.clear();
    this.refreshView();
  },

  findHint(playerId) {
    const hand = [...this.game.players[playerId].hand].sort((a, b) => a.rank - b.rank);
    const previous = this.game.lastPlay?.combo || null;
    if (!previous) return hand.length ? [hand[0]] : null;
    const targetSizes = previous.type === 'straight510' || previous.type === 'mixed510' ? [3, 6, 9, 12] : previous.type === 'chainPair' ? [previous.length * 2] : [previous.length];
    const choose = size => {
      let found = null;
      const walk = (start, picked) => {
        if (found) return;
        if (picked.length === size) {
          const combo = rules.evaluate(picked);
          if (combo && rules.canBeat(combo, previous)) found = [...picked];
          return;
        }
        for (let index = start; index <= hand.length - (size - picked.length); index++) walk(index + 1, [...picked, hand[index]]);
      };
      walk(0, []);
      return found;
    };
    for (const size of targetSizes) {
      if (size <= hand.length) {
        const cards = choose(size);
        if (cards) return cards;
      }
    }
    const rocket = hand.filter(card => card.joker);
    if (rocket.length === 2 && rules.canBeat(rules.evaluate(rocket), previous)) return rocket;
    for (const rank of [...new Set(hand.map(card => card.rank))]) {
      const bomb = hand.filter(card => card.rank === rank).slice(0, 4);
      if (bomb.length === 4 && rules.canBeat(rules.evaluate(bomb), previous)) return bomb;
    }
    return null;
  },

  showHint() {
    const localId = this.getLocalId();
    if (!this.game || this.game.mode !== 'playing' || this.game.turn !== localId) return;
    this.selected.clear();
    const cards = this.findHint(localId);
    if (cards) cards.forEach(card => this.selected.add(card.id));
    this.addLog(cards ? `提示：可以出 ${rules.TYPE_NAMES[rules.evaluate(cards).type]}。` : '提示：当前没有能压过桌面的牌，可以不要。');
    this.refreshView();
  },

  copyRoomCode() {
    if (!this.onlineRoom?.code) return;
    wx.setClipboardData({ data: this.onlineRoom.code, success: () => this.setStatus('房间码已复制，发给朋友吧。') });
  },

  leaveRoom() {
    this.sendMessage({ type: 'leave' });
    if (this.socket) this.socket.close();
    this.socket = null;
    this.socketOpen = false;
    this.pending = null;
    this.onlineRoom = null;
    this.game = null;
    this.selected.clear();
    this.setData({ screen: 'welcome', roomCode: '', selfId: -1, readyCount: 0, roomReady: false, roomFull: false, roomSeats: Array.from({ length: 4 }, (_, id) => ({ id, empty: true, seatNo: id + 1 })), gameView: null });
    this.setStatus('已退出房间。');
  },

  onShareAppMessage() {
    const roomCode = this.data.roomCode ? `?room=${encodeURIComponent(this.data.roomCode)}` : '';
    return { title: '衡阳 510K · 四人在线牌局', path: `/pages/index/index${roomCode}` };
  }
});
