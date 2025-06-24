class TavlaGame {
    constructor() {
        this.initializeGame();
    }

    initializeGame() {
        // Turkish Tavla starting position
        this.board = new Array(25).fill(null).map(() => ({ color: null, count: 0 }));
        
        // Set up initial checker positions (Turkish Tavla setup)
        // White pieces (moving counter-clockwise from 24 to 1)
        this.board[24] = { color: 'white', count: 2 };
        this.board[13] = { color: 'white', count: 5 };
        this.board[8] = { color: 'white', count: 3 };
        this.board[6] = { color: 'white', count: 5 };
        
        // Black pieces (moving clockwise from 1 to 24)
        this.board[1] = { color: 'black', count: 2 };
        this.board[12] = { color: 'black', count: 5 };
        this.board[17] = { color: 'black', count: 3 };
        this.board[19] = { color: 'black', count: 5 };

        // Bar and home
        this.bar = { white: 0, black: 0 };
        this.home = { white: 0, black: 0 };

        // Game state
        this.currentPlayer = 'white';
        this.dice = [];
        this.availableMoves = [];
        this.moveHistory = [];
        this.gameOver = false;
        this.winner = null;

        // Track if player has moved (for doubles)
        this.movesThisTurn = [];
    }

    rollDice() {
        const die1 = Math.floor(Math.random() * 6) + 1;
        const die2 = Math.floor(Math.random() * 6) + 1;
        
        if (die1 === die2) {
            // Doubles - player gets 4 moves
            this.dice = [die1, die1, die1, die1];
        } else {
            this.dice = [die1, die2];
        }
        
        this.movesThisTurn = [];
        return [die1, die2];
    }

    isValidMove(from, to) {
        // Special handling for bar moves
        if (from === 'bar') {
            return this.isValidBarMove(to);
        }

        // Special handling for bearing off
        if (to === 'home') {
            return this.isValidBearOff(from);
        }

        // Regular move validation
        const fromPoint = parseInt(from);
        const toPoint = parseInt(to);

        // Check if move is in correct direction
        if (this.currentPlayer === 'white') {
            if (toPoint >= fromPoint) return false;
        } else {
            if (toPoint <= fromPoint) return false;
        }

        // Check if the move distance matches any available die
        const distance = Math.abs(toPoint - fromPoint);
        if (!this.dice.includes(distance)) return false;

        // Check if there's a checker to move
        if (!this.board[fromPoint] || this.board[fromPoint].color !== this.currentPlayer) {
            return false;
        }

        // Check if destination is valid
        const destPoint = this.board[toPoint];
        if (destPoint && destPoint.color !== this.currentPlayer && destPoint.count > 1) {
            return false; // Can't land on opponent's point with 2+ checkers
        }

        return true;
    }

    isValidBarMove(to) {
        if (this.bar[this.currentPlayer] === 0) return false;

        const toPoint = parseInt(to);
        
        // White enters on points 19-24 (using dice 1-6)
        // Black enters on points 1-6 (using dice 1-6)
        let dieNeeded;
        if (this.currentPlayer === 'white') {
            dieNeeded = 25 - toPoint; // Point 24 needs die 1, point 19 needs die 6
        } else {
            dieNeeded = toPoint; // Point 1 needs die 1, point 6 needs die 6
        }

        // Check if move matches dice
        if (!this.dice.includes(dieNeeded)) return false;

        // Check if destination is valid
        const destPoint = this.board[toPoint];
        if (destPoint && destPoint.color !== this.currentPlayer && destPoint.count > 1) {
            return false;
        }

        return true;
    }

    isValidBearOff(from) {
        // Check if all checkers are in home board
        if (!this.canBearOff()) return false;

        const fromPoint = parseInt(from);
        
        // Check if there's a checker to move
        if (!this.board[fromPoint] || this.board[fromPoint].color !== this.currentPlayer) {
            return false;
        }

        // Verify the point is in home board
        if (this.currentPlayer === 'white') {
            if (fromPoint < 1 || fromPoint > 6) return false;
        } else {
            if (fromPoint < 19 || fromPoint > 24) return false;
        }

        // Calculate distance to bear off
        const distance = this.currentPlayer === 'white' ? fromPoint : 25 - fromPoint;

        // Check each die
        for (const die of this.dice) {
            if (die === distance) {
                return true; // Exact match
            } else if (die > distance) {
                // Can use higher die if no checkers on higher points
                let hasHigherCheckers = false;
                
                if (this.currentPlayer === 'white') {
                    for (let i = fromPoint + 1; i <= 6; i++) {
                        if (this.board[i] && this.board[i].color === 'white' && this.board[i].count > 0) {
                            hasHigherCheckers = true;
                            break;
                        }
                    }
                } else {
                    // For black, "higher" points are lower numbers (moving toward 19)
                    for (let i = 19; i < fromPoint; i++) {
                        if (this.board[i] && this.board[i].color === 'black' && this.board[i].count > 0) {
                            hasHigherCheckers = true;
                            break;
                        }
                    }
                }
                
                if (!hasHigherCheckers) {
                    return true;
                }
            }
        }

        return false;
    }

    canBearOff() {
        // Check if player has checkers on bar
        if (this.bar[this.currentPlayer] > 0) return false;

        // Check if all checkers are in home board
        if (this.currentPlayer === 'white') {
            // White home board is 1-6, check no checkers on 7-24
            for (let i = 7; i <= 24; i++) {
                if (this.board[i] && this.board[i].color === 'white' && this.board[i].count > 0) {
                    return false;
                }
            }
        } else {
            // Black home board is 19-24, check no checkers on 1-18
            for (let i = 1; i <= 18; i++) {
                if (this.board[i] && this.board[i].color === 'black' && this.board[i].count > 0) {
                    return false;
                }
            }
        }

        return true;
    }

    makeMove(from, to) {
        if (!this.isValidMove(from, to)) return false;

        // Handle bar moves
        if (from === 'bar') {
            this.bar[this.currentPlayer]--;
            const toPoint = parseInt(to);
            
            // Hit opponent's blot
            if (this.board[toPoint] && this.board[toPoint].color !== this.currentPlayer && this.board[toPoint].count === 1) {
                this.bar[this.board[toPoint].color]++;
                this.board[toPoint] = { color: this.currentPlayer, count: 1 };
            } else {
                if (!this.board[toPoint] || this.board[toPoint].count === 0) {
                    this.board[toPoint] = { color: this.currentPlayer, count: 1 };
                } else {
                    this.board[toPoint].count++;
                }
            }
            
            // Remove used die
            const targetPoint = this.currentPlayer === 'white' ? 25 - toPoint : toPoint;
            const dieIndex = this.dice.indexOf(targetPoint);
            this.dice.splice(dieIndex, 1);
        }
        // Handle bearing off
        else if (to === 'home') {
            const fromPoint = parseInt(from);
            this.board[fromPoint].count--;
            if (this.board[fromPoint].count === 0) {
                this.board[fromPoint] = { color: null, count: 0 };
            }
            this.home[this.currentPlayer]++;
            
            // Remove used die
            const distance = this.currentPlayer === 'white' ? fromPoint : 25 - fromPoint;
            let dieIndex = this.dice.indexOf(distance);
            if (dieIndex === -1) {
                // Using a higher die
                const higherDie = Math.max(...this.dice);
                dieIndex = this.dice.indexOf(higherDie);
            }
            this.dice.splice(dieIndex, 1);
        }
        // Regular moves
        else {
            const fromPoint = parseInt(from);
            const toPoint = parseInt(to);
            
            // Remove checker from source
            this.board[fromPoint].count--;
            if (this.board[fromPoint].count === 0) {
                this.board[fromPoint] = { color: null, count: 0 };
            }
            
            // Hit opponent's blot
            if (this.board[toPoint] && this.board[toPoint].color !== this.currentPlayer && this.board[toPoint].count === 1) {
                this.bar[this.board[toPoint].color]++;
                this.board[toPoint] = { color: this.currentPlayer, count: 1 };
            } else {
                // Add checker to destination
                if (!this.board[toPoint] || this.board[toPoint].count === 0) {
                    this.board[toPoint] = { color: this.currentPlayer, count: 1 };
                } else {
                    this.board[toPoint].count++;
                }
            }
            
            // Remove used die
            const distance = Math.abs(toPoint - fromPoint);
            const dieIndex = this.dice.indexOf(distance);
            this.dice.splice(dieIndex, 1);
        }

        // Record move
        this.movesThisTurn.push({ from, to });
        this.moveHistory.push({
            player: this.currentPlayer,
            from,
            to,
            boardState: this.cloneBoardState()
        });

        // Check for game over
        if (this.home[this.currentPlayer] === 15) {
            this.gameOver = true;
            this.winner = this.currentPlayer;
        }

        // Check if there are any valid moves left with remaining dice
        if (this.dice.length > 0) {
            const possibleMoves = this.getPossibleMoves();
            if (possibleMoves.length === 0) {
                // No valid moves available, end turn
                this.endTurn();
            }
        } else {
            // No dice left, end turn
            this.endTurn();
        }

        return true;
    }

    endTurn() {
        this.currentPlayer = this.currentPlayer === 'white' ? 'black' : 'white';
        this.dice = [];
        this.movesThisTurn = [];
    }

    getPossibleMoves() {
        const moves = [];
        
        // Must enter from bar first
        if (this.bar[this.currentPlayer] > 0) {
            for (const die of this.dice) {
                const targetPoint = this.currentPlayer === 'white' ? 25 - die : die;
                if (this.isValidMove('bar', targetPoint.toString())) {
                    moves.push({ from: 'bar', to: targetPoint.toString(), die });
                }
            }
            return moves; // Can only enter from bar
        }

        // Check bearing off - MUST recheck canBearOff() each time since checkers may have moved
        if (this.canBearOff()) {
            const homeStart = this.currentPlayer === 'white' ? 1 : 19;
            const homeEnd = this.currentPlayer === 'white' ? 6 : 24;
            
            // Check all home board points
            if (this.currentPlayer === 'white') {
                for (let i = 1; i <= 6; i++) {
                    if (this.board[i] && this.board[i].color === 'white' && this.board[i].count > 0) {
                        // Check each unique die value
                        for (const die of [...new Set(this.dice)]) {
                            if (die === i) {
                                // Exact match
                                moves.push({ from: i.toString(), to: 'home', die });
                            } else if (die > i) {
                                // Can use higher die if no checkers on higher points
                                let canUseHigher = true;
                                for (let j = i + 1; j <= 6; j++) {
                                    if (this.board[j] && this.board[j].color === 'white' && this.board[j].count > 0) {
                                        canUseHigher = false;
                                        break;
                                    }
                                }
                                if (canUseHigher) {
                                    moves.push({ from: i.toString(), to: 'home', die });
                                }
                            }
                        }
                    }
                }
            } else {
                // Black player
                for (let i = 19; i <= 24; i++) {
                    if (this.board[i] && this.board[i].color === 'black' && this.board[i].count > 0) {
                        // Check each unique die value
                        for (const die of [...new Set(this.dice)]) {
                            const distance = 25 - i;
                            if (die === distance) {
                                // Exact match
                                moves.push({ from: i.toString(), to: 'home', die });
                            } else if (die > distance) {
                                // Can use higher die if no checkers on higher points
                                let canUseHigher = true;
                                for (let j = 19; j < i; j++) {
                                    if (this.board[j] && this.board[j].color === 'black' && this.board[j].count > 0) {
                                        canUseHigher = false;
                                        break;
                                    }
                                }
                                if (canUseHigher) {
                                    moves.push({ from: i.toString(), to: 'home', die });
                                }
                            }
                        }
                    }
                }
            }
        }

        // Regular moves
        for (let i = 1; i <= 24; i++) {
            if (this.board[i] && this.board[i].color === this.currentPlayer && this.board[i].count > 0) {
                for (const die of [...new Set(this.dice)]) { // Use Set to avoid duplicate moves for doubles
                    const targetPoint = this.currentPlayer === 'white' ? i - die : i + die;
                    if (targetPoint >= 1 && targetPoint <= 24) {
                        if (this.isValidMove(i.toString(), targetPoint.toString())) {
                            moves.push({ from: i.toString(), to: targetPoint.toString(), die });
                        }
                    }
                }
            }
        }

        return moves;
    }

    undoLastMove() {
        if (this.moveHistory.length === 0) return false;
        
        // TODO: Implement undo functionality
        // This would restore the previous board state
        return false;
    }

    cloneBoardState() {
        return {
            board: this.board.map(point => ({ ...point })),
            bar: { ...this.bar },
            home: { ...this.home },
            dice: [...this.dice]
        };
    }

    calculatePipCount() {
        const pipCount = { white: 0, black: 0 };
        
        // Count pips on board
        for (let i = 1; i <= 24; i++) {
            if (this.board[i] && this.board[i].count > 0) {
                const color = this.board[i].color;
                const distance = color === 'white' ? i : 25 - i;
                pipCount[color] += this.board[i].count * distance;
            }
        }
        
        // Count pips on bar
        pipCount.white += this.bar.white * 25;
        pipCount.black += this.bar.black * 25;
        
        return pipCount;
    }

    exportGameState() {
        return {
            board: this.board.map(point => ({ ...point })),
            bar: { ...this.bar },
            home: { ...this.home },
            currentPlayer: this.currentPlayer,
            dice: [...this.dice],
            moveHistory: this.moveHistory.map(move => ({ ...move })),
            gameOver: this.gameOver,
            winner: this.winner
        };
    }

    importGameState(state) {
        this.board = state.board.map(point => ({ ...point }));
        this.bar = { ...state.bar };
        this.home = { ...state.home };
        this.currentPlayer = state.currentPlayer;
        this.dice = [...state.dice];
        this.moveHistory = state.moveHistory.map(move => ({ ...move }));
        this.gameOver = state.gameOver;
        this.winner = state.winner;
    }

    // Position Evaluation System for EV Analysis
    evaluatePosition(player = this.currentPlayer) {
        const evaluation = {
            pipCount: this.calculatePipCount()[player],
            opponentPipCount: this.calculatePipCount()[player === 'white' ? 'black' : 'white'],
            blotCount: this.countBlots(player),
            blockadeStrength: this.calculateBlockadeStrength(player),
            homeAdvancement: this.calculateHomeAdvancement(player),
            bearingOffAdvantage: this.calculateBearingOffAdvantage(player),
            racingAdvantage: this.calculateRacingAdvantage(player),
            totalEV: 0
        };

        // Weighted EV calculation
        evaluation.totalEV = this.calculateTotalEV(evaluation);
        return evaluation;
    }

    countBlots(player) {
        let blots = 0;
        for (let i = 1; i <= 24; i++) {
            if (this.board[i] && this.board[i].color === player && this.board[i].count === 1) {
                blots++;
            }
        }
        return blots;
    }

    calculateBlockadeStrength(player) {
        let blockadeStrength = 0;
        let consecutiveBlocks = 0;
        const direction = player === 'white' ? -1 : 1;
        const homeStart = player === 'white' ? 1 : 19;
        const homeEnd = player === 'white' ? 6 : 24;

        for (let i = 1; i <= 24; i++) {
            if (this.board[i] && this.board[i].color === player && this.board[i].count >= 2) {
                consecutiveBlocks++;
                // Points closer to opponent's home are more valuable
                const distanceWeight = player === 'white' ? (25 - i) / 24 : i / 24;
                blockadeStrength += 1 + distanceWeight;
            } else {
                // Bonus for consecutive blocks
                if (consecutiveBlocks >= 3) {
                    blockadeStrength += consecutiveBlocks * 0.5;
                }
                consecutiveBlocks = 0;
            }
        }

        return blockadeStrength;
    }

    calculateHomeAdvancement(player) {
        const homeStart = player === 'white' ? 1 : 19;
        const homeEnd = player === 'white' ? 6 : 24;
        let homeCheckers = 0;
        
        for (let i = homeStart; i <= homeEnd; i++) {
            if (this.board[i] && this.board[i].color === player) {
                homeCheckers += this.board[i].count;
            }
        }
        
        return homeCheckers / 15; // Percentage of pieces in home
    }

    calculateBearingOffAdvantage(player) {
        // Temporarily set current player to evaluate bearing off for the specified player
        const originalPlayer = this.currentPlayer;
        this.currentPlayer = player;
        const canBearOff = this.canBearOff();
        this.currentPlayer = originalPlayer;
        
        if (!canBearOff) return 0;
        
        // Advanced bearing off position evaluation
        const homeStart = player === 'white' ? 1 : 19;
        const homeEnd = player === 'white' ? 6 : 24;
        let advantage = 0;
        
        for (let i = homeStart; i <= homeEnd; i++) {
            if (this.board[i] && this.board[i].color === player) {
                const pointValue = player === 'white' ? i : (25 - i);
                advantage += this.board[i].count * (7 - pointValue); // Higher points are better
            }
        }
        
        return advantage;
    }

    calculateRacingAdvantage(player) {
        const pipCounts = this.calculatePipCount();
        const myPips = pipCounts[player];
        const opponentPips = pipCounts[player === 'white' ? 'black' : 'white'];
        
        // Positive value means we're ahead in the race
        return (opponentPips - myPips) / Math.max(myPips, opponentPips);
    }

    calculateTotalEV(evaluation) {
        // Weighted combination of factors
        const weights = {
            pipAdvantage: -0.4,  // Lower pip count is better
            blotPenalty: -0.3,   // Fewer blots is better
            blockadeBonus: 0.2,  // More blockades is better
            homeBonus: 0.3,      // More pieces home is better
            bearingOffBonus: 0.4, // Better bearing off position
            racingBonus: 0.3     // Racing advantage
        };

        const pipAdvantage = (evaluation.opponentPipCount - evaluation.pipCount) / 
                            Math.max(evaluation.pipCount, evaluation.opponentPipCount);

        return (
            weights.pipAdvantage * pipAdvantage +
            weights.blotPenalty * evaluation.blotCount +
            weights.blockadeBonus * evaluation.blockadeStrength +
            weights.homeBonus * evaluation.homeAdvancement +
            weights.bearingOffBonus * evaluation.bearingOffAdvantage +
            weights.racingBonus * evaluation.racingAdvantage
        );
    }

    // Move Analysis System
    analyzeMoves(moves = null) {
        if (!moves) {
            moves = this.getPossibleMoves();
        }

        const analysis = [];
        const currentEV = this.evaluatePosition().totalEV;

        for (const move of moves) {
            // Simulate the move
            const gameState = this.cloneBoardState();
            const tempGame = new TavlaGame();
            tempGame.importGameState({
                ...gameState,
                currentPlayer: this.currentPlayer,
                dice: [...this.dice],
                moveHistory: [...this.moveHistory],
                gameOver: this.gameOver,
                winner: this.winner
            });

            // Make the move
            if (tempGame.makeMove(move.from, move.to)) {
                const newEV = tempGame.evaluatePosition(this.currentPlayer).totalEV;
                const evDifference = newEV - currentEV;
                
                analysis.push({
                    move: move,
                    ev: newEV,
                    evDifference: evDifference,
                    risks: this.analyzeRisks(move, tempGame),
                    benefits: this.analyzeBenefits(move, tempGame)
                });
            }
        }

        // Sort by EV (best first)
        analysis.sort((a, b) => b.ev - a.ev);
        return analysis;
    }

    analyzeRisks(move, tempGame) {
        const risks = [];
        const toPoint = parseInt(move.to);
        
        if (move.to !== 'home' && tempGame.board[toPoint] && 
            tempGame.board[toPoint].count === 1 && 
            tempGame.board[toPoint].color === this.currentPlayer) {
            
            // Calculate hit probability
            const hitProbability = this.calculateHitProbability(toPoint, this.currentPlayer === 'white' ? 'black' : 'white');
            if (hitProbability > 0.2) {
                risks.push({
                    type: 'exposure',
                    probability: hitProbability,
                    description: `Blot exposed with ${(hitProbability * 100).toFixed(1)}% hit chance`
                });
            }
        }

        return risks;
    }

    analyzeBenefits(move, tempGame) {
        const benefits = [];
        const fromPoint = parseInt(move.from);
        const toPoint = parseInt(move.to);

        // Hit opponent
        if (move.to !== 'home' && this.board[toPoint] && 
            this.board[toPoint].color !== this.currentPlayer && 
            this.board[toPoint].count === 1) {
            benefits.push({
                type: 'hit',
                description: 'Hits opponent blot'
            });
        }

        // Make point
        if (move.to !== 'home' && tempGame.board[toPoint] && 
            tempGame.board[toPoint].count === 2 && 
            tempGame.board[toPoint].color === this.currentPlayer) {
            benefits.push({
                type: 'makePoint',
                description: 'Makes a new point'
            });
        }

        // Advance home
        if (move.to === 'home' || this.isInHomeBoard(toPoint, this.currentPlayer)) {
            benefits.push({
                type: 'homeAdvancement',
                description: 'Advances toward home'
            });
        }

        return benefits;
    }

    calculateHitProbability(point, opponent) {
        let hitShots = 0;
        const totalShots = 36; // 6x6 dice combinations

        // Check all possible dice combinations
        for (let die1 = 1; die1 <= 6; die1++) {
            for (let die2 = 1; die2 <= 6; die2++) {
                const dice = die1 === die2 ? [die1, die1, die1, die1] : [die1, die2];
                
                for (const die of dice) {
                    const fromPoint = opponent === 'white' ? point + die : point - die;
                    if (fromPoint >= 1 && fromPoint <= 24 && 
                        this.board[fromPoint] && 
                        this.board[fromPoint].color === opponent && 
                        this.board[fromPoint].count > 0) {
                        hitShots++;
                        break; // Count each dice combination only once
                    }
                }
                
                // Check bar entry
                if (this.bar[opponent] > 0) {
                    const entryPoint = opponent === 'white' ? 25 - die1 : die1;
                    if (entryPoint === point) hitShots++;
                    if (die1 !== die2) {
                        const entryPoint2 = opponent === 'white' ? 25 - die2 : die2;
                        if (entryPoint2 === point) hitShots++;
                    }
                }
            }
        }

        return Math.min(hitShots / totalShots, 1.0);
    }

    isInHomeBoard(point, player) {
        if (player === 'white') {
            return point >= 1 && point <= 6;
        } else {
            return point >= 19 && point <= 24;
        }
    }

    // Get the best move for AI
    getBestMove(avoidBestMove = false, targetEVDifference = 0.05) {
        const analysis = this.analyzeMoves();
        if (analysis.length === 0) return null;

        if (avoidBestMove && analysis.length > 1) {
            // Find a move that's slightly worse than the best
            const bestEV = analysis[0].ev;
            for (let i = 1; i < analysis.length; i++) {
                const evDifference = bestEV - analysis[i].ev;
                if (evDifference >= targetEVDifference) {
                    return analysis[i];
                }
            }
            // If no suitable move found, return second best
            return analysis[1];
        }

        return analysis[0];
    }
}