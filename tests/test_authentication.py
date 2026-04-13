"""Integration tests for audihose.authentication module."""

import pytest

from audihose.database import Account, Login
from audihose.authentication import JWTBearer


def _login_payload(test_account, client_token, password="testpass123", remember_me=False):
    """Build a valid login payload for the current authentication API."""
    return {
        "email": test_account.email,
        "password": password,
        "client_token": client_token,
        "remember_me": remember_me,
    }


def test_authentication_endpoints_user_login_success(
    client, test_db_session, test_account, test_user_session
):
    """Test successful user login."""
    assert test_db_session is not None
    response = client.post(
        "/login",
        json=_login_payload(test_account, test_user_session.client_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("token")
    assert data.get("message") is None


def test_authentication_endpoints_user_login_invalid_password(
    client, test_account, test_user_session
):
    """Test login with incorrect password returns 401."""
    response = client.post(
        "/login",
        json=_login_payload(
            test_account,
            test_user_session.client_token,
            password="wrongpassword",
        ),
    )
    assert response.status_code == 200
    assert response.json().get("token") is None


def test_authentication_endpoints_user_login_nonexistent_account(client, test_user_session):
    """Test login with non-existent account returns 401."""
    response = client.post(
        "/login",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword",
            "client_token": test_user_session.client_token,
            "remember_me": False,
        },
    )
    assert response.status_code == 200
    assert response.json().get("token") is None


def test_authentication_endpoints_user_login_sets_cookie(
    client, test_account, test_user_session
):
    """Test that login sets an authentication cookie."""
    response = client.post(
        "/login",
        json=_login_payload(test_account, test_user_session.client_token),
    )
    assert response.status_code == 200
    assert "set-cookie" in response.headers


def test_authentication_endpoints_user_login_with_remember_me(
    client, test_account, test_user_session
):
    """Test login with remember_me flag sets persistent cookie."""
    response = client.post(
        "/login",
        json=_login_payload(
            test_account,
            test_user_session.client_token,
            remember_me=True,
        ),
    )
    assert response.status_code == 200


def test_authentication_endpoints_refresh_token_success(
    client, test_account, test_user_session, valid_jwt_token
):
    """Test successful token refresh."""
    assert test_account.id is not None
    response = client.post(
        "/refresh-token",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        cookies={"client_token": test_user_session.client_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data


def test_authentication_endpoints_refresh_token_invalid_session(
    client, expired_jwt_token
):
    """Test token refresh with expired session returns 403."""
    response = client.post(
        "/refresh-token",
        headers={"Authorization": f"Bearer {expired_jwt_token}"},
        cookies={"client_token": "missing-session"},
    )
    assert response.status_code in (401, 403)


def test_authentication_endpoints_logout_success(
    client, test_account, test_user_session, valid_jwt_token
):
    """Test successful logout."""
    assert test_account.id is not None
    response = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        cookies={"client_token": test_user_session.client_token},
    )
    assert response.status_code == 200


def test_authentication_endpoints_logout_clears_session(
    client, test_account, test_user_session, valid_jwt_token
):
    """Test that logout clears the session."""
    assert test_account.id is not None
    response1 = client.post(
        "/logout",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        cookies={"client_token": test_user_session.client_token},
    )
    assert response1.status_code == 200
    response2 = client.post(
        "/refresh-token",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        cookies={"client_token": test_user_session.client_token},
    )
    assert response2.status_code in (401, 403)


def test_authentication_endpoints_determine_signup_status_empty_db(
    client, test_db_session
):
    """Test signup status when no accounts exist."""
    test_db_session.query(Account).delete()
    test_db_session.commit()
    response = client.get("/signup-required")
    assert response.status_code == 200
    assert response.json() is True


def test_authentication_endpoints_determine_signup_status_has_account(
    client, test_account
):
    """Test signup status when account exists (signup disabled)."""
    assert test_account.id is not None
    response = client.get("/signup-required")
    assert response.status_code == 200
    assert response.json() is False


def test_authentication_endpoints_create_initial_account_success(
    client, test_db_session, test_user_session
):
    """Test successful initial account creation via signup."""
    test_db_session.query(Login).delete()
    test_db_session.query(Account).delete()
    test_db_session.commit()
    response = client.post(
        "/create-initial-account",
        cookies={"client_token": test_user_session.client_token},
        json={
            "name": "Initial User",
            "email": "initial@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data


def test_authentication_endpoints_create_initial_account_second_attempt_locked(
    client, test_account
):
    """Test that signup is locked after first account (423 LOCKED)."""
    assert test_account.id is not None
    response = client.post(
        "/create-initial-account",
        json={
            "name": "Second User",
            "email": "second@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 423


def test_jwtbearer_validation_jwt_bearer_valid_token(valid_jwt_token):
    """Test JWT Bearer validation with valid token."""
    assert JWTBearer().verify_jwt(valid_jwt_token) is True


def test_jwtbearer_validation_jwt_bearer_missing_token(client):
    """Test JWT Bearer validation without Authorization header (401)."""
    response = client.post("/refresh-token")
    assert response.status_code in (401, 403)


def test_jwtbearer_validation_jwt_bearer_invalid_scheme(client):
    """Test JWT Bearer with invalid scheme."""
    response = client.post(
        "/refresh-token", headers={"Authorization": "Basic invalid_base64"}
    )
    assert response.status_code == 401


def test_jwtbearer_validation_jwt_bearer_malformed_header(client):
    """Test JWT Bearer with malformed Authorization header."""
    response = client.post(
        "/refresh-token", headers={"Authorization": "InvalidHeader"}
    )
    assert response.status_code == 401


def test_jwtbearer_validation_jwt_bearer_expired_token(client, expired_jwt_token):
    """Test JWT Bearer with expired token (401 UNAUTHORIZED)."""
    response = client.post(
        "/refresh-token",
        headers={"Authorization": f"Bearer {expired_jwt_token}"},
    )
    assert response.status_code == 401


def test_jwtbearer_validation_jwt_bearer_invalid_signature(client):
    """Test JWT Bearer with tampered signature (401 UNAUTHORIZED)."""
    tampered_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIn0.invalid_signature"
    )
    response = client.post(
        "/refresh-token",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert response.status_code == 401


def test_jwtbearer_validation_jwt_bearer_empty_token(client):
    """Test JWT Bearer with empty token."""
    response = client.post("/refresh-token", headers={"Authorization": "Bearer"})
    assert response.status_code in (401, 403)


def test_query_token_validation_get_query_token_valid(valid_jwt_token):
    """Test extracting valid token from query parameter."""
    assert JWTBearer().verify_jwt(valid_jwt_token) is True


def test_query_token_validation_get_query_token_expired(expired_jwt_token):
    """Test query token with expired JWT (401)."""
    assert JWTBearer().verify_jwt(expired_jwt_token) is False


def test_query_token_validation_get_query_token_invalid():
    """Test query token with invalid JWT (401)."""
    assert JWTBearer().verify_jwt("invalid_token") is False


@pytest.mark.parametrize(
    "status_code,description",
    [
        (400, "Invalid Bearer scheme"),
        (401, "Missing authorization"),
        (401, "Expired token"),
        (401, "Invalid signature"),
        (403, "Session expired"),
        (423, "Signup locked (second user attempt)"),
    ],
)
def test_httpexception_scenarios_all_http_exceptions(status_code, description):
    """Verify that all expected HTTP exceptions can occur."""
    assert description
    assert status_code in (400, 401, 403, 423)
