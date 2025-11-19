import { ENDPOINTS } from './config.js';

let currentPage = 1;
let currentFilters = {};
let selectedCorrectAnswer = 'A';

// Check admin access
async function checkAdminAccess() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }

    try {
        const response = await fetch(ENDPOINTS.ME, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Auth failed');
        const data = await response.json();

        if (!data.is_admin) {
            alert('Access denied. Admin privileges required.');
            window.location.href = 'dashboard.html';
            return false;
        }

        return true;
    } catch (error) {
        console.error('Auth error:', error);
        localStorage.removeItem('token');
        window.location.href = 'login.html';
        return false;
    }
}

// Load questions with pagination
async function loadQuestions(page = 1) {
    const token = localStorage.getItem('access_token');
    const params = new URLSearchParams({
        page: page,
        page_size: 20,
        ...currentFilters
    });

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_QUESTIONS}?${params}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to load questions');
        const data = await response.json();

        displayQuestions(data.questions);
        displayPagination(data);
        document.getElementById('total-count').textContent = `(${data.total})`;

    } catch (error) {
        console.error('Error loading questions:', error);
        alert('Failed to load questions');
    }
}

// Display questions in table
function displayQuestions(questions) {
    const tbody = document.getElementById('questions-tbody');
    const table = document.getElementById('questions-table');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');

    loadingState.style.display = 'none';

    if (questions.length === 0) {
        table.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    table.style.display = 'table';
    emptyState.style.display = 'none';

    tbody.innerHTML = questions.map(q => {
        const examBadge = `badge-${q.exam_type}`;
        return `
            <tr>
                <td><strong>${q.question_id}</strong></td>
                <td>
                    <div class="question-text" title="${escapeHtml(q.question_text)}">
                        ${escapeHtml(q.question_text)}
                    </div>
                </td>
                <td><span class="badge ${examBadge}">${q.exam_type.toUpperCase()}</span></td>
                <td>${q.domain}</td>
                <td><strong>${q.correct_answer}</strong></td>
                <td>
                    <div class="actions">
                        <button class="btn-icon" onclick="editQuestion(${q.id})" title="Edit">✏️</button>
                        <button class="btn-icon" onclick="deleteQuestion(${q.id}, '${escapeHtml(q.question_id)}')" title="Delete">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// Display pagination
function displayPagination(data) {
    const pagination = document.getElementById('pagination');
    const { page, total_pages, total } = data;

    if (total_pages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = `
        <button class="page-btn" ${page === 1 ? 'disabled' : ''} onclick="changePage(${page - 1})">
            ← Previous
        </button>
        <span style="margin: 0 15px;">Page ${page} of ${total_pages}</span>
        <button class="page-btn" ${page === total_pages ? 'disabled' : ''} onclick="changePage(${page + 1})">
            Next →
        </button>
    `;

    pagination.innerHTML = html;
}

// Change page
window.changePage = function(page) {
    currentPage = page;
    loadQuestions(page);
};

// Apply filters
document.getElementById('apply-filters').addEventListener('click', function() {
    const search = document.getElementById('search-input').value;
    const examType = document.getElementById('exam-filter').value;
    const domain = document.getElementById('domain-filter').value;

    currentFilters = {};
    if (search) currentFilters.search = search;
    if (examType) currentFilters.exam_type = examType;
    if (domain) currentFilters.domain = domain;

    currentPage = 1;
    loadQuestions(1);
});

// Open create modal
document.getElementById('create-question-btn').addEventListener('click', function() {
    document.getElementById('modal-title').textContent = 'Add New Question';
    document.getElementById('question-form').reset();
    document.getElementById('editing-id').value = '';
    selectedCorrectAnswer = 'A';
    updateCorrectAnswerUI();
    document.getElementById('question-modal').classList.add('active');
});

// Close modal
function closeModal() {
    document.getElementById('question-modal').classList.remove('active');
}

document.getElementById('close-modal').addEventListener('click', closeModal);
document.getElementById('cancel-btn').addEventListener('click', closeModal);

// Correct answer selection
document.querySelectorAll('.correct-indicator').forEach(indicator => {
    indicator.addEventListener('click', function() {
        selectedCorrectAnswer = this.dataset.option;
        document.getElementById('correct-answer').value = selectedCorrectAnswer;
        updateCorrectAnswerUI();
    });
});

function updateCorrectAnswerUI() {
    document.querySelectorAll('.correct-indicator').forEach(indicator => {
        if (indicator.dataset.option === selectedCorrectAnswer) {
            indicator.classList.add('selected');
        } else {
            indicator.classList.remove('selected');
        }
    });
}

// Submit form (create or update)
document.getElementById('question-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const token = localStorage.getItem('access_token');
    const editingId = document.getElementById('editing-id').value;

    const questionData = {
        question_id: document.getElementById('question-id').value,
        exam_type: document.getElementById('exam-type').value,
        domain: document.getElementById('domain').value,
        question_text: document.getElementById('question-text').value,
        correct_answer: selectedCorrectAnswer,
        options: {
            A: {
                text: document.getElementById('option-a-text').value,
                explanation: document.getElementById('option-a-explanation').value
            },
            B: {
                text: document.getElementById('option-b-text').value,
                explanation: document.getElementById('option-b-explanation').value
            },
            C: {
                text: document.getElementById('option-c-text').value,
                explanation: document.getElementById('option-c-explanation').value
            },
            D: {
                text: document.getElementById('option-d-text').value,
                explanation: document.getElementById('option-d-explanation').value
            }
        }
    };

    try {
        const url = editingId
            ? `${ENDPOINTS.ADMIN_QUESTIONS}/${editingId}`
            : ENDPOINTS.ADMIN_QUESTIONS;

        const method = editingId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(questionData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save question');
        }

        alert(editingId ? 'Question updated successfully!' : 'Question created successfully!');
        closeModal();
        loadQuestions(currentPage);

    } catch (error) {
        console.error('Error saving question:', error);
        alert('Error: ' + error.message);
    }
});

// Edit question
window.editQuestion = async function(id) {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_QUESTIONS}/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to load question');
        const question = await response.json();

        // Populate form
        document.getElementById('modal-title').textContent = 'Edit Question';
        document.getElementById('editing-id').value = question.id;
        document.getElementById('question-id').value = question.question_id;
        document.getElementById('exam-type').value = question.exam_type;
        document.getElementById('domain').value = question.domain;
        document.getElementById('question-text').value = question.question_text;

        // Populate options
        ['A', 'B', 'C', 'D'].forEach(letter => {
            const option = question.options[letter];
            document.getElementById(`option-${letter.toLowerCase()}-text`).value = option.text;
            document.getElementById(`option-${letter.toLowerCase()}-explanation`).value = option.explanation;
        });

        selectedCorrectAnswer = question.correct_answer;
        updateCorrectAnswerUI();

        document.getElementById('question-modal').classList.add('active');

    } catch (error) {
        console.error('Error loading question:', error);
        alert('Failed to load question');
    }
};

// Delete question
window.deleteQuestion = async function(id, questionId) {
    if (!confirm(`Are you sure you want to delete question "${questionId}"? This cannot be undone.`)) {
        return;
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_QUESTIONS}/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to delete question');

        alert('Question deleted successfully!');
        loadQuestions(currentPage);

    } catch (error) {
        console.error('Error deleting question:', error);
        alert('Failed to delete question');
    }
};

// Logout
document.getElementById('nav-logout').addEventListener('click', function() {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
});

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
checkAdminAccess().then(isAdmin => {
    if (isAdmin) {
        loadQuestions(1);
    }
});
