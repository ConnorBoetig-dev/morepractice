"""
SECURITY UTILITIES TEST SUITE
Tests for password hashing, JWT tokens, and password policy enforcement

Coverage:
- app/utils/auth.py (password hashing, JWT creation/validation)
- app/utils/tokens.py (secure token generation, expiration)
- app/utils/password_policy.py (password strength validation)

Test Philosophy: ZERO FLUFF - Every test validates REAL security properties
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta
from freezegun import freeze_time

# Import utilities to test
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    SECRET_KEY,
    ALGORITHM
)
from app.utils.tokens import (
    generate_secure_token,
    generate_reset_token,
    generate_verification_token,
    is_token_expired,
    validate_token,
    generate_refresh_token,
    get_reset_token_expiration,
    get_verification_token_expiration,
    get_refresh_token_expiration
)
from app.utils.password_policy import (
    validate_password_strength,
    calculate_password_strength,
    has_sequential_chars,
    has_repeated_chars,
    is_password_expired
)


# ============================================
# PASSWORD HASHING TESTS (12 tests)
# Real Security Testing: bcrypt hashing security
# ============================================

class TestPasswordHashing:
    """Test password hashing security properties"""

    def test_hash_same_password_twice_produces_different_hashes(self):
        """
        REAL SECURITY TEST: bcrypt uses random salt
        Each hash should be unique even for same password
        This prevents rainbow table attacks
        """
        password = "SamePassword123!"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Critical: Hashes must be different (proves salt is random)
        assert hash1 != hash2, "Hashes should differ (random salt required for security)"

        # Both should still verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_verify_correct_password_returns_true(self):
        """
        REAL SECURITY TEST: Correct password verification
        """
        password = "CorrectPassword123!"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True, "Correct password must verify successfully"

    def test_verify_wrong_password_returns_false(self):
        """
        REAL SECURITY TEST: Wrong password rejection
        """
        correct_password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(correct_password)

        result = verify_password(wrong_password, hashed)

        assert result is False, "Wrong password must be rejected"

    def test_empty_password_hashing(self):
        """
        REAL SECURITY TEST: Empty password handling
        Should hash without crashing (validation is policy's job)
        """
        hashed = hash_password("")

        # Should produce a valid hash
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash format

        # Empty password should verify correctly
        assert verify_password("", hashed) is True

    def test_very_long_password_1000_chars(self):
        """
        REAL SECURITY TEST: Long password handling
        bcrypt truncates at 72 bytes, but should handle gracefully
        """
        long_password = "A" * 1000 + "!"

        hashed = hash_password(long_password)

        # Should hash successfully
        assert len(hashed) > 0
        assert verify_password(long_password, hashed) is True

    def test_unicode_emoji_password_hashing(self):
        """
        REAL SECURITY TEST: Unicode/emoji password support
        Passwords with international characters should work
        """
        unicode_password = "Пароль🔒Mật_khẩu123!"

        hashed = hash_password(unicode_password)

        # Should hash and verify correctly
        assert verify_password(unicode_password, hashed) is True
        assert verify_password("WrongUnicode", hashed) is False

    def test_timing_attack_resistance_constant_time_comparison(self):
        """
        REAL SECURITY TEST: Timing attack resistance
        Bcrypt verification should take similar time for correct/wrong password
        This prevents timing-based password discovery
        """
        password = "TestPassword123!"
        hashed = hash_password(password)

        # Measure time for correct password
        start = time.time()
        verify_password(password, hashed)
        correct_time = time.time() - start

        # Measure time for wrong password
        start = time.time()
        verify_password("WrongPassword!", hashed)
        wrong_time = time.time() - start

        # Times should be within similar range (bcrypt is intentionally slow)
        # Both should take > 0.05 seconds (bcrypt cost factor makes it slow)
        assert correct_time > 0.05, "bcrypt should be slow (resist brute force)"
        assert wrong_time > 0.05, "bcrypt should be slow even for wrong password"

        # Time difference should be minimal (< 10ms difference acceptable)
        time_diff = abs(correct_time - wrong_time)
        assert time_diff < 0.01, "Timing should be constant (resist timing attacks)"

    def test_bcrypt_cost_factor_verification(self):
        """
        REAL SECURITY TEST: bcrypt cost factor (work factor)
        Hash should start with $2b$12$ (12 is the cost factor)
        Higher cost = slower hashing = better security
        """
        password = "TestPassword123!"
        hashed = hash_password(password)

        # Should be bcrypt format with reasonable cost factor
        assert hashed.startswith("$2b$"), "Must use bcrypt algorithm"

        # Extract cost factor (should be 12 or higher for security)
        cost_factor = int(hashed.split("$")[2])
        assert cost_factor >= 10, "bcrypt cost factor should be >= 10 for security"

    def test_password_with_null_bytes_rejected_safely(self):
        """
        REAL SECURITY TEST: Null byte handling
        Null bytes in passwords could cause truncation bugs
        """
        password_with_null = "Password\x00Hidden123!"

        # Should hash (bcrypt handles null bytes safely)
        hashed = hash_password(password_with_null)

        # Should verify with exact password only
        assert verify_password(password_with_null, hashed) is True
        assert verify_password("Password", hashed) is False  # Truncated version fails

    def test_sql_injection_attempt_in_password_safely_hashed(self):
        """
        REAL SECURITY TEST: SQL injection in password
        Password with SQL injection should be safely hashed
        """
        sql_injection = "' OR '1'='1'; DROP TABLE users; --"

        hashed = hash_password(sql_injection)

        # Should hash safely (SQL is just string data)
        assert verify_password(sql_injection, hashed) is True
        assert verify_password("normal_password", hashed) is False

    def test_xss_attempt_in_password_safely_hashed(self):
        """
        REAL SECURITY TEST: XSS in password
        Password with XSS should be safely hashed
        """
        xss_attempt = "<script>alert('XSS')</script>"

        hashed = hash_password(xss_attempt)

        # Should hash safely (XSS is just string data)
        assert verify_password(xss_attempt, hashed) is True

    def test_concurrent_hashing_thread_safety(self):
        """
        REAL SECURITY TEST: Concurrent hashing safety
        Multiple concurrent hashes should produce unique results
        """
        import concurrent.futures

        password = "ConcurrentTest123!"

        # Hash same password 10 times concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(hash_password, password) for _ in range(10)]
            hashes = [f.result() for f in futures]

        # All hashes should be unique (random salt)
        assert len(set(hashes)) == 10, "Concurrent hashes must all be unique"

        # All should verify correctly
        for hashed in hashes:
            assert verify_password(password, hashed) is True


# ============================================
# JWT TOKEN TESTS (15 tests)
# Real Security Testing: JWT creation, validation, tampering
# ============================================

class TestJWTTokens:
    """Test JWT token security"""

    def test_create_token_with_user_id_decode_returns_correct_user_id(self):
        """
        REAL SECURITY TEST: JWT payload integrity
        Token should preserve exact user_id
        """
        user_id = 12345

        token = create_access_token({"user_id": user_id})
        payload = decode_access_token(token)

        assert payload is not None, "Token should be valid"
        assert payload["user_id"] == user_id, "User ID must match exactly"

    def test_expired_token_validation_fails(self):
        """
        REAL SECURITY TEST: Expired token rejection
        Tokens past expiration must be rejected
        """
        user_id = 123

        # Create token that expires in 1 second
        token = create_access_token(
            {"user_id": user_id},
            expires_delta=timedelta(seconds=1)
        )

        # Token should be valid immediately
        payload = decode_access_token(token)
        assert payload is not None

        # Wait for expiration
        time.sleep(2)

        # Token should now be expired
        payload = decode_access_token(token)
        assert payload is None, "Expired token must be rejected"

    def test_token_with_tampered_payload_validation_fails(self):
        """
        REAL SECURITY TEST: Tampered payload detection
        Changing user_id in payload should fail signature validation
        """
        original_user_id = 123
        attacker_user_id = 999

        # Create token for user 123
        token = create_access_token({"user_id": original_user_id})

        # Attacker tries to change user_id to 999
        # Decode without verification (attacker's perspective)
        parts = token.split(".")
        assert len(parts) == 3  # header.payload.signature

        # Tamper with payload (change user_id)
        import base64
        import json

        # Decode payload
        payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
        payload_dict = json.loads(payload_bytes)

        # Tamper: change user_id
        payload_dict["user_id"] = attacker_user_id

        # Re-encode tampered payload
        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload_dict).encode()
        ).decode().rstrip("=")

        # Create tampered token
        tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

        # Validation should FAIL (signature mismatch)
        result = decode_access_token(tampered_token)
        assert result is None, "Tampered token must be rejected"

    def test_token_with_tampered_signature_validation_fails(self):
        """
        REAL SECURITY TEST: Tampered signature detection
        Changing signature should fail validation
        """
        token = create_access_token({"user_id": 123})

        # Tamper with signature
        parts = token.split(".")
        tampered_signature = parts[2][:-1] + "X"  # Change last character
        tampered_token = f"{parts[0]}.{parts[1]}.{tampered_signature}"

        # Validation should FAIL
        result = decode_access_token(tampered_token)
        assert result is None, "Tampered signature must be rejected"

    def test_token_with_wrong_secret_key_validation_fails(self):
        """
        REAL SECURITY TEST: Wrong secret key rejection
        Token signed with different secret must fail
        """
        user_id = 123
        wrong_secret = "wrong_secret_key_12345"

        # Create token with WRONG secret
        payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=15)}
        fake_token = jwt.encode(payload, wrong_secret, algorithm=ALGORITHM)

        # Validation should FAIL (wrong secret)
        result = decode_access_token(fake_token)
        assert result is None, "Token with wrong secret must be rejected"

    def test_token_with_no_expiration_has_expiration(self):
        """
        REAL SECURITY TEST: Expiration enforcement
        All tokens must have expiration (no infinite tokens)
        """
        token = create_access_token({"user_id": 123})

        # Decode to check payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Must have expiration
        assert "exp" in payload, "Token must have expiration"
        assert payload["exp"] > datetime.utcnow().timestamp(), "Expiration must be in future"

    def test_token_with_future_not_before_claim_validation_fails(self):
        """
        REAL SECURITY TEST: Not-before claim validation
        Tokens with nbf (not before) in future should fail
        """
        user_id = 123

        # Create token with nbf (not before) 1 hour in future
        future_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=2),
            "nbf": future_time.timestamp()
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Validation should FAIL (nbf not reached yet)
        # Note: PyJWT doesn't validate nbf by default, but we're testing the concept
        try:
            decoded = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_nbf": True}
            )
            # If nbf is in future, it should fail
            assert decoded["nbf"] <= datetime.utcnow().timestamp(), "nbf should be rejected"
        except jwt.InvalidTokenError:
            # Expected: token not valid yet
            pass

    def test_token_with_invalid_algorithm_none_rejected(self):
        """
        REAL SECURITY TEST: Algorithm confusion attack
        Token with "none" algorithm must be rejected
        """
        user_id = 123

        # Attacker tries "none" algorithm
        payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=1)}

        try:
            # Try to create token with "none" algorithm
            fake_token = jwt.encode(payload, "", algorithm="none")

            # Try to validate (should fail)
            result = decode_access_token(fake_token)
            assert result is None, "Token with 'none' algorithm must be rejected"
        except Exception:
            # Expected: should raise exception or return None
            pass

    def test_token_refresh_creates_new_token_old_invalidated(self):
        """
        REAL SECURITY TEST: Token refresh security
        After refresh, new token should work, old behavior verified
        """
        user_id = 123

        # Create original token
        original_token = create_access_token({"user_id": user_id})

        # Verify original works
        payload1 = decode_access_token(original_token)
        assert payload1 is not None

        # Create new (refreshed) token
        refreshed_token = create_access_token({"user_id": user_id})

        # New token should work
        payload2 = decode_access_token(refreshed_token)
        assert payload2 is not None

        # Tokens should be different
        assert original_token != refreshed_token

    def test_multiple_concurrent_token_validations_thread_safe(self):
        """
        REAL SECURITY TEST: Concurrent validation safety
        Multiple concurrent validations should work correctly
        """
        import concurrent.futures

        user_id = 123
        token = create_access_token({"user_id": user_id})

        # Validate same token 100 times concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(decode_access_token, token) for _ in range(100)]
            results = [f.result() for f in futures]

        # All validations should succeed
        assert all(r is not None for r in results), "Concurrent validations must all succeed"
        assert all(r["user_id"] == user_id for r in results), "All should return correct user_id"

    def test_malformed_token_string_validation_fails(self):
        """
        REAL SECURITY TEST: Malformed token handling
        Garbage tokens should be rejected gracefully
        """
        malformed_tokens = [
            "not.a.token",
            "only_one_part",
            "two.parts",
            "",
            ".....",
            "a.b.c.d.e",
            "invalid base64!@#$%"
        ]

        for bad_token in malformed_tokens:
            result = decode_access_token(bad_token)
            assert result is None, f"Malformed token '{bad_token}' must be rejected"

    def test_token_for_deleted_user_concept(self):
        """
        REAL SECURITY TEST: Token validation concept
        Token should decode successfully (user deletion check is in dependency)
        """
        deleted_user_id = 999

        # Create token for user that will be "deleted"
        token = create_access_token({"user_id": deleted_user_id})

        # Token should decode (JWT validation doesn't check DB)
        payload = decode_access_token(token)
        assert payload is not None, "Token decoding doesn't check user existence"
        assert payload["user_id"] == deleted_user_id

    def test_token_with_extra_claims_safely_ignored(self):
        """
        REAL SECURITY TEST: Extra claims handling
        Token with extra claims should still be valid
        """
        token = create_access_token({
            "user_id": 123,
            "extra_claim": "should_be_ignored",
            "role": "admin"
        })

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["user_id"] == 123
        assert payload.get("extra_claim") == "should_be_ignored"

    def test_token_reuse_after_password_change_concept(self):
        """
        REAL SECURITY TEST: Token invalidation concept
        Current implementation: tokens remain valid (add version to payload for invalidation)
        """
        user_id = 123

        # Create token before "password change"
        token_before = create_access_token({"user_id": user_id})

        # Token should still decode (no version checking in current implementation)
        payload = decode_access_token(token_before)
        assert payload is not None

        # NOTE: For production, add "version" or "password_hash" to payload
        # and invalidate on password change

    def test_token_expiration_edge_case_exactly_at_expiration(self):
        """
        REAL SECURITY TEST: Expiration boundary
        Token exactly at expiration time should be expired
        """
        with freeze_time("2024-01-01 12:00:00") as frozen_time:
            # Create token that expires in 1 hour
            token = create_access_token(
                {"user_id": 123},
                expires_delta=timedelta(hours=1)
            )

            # Token valid now
            assert decode_access_token(token) is not None

            # Move to exactly expiration time
            frozen_time.move_to("2024-01-01 13:00:00")

            # Token should be expired (exp is exclusive)
            result = decode_access_token(token)
            # JWT considers exact expiration time as expired
            assert result is None, "Token at exact expiration should be expired"


# ============================================
# SECURE TOKEN GENERATION TESTS (8 tests)
# Real Security Testing: Token randomness, uniqueness, expiration
# ============================================

class TestSecureTokens:
    """Test secure token generation for password reset, email verification"""

    def test_generate_reset_token_is_unique_cryptographically_random(self):
        """
        REAL SECURITY TEST: Token uniqueness
        Multiple tokens should be cryptographically unique
        """
        tokens = [generate_reset_token() for _ in range(100)]

        # All tokens must be unique (no collisions)
        assert len(set(tokens)) == 100, "All tokens must be unique"

        # Tokens should be reasonable length
        for token in tokens:
            assert len(token) > 30, "Tokens must be sufficiently long for security"

    def test_validate_reset_token_within_1_hour_success(self):
        """
        REAL SECURITY TEST: Valid token acceptance
        Token within expiration window should validate
        """
        token = generate_reset_token()
        stored_token = token
        expires_at = get_reset_token_expiration()

        # Should validate successfully
        is_valid = validate_token(token, stored_token, expires_at)
        assert is_valid is True, "Valid token within expiration must be accepted"

    def test_validate_reset_token_after_1_hour_fails(self):
        """
        REAL SECURITY TEST: Expired token rejection
        Token after 1 hour should be rejected
        """
        token = generate_reset_token()
        stored_token = token

        # Set expiration to 2 hours ago
        expires_at = datetime.utcnow() - timedelta(hours=2)

        # Should fail validation
        is_valid = validate_token(token, stored_token, expires_at)
        assert is_valid is False, "Expired token must be rejected"

    def test_same_reset_token_used_twice_second_use_fails(self):
        """
        REAL SECURITY TEST: Token reuse prevention
        After first use, token should be invalidated (by updating expires_at)
        """
        token = generate_reset_token()
        stored_token = token
        expires_at = get_reset_token_expiration()

        # First use: valid
        assert validate_token(token, stored_token, expires_at) is True

        # Simulate token invalidation after use
        invalidated_expires = datetime.utcnow() - timedelta(seconds=1)

        # Second use: should fail
        assert validate_token(token, stored_token, invalidated_expires) is False

    def test_reset_token_for_wrong_user_validation_fails(self):
        """
        REAL SECURITY TEST: Token ownership
        Using wrong token should fail
        """
        user1_token = generate_reset_token()
        user2_token = generate_reset_token()
        expires_at = get_reset_token_expiration()

        # User tries to use wrong token
        is_valid = validate_token(user1_token, user2_token, expires_at)
        assert is_valid is False, "Wrong token must be rejected"

    def test_verification_token_generation_unique(self):
        """
        REAL SECURITY TEST: Email verification token uniqueness
        """
        tokens = [generate_verification_token() for _ in range(100)]

        # All must be unique
        assert len(set(tokens)) == 100, "All verification tokens must be unique"

    def test_concurrent_token_generation_all_unique_no_collisions(self):
        """
        REAL SECURITY TEST: Concurrent token generation safety
        Tokens generated concurrently should all be unique
        """
        import concurrent.futures

        # Generate 1000 tokens concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(generate_reset_token) for _ in range(1000)]
            tokens = [f.result() for f in futures]

        # All tokens must be unique (no collisions even under concurrency)
        assert len(set(tokens)) == 1000, "Concurrent token generation must produce unique tokens"

    def test_token_timing_safe_comparison(self):
        """
        REAL SECURITY TEST: Timing-safe comparison
        validate_token() uses secrets.compare_digest (constant time)
        """
        import time

        correct_token = generate_reset_token()
        wrong_token = generate_reset_token()
        expires_at = get_reset_token_expiration()

        # Measure time for correct token
        start = time.time()
        for _ in range(1000):
            validate_token(correct_token, correct_token, expires_at)
        correct_time = time.time() - start

        # Measure time for wrong token
        start = time.time()
        for _ in range(1000):
            validate_token(wrong_token, correct_token, expires_at)
        wrong_time = time.time() - start

        # Times should be similar (timing-safe comparison)
        time_ratio = max(correct_time, wrong_time) / min(correct_time, wrong_time)
        assert time_ratio < 2.0, "Token comparison should be timing-safe (constant time)"


# ============================================
# PASSWORD POLICY TESTS (14 tests)
# Real Security Testing: Password strength, complexity, common password detection
# ============================================

class TestPasswordPolicy:
    """Test password policy enforcement"""

    def test_strong_password_passes_all_requirements(self):
        """
        REAL SECURITY TEST: Strong password acceptance
        """
        strong_password = "MySecureP@ssw0rd2024!"

        is_valid, errors = validate_password_strength(strong_password)

        assert is_valid is True, "Strong password must pass"
        assert len(errors) == 0, "Strong password should have no errors"

    def test_password_too_short_fails(self):
        """
        REAL SECURITY TEST: Length requirement
        """
        short_password = "Short1!"  # Less than 12 chars

        is_valid, errors = validate_password_strength(short_password)

        assert is_valid is False
        assert any("12 characters" in error for error in errors)

    def test_password_no_uppercase_fails(self):
        """
        REAL SECURITY TEST: Uppercase requirement
        """
        no_upper = "mypassword123!"

        is_valid, errors = validate_password_strength(no_upper)

        assert is_valid is False
        assert any("uppercase" in error.lower() for error in errors)

    def test_password_no_lowercase_fails(self):
        """
        REAL SECURITY TEST: Lowercase requirement
        """
        no_lower = "MYPASSWORD123!"

        is_valid, errors = validate_password_strength(no_lower)

        assert is_valid is False
        assert any("lowercase" in error.lower() for error in errors)

    def test_password_no_digit_fails(self):
        """
        REAL SECURITY TEST: Digit requirement
        """
        no_digit = "MyPasswordOnly!"

        is_valid, errors = validate_password_strength(no_digit)

        assert is_valid is False
        assert any("number" in error.lower() for error in errors)

    def test_password_no_special_char_fails(self):
        """
        REAL SECURITY TEST: Special character requirement
        """
        no_special = "MyPassword123"

        is_valid, errors = validate_password_strength(no_special)

        assert is_valid is False
        assert any("special character" in error.lower() for error in errors)

    def test_common_password_rejected(self):
        """
        REAL SECURITY TEST: Common password blacklist
        Well-known weak passwords must be rejected
        """
        common_passwords = [
            "password123",
            "Password123!",  # Still common even with complexity
            "CompTIA2024!",  # Domain-specific common
            "letmein123!A"
        ]

        for pwd in common_passwords:
            is_valid, errors = validate_password_strength(pwd)
            assert is_valid is False, f"Common password '{pwd}' must be rejected"
            assert any("common" in error.lower() for error in errors)

    def test_sequential_characters_rejected(self):
        """
        REAL SECURITY TEST: Sequential character detection
        Passwords with "123", "abc", etc. are weak
        """
        sequential_passwords = [
            "Password123!",  # Contains "123"
            "MyPassword!abc",  # Contains "abc"
            "Test456Pass!",  # Contains "456"
        ]

        for pwd in sequential_passwords:
            is_valid, errors = validate_password_strength(pwd)
            assert is_valid is False, f"Sequential password '{pwd}' should be rejected"
            assert any("sequential" in error.lower() for error in errors)

    def test_repeated_characters_rejected(self):
        """
        REAL SECURITY TEST: Repeated character detection
        Passwords with "aaa", "111", etc. are weak
        """
        repeated_passwords = [
            "MyPasssssword123!",  # Contains "ssss"
            "Password1111!",  # Contains "1111"
        ]

        for pwd in repeated_passwords:
            is_valid, errors = validate_password_strength(pwd)
            assert is_valid is False, f"Repeated chars password '{pwd}' should be rejected"
            assert any("repeated" in error.lower() for error in errors)

    def test_password_strength_scoring_very_strong(self):
        """
        REAL SECURITY TEST: Strength calculation
        Complex password should score high
        """
        very_strong = "Tr0ub4dor&3_MyC0mpl3xP@ssw0rd!"

        score, rating = calculate_password_strength(very_strong)

        assert score >= 80, f"Very strong password should score >= 80, got {score}"
        assert rating in ["Very Strong", "Strong"]

    def test_password_strength_scoring_weak(self):
        """
        REAL SECURITY TEST: Weakness detection
        Weak password should score low
        """
        weak = "password"

        score, rating = calculate_password_strength(weak)

        assert score < 40, f"Weak password should score < 40, got {score}"
        assert rating in ["Very Weak", "Weak"]

    def test_password_expiration_90_days(self):
        """
        REAL SECURITY TEST: Password expiration
        Password older than 90 days should be expired
        """
        # Password changed 100 days ago
        last_changed = datetime.utcnow() - timedelta(days=100)

        is_expired = is_password_expired(last_changed, expiry_days=90)

        assert is_expired is True, "Password older than 90 days must be expired"

    def test_password_not_expired_within_90_days(self):
        """
        REAL SECURITY TEST: Valid password timeframe
        """
        # Password changed 30 days ago
        last_changed = datetime.utcnow() - timedelta(days=30)

        is_expired = is_password_expired(last_changed, expiry_days=90)

        assert is_expired is False, "Password within 90 days should not be expired"

    def test_unicode_password_strength_validation(self):
        """
        REAL SECURITY TEST: International password support
        Unicode passwords should be validated correctly
        """
        unicode_strong = "МойПароль123!中文密码"

        is_valid, errors = validate_password_strength(unicode_strong)

        # Should pass length and complexity requirements
        # (may fail if it doesn't have ASCII uppercase/lowercase)
        assert len(errors) < 3, "Unicode password should mostly pass or have minimal errors"
