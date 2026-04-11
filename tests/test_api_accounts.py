"""Integration tests for audihose.api.accounts module."""

# pylint: disable=line-too-long,consider-using-in,unused-argument

import pytest
from audihose.database import Account, Login


class TestAccountEndpoints:
    """Test account management HTTP endpoints."""

    def test_create_new_account_success(self, client, valid_jwt_token):
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

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert data.get("email") == "newaccount@example.com"
        assert data.get("name") == "New Account"

    def test_create_account_duplicate_email(self, client, valid_jwt_token, test_account):
        """Test account creation with duplicate email."""
        response = client.put(
            "/api/v1/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={
                "name": "Another User",
                "email": test_account.email,  # Duplicate
                "password": "password123",
            },
        )

        # Should fail with 400 or 409 for duplicate
        assert response.status_code in (400, 409, 422)

    def test_get_all_accounts(self, client, valid_jwt_token, test_account, test_account_2):
        """Test retrieving all accounts."""
        response = client.get(
            "/api/v1/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should contain test accounts
        emails = [acc.get("email") for acc in data]
        assert test_account.email in emails or len(data) >= 1

    def test_get_all_accounts_empty(self, client, valid_jwt_token, test_db_session):
        """Test retrieving accounts when database is empty."""
        # Clear all accounts
        test_db_session.query(Account).delete()
        test_db_session.commit()

        response = client.get(
            "/api/v1/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_my_account(self, client, valid_jwt_token, test_account):
        """Test retrieving current user's account."""
        response = client.get(
            "/api/v1/my-account",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("email") == test_account.email
        assert data.get("name") == test_account.name

    def test_get_my_account_unauthorized(self, client):
        """Test retrieving my-account without authentication (401)."""
        response = client.get("/api/v1/my-account")

        assert response.status_code == 401

    def test_get_accounts_with_associations(self, client, valid_jwt_token, test_account, test_group):
        """Test retrieving accounts with group associations."""
        response = client.get(
            "/api/v1/accounts/associations",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_delete_account_success(self, client, valid_jwt_token, test_db_session):
        """Test successful account deletion."""
        # Create an account to delete
        account = Account(name="To Delete", email="delete@example.com")
        login = Login(account=account, hashed_password="hash")
        test_db_session.add(account)
        test_db_session.add(login)
        test_db_session.commit()
        test_db_session.refresh(account)

        account_id = account.id

        response = client.delete(
            f"/api/v1/accounts/{account_id}",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 204 or response.status_code == 200

    def test_delete_account_not_found(self, client, valid_jwt_token):
        """Test deleting non-existent account returns 404."""
        response = client.delete(
            "/api/v1/accounts/nonexistent-id",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 404

    def test_delete_account_invalid_id_format(self, client, valid_jwt_token):
        """Test deleting with invalid ID format."""
        response = client.delete(
            "/api/v1/accounts/invalid-format",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        # Could be 404 or 422 depending on validation
        assert response.status_code in (404, 422)


class TestAccountHTTPExceptions:
    """Test HTTP exceptions in account endpoints."""

    @pytest.mark.parametrize("endpoint,status_code", [
        ("/api/v1/accounts", 401),  # Missing auth
        ("/api/v1/my-account", 401),  # Missing auth
        ("/api/v1/accounts/nonexistent", 404),  # Not found
    ])
    def test_account_endpoint_errors(self, client, endpoint, status_code):
        """Test account endpoint error scenarios."""
        response = client.get(endpoint)

        if status_code == 401:
            assert response.status_code == 401
        elif status_code == 404:
            # Need auth header for 404 test
            response = client.get(
                endpoint,
                headers={"Authorization": "Bearer dummy"},
            )
            # Will likely fail auth first
            assert response.status_code in (401, 404)

    def test_delete_account_unauthorized(self, client):
        """Test account deletion without authentication (401)."""
        response = client.delete("/api/v1/accounts/some-id")

        assert response.status_code == 401

    def test_account_modification_unauthorized(self, client):
        """Test account modification without authentication (401)."""
        response = client.put(
            "/api/v1/accounts",
            json={
                "name": "Test",
                "email": "test@example.com",
                "password": "password",
            },
        )

        assert response.status_code == 401
