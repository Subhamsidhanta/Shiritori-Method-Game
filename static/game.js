// Game State Management
class ShiritoriGame {
    constructor() {
        this.currentMode = null;
        this.score = 0;
        this.timer = 0;
        this.gameInterval = null;
        this.wordTimer = null;
        this.bestStreak = 0;
        this.currentStreak = 0;
        this.startTime = null;
        
        // Number game state
        this.currentNumbers = [];
        this.round = 1;
        this.minRange = 1;
        this.maxRange = 100;
        this.memoryTime = 3;
        this.isShowingNumbers = false;
        this.canSubmitNumbers = false;
        this.answerTimer = null;
        this.answerTimeLeft = 15;
        
        // Word game state
        this.currentTopic = '';
        this.wordSequence = [];
        this.currentAIWord = '';
        this.userWords = [];
        this.wordTimeLeft = 15;
        this.selectedArrangement = [];
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        // Get all important DOM elements
        this.scoreElement = document.getElementById('score');
        this.timerElement = document.getElementById('timer');
        this.finalScoreElement = document.getElementById('final-score');
        this.timePlayed = document.getElementById('time-played');
        this.bestStreakElement = document.getElementById('best-streak');
        this.notification = document.getElementById('notification');
        this.notificationText = document.getElementById('notification-text');
        this.loading = document.getElementById('loading');
        
        // Number game elements
        this.numberDisplay = document.getElementById('number-display');
        this.numberInput = document.getElementById('number-input');
        this.roundNumber = document.getElementById('round-number');
        
        // Word game elements
        this.currentTopicElement = document.getElementById('current-topic');
        this.wordSequenceElement = document.getElementById('word-sequence');
        this.aiWordElement = document.getElementById('ai-word');
        this.wordTimerElement = document.getElementById('word-timer');
        this.wordInput = document.getElementById('word-input');
        this.arrangementSection = document.getElementById('arrangement-section');
        this.arrangementButtons = document.getElementById('arrangement-buttons');
    }
    
    bindEvents() {
        // Bind Enter key events with proper error handling
        const numberInput = document.getElementById('number-input');
        if (numberInput) {
            numberInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && game.canSubmitNumbers) {
                    e.preventDefault();
                    submitNumbers();
                }
            });
        }
        
        const wordInput = document.getElementById('word-input');
        if (wordInput) {
            wordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    submitWord();
                }
            });
        }
        
        const topicInput = document.getElementById('topic-input');
        if (topicInput) {
            topicInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    startWordGame();
                }
            });
        }
        
        // Add setup form enter key bindings
        const setupInputs = ['min-range', 'max-range', 'memory-time'];
        setupInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        startNumberGame();
                    }
                });
            }
        });
    }
    
    showNotification(message, type = 'info') {
        this.notificationText.textContent = message;
        this.notification.className = `notification show ${type}`;
        
        setTimeout(() => {
            this.notification.classList.remove('show');
        }, 3000);
    }
    
    showLoading(show = true) {
        this.loading.style.display = show ? 'flex' : 'none';
    }
    
    updateScore(points = 1) {
        this.score += points;
        this.currentStreak++;
        this.bestStreak = Math.max(this.bestStreak, this.currentStreak);
        this.scoreElement.textContent = this.score;
        this.showNotification(`+${points} points! Great job!`, 'success');
    }
    
    resetStreak() {
        this.currentStreak = 0;
    }
    
    startGameTimer() {
        this.startTime = Date.now();
        this.gameInterval = setInterval(() => {
            this.timer = Math.floor((Date.now() - this.startTime) / 1000);
            this.timerElement.textContent = this.timer;
        }, 1000);
    }
    
    stopGameTimer() {
        if (this.gameInterval) {
            clearInterval(this.gameInterval);
            this.gameInterval = null;
        }
        if (this.answerTimer) {
            clearInterval(this.answerTimer);
            this.answerTimer = null;
        }
    }
    
    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.game-section').forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
        });
        
        // Show the target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.style.display = 'block';
        }
    }
}

// Initialize game instance
const game = new ShiritoriGame();

