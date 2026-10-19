class Game2048 {
    // ... 其他方法保持不变 ...

    createTileElement(x, y, value, isNew = true) {
        const tile = document.createElement('div');
        tile.classList.add('tile');
        if (isNew) {
            tile.classList.add('new');
        }
        tile.setAttribute('data-value', value);
        tile.setAttribute('data-x', x);
        tile.setAttribute('data-y', y);
        tile.textContent = value;
        
        const position = this.calculatePosition(x, y);
        tile.style.left = position.left + 'px';
        tile.style.top = position.top + 'px';
        
        document.querySelector('.grid-container').appendChild(tile);
        return tile;
    }

    async move(direction) {
        if (this.gameOver || this.isAnimating) return;
        this.isAnimating = true;

        const previousState = JSON.stringify(this.cells);
        const movements = []; // 记录移动轨迹

        // 根据方向重新排列数组
        let grid = this.cells;
        if (direction === 'right' || direction === 'down') {
            grid = grid.map(row => row.reverse());
        }
        if (direction === 'up' || direction === 'down') {
            grid = this.transpose(grid);
        }

        // 对每一行进行移动和合并
        grid = grid.map((row, i) => {
            const newRow = row.filter(cell => cell !== null);
            const originalRow = [...newRow];
            
            for (let j = 0; j < newRow.length - 1; j++) {
                if (newRow[j] === newRow[j + 1]) {
                    const value = newRow[j] * 2;
                    newRow[j] = value;
                    this.score += value;
                    newRow.splice(j + 1, 1);
                    
                    // 记录合并动作
                    movements.push({
                        from: { x: i, y: j + 1 },
                        to: { x: i, y: j },
                        value: value,
                        merged: true
                    });
                }
            }
            
            // 记录移动动作
            originalRow.forEach((value, j) => {
                if (value !== null) {
                    const newPos = newRow.indexOf(value);
                    if (newPos !== j) {
                        movements.push({
                            from: { x: i, y: j },
                            to: { x: i, y: newPos },
                            value: value,
                            merged: false
                        });
                    }
                }
            });

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

        // 如果有变化，执行动画
        if (previousState !== JSON.stringify(this.cells)) {
            await this.animateMovements(movements, direction);
            this.updateTiles();
            this.addNewTile();
            this.updateScore();
            
            if (!this.canMove()) {
                this.gameOver = true;
                document.querySelector('.game-message').classList.add('game-over');
                document.querySelector('.game-message p').textContent = '游戏结束！';
            }
        }

        this.isAnimating = false;
    }

    async animateMovements(movements, direction) {
        const tiles = document.querySelectorAll('.tile');
        const promises = [];

        movements.forEach(move => {
            const tile = Array.from(tiles).find(t => 
                parseInt(t.getAttribute('data-x')) === move.from.x &&
                parseInt(t.getAttribute('data-y')) === move.from.y &&
                parseInt(t.getAttribute('data-value')) === move.value
            );

            if (tile) {
                tile.classList.add('moving');
                if (move.merged) {
                    tile.classList.add('merged');
                }

                const position = this.calculatePosition(move.to.x, move.to.y);
                tile.style.left = position.left + 'px';
                tile.style.top = position.top + 'px';

                promises.push(new Promise(resolve => {
                    tile.addEventListener('transitionend', resolve, { once: true });
                }));
            }
        });

        await Promise.all(promises);
    }

    updateTiles() {
        const container = document.querySelector('.grid-container');
        const tiles = document.querySelectorAll('.tile');
        tiles.forEach(tile => tile.remove());

        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.cells[i][j]) {
                    this.createTileElement(i, j, this.cells[i][j], false);
                }
            }
        }
    }
}