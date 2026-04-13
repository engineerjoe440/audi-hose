"""Unit tests for audihose.security module."""

import time

import pytest

from audihose.security import (
    get_hashed_password,
    check_password,
    sign_jwt,
    decode_jwt,
    verify_token,
)


def test_password_hashing_get_hashed_password():
    """Test that get_hashed_password generates a bcrypt hash."""
    password = "test_password_123"
    hashed = get_hashed_password(password)
    assert hashed
    assert hashed != password


def test_password_hashing_check_password_valid():
    """Test check_password returns True for correct password."""
    password = "test_password_123"
    hashed = get_hashed_password(password)
    assert check_password(password, hashed) is True


def test_password_hashing_check_password_invalid():
    """Test check_password returns False for incorrect password."""
    password = "test_password_123"
    wrong_password = "wrong_password"
    hashed = get_hashed_password(password)
    assert check_password(wrong_password, hashed) is False


def test_password_hashing_check_password_empty_password():
    """Test check_password handles empty passwords."""
    hashed = get_hashed_password("something")
    assert check_password("", hashed) is False


def test_password_hashing_check_password_with_invalid_hash():
    """Test check_password handles invalid hash gracefully."""
    with pytest.raises(ValueError):
        check_password("password", "invalid_hash_format")


def test_jwtoperations_sign_jwt_creates_token():
    """Test that sign_jwt creates a valid token."""
    data = {"sub": "test@example.com", "account_id": "123"}
    expiry_seconds = 3600
    token = sign_jwt(data, expiry_seconds)
    assert token
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_jwtoperations_decode_jwt_valid_token():
    """Test that decode_jwt successfully decodes a valid token."""
    data = {"sub": "test@example.com", "account_id": "123"}
    expiry_seconds = 3600
    token = sign_jwt(data, expiry_seconds)
    decoded = decode_jwt(token)
    assert decoded is not None
    assert decoded != {}
    assert decoded.get("sub") == "test@example.com"
    assert decoded.get("account_id") == "123"


def test_jwtoperations_decode_jwt_expired_token():
    """Test that decode_jwt returns None or empty dict for expired token."""
    data = {"sub": "test@example.com", "account_id": "123"}
    expiry_seconds = 0
    token = sign_jwt(data, expiry_seconds)
    time.sleep(0.01)
    decoded = decode_jwt(token)
    assert decoded is None or decoded == {}


def test_jwtoperations_decode_jwt_invalid_token():
    """Test that decode_jwt returns empty dict for invalid token."""
    invalid_token = "invalid.token.format"
    decoded = decode_jwt(invalid_token)
    assert decoded is None or decoded == {}


def test_jwtoperations_decode_jwt_tampered_signature():
    """Test that decode_jwt returns empty dict for tampered token."""
    data = {"sub": "test@example.com", "account_id": "123"}
    expiry_seconds = 3600
    token = sign_jwt(data, expiry_seconds)
    tampered_token = token[:-1] + "X"
    decoded = decode_jwt(tampered_token)
    assert decoded is None or decoded == {}


def test_jwtoperations_verify_token_valid():
    """Test that verify_token returns True for valid token."""
    data = {"sub": "test@example.com", "account_id": "123"}
    expiry_seconds = 3600
    token = sign_jwt(data, expiry_seconds)
    assert verify_token(token) is True


def test_jwtoperations_verify_token_expired():
    """Test that verify_token returns False for expired token."""
    data = {"sub": "test@example.com", "account_id": "123"}
    expiry_seconds = 0
    token = sign_jwt(data, expiry_seconds)
    time.sleep(0.01)
    assert verify_token(token) is False


def test_jwtoperations_verify_token_invalid():
    """Test that verify_token returns False for invalid token."""
    assert verify_token("invalid.token.format") is False