// Mode Selection
function selectMode(mode) {
    game.currentMode = mode;
    if (mode === 'number') {
        game.showSection('number-setup');
    } else if (mode === 'words') {
        game.showSection('word-setup');
    }
}

// Number Game Functions
function startNumberGame() {
    const minRange = parseInt(document.getElementById('min-range').value);
    const maxRange = parseInt(document.getElementById('max-range').value);
    const memoryTime = parseInt(document.getElementById('memory-time').value);
    
    if (minRange >= maxRange) {
        game.showNotification('Maximum must be greater than minimum!', 'error');
        return;
    }
    
    game.minRange = minRange;
    game.maxRange = maxRange;
    game.memoryTime = memoryTime;
    game.round = 1;
    game.currentNumbers = [];
    
    game.showSection('number-game');
    game.startGameTimer();
    generateNewNumber();
}

function generateNewNumber() {
    // Reset states
    game.canSubmitNumbers = false;
    game.isShowingNumbers = true;
    
    // Clear any existing timers
    if (game.answerTimer) {
        clearInterval(game.answerTimer);
        game.answerTimer = null;
    }
    
    const newNumber = Math.floor(Math.random() * (game.maxRange - game.minRange + 1)) + game.minRange;
    game.currentNumbers.push(newNumber);
    
    // Display the sequence
    const displayText = game.currentNumbers.join('');
    game.numberDisplay.textContent = displayText;
    game.roundNumber.textContent = game.round;
    
    // Clear and disable input
    game.numberInput.value = '';
    game.numberInput.disabled = true;
    game.numberInput.placeholder = `Memorize the numbers... (${game.memoryTime}s)`;
    
    // Show for memory time, then hide and start answer timer
    setTimeout(() => {
        game.isShowingNumbers = false;
        game.canSubmitNumbers = true;
        game.numberDisplay.textContent = 'Enter the numbers you remember';
        game.numberInput.disabled = false;
        game.numberInput.placeholder = 'Enter the numbers you saw';
        game.numberInput.focus();
        
        // Start 15-second answer timer
        startAnswerTimer();
    }, game.memoryTime * 1000);
}

function startAnswerTimer() {
    game.answerTimeLeft = 15;
    updateAnswerTimerDisplay();
    
    game.answerTimer = setInterval(() => {
        game.answerTimeLeft--;
        updateAnswerTimerDisplay();
        
        if (game.answerTimeLeft <= 0) {
            clearInterval(game.answerTimer);
            game.answerTimer = null;
            game.canSubmitNumbers = false;
            game.numberInput.disabled = true;
            game.showNotification('Time\'s up! You failed this round.', 'error');
            
            setTimeout(() => {
                endGame();
            }, 2000);
        }
    }, 1000);
}

