class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.setupCanvas();
        
        // 游戏状态
        this.isPlaying = false;
        this.score = 0;
        this.player = null;
        this.enemies = [];
        this.bullets = [];
        this.powerUps = [];
        this.lastEnemySpawn = 0;
        this.lastPowerUpSpawn = 0;
        
        // 控制状态
        this.keys = {};
        this.touchPos = null;
        
        this.setupEventListeners();
        this.showStartScreen();
    }

    setupCanvas() {
        // 设置画布大小
        this.canvas.width = 400;
        this.canvas.height = 600;
    }

    setupEventListeners() {
        // 键盘控制
        window.addEventListener('keydown', (e) => this.keys[e.code] = true);
        window.addEventListener('keyup', (e) => this.keys[e.code] = false);
        
        // 触摸控制
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            this.touchPos = {
                x: (touch.clientX - rect.left) * (this.canvas.width / rect.width),
                y: (touch.clientY - rect.top) * (this.canvas.height / rect.height)
            };
        });
        
        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            this.touchPos = {
                x: (touch.clientX - rect.left) * (this.canvas.width / rect.width),
                y: (touch.clientY - rect.top) * (this.canvas.height / rect.height)
            };
        });
        
        this.canvas.addEventListener('touchend', () => {
            this.touchPos = null;
        });
        
        // 开始按钮
        document.getElementById('startBtn').addEventListener('click', () => this.startGame());
        document.getElementById('restartBtn').addEventListener('click', () => this.startGame());
    }

    startGame() {
        this.isPlaying = true;
        this.score = 0;
        this.updateScore();
        this.player = new Player(this);
        this.enemies = [];
        this.bullets = [];
        this.powerUps = [];
        
        document.querySelector('.game-start').style.display = 'none';
        document.querySelector('.game-over').style.display = 'none';
        
        this.gameLoop();
    }

    gameLoop() {
        if (!this.isPlaying) return;
        
        this.update();
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }

    update() {
        // 更新玩家
        this.player.update();
        
        // 生成敌人
        if (Date.now() - this.lastEnemySpawn > 1000) {
            this.spawnEnemy();
            this.lastEnemySpawn = Date.now();
        }
        
        // 生成道具
        if (Date.now() - this.lastPowerUpSpawn > 10000) {
            this.spawnPowerUp();
            this.lastPowerUpSpawn = Date.now();
        }
        
        // 更新敌人
        this.enemies = this.enemies.filter(enemy => {
            enemy.update();
            return !enemy.isDestroyed && enemy.y < this.canvas.height;
        });
        
        // 更新子弹
        this.bullets = this.bullets.filter(bullet => {
            bullet.update();
            return !bullet.isDestroyed && bullet.y > 0;
        });
        
        // 更新道具
        this.powerUps = this.powerUps.filter(powerUp => {
            powerUp.update();
            return !powerUp.isCollected && powerUp.y < this.canvas.height;
        });
        
        // 碰撞检测
        this.checkCollisions();
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.player.draw();
        this.enemies.forEach(enemy => enemy.draw());
        this.bullets.forEach(bullet => bullet.draw());
        this.powerUps.forEach(powerUp => powerUp.draw());
    }

    spawnEnemy() {
        const types = ['small', 'medium', 'large'];
        const type = types[Math.floor(Math.random() * types.length)];
        this.enemies.push(new Enemy(this, type));
    }

    spawnPowerUp() {
        const types = ['health', 'weapon', 'shield'];
        const type = types[Math.floor(Math.random() * types.length)];
        this.powerUps.push(new PowerUp(this, type));
    }

    checkCollisions() {
        // 子弹与敌人碰撞
        this.bullets.forEach(bullet => {
            this.enemies.forEach(enemy => {
                if (!enemy.isDestroyed && this.checkCollision(bullet, enemy)) {
                    enemy.hit(bullet.damage);
                    bullet.isDestroyed = true;
                    if (enemy.isDestroyed) {
                        this.score += enemy.points;
                        this.updateScore();
                    }
                }
            });
        });
        
        // 玩家与敌人碰撞
        this.enemies.forEach(enemy => {
            if (!enemy.isDestroyed && this.checkCollision(this.player, enemy)) {
                this.player.hit(enemy.damage);
                enemy.isDestroyed = true;
            }
        });
        
        // 玩家与道具碰撞
        this.powerUps.forEach(powerUp => {
            if (!powerUp.isCollected && this.checkCollision(this.player, powerUp)) {
                powerUp.collect();
            }
        });
    }

    checkCollision(obj1, obj2) {
        return obj1.x < obj2.x + obj2.width &&
               obj1.x + obj1.width > obj2.x &&
               obj1.y < obj2.y + obj2.height &&
               obj1.y + obj1.height > obj2.y;
    }

    updateScore() {
        document.getElementById('score').textContent = this.score;
    }

    gameOver() {
        this.isPlaying = false;
        document.getElementById('finalScore').textContent = this.score;
        document.querySelector('.game-over').style.display = 'block';
    }
}

class Player {
    constructor(game) {
        this.game = game;
        this.width = 40;
        this.height = 40;
        this.x = game.canvas.width / 2 - this.width / 2;
        this.y = game.canvas.height - this.height - 20;
        this.speed = 5;
        this.hp = 100;
        this.weapon = 'normal';
        this.lastShot = 0;
        this.shotDelay = 200;
        
        this.updateHp();
        this.updateWeapon();
    }

