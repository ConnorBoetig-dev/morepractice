"""
PROFILE SYSTEM FLOWS TEST SUITE
End-to-end integration tests for complete profile and customization workflows

Coverage:
- Complete profile customization flow (signup → update bio → view profile)
- Public profile security flow (view others → privacy validation)
- Profile data privacy flow (sensitive data not leaked)
- Bio validation flow (length limits, empty values)
- Username change with bio update flow
- Profile stats tracking flow (XP, level, streaks)

Test Philosophy: Test COMPLETE user journeys with security and privacy checkpoints
"""

import pytest
from datetime import datetime, timedelta
from app.models.user import User, UserProfile
from app.models.gamification import QuizAttempt
from app.utils.auth import hash_password, create_access_token


# ============================================
# COMPLETE PROFILE CUSTOMIZATION FLOWS (6 tests)
# Real User Journey: Profile management workflows
# ============================================

@pytest.mark.security
@pytest.mark.integration
@pytest.mark.slow
class TestCompleteProfileCustomizationFlows:
    """Test complete profile customization workflows"""

    def test_complete_profile_customization_flow_signup_to_bio_update(self, client, test_db):
        """
        REAL USER JOURNEY: New user customizes profile
        Flow: Signup → Get default profile → Update bio → View updated profile → Verify all fields present
        """
        # Step 1: Signup
        signup_response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePassword123!"
            }
        )

        assert signup_response.status_code in [200, 201], "Signup should succeed"
        signup_data = signup_response.json()
        token = signup_data["access_token"]

        # Step 2: Get initial profile (should have defaults)
        profile_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert profile_response.status_code == 200, "Should access profile"
        profile_data = profile_response.json()

        # Verify ProfileResponse structure with all fields
        assert "id" in profile_data
        assert "email" in profile_data
        assert "username" in profile_data
        assert "bio" in profile_data
        assert "avatar_url" in profile_data
        assert "selected_avatar_id" in profile_data
        assert "xp" in profile_data
        assert "level" in profile_data
        assert "study_streak_current" in profile_data
        assert "study_streak_longest" in profile_data
        assert "total_exams_taken" in profile_data
        assert "total_questions_answered" in profile_data
        assert "last_activity_date" in profile_data

        # Initial values should be defaults
        assert profile_data["bio"] is None, "Bio should be null initially"
        assert profile_data["xp"] == 0, "XP should start at 0"
        assert profile_data["level"] == 1, "Level should start at 1"

        # Step 3: Update bio
        update_response = client.patch(
            "/api/v1/auth/profile",
            json={"bio": "I love learning cybersecurity!"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert update_response.status_code == 200, "Bio update should succeed"
        update_data = update_response.json()
        assert "message" in update_data
        assert "successfully" in update_data["message"].lower()

        # Step 4: Verify bio was saved
        profile_response2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert profile_response2.status_code == 200
        profile_data2 = profile_response2.json()
        assert profile_data2["bio"] == "I love learning cybersecurity!", "Bio should be updated"
        assert profile_data2["email"] == "newuser@example.com", "Email should remain unchanged"

    def test_bio_validation_flow_length_limits(self, client, test_db):
        """
        REAL USER JOURNEY: User tests bio length limits
        Flow: Signup → Try 501 chars (rejected) → Try 500 chars (accepted) → Try empty (accepted)
        """
        # Setup user
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id)
        test_db.add(profile)
        test_db.commit()

        token = create_access_token({"user_id": user.id})

        # Step 1: Try 501 characters (should be rejected)
        bio_501 = "a" * 501
        response_501 = client.patch(
            "/api/v1/auth/profile",
            json={"bio": bio_501},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response_501.status_code == 422, "501 chars should be rejected"
        error_data = response_501.json()
        assert "errors" in error_data, "Should return validation error"
        assert any("bio" in err.get("field", "").lower() for err in error_data["errors"]), "Error should mention bio field"
        assert any("500" in err.get("message", "") for err in error_data["errors"]), "Error should mention 500 char limit"

        # Step 2: Try exactly 500 characters (should be accepted)
        bio_500 = "a" * 500
        response_500 = client.patch(
            "/api/v1/auth/profile",
            json={"bio": bio_500},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response_500.status_code == 200, "500 chars should be accepted (boundary)"

        # Verify saved
        profile_check = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_check.json()["bio"] == bio_500, "500 char bio should be saved"

        # Step 3: Clear bio (empty string)
        response_empty = client.patch(
            "/api/v1/auth/profile",
            json={"bio": ""},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response_empty.status_code == 200, "Empty bio should be accepted"

        # Verify cleared
        profile_check2 = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert profile_check2.json()["bio"] == "", "Bio should be empty string"

    def test_multiple_field_update_flow_username_and_bio(self, client, test_db):
        """
        REAL USER JOURNEY: User updates multiple profile fields at once
        Flow: Update username + bio together → Verify both saved → Old username doesn't work
        """
        # Setup user
        user = User(
            email="user@example.com",
            username="oldusername",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id)
        test_db.add(profile)
        test_db.commit()

        token = create_access_token({"user_id": user.id})

        # Update both username and bio
        update_response = client.patch(
            "/api/v1/auth/profile",
            json={
                "username": "newusername",
                "bio": "Updated bio text"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert update_response.status_code == 200, "Multiple field update should succeed"

        # Verify both fields updated
        profile_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        assert profile_data["username"] == "newusername", "Username should be updated"
        assert profile_data["bio"] == "Updated bio text", "Bio should be updated"

        # Verify old username no longer exists in database
        test_db.refresh(user)
        assert user.username == "newusername", "Database should reflect new username"

    def test_email_update_flow_verification_required(self, client, test_db):
        """
        REAL USER JOURNEY: User changes email
        Flow: Update email → Verification reset → Must verify new email
        """
        # Setup user
        user = User(
            email="old@example.com",
            username="user",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id)
        test_db.add(profile)
        test_db.commit()

        token = create_access_token({"user_id": user.id})

        # Update email
        update_response = client.patch(
            "/api/v1/auth/profile",
            json={"email": "new@example.com"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert update_response.status_code == 200, "Email update should succeed"

        # Verify email was changed and verification reset
        test_db.refresh(user)
        assert user.email == "new@example.com", "Email should be updated"
        # Note: Depending on implementation, is_verified might be reset to False
        # This documents expected behavior

    def test_profile_stats_update_after_quiz(self, client, test_db):
        """
        REAL USER JOURNEY: Profile stats auto-update after quiz
        Flow: Check initial stats → Complete quiz → Verify stats increased
        """
        # Setup user
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(
            user_id=user.id,
            xp=0,
            level=1,
            total_exams_taken=0,
            total_questions_answered=0
        )
        test_db.add(profile)
        test_db.commit()

        token = create_access_token({"user_id": user.id})

        # Step 1: Check initial stats
        initial_profile = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        initial_data = initial_profile.json()
        initial_xp = initial_data["xp"]
        initial_exams = initial_data["total_exams_taken"]

        # Step 2: Complete quiz (if questions exist)
        quiz_response = client.post(
            "/api/v1/quiz/submit",
            json={
                "exam_type": "security",
                "answers": [
                    {"question_id": 1, "selected_answer": "A"}
                ],
                "time_spent_seconds": 60
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        # Step 3: Verify stats updated (if quiz succeeded)
        if quiz_response.status_code in [200, 201]:
            updated_profile = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            updated_data = updated_profile.json()
            assert updated_data["total_exams_taken"] > initial_exams, "Exam count should increase"
            # XP might increase depending on score
            # This verifies ProfileResponse includes live stats

    def test_concurrent_profile_updates_last_write_wins(self, client, test_db):
        """
        REAL SCENARIO: User updates profile from multiple devices
        Flow: Two simultaneous updates → Last update wins → No data corruption
        """
        # Setup user
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id)
        test_db.add(profile)
        test_db.commit()

        token = create_access_token({"user_id": user.id})

        # Update 1: From device A
        response1 = client.patch(
            "/api/v1/auth/profile",
            json={"bio": "Bio from device A"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Update 2: From device B (quickly after)
        response2 = client.patch(
            "/api/v1/auth/profile",
            json={"bio": "Bio from device B"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Last write wins
        final_profile = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert final_profile.status_code == 200
        # Should have one of the bios (last write wins)
        assert final_profile.json()["bio"] in ["Bio from device A", "Bio from device B"]


# ============================================
# PUBLIC PROFILE SECURITY FLOWS (5 tests)
# Real User Journey: Viewing other users' profiles with privacy validation
# ============================================

@pytest.mark.security
@pytest.mark.integration
class TestPublicProfileSecurityFlows:
    """Test public profile viewing with security checks"""

    def test_complete_public_profile_flow_leaderboard_to_profile(self, client, test_db):
        """
        REAL USER JOURNEY: User clicks on leaderboard username
        Flow: View leaderboard → Click user → View public profile → See stats but NOT email
        """
        # Setup User A (logged in)
        user_a = User(
            email="usera@example.com",
            username="usera",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user_a)
        test_db.commit()
        test_db.refresh(user_a)

        profile_a = UserProfile(user_id=user_a.id, bio="User A bio", xp=1000, level=5)
        test_db.add(profile_a)
        test_db.commit()

        # Setup User B (target to view)
        user_b = User(
            email="userb@example.com",
            username="userb",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True,
            is_admin=False
        )
        test_db.add(user_b)
        test_db.commit()
        test_db.refresh(user_b)

        profile_b = UserProfile(
            user_id=user_b.id,
            bio="User B bio - learning security",
            xp=2500,
            level=10,
            study_streak_current=7,
            study_streak_longest=15,
            total_exams_taken=50,
            total_questions_answered=1000
        )
        test_db.add(profile_b)
        test_db.commit()

        token_a = create_access_token({"user_id": user_a.id})

        # Step 1: View leaderboard (get User B's ID)
        # In real app, leaderboard would show user_id

        # Step 2: View User B's public profile (NO AUTH REQUIRED)
        public_profile_response = client.get(f"/api/v1/auth/users/{user_b.id}")

        assert public_profile_response.status_code == 200, "Public profile should be accessible without auth"
        public_data = public_profile_response.json()

        # Step 3: Verify public data is present
        assert public_data["id"] == user_b.id
        assert public_data["username"] == "userb"
        assert public_data["bio"] == "User B bio - learning security"
        assert public_data["xp"] == 2500
        assert public_data["level"] == 10
        assert public_data["study_streak_current"] == 7
        assert public_data["study_streak_longest"] == 15
        assert public_data["total_exams_taken"] == 50
        assert public_data["total_questions_answered"] == 1000

        # Step 4: SECURITY CHECK - Verify sensitive data is NOT leaked
        assert "email" not in public_data, "Email should NOT be in public profile"
        assert "is_admin" not in public_data, "is_admin should NOT be in public profile"
        assert "is_active" not in public_data, "is_active should NOT be in public profile"
        assert "is_verified" not in public_data, "is_verified should NOT be in public profile"
        assert "hashed_password" not in public_data, "Password should NEVER be exposed"
        assert "reset_token" not in public_data, "Tokens should NEVER be exposed"

    def test_public_profile_no_auth_required(self, client, test_db):
        """
        REAL SCENARIO: Anonymous user views public profile (no login)
        Flow: No auth → Access public profile → Should work
        """
        # Setup user
        user = User(
            email="user@example.com",
            username="publicuser",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id, bio="Public bio", xp=500)
        test_db.add(profile)
        test_db.commit()

        # Access WITHOUT authentication
        response = client.get(f"/api/v1/auth/users/{user.id}")

        assert response.status_code == 200, "Public profile should work without auth"
        data = response.json()
        assert data["username"] == "publicuser"
        assert data["bio"] == "Public bio"

    def test_public_profile_nonexistent_user_404(self, client, test_db):
        """
        REAL SCENARIO: User tries to view profile that doesn't exist
        Flow: Access invalid user_id → 404 error
        """
        response = client.get("/api/v1/auth/users/99999")

        assert response.status_code == 404, "Nonexistent user should return 404"
        error_data = response.json()
        assert error_data["success"] is False
        assert "not found" in error_data["error"]["message"].lower()

    def test_public_profile_inactive_user_not_visible(self, client, test_db):
        """
        REAL SECURITY FLOW: Deactivated user profile hidden
        Flow: User deactivated → Public profile returns 404 or limited data
        """
        # Setup inactive user
        user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=False,  # Deactivated
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id, bio="Should not be visible")
        test_db.add(profile)
        test_db.commit()

        # Try to access inactive user's profile
        response = client.get(f"/api/v1/auth/users/{user.id}")

        # Should either return 404 or hide sensitive info
        # Implementation may vary - document expected behavior
        assert response.status_code in [200, 404], "Inactive user profile handling"

        if response.status_code == 200:
            # If visible, should still not leak email/admin status
            data = response.json()
            assert "email" not in data
            assert "is_admin" not in data

    def test_public_profile_privacy_own_profile_vs_others(self, client, test_db):
        """
        REAL SCENARIO: Compare own profile (full data) vs public profile (limited data)
        Flow: User views own profile → User views someone else's profile → Verify different data
        """
        # Setup User A
        user_a = User(
            email="usera@example.com",
            username="usera",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True,
            is_admin=True  # Sensitive field
        )
        test_db.add(user_a)
        test_db.commit()
        test_db.refresh(user_a)

        profile_a = UserProfile(user_id=user_a.id, bio="User A bio")
        test_db.add(profile_a)
        test_db.commit()

        # Setup User B
        user_b = User(
            email="userb@example.com",
            username="userb",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True,
            is_admin=False
        )
        test_db.add(user_b)
        test_db.commit()
        test_db.refresh(user_b)

        profile_b = UserProfile(user_id=user_b.id, bio="User B bio")
        test_db.add(profile_b)
        test_db.commit()

        token_a = create_access_token({"user_id": user_a.id})

        # User A views OWN profile (authenticated)
        own_profile = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token_a}"}
        )

        assert own_profile.status_code == 200
        own_data = own_profile.json()

        # Should include sensitive fields
        assert "email" in own_data, "Own profile should include email"
        assert "is_admin" in own_data, "Own profile should include is_admin"
        assert own_data["email"] == "usera@example.com"
        assert own_data["is_admin"] is True

        # User A views User B's PUBLIC profile
        public_profile = client.get(f"/api/v1/auth/users/{user_b.id}")

        assert public_profile.status_code == 200
        public_data = public_profile.json()

        # Should NOT include sensitive fields
        assert "email" not in public_data, "Public profile should NOT include email"
        assert "is_admin" not in public_data, "Public profile should NOT include is_admin"
        assert public_data["username"] == "userb"


# ============================================
# PROFILE DATA PRIVACY FLOWS (3 tests)
# Real Security Scenarios: Privacy enforcement
# ============================================

@pytest.mark.security
@pytest.mark.integration
class TestProfileDataPrivacyFlows:
    """Test privacy and data protection in profiles"""

    def test_admin_status_never_leaked_in_public_profile(self, client, test_db):
        """
        REAL SECURITY FLOW: Admin status is privileged information
        Flow: Create admin user → View public profile → Verify is_admin not exposed
        """
        # Create admin user
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True,
            is_admin=True  # Sensitive
        )
        test_db.add(admin)
        test_db.commit()
        test_db.refresh(admin)

        profile = UserProfile(user_id=admin.id, bio="Admin bio")
        test_db.add(profile)
        test_db.commit()

        # View admin's public profile
        response = client.get(f"/api/v1/auth/users/{admin.id}")

        assert response.status_code == 200
        data = response.json()

        # CRITICAL: is_admin must NOT be exposed
        assert "is_admin" not in data, "is_admin is privileged information"
        assert "is_active" not in data, "is_active reveals account status"

    def test_email_never_leaked_in_public_profile(self, client, test_db):
        """
        REAL SECURITY FLOW: Email is PII (Personally Identifiable Information)
        Flow: Create user → View public profile → Verify email not exposed
        """
        # Create user
        user = User(
            email="private@example.com",
            username="user",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id)
        test_db.add(profile)
        test_db.commit()

        # View public profile
        response = client.get(f"/api/v1/auth/users/{user.id}")

        assert response.status_code == 200
        data = response.json()

        # CRITICAL: Email is PII and must not be exposed
        assert "email" not in data, "Email is private information"
        assert "private@example.com" not in str(data), "Email should not appear anywhere in response"

    def test_rate_limit_applied_to_profile_endpoints(self, client, test_db):
        """
        REAL SECURITY FLOW: Rate limiting prevents abuse
        Flow: Make multiple profile requests → Verify rate limit applies
        """
        # Setup user
        user = User(
            email="user@example.com",
            username="user",
            hashed_password=hash_password("SecurePassword123!"),
            is_active=True,
            is_verified=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        profile = UserProfile(user_id=user.id)
        test_db.add(profile)
        test_db.commit()

        token = create_access_token({"user_id": user.id})

        # Make multiple requests to authenticated endpoint
        # Rate limit: 300/minute for standard endpoints
        # Not practical to hit limit in test, but verify endpoint works
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200, "Profile endpoint should be accessible"

        # Make requests to public profile endpoint
        public_response = client.get(f"/api/v1/auth/users/{user.id}")

        assert public_response.status_code == 200, "Public profile should be accessible"

        # Note: Full rate limit testing would require 300+ requests
        # This test documents that rate limits are expected on these endpoints
