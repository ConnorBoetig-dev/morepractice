/*
    DASHBOARD PAGE LOGIC

    Purpose: Display authenticated user information

    What this file does:
    - Check if user is authenticated (redirect if not)
    - Fetch current user data from /api/v1/auth/me
    - Display user information on the page
    - Handle logout button click
    - Show JWT token details (for learning)

    Learning Notes:
    - This is a PROTECTED route (requires authentication)
    - GET request with Bearer token in Authorization header
    - 401 error means token expired → redirect to login
    - Logout removes token and redirects to login
*/

import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { getToken, removeToken, redirectIfNotAuthenticated } from './auth.js';

/*
    STEP 1: Route Guard

    CRITICAL: Check authentication BEFORE doing anything else
    If user has no token, redirect to login immediately
    This protects the dashboard from unauthenticated access
*/
redirectIfNotAuthenticated();

/*
    STEP 2: Get references to HTML elements
*/
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error-message');
const userInfoDiv = document.getElementById('user-info');
const logoutButton = document.getElementById('logout-btn');

// User info fields
const userIdSpan = document.getElementById('user-id');
const userEmailSpan = document.getElementById('user-email');
const userUsernameSpan = document.getElementById('user-username');
const userStatusSpan = document.getElementById('user-status');
const userCreatedSpan = document.getElementById('user-created');

// Token display (for learning)
const tokenDisplay = document.getElementById('token-display');

/*
    STEP 3: Fetch user data when page loads

    This runs immediately when dashboard.html loads
    Uses async IIFE (Immediately Invoked Function Expression)
*/
(async function loadUserData() {
    /*
        LEARNING: IIFE Pattern
        - Wrapping code in () makes it an expression
        - () at end invokes it immediately
        - "async" allows us to use "await"
        - Useful for running async code at page load
    */

    try {
        console.log('📡 Fetching user data...');

        /*
            STEP 4: Make authenticated GET request

            LEARNING: Authenticated Request
            - GET method retrieves data
            - Endpoint: /api/v1/auth/me
            - No body needed (GET requests don't have bodies)
            - requiresAuth: true → adds Authorization: Bearer <token>
        */
        const user = await apiRequest(
            'GET',
            ENDPOINTS.ME,
            null,         // No request body for GET
            true          // Authentication required
        );

        /*
            LEARNING: Response structure
            Backend returns User model (from app/schemas/auth.py):
            {
                id: 1,
                email: "user@example.com",
                username: "johndoe",
                is_active: true,
                created_at: "2024-01-15T10:30:00.123456"
            }

            Note: Password hash is NOT included (filtered by response_model)
        */

        console.log('✓ User data loaded:', user);

        /*
            STEP 5: Display user data on page

            Using textContent (not innerHTML) for security
            Prevents XSS attacks if data contains HTML/JavaScript
        */
        userIdSpan.textContent = user.id;
        userEmailSpan.textContent = user.email;
        userUsernameSpan.textContent = user.username;

        // Show active status with color
        if (user.is_active) {
            userStatusSpan.textContent = '✓ Active';
            userStatusSpan.style.color = '#28a745';
        } else {
            userStatusSpan.textContent = '⚠ Inactive';
            userStatusSpan.style.color = '#dc3545';
        }

        // Format date nicely
        const createdDate = new Date(user.created_at);
        userCreatedSpan.textContent = createdDate.toLocaleString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        /*
            STEP 6: Show JWT token (for educational purposes)
        */
        const token = getToken();
        if (token) {
            tokenDisplay.textContent = token;
        }

        /*
            STEP 7: Show user info, hide loading
        */
        loadingDiv.style.display = 'none';
        userInfoDiv.style.display = 'block';

    } catch (error) {
        /*
            STEP 8: Handle errors

            Common errors:
            - 401 Unauthorized → token expired
            - Network error → backend not running
            - 500 Server Error → backend crashed

            LEARNING: Token Expiration
            - JWT tokens expire after 15 minutes (set in backend .env)
            - Backend returns 401 if token is expired or invalid
            - apiRequest() automatically removes token and throws error
            - We catch the error and redirect to login
        */

        console.error('❌ Failed to load user data:', error.message);

        // Hide loading
        loadingDiv.style.display = 'none';

        // Show error message
        errorDiv.textContent = `❌ ${error.message}`;
        errorDiv.style.display = 'block';

        // If unauthorized, redirect to login after 2 seconds
        if (error.message.includes('Unauthorized') || error.message.includes('log in')) {
            errorDiv.textContent += ' Redirecting to login...';

            setTimeout(() => {
                window.location.href = '/login.html';
            }, 2000);
        }
    }
})();

/*
    STEP 9: Handle logout button click

    Logout flow:
    1. User clicks logout button
    2. Remove token from localStorage
    3. Redirect to login page

    LEARNING: Client-side vs Server-side Logout
    - This is CLIENT-SIDE logout (just removes token)
    - Backend has no "logout" state (JWT is stateless)
    - Token remains valid until expiration (even after logout)
    - For true server-side logout, need token blacklist (more complex)
*/
logoutButton.addEventListener('click', () => {
    console.log('🚪 Logging out...');

    // Remove token from localStorage
    removeToken();

    // Redirect to login page
    window.location.href = '/login.html';
});

/*
    LEARNING SUMMARY:

    PROTECTED ROUTE FLOW:
    1. Page loads → redirectIfNotAuthenticated() checks for token
    2. If no token → redirect to login immediately
    3. If token exists → continue loading page
    4. Fetch user data with GET /api/v1/auth/me (token in header)
    5. Backend validates token and returns user data
    6. Display user data on page
    7. Show JWT token details (educational)

    AUTHENTICATION HEADER:
    - Format: Authorization: Bearer <token>
    - "Bearer" is the authentication scheme
    - Token is the JWT string from login/signup
    - Backend validates token on every protected request

    TOKEN EXPIRATION:
    - Tokens expire after 15 minutes (backend setting)
    - Expired token → 401 Unauthorized
    - apiRequest() catches 401 and removes token
    - User redirected to login page

    LOGOUT FLOW:
    - Remove token from localStorage
    - Redirect to login page
    - Simple but effective for learning
    - Production apps often have more complex logout (token blacklist)

    SECURITY NOTES:
    - Protected routes MUST check authentication first
    - Never trust client-side checks alone (backend validates token)
    - Use textContent (not innerHTML) to prevent XSS
    - Tokens should be sent over HTTPS in production
    - Token expiration limits damage if token is stolen

    DATA DISPLAY:
    - User model from backend (no password hash)
    - Date formatting with toLocaleString()
    - Conditional styling (active/inactive status)
    - Token display for educational purposes
*/
