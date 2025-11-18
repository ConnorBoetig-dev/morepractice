/**
 * UTILITY FUNCTIONS
 * Shared utilities for gamification features
 */

// ============================================
// XP & LEVEL CALCULATIONS
// ============================================

/**
 * Calculate XP required for a specific level
 * Formula: (level - 1)^2 * 100
 */
export function xpForLevel(level) {
    return Math.pow(level - 1, 2) * 100;
}

/**
 * Calculate XP needed to reach next level
 */
export function xpToNextLevel(currentXp, currentLevel) {
    const nextLevelXp = xpForLevel(currentLevel + 1);
    return nextLevelXp - currentXp;
}

/**
 * Calculate progress percentage toward next level
 */
export function levelProgressPercentage(currentXp, currentLevel) {
    const currentLevelXp = xpForLevel(currentLevel);
    const nextLevelXp = xpForLevel(currentLevel + 1);
    const xpIntoLevel = currentXp - currentLevelXp;
    const xpNeeded = nextLevelXp - currentLevelXp;
    return (xpIntoLevel / xpNeeded) * 100;
}

// ============================================
// PROGRESS BAR RENDERING
// ============================================

/**
 * Create a progress bar HTML element
 * @param {number} percentage - Progress percentage (0-100)
 * @param {string} colorClass - CSS class for color (e.g., 'progress-primary', 'progress-success')
 * @returns {string} HTML string
 */
export function createProgressBar(percentage, colorClass = 'progress-primary') {
    const clampedPercentage = Math.min(Math.max(percentage, 0), 100);
    return `
        <div class="progress-bar-container">
            <div class="progress-bar ${colorClass}" style="width: ${clampedPercentage}%"></div>
        </div>
    `;
}

/**
 * Create a progress bar with label
 */
export function createLabeledProgressBar(label, current, total, percentage) {
    return `
        <div class="labeled-progress">
            <div class="progress-label">
                <span>${label}</span>
                <span>${current}/${total} (${Math.round(percentage)}%)</span>
            </div>
            ${createProgressBar(percentage)}
        </div>
    `;
}

// ============================================
// RARITY UTILITIES
// ============================================

/**
 * Get color class for avatar rarity
 */
export function getRarityClass(rarity) {
    const rarityMap = {
        'common': 'rarity-common',
        'rare': 'rarity-rare',
        'epic': 'rarity-epic',
        'legendary': 'rarity-legendary'
    };
    return rarityMap[rarity?.toLowerCase()] || 'rarity-common';
}

/**
 * Get display color for rarity
 */
export function getRarityColor(rarity) {
    const colorMap = {
        'common': '#6c757d',
        'rare': '#0d6efd',
        'epic': '#6f42c1',
        'legendary': '#ffc107'
    };
    return colorMap[rarity?.toLowerCase()] || '#6c757d';
}

// ============================================
// MODAL / NOTIFICATION SYSTEM
// ============================================

/**
 * Show achievement unlocked modal
 */
export function showAchievementModal(achievement) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal achievement-modal">
            <div class="modal-header">
                <h2>🏆 Achievement Unlocked!</h2>
            </div>
            <div class="modal-body">
                <div class="achievement-unlock-content">
                    ${achievement.badge_icon_url ?
                        `<img src="${achievement.badge_icon_url}" alt="${achievement.name}" class="achievement-badge-large" onerror="this.style.display='none'">`
                        : '<div class="achievement-badge-placeholder">🏆</div>'}
                    <h3>${achievement.name}</h3>
                    <p>${achievement.description}</p>
                    <div class="xp-reward">+${achievement.xp_reward} XP</div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="button button-primary" onclick="this.closest('.modal-overlay').remove()">
                    Awesome!
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add confetti effect (simple animation)
    addConfetti();

    // Auto-close after 5 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 5000);
}

/**
 * Show level up modal
 */
export function showLevelUpModal(newLevel) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal level-up-modal">
            <div class="modal-header">
                <h2>⭐ Level Up!</h2>
            </div>
            <div class="modal-body">
                <div class="level-up-content">
                    <div class="level-display-large">${newLevel}</div>
                    <h3>You reached Level ${newLevel}!</h3>
                    <p>Keep up the great work!</p>
                </div>
            </div>
            <div class="modal-footer">
                <button class="button button-primary" onclick="this.closest('.modal-overlay').remove()">
                    Continue
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    addConfetti();

    // Auto-close after 4 seconds
    setTimeout(() => {
        if (modal.parentElement) {
            modal.remove();
        }
    }, 4000);
}

/**
 * Simple confetti effect
 */
function addConfetti() {
    const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
    const confettiCount = 50;

    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 0.5 + 's';
        confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
        document.body.appendChild(confetti);

        setTimeout(() => confetti.remove(), 4000);
    }
}

/**
 * Show toast notification
 */
export function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 100);

    // Remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// DATE FORMATTING
// ============================================

/**
 * Format date to readable string
 */
export function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Format date to relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    return formatDate(dateString);
}

// ============================================
// NUMBER FORMATTING
// ============================================

/**
 * Format number with commas (e.g., 1000 -> 1,000)
 */
export function formatNumber(num) {
    return num.toLocaleString('en-US');
}

/**
 * Format percentage (e.g., 0.875 -> 87.5%)
 */
export function formatPercentage(decimal, decimals = 1) {
    return (decimal * 100).toFixed(decimals) + '%';
}

// ============================================
// DOM HELPERS
// ============================================

/**
 * Safely set innerHTML and return the element
 */
export function setHTML(element, html) {
    if (element) {
        element.innerHTML = html;
    }
    return element;
}

/**
 * Show/hide element
 */
export function toggleElement(element, show) {
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}
