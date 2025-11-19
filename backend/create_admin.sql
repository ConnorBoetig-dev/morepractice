-- ============================================================
-- QUICK ADMIN USER CREATION SCRIPT
-- ============================================================
-- This SQL script will make an existing user an admin
-- OR create a new admin user from scratch

-- ============================================================
-- OPTION 1: Make existing user an admin
-- ============================================================
-- First, see all users:
-- SELECT id, username, email, is_admin FROM users;

-- Then, update a specific user to be admin (replace USER_ID):
-- UPDATE users SET is_admin = TRUE WHERE id = 1;

-- ============================================================
-- OPTION 2: Create a new admin user
-- ============================================================
-- NOTE: Password needs to be bcrypt hashed!
-- The hash below is for password: "admin123"
-- Generated with: bcrypt.hashpw(b"admin123", bcrypt.gensalt())

INSERT INTO users (
    username,
    email,
    hashed_password,
    is_active,
    is_verified,
    is_admin,
    created_at
) VALUES (
    'admin',
    'admin@billings.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eo5wCjreF96.',  -- Password: admin123
    TRUE,
    TRUE,
    TRUE,
    NOW()
) ON CONFLICT (email) DO NOTHING
RETURNING id;

-- Create profile for the admin user (replace USER_ID with the ID returned above)
-- INSERT INTO user_profiles (user_id) VALUES (1);

-- ============================================================
-- Verify admin user was created:
-- ============================================================
-- SELECT id, username, email, is_admin FROM users WHERE is_admin = TRUE;
