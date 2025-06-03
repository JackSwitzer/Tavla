class TavlaUI {
    constructor(game) {
        this.game = game;
        this.selectedChecker = null;
        this.selectedFrom = null;
        this.validMoves = [];
        this.previousPlayer = 'white';
        
        this.initializeUI();
        this.renderBoard();
        this.attachEventListeners();
    }

    initializeUI() {
        this.elements = {
            die1: document.getElementById('die1'),
            die2: document.getElementById('die2'),
            rollButton: document.getElementById('roll-dice'),
            movesLeft: document.getElementById('moves-left'),
            messageArea: document.getElementById('message-area'),
            currentPlayer: document.getElementById('current-player'),
            player1Pips: document.getElementById('player1-pips'),
            player2Pips: document.getElementById('player2-pips'),
            newGameButton: document.getElementById('new-game'),
            undoButton: document.getElementById('undo-move')
        };
    }

    renderBoard() {
        // Clear all checkers first
        document.querySelectorAll('.checker').forEach(checker => checker.remove());

        // Render checkers on points
        for (let i = 1; i <= 24; i++) {
            const point = this.game.board[i];
            if (point && point.count > 0) {
                this.renderCheckersOnPoint(i.toString(), point.color, point.count);
            }
        }

        // Render bar checkers
        this.renderCheckersOnBar();

        // Render home checkers
        this.renderCheckersInHome();

        // Update pip counts
        this.updatePipCounts();

        // Update current player indicator
        this.updateTurnIndicator();
    }

    renderCheckersOnPoint(position, color, count) {
        const pointElement = document.querySelector(`[data-position="${position}"]`);
        if (!pointElement) return;

        let stackElement = pointElement.querySelector('.checker-stack');
        if (!stackElement) {
            stackElement = document.createElement('div');
            stackElement.className = 'checker-stack';
            pointElement.appendChild(stackElement);
        }

        stackElement.innerHTML = '';

        const maxVisible = 5;
        const overlapPixels = count > maxVisible ? 200 / count : 40;

        for (let i = 0; i < count; i++) {
            const checker = document.createElement('div');
            checker.className = `checker ${color}`;
            checker.dataset.position = position;
            checker.dataset.index = i;

            if (parseInt(position) >= 13) {
                checker.style.top = `${i * overlapPixels}px`;
            } else {
                checker.style.bottom = `${i * overlapPixels}px`;
            }

            if (count > maxVisible && i > 0 && i < count - 1) {
                checker.style.opacity = '0.8';
            }

            stackElement.appendChild(checker);
        }

        // Add count indicator for large stacks
        if (count > maxVisible) {
            const countIndicator = document.createElement('div');
            countIndicator.className = 'checker-count';
            countIndicator.textContent = count;
            stackElement.appendChild(countIndicator);
        }
    }

    renderCheckersOnBar() {
        // White bar
        const whiteBarElement = document.querySelector('[data-position="bar-white"]');
        if (whiteBarElement) {
            whiteBarElement.innerHTML = '';
            for (let i = 0; i < this.game.bar.white; i++) {
                const checker = document.createElement('div');
                checker.className = 'checker white';
                checker.dataset.position = 'bar';
                checker.style.position = 'relative';
                checker.style.marginTop = i > 0 ? '-30px' : '0';
                whiteBarElement.appendChild(checker);
            }
        }

        // Black bar
        const blackBarElement = document.querySelector('[data-position="bar-black"]');
        if (blackBarElement) {
            blackBarElement.innerHTML = '';
            for (let i = 0; i < this.game.bar.black; i++) {
                const checker = document.createElement('div');
                checker.className = 'checker black';
                checker.dataset.position = 'bar';
                checker.style.position = 'relative';
                checker.style.marginTop = i > 0 ? '-30px' : '0';
                blackBarElement.appendChild(checker);
            }
        }
    }

    renderCheckersInHome() {
        // White home
        const whiteHomeElement = document.querySelector('[data-position="home-white"]');
        if (whiteHomeElement) {
            whiteHomeElement.innerHTML = '';
            if (this.game.home.white > 0) {
                const stack = document.createElement('div');
                stack.className = 'home-stack';
                stack.innerHTML = `<div class="checker white"></div><span class="home-count">${this.game.home.white}</span>`;
                whiteHomeElement.appendChild(stack);
            }
        }

        // Black home
        const blackHomeElement = document.querySelector('[data-position="home-black"]');
        if (blackHomeElement) {
            blackHomeElement.innerHTML = '';
            if (this.game.home.black > 0) {
                const stack = document.createElement('div');
                stack.className = 'home-stack';
                stack.innerHTML = `<div class="checker black"></div><span class="home-count">${this.game.home.black}</span>`;
                blackHomeElement.appendChild(stack);
            }
        }
    }

    updatePipCounts() {
        const pipCounts = this.game.calculatePipCount();
        this.elements.player1Pips.textContent = pipCounts.white;
        this.elements.player2Pips.textContent = pipCounts.black;
    }

    updateTurnIndicator() {
        const playerName = this.game.currentPlayer === 'white' ? 'Player 1' : 'Player 2';
        this.elements.currentPlayer.textContent = `${playerName}'s Turn`;
        
        // Update player info highlighting
        document.getElementById('player1-info').classList.toggle('active', this.game.currentPlayer === 'white');
        document.getElementById('player2-info').classList.toggle('active', this.game.currentPlayer === 'black');
    }

    attachEventListeners() {
        // Roll dice button
        this.elements.rollButton.addEventListener('click', () => this.handleRollDice());

        // New game button
        this.elements.newGameButton.addEventListener('click', () => this.handleNewGame());

        // Board click handlers
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('checker')) {
                this.handleCheckerClick(e.target);
            } else if (e.target.closest('.point')) {
                this.handlePointClick(e.target.closest('.point'));
            } else if (e.target.closest('.home')) {
                this.handleHomeClick();
            }
        });
    }

    handleRollDice() {
        if (this.game.dice.length > 0) return;

        const [die1, die2] = this.game.rollDice();
        
        // Animate dice
        this.elements.die1.classList.add('rolling');
        this.elements.die2.classList.add('rolling');
        
        setTimeout(() => {
            this.elements.die1.classList.remove('rolling');
            this.elements.die2.classList.remove('rolling');
            this.elements.die1.textContent = die1;
            this.elements.die2.textContent = die2;
            
            this.updateMovesLeft();
            this.elements.rollButton.disabled = true;
            
            // Check if player has any valid moves
            const possibleMoves = this.game.getPossibleMoves();
            if (possibleMoves.length === 0) {
                this.showMessage('No valid moves available. Turn will end.', 'info');
                setTimeout(() => {
                    this.game.endTurn();
                    this.endTurn();
                }, 2000);
            }
        }, 500);
    }

    handleCheckerClick(checker) {
        const position = checker.dataset.position;
        const isCurrentPlayerChecker = checker.classList.contains(this.game.currentPlayer);

        if (!isCurrentPlayerChecker || this.game.dice.length === 0) {
            console.log('Cannot select checker:', { isCurrentPlayerChecker, diceLength: this.game.dice.length });
            return;
        }

        // Handle bar checkers
        if (position === 'bar' && this.game.bar[this.game.currentPlayer] > 0) {
            this.selectChecker(checker, 'bar');
            return;
        }

        // Regular checker selection
        if (position !== 'bar') {
            this.selectChecker(checker, position);
        }
    }

    handlePointClick(pointElement) {
        const position = pointElement.dataset.position;
        
        if (this.selectedChecker && this.validMoves.includes(position)) {
            this.makeMove(this.selectedFrom, position);
        } else {
            // Check if clicking on own checker
            const point = this.game.board[parseInt(position)];
            if (point && point.color === this.game.currentPlayer && this.game.dice.length > 0) {
                const checker = pointElement.querySelector('.checker:last-child');
                if (checker) {
                    this.handleCheckerClick(checker);
                }
            }
        }
    }

    handleHomeClick() {
        if (this.selectedChecker && this.validMoves.includes('home')) {
            this.makeMove(this.selectedFrom, 'home');
        }
    }

    selectChecker(checker, position) {
        // Clear previous selection
        document.querySelectorAll('.checker.selected').forEach(c => c.classList.remove('selected'));
        document.querySelectorAll('.point.selected').forEach(p => p.classList.remove('selected'));
        document.querySelectorAll('.point.valid-move').forEach(p => p.classList.remove('valid-move'));
        document.querySelectorAll('.home.valid-move').forEach(h => h.classList.remove('valid-move'));
        document.querySelectorAll('.bar-section.valid-move').forEach(b => b.classList.remove('valid-move'));

        // Select new checker
        checker.classList.add('selected');
        if (position !== 'bar') {
            const pointElement = checker.closest('.point');
            if (pointElement) {
                pointElement.classList.add('selected');
            }
        }

        this.selectedChecker = checker;
        this.selectedFrom = position;

        // Show valid moves
        this.showValidMoves(position);
        console.log('Selected checker from position:', position);
    }

    showValidMoves(from) {
        this.validMoves = [];
        const possibleMoves = this.game.getPossibleMoves();
        console.log('Possible moves from', from, ':', possibleMoves);
        
        possibleMoves.forEach(move => {
            if (move.from === from) {
                this.validMoves.push(move.to);
                
                if (move.to === 'home') {
                    const homeElement = document.getElementById(`home-${this.game.currentPlayer}`);
                    if (homeElement) {
                        homeElement.classList.add('valid-move');
                        console.log('Highlighted home as valid move');
                    }
                } else {
                    const pointElement = document.querySelector(`[data-position="${move.to}"]`);
                    if (pointElement) {
                        pointElement.classList.add('valid-move');
                        console.log('Highlighted point', move.to, 'as valid move');
                    }
                }
            }
        });
        
        console.log('Valid moves for position', from, ':', this.validMoves);
    }

    makeMove(from, to) {
        if (this.game.makeMove(from, to)) {
            this.clearSelection();
            this.renderBoard();
            this.updateMovesLeft();
            
            if (this.game.gameOver) {
                this.showGameOver();
            } else if (this.game.dice.length === 0) {
                // Turn already ended in game engine
                this.endTurn();
            } else {
                // The game engine already checked for valid moves
                // If turn was ended, update UI accordingly
                if (this.game.currentPlayer !== this.previousPlayer) {
                    this.showMessage('No more valid moves. Turn ended.', 'info');
                    this.endTurn();
                }
            }
            
            // Track the current player for next move
            this.previousPlayer = this.game.currentPlayer;
        } else {
            this.showMessage('Invalid move!', 'error');
        }
    }

    clearSelection() {
        document.querySelectorAll('.checker.selected').forEach(c => c.classList.remove('selected'));
        document.querySelectorAll('.point.selected').forEach(p => p.classList.remove('selected'));
        document.querySelectorAll('.point.valid-move').forEach(p => p.classList.remove('valid-move'));
        document.querySelectorAll('.home.valid-move').forEach(h => h.classList.remove('valid-move'));
        document.querySelectorAll('.bar-section.valid-move').forEach(b => b.classList.remove('valid-move'));
        
        this.selectedChecker = null;
        this.selectedFrom = null;
        this.validMoves = [];
    }

    updateMovesLeft() {
        if (this.game.dice.length > 0) {
            this.elements.movesLeft.textContent = `Moves left: ${this.game.dice.join(', ')}`;
        } else {
            this.elements.movesLeft.textContent = '';
        }
    }

    endTurn() {
        this.clearSelection();
        this.elements.rollButton.disabled = false;
        this.elements.die1.textContent = '?';
        this.elements.die2.textContent = '?';
        this.updateMovesLeft();
        this.renderBoard();
        this.showMessage('', '');
    }

    showMessage(message, type = 'info') {
        this.elements.messageArea.textContent = message;
        this.elements.messageArea.className = `message-area ${type}`;
    }

    showGameOver() {
        const winner = this.game.winner === 'white' ? 'Player 1' : 'Player 2';
        this.showMessage(`Game Over! ${winner} wins!`, 'success');
        this.elements.rollButton.disabled = true;
    }

    handleNewGame() {
        this.game.initializeGame();
        this.clearSelection();
        this.renderBoard();
        this.endTurn();
        this.showMessage('New game started!', 'info');
    }
}