function updateAnswerTimerDisplay() {
    // Update the timer display in the header or create a new one
    let answerTimerElement = document.getElementById('answer-timer');
    if (!answerTimerElement) {
        answerTimerElement = document.createElement('div');
        answerTimerElement.id = 'answer-timer';
        answerTimerElement.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.2rem;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        `;
        document.body.appendChild(answerTimerElement);
    }
    
    answerTimerElement.textContent = `Answer Time: ${game.answerTimeLeft}s`;
    
    // Add warning style when time is low
    if (game.answerTimeLeft <= 5) {
        answerTimerElement.style.animation = 'pulse 0.5s infinite';
    } else {
        answerTimerElement.style.animation = 'none';
    }
    
    // Hide timer when not needed
    if (game.answerTimeLeft <= 0 || !game.canSubmitNumbers) {
        setTimeout(() => {
            if (answerTimerElement && answerTimerElement.parentNode) {
                answerTimerElement.parentNode.removeChild(answerTimerElement);
            }
        }, 1000);
    }
}

function submitNumbers() {
    console.log('submitNumbers() called');
    console.log('canSubmitNumbers:', game.canSubmitNumbers);
    console.log('isShowingNumbers:', game.isShowingNumbers);
    
    // Prevent multiple submissions
    if (!game.canSubmitNumbers || game.isShowingNumbers) {
        console.log('Submission blocked - conditions not met');
        return;
    }
    
    game.canSubmitNumbers = false;
    console.log('Processing number submission...');
    
    // Clear answer timer
    if (game.answerTimer) {
        clearInterval(game.answerTimer);
        game.answerTimer = null;
    }
    
    // Remove answer timer display
    const answerTimerElement = document.getElementById('answer-timer');
    if (answerTimerElement && answerTimerElement.parentNode) {
        answerTimerElement.parentNode.removeChild(answerTimerElement);
    }
    
    const userInput = game.numberInput.value.trim();
    const correctAnswer = game.currentNumbers.join('');
    
    console.log('User input:', userInput);
    console.log('Correct answer:', correctAnswer);
    
    // Disable input to prevent further submissions
    game.numberInput.disabled = true;
    
    if (userInput === correctAnswer) {
        console.log('Correct answer!');
        game.updateScore();
        game.round++;
        game.numberDisplay.textContent = 'Correct! Get ready for next round...';
        
        setTimeout(() => {
            generateNewNumber();
        }, 2000);
    } else {
        console.log('Wrong answer!');
        game.resetStreak();
        game.numberDisplay.textContent = `Wrong! Answer was: ${correctAnswer}`;
        game.showNotification(`Wrong! Correct answer was: ${correctAnswer}`, 'error');
        
        setTimeout(() => {
            endGame();
        }, 3000);
    }
}

// Word Game Functions
function selectTopic(topic) {
    document.getElementById('topic-input').value = topic;
    document.querySelectorAll('.topic-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

async function selectRandomTopic() {
    game.showLoading(true);
    try {
        const response = await fetch('/get-random-topic', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('topic-input').value = data.topic;
            game.showNotification(`Random topic selected: ${data.topic}`, 'success');
        } else {
            game.showNotification('Failed to get random topic. Please enter manually.', 'error');
        }
    } catch (error) {
        game.showNotification('Error getting random topic. Please enter manually.', 'error');
    } finally {
        game.showLoading(false);
    }
}

function showTopicExamples(topic) {
    const topicExamplesElement = document.getElementById('topic-examples');
    const examples = {
        'programming': 'Examples: python, java, javascript, cpp, ruby...',
        'programming languages': 'Examples: python, java, javascript, cpp, ruby...',
        'fruits': 'Examples: apple, banana, orange, grape, cherry...',
        'animals': 'Examples: elephant, tiger, dog, cat, eagle...',
        'colors': 'Examples: red, blue, green, yellow, purple...',
        'countries': 'Examples: usa, japan, france, brazil, canada...',
        'vegetables': 'Examples: carrot, broccoli, spinach, potato, onion...',
        'movies': 'Examples: avatar, batman, inception, frozen, jaws...',
        'sports': 'Examples: football, basketball, tennis, golf, swimming...',
        'cars': 'Examples: toyota, honda, bmw, ford, mercedes...'
    };
    
    const lowerTopic = topic.toLowerCase();
    const exampleText = examples[lowerTopic] || `Only words strictly related to "${topic}" are allowed`;
    topicExamplesElement.textContent = exampleText;
}

async function startWordGame() {
    const topic = document.getElementById('topic-input').value.trim();
    if (!topic) {
        game.showNotification('Please enter a topic!', 'error');
        return;
    }
    
    game.currentTopic = topic;
    game.wordSequence = [];
    game.userWords = [];
    game.selectedArrangement = [];
    
    game.showSection('word-game');
    game.currentTopicElement.textContent = topic;
    showTopicExamples(topic);
    game.startGameTimer();
    
    // Get first word from AI
    await getAIWord();
}

async function getAIWord() {
    game.showLoading(true);
    try {
        const response = await fetch('/get-ai-word', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: game.currentTopic,
                lastWord: game.wordSequence.length > 0 ? game.wordSequence[game.wordSequence.length - 1] : null,
                usedWords: game.wordSequence
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            game.currentAIWord = data.word;
            game.aiWordElement.textContent = data.word;
            game.wordSequence.push(data.word);
            updateWordSequenceDisplay();
            
            if (game.wordSequence.length > 1) {
                showArrangementSection();
            } else {
                startWordTimer();
            }
        } else {
            game.showNotification('AI failed to generate word. Game over!', 'error');
            endGame();
        }
    } catch (error) {
        game.showNotification('Error communicating with AI. Game over!', 'error');
        endGame();
    } finally {
        game.showLoading(false);
    }
}

function startWordTimer() {
    game.wordTimeLeft = 15;
    game.wordTimerElement.textContent = game.wordTimeLeft;
    game.wordTimerElement.parentElement.classList.remove('warning');
    
    // Enable input
    game.wordInput.disabled = false;
    game.wordInput.focus();
    
    game.wordTimer = setInterval(() => {
        game.wordTimeLeft--;
        game.wordTimerElement.textContent = game.wordTimeLeft;
        
        if (game.wordTimeLeft <= 5) {
            game.wordTimerElement.parentElement.classList.add('warning');
        }
        
        if (game.wordTimeLeft <= 0) {
            clearInterval(game.wordTimer);
            game.wordTimer = null;
            
            // Disable input
            game.wordInput.disabled = true;
            
            game.showNotification('Time\'s up! You failed this round.', 'error');
            
            setTimeout(() => {
                endGame();
            }, 2000);
        }
    }, 1000);
}

function stopWordTimer() {
    if (game.wordTimer) {
        clearInterval(game.wordTimer);
        game.wordTimer = null;
        game.wordTimerElement.parentElement.classList.remove('warning');
    }
}

async function submitWord() {
    const userWord = game.wordInput.value.trim().toLowerCase();
    
    if (!userWord) {
        game.showNotification('Please enter a word!', 'error');
        return;
    }
    
    // Prevent multiple submissions
    if (game.wordInput.disabled) {
        return;
    }
    
    // Disable input immediately to prevent multiple submissions
    game.wordInput.disabled = true;
    
    // Check if word follows Shiritori rules
    const lastChar = game.currentAIWord.slice(-1).toLowerCase();
    const firstChar = userWord.charAt(0).toLowerCase();
    
    if (firstChar !== lastChar) {
        game.showNotification(`Word must start with '${lastChar.toUpperCase()}'!`, 'error');
        game.wordInput.disabled = false; // Re-enable for correction
        return;
    }
    
    // Check if word was already used
    if (game.wordSequence.includes(userWord)) {
        game.showNotification('Word already used!', 'error');
        game.wordInput.disabled = false; // Re-enable for correction
        return;
    }
    
    // Validate word with AI
    game.showLoading(true);
    try {
        const response = await fetch('/validate-word', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                word: userWord,
                topic: game.currentTopic
            })
        });
        
        const data = await response.json();
        
        if (data.valid) {
            stopWordTimer();
            game.wordSequence.push(userWord);
            game.userWords.push(userWord);
            game.wordInput.value = '';
            game.updateScore();
            
            updateWordSequenceDisplay();
            
            // Get next AI word
            setTimeout(() => {
                getAIWord();
            }, 1500);
        } else {
            const reason = data.reason || `"${userWord}" is not valid for topic "${game.currentTopic}"`;
            game.showNotification(reason, 'error');
            game.wordInput.disabled = false; // Re-enable for correction
            game.wordInput.focus(); // Keep focus on input for retry
        }
    } catch (error) {
        game.showNotification('Error validating word. Please try again.', 'error');
        game.wordInput.disabled = false; // Re-enable for correction
    } finally {
        game.showLoading(false);
    }
}

function updateWordSequenceDisplay() {
    game.wordSequenceElement.innerHTML = game.wordSequence.map((word, index) => {
        const isAI = !game.userWords.includes(word);
        return `<div class="word-chip ${isAI ? 'ai-word' : 'user-word'}">
            ${isAI ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>'}
            ${word}
        </div>`;
    }).join('');
}

function showArrangementSection() {
    const wordsToArrange = [...game.wordSequence];
    game.selectedArrangement = [];
    
    // Hide the word input section during arrangement
    document.querySelector('.word-input-section').style.display = 'none';
    
    // Hide the word sequence section during arrangement
    game.wordSequenceElement.style.display = 'none';
    
    // Clear any existing arrangement preview
    const existingPreview = document.getElementById('arrangement-preview');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    // Shuffle the words for arrangement (make it more challenging)
    const shuffledWords = shuffleArray([...wordsToArrange]);
    
    // Create arrangement buttons in shuffled order
    game.arrangementButtons.innerHTML = shuffledWords.map((word, shuffledIndex) => {
        const originalIndex = wordsToArrange.indexOf(word);
        return `<button class="arrangement-btn" data-word="${word}" data-original-index="${originalIndex}" onclick="selectWordForArrangement('${word}', ${originalIndex})">
            ${word}
        </button>`;
    }).join('');
    
    // Show arrangement section
    game.arrangementSection.style.display = 'block';
    
    // Add instruction text
    const instructionText = game.arrangementSection.querySelector('h3');
    if (instructionText) {
        instructionText.textContent = `Arrange these ${wordsToArrange.length} words in the correct sequence:`;
    }
    
    // Initialize empty preview
    updateArrangementPreview();
}

// Helper function to shuffle array
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

function selectWordForArrangement(word, originalIndex) {
    const button = document.querySelector(`[data-word="${word}"][data-original-index="${originalIndex}"]`);
    
    if (button.classList.contains('selected')) {
        // Deselect - remove from arrangement and update visual
        button.classList.remove('selected');
        button.querySelector('.order-number')?.remove();
        game.selectedArrangement = game.selectedArrangement.filter(item => 
            !(item.word === word && item.originalIndex === originalIndex)
        );
        
        // Update order numbers for remaining selected items
        updateOrderNumbers();
    } else {
        // Select - add to arrangement
        button.classList.add('selected');
        const orderNumber = game.selectedArrangement.length + 1;
        game.selectedArrangement.push({ word, originalIndex, order: orderNumber });
        
        // Add order number to button
        const orderSpan = document.createElement('span');
        orderSpan.className = 'order-number';
        orderSpan.textContent = orderNumber;
        button.appendChild(orderSpan);
    }
    
    // Update the arrangement preview
    updateArrangementPreview();
}

function updateOrderNumbers() {
    // Remove all existing order numbers
    document.querySelectorAll('.order-number').forEach(span => span.remove());
    
    // Re-add order numbers based on current selection order
    game.selectedArrangement.forEach((item, index) => {
        const button = document.querySelector(`[data-word="${item.word}"][data-original-index="${item.originalIndex}"]`);
        if (button) {
            const orderSpan = document.createElement('span');
            orderSpan.className = 'order-number';
            orderSpan.textContent = index + 1;
            button.appendChild(orderSpan);
            item.order = index + 1;
        }
    });
    
    updateArrangementPreview();
}

function updateArrangementPreview() {
    // Show current arrangement order above the buttons
    let previewElement = document.getElementById('arrangement-preview');
    if (!previewElement) {
        previewElement = document.createElement('div');
        previewElement.id = 'arrangement-preview';
        previewElement.className = 'arrangement-preview';
        game.arrangementButtons.parentNode.insertBefore(previewElement, game.arrangementButtons);
    }
    
    if (game.selectedArrangement.length > 0) {
        const sortedArrangement = [...game.selectedArrangement].sort((a, b) => a.order - b.order);
        previewElement.innerHTML = `
            <div class="preview-label">Your sequence:</div>
            <div class="preview-words">
                ${sortedArrangement.map(item => `<span class="preview-word">${item.word}</span>`).join(' → ')}
            </div>
        `;
        previewElement.style.display = 'block';
    } else {
        previewElement.style.display = 'none';
    }
}

function confirmArrangement() {
    if (game.selectedArrangement.length !== game.wordSequence.length) {
        game.showNotification('Please arrange all words!', 'error');
        return;
    }
    
    // Check if arrangement is correct
    const sortedArrangement = [...game.selectedArrangement].sort((a, b) => a.order - b.order);
    const userArrangementWords = sortedArrangement.map(item => item.word);
    const correctArrangement = [...game.wordSequence];
    
    const isCorrect = JSON.stringify(correctArrangement) === JSON.stringify(userArrangementWords);
    
    if (isCorrect) {
        game.showNotification('Correct arrangement! 🎉', 'success');
        
        // Hide arrangement section
        game.arrangementSection.style.display = 'none';
        
        // Show the word sequence section again
        game.wordSequenceElement.style.display = 'flex';
        
        // Show the word input section again
        document.querySelector('.word-input-section').style.display = 'block';
        
        // Clear the word input and focus it
        game.wordInput.value = '';
        game.wordInput.focus();
        
        // Clear arrangement preview for next round
        const previewElement = document.getElementById('arrangement-preview');
        if (previewElement) {
            previewElement.remove();
        }
        
        startWordTimer();
    } else {
        game.showNotification('Wrong arrangement! Try again...', 'error');
        // Don't end the game, let them try again
        
        // Reset the arrangement and refresh preview
        game.selectedArrangement = [];
        document.querySelectorAll('.arrangement-btn').forEach(btn => {
            btn.classList.remove('selected');
            btn.querySelector('.order-number')?.remove();
        });
        
        // Refresh the arrangement preview
        updateArrangementPreview();
    }
}

// Game Over and Restart Functions
function endGame() {
    game.stopGameTimer();
    stopWordTimer();
    
    // Hide arrangement section and show input/sequence sections
    game.arrangementSection.style.display = 'none';
    document.querySelector('.word-input-section').style.display = 'block';
    game.wordSequenceElement.style.display = 'flex';
    
    // Clear any arrangement preview
    const previewElement = document.getElementById('arrangement-preview');
    if (previewElement) {
        previewElement.remove();
    }
    
    // Save score based on game mode
    if (game.currentMode === 'number') {
        saveScore('number', game.score, {
            level: game.round - 1 // Current round minus 1 since we started at round 1
        });
    } else if (game.currentMode === 'words') {
        saveScore('word', game.score, {
            wordsCount: game.userWords.length
        });
    }
    
    game.finalScoreElement.textContent = game.score;
    game.timePlayed.textContent = game.timer;
    game.bestStreakElement.textContent = game.bestStreak;
    
    game.showSection('game-over');
}

function restartGame() {
    // Clear all timers
    game.stopGameTimer();
    stopWordTimer();
    if (game.answerTimer) {
        clearInterval(game.answerTimer);
        game.answerTimer = null;
    }
    
    // Remove answer timer display
    const answerTimerElement = document.getElementById('answer-timer');
    if (answerTimerElement && answerTimerElement.parentNode) {
        answerTimerElement.parentNode.removeChild(answerTimerElement);
    }
    
    // Reset game state
    game.score = 0;
    game.timer = 0;
    game.round = 1;
    game.currentStreak = 0;
    game.currentNumbers = [];
    game.wordSequence = [];
    game.userWords = [];
    game.selectedArrangement = [];
    
    // Reset section visibility
    game.arrangementSection.style.display = 'none';
    document.querySelector('.word-input-section').style.display = 'block';
    game.wordSequenceElement.style.display = 'flex';
    
    // Clear any arrangement preview
    const previewElement = document.getElementById('arrangement-preview');
    if (previewElement) {
        previewElement.remove();
    }
    
    // Update display
    game.scoreElement.textContent = '0';
    game.timerElement.textContent = '0';
    game.wordSequence = [];
    game.userWords = [];
    game.selectedArrangement = [];
    game.isShowingNumbers = false;
    game.canSubmitNumbers = false;
    game.answerTimeLeft = 15;
    
    // Update display
    game.scoreElement.textContent = '0';
    game.timerElement.textContent = '0';
    
    // Reset inputs
    game.numberInput.disabled = false;
    game.wordInput.disabled = false;
    
    // Restart same mode
    if (game.currentMode === 'number') {
        startNumberGame();
    } else if (game.currentMode === 'words') {
        startWordGame();
    }
}

function goHome() {
    // Clear all timers
    game.stopGameTimer();
    stopWordTimer();
    if (game.answerTimer) {
        clearInterval(game.answerTimer);
        game.answerTimer = null;
    }
    
    // Remove answer timer display
    const answerTimerElement = document.getElementById('answer-timer');
    if (answerTimerElement && answerTimerElement.parentNode) {
        answerTimerElement.parentNode.removeChild(answerTimerElement);
    }
    
    // Reset everything
    game.score = 0;
    game.timer = 0;
    game.round = 1;
    game.currentStreak = 0;
    game.bestStreak = 0;
    game.currentNumbers = [];
    game.wordSequence = [];
    game.userWords = [];
    game.selectedArrangement = [];
    game.currentMode = null;
    game.isShowingNumbers = false;
    game.canSubmitNumbers = false;
    game.answerTimeLeft = 15;
    
    // Update display
    game.scoreElement.textContent = '0';
    game.timerElement.textContent = '0';
    
    // Reset all section visibility
    game.arrangementSection.style.display = 'none';
    document.querySelector('.word-input-section').style.display = 'block';
    game.wordSequenceElement.style.display = 'flex';
    
    // Clear any arrangement preview
    const previewElement = document.getElementById('arrangement-preview');
    if (previewElement) {
        previewElement.remove();
    }
    
    // Clear inputs
    document.getElementById('min-range').value = '1';
    document.getElementById('max-range').value = '100';
    document.getElementById('memory-time').value = '3';
    document.getElementById('topic-input').value = '';
    document.getElementById('number-input').value = '';
    document.getElementById('word-input').value = '';
    
    // Reset input states
    game.numberInput.disabled = false;
    game.wordInput.disabled = false;
    
    // Clear topic buttons selection
    document.querySelectorAll('.topic-btn').forEach(btn => btn.classList.remove('active'));
    
    // Hide all sections first
    hideAllSections();
    
    // Show mode selection
    game.showSection('mode-selection');
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    game.showSection('mode-selection');
});

// Utility Functions
function hideAllSections() {
    document.querySelectorAll('.game-section').forEach(section => {
        section.style.display = 'none';
    });
}

function showLoading(message = 'Loading...') {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        const loadingText = loadingElement.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
        loadingElement.style.display = 'flex';
        game.showLoading(true);
    }
}

function hideLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
        game.showLoading(false);
    }
}

function showNotification(message, type = 'info') {
    game.showNotification(message, type);
}

// Score Management Functions
async function saveScore(gameType, score, additionalData = {}) {
    try {
        console.log('Saving score:', {gameType, score, additionalData});
        
        const scoreData = {
            gameType: gameType,
            score: score,
            timePlayed: Math.floor((Date.now() - game.startTime) / 1000),
            ...additionalData
        };
        
        console.log('Score data to send:', scoreData);
        
        const response = await fetch('/save-score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(scoreData)
        });
        
        console.log('Save score response status:', response.status);
        
        if (!response.ok) {
            console.error('Save score response not ok:', response.status, response.statusText);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Save score result:', result);
        
        if (result.success) {
            console.log('Score saved successfully');
            showNotification('Score saved to leaderboard!', 'success');
        } else {
            console.error('Failed to save score:', result.error);
            showNotification('Failed to save score: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error saving score:', error);
        showNotification('Error saving score: ' + error.message, 'error');
    }
}

async function loadScores(gameType) {
    try {
        const response = await fetch(`/get-scores/${gameType}`);
        const result = await response.json();
        
        if (result.success) {
            return result.scores;
        } else {
            console.error('Failed to load scores:', result.error);
            return [];
        }
    } catch (error) {
        console.error('Error loading scores:', error);
        return [];
    }
}

function displayScores(gameType, scores) {
    const scoreListElement = document.getElementById(`${gameType}-scores`);
    
    if (!scores || scores.length === 0) {
        scoreListElement.innerHTML = `
            <div class="empty-scoreboard">
                <i class="fas fa-trophy"></i>
                <p>No scores yet. Be the first to play!</p>
            </div>
        `;
        return;
    }
    
    scoreListElement.innerHTML = scores.map((score, index) => {
        const rank = index + 1;
        const detailText = gameType === 'number' ? `Level ${score.level}` : `${score.wordsCount} words`;
        const date = new Date(score.date).toLocaleDateString();
        
        return `
            <div class="score-item">
                <div class="score-rank">#${rank}</div>
                <div class="score-value">${score.score}</div>
                <div class="score-details">${detailText}</div>
                <div class="score-date">${date}</div>
            </div>
        `;
    }).join('');
}

async function showScoreboards() {
    // Show loading
    showLoading();
    
    try {
        // Load scores for both game types
        const [numberScores, wordScores] = await Promise.all([
            loadScores('number'),
            loadScores('word')
        ]);
        
        // Display the scores
        displayScores('number', numberScores);
        displayScores('word', wordScores);
        
        // Hide loading and show scoreboards
        hideLoading();
        game.showSection('scoreboards');
        
    } catch (error) {
        console.error('Error loading scoreboards:', error);
        hideLoading();
        showNotification('Failed to load scoreboards', 'error');
    }
}

async function clearScores(gameType) {
    if (!confirm(`Are you sure you want to clear all ${gameType === 'number' ? 'Number Memory' : 'Word Game'} scores?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/clear-scores/${gameType}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        if (result.success) {
            showNotification(`${gameType === 'number' ? 'Number Memory' : 'Word Game'} scores cleared!`, 'success');
            // Refresh the scoreboard
            showScoreboards();
        } else {
            showNotification('Failed to clear scores', 'error');
        }
    } catch (error) {
        console.error('Error clearing scores:', error);
        showNotification('Failed to clear scores', 'error');
    }
}

// Individual score viewing functions
async function showNumberScores() {
    try {
        showLoading('Loading Number Game scores...');
        
        const response = await fetch('/get-scores/number');
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            hideAllSections();
            document.getElementById('number-scoreboard').style.display = 'block';
            
            const scoresList = document.getElementById('number-scores-list');
            if (data.scores.length === 0) {
                scoresList.innerHTML = '<div class="no-scores">No scores yet. Play the Number Memory Game to set some records!</div>';
            } else {
                scoresList.innerHTML = data.scores.map((score, index) => `
                    <div class="score-item ${index === 0 ? 'top-score' : ''}">
                        <div class="score-rank">#${index + 1}</div>
                        <div class="score-details">
                            <div class="score-value">${score.score} points</div>
                            <div class="score-info">
                                Range: ${score.range} | Memory Time: ${score.memoryTime}s
                            </div>
                            <div class="score-date">${new Date(score.timestamp).toLocaleDateString()}</div>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            showNotification('Failed to load Number Game scores', 'error');
        }
    } catch (error) {
        console.error('Error loading Number Game scores:', error);
        hideLoading();
        showNotification('Failed to load Number Game scores', 'error');
    }
}

async function showWordScores() {
    try {
        showLoading('Loading Word Game scores...');
        
        const response = await fetch('/get-scores/word');
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            hideAllSections();
            document.getElementById('word-scoreboard').style.display = 'block';
            
            const scoresList = document.getElementById('word-scores-list');
            if (data.scores.length === 0) {
                scoresList.innerHTML = '<div class="no-scores">No scores yet. Play the Word Shiritori Game to set some records!</div>';
            } else {
                scoresList.innerHTML = data.scores.map((score, index) => `
                    <div class="score-item ${index === 0 ? 'top-score' : ''}">
                        <div class="score-rank">#${index + 1}</div>
                        <div class="score-details">
                            <div class="score-value">${score.score} points</div>
                            <div class="score-info">
                                Topic: ${score.topic} | Chain Length: ${score.chainLength}
                            </div>
                            <div class="score-date">${new Date(score.timestamp).toLocaleDateString()}</div>
                        </div>
                    </div>
                `).join('');
            }
        } else {
            showNotification('Failed to load Word Game scores', 'error');
        }
    } catch (error) {
        console.error('Error loading Word Game scores:', error);
        hideLoading();
        showNotification('Failed to load Word Game scores', 'error');
    }
}