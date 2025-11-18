/**
 * ACHIEVEMENTS PAGE LOGIC
 * Displays all achievements with progress tracking
 */

import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { redirectIfNotAuthenticated, removeToken } from './auth.js';
import { createProgressBar, formatNumber } from './utils.js';

redirectIfNotAuthenticated();

// DOM Elements
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const achievementGrid = document.getElementById('achievement-grid');
const achievementSummary = document.getElementById('achievement-summary');
const emptyState = document.getElementById('empty-state');

// Summary stats
const earnedCount = document.getElementById('earned-count');
const totalCount = document.getElementById('total-count');
const completionPercentage = document.getElementById('completion-percentage');
const totalXp = document.getElementById('total-xp');

// Load achievements
(async function loadAchievements() {
    try {
        console.log('📡 Fetching achievements...');

        // Fetch achievements with user progress
        const achievements = await apiRequest('GET', ENDPOINTS.ACHIEVEMENTS_ME, null, true);

        console.log('✓ Loaded', achievements.length, 'achievements');

        if (achievements.length === 0) {
            loading.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        // Calculate stats
        const earned = achievements.filter(a => a.is_earned).length;
        const total = achievements.length;
        const completion = Math.round((earned / total) * 100);
        const xpEarned = achievements
            .filter(a => a.is_earned)
            .reduce((sum, a) => sum + a.xp_reward, 0);

        // Display stats
        earnedCount.textContent = formatNumber(earned);
        totalCount.textContent = formatNumber(total);
        completionPercentage.textContent = `${completion}%`;
        totalXp.textContent = formatNumber(xpEarned);

        // Render achievements
        achievementGrid.innerHTML = achievements.map(achievement => renderAchievement(achievement)).join('');

        // Show UI
        loading.style.display = 'none';
        achievementSummary.style.display = 'block';
        achievementGrid.style.display = 'grid';

    } catch (error) {
        console.error('❌ Failed to load achievements:', error);
        loading.style.display = 'none';
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';

        if (error.message.includes('Unauthorized')) {
            setTimeout(() => window.location.href = '/login.html', 2000);
        }
    }
})();

function renderAchievement(achievement) {
    const earnedClass = achievement.is_earned ? 'earned' : 'locked';
    const progressPercent = Math.round(achievement.progress_percentage || 0);

    return `
        <div class="achievement-card ${earnedClass}">
            <div class="achievement-badge">
                ${achievement.is_earned ? '🏆' : '🔒'}
            </div>
            <div class="achievement-name">${achievement.name}</div>
            <div class="achievement-description">${achievement.description}</div>
            <div class="achievement-xp">+${achievement.xp_reward} XP</div>

            ${!achievement.is_earned ? `
                <div class="labeled-progress">
                    <div class="progress-label">
                        <span>Progress</span>
                        <span>${achievement.progress || 0}/${achievement.criteria_value}</span>
                    </div>
                    ${createProgressBar(progressPercent, 'progress-primary')}
                </div>
            ` : ''}

            <div class="achievement-status ${achievement.is_earned ? 'earned' : 'locked'}">
                ${achievement.is_earned ? '✓ Unlocked' : `${progressPercent}% Complete`}
            </div>
        </div>
    `;
}

// Initialize navigation
import { initializeNavigation } from './navigation.js';
initializeNavigation();
