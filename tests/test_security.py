"""Unit tests for audihose.security module."""

# pylint: disable=import-outside-toplevel

import pytest
from audihose.security import (
    get_hashed_password,
    check_password,
    sign_jwt,
    decode_jwt,
    verify_token,
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_get_hashed_password(self):
        """Test that get_hashed_password generates a bcrypt hash."""
        password = "test_password_123"
        hashed = get_hashed_password(password)

        # Should be a non-empty string/bytes
        assert hashed
        # Should not be the plaintext password
        assert hashed != password

    def test_check_password_valid(self):
        """Test check_password returns True for correct password."""
        password = "test_password_123"
        hashed = get_hashed_password(password)

        assert check_password(password, hashed) is True

    def test_check_password_invalid(self):
        """Test check_password returns False for incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_hashed_password(password)

        assert check_password(wrong_password, hashed) is False

    def test_check_password_empty_password(self):
        """Test check_password handles empty passwords."""
        hashed = get_hashed_password("something")

        assert check_password("", hashed) is False

    def test_check_password_with_invalid_hash(self):
        """Test check_password handles invalid hash gracefully."""
        # Invalid hash format will raise ValueError
        with pytest.raises(ValueError):
            check_password("password", "invalid_hash_format")


class TestJWTOperations:
    """Test JWT token signing and decoding."""

    def test_sign_jwt_creates_token(self):
        """Test that sign_jwt creates a valid token."""
        data = {"sub": "test@example.com", "account_id": "123"}
        expiry_seconds = 3600  # 1 hour in seconds

        token = sign_jwt(data, expiry_seconds)

        # Token should be a non-empty string
        assert token
        assert isinstance(token, str)
        # Should have JWT structure (header.payload.signature)
        assert token.count(".") == 2

    def test_decode_jwt_valid_token(self):
        """Test that decode_jwt successfully decodes a valid token."""
        data = {"sub": "test@example.com", "account_id": "123"}
        expiry_seconds = 3600  # 1 hour in seconds

        token = sign_jwt(data, expiry_seconds)
        decoded = decode_jwt(token)

        assert decoded is not None
        assert decoded != {}
        assert decoded.get("sub") == "test@example.com"
        assert decoded.get("account_id") == "123"

    def test_decode_jwt_expired_token(self):
        """Test that decode_jwt returns None or empty dict for expired token."""
        data = {"sub": "test@example.com", "account_id": "123"}
        expiry_seconds = 0  # Expire immediately

        token = sign_jwt(data, expiry_seconds)

        # Give a tiny bit of time to ensure it's expired
        import time
        time.sleep(0.01)

        decoded = decode_jwt(token)

        # Should return None or empty dict for expired token
        assert decoded is None or decoded == {}

    def test_decode_jwt_invalid_token(self):
        """Test that decode_jwt returns empty dict for invalid token."""
        invalid_token = "invalid.token.format"

        decoded = decode_jwt(invalid_token)

        # Should return empty dict or None
        assert decoded is None or decoded == {}

    def test_decode_jwt_tampered_signature(self):
        """Test that decode_jwt returns empty dict for tampered token."""
        data = {"sub": "test@example.com", "account_id": "123"}
        expiry_seconds = 3600

        token = sign_jwt(data, expiry_seconds)
        # Tamper with the signature
        tampered_token = token[:-1] + "X"

        decoded = decode_jwt(tampered_token)

        # Should return empty dict or None
        assert decoded is None or decoded == {}

    def test_verify_token_valid(self):
        """Test that verify_token returns True for valid token."""
        data = {"sub": "test@example.com", "account_id": "123"}
        expiry_seconds = 3600

        token = sign_jwt(data, expiry_seconds)

        assert verify_token(token) is True

    def test_verify_token_expired(self):
        """Test that verify_token returns False for expired token."""
        data = {"sub": "test@example.com", "account_id": "123"}
        expiry_seconds = 0  # Expire immediately

        token = sign_jwt(data, expiry_seconds)

        import time
        time.sleep(0.01)

        assert verify_token(token) is False

    def test_verify_token_invalid(self):
        """Test that verify_token returns False for invalid token."""
        assert verify_token("invalid.token.format") is False
