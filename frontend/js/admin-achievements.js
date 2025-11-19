import { ENDPOINTS } from './config.js';

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

// Load all achievements
async function loadAchievements() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(ENDPOINTS.ADMIN_ACHIEVEMENTS, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to load achievements');
        const data = await response.json();

        displayAchievements(data.achievements);
        document.getElementById('total-count').textContent = `(${data.total})`;

    } catch (error) {
        console.error('Error loading achievements:', error);
        alert('Failed to load achievements');
    }
}

// Display achievements in grid
function displayAchievements(achievements) {
    const grid = document.getElementById('achievements-grid');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');

    loadingState.style.display = 'none';

    if (achievements.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    emptyState.style.display = 'none';

    grid.innerHTML = achievements.map(achievement => {
        const rarityClass = `rarity-${achievement.rarity}`;
        const criteriaText = getCriteriaText(achievement);

        return `
            <div class="achievement-card">
                <div class="achievement-header">
                    <div class="achievement-icon">${achievement.icon}</div>
                    <div class="achievement-info">
                        <div class="achievement-name">${escapeHtml(achievement.name)}</div>
                        <div class="achievement-meta">
                            <span class="meta-badge ${rarityClass}">${achievement.rarity.toUpperCase()}</span>
                            ${achievement.is_hidden ? '<span class="meta-badge hidden-badge">HIDDEN</span>' : ''}
                            ${achievement.xp_reward > 0 ? `<span class="meta-badge" style="background: #fff3e0; color: #f57c00;">+${achievement.xp_reward} XP</span>` : ''}
                        </div>
                    </div>
                </div>

                <div class="achievement-description">
                    ${escapeHtml(achievement.description)}
                </div>

                <div class="achievement-criteria">
                    <strong>Unlock Criteria:</strong> ${criteriaText}
                </div>

                <div class="card-actions">
                    <button class="button button-secondary-outline" onclick="editAchievement(${achievement.id})" style="flex: 1;">
                        ✏️ Edit
                    </button>
                    <button class="button button-danger-outline" onclick="deleteAchievement(${achievement.id}, '${escapeHtml(achievement.name)}')" style="flex: 1;">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Get human-readable criteria text
function getCriteriaText(achievement) {
    const { criteria_type, criteria_value, criteria_exam_type } = achievement;

    switch (criteria_type) {
        case 'quiz_count':
            return `Complete ${criteria_value} quiz${criteria_value > 1 ? 'zes' : ''}`;
        case 'perfect_quiz':
            return `Get ${criteria_value} perfect score${criteria_value > 1 ? 's' : ''} (100%)`;
        case 'high_score':
            return `Score ${criteria_value}% or higher on a quiz`;
        case 'streak':
            return `Maintain a ${criteria_value}-day study streak`;
        case 'level':
            return `Reach level ${criteria_value}`;
        case 'exam_specific':
            const exam = criteria_exam_type ? ` (${criteria_exam_type.toUpperCase()})` : '';
            return `Complete ${criteria_value} ${exam} quiz${criteria_value > 1 ? 'zes' : ''}`;
        default:
            return `${criteria_type}: ${criteria_value}`;
    }
}

// Open create modal
document.getElementById('create-achievement-btn').addEventListener('click', function() {
    document.getElementById('modal-title').textContent = 'Create Achievement';
    document.getElementById('achievement-form').reset();
    document.getElementById('editing-id').value = '';
    document.getElementById('achievement-modal').classList.add('active');
});

// Close modal
function closeModal() {
    document.getElementById('achievement-modal').classList.remove('active');
}

document.getElementById('close-modal').addEventListener('click', closeModal);
document.getElementById('cancel-btn').addEventListener('click', closeModal);

// Show/hide exam type field based on criteria type
document.getElementById('criteria-type').addEventListener('change', function() {
    const examTypeGroup = document.getElementById('exam-type-group');
    if (this.value === 'exam_specific') {
        examTypeGroup.style.display = 'block';
    } else {
        examTypeGroup.style.display = 'none';
        document.getElementById('criteria-exam-type').value = '';
    }
});

// Submit form (create or update)
document.getElementById('achievement-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const token = localStorage.getItem('access_token');
    const editingId = document.getElementById('editing-id').value;

    const achievementData = {
        name: document.getElementById('achievement-name').value,
        description: document.getElementById('achievement-description').value,
        icon: document.getElementById('achievement-icon').value,
        criteria_type: document.getElementById('criteria-type').value,
        criteria_value: parseInt(document.getElementById('criteria-value').value),
        xp_reward: parseInt(document.getElementById('xp-reward').value) || 0,
        is_hidden: document.getElementById('is-hidden').checked,
        rarity: document.getElementById('achievement-rarity').value
    };

    const examType = document.getElementById('criteria-exam-type').value;
    if (achievementData.criteria_type === 'exam_specific' && examType) {
        achievementData.criteria_exam_type = examType;
    }

    try {
        const url = editingId
            ? `${ENDPOINTS.ADMIN_ACHIEVEMENTS}/${editingId}`
            : ENDPOINTS.ADMIN_ACHIEVEMENTS;

        const method = editingId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(achievementData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save achievement');
        }

        alert(editingId ? 'Achievement updated successfully!' : 'Achievement created successfully!');
        closeModal();
        loadAchievements();

    } catch (error) {
        console.error('Error saving achievement:', error);
        alert('Error: ' + error.message);
    }
});

// Edit achievement
window.editAchievement = async function(id) {
    const token = localStorage.getItem('access_token');

    try {
        // Find achievement in current list (we already have it)
        const response = await fetch(ENDPOINTS.ADMIN_ACHIEVEMENTS, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to load achievement');
        const data = await response.json();
        const achievement = data.achievements.find(a => a.id === id);

        if (!achievement) throw new Error('Achievement not found');

        // Populate form
        document.getElementById('modal-title').textContent = 'Edit Achievement';
        document.getElementById('editing-id').value = achievement.id;
        document.getElementById('achievement-name').value = achievement.name;
        document.getElementById('achievement-description').value = achievement.description;
        document.getElementById('achievement-icon').value = achievement.icon;
        document.getElementById('achievement-rarity').value = achievement.rarity;
        document.getElementById('criteria-type').value = achievement.criteria_type;
        document.getElementById('criteria-value').value = achievement.criteria_value;
        document.getElementById('xp-reward').value = achievement.xp_reward;
        document.getElementById('is-hidden').checked = achievement.is_hidden;

        if (achievement.criteria_exam_type) {
            document.getElementById('exam-type-group').style.display = 'block';
            document.getElementById('criteria-exam-type').value = achievement.criteria_exam_type;
        }

        document.getElementById('achievement-modal').classList.add('active');

    } catch (error) {
        console.error('Error loading achievement:', error);
        alert('Failed to load achievement');
    }
};

// Delete achievement
window.deleteAchievement = async function(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"? This will remove it from all users who earned it.`)) {
        return;
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_ACHIEVEMENTS}/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to delete achievement');

        alert('Achievement deleted successfully!');
        loadAchievements();

    } catch (error) {
        console.error('Error deleting achievement:', error);
        alert('Failed to delete achievement');
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
        loadAchievements();
    }
});
