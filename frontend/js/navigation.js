/**
 * NAVIGATION COMPONENT
 * Handles consistent navigation across all pages
 */

import { getToken, removeToken } from './auth.js';

/**
 * Initialize navigation on page load
 * Shows/hides Login/Logout buttons based on auth state
 */
export function initializeNavigation() {
    const token = getToken();
    const loginBtn = document.getElementById('nav-login');
    const signupBtn = document.getElementById('nav-signup');
    const logoutBtn = document.getElementById('nav-logout');

    if (token) {
        // User is logged in - show logout, hide login/signup
        if (loginBtn) loginBtn.style.display = 'none';
        if (signupBtn) signupBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
    } else {
        // User is not logged in - show login/signup, hide logout
        if (loginBtn) loginBtn.style.display = 'inline-block';
        if (signupBtn) signupBtn.style.display = 'inline-block';
        if (logoutBtn) logoutBtn.style.display = 'none';
    }

    // Attach logout handler
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            removeToken();
            window.location.href = '/index.html';
        });
    }
}
