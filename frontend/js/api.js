/*
    API REQUEST WRAPPER

    Purpose: Generic function for making API requests to backend

    What this file does:
    - Wraps fetch() API with error handling
    - Automatically adds Authorization header for authenticated requests
    - Converts request/response to JSON
    - Handles HTTP errors (400, 401, 500, etc.)
    - Provides consistent error messages

    Learning Notes:
    - fetch() is the modern way to make HTTP requests in JavaScript
    - async/await makes asynchronous code look synchronous
    - try/catch handles errors gracefully
    - This DRY approach avoids repeating fetch() code everywhere
*/

import { getToken, removeToken } from './auth.js';

/**
 * Make an API request to the backend
 *
 * Generic function that handles ALL API calls in the app
 *
 * @param {string} method - HTTP method (GET, POST, PUT, DELETE)
 * @param {string} endpoint - Full URL endpoint
 * @param {object|null} data - Request body data (for POST/PUT)
 * @param {boolean} requiresAuth - Whether to include Authorization header
 *
 * @returns {Promise<object>} Response data from API
 * @throws {Error} If request fails
 *
 * Examples:
 *   // Signup (no auth required)
 *   await apiRequest('POST', ENDPOINTS.SIGNUP, { email, password, username }, false);
 *
 *   // Get current user (auth required)
 *   await apiRequest('GET', ENDPOINTS.ME, null, true);
 */
export async function apiRequest(method, endpoint, data = null, requiresAuth = false) {
    /*
        LEARNING: async function
        - "async" keyword makes function return a Promise
        - Allows us to use "await" inside the function
        - Makes asynchronous code easier to read
    */

    // 1. Build request headers
    const headers = {
        'Content-Type': 'application/json', // Tell server we're sending JSON
    };

    // 2. Add Authorization header if this is a protected route
    if (requiresAuth) {
        const token = getToken();

        if (!token) {
            // No token found - user needs to log in
            throw new Error('Not authenticated. Please log in.');
        }

        // Add Bearer token to Authorization header
        // Format: "Authorization: Bearer <token>"
        headers['Authorization'] = `Bearer ${token}`;

        console.log('✓ Added Authorization header with Bearer token');
    }

    // 3. Build fetch options
    const options = {
        method: method,           // GET, POST, PUT, DELETE
        headers: headers,          // Headers object we built above
    };

    // 4. Add request body for POST/PUT requests
    if (data) {
        // JSON.stringify() converts JavaScript object to JSON string
        // Backend expects JSON string in request body
        options.body = JSON.stringify(data);

        console.log(`→ ${method} ${endpoint}`, data);
    } else {
        console.log(`→ ${method} ${endpoint}`);
    }

    /*
        LEARNING: try/catch
        - "try" block contains code that might throw an error
        - "catch" block handles the error if it occurs
        - Essential for error handling in async operations
    */
    try {
        /*
            LEARNING: fetch() API
            - fetch() is a browser API for making HTTP requests
            - Returns a Promise that resolves to a Response object
            - "await" waits for Promise to resolve before continuing
        */
        const response = await fetch(endpoint, options);

        /*
            LEARNING: Response object
            - response.ok is true if status code is 200-299
            - response.status is the HTTP status code (200, 401, 404, etc.)
            - response.json() parses JSON response body
        */

        // Try to parse JSON response (even if request failed)
        // Backend sends JSON for both success and error responses
        let json;
        try {
            json = await response.json();
        } catch (parseError) {
            // If JSON parsing fails, create a generic error object
            json = { detail: 'Invalid response from server' };
        }

        console.log(`← ${response.status} ${endpoint}`, json);

        // 5. Handle HTTP errors
        if (!response.ok) {
            /*
                LEARNING: HTTP Status Codes
                - 200-299: Success
                - 400-499: Client errors (bad request, unauthorized, not found)
                - 500-599: Server errors (backend crashed, database down)
            */

            // Special handling for 401 Unauthorized
            if (response.status === 401) {
                console.warn('⚠ 401 Unauthorized - token may be expired');

                // Remove invalid/expired token
                removeToken();

                // Throw error with detail from backend
                throw new Error(json.detail || 'Unauthorized. Please log in again.');
            }

            // For other errors, throw with backend error message
            throw new Error(json.detail || `Request failed with status ${response.status}`);
        }

        // 6. Return parsed JSON response
        return json;

    } catch (error) {
        /*
            LEARNING: Error handling
            - catch block receives the error object
            - error.message contains the error description
            - We can add context to error messages
        */

        console.error('❌ API Request Error:', error);

        // Check if error is a network error (backend not running)
        if (error.message.includes('fetch')) {
            throw new Error('Cannot connect to server. Is the backend running?');
        }

        // Re-throw the error so calling code can handle it
        throw error;
    }
}

/*
    USAGE EXAMPLES:

    // Example 1: Signup (no authentication required)
    try {
        const result = await apiRequest(
            'POST',
            ENDPOINTS.SIGNUP,
            { email: 'user@example.com', password: 'pass123', username: 'john' },
            false
        );
        console.log('Signup successful:', result);
        saveToken(result.access_token);
    } catch (error) {
        console.error('Signup failed:', error.message);
    }

    // Example 2: Get current user (authentication required)
    try {
        const user = await apiRequest(
            'GET',
            ENDPOINTS.ME,
            null,
            true
        );
        console.log('Current user:', user);
    } catch (error) {
        if (error.message.includes('Unauthorized')) {
            window.location.href = '/login.html';
        }
    }
*/

/*
    ERROR HANDLING FLOW:

    1. Network error (backend down)
       → catch block catches fetch error
       → throw "Cannot connect to server"

    2. HTTP 401 (expired token)
       → response.status === 401
       → removeToken()
       → throw "Unauthorized. Please log in again"

    3. HTTP 400 (validation error)
       → response.ok === false
       → throw backend error message (e.g., "Email already exists")

    4. HTTP 500 (server error)
       → response.ok === false
       → throw "Request failed with status 500"

    5. JSON parse error (invalid response)
       → json parsing fails
       → use generic error message
*/
