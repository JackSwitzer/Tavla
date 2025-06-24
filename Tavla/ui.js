class TavlaUI {
    constructor(game) {
        this.game = game;
        this.selectedChecker = null;
        this.selectedFrom = null;
        this.validMoves = [];
        this.previousPlayer = 'white';
        
        // AI Integration
        this.aiPlayer = new AIPlayer(game, 'hard');
        this.pendingPlayerMove = null;
        this.gameStateBeforeMove = null;
        
        // Game statistics
        this.gameStartTime = Date.now();
        this.totalMoves = 0;
        this.playerMoves = 0;
        
        // Drag functionality
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        
        this.initializeUI();
        this.renderBoard();
        this.attachEventListeners();
        this.createFeedbackModal();
        this.createWinningModal();
        this.updateAnalysisSidebar();
        this.initializeDragFunctionality();
        this.loadSidebarPosition();
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
            undoButton: document.getElementById('undo-move'),
            // Analysis sidebar elements
            positionMeterFill: document.getElementById('position-meter-fill'),
            yourEV: document.getElementById('your-ev'),
            aiEV: document.getElementById('ai-ev'),
            pipLead: document.getElementById('pip-lead'),
            moveQuality: document.getElementById('move-quality'),
            moveDescription: document.getElementById('move-description'),
            bestMoveText: document.getElementById('best-move-text'),
            bestMoveReason: document.getElementById('best-move-reason')
        };
    }

    createFeedbackModal() {
        // Create feedback modal HTML
        const modalHTML = `
            <div id="feedback-modal" class="feedback-modal" style="display: none;">
                <div class="feedback-content">
                    <div class="feedback-header">
                        <h3>Move Analysis</h3>
                        <button class="feedback-close" id="feedback-close">&times;</button>
                    </div>
                    <div class="feedback-body">
                        <div id="feedback-message"></div>
                        <div class="feedback-stats" id="feedback-stats"></div>
                    </div>
                    <div class="feedback-footer">
                        <button id="feedback-ok" class="feedback-button">Got it!</button>
                        <button id="feedback-disable" class="feedback-button secondary">Disable hints</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Add event listeners for modal
        document.getElementById('feedback-close').addEventListener('click', () => this.hideFeedback());
        document.getElementById('feedback-ok').addEventListener('click', () => this.hideFeedback());
        document.getElementById('feedback-disable').addEventListener('click', () => this.toggleFeedback());
        
        // Close modal when clicking outside
        document.getElementById('feedback-modal').addEventListener('click', (e) => {
            if (e.target.id === 'feedback-modal') {
                this.hideFeedback();
            }
        });
        
        this.feedbackEnabled = true;
    }

    createWinningModal() {
        // Add event listeners for winning modal
        document.getElementById('play-again-btn').addEventListener('click', () => this.handleNewGame());
        document.getElementById('close-winning-btn').addEventListener('click', () => this.hideWinningScreen());
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
        if (this.game.dice.length > 0 || this.game.currentPlayer === 'black') return;

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
                    this.scheduleAIMove();
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
        // Store game state before move for analysis
        this.gameStateBeforeMove = this.game.exportGameState();
        this.pendingPlayerMove = { from, to };

        if (this.game.makeMove(from, to)) {
            this.clearSelection();
            this.renderBoard();
            this.updateMovesLeft();
            this.totalMoves++;
            
            // Analyze player move if it's a human player move
            if (this.gameStateBeforeMove.currentPlayer === 'white') {
                this.playerMoves++;
                this.analyzeAndShowFeedback();
            }
            
            // Update analysis sidebar
            this.updateAnalysisSidebar();
            
            if (this.game.gameOver) {
                this.showWinningScreen();
            } else if (this.game.dice.length === 0) {
                // Turn ended, check if AI should play
                this.endTurn();
                this.scheduleAIMove();
            } else {
                // Check if turn ended due to no valid moves
                if (this.game.currentPlayer !== this.previousPlayer) {
                    this.showMessage('No more valid moves. Turn ended.', 'info');
                    this.endTurn();
                    this.scheduleAIMove();
                }
            }
            
            this.previousPlayer = this.game.currentPlayer;
        } else {
            this.showMessage('Invalid move!', 'error');
        }
    }

    analyzeAndShowFeedback() {
        if (!this.pendingPlayerMove || !this.gameStateBeforeMove) {
            return;
        }

        const gameStateAfter = this.game.exportGameState();
        const feedback = this.aiPlayer.analyzePlayerMove(
            this.pendingPlayerMove,
            this.gameStateBeforeMove,
            gameStateAfter
        );

        if (feedback) {
            // Always update analysis sidebar
            this.updateLastMoveAnalysis(feedback);
            
            // Show feedback popup only for non-excellent moves
            if (feedback.category !== 'excellent' && feedback.category !== 'good') {
                setTimeout(() => this.showFeedback(feedback), 500);
            }
        }

        // Clear pending move data
        this.pendingPlayerMove = null;
        this.gameStateBeforeMove = null;
    }

    updateAnalysisSidebar() {
        // Get current position evaluation
        const whiteEval = this.game.evaluatePosition('white');
        const blackEval = this.game.evaluatePosition('black');
        
        // Update position meter (50% = even, left = you winning, right = AI winning)
        const positionAdvantage = whiteEval.totalEV - blackEval.totalEV;
        const meterPosition = 50 + (positionAdvantage * 100); // Scale for display
        const clampedPosition = Math.max(10, Math.min(90, meterPosition));
        
        this.elements.positionMeterFill.style.transform = `translateX(${clampedPosition - 50}%)`;
        
        // Update EV displays
        this.elements.yourEV.textContent = whiteEval.totalEV >= 0 ? 
            `+${whiteEval.totalEV.toFixed(3)}` : whiteEval.totalEV.toFixed(3);
        this.elements.aiEV.textContent = blackEval.totalEV >= 0 ? 
            `+${blackEval.totalEV.toFixed(3)}` : blackEval.totalEV.toFixed(3);
            
        // Update pip lead
        const pipCounts = this.game.calculatePipCount();
        const pipDiff = pipCounts.white - pipCounts.black;
        if (Math.abs(pipDiff) < 2) {
            this.elements.pipLead.textContent = 'Even';
        } else if (pipDiff > 0) {
            this.elements.pipLead.textContent = `AI +${pipDiff}`;
        } else {
            this.elements.pipLead.textContent = `You +${Math.abs(pipDiff)}`;
        }
    }

    updateLastMoveAnalysis(feedback) {
        // Update move quality indicator
        this.elements.moveQuality.textContent = feedback.category;
        this.elements.moveQuality.className = `move-quality ${feedback.category}`;
        
        // Update move description with cleaner text
        const moveDesc = `${feedback.feedbackMessage.split('.')[0]}. (Rank ${feedback.rank}/${feedback.totalMoves})`;
        this.elements.moveDescription.textContent = moveDesc;
            
        // Update best move display with improved clarity
        const bestMoveDesc = this.aiPlayer.describeBestMove(feedback.bestMove);
        this.elements.bestMoveText.textContent = `Optimal: ${bestMoveDesc}`;
        
        // Show why it's the best move with EV comparison
        if (feedback.evDifference > 0.01) {
            const evGain = (feedback.evDifference * 100).toFixed(1);
            this.elements.bestMoveReason.textContent = `+${evGain}% EV better than your move`;
        } else if (feedback.bestMove.benefits.length > 0) {
            const reasons = feedback.bestMove.benefits.map(b => {
                switch(b.type) {
                    case 'hit': return 'hits opponent blot';
                    case 'makePoint': return 'secures new point';
                    case 'homeAdvancement': return 'advances toward home';
                    default: return b.description;
                }
            }).join(', ');
            this.elements.bestMoveReason.textContent = `Strategic value: ${reasons}`;
        } else {
            this.elements.bestMoveReason.textContent = 'Your move was optimal!';
        }
    }

    describeBestMove(bestMoveAnalysis) {
        // Use the AI's improved description method
        return this.aiPlayer.describeBestMove(bestMoveAnalysis);
    }

    showFeedback(feedback) {
        const modal = document.getElementById('feedback-modal');
        const messageElement = document.getElementById('feedback-message');
        const statsElement = document.getElementById('feedback-stats');

        messageElement.innerHTML = feedback.feedbackMessage.replace(/\n/g, '<br>');
        
        // Add move statistics
        const statsHTML = `
            <div class="move-stats">
                <div class="stat-item">
                    <span class="stat-label">Your move rank:</span>
                    <span class="stat-value">${feedback.rank} of ${feedback.totalMoves}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Move quality:</span>
                    <span class="stat-value ${feedback.category}">${feedback.category.toUpperCase()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">EV difference:</span>
                    <span class="stat-value">${(feedback.evDifference * 100).toFixed(2)}%</span>
                </div>
            </div>
        `;
        
        statsElement.innerHTML = statsHTML;
        modal.style.display = 'flex';
    }

    hideFeedback() {
        document.getElementById('feedback-modal').style.display = 'none';
    }

    toggleFeedback() {
        this.feedbackEnabled = !this.feedbackEnabled;
        const button = document.getElementById('feedback-disable');
        button.textContent = this.feedbackEnabled ? 'Disable hints' : 'Enable hints';
        this.hideFeedback();
        
        this.showMessage(
            this.feedbackEnabled ? 'Move hints enabled' : 'Move hints disabled',
            'info'
        );
    }

    scheduleAIMove() {
        if (this.game.currentPlayer === 'black' && !this.game.gameOver) {
            // Add a delay to make AI moves feel more natural
            setTimeout(() => {
                this.makeAIMove();
            }, 1000 + Math.random() * 1000); // 1-2 second delay
        }
    }

    makeAIMove() {
        if (this.game.currentPlayer !== 'black' || this.game.gameOver) {
            return;
        }

        // AI needs dice to be rolled
        if (this.game.dice.length === 0) {
            const [die1, die2] = this.game.rollDice();
            this.elements.die1.textContent = die1;
            this.elements.die2.textContent = die2;
            this.updateMovesLeft();
            
            // Show AI thinking
            this.showMessage('AI is analyzing...', 'info');
        }

        // Get AI move
        const aiMove = this.aiPlayer.makeMove();
        if (aiMove) {
            // Animate AI move
            setTimeout(() => {
                this.highlightMove(aiMove);
                setTimeout(() => {
                    if (this.game.makeMove(aiMove.from, aiMove.to)) {
                        this.clearSelection();
                        this.renderBoard();
                        this.updateMovesLeft();
                        this.updateAnalysisSidebar();
                        this.totalMoves++;
                        
                        if (this.game.gameOver) {
                            this.showWinningScreen();
                        } else if (this.game.dice.length === 0) {
                            this.endTurn();
                        } else {
                            // AI might have more moves
                            this.scheduleAIMove();
                        }
                    }
                }, 1000);
            }, 500);
        } else {
            // No valid moves for AI
            this.showMessage('AI has no valid moves', 'info');
            this.game.endTurn();
            this.endTurn();
        }
    }

    highlightMove(move) {
        // Highlight the AI's move temporarily
        const fromElement = move.from === 'bar' 
            ? document.querySelector(`[data-position="bar-black"]`)
            : document.querySelector(`[data-position="${move.from}"]`);
            
        const toElement = move.to === 'home' 
            ? document.getElementById('home-black')
            : document.querySelector(`[data-position="${move.to}"]`);

        if (fromElement) fromElement.classList.add('ai-move-from');
        if (toElement) toElement.classList.add('ai-move-to');

        setTimeout(() => {
            if (fromElement) fromElement.classList.remove('ai-move-from');
            if (toElement) toElement.classList.remove('ai-move-to');
        }, 2000);
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
        
        // Only enable roll button for human player
        if (this.game.currentPlayer === 'white') {
            this.elements.rollButton.disabled = false;
        } else {
            this.elements.rollButton.disabled = true;
        }
        
        this.elements.die1.textContent = '?';
        this.elements.die2.textContent = '?';
        this.updateMovesLeft();
        this.renderBoard();
        this.showMessage('', '');
        this.updateAnalysisSidebar();
    }

    showMessage(message, type = 'info') {
        this.elements.messageArea.textContent = message;
        this.elements.messageArea.className = `message-area ${type}`;
    }

    showWinningScreen() {
        const winner = this.game.winner === 'white' ? 'You Win!' : 'AI Wins!';
        const gameDuration = this.formatDuration(Date.now() - this.gameStartTime);
        
        // Calculate performance stats
        const playerStats = this.aiPlayer.getPerformanceStats();
        const aiStats = this.aiPlayer.getPerformanceStats();
        
        const playerAvgEV = this.aiPlayer.playerMoveAnalysis.length > 0 ? 
            this.aiPlayer.playerMoveAnalysis.reduce((sum, analysis) => sum + analysis.playerMove.ev, 0) / 
            this.aiPlayer.playerMoveAnalysis.length : 0;
            
        const aiAvgEV = this.aiPlayer.moveHistory.length > 0 ?
            this.aiPlayer.moveHistory.reduce((sum, move) => sum + move.analysis.ev, 0) /
            this.aiPlayer.moveHistory.length : 0;

        // Update winning modal content
        document.getElementById('winner-text').textContent = winner;
        document.getElementById('game-duration').textContent = gameDuration;
        document.getElementById('total-moves').textContent = this.totalMoves.toString();
        document.getElementById('player-avg-ev').textContent = playerAvgEV >= 0 ? 
            `+${playerAvgEV.toFixed(3)}` : playerAvgEV.toFixed(3);
        document.getElementById('ai-avg-ev').textContent = aiAvgEV >= 0 ? 
            `+${aiAvgEV.toFixed(3)}` : aiAvgEV.toFixed(3);

        // Show the modal
        document.getElementById('winning-modal').style.display = 'flex';
    }

    hideWinningScreen() {
        document.getElementById('winning-modal').style.display = 'none';
    }

    formatDuration(ms) {
        const minutes = Math.floor(ms / 60000);
        const seconds = Math.floor((ms % 60000) / 1000);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    handleNewGame() {
        this.game.initializeGame();
        this.aiPlayer.reset();
        this.clearSelection();
        this.renderBoard();
        this.endTurn();
        this.showMessage('New game started! You play as white.', 'info');
        
        // Reset game statistics
        this.gameStartTime = Date.now();
        this.totalMoves = 0;
        this.playerMoves = 0;
        
        // Clear any pending move data
        this.pendingPlayerMove = null;
        this.gameStateBeforeMove = null;
        
        // Reset analysis sidebar
        this.resetAnalysisSidebar();
        
        // Hide winning screen if shown
        this.hideWinningScreen();
    }

    resetAnalysisSidebar() {
        this.elements.positionMeterFill.style.transform = 'translateX(0%)';
        this.elements.yourEV.textContent = '0.000';
        this.elements.aiEV.textContent = '0.000';
        this.elements.pipLead.textContent = 'Even';
        this.elements.moveQuality.textContent = '-';
        this.elements.moveQuality.className = 'move-quality';
        this.elements.moveDescription.textContent = 'Make your first move';
        this.elements.bestMoveText.textContent = 'Play to see analysis';
        this.elements.bestMoveReason.textContent = '';
        
        // Update initial position analysis
        this.updateAnalysisSidebar();
    }

    initializeDragFunctionality() {
        const sidebar = document.getElementById('analysis-sidebar');
        const dragHandle = document.getElementById('drag-handle');
        
        // Mouse events
        dragHandle.addEventListener('mousedown', (e) => this.startDrag(e));
        document.addEventListener('mousemove', (e) => this.handleDrag(e));
        document.addEventListener('mouseup', () => this.endDrag());
        
        // Touch events for mobile
        dragHandle.addEventListener('touchstart', (e) => this.startDrag(e.touches[0]), { passive: false });
        document.addEventListener('touchmove', (e) => this.handleDrag(e.touches[0]), { passive: false });
        document.addEventListener('touchend', () => this.endDrag());
        
        // Prevent default drag behavior
        dragHandle.addEventListener('dragstart', (e) => e.preventDefault());
    }

    startDrag(e) {
        this.isDragging = true;
        const sidebar = document.getElementById('analysis-sidebar');
        const rect = sidebar.getBoundingClientRect();
        
        this.dragOffset.x = e.clientX - rect.left;
        this.dragOffset.y = e.clientY - rect.top;
        
        sidebar.classList.add('dragging');
        document.body.style.userSelect = 'none';
        
        e.preventDefault();
    }

    handleDrag(e) {
        if (!this.isDragging) return;
        
        const sidebar = document.getElementById('analysis-sidebar');
        const newX = e.clientX - this.dragOffset.x;
        const newY = e.clientY - this.dragOffset.y;
        
        // Keep sidebar within viewport bounds
        const maxX = window.innerWidth - sidebar.offsetWidth;
        const maxY = window.innerHeight - sidebar.offsetHeight;
        
        const constrainedX = Math.max(0, Math.min(newX, maxX));
        const constrainedY = Math.max(0, Math.min(newY, maxY));
        
        sidebar.style.left = `${constrainedX}px`;
        sidebar.style.top = `${constrainedY}px`;
        
        e.preventDefault();
    }

    endDrag() {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        const sidebar = document.getElementById('analysis-sidebar');
        
        sidebar.classList.remove('dragging');
        document.body.style.userSelect = '';
        
        // Save position to localStorage
        this.saveSidebarPosition();
    }

    saveSidebarPosition() {
        const sidebar = document.getElementById('analysis-sidebar');
        const position = {
            left: sidebar.style.left,
            top: sidebar.style.top
        };
        localStorage.setItem('analysisPosition', JSON.stringify(position));
    }

    loadSidebarPosition() {
        const savedPosition = localStorage.getItem('analysisPosition');
        if (savedPosition) {
            const position = JSON.parse(savedPosition);
            const sidebar = document.getElementById('analysis-sidebar');
            
            // Validate position is still within viewport
            const maxX = window.innerWidth - sidebar.offsetWidth;
            const maxY = window.innerHeight - sidebar.offsetHeight;
            
            const x = Math.max(0, Math.min(parseInt(position.left), maxX));
            const y = Math.max(0, Math.min(parseInt(position.top), maxY));
            
            sidebar.style.left = `${x}px`;
            sidebar.style.top = `${y}px`;
        }
    }

    // Handle window resize to keep sidebar in bounds
    handleWindowResize() {
        const sidebar = document.getElementById('analysis-sidebar');
        const maxX = window.innerWidth - sidebar.offsetWidth;
        const maxY = window.innerHeight - sidebar.offsetHeight;
        
        const currentX = parseInt(sidebar.style.left) || 20;
        const currentY = parseInt(sidebar.style.top) || 20;
        
        const newX = Math.max(0, Math.min(currentX, maxX));
        const newY = Math.max(0, Math.min(currentY, maxY));
        
        sidebar.style.left = `${newX}px`;
        sidebar.style.top = `${newY}px`;
    }
}