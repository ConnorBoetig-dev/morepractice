import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { redirectIfNotAuthenticated } from './auth.js';

// Protect this page - require authentication
redirectIfNotAuthenticated();

const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const reviewContent = document.getElementById('review-content');
const reviewTitle = document.getElementById('review-title');
const reviewDate = document.getElementById('review-date');
const scoreDisplay = document.getElementById('score-display');
const questionsDisplay = document.getElementById('questions-display');
const timeDisplay = document.getElementById('time-display');
const xpDisplay = document.getElementById('xp-display');
const domainPerformanceSection = document.getElementById('domain-performance-section');
const domainGrid = document.getElementById('domain-grid');
const questionsContainer = document.getElementById('questions-container');

const EXAM_NAMES = {
    'security': 'CompTIA Security+',
    'network': 'CompTIA Network+',
    'a1101': 'CompTIA A+ (Core 1)',
    'a1102': 'CompTIA A+ (Core 2)'
};

function getAttemptId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('attempt_id');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatTime(seconds) {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
}

function getAccuracyColor(percentage) {
    if (percentage >= 90) return '#28a745';
    if (percentage >= 80) return '#ffc107';
    if (percentage >= 70) return '#fd7e14';
    return '#dc3545';
}

async function loadQuizReview() {
    try {
        const attemptId = getAttemptId();
        if (!attemptId) {
            throw new Error('No quiz attempt ID provided');
        }

        loadingDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        reviewContent.style.display = 'none';

        const reviewURL = `${ENDPOINTS.QUIZ_REVIEW}/${attemptId}`;
        const review = await apiRequest('GET', reviewURL);

        displayReview(review);

        loadingDiv.style.display = 'none';
        reviewContent.style.display = 'block';
    } catch (error) {
        console.error('Error loading quiz review:', error);
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = `Failed to load quiz review: ${error.message}`;
    }
}

function displayReview(review) {
    // Set header information
    reviewTitle.textContent = `${EXAM_NAMES[review.exam_type] || review.exam_type} - Quiz Review`;
    reviewDate.textContent = `Completed on ${formatDate(review.completed_at)}`;

    // Set stats
    scoreDisplay.textContent = `${review.score_percentage.toFixed(1)}%`;
    scoreDisplay.style.color = getAccuracyColor(review.score_percentage);
    questionsDisplay.textContent = `${review.correct_answers}/${review.total_questions}`;
    timeDisplay.textContent = formatTime(review.time_taken_seconds);
    xpDisplay.textContent = `${review.xp_earned} XP`;

    // Display domain performance
    if (review.domain_performance && review.domain_performance.length > 0) {
        displayDomainPerformance(review.domain_performance);
    }

    // Display questions
    displayQuestions(review.questions);
}

function displayDomainPerformance(domainPerformance) {
    domainPerformanceSection.style.display = 'block';

    const domainHTML = domainPerformance.map(domain => {
        const accuracy = domain.accuracy_percentage.toFixed(0);
        const color = getAccuracyColor(domain.accuracy_percentage);

        return `
            <div class="domain-card">
                <div class="domain-name">Domain ${domain.domain}</div>
                <div class="domain-accuracy" style="color: ${color};">${accuracy}%</div>
                <div class="domain-questions">${domain.correct_answers}/${domain.total_questions} correct</div>
            </div>
        `;
    }).join('');

    domainGrid.innerHTML = domainHTML;
}

function displayQuestions(questions) {
    const questionsHTML = questions.map((q, index) => {
        const isCorrect = q.is_correct;
        const resultClass = isCorrect ? 'result-correct' : 'result-incorrect';
        const resultText = isCorrect ? '✓ Correct' : '✗ Incorrect';

        // Build options HTML
        const optionsHTML = Object.entries(q.options).map(([key, option]) => {
            const isUserAnswer = key === q.user_answer;
            const isCorrectAnswer = key === q.correct_answer;

            let optionClass = 'review-option';
            let badges = [];

            if (isCorrectAnswer) {
                optionClass += ' correct-answer';
                badges.push('<span class="option-badge badge-correct">CORRECT ANSWER</span>');
            }

            if (isUserAnswer) {
                if (isCorrect) {
                    badges.push('<span class="option-badge badge-your-answer">YOUR ANSWER</span>');
                } else {
                    optionClass += ' user-incorrect';
                    badges.push('<span class="option-badge badge-your-answer">YOUR ANSWER</span>');
                }
            }

            return `
                <div class="${optionClass}">
                    <div class="option-header">
                        <span class="option-text">${key}. ${escapeHtml(option.text)}</span>
                        ${badges.join(' ')}
                    </div>
                    <div class="option-explanation">
                        ${escapeHtml(option.explanation)}
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="review-question">
                <div class="question-header">
                    <span class="question-number">Question ${index + 1}</span>
                    <div style="display: flex; gap: 10px;">
                        <span class="question-domain">Domain ${q.domain}</span>
                        <span class="question-result ${resultClass}">${resultText}</span>
                    </div>
                </div>
                <div class="question-text">${escapeHtml(q.question_text)}</div>
                <div class="options-container">
                    ${optionsHTML}
                </div>
            </div>
        `;
    }).join('');

    questionsContainer.innerHTML = questionsHTML;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
loadQuizReview();

// Initialize navigation
import { initializeNavigation } from './navigation.js';
initializeNavigation();
