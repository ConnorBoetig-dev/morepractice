/**
 * LEADERBOARDS PAGE LOGIC
 * Display 5 different leaderboard types
 */

import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { removeToken, isAuthenticated } from './auth.js';
import { formatNumber } from './utils.js';

// Leaderboard is PUBLIC - no authentication required
// Optional: Show user's position if they are logged in

// DOM Elements
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const leaderboardContainer = document.getElementById('leaderboard-container');
const emptyState = document.getElementById('empty-state');

// Leaderboard tabs
const tabs = document.querySelectorAll('.leaderboard-tab');
let currentLeaderboard = 'xp';

// Initialize
loadLeaderboard('xp');

// Tab switching
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const leaderboardType = tab.dataset.leaderboard;

        // Update active tab
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Load selected leaderboard
        currentLeaderboard = leaderboardType;
        loadLeaderboard(leaderboardType);
    });
});

async function loadLeaderboard(type) {
    try {
        loading.style.display = 'block';
        leaderboardContainer.style.display = 'none';
        emptyState.style.display = 'none';
        errorMessage.style.display = 'none';

        console.log('📡 Fetching leaderboard:', type);

        let endpoint = '';
        switch (type) {
            case 'xp':
                endpoint = ENDPOINTS.LEADERBOARD_XP;
                break;
            case 'quiz-count':
                endpoint = ENDPOINTS.LEADERBOARD_QUIZ_COUNT;
                break;
            case 'accuracy':
                endpoint = ENDPOINTS.LEADERBOARD_ACCURACY;
                break;
            case 'streak':
                endpoint = ENDPOINTS.LEADERBOARD_STREAK;
                break;
        }

        const response = await apiRequest('GET', endpoint, null, false);
        const leaderboard = response.entries || [];

        console.log('✓ Loaded', leaderboard.length, 'entries');
        console.log('📊 Leaderboard data:', leaderboard);

        if (leaderboard.length === 0) {
            loading.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        // Render leaderboard
        const html = renderLeaderboard(leaderboard, type);
        console.log('✓ Generated HTML:', html.substring(0, 200) + '...');
        leaderboardContainer.innerHTML = html;

        console.log('✓ Setting display to block');
        loading.style.display = 'none';
        leaderboardContainer.style.display = 'block';

    } catch (error) {
        console.error('❌ Failed to load leaderboard:', error);
        loading.style.display = 'none';
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';
    }
}

function renderLeaderboard(leaderboard, type) {
    return `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Username</th>
                    <th>Level</th>
                    ${getStatsColumns(type)}
                </tr>
            </thead>
            <tbody>
                ${leaderboard.map(entry => renderEntry(entry, type)).join('')}
            </tbody>
        </table>
    `;
}

function getStatsColumns(type) {
    switch (type) {
        case 'xp':
            return '<th>XP</th>';
        case 'quiz-count':
            return '<th>Quizzes</th>';
        case 'accuracy':
            return '<th>Accuracy</th>';
        case 'streak':
            return '<th>Streak</th>';
        default:
            return '';
    }
}

function renderEntry(entry, type) {
    const rankClass = getRankClass(entry.rank);

    return `
        <tr>
            <td><span class="leaderboard-rank ${rankClass}">${getRankDisplay(entry.rank)}</span></td>
            <td class="leaderboard-username">${entry.username}</td>
            <td>Level ${entry.level}</td>
            ${getStatsValues(entry, type)}
        </tr>
    `;
}

function getStatsValues(entry, type) {
    switch (type) {
        case 'xp':
            return `<td class="leaderboard-stat-highlight">${formatNumber(entry.score)} XP</td>`;
        case 'quiz-count':
            return `<td class="leaderboard-stat-highlight">${formatNumber(entry.score)}</td>`;
        case 'accuracy':
            return `<td class="leaderboard-stat-highlight">${entry.score}%</td>`;
        case 'streak':
            return `<td class="leaderboard-stat-highlight">${formatNumber(entry.score)} days</td>`;
        default:
            return '';
    }
}

function getRankClass(rank) {
    if (rank === 1) return 'top-1';
    if (rank === 2) return 'top-2';
    if (rank === 3) return 'top-3';
    return '';
}

function getRankDisplay(rank) {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
}

// Initialize navigation
import { initializeNavigation } from './navigation.js';
initializeNavigation();
