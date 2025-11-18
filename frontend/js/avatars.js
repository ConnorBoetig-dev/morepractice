/**
 * AVATARS PAGE LOGIC
 * Display and equip avatars
 */

import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { redirectIfNotAuthenticated, removeToken } from './auth.js';
import { getRarityClass, formatNumber, showToast } from './utils.js';

redirectIfNotAuthenticated();

// DOM Elements
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const avatarGrid = document.getElementById('avatar-grid');
const avatarSummary = document.getElementById('avatar-summary');
const rarityLegend = document.getElementById('rarity-legend');

// Summary stats
const unlockedCount = document.getElementById('unlocked-count');
const totalAvatars = document.getElementById('total-avatars');
const collectionPercentage = document.getElementById('collection-percentage');
const equippedAvatar = document.getElementById('equipped-avatar');

let currentlyEquippedId = null;

// Load avatars
(async function loadAvatars() {
    try {
        console.log('📡 Fetching avatars...');

        // Fetch avatars with unlock status
        const avatars = await apiRequest('GET', ENDPOINTS.AVATARS_ME, null, true);

        console.log('✓ Loaded', avatars.length, 'avatars');

        // Calculate stats
        const unlocked = avatars.filter(a => a.is_unlocked).length;
        const total = avatars.length;
        const collection = total > 0 ? Math.round((unlocked / total) * 100) : 0;
        const equipped = avatars.find(a => a.is_selected);

        // Store currently equipped ID
        currentlyEquippedId = equipped?.id || null;

        // Display stats
        unlockedCount.textContent = formatNumber(unlocked);
        totalAvatars.textContent = formatNumber(total);
        collectionPercentage.textContent = `${collection}%`;
        equippedAvatar.textContent = equipped ? equipped.name : 'None';

        // Render avatars
        avatarGrid.innerHTML = avatars.map(avatar => renderAvatar(avatar)).join('');

        // Add click listeners
        attachAvatarListeners();

        // Show UI
        loading.style.display = 'none';
        avatarSummary.style.display = 'block';
        rarityLegend.style.display = 'block';
        avatarGrid.style.display = 'grid';

    } catch (error) {
        console.error('❌ Failed to load avatars:', error);
        loading.style.display = 'none';
        errorMessage.textContent = `Error: ${error.message}`;
        errorMessage.style.display = 'block';

        if (error.message.includes('Unauthorized')) {
            setTimeout(() => window.location.href = '/login.html', 2000);
        }
    }
})();

function renderAvatar(avatar) {
    const rarityClass = getRarityClass(avatar.rarity);
    const lockedClass = !avatar.is_unlocked ? 'locked' : '';
    const equippedClass = avatar.is_selected ? 'equipped' : '';

    return `
        <div class="avatar-card ${rarityClass} ${lockedClass} ${equippedClass}"
             data-avatar-id="${avatar.id}"
             data-unlocked="${avatar.is_unlocked}">
            ${avatar.is_selected ? '<div class="equipped-badge">EQUIPPED</div>' : ''}

            <div class="avatar-image">
                ${avatar.image_url ?
                    `<img src="${avatar.image_url}" alt="${avatar.name}" onerror="this.parentElement.innerHTML='${getAvatarEmoji(avatar.rarity)}'">`
                    : getAvatarEmoji(avatar.rarity)}
            </div>

            <div class="avatar-name">${avatar.name}</div>
            <div class="avatar-description">${avatar.description || ''}</div>

            <span class="rarity-badge ${avatar.rarity}">${avatar.rarity?.toUpperCase() || 'COMMON'}</span>

            <div class="avatar-unlock-status ${avatar.is_unlocked ? 'unlocked' : 'locked'}">
                ${avatar.is_unlocked ?
                    (avatar.is_selected ? '✓ Currently Equipped' : '✓ Unlocked - Click to Equip')
                    : '🔒 Locked'}
            </div>
        </div>
    `;
}

function getAvatarEmoji(rarity) {
    const rarityEmojis = {
        'common': '👤',
        'rare': '🎭',
        'epic': '⚡',
        'legendary': '👑'
    };
    return rarityEmojis[rarity?.toLowerCase()] || '👤';
}

function attachAvatarListeners() {
    const avatarCards = document.querySelectorAll('.avatar-card');

    avatarCards.forEach(card => {
        const avatarId = parseInt(card.dataset.avatarId);
        const isUnlocked = card.dataset.unlocked === 'true';

        if (isUnlocked && !card.classList.contains('equipped')) {
            card.addEventListener('click', () => equipAvatar(avatarId));
        }
    });
}

async function equipAvatar(avatarId) {
    try {
        console.log('Equipping avatar:', avatarId);

        await apiRequest('POST', ENDPOINTS.AVATARS_SELECT, { avatar_id: avatarId }, true);

        showToast('Avatar equipped successfully!', 'success');

        // Reload page to reflect changes
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        console.error('Failed to equip avatar:', error);
        showToast(`Failed to equip avatar: ${error.message}`, 'error');
    }
}

// Initialize navigation
import { initializeNavigation} from './navigation.js';
initializeNavigation();
