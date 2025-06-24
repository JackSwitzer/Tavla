// Initialize the game when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    let game;
    let ui;
    
    // Theme selection handler
    const themeOptions = document.querySelectorAll('.theme-option');
    const themeSelector = document.getElementById('theme-selector');
    const gameContainer = document.querySelector('.game-container');
    
    themeOptions.forEach(option => {
        option.addEventListener('click', () => {
            const selectedTheme = option.dataset.theme;
            
            // Apply theme
            document.documentElement.className = `theme-${selectedTheme}`;
            
            // Store theme preference
            localStorage.setItem('tavlaTheme', selectedTheme);
            
            // Hide selector and show game
            themeSelector.style.display = 'none';
            gameContainer.style.display = 'block';
            
            // Initialize game after theme selection
            if (!game) {
                game = new TavlaGame();
                ui = new TavlaUI(game);
                
                // Make game instance available globally for debugging
                window.tavlaGame = game;
                window.tavlaUI = ui;
                
                // Add window resize handler for draggable sidebar
                window.addEventListener('resize', () => {
                    if (ui && ui.handleWindowResize) {
                        ui.handleWindowResize();
                    }
                });
                
                console.log('Turkish Tavla game initialized!');
                console.log('Selected theme:', selectedTheme);
                console.log('Game instance available as window.tavlaGame');
                console.log('UI instance available as window.tavlaUI');
                console.log('📋 Analysis sidebar is draggable - grab the handle at the top!');
            }
        });
    });
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('tavlaTheme');
    if (savedTheme) {
        // Auto-select saved theme
        const savedOption = document.querySelector(`[data-theme="${savedTheme}"]`);
        if (savedOption) {
            savedOption.click();
        }
    }
});