    update() {
        // 键盘控制
        if (this.game.keys['ArrowLeft']) this.x -= this.speed;
        if (this.game.keys['ArrowRight']) this.x += this.speed;
        if (this.game.keys['ArrowUp']) this.y -= this.speed;
        if (this.game.keys['ArrowDown']) this.y += this.speed;
        if (this.game.keys['Space'] && Date.now() - this.lastShot > this.shotDelay) {
            this.shoot();
        }
        
        // 触摸控制
        if (this.game.touchPos) {
            const dx = this.game.touchPos.x - (this.x + this.width / 2);
            const dy = this.game.touchPos.y - (this.y + this.height / 2);
            this.x += Math.sign(dx) * Math.min(Math.abs(dx), this.speed);
            this.y += Math.sign(dy) * Math.min(Math.abs(dy), this.speed);
            
            // 自动开火
            if (Date.now() - this.lastShot > this.shotDelay) {
                this.shoot();
            }
        }
        
        // 边界检查
        this.x = Math.max(0, Math.min(this.x, this.game.canvas.width - this.width));
        this.y = Math.max(0, Math.min(this.y, this.game.canvas.height - this.height));
    }

    draw() {
        this.game.ctx.fillStyle = '#4a90e2';
        this.game.ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    shoot() {
        switch(this.weapon) {
            case 'normal':
                this.game.bullets.push(new Bullet(this.game, this.x + this.width/2, this.y));
                break;
            case 'double':
                this.game.bullets.push(
                    new Bullet(this.game, this.x + 10, this.y),
                    new Bullet(this.game, this.x + this.width - 10, this.y)
                );
                break;
            case 'spread':
                for (let i = -1; i <= 1; i++) {
                    this.game.bullets.push(new Bullet(this.game, this.x + this.width/2, this.y, i * 0.3));
                }
                break;
        }
        this.lastShot = Date.now();
    }

    hit(damage) {
        this.hp -= damage;
        this.updateHp();
        if (this.hp <= 0) {
            this.game.gameOver();
        }
    }

    updateHp() {
        document.getElementById('hp').textContent = this.hp;
    }

    updateWeapon() {
        const weaponNames = {
            normal: '普通激光',
            double: '双发激光',
            spread: '散射激光'
        };
        document.getElementById('weapon').textContent = weaponNames[this.weapon];
    }
}

class Enemy {
    constructor(game, type) {
        this.game = game;
        this.type = type;
        this.isDestroyed = false;
        
        switch(type) {
            case 'small':
                this.width = 30;
                this.height = 30;
                this.hp = 1;
                this.speed = 3;
                this.damage = 10;
                this.points = 100;
                break;
            case 'medium':
                this.width = 40;
                this.height = 40;
                this.hp = 3;
                this.speed = 2;
                this.damage = 20;
                this.points = 200;
                break;
            case 'large':
                this.width = 60;
                this.height = 60;
                this.hp = 5;
                this.speed = 1;
                this.damage = 30;
                this.points = 300;
                break;
        }
        
        this.x = Math.random() * (game.canvas.width - this.width);
        this.y = -this.height;
    }

    update() {
        this.y += this.speed;
    }

    draw() {
        const colors = {
            small: '#ff4757',
            medium: '#ffa502',
            large: '#ff6b81'
        };
        this.game.ctx.fillStyle = colors[this.type];
        this.game.ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    hit(damage) {
        this.hp -= damage;
        if (this.hp <= 0) {
            this.isDestroyed = true;
        }
    }
}

class Bullet {
    constructor(game, x, y, angleOffset = 0) {
        this.game = game;
        this.width = 4;
        this.height = 10;
        this.x = x - this.width/2;
        this.y = y;
        this.speed = 7;
        this.damage = 1;
        this.angleOffset = angleOffset;
        this.isDestroyed = false;
    }

    update() {
        this.x += this.speed * this.angleOffset;
        this.y -= this.speed;
    }

    draw() {
        this.game.ctx.fillStyle = '#fff';
        this.game.ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class PowerUp {
    constructor(game, type) {
        this.game = game;
        this.type = type;
        this.width = 20;
        this.height = 20;
        this.x = Math.random() * (game.canvas.width - this.width);
        this.y = -this.height;
        this.speed = 2;
        this.isCollected = false;
    }

    update() {
        this.y += this.speed;
    }

    draw() {
        const colors = {
            health: '#2ecc71',
            weapon: '#f1c40f',
            shield: '#3498db'
        };
        this.game.ctx.fillStyle = colors[this.type];
        this.game.ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    collect() {
        this.isCollected = true;
        switch(this.type) {
            case 'health':
                this.game.player.hp = Math.min(100, this.game.player.hp + 30);
                this.game.player.updateHp();
                break;
            case 'weapon':
                const weapons = ['normal', 'double', 'spread'];
                const currentIndex = weapons.indexOf(this.game.player.weapon);
                this.game.player.weapon = weapons[(currentIndex + 1) % weapons.length];
                this.game.player.updateWeapon();
                break;
            case 'shield':
                this.game.player.hp = Math.min(100, this.game.player.hp + 50);
                this.game.player.updateHp();
                break;
        }
    }
}

// 启动游戏
window.onload = () => {
    new Game();
};