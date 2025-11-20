/*
    LOGIN PAGE LOGIC

    Purpose: Handle user authentication

    What this file does:
    - Listen for form submission
    - Validate form inputs
    - Send POST request to /api/v1/auth/login
    - Save JWT token to localStorage
    - Redirect to dashboard on success
    - Show error messages on failure (invalid credentials, etc.)

    Learning Notes:
    - Similar to signup.js but simpler (no username field)
    - 401 Unauthorized means invalid email/password
    - Token from login response is same format as signup
*/

import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { saveToken, redirectIfAuthenticated } from './auth.js';

/*
    STEP 1: Check if user is already logged in
*/
redirectIfAuthenticated();

/*
    STEP 2: Get references to HTML elements
*/
const form = document.getElementById('login-form');
const errorDiv = document.getElementById('error-message');
const successDiv = document.getElementById('success-message');
const loadingDiv = document.getElementById('loading');
const submitButton = form.querySelector('button[type="submit"]');

/*
    STEP 3: Add event listener for form submission
*/
form.addEventListener('submit', async (event) => {
    // Prevent default form submission (page reload)
    event.preventDefault();

    // Hide previous messages
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    /*
        STEP 4: Get form data
    */
    const formData = new FormData(form);

    const email = formData.get('email');
    const password = formData.get('password');

    /*
        STEP 5: Client-side validation
    */
    if (!email || !password) {
        showError('Please fill in all fields');
        return;
    }

    // Basic validation - accept email OR username
    // Email: must contain @ and .
    // Username: 3-50 chars, alphanumeric, underscore, hyphen
    if (email.includes('@')) {
        // Validate as email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showError('Please enter a valid email address');
            return;
        }
    } else {
        // Validate as username
        if (email.length < 3 || email.length > 50) {
            showError('Username must be 3-50 characters');
            return;
        }
        if (!/^[a-zA-Z0-9_-]+$/.test(email)) {
            showError('Username can only contain letters, numbers, underscores, and hyphens');
            return;
        }
    }

    /*
        STEP 6: Show loading state
    */
    submitButton.disabled = true;
    submitButton.textContent = 'Logging In...';
    loadingDiv.style.display = 'block';

    /*
        STEP 7: Make API request
    */
    try {
        /*
            LEARNING: Login API Request
            - POST method to /api/v1/auth/login
            - Body: { email, password }
            - No authentication required (public endpoint)
            - Backend validates credentials and returns token
        */
        const response = await apiRequest(
            'POST',
            ENDPOINTS.LOGIN,
            {
                email: email,
                password: password,
            },
            false // No authentication needed for login
        );

        /*
            LEARNING: Response structure (same as signup)
            {
                access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                token_type: "bearer"
            }
        */

        console.log('✓ Login successful:', response);

        /*
            STEP 8: Save JWT token
        */
        saveToken(response.access_token);

        /*
            STEP 9: Show success message
        */
        showSuccess('Login successful! Redirecting...');

        /*
            STEP 10: Redirect to dashboard
        */
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 1500);

    } catch (error) {
        /*
            STEP 11: Handle errors

            Common login errors:
            - "Invalid email or password" (401 Unauthorized)
            - "Cannot connect to server" (network error)
            - "User not found" (backend might return this)

            LEARNING: 401 Unauthorized
            - This is the correct status code for failed login
            - Backend sends generic message to prevent email enumeration
              (attacker shouldn't know if email exists or not)
        */

        console.error('❌ Login failed:', error.message);

        // Show user-friendly error message
        if (error.message.includes('Unauthorized') || error.message.includes('Invalid')) {
            showError('Invalid email or password. Please try again.');
        } else {
            showError(error.message);
        }

        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = 'Log In';
        loadingDiv.style.display = 'none';
    }
});

/**
 * Show error message to user
 *
 * @param {string} message - Error message to display
 */
function showError(message) {
    errorDiv.textContent = `❌ ${message}`;
    errorDiv.style.display = 'block';

    // Scroll to top so user sees the error
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Show success message to user
 *
 * @param {string} message - Success message to display
 */
function showSuccess(message) {
    successDiv.textContent = `✓ ${message}`;
    successDiv.style.display = 'block';

    // Scroll to top so user sees the success message
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/*
    LEARNING SUMMARY:

    AUTHENTICATION FLOW:
    1. User enters email and password
    2. Frontend validates inputs (basic checks)
    3. POST request to /api/v1/auth/login
    4. Backend checks password against hashed password in database
    5. If valid: backend creates JWT token and returns it
    6. Frontend saves token to localStorage
    7. User redirected to dashboard
    8. Dashboard uses token for authenticated requests

    SECURITY NOTES:
    - Password sent over HTTPS (encrypted in transit)
    - Backend never stores plain text passwords (uses bcrypt)
    - JWT token proves user is authenticated
    - Token expires after 15 minutes (backend enforces this)
    - Generic error messages prevent email enumeration attacks

    ERROR HANDLING:
    - 401 Unauthorized → "Invalid email or password"
    - Network error → "Cannot connect to server"
    - Other errors → Display backend error message

    DIFFERENCES FROM SIGNUP:
    - Login: authenticates existing user
    - Signup: creates new user
    - Both return JWT token in same format
    - Both redirect to dashboard on success
*/
