/*
    API CONFIGURATION

    Purpose: Centralize API endpoint configuration

    Why this file exists:
    - Single place to change API URL (useful for dev vs production)
    - Makes it easy to update if backend port changes
    - DRY principle (Don't Repeat Yourself)

    Learning Notes:
    - Export allows other files to import this constant
    - Template literals (`${}`) make URL building easier
    - Having a config file is a best practice in real applications
*/

// Base URL for our FastAPI backend
// This is where your uvicorn server is running
export const API_BASE_URL = 'http://localhost:8000';

// API version prefix
// FastAPI routes are under /api/v1
export const API_VERSION = '/api/v1';

// Full API base (combines both above)
export const API_FULL_BASE = `${API_BASE_URL}${API_VERSION}`;

// Auth endpoints
// We define these as constants so there are no typos in route strings
export const ENDPOINTS = {
    SIGNUP: `${API_FULL_BASE}/auth/signup`,
    LOGIN: `${API_FULL_BASE}/auth/login`,
    ME: `${API_FULL_BASE}/auth/me`,
    LOGOUT: `${API_FULL_BASE}/auth/logout`,
};

/*
    USAGE EXAMPLE:

    import { ENDPOINTS } from './config.js';

    fetch(ENDPOINTS.LOGIN, {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
*/
