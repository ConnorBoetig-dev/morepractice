import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { redirectIfNotAuthenticated } from './auth.js';

// Protect this page - require authentication
redirectIfNotAuthenticated();

const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const formDiv = document.getElementById('quiz-config-form');
const statsDiv = document.getElementById('exam-stats');
const examSelect = document.getElementById('exam-select');
const quizForm = document.getElementById('quiz-form');

const EXAM_NAMES = {
    'security': {
        name: 'CompTIA Security+',
        description: 'Cybersecurity Fundamentals',
        color: '#dc3545'
    },
    'network': {
        name: 'CompTIA Network+',
        description: 'Networking Fundamentals',
        color: '#007bff'
    },
    'a1101': {
        name: 'CompTIA A+ (Core 1)',
        description: 'Hardware & Networking',
        color: '#28a745'
    },
    'a1102': {
        name: 'CompTIA A+ (Core 2)',
        description: 'Operating Systems & Security',
        color: '#17a2b8'
    }
};

async function loadAvailableExams() {
    try {
        loadingDiv.style.display = 'block';
        errorDiv.style.display = 'none';
        formDiv.style.display = 'none';
        statsDiv.style.display = 'none';

        const response = await apiRequest('GET', ENDPOINTS.EXAMS);
        populateExamDropdown(response.exams);
        displayExamStats(response.exams);

        loadingDiv.style.display = 'none';
        formDiv.style.display = 'block';
        statsDiv.style.display = 'grid';
    } catch (error) {
        console.error('Error loading exams:', error);
        loadingDiv.style.display = 'none';
        errorDiv.style.display = 'block';
        errorDiv.textContent = `Failed to load exams: ${error.message}`;
    }
}

function populateExamDropdown(exams) {
    examSelect.innerHTML = '<option value="">-- Select an exam --</option>';
    exams.sort().forEach(examType => {
        const examInfo = EXAM_NAMES[examType];
        if (examInfo) {
            const option = document.createElement('option');
            option.value = examType;
            option.textContent = `${examInfo.name} - ${examInfo.description}`;
            examSelect.appendChild(option);
        }
    });
}

function displayExamStats(exams) {
    const questionCounts = {
        'security': 987,
        'network': 1141,
        'a1101': 994,
        'a1102': 1048
    };

    const statsHTML = exams.sort().map(examType => {
        const examInfo = EXAM_NAMES[examType];
        const count = questionCounts[examType] || '?';

        return `
            <div class="exam-stat-card">
                <div class="exam-stat-header">
                    <h3>${examInfo.name}</h3>
                    <span class="exam-count">${count} questions</span>
                </div>
                <p class="exam-description">${examInfo.description}</p>
            </div>
        `;
    }).join('');

    statsDiv.innerHTML = statsHTML;
}

quizForm.addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(quizForm);
    const examType = formData.get('exam_type');
    const count = formData.get('count');

    if (!examType) {
        errorDiv.style.display = 'block';
        errorDiv.textContent = 'Please select an exam type';
        return;
    }

    const quizURL = `quiz.html?exam_type=${examType}&count=${count}`;
    window.location.href = quizURL;
});

loadAvailableExams();

// Initialize navigation
import { initializeNavigation } from './navigation.js';
initializeNavigation();
