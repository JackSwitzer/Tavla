class BackgammonGame {
    constructor() {
        if (window.game) {
            console.warn('Game instance already exists');
            return window.game;
        }
        
        this.initializeProperties();
        this.initializeGame();
        this.setupEventListeners();
    }

    initializeProperties() {
        // Clear any existing properties
        this.gameId = null;
        this.selectedPoint = null;
        this.currentPlayer = 'white';
        this.validMoves = [];
        this.gameState = null;
        this.dice = null;
        
        // Get DOM elements
        this.board = document.querySelector('.board');
        this.diceDisplay = document.getElementById('dice-display');
        this.gameStatus = document.getElementById('game-status');
        
        // Clear any existing highlights or selections
        document.querySelectorAll('.valid-move').forEach(el => {
            el.classList.remove('valid-move');
        });
        document.querySelectorAll('.checker').forEach(el => {
            el.style.backgroundColor = '';
        });
    }

    async initializeGame() {
        try {
            const existingGameId = sessionStorage.getItem('gameId');
            if (existingGameId) {
                // Try to fetch existing game state
                try {
                    const response = await fetch(`/api/game/${existingGameId}/state`);
                    if (response.ok) {
                        const data = await response.json();
                        this.gameId = existingGameId;
                        this.updateGameState(data.state);
                        return;
                    }
                } catch (error) {
                    console.warn('Failed to load existing game, creating new one');
                    sessionStorage.removeItem('gameId');
                }
            }
            
            // Create new game if no existing game or failed to load
            const response = await fetch('/api/game/new', {
                method: 'POST',
            });
            const data = await response.json();
            
            if (data.error) {
                this.updateStatus(`Error: ${data.error}`);
                return;
            }
            
            this.gameId = data.game_id;
            sessionStorage.setItem('gameId', this.gameId);
            this.updateGameState(data.state);
        } catch (error) {
            console.error('Error initializing game:', error);
            this.updateStatus('Error initializing game. Please refresh the page.');
        }
    }

    async updateGameState(state) {
        try {
            if (!state) {
                console.error('Invalid game state received');
                return;
            }
            
            this.gameState = state;
            this.currentPlayer = state.current_player;
            this.renderBoard(state.board);
            this.updateStatus(`Current player: ${this.currentPlayer}`);
            
            // Update dice display if present
            if (state.dice) {
                this.dice = state.dice;
                const [die1, die2] = this.dice;
                
                const dieElement1 = document.getElementById('die-1');
                const dieElement2 = document.getElementById('die-2');
                
                if (dieElement1 && dieElement2) {
                    dieElement1.textContent = die1;
                    dieElement2.textContent = die2;
                }
            }
            
            // Check for game over
            if (state.game_over) {
                this.handleGameOver();
            }
        } catch (error) {
            console.error('Error updating game state:', error);
            this.updateStatus('Error updating game state');
        }
    }

    renderBoard(boardState) {
        // Clear existing pieces
        document.querySelectorAll('.piece-spots').forEach(spot => {
            spot.innerHTML = '';
        });
        
        // Render checkers for each point
        for (let i = 0; i < 24; i++) {
            const count = boardState[i];
            if (count !== 0) {  // Only render if pieces exist
                const pointElement = document.querySelector(`[data-point="${i + 1}"]`);
                if (!pointElement) {
                    console.error(`Point element ${i + 1} not found`);
                    continue;
                }
                
                const pieceSpots = pointElement.querySelector('.piece-spots');
                if (!pieceSpots) {
                    console.error(`Piece spots not found for point ${i + 1}`);
                    continue;
                }

                const isWhite = count > 0;
                const absCount = Math.abs(count);
                
                // Limit visible checkers and add count indicator if needed
                const visibleCount = Math.min(absCount, 5);
                for (let j = 0; j < visibleCount; j++) {
                    const checker = document.createElement('div');
                    checker.className = `checker ${isWhite ? 'white' : 'black'}`;
                    checker.dataset.pointIndex = i + 1;
                    
                    // Add count indicator on top checker if there are more than visible
                    if (j === 0 && absCount > 5) {
                        checker.setAttribute('data-count', absCount.toString());
                    }
                    
                    pieceSpots.appendChild(checker);
                }
            }
        }

        // Render bar pieces
        this.renderBarPieces(this.gameState.bar);
    }

    renderBarPieces(barState) {
        const barTop = document.querySelector('.bar-top .piece-spots');
        const barBottom = document.querySelector('.bar-bottom .piece-spots');
        
        if (barState.black > 0) {
            for (let i = 0; i < Math.min(barState.black, 5); i++) {
                const checker = document.createElement('div');
                checker.className = 'checker black';
                if (i === 0 && barState.black > 5) {
                    checker.setAttribute('data-count', barState.black.toString());
                }
                barTop.appendChild(checker);
            }
        }
        
        if (barState.white > 0) {
            for (let i = 0; i < Math.min(barState.white, 5); i++) {
                const checker = document.createElement('div');
                checker.className = 'checker white';
                if (i === 0 && barState.white > 5) {
                    checker.setAttribute('data-count', barState.white.toString());
                }
                barBottom.appendChild(checker);
            }
        }
    }

    setupEventListeners() {
        // Bind the click handler
        this._boundClickHandler = this.handleBoardClick.bind(this);
        this.board.addEventListener('click', this._boundClickHandler);
        
        // Set up dice roller with proper binding
        const rollButton = document.getElementById('roll-dice');
        if (rollButton) {
            this._boundRollDice = this.rollDice.bind(this);
            rollButton.addEventListener('click', this._boundRollDice);
        }
        
        // Set up refresh button with proper binding
        const refreshButton = document.getElementById('refresh-game');
        if (refreshButton) {
            this._boundRefreshGame = this.refreshGame.bind(this);
            refreshButton.addEventListener('click', this._boundRefreshGame);
        }
    }

    async makeMove(fromPoint, toPoint) {
        try {
            const response = await fetch(`/api/game/${this.gameId}/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from: fromPoint,
                    to: toPoint,
                    color: this.currentPlayer
                })
            });
            const data = await response.json();
            
            if (data.error) {
                this.updateStatus(`Invalid move: ${data.error}`);
                return false;
            }
            
            this.updateGameState(data.state);
            return true;
        } catch (error) {
            console.error('Error making move:', error);
            this.updateStatus('Error making move');
            return false;
        }
    }

    async requestAiMove() {
        if (this.currentPlayer === 'black') {
            try {
                const response = await fetch(`/api/game/${this.gameId}/ai-move`, {
                    method: 'POST'
                });
                const data = await response.json();
                this.updateGameState(data.state);
            } catch (error) {
                console.error('Error making AI move:', error);
                this.updateStatus('Error making AI move');
            }
        }
    }

    updateStatus(message) {
        this.gameStatus.textContent = message;
    }

    async rollDice() {
        try {
            const response = await fetch(`/api/game/${this.gameId}/roll`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            if (data.error) {
                this.updateStatus(`Error: ${data.error}`);
                return;
            }

            // Update game state first
            this.updateGameState(data.state);
            
            // Then handle dice animation separately
            const [die1, die2] = this.dice;
            const dieElement1 = document.getElementById('die-1');
            const dieElement2 = document.getElementById('die-2');
            
            if (dieElement1 && dieElement2) {
                // Add animation
                dieElement1.classList.add('rolling');
                dieElement2.classList.add('rolling');
                
                // Update values after a brief delay
                setTimeout(() => {
                    dieElement1.textContent = die1;
                    dieElement2.textContent = die2;
                    dieElement1.classList.remove('rolling');
                    dieElement2.classList.remove('rolling');
                }, 500);
            }
            
            // Get valid moves after rolling
            await this.getValidMoves();
        } catch (error) {
            console.error('Error rolling dice:', error);
            this.updateStatus('Error rolling dice');
        }
    }

    async getValidMoves() {
        try {
            const response = await fetch(`/api/game/${this.gameId}/valid-moves`);
            const data = await response.json();
            
            if (data.error) {
                this.updateStatus(`Error: ${data.error}`);
                return;
            }

            this.validMoves = data.valid_moves;
            this.highlightValidMoves();
        } catch (error) {
            console.error('Error getting valid moves:', error);
        }
    }

    highlightValidMoves() {
        // Remove previous highlights
        document.querySelectorAll('.valid-move').forEach(el => {
            el.classList.remove('valid-move');
        });

        // Add highlights to valid moves
        this.validMoves.forEach(move => {
            const point = document.querySelector(`[data-point-index="${move.to}"]`);
            if (point) {
                point.classList.add('valid-move');
            }
        });
    }

    async refreshGame() {
        try {
            // Call the refresh endpoint with current game ID
            const response = await fetch(`/api/game/${this.gameId}/refresh`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.error) {
                this.updateStatus(`Error: ${data.error}`);
                return;
            }
            
            // Clean up current game state
            this.cleanup();
            
            // Update session storage with new game ID
            this.gameId = data.game_id;
            sessionStorage.setItem('gameId', this.gameId);
            
            // Reset properties and update state
            this.initializeProperties();
            this.updateGameState(data.state);
            this.setupEventListeners();  // Re-attach event listeners
            
            this.updateStatus('Game refreshed. White to play.');
        } catch (error) {
            console.error('Error refreshing game:', error);
            this.updateStatus('Error refreshing game');
        }
    }

    cleanup() {
        // Clear all game state
        this.validMoves = [];
        this.selectedPoint = null;
        this.dice = null;
        this.diceDisplay.textContent = 'Dice: ';
        
        // Clear visual state
        this.board.querySelectorAll('.piece-spots').forEach(spot => {
            spot.innerHTML = '';
        });
        
        // Clear dice display
        const dieElement1 = document.getElementById('die-1');
        const dieElement2 = document.getElementById('die-2');
        if (dieElement1) dieElement1.textContent = '';
        if (dieElement2) dieElement2.textContent = '';
        
        // Remove all event listeners
        this.removeEventListeners();
    }

    removeEventListeners() {
        if (this._boundClickHandler) {
            this.board.removeEventListener('click', this._boundClickHandler);
        }
        
        const rollButton = document.getElementById('roll-dice');
        const refreshButton = document.getElementById('refresh-game');
        
        if (rollButton && this._boundRollDice) {
            rollButton.removeEventListener('click', this._boundRollDice);
        }
        if (refreshButton && this._boundRefreshGame) {
            refreshButton.removeEventListener('click', this._boundRefreshGame);
        }
    }

    async handleBoardClick(event) {
        // Find the clicked checker or point
        const checker = event.target.closest('.checker');
        const point = event.target.closest('[data-point]');
        
        if (!checker && !point) return;
        
        // If no dice roll, ignore clicks
        if (!this.dice) {
            this.updateStatus('Roll dice first!');
            return;
        }
        
        // Handle checker selection
        if (checker) {
            const pointIndex = parseInt(checker.closest('[data-point]').dataset.point);
            const checkerColor = checker.classList.contains('white') ? 'white' : 'black';
            
            // Only allow selection of current player's pieces
            if (checkerColor !== this.currentPlayer) {
                this.updateStatus(`It's ${this.currentPlayer}'s turn`);
                return;
            }
            
            this.selectedPoint = pointIndex;
            // Highlight selected checker
            document.querySelectorAll('.checker').forEach(c => c.style.backgroundColor = '');
            checker.style.backgroundColor = 'rgba(255, 255, 0, 0.5)';
            
            // Get and show valid moves
            await this.getValidMoves();
            return;
        }
        
        // Handle point selection (for move destination)
        if (point && this.selectedPoint !== null) {
            const toPoint = parseInt(point.dataset.point);
            
            // Attempt to make the move
            const success = await this.makeMove(this.selectedPoint, toPoint);
            if (success) {
                // Clear selection and highlights
                this.selectedPoint = null;
                document.querySelectorAll('.checker').forEach(c => c.style.backgroundColor = '');
                document.querySelectorAll('.valid-move').forEach(el => el.classList.remove('valid-move'));
                
                // Request AI move if it's black's turn
                await this.requestAiMove();
            }
        }
    }

    handleGameOver() {
        this.updateStatus(`Game Over! ${this.currentPlayer} wins!`);
        // Disable further moves
        this.board.removeEventListener('click', this._boundClickHandler);
    }
}

// Initialize game when page loads - with singleton pattern
document.addEventListener('DOMContentLoaded', () => {
    if (!window.game) {
        window.game = new BackgammonGame();
    }
});