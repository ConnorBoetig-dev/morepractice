import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { getToken } from './auth.js';

const quizState = {
    examType: null,
    requestedCount: 0,
    questions: [],
    currentIndex: 0,
    userAnswers: [],
    score: 0,
    answered: false,
};

const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const quizContainer = document.getElementById('quiz-container');
const examTitle = document.getElementById('exam-title');
const quizProgress = document.getElementById('quiz-progress');
const domainTag = document.getElementById('domain-tag');
const progressFill = document.getElementById('progress-fill');
const currentQuestionNum = document.getElementById('current-question-num');
const questionText = document.getElementById('question-text');
const answerOptions = document.getElementById('answer-options');
const explanationArea = document.getElementById('explanation-area');
const answerFeedback = document.getElementById('answer-feedback');
const explanationText = document.getElementById('explanation-text');
const checkAnswerBtn = document.getElementById('check-answer-btn');
const nextQuestionBtn = document.getElementById('next-question-btn');
const finishQuizBtn = document.getElementById('finish-quiz-btn');

const EXAM_NAMES = {
    'security': 'CompTIA Security+',
    'network': 'CompTIA Network+',
    'a1101': 'CompTIA A+ (Core 1)',
    'a1102': 'CompTIA A+ (Core 2)'
};

function getURLParameters() {
    const params = new URLSearchParams(window.location.search);
    return {
        exam_type: params.get('exam_type'),
        count: params.get('count') || '10'
    };
}

async function loadQuiz() {
    try {
        const params = getURLParameters();
        if (!params.exam_type) {
            throw new Error('No exam type specified');
        }

        quizState.examType = params.exam_type;
        quizState.requestedCount = parseInt(params.count);

        loadingDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        quizContainer.style.display = 'none';

        const quizURL = `${ENDPOINTS.QUIZ}?exam_type=${params.exam_type}&count=${params.count}`;
        const response = await apiRequest('GET', quizURL);

        quizState.questions = response.questions;
        quizState.userAnswers = new Array(quizState.questions.length).fill(null);
        examTitle.textContent = EXAM_NAMES[quizState.examType] || 'Quiz';

        loadingDiv.style.display = 'none';
        quizContainer.style.display = 'block';
        displayQuestion();
    } catch (error) {
        console.error('Error loading quiz:', error);
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = `Failed to load quiz: ${error.message}`;
    }
}

function displayQuestion() {
    const question = quizState.questions[quizState.currentIndex];
    const questionNumber = quizState.currentIndex + 1;
    const totalQuestions = quizState.questions.length;

    quizState.answered = false;
    quizProgress.textContent = `Question ${questionNumber} of ${totalQuestions}`;
    currentQuestionNum.textContent = questionNumber;
    domainTag.textContent = `Domain ${question.domain}`;

    const progressPercent = ((questionNumber - 1) / totalQuestions) * 100;
    progressFill.style.width = `${progressPercent}%`;

    questionText.textContent = question.question_text;
    displayAnswerOptions(question.options, question.correct_answer);

    explanationArea.style.display = 'none';
    checkAnswerBtn.disabled = true;
    checkAnswerBtn.style.display = 'inline-block';
    nextQuestionBtn.style.display = 'none';
    finishQuizBtn.style.display = 'none';

    window.scrollTo(0, 0);
}

function displayAnswerOptions(options, correctAnswer) {
    answerOptions.innerHTML = '';
    const optionLetters = ['A', 'B', 'C', 'D'];

    optionLetters.forEach(letter => {
        const option = options[letter];
        const button = document.createElement('button');
        button.className = 'answer-option';
        button.dataset.letter = letter;
        button.dataset.explanation = option.explanation;

        button.innerHTML = `
            <span class="option-letter">${letter}</span>
            <span class="option-text">${option.text}</span>
        `;

        button.addEventListener('click', () => selectAnswer(letter));
        answerOptions.appendChild(button);
    });
}

function selectAnswer(selectedLetter) {
    if (quizState.answered) return;

    document.querySelectorAll('.answer-option').forEach(btn => {
        btn.classList.remove('selected');
    });

    const selectedButton = document.querySelector(`[data-letter="${selectedLetter}"]`);
    selectedButton.classList.add('selected');
    checkAnswerBtn.disabled = false;
    quizState.currentSelection = selectedLetter;
}

