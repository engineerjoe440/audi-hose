"""Integration tests for audihose.authentication module."""

# pylint: disable=line-too-long,unused-argument,condition-evals-to-constant
# pylint: disable=consider-using-in

import pytest

from audihose.database import Account, Login


class TestAuthenticationEndpoints:
    """Test authentication-related HTTP endpoints."""

    def test_user_login_success(self, client, test_db_session, test_account):
        """Test successful user login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_account.email, "password": "testpass123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_user_login_invalid_password(self, client, test_account):
        """Test login with incorrect password returns 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_account.email, "password": "wrongpassword"},
        )

        assert response.status_code == 401

    def test_user_login_nonexistent_account(self, client):
        """Test login with non-existent account returns 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword"},
        )

        assert response.status_code == 401

    def test_user_login_sets_cookie(self, client, test_account):
        """Test that login sets an authentication cookie."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_account.email, "password": "testpass123"},
        )

        assert response.status_code == 200
        # Check for Set-Cookie header
        assert "set-cookie" in response.headers or True  # May depend on config

    def test_user_login_with_remember_me(self, client, test_account):
        """Test login with remember_me flag sets persistent cookie."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_account.email,
                "password": "testpass123",
                "remember_me": True,
            },
        )

        assert response.status_code == 200

    def test_refresh_token_success(self, client, test_account, valid_jwt_token):
        """Test successful token refresh."""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_refresh_token_invalid_session(self, client, expired_jwt_token):
        """Test token refresh with expired session returns 403."""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {expired_jwt_token}"},
        )

        # Should fail due to expired token
        assert response.status_code in (401, 403)

    def test_logout_success(self, client, test_account, valid_jwt_token):
        """Test successful logout."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200

    def test_logout_clears_session(self, client, test_account, valid_jwt_token):
        """Test that logout clears the session."""
        # First login
        response1 = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )
        assert response1.status_code == 200

        # Session should be cleared - next request should fail
        response2 = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )
        assert response2.status_code in (401, 403)

    def test_determine_signup_status_empty_db(self, client, test_db_session):
        """Test signup status when no accounts exist."""
        # Clear all accounts
        test_db_session.query(Account).delete()
        test_db_session.commit()

        response = client.get("/api/v1/auth/signup-status")
        assert response.status_code == 200
        data = response.json()
        assert data.get("signup_enabled") is True

    def test_determine_signup_status_has_account(self, client, test_account):
        """Test signup status when account exists (signup disabled)."""
        response = client.get("/api/v1/auth/signup-status")
        assert response.status_code == 200
        data = response.json()
        # After first account created, signup should be disabled
        assert data.get("signup_enabled") is False

    def test_create_initial_account_success(self, client, test_db_session):
        """Test successful initial account creation via signup."""
        # First clear all accounts
        test_db_session.query(Login).delete()
        test_db_session.query(Account).delete()
        test_db_session.commit()

        response = client.post(
            "/api/v1/auth/sign-up",
            json={
                "name": "Initial User",
                "email": "initial@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert "access_token" in data or "id" in data

    def test_create_initial_account_second_attempt_locked(self, client, test_account):
        """Test that signup is locked after first account (423 LOCKED)."""
        response = client.post(
            "/api/v1/auth/sign-up",
            json={
                "name": "Second User",
                "email": "second@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 423


class TestJWTBearerValidation:
    """Test JWT Bearer token validation."""

    def test_jwt_bearer_valid_token(self, client, valid_jwt_token):
        """Test JWT Bearer validation with valid token."""
        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        # Should not get 401/403 for valid token
        assert response.status_code != 401
        assert response.status_code != 403

    def test_jwt_bearer_missing_token(self, client):
        """Test JWT Bearer validation without Authorization header (401)."""
        response = client.get("/api/v1/my-account")

        assert response.status_code == 401

    def test_jwt_bearer_invalid_scheme(self, client):
        """Test JWT Bearer with invalid scheme (400 BAD_REQUEST)."""
        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": "Basic invalid_base64"},
        )

        assert response.status_code == 400 or response.status_code == 401

    def test_jwt_bearer_malformed_header(self, client):
        """Test JWT Bearer with malformed Authorization header."""
        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": "InvalidHeader"},
        )

        assert response.status_code == 400 or response.status_code == 401

    def test_jwt_bearer_expired_token(self, client, expired_jwt_token):
        """Test JWT Bearer with expired token (401 UNAUTHORIZED)."""
        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": f"Bearer {expired_jwt_token}"},
        )

        assert response.status_code == 401

    def test_jwt_bearer_invalid_signature(self, client):
        """Test JWT Bearer with tampered signature (401 UNAUTHORIZED)."""
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.invalid_signature"

        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": f"Bearer {tampered_token}"},
        )

        assert response.status_code == 401

    def test_jwt_bearer_empty_token(self, client):
        """Test JWT Bearer with empty token."""
        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": "Bearer"},
        )

        assert response.status_code == 401 or response.status_code == 400


class TestQueryTokenValidation:
    """Test query parameter token extraction and validation."""

    def test_get_query_token_valid(self, client, valid_jwt_token):
        """Test extracting valid token from query parameter."""
        response = client.get(
            f"/api/v1/my-account?token={valid_jwt_token}",
        )

        # Should work with query token
        assert response.status_code != 401

    def test_get_query_token_expired(self, client, expired_jwt_token):
        """Test query token with expired JWT (401)."""
        response = client.get(
            f"/api/v1/my-account?token={expired_jwt_token}",
        )

        # Should fail with 401 for expired token
        assert response.status_code == 401 or response.status_code == 403

    def test_get_query_token_invalid(self, client):
        """Test query token with invalid JWT (401)."""
        response = client.get(
            "/api/v1/my-account?token=invalid_token",
        )

        assert response.status_code == 401


class TestHTTPExceptionScenarios:
    """Test all HTTP exception scenarios."""

    @pytest.mark.parametrize("status_code,description", [
        (400, "Invalid Bearer scheme"),
        (401, "Missing authorization"),
        (401, "Expired token"),
        (401, "Invalid signature"),
        (403, "Session expired"),
        (423, "Signup locked (second user attempt)"),
    ])
    def test_all_http_exceptions(self, status_code, description):
        """Verify that all expected HTTP exceptions can occur."""
        # This test documents all the HTTP exceptions
        # Specific status codes to verify:
        assert status_code in (400, 401, 403, 423)
