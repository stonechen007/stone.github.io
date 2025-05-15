class Game2048 {
    constructor() {
        this.gridSize = 4;
        this.cells = [];
        this.score = 0;
        this.bestScore = parseInt(localStorage.getItem('bestScore')) || 0;
        this.gameOver = false;
        
        this.init();
        this.setupEventListeners();
    }

    init() {
        this.createGrid();
        this.score = 0;
        this.updateScore();
        this.gameOver = false;
        
        // 清空所有方块
        const tiles = document.querySelectorAll('.tile');
        tiles.forEach(tile => tile.remove());
        
        // 初始化空数组
        this.cells = Array(this.gridSize).fill(null)
            .map(() => Array(this.gridSize).fill(null));
        
        // 添加两个初始方块
        this.addNewTile();
        this.addNewTile();
        
        document.querySelector('.game-message').classList.remove('game-over');
    }

    createGrid() {
        const container = document.querySelector('.grid-container');
        container.innerHTML = '';
        
        // 创建背景格子
        for (let i = 0; i < this.gridSize * this.gridSize; i++) {
            const cell = document.createElement('div');
            cell.classList.add('grid-cell');
            container.appendChild(cell);
        }
    }

    addNewTile() {
        const emptyCells = [];
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (!this.cells[i][j]) {
                    emptyCells.push({x: i, y: j});
                }
            }
        }
        
        if (emptyCells.length) {
            const {x, y} = emptyCells[Math.floor(Math.random() * emptyCells.length)];
            const value = Math.random() < 0.9 ? 2 : 4;
            this.cells[x][y] = value;
            this.createTileElement(x, y, value);
        }
    }

    createTileElement(x, y, value) {
        const tile = document.createElement('div');
        tile.classList.add('tile');
        tile.setAttribute('data-value', value);
        tile.textContent = value;
        
        const position = this.calculatePosition(x, y);
        tile.style.left = position.left + 'px';
        tile.style.top = position.top + 'px';
        
        document.querySelector('.grid-container').appendChild(tile);
    }

    calculatePosition(row, col) {
        const cellSize = document.querySelector('.grid-cell').offsetWidth;
        const gap = 15; // CSS中定义的grid-gap
        return {
            top: row * (cellSize + gap),
            left: col * (cellSize + gap)
        };
    }

    updateScore() {
        document.getElementById('score').textContent = this.score;
        if (this.score > this.bestScore) {
            this.bestScore = this.score;
            localStorage.setItem('bestScore', this.bestScore);
            document.getElementById('best-score').textContent = this.bestScore;
        }
    }

    move(direction) {
        if (this.gameOver) return;

        const previousState = JSON.stringify(this.cells);
        let moved = false;

        // 根据方向重新排列数组
        let grid = this.cells;
        if (direction === 'right' || direction === 'down') {
            grid = grid.map(row => row.reverse());
        }
        if (direction === 'up' || direction === 'down') {
            grid = this.transpose(grid);
        }

        // 对每一行进行移动和合并
        grid = grid.map(row => {
            const newRow = row.filter(cell => cell !== null);
            for (let i = 0; i < newRow.length - 1; i++) {
                if (newRow[i] === newRow[i + 1]) {
                    newRow[i] *= 2;
                    this.score += newRow[i];
                    newRow.splice(i + 1, 1);
                }
            }
            while (newRow.length < this.gridSize) {
                newRow.push(null);
            }
            return newRow;
        });

        // 还原数组方向
        if (direction === 'up' || direction === 'down') {
            grid = this.transpose(grid);
        }
        if (direction === 'right' || direction === 'down') {
            grid = grid.map(row => row.reverse());
        }

        this.cells = grid;

        // 检查是否有变化
        if (previousState !== JSON.stringify(this.cells)) {
            this.updateTiles();
            this.addNewTile();
            this.updateScore();
            
            // 检查游戏是否结束
            if (!this.canMove()) {
                this.gameOver = true;
                document.querySelector('.game-message').classList.add('game-over');
                document.querySelector('.game-message p').textContent = '游戏结束！';
            }
        }
    }

    transpose(array) {
        return array[0].map((_, colIndex) => array.map(row => row[colIndex]));
    }

    updateTiles() {
        const container = document.querySelector('.grid-container');
        const tiles = document.querySelectorAll('.tile');
        tiles.forEach(tile => tile.remove());

        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.cells[i][j]) {
                    this.createTileElement(i, j, this.cells[i][j]);
                }
            }
        }
    }

    canMove() {
        // 检查是否有空格子
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (!this.cells[i][j]) return true;
            }
        }

        // 检查是否有相邻的相同数字
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                const current = this.cells[i][j];
                if ((i < this.gridSize - 1 && current === this.cells[i + 1][j]) ||
                    (j < this.gridSize - 1 && current === this.cells[i][j + 1])) {
                    return true;
                }
            }
        }

        return false;
    }

    setupEventListeners() {
        // 键盘控制
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowLeft': this.move('left'); break;
                case 'ArrowRight': this.move('right'); break;
                case 'ArrowUp': this.move('up'); break;
                case 'ArrowDown': this.move('down'); break;
            }
        });

        // 触摸控制
        let touchStartX, touchStartY;
        const container = document.querySelector('.grid-container');

        container.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        });

        container.addEventListener('touchend', (e) => {
            if (!touchStartX || !touchStartY) return;

            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;

            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;

            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                if (Math.abs(deltaX) > 30) { // 最小滑动距离
                    this.move(deltaX > 0 ? 'right' : 'left');
                }
            } else {
                if (Math.abs(deltaY) > 30) {
                    this.move(deltaY > 0 ? 'down' : 'up');
                }
            }
        });

        // 重新开始按钮
        document.querySelector('.retry-button').addEventListener('click', () => {
            this.init();
        });
    }
}

// 启动游戏
window.onload = () => {
    new Game2048();
};