function checkAnswer() {
    if (!quizState.currentSelection) return;

    const question = quizState.questions[quizState.currentIndex];
    const selectedLetter = quizState.currentSelection;
    const correctLetter = question.correct_answer;
    const isCorrect = selectedLetter === correctLetter;

    quizState.answered = true;
    quizState.userAnswers[quizState.currentIndex] = {
        questionId: question.id,
        questionText: question.question_text,
        domain: question.domain,
        selectedAnswer: selectedLetter,
        correctAnswer: correctLetter,
        isCorrect: isCorrect,
        options: question.options
    };

    if (isCorrect) quizState.score++;

    highlightAnswers(correctLetter, selectedLetter);
    showExplanation(isCorrect, question.options);

    checkAnswerBtn.style.display = 'none';
    if (quizState.currentIndex < quizState.questions.length - 1) {
        nextQuestionBtn.style.display = 'inline-block';
    } else {
        finishQuizBtn.style.display = 'inline-block';
    }
}

function highlightAnswers(correctLetter, selectedLetter) {
    const correctButton = document.querySelector(`[data-letter="${correctLetter}"]`);
    correctButton.classList.add('correct');

    if (selectedLetter !== correctLetter) {
        const incorrectButton = document.querySelector(`[data-letter="${selectedLetter}"]`);
        incorrectButton.classList.add('incorrect');
    }

    document.querySelectorAll('.answer-option').forEach(btn => {
        btn.disabled = true;
    });
}

function showExplanation(isCorrect, options) {
    const question = quizState.questions[quizState.currentIndex];
    const selectedLetter = quizState.currentSelection;
    const correctLetter = question.correct_answer;

    answerFeedback.className = `answer-feedback ${isCorrect ? 'correct-feedback' : 'incorrect-feedback'}`;
    answerFeedback.innerHTML = isCorrect
        ? '<strong>✓ Correct!</strong>'
        : `<strong>✗ Incorrect</strong> - The correct answer is ${correctLetter}`;

    const explanationHTML = `
        <div class="explanation-header">
            <strong>Explanation:</strong>
        </div>
        <div class="explanation-options">
            ${['A', 'B', 'C', 'D'].map(letter => {
                const option = options[letter];
                const isThisCorrect = letter === correctLetter;
                const wasSelected = letter === selectedLetter;

                return `
                    <div class="explanation-option ${isThisCorrect ? 'correct-option' : ''} ${wasSelected ? 'selected-option' : ''}">
                        <div class="explanation-option-header">
                            <span class="option-letter">${letter}</span>
                            <span>${option.text}</span>
                            ${isThisCorrect ? '<span class="correct-badge">✓ Correct</span>' : ''}
                        </div>
                        <div class="explanation-option-text">
                            ${option.explanation}
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;

    explanationText.innerHTML = explanationHTML;
    explanationArea.style.display = 'block';
}

function nextQuestion() {
    quizState.currentIndex++;
    displayQuestion();
}

async function finishQuiz() {
    try {
        const resultsData = {
            examType: quizState.examType,
            examName: EXAM_NAMES[quizState.examType],
            totalQuestions: quizState.questions.length,
            score: quizState.score,
            percentage: Math.round((quizState.score / quizState.questions.length) * 100),
            answers: quizState.userAnswers
        };

        // Submit to backend if user is logged in
        let gamificationData = null;
        const token = getToken();

        if (token) {
            // Prepare submission data for backend
            const submissionData = {
                exam_type: quizState.examType,
                total_questions: quizState.questions.length,
                answers: quizState.userAnswers.map(answer => ({
                    question_id: answer.questionId,
                    user_answer: answer.selectedAnswer,
                    correct_answer: answer.correctAnswer,
                    is_correct: answer.isCorrect,
                    time_spent_seconds: 0  // We don't track individual question time yet
                })),
                time_taken_seconds: 0  // We don't track total time yet
            };

            try {
                const response = await apiRequest('POST', ENDPOINTS.QUIZ_SUBMIT, submissionData, true);
                gamificationData = {
                    xp_earned: response.xp_earned,
                    total_xp: response.total_xp,
                    current_level: response.current_level,
                    previous_level: response.previous_level,
                    level_up: response.level_up,
                    achievements_unlocked: response.achievements_unlocked || []
                };
            } catch (error) {
                console.error('Failed to submit quiz to backend:', error);
                // Continue anyway - we'll show results without gamification
            }
        }

        // Store results and gamification data
        sessionStorage.setItem('quizResults', JSON.stringify(resultsData));
        if (gamificationData) {
            sessionStorage.setItem('gamificationRewards', JSON.stringify(gamificationData));
        }

        window.location.href = 'results.html';
    } catch (error) {
        console.error('Error finishing quiz:', error);
        // Fallback to just showing results
        window.location.href = 'results.html';
    }
}

checkAnswerBtn.addEventListener('click', checkAnswer);
nextQuestionBtn.addEventListener('click', nextQuestion);
finishQuizBtn.addEventListener('click', finishQuiz);

loadQuiz();

// Initialize navigation
import { initializeNavigation } from './navigation.js';
initializeNavigation();
