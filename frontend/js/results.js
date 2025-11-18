import { showAchievementModal, showLevelUpModal, formatNumber } from './utils.js';

const examName = document.getElementById('exam-name');
const scoreNumber = document.getElementById('score-number');
const scorePercentage = document.getElementById('score-percentage');
const scoreStatus = document.getElementById('score-status');
const correctCount = document.getElementById('correct-count');
const incorrectCount = document.getElementById('incorrect-count');
const totalQuestions = document.getElementById('total-questions');
const reviewAnswersBtn = document.getElementById('review-answers-btn');
const answerReviewSection = document.getElementById('answer-review-section');
const reviewContainer = document.getElementById('review-container');

// Gamification elements
const gamificationRewards = document.getElementById('gamification-rewards');
const xpEarnedElement = document.getElementById('xp-earned');
const levelUpReward = document.getElementById('level-up-reward');
const levelUpText = document.getElementById('level-up-text');
const levelUpDetail = document.getElementById('level-up-detail');
const achievementsReward = document.getElementById('achievements-reward');
const achievementsList = document.getElementById('achievements-list');

function loadResults() {
    const resultsJSON = sessionStorage.getItem('quizResults');
    if (!resultsJSON) {
        window.location.href = 'quiz-select.html';
        return;
    }

    const results = JSON.parse(resultsJSON);
    displayResults(results);

    // Load and display gamification rewards if available
    const gamificationJSON = sessionStorage.getItem('gamificationRewards');
    if (gamificationJSON) {
        const gamification = JSON.parse(gamificationJSON);
        displayGamificationRewards(gamification);

        // Clean up sessionStorage
        sessionStorage.removeItem('gamificationRewards');
    }
}

function displayResults(results) {
    examName.textContent = results.examName;
    scoreNumber.textContent = `${results.score}/${results.totalQuestions}`;
    scorePercentage.textContent = `${results.percentage}%`;
    correctCount.textContent = results.score;
    incorrectCount.textContent = results.totalQuestions - results.score;
    totalQuestions.textContent = results.totalQuestions;

    const passed = results.percentage >= 70;
    scoreStatus.className = `score-status ${passed ? 'pass' : 'fail'}`;
    scoreStatus.innerHTML = passed
        ? '<strong>✓ Pass</strong><span>Great job!</span>'
        : '<strong>✗ Needs Improvement</strong><span>Keep practicing!</span>';

    window.quizResults = results;
}

function reviewAnswers() {
    const results = window.quizResults;

    const reviewHTML = results.answers.map((answer, index) => {
        const questionNumber = index + 1;
        const isCorrect = answer.isCorrect;

        return `
            <div class="review-question ${isCorrect ? 'review-correct' : 'review-incorrect'}">
                <div class="review-question-header">
                    <div class="review-question-number">
                        <span>Question ${questionNumber}</span>
                        <span class="review-domain">Domain ${answer.domain}</span>
                    </div>
                    <div class="review-result-badge ${isCorrect ? 'correct' : 'incorrect'}">
                        ${isCorrect ? '✓ Correct' : '✗ Incorrect'}
                    </div>
                </div>

                <div class="review-question-text">
                    <p><strong>${answer.questionText}</strong></p>
                </div>

                <div class="review-answer-summary">
                    <div class="review-answer-item ${isCorrect ? 'correct' : 'incorrect'}">
                        <strong>Your Answer:</strong>
                        <span>${answer.selectedAnswer} - ${answer.options[answer.selectedAnswer].text}</span>
                    </div>
                    ${!isCorrect ? `
                        <div class="review-answer-item correct">
                            <strong>Correct Answer:</strong>
                            <span>${answer.correctAnswer} - ${answer.options[answer.correctAnswer].text}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="review-explanations">
                    <strong>Explanations:</strong>
                    ${['A', 'B', 'C', 'D'].map(letter => {
                        const option = answer.options[letter];
                        const isThisCorrect = letter === answer.correctAnswer;
                        const wasSelected = letter === answer.selectedAnswer;

                        return `
                            <div class="review-explanation-option ${isThisCorrect ? 'correct-option' : ''} ${wasSelected && !isCorrect ? 'incorrect-option' : ''}">
                                <div class="review-explanation-header">
                                    <span class="option-letter">${letter}</span>
                                    <span>${option.text}</span>
                                    ${isThisCorrect ? '<span class="correct-badge">✓</span>' : ''}
                                </div>
                                <div class="review-explanation-text">
                                    ${option.explanation}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }).join('');

    reviewContainer.innerHTML = reviewHTML;
    answerReviewSection.style.display = 'block';
    answerReviewSection.scrollIntoView({ behavior: 'smooth' });

    reviewAnswersBtn.textContent = 'Hide Review';
    reviewAnswersBtn.onclick = hideReview;
}

function hideReview() {
    answerReviewSection.style.display = 'none';
    reviewAnswersBtn.textContent = 'Review Answers';
    reviewAnswersBtn.onclick = reviewAnswers;
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function displayGamificationRewards(gamification) {
    // Display XP earned
    xpEarnedElement.textContent = `+${formatNumber(gamification.xp_earned)} XP`;

    // Display level up if applicable
    if (gamification.level_up) {
        levelUpReward.style.display = 'flex';
        levelUpDetail.textContent = `Level ${gamification.previous_level} → Level ${gamification.current_level}`;

        // Show level up modal after a short delay
        setTimeout(() => {
            showLevelUpModal(gamification.current_level, gamification.total_xp);
        }, 1000);
    }

    // Display achievements unlocked
    if (gamification.achievements_unlocked && gamification.achievements_unlocked.length > 0) {
        achievementsReward.style.display = 'block';

        achievementsList.innerHTML = gamification.achievements_unlocked.map(achievement => `
            <div class="achievement-unlocked-item">
                <div class="achievement-unlocked-badge">🏆</div>
                <div class="achievement-unlocked-details">
                    <div class="achievement-unlocked-name">${achievement.name}</div>
                    <div class="achievement-unlocked-description">${achievement.description}</div>
                    <div class="achievement-unlocked-xp">+${achievement.xp_reward} XP</div>
                </div>
            </div>
        `).join('');

        // Show achievement modals one by one with delays
        gamification.achievements_unlocked.forEach((achievement, index) => {
            setTimeout(() => {
                showAchievementModal(achievement);
            }, 2000 + (index * 3000)); // First after 2s, then 3s apart
        });
    }

    // Show the rewards section
    gamificationRewards.style.display = 'block';
}

reviewAnswersBtn.addEventListener('click', reviewAnswers);
loadResults();

// Initialize navigation
import { initializeNavigation } from './navigation.js';
initializeNavigation();
