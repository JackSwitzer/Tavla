class AIPlayer {
    constructor(game, difficulty = 'hard') {
        this.game = game;
        this.difficulty = difficulty; // 'easy', 'medium', 'hard', 'expert', 'adaptive'
        this.playerColor = 'black'; // AI plays as black
        this.moveHistory = [];
        this.playerMoveAnalysis = [];
        
        // Opening book for optimal first moves
        this.openingBook = this.initializeOpeningBook();
        
        // EV thresholds for feedback - now always show analysis
        this.feedbackThresholds = {
            terrible: -0.12,
            bad: -0.06,
            questionable: -0.03,
            acceptable: 0.02
        };
    }

    initializeOpeningBook() {
        // Precomputed optimal opening moves for black player (moving from 1→24)
        return {
            '3,1': [{ from: '17', to: '20' }, { from: '19', to: '20' }],
            '1,3': [{ from: '17', to: '20' }, { from: '19', to: '20' }],
            '4,2': [{ from: '17', to: '21' }, { from: '19', to: '21' }],
            '2,4': [{ from: '17', to: '21' }, { from: '19', to: '21' }],
            '6,1': [{ from: '12', to: '18' }, { from: '17', to: '18' }],
            '1,6': [{ from: '12', to: '18' }, { from: '17', to: '18' }],
            '5,3': [{ from: '12', to: '17' }, { from: '17', to: '20' }],
            '3,5': [{ from: '12', to: '17' }, { from: '17', to: '20' }],
            '6,5': [{ from: '1', to: '12' }],
            '5,6': [{ from: '1', to: '12' }],
            '4,1': [{ from: '1', to: '2' }, { from: '12', to: '16' }],
            '1,4': [{ from: '1', to: '2' }, { from: '12', to: '16' }],
            '6,4': [{ from: '1', to: '7' }, { from: '12', to: '16' }],
            '4,6': [{ from: '1', to: '7' }, { from: '12', to: '16' }],
            '5,2': [{ from: '12', to: '14' }, { from: '12', to: '17' }],
            '2,5': [{ from: '12', to: '14' }, { from: '12', to: '17' }],
            '6,3': [{ from: '1', to: '7' }, { from: '12', to: '15' }],
            '3,6': [{ from: '1', to: '7' }, { from: '12', to: '15' }],
            '5,4': [{ from: '12', to: '16' }, { from: '12', to: '17' }],
            '4,5': [{ from: '12', to: '16' }, { from: '12', to: '17' }],
            '6,2': [{ from: '1', to: '7' }, { from: '12', to: '14' }],
            '2,6': [{ from: '1', to: '7' }, { from: '12', to: '14' }]
        };
    }

    // Analyze player's move and provide feedback
    analyzePlayerMove(move, beforeState, afterState) {
        // Simulate all possible moves from before state
        const tempGame = new TavlaGame();
        tempGame.importGameState(beforeState);
        
        const moveAnalysis = tempGame.analyzeMoves();
        const playerMoveAnalysis = moveAnalysis.find(analysis => 
            analysis.move.from === move.from && analysis.move.to === move.to
        );

        if (!playerMoveAnalysis) {
            return null; // Invalid move
        }

        const bestMove = moveAnalysis[0];
        const evDifference = bestMove.ev - playerMoveAnalysis.ev; // Positive means player's move was worse
        
        const feedback = {
            playerMove: playerMoveAnalysis,
            bestMove: bestMove,
            evDifference: evDifference,
            rank: moveAnalysis.indexOf(playerMoveAnalysis) + 1,
            totalMoves: moveAnalysis.length,
            category: this.categorizeMoveQuality(evDifference),
            shouldShowFeedback: true, // Always show analysis now
            feedbackMessage: this.generateFeedbackMessage(playerMoveAnalysis, bestMove, evDifference),
            allMoves: moveAnalysis // Include all moves for comprehensive analysis
        };

        this.playerMoveAnalysis.push(feedback);
        return feedback;
    }

    categorizeMoveQuality(evDifference) {
        // evDifference is positive when player's move was worse than optimal
        if (evDifference <= this.feedbackThresholds.acceptable) return 'excellent';
        if (evDifference <= this.feedbackThresholds.questionable) return 'good';
        if (evDifference <= this.feedbackThresholds.bad) return 'questionable';
        if (evDifference <= this.feedbackThresholds.terrible) return 'bad';
        return 'terrible';
    }

    shouldShowFeedback(evDifference) {
        // Always show analysis now
        return true;
    }

    generateFeedbackMessage(playerMove, bestMove, evDifference) {
        const category = this.categorizeMoveQuality(evDifference);
        let message = '';

        switch (category) {
            case 'excellent':
                message = '🎯 Excellent move! ';
                break;
            case 'good':
                message = '👍 Good move! ';
                break;
            case 'questionable':
                message = '🤔 Decent move, but could be improved. ';
                break;
            case 'bad':
                message = '⚠️ This move has significant issues. ';
                break;
            case 'terrible':
                message = '🚫 This move is quite poor. ';
                break;
        }

        // Add specific reasons for non-excellent moves
        if (category !== 'excellent') {
            const reasons = [];
            
            // Risk analysis
            if (playerMove.risks.length > 0) {
                playerMove.risks.forEach(risk => {
                    if (risk.type === 'exposure') {
                        reasons.push(`Exposing blot with ${(risk.probability * 100).toFixed(1)}% hit chance`);
                    }
                });
            }

            // Missed opportunities
            if (bestMove.benefits.length > 0) {
                bestMove.benefits.forEach(benefit => {
                    if (benefit.type === 'hit') {
                        reasons.push('Missed chance to hit opponent blot');
                    } else if (benefit.type === 'makePoint') {
                        reasons.push('Missed chance to make a valuable point');
                    }
                });
            }

            // EV difference
            if (evDifference > 0.01) {
                const evLoss = (evDifference * 100).toFixed(1);
                reasons.push(`${evLoss}% EV loss from optimal`);
            }

            if (reasons.length > 0) {
                message += reasons.join('. ') + '.';
            }
        } else {
            // Positive feedback for excellent moves
            if (playerMove.benefits.length > 0) {
                const benefits = playerMove.benefits.map(b => b.description).join(', ');
                message += `Great strategic choice: ${benefits}`;
            } else {
                message += 'This is the optimal or near-optimal move!';
            }
        }

        return message;
    }

    describeBestMove(bestMove) {
        const move = bestMove.move;
        let description = '';

        if (move.from === 'bar') {
            description = `Enter from bar to point ${move.to}`;
        } else if (move.to === 'home') {
            description = `Bear off from point ${move.from}`;
        } else {
            description = `Move from point ${move.from} to point ${move.to}`;
        }

        // Add benefits to make it clearer why it's the best move
        if (bestMove.benefits.length > 0) {
            const benefitDesc = bestMove.benefits.map(b => {
                switch(b.type) {
                    case 'hit': return 'hits opponent';
                    case 'makePoint': return 'makes point';
                    case 'homeAdvancement': return 'advances home';
                    default: return b.description;
                }
            }).join(', ');
            description += ` (${benefitDesc})`;
        }

        return description;
    }

    // AI move selection - now plays much stronger
    makeMove() {
        if (this.game.currentPlayer !== this.playerColor) {
            return null;
        }

        // Check if this is an opening move
        if (this.game.moveHistory.length <= 2) {
            const openingMove = this.getOpeningMove();
            if (openingMove) {
                // Still track the move
                const moveAnalysis = this.game.analyzeMoves();
                const selectedAnalysis = moveAnalysis.find(analysis => 
                    analysis.move.from === openingMove.from && analysis.move.to === openingMove.to
                ) || { move: openingMove, ev: 0, evDifference: 0 };

                this.moveHistory.push({
                    move: openingMove,
                    analysis: selectedAnalysis,
                    timestamp: Date.now()
                });

                return openingMove;
            }
        }

        // Analyze all possible moves
        const moveAnalysis = this.game.analyzeMoves();
        if (moveAnalysis.length === 0) {
            return null;
        }

        // Get the last player move analysis to determine AI strategy
        const lastPlayerAnalysis = this.playerMoveAnalysis[this.playerMoveAnalysis.length - 1];
        
        // Determine AI move based on difficulty
        let selectedMove;
        
        switch (this.difficulty) {
            case 'easy':
                // Pick a random move from top 40%
                const easyMoves = moveAnalysis.slice(0, Math.max(1, Math.floor(moveAnalysis.length * 0.4)));
                selectedMove = easyMoves[Math.floor(Math.random() * easyMoves.length)];
                break;
                
            case 'medium':
                // Pick from top 25% of moves
                const mediumMoves = moveAnalysis.slice(0, Math.max(1, Math.floor(moveAnalysis.length * 0.25)));
                selectedMove = mediumMoves[Math.floor(Math.random() * mediumMoves.length)];
                break;
                
            case 'hard':
                // Pick from top 3 moves, weighted toward the best
                const hardMoves = moveAnalysis.slice(0, Math.min(3, moveAnalysis.length));
                const weights = [0.6, 0.3, 0.1];
                const rand = Math.random();
                let cumWeight = 0;
                for (let i = 0; i < hardMoves.length; i++) {
                    cumWeight += weights[i];
                    if (rand < cumWeight) {
                        selectedMove = hardMoves[i];
                        break;
                    }
                }
                selectedMove = selectedMove || hardMoves[0];
                break;
                
            case 'expert':
                // Almost always pick the best move
                selectedMove = Math.random() < 0.95 ? moveAnalysis[0] : moveAnalysis[Math.min(1, moveAnalysis.length - 1)];
                break;
                
            case 'adaptive':
            default:
                // Adapt based on player skill - but play stronger overall
                selectedMove = this.getAdaptiveMove(moveAnalysis, lastPlayerAnalysis);
                break;
        }

        this.moveHistory.push({
            move: selectedMove.move,
            analysis: selectedMove,
            timestamp: Date.now()
        });

        return selectedMove.move;
    }

    getOpeningMove() {
        const dice = this.game.dice;
        if (dice.length !== 2) return null;

        const diceKey = `${dice[0]},${dice[1]}`;
        const reverseDiceKey = `${dice[1]},${dice[0]}`;
        
        const openingMoves = this.openingBook[diceKey] || this.openingBook[reverseDiceKey];
        if (!openingMoves) return null;

        // Validate and return the first valid move
        for (const move of openingMoves) {
            if (this.game.isValidMove(move.from, move.to)) {
                return move;
            }
        }

        return null;
    }

    getAdaptiveMove(moveAnalysis, lastPlayerAnalysis) {
        const bestMove = moveAnalysis[0];
        
        if (!lastPlayerAnalysis) {
            // No previous player move, play strong but not perfect
            return Math.random() < 0.8 ? bestMove : moveAnalysis[Math.min(1, moveAnalysis.length - 1)];
        }

        const playerMoveCategory = lastPlayerAnalysis.category;
        const playerAvgEV = this.getPlayerAverageEV();
        
        // Adjust AI strength based on player performance
        switch (playerMoveCategory) {
            case 'terrible':
            case 'bad':
                if (playerAvgEV < -0.1) {
                    // Player is really struggling, play a bit weaker
                    const weakerMoves = moveAnalysis.slice(0, Math.min(4, moveAnalysis.length));
                    return weakerMoves[Math.floor(Math.random() * weakerMoves.length)];
                }
                // Otherwise play normally strong
                return Math.random() < 0.85 ? bestMove : moveAnalysis[Math.min(1, moveAnalysis.length - 1)];
                
            case 'questionable':
                // Play very strong
                return Math.random() < 0.9 ? bestMove : moveAnalysis[Math.min(1, moveAnalysis.length - 1)];
                
            case 'good':
            case 'excellent':
                // Player is playing well, play near-optimal
                return Math.random() < 0.95 ? bestMove : moveAnalysis[Math.min(1, moveAnalysis.length - 1)];
                
            default:
                return Math.random() < 0.85 ? bestMove : moveAnalysis[Math.min(1, moveAnalysis.length - 1)];
        }
    }

    getPlayerAverageEV() {
        if (this.playerMoveAnalysis.length === 0) return 0;
        
        const totalEV = this.playerMoveAnalysis.reduce((sum, analysis) => sum + analysis.playerMove.ev, 0);
        return totalEV / this.playerMoveAnalysis.length;
    }

    // Get AI performance statistics
    getPerformanceStats() {
        if (this.moveHistory.length === 0) return null;

        const totalMoves = this.moveHistory.length;
        const avgEV = this.moveHistory.reduce((sum, move) => sum + move.analysis.ev, 0) / totalMoves;
        const avgEVDifference = this.moveHistory.reduce((sum, move) => sum + move.analysis.evDifference, 0) / totalMoves;

        return {
            totalMoves,
            avgEV,
            avgEVDifference,
            playingStrength: this.categorizePlayingStrength(avgEVDifference)
        };
    }

    categorizePlayingStrength(avgEVDifference) {
        if (avgEVDifference >= -0.01) return 'Expert';
        if (avgEVDifference >= -0.03) return 'Advanced';
        if (avgEVDifference >= -0.05) return 'Intermediate';
        if (avgEVDifference >= -0.08) return 'Beginner';
        return 'Novice';
    }

    // Reset for new game
    reset() {
        this.moveHistory = [];
        this.playerMoveAnalysis = [];
    }
} 