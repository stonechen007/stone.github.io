class Minesweeper {
    constructor() {
        this.difficulties = {
            easy: { rows: 9, cols: 9, mines: 10 },
            medium: { rows: 16, cols: 16, mines: 40 },
            hard: { rows: 16, cols: 30, mines: 99 }
        };
        this.currentDifficulty = 'easy';
        this.board = [];
        this.mineLocations = new Set();
        this.flaggedCells = new Set();
        this.revealedCells = new Set();
        this.isGameOver = false;
        this.isFirstClick = true;
        this.timer = 0;
        this.timerInterval = null;
        
        this.initializeGame();
        this.setupEventListeners();
    }

    initializeGame() {
        const { rows, cols, mines } = this.difficulties[this.currentDifficulty];
        this.board = Array(rows).fill().map(() => Array(cols).fill(0));
        this.mineLocations.clear();
        this.flaggedCells.clear();
        this.revealedCells.clear();
        this.isGameOver = false;
        this.isFirstClick = true;
        
        // 重置计时器
        clearInterval(this.timerInterval);
        this.timer = 0;
        document.getElementById('timer').textContent = '0';
        document.getElementById('mines-left').textContent = mines;
        
        this.renderBoard();
    }

    setupEventListeners() {
        const board = document.getElementById('board');
        
        // 电脑操作
        board.addEventListener('click', (e) => {
            const cell = e.target.closest('.cell');
            if (cell) this.handleCellClick(cell);
        });
        
        board.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const cell = e.target.closest('.cell');
            if (cell) this.toggleFlag(cell);
        });
        
        // 移动端操作
        let longPressTimer;
        let isLongPress = false;
        
        board.addEventListener('touchstart', (e) => {
            const cell = e.target.closest('.cell');
            if (!cell) return;
            
            isLongPress = false;
            longPressTimer = setTimeout(() => {
                isLongPress = true;
                this.toggleFlag(cell);
            }, 500);
        });
        
        board.addEventListener('touchend', (e) => {
            clearTimeout(longPressTimer);
            const cell = e.target.closest('.cell');
            if (cell && !isLongPress) {
                this.handleCellClick(cell);
            }
        });
        
        // 难度选择
        document.querySelectorAll('.difficulty button').forEach(button => {
            button.addEventListener('click', () => {
                document.querySelector('.difficulty button.active').classList.remove('active');
                button.classList.add('active');
                this.currentDifficulty = button.dataset.difficulty;
                this.initializeGame();
            });
        });
        
        // 新游戏按钮
        document.getElementById('new-game').addEventListener('click', () => {
            this.initializeGame();
        });
    }

    startTimer() {
        clearInterval(this.timerInterval);
        this.timer = 0;
        document.getElementById('timer').textContent = '0';
        this.timerInterval = setInterval(() => {
            this.timer++;
            document.getElementById('timer').textContent = this.timer;
        }, 1000);
    }

    placeMines(firstClickRow, firstClickCol) {
        const { rows, cols, mines } = this.difficulties[this.currentDifficulty];
        while (this.mineLocations.size < mines) {
            const row = Math.floor(Math.random() * rows);
            const col = Math.floor(Math.random() * cols);
            const key = `${row},${col}`;
            
            // 确保第一次点击的位置及其周围没有地雷
            if (Math.abs(row - firstClickRow) <= 1 && Math.abs(col - firstClickCol) <= 1) {
                continue;
            }
            
            if (!this.mineLocations.has(key)) {
                this.mineLocations.add(key);
                this.board[row][col] = -1; // -1 表示地雷
            }
        }
        
        // 计算每个格子周围的地雷数
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                if (this.board[row][col] !== -1) {
                    this.board[row][col] = this.countAdjacentMines(row, col);
                }
            }
        }
    }

    countAdjacentMines(row, col) {
        let count = 0;
        for (let i = -1; i <= 1; i++) {
            for (let j = -1; j <= 1; j++) {
                const newRow = row + i;
                const newCol = col + j;
                if (this.isValidCell(newRow, newCol) && this.board[newRow][newCol] === -1) {
                    count++;
                }
            }
        }
        return count;
    }

    isValidCell(row, col) {
        const { rows, cols } = this.difficulties[this.currentDifficulty];
        return row >= 0 && row < rows && col >= 0 && col < cols;
    }

    renderBoard() {
        const board = document.getElementById('board');
        const { rows, cols } = this.difficulties[this.currentDifficulty];
        
        board.style.gridTemplateColumns = `repeat(${cols}, var(--cell-size))`;
        board.innerHTML = '';
        
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                board.appendChild(cell);
            }
        }
    }

    handleCellClick(cell) {
        if (this.isGameOver) return;
        
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        if (this.flaggedCells.has(`${row},${col}`)) return;
        
        if (this.isFirstClick) {
            this.isFirstClick = false;
            this.placeMines(row, col);
            this.startTimer();
        }
        
        this.revealCell(row, col);
    }

    revealCell(row, col) {
        if (!this.isValidCell(row, col)) return;
        
        const key = `${row},${col}`;
        if (this.revealedCells.has(key) || this.flaggedCells.has(key)) return;
        
        this.revealedCells.add(key);
        const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
        cell.classList.add('revealed');
        
        if (this.board[row][col] === -1) {
            this.gameOver(false);
            return;
        }
        
        if (this.board[row][col] > 0) {
            cell.textContent = this.board[row][col];
            cell.dataset.number = this.board[row][col];
        } else {
            // 如果是空格，递归揭开周围的格子
            for (let i = -1; i <= 1; i++) {
                for (let j = -1; j <= 1; j++) {
                    this.revealCell(row + i, col + j);
                }
            }
        }
        
        this.checkWin();
    }

    toggleFlag(cell) {
        if (this.isGameOver || this.revealedCells.has(`${cell.dataset.row},${cell.dataset.col}`)) return;
        
        const key = `${cell.dataset.row},${cell.dataset.col}`;
        const minesLeft = document.getElementById('mines-left');
        
        if (this.flaggedCells.has(key)) {
            this.flaggedCells.delete(key);
            cell.classList.remove('flagged');
            cell.innerHTML = '';
            minesLeft.textContent = parseInt(minesLeft.textContent) + 1;
        } else {
            if (parseInt(minesLeft.textContent) > 0) {
                this.flaggedCells.add(key);
                cell.classList.add('flagged');
                cell.innerHTML = '<i class="fas fa-flag"></i>';
                minesLeft.textContent = parseInt(minesLeft.textContent) - 1;
            }
        }
    }

    gameOver(isWin) {
        this.isGameOver = true;
        clearInterval(this.timerInterval);
        
        // 显示所有地雷
        this.mineLocations.forEach(key => {
            const [row, col] = key.split(',').map(Number);
            const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
            if (!this.flaggedCells.has(key)) {
                cell.classList.add('mine');
                cell.innerHTML = '<i class="fas fa-bomb"></i>';
            }
        });
        
        setTimeout(() => {
            alert(isWin ? '恭喜你赢了！' : '游戏结束！');
        }, 100);
    }

    checkWin() {
        const { rows, cols, mines } = this.difficulties[this.currentDifficulty];
        const totalCells = rows * cols;
        
        if (this.revealedCells.size === totalCells - mines) {
            this.gameOver(true);
        }
    }
}

// 启动游戏
window.onload = () => {
    new Minesweeper();
};