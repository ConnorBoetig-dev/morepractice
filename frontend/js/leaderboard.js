// Leaderboard Frontend Integration
// Integrates with backend leaderboard API endpoints

const API_BASE_URL = 'http://localhost:8000/api/v1';

// State
let currentLeaderboardType = 'xp';
let currentUserId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadLeaderboard();
});

// Check authentication
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    try {
        // Get current user info
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Authentication failed');
        }

        const data = await response.json();
        currentUserId = data.user_id;
        document.getElementById('username').textContent = data.username;
    } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    window.location.href = 'login.html';
}

// Switch leaderboard type
function switchLeaderboard(type) {
    currentLeaderboardType = type;

    // Update active tab
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-type="${type}"]`).classList.add('active');

    // Show/hide filters based on leaderboard type
    const filtersDiv = document.getElementById('filters');
    const examFilter = document.getElementById('examFilter');
    const minQuizzesFilter = document.getElementById('minQuizzesFilter');
    const timePeriodSelect = document.getElementById('timePeriod');

    if (type === 'streak') {
        filtersDiv.style.display = 'none';
    } else {
        filtersDiv.style.display = 'flex';
    }

    // Show exam filter only for exam leaderboard
    examFilter.style.display = type === 'exam' ? 'block' : 'none';

    // Show min quizzes filter only for accuracy
    minQuizzesFilter.style.display = type === 'accuracy' ? 'block' : 'none';

    // Reset time period to all_time
    timePeriodSelect.value = 'all_time';

    loadLeaderboard();
}

// Load leaderboard data
async function loadLeaderboard() {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const table = document.getElementById('leaderboardTable');
    const currentUserEntry = document.getElementById('currentUserEntry');

    // Show loading
    loading.style.display = 'block';
    error.style.display = 'none';
    table.style.display = 'none';
    currentUserEntry.style.display = 'none';

    try {
        const token = localStorage.getItem('token');
        let url = `${API_BASE_URL}/leaderboard/`;

        // Build URL based on leaderboard type
        if (currentLeaderboardType === 'exam') {
            const examType = document.getElementById('examType').value;
            url += `exam/${examType}`;
        } else {
            url += currentLeaderboardType;
        }

        // Add query parameters
        const params = new URLSearchParams();
        params.append('limit', '100');

        // Add time period (except for streak)
        if (currentLeaderboardType !== 'streak') {
            const timePeriod = document.getElementById('timePeriod').value;
            params.append('time_period', timePeriod);
        }

        // Add minimum quizzes for accuracy
        if (currentLeaderboardType === 'accuracy') {
            const minQuizzes = document.getElementById('minQuizzes').value;
            params.append('minimum_quizzes', minQuizzes);
        }

        url += '?' + params.toString();

        // Fetch leaderboard data
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch leaderboard: ${response.status}`);
        }

        const data = await response.json();
        displayLeaderboard(data);

    } catch (err) {
        console.error('Error loading leaderboard:', err);
        loading.style.display = 'none';
        error.style.display = 'block';
        error.textContent = `Error loading leaderboard: ${err.message}`;
    }
}

