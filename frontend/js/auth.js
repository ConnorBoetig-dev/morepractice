/*
    AUTHENTICATION UTILITIES

    Purpose: Manage JWT tokens in localStorage

    What this file does:
    - Store JWT token after successful login/signup
    - Retrieve JWT token for authenticated requests
    - Check if user is authenticated
    - Remove token on logout
    - Redirect to login if not authenticated (route guard)

    Learning Notes:
    - localStorage is browser storage (persists even after closing browser)
    - Tokens are strings, not objects
    - Always check if token exists before using it
    - This is CLIENT-SIDE authentication (server still validates token)
*/

// Key name for storing token in localStorage
// Using a consistent key makes it easy to find/remove
const TOKEN_KEY = 'access_token';

/**
 * Save JWT token to localStorage
 *
 * Called after successful login or signup
 *
 * @param {string} token - JWT token from backend
 *
 * Example:
 *   saveToken('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
 */
export function saveToken(token) {
    // localStorage.setItem() stores a key-value pair
    // Both key and value must be strings
    localStorage.setItem(TOKEN_KEY, token);

    console.log('✓ Token saved to localStorage');
}

/**
 * Get JWT token from localStorage
 *
 * Returns token if exists, null if not found
 *
 * @returns {string|null} JWT token or null
 *
 * Example:
 *   const token = getToken();
 *   if (token) {
 *       // User is logged in
 *   }
 */
export function getToken() {
    // localStorage.getItem() retrieves value by key
    // Returns null if key doesn't exist
    const token = localStorage.getItem(TOKEN_KEY);

    return token;
}

/**
 * Remove JWT token from localStorage
 *
 * Called when user logs out
 *
 * Example:
 *   removeToken();
 *   window.location.href = '/login.html';
 */
export function removeToken() {
    // localStorage.removeItem() deletes the key-value pair
    localStorage.removeItem(TOKEN_KEY);

    console.log('✓ Token removed from localStorage');
}

/**
 * Check if user is authenticated
 *
 * Returns true if token exists, false otherwise
 *
 * @returns {boolean} True if authenticated
 *
 * Example:
 *   if (isAuthenticated()) {
 *       showDashboard();
 *   } else {
 *       showLoginPage();
 *   }
 */
export function isAuthenticated() {
    // Double negation (!!) converts value to boolean
    // !!null = false
    // !!'some-token' = true
    return !!getToken();
}

/**
 * Redirect to login page if not authenticated
 *
 * This is a "route guard" - protects pages that require authentication
 * Use this at the top of protected pages (like dashboard)
 *
 * Example:
 *   // In dashboard.js
 *   redirectIfNotAuthenticated(); // Runs before anything else
 */
export function redirectIfNotAuthenticated() {
    if (!isAuthenticated()) {
        console.log('⚠ Not authenticated - redirecting to login');
        window.location.href = '/login.html';
    }
}

/**
 * Redirect to dashboard if already authenticated
 *
 * Use this on login/signup pages to prevent logged-in users
 * from seeing those pages
 *
 * Example:
 *   // In login.js
 *   redirectIfAuthenticated(); // Logged-in users go to dashboard
 */
export function redirectIfAuthenticated() {
    if (isAuthenticated()) {
        console.log('✓ Already authenticated - redirecting to dashboard');
        window.location.href = '/dashboard.html';
    }
}

/*
    SECURITY NOTES FOR LEARNING:

    1. localStorage is NOT secure storage
       - JavaScript can access it (vulnerable to XSS attacks)
       - Never store sensitive data (passwords, credit cards)
       - OK for JWT tokens if backend validates them

    2. Token expiration is handled by backend
       - Tokens expire after 15 minutes (set in backend .env)
       - Backend will return 401 Unauthorized if token is expired
       - Frontend should handle 401 by redirecting to login

    3. Logout is client-side only
       - Removing token from localStorage doesn't "invalidate" it on server
       - If someone has your token, they can use it until it expires
       - For better security, backend could maintain a "blacklist" of revoked tokens

    4. HTTPS is critical in production
       - Always use HTTPS in production (not HTTP)
       - HTTPS encrypts data in transit (including tokens)
       - Without HTTPS, tokens can be intercepted

    5. Alternative: HttpOnly cookies
       - More secure than localStorage (JavaScript can't access)
       - Requires backend to set cookies
       - We use localStorage for simplicity in this learning project
*/
