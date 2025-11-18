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

    console.log('🔧 Navigation Init:', {
        hasToken: !!token,
        foundLoginBtn: !!loginBtn,
        foundSignupBtn: !!signupBtn,
        foundLogoutBtn: !!logoutBtn
    });

    if (token) {
        // User is logged in - show logout, hide login/signup
        console.log('✅ User is logged in - hiding login/signup, showing logout');
        if (loginBtn) loginBtn.style.display = 'none';
        if (signupBtn) signupBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
    } else {
        // User is not logged in - show login/signup, hide logout
        console.log('⚠️ User is NOT logged in - showing login/signup, hiding logout');
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
