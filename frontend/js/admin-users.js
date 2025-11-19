import { ENDPOINTS } from './config.js';

let currentPage = 1;
let currentFilters = {};

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

// Load users with pagination
async function loadUsers(page = 1) {
    const token = localStorage.getItem('access_token');
    const params = new URLSearchParams({
        page: page,
        page_size: 20,
        ...currentFilters
    });

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_USERS}?${params}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to load users');
        const data = await response.json();

        displayUsers(data.users);
        displayPagination(data);
        document.getElementById('total-count').textContent = `(${data.total})`;

    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

// Display users in table
function displayUsers(users) {
    const tbody = document.getElementById('users-tbody');
    const table = document.getElementById('users-table');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');

    loadingState.style.display = 'none';

    if (users.length === 0) {
        table.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    table.style.display = 'table';
    emptyState.style.display = 'none';

    tbody.innerHTML = users.map(user => {
        const initials = user.username.substring(0, 2).toUpperCase();
        const statusBadge = user.is_active
            ? '<span class="badge badge-active">Active</span>'
            : '<span class="badge badge-banned">Banned</span>';
        const verifiedBadge = user.is_verified
            ? '<span class="badge badge-verified">Verified</span>'
            : '<span class="badge badge-unverified">Unverified</span>';
        const adminBadge = user.is_admin
            ? '<span class="badge badge-admin">Admin</span>'
            : '';

        const joinDate = new Date(user.created_at).toLocaleDateString();
        const lastLogin = user.last_login_at
            ? new Date(user.last_login_at).toLocaleString()
            : 'Never';

        return `
            <tr>
                <td>
                    <div class="user-info">
                        <div class="user-avatar">${initials}</div>
                        <div class="user-details">
                            <div class="user-name">${escapeHtml(user.username)}</div>
                            <div class="user-email">${escapeHtml(user.email)}</div>
                        </div>
                    </div>
                </td>
                <td>
                    ${adminBadge}
                    ${statusBadge}
                    ${verifiedBadge}
                </td>
                <td>
                    <div style="font-size: 0.85em;">
                        <div>Level ${user.level} • ${user.xp} XP</div>
                        <div style="color: #999;">Streak: ${user.study_streak_current} days</div>
                    </div>
                </td>
                <td>${joinDate}</td>
                <td style="font-size: 0.85em;">${lastLogin}</td>
                <td>
                    <div class="actions">
                        <button class="btn-icon" onclick="viewUser(${user.id})" title="View Details">👁️</button>
                        <button class="btn-icon" onclick="toggleAdmin(${user.id}, ${user.is_admin})" title="${user.is_admin ? 'Remove Admin' : 'Make Admin'}">${user.is_admin ? '⭐' : '☆'}</button>
                        <button class="btn-icon" onclick="toggleActive(${user.id}, ${user.is_active})" title="${user.is_active ? 'Ban User' : 'Unban User'}">${user.is_active ? '🔒' : '🔓'}</button>
                        <button class="btn-icon" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')" title="Delete User">🗑️</button>
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
    loadUsers(page);
};

// Apply filters
document.getElementById('apply-filters').addEventListener('click', function() {
    const search = document.getElementById('search-input').value;
    const isAdmin = document.getElementById('admin-filter').value;
    const isVerified = document.getElementById('verified-filter').value;

    currentFilters = {};
    if (search) currentFilters.search = search;
    if (isAdmin) currentFilters.is_admin = isAdmin;
    if (isVerified) currentFilters.is_verified = isVerified;

    currentPage = 1;
    loadUsers(1);
});

// View user details
window.viewUser = async function(userId) {
    const token = localStorage.getItem('access_token');

    try {
        // Fetch user details and activity in parallel
        const [userResponse, activityResponse] = await Promise.all([
            fetch(`${ENDPOINTS.ADMIN_USERS}/${userId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch(`${ENDPOINTS.ADMIN_USERS}/${userId}/activity?limit=10`, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
        ]);

        if (!userResponse.ok) throw new Error('Failed to load user details');
        const user = await userResponse.json();

        const activity = activityResponse.ok ? await activityResponse.json() : null;

        displayUserDetails(user, activity);
        document.getElementById('user-modal').classList.add('active');

    } catch (error) {
        console.error('Error loading user details:', error);
        alert('Failed to load user details');
    }
};

// Display user details in modal
function displayUserDetails(user, activity) {
    const content = document.getElementById('user-details-content');

    const joinDate = new Date(user.created_at).toLocaleString();
    const lastLogin = user.last_login_at
        ? new Date(user.last_login_at).toLocaleString()
        : 'Never';

    // Build activity HTML
    let activityHTML = '';
    if (activity) {
        // Recent quiz attempts
        if (activity.quiz_attempts && activity.quiz_attempts.length > 0) {
            activityHTML += `
                <div class="detail-item detail-item-full">
                    <div class="detail-label" style="margin-bottom: 10px;">Recent Quiz Attempts</div>
                    <div style="max-height: 150px; overflow-y: auto; font-size: 0.85em;">
                        ${activity.quiz_attempts.map(attempt => `
                            <div style="padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 5px;">
                                <strong>${attempt.exam_type.toUpperCase()}</strong> -
                                Score: ${attempt.score_percentage}%
                                (${attempt.correct_answers}/${attempt.total_questions}) -
                                +${attempt.xp_earned} XP
                                <div style="color: #999; font-size: 0.9em;">
                                    ${new Date(attempt.completed_at).toLocaleString()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Recent achievements
        if (activity.achievements_earned && activity.achievements_earned.length > 0) {
            activityHTML += `
                <div class="detail-item detail-item-full">
                    <div class="detail-label" style="margin-bottom: 10px;">Recent Achievements</div>
                    <div style="max-height: 150px; overflow-y: auto; font-size: 0.85em;">
                        ${activity.achievements_earned.map(ach => `
                            <div style="padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 5px;">
                                ${ach.achievement_icon} <strong>${ach.achievement_name}</strong> -
                                +${ach.xp_reward} XP
                                <div style="color: #999; font-size: 0.9em;">
                                    ${new Date(ach.earned_at).toLocaleString()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Active sessions
        if (activity.active_sessions && activity.active_sessions.length > 0) {
            activityHTML += `
                <div class="detail-item detail-item-full">
                    <div class="detail-label" style="margin-bottom: 10px;">Active Sessions (${activity.active_sessions.length})</div>
                    <div style="max-height: 100px; overflow-y: auto; font-size: 0.85em;">
                        ${activity.active_sessions.map(session => `
                            <div style="padding: 8px; background: #e8f5e9; border-radius: 6px; margin-bottom: 5px;">
                                <strong>IP:</strong> ${session.ip_address || 'Unknown'}<br>
                                <strong>Last Active:</strong> ${new Date(session.last_active).toLocaleString()}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        // Recent audit logs
        if (activity.audit_logs && activity.audit_logs.length > 0) {
            activityHTML += `
                <div class="detail-item detail-item-full">
                    <div class="detail-label" style="margin-bottom: 10px;">Recent Activity Log</div>
                    <div style="max-height: 150px; overflow-y: auto; font-size: 0.85em;">
                        ${activity.audit_logs.map(log => `
                            <div style="padding: 8px; background: ${log.success ? '#f8f9fa' : '#ffebee'}; border-radius: 6px; margin-bottom: 5px;">
                                <strong>${log.action}</strong> -
                                ${log.success ? '✓ Success' : '✗ Failed'}
                                ${log.ip_address ? ` from ${log.ip_address}` : ''}
                                <div style="color: #999; font-size: 0.9em;">
                                    ${new Date(log.timestamp).toLocaleString()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
    }

    content.innerHTML = `
        <div class="detail-grid">
            <div class="detail-item">
                <div class="detail-label">Username</div>
                <div class="detail-value">${escapeHtml(user.username)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Email</div>
                <div class="detail-value">${escapeHtml(user.email)}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Level</div>
                <div class="detail-value">${user.level}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">XP</div>
                <div class="detail-value">${user.xp}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Current Streak</div>
                <div class="detail-value">${user.study_streak_current} days</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Longest Streak</div>
                <div class="detail-value">${user.study_streak_longest} days</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Quizzes Completed</div>
                <div class="detail-value">${user.total_quizzes_completed}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Achievements Earned</div>
                <div class="detail-value">${user.total_achievements_earned}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Account Created</div>
                <div class="detail-value" style="font-size: 0.9em;">${joinDate}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Last Login</div>
                <div class="detail-value" style="font-size: 0.9em;">${lastLogin}</div>
            </div>
            <div class="detail-item detail-item-full">
                <div class="detail-label">Account Status</div>
                <div style="margin-top: 10px;">
                    ${user.is_admin ? '<span class="badge badge-admin">Admin</span>' : ''}
                    ${user.is_verified ? '<span class="badge badge-verified">Verified</span>' : '<span class="badge badge-unverified">Unverified</span>'}
                    ${user.is_active ? '<span class="badge badge-active">Active</span>' : '<span class="badge badge-banned">Banned</span>'}
                </div>
            </div>
            ${user.last_login_ip ? `
            <div class="detail-item detail-item-full">
                <div class="detail-label">Last Login IP</div>
                <div class="detail-value" style="font-size: 0.9em;">${escapeHtml(user.last_login_ip)}</div>
            </div>
            ` : ''}
            ${activityHTML}
        </div>

        <div class="action-buttons">
            <button class="button ${user.is_admin ? 'button-danger-outline' : 'button-primary'}"
                    onclick="toggleAdmin(${user.id}, ${user.is_admin}); closeModal();">
                ${user.is_admin ? 'Remove Admin' : 'Grant Admin'}
            </button>
            <button class="button ${user.is_active ? 'button-danger-outline' : 'button-success'}"
                    onclick="toggleActive(${user.id}, ${user.is_active}); closeModal();">
                ${user.is_active ? 'Ban User' : 'Unban User'}
            </button>
            <button class="button button-danger"
                    onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}'); closeModal();">
                Delete Account
            </button>
            <button class="button button-secondary-outline" onclick="closeModal()">
                Close
            </button>
        </div>
    `;
}

// Toggle admin status
window.toggleAdmin = async function(userId, currentIsAdmin) {
    const action = currentIsAdmin ? 'remove admin privileges from' : 'grant admin privileges to';
    if (!confirm(`Are you sure you want to ${action} this user?`)) {
        return;
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_USERS}/${userId}/toggle-admin`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to toggle admin status');
        const result = await response.json();

        alert(result.message);
        loadUsers(currentPage);

    } catch (error) {
        console.error('Error toggling admin:', error);
        alert('Failed to toggle admin status');
    }
};

// Toggle active status (ban/unban)
window.toggleActive = async function(userId, currentIsActive) {
    const action = currentIsActive ? 'ban' : 'unban';
    if (!confirm(`Are you sure you want to ${action} this user?`)) {
        return;
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_USERS}/${userId}/toggle-active`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to toggle active status');
        const result = await response.json();

        alert(result.message);
        loadUsers(currentPage);

    } catch (error) {
        console.error('Error toggling active status:', error);
        alert('Failed to toggle active status');
    }
};

// Delete user
window.deleteUser = async function(userId, username) {
    if (!confirm(`Are you sure you want to DELETE the account for "${username}"? This action CANNOT be undone and will delete all their data.`)) {
        return;
    }

    // Double confirmation for safety
    const confirmText = prompt(`Type "${username}" to confirm deletion:`);
    if (confirmText !== username) {
        alert('Deletion cancelled. Username did not match.');
        return;
    }

    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${ENDPOINTS.ADMIN_USERS}/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete user');
        }

        alert('User deleted successfully!');
        loadUsers(currentPage);

    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Error: ' + error.message);
    }
};

// Close modal
function closeModal() {
    document.getElementById('user-modal').classList.remove('active');
}

window.closeModal = closeModal;
document.getElementById('close-modal').addEventListener('click', closeModal);

// Logout
document.getElementById('nav-logout').addEventListener('click', function() {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
});

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
checkAdminAccess().then(isAdmin => {
    if (isAdmin) {
        loadUsers(1);
    }
});
