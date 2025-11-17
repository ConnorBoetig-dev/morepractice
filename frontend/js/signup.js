/*
    SIGNUP PAGE LOGIC

    Purpose: Handle user registration form

    What this file does:
    - Listen for form submission
    - Validate form inputs
    - Send POST request to /api/v1/auth/signup
    - Save JWT token to localStorage
    - Redirect to dashboard on success
    - Show error messages on failure

    Learning Notes:
    - Event listeners detect user actions (form submit, button click)
    - preventDefault() stops default form submission (page reload)
    - FormData makes it easy to get form values
    - async/await handles asynchronous operations cleanly
*/

import { ENDPOINTS } from './config.js';
import { apiRequest } from './api.js';
import { saveToken, redirectIfAuthenticated } from './auth.js';

/*
    STEP 1: Check if user is already logged in

    If user has a token, they don't need to sign up again
    Redirect them to dashboard instead
*/
redirectIfAuthenticated();

/*
    STEP 2: Get references to HTML elements

    We'll need these to:
    - Listen for form submission
    - Show/hide error/success messages
    - Disable submit button while processing
*/
const form = document.getElementById('signup-form');
const errorDiv = document.getElementById('error-message');
const successDiv = document.getElementById('success-message');
const loadingDiv = document.getElementById('loading');
const submitButton = form.querySelector('button[type="submit"]');

/*
    STEP 3: Add event listener for form submission

    addEventListener() registers a function to run when event occurs
    'submit' event fires when user clicks submit button or presses Enter
*/
form.addEventListener('submit', async (event) => {
    /*
        LEARNING: Event object
        - event.preventDefault() stops default behavior
        - Without this, form would reload the page (old-school form submission)
        - We want to handle submission with JavaScript instead
    */
    event.preventDefault();

    // Hide previous messages
    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    /*
        STEP 4: Get form data

        FormData is a browser API that makes it easy to get form values
        Alternative: document.getElementById('email').value (more verbose)
    */
    const formData = new FormData(form);

    const email = formData.get('email');
    const username = formData.get('username');
    const password = formData.get('password');

    /*
        STEP 5: Client-side validation

        Check inputs before sending to server
        This gives instant feedback to users
        Backend will also validate (never trust client-side validation alone)
    */
    if (!email || !username || !password) {
        showError('Please fill in all fields');
        return;
    }

    if (password.length < 8) {
        showError('Password must be at least 8 characters');
        return;
    }

    // Email validation regex (basic)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Please enter a valid email address');
        return;
    }

    /*
        STEP 6: Show loading state

        Disable submit button and show loading message
        This prevents duplicate submissions while waiting for API response
    */
    submitButton.disabled = true;
    submitButton.textContent = 'Creating Account...';
    loadingDiv.style.display = 'block';

    /*
        STEP 7: Make API request

        Use try/catch to handle success and errors
    */
    try {
        /*
            LEARNING: API Request
            - POST method creates new resources
            - Endpoint: /api/v1/auth/signup
            - Body: { email, password, username }
            - No authentication required (public endpoint)
        */
        const response = await apiRequest(
            'POST',
            ENDPOINTS.SIGNUP,
            {
                email: email,
                password: password,
                username: username,
            },
            false // No authentication needed for signup
        );

        /*
            LEARNING: Response structure
            Backend returns:
            {
                access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                token_type: "bearer"
            }
        */

        console.log('✓ Signup successful:', response);

        /*
            STEP 8: Save JWT token

            Store token in localStorage for future authenticated requests
        */
        saveToken(response.access_token);

        /*
            STEP 9: Show success message
        */
        showSuccess('Account created successfully! Redirecting...');

        /*
            STEP 10: Redirect to dashboard

            setTimeout delays the redirect by 1.5 seconds
            This lets user see the success message
        */
        setTimeout(() => {
            window.location.href = '/dashboard.html';
        }, 1500);

    } catch (error) {
        /*
            STEP 11: Handle errors

            Common errors:
            - "Email already exists" (400 Bad Request)
            - "Cannot connect to server" (network error)
            - "Invalid email or password" (validation error)
        */

        console.error('❌ Signup failed:', error.message);

        showError(error.message);

        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.textContent = 'Create Account';
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

    FLOW:
    1. User fills form and clicks submit
    2. JavaScript prevents default form submission
    3. Client validates inputs (instant feedback)
    4. POST request sent to /api/v1/auth/signup
    5. Backend creates user and returns JWT token
    6. Frontend saves token to localStorage
    7. User redirected to dashboard

    ERROR HANDLING:
    - Client validation errors → show message instantly
    - Network errors → "Cannot connect to server"
    - 400 Bad Request → backend validation message (e.g., "Email already exists")
    - 500 Server Error → "Request failed"

    KEY CONCEPTS:
    - Event listeners detect user actions
    - preventDefault() stops default behavior
    - async/await handles asynchronous operations
    - try/catch handles errors gracefully
    - FormData extracts form values
    - Token storage enables authenticated requests
*/
