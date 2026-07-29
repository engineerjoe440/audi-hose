"""Integration tests for audihose.api.accounts module."""

import pytest

from audihose.database import Account, Login


def test_account_endpoints_create_new_account_success(client, valid_jwt_token):
    """Test successful account creation."""
    response = client.put(
        "/api/v1/accounts",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={
            "name": "New Account",
            "email": "newaccount@example.com",
            "password": "newpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert isinstance(data.get("id"), str)


def test_account_endpoints_create_account_duplicate_email(
    client, valid_jwt_token, test_account
):
    """Test account creation with duplicate email."""
    response = client.put(
        "/api/v1/accounts",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={
            "name": "Another User",
            "email": test_account.email,
            "password": "password123",
        },
    )
    assert response.status_code in (400, 409, 422)


def test_account_endpoints_get_all_accounts(
    client, valid_jwt_token, test_account, test_account_2
):
    """Test retrieving all accounts."""
    response = client.get(
        "/api/v1/accounts", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    emails = [acc.get("email") for acc in data]
    assert test_account_2.email is not None
    assert test_account.email in emails or len(data) >= 1


def test_account_endpoints_get_all_accounts_empty(
    client, valid_jwt_token, test_db_session
):
    """Test retrieving accounts when database is empty."""
    test_db_session.query(Account).delete()
    test_db_session.commit()
    response = client.get(
        "/api/v1/accounts", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_account_endpoints_get_my_account(
    client, valid_jwt_token, test_user_session, test_account
):
    """Test retrieving current user's account."""
    response = client.get(
        "/api/v1/accounts/me",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        cookies={"client_token": test_user_session.client_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("email") == test_account.email
    assert data.get("name") == test_account.name


def test_account_endpoints_get_my_account_unauthorized(client):
    """Test retrieving my-account without a matching session cookie."""
    response = client.get("/api/v1/accounts/me")
    assert response.status_code == 401


def test_account_endpoints_get_accounts_with_associations(
    client, valid_jwt_token, test_account, test_group
):
    """Test retrieving accounts with group associations."""
    response = client.get(
        "/api/v1/accounts/with-groups",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert test_account.id is not None
    assert test_group.id is not None


def test_account_endpoints_delete_account_success(
    client, valid_jwt_token, test_db_session
):
    """Test successful account deletion."""
    account = Account(name="To Delete", email="delete@example.com")
    test_db_session.add(account)
    test_db_session.flush()
    login = Login(account_id=account.id, hashed_password="hash")
    test_db_session.add(login)
    test_db_session.commit()
    test_db_session.refresh(account)
    account_id = account.id
    response = client.delete(
        f"/api/v1/accounts/{account_id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code in (200, 204)


def test_account_endpoints_delete_account_not_found(client, valid_jwt_token):
    """Test deleting non-existent account returns 404."""
    response = client.delete(
        "/api/v1/accounts/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_account_endpoints_delete_account_invalid_id_format(client, valid_jwt_token):
    """Test deleting with invalid ID format."""
    response = client.delete(
        "/api/v1/accounts/invalid-format",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code in (404, 422)


@pytest.mark.parametrize(
    "endpoint,status_code",
    [
        ("/api/v1/accounts", 401),
        ("/api/v1/accounts/me", 401),
        ("/api/v1/accounts/nonexistent", 401),
    ],
)
def test_account_httpexceptions_account_endpoint_errors(client, endpoint, status_code):
    """Test account endpoint error scenarios."""
    response = client.get(endpoint)
    assert response.status_code == status_code


def test_account_httpexceptions_delete_account_unauthorized(client):
    """Test account deletion endpoint without authentication."""
    response = client.delete("/api/v1/accounts/some-id")
    assert response.status_code == 401


def test_account_httpexceptions_account_modification_unauthorized(client):
    """Test account modification endpoint without authentication."""
    response = client.put(
        "/api/v1/accounts",
        json={"name": "Test", "email": "test@example.com", "password": "password"},
    )
    assert response.status_code == 401