// Display leaderboard data
function displayLeaderboard(data) {
    const loading = document.getElementById('loading');
    const table = document.getElementById('leaderboardTable');
    const tbody = document.getElementById('leaderboardBody');
    const currentUserEntry = document.getElementById('currentUserEntry');
    const currentUserBody = document.getElementById('currentUserBody');

    // Hide loading
    loading.style.display = 'none';

    // Update stats
    document.getElementById('totalUsers').textContent = data.total_users || 0;

    if (data.current_user_entry) {
        document.getElementById('yourRank').textContent = `#${data.current_user_entry.rank}`;
        document.getElementById('yourScore').textContent = formatScore(data.current_user_entry.score);
    } else {
        // Check if user is in the top entries
        const userEntry = data.entries.find(e => e.is_current_user);
        if (userEntry) {
            document.getElementById('yourRank').textContent = `#${userEntry.rank}`;
            document.getElementById('yourScore').textContent = formatScore(userEntry.score);
        } else {
            document.getElementById('yourRank').textContent = '-';
            document.getElementById('yourScore').textContent = '-';
        }
    }

    // Check if leaderboard is empty
    if (!data.entries || data.entries.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    <h3>No entries yet</h3>
                    <p>Be the first to appear on this leaderboard!</p>
                </td>
            </tr>
        `;
        table.style.display = 'table';
        return;
    }

    // Populate leaderboard entries
    tbody.innerHTML = '';
    data.entries.forEach(entry => {
        tbody.appendChild(createLeaderboardRow(entry));
    });

    // Show table
    table.style.display = 'table';

    // Show current user entry if not in top list
    if (data.current_user_entry && !data.entries.find(e => e.is_current_user)) {
        currentUserBody.innerHTML = '';
        currentUserBody.appendChild(createLeaderboardRow(data.current_user_entry));
        currentUserEntry.style.display = 'block';
    }
}

// Create leaderboard row
function createLeaderboardRow(entry) {
    const tr = document.createElement('tr');
    if (entry.is_current_user) {
        tr.classList.add('current-user');
    }

    // Rank cell
    const rankTd = document.createElement('td');
    const rankSpan = document.createElement('span');
    rankSpan.className = 'rank';
    if (entry.rank === 1) {
        rankSpan.classList.add('top-1');
        rankSpan.textContent = '🥇';
    } else if (entry.rank === 2) {
        rankSpan.classList.add('top-2');
        rankSpan.textContent = '🥈';
    } else if (entry.rank === 3) {
        rankSpan.classList.add('top-3');
        rankSpan.textContent = '🥉';
    } else {
        rankSpan.textContent = `#${entry.rank}`;
    }
    rankTd.appendChild(rankSpan);

    // Player cell
    const playerTd = document.createElement('td');
    const playerDiv = document.createElement('div');
    playerDiv.className = 'player';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    if (entry.avatar_url) {
        const img = document.createElement('img');
        img.src = entry.avatar_url;
        img.alt = entry.username;
        avatarDiv.appendChild(img);
    } else {
        avatarDiv.textContent = entry.username.charAt(0).toUpperCase();
    }

    const playerInfo = document.createElement('div');
    playerInfo.className = 'player-info';
    const playerName = document.createElement('span');
    playerName.className = 'player-name';
    playerName.textContent = entry.username;
    playerInfo.appendChild(playerName);

    if (entry.is_current_user) {
        const badge = document.createElement('span');
        badge.className = 'player-badge';
        badge.textContent = 'YOU';
        playerInfo.appendChild(badge);
    }

    playerDiv.appendChild(avatarDiv);
    playerDiv.appendChild(playerInfo);
    playerTd.appendChild(playerDiv);

    // Score cell
    const scoreTd = document.createElement('td');
    const scoreSpan = document.createElement('span');
    scoreSpan.className = 'score';
    scoreSpan.textContent = formatScore(entry.score);
    scoreTd.appendChild(scoreSpan);

    // Level cell
    const levelTd = document.createElement('td');
    levelTd.className = 'level';
    const levelBadge = document.createElement('span');
    levelBadge.className = 'level-badge';
    levelBadge.textContent = `Lv ${entry.level}`;
    levelTd.appendChild(levelBadge);

    tr.appendChild(rankTd);
    tr.appendChild(playerTd);
    tr.appendChild(scoreTd);
    tr.appendChild(levelTd);

    return tr;
}

// Format score based on leaderboard type
function formatScore(score) {
    switch (currentLeaderboardType) {
        case 'xp':
            return `${score} XP`;
        case 'quiz-count':
            return `${score} quizzes`;
        case 'accuracy':
            return `${score}%`;
        case 'streak':
            return `${score} days`;
        case 'exam':
            return `${score} quizzes`;
        default:
            return score;
    }
}

// Make functions available globally
window.switchLeaderboard = switchLeaderboard;
window.logout = logout;
