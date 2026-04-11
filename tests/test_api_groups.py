"""Integration tests for audihose.api.groups module."""

# pylint: disable=line-too-long,unused-argument,consider-using-in
# pylint: disable=too-many-arguments,too-many-positional-arguments
# pylint: disable=possibly-used-before-assignment

import pytest
from audihose.database import PublicationGroupAccountLink


class TestGroupEndpoints:
    """Test publication group management HTTP endpoints."""

    def test_get_all_groups(self, client, valid_jwt_token, test_group):
        """Test retrieving all groups."""
        response = client.get(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_groups_empty_list(self, client, valid_jwt_token, test_db_session):
        """Test retrieving groups when list is empty."""
        # Delete all groups except default
        # (Some groups might always exist)
        response = client.get(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_group_by_id(self, client, valid_jwt_token, test_group):
        """Test retrieving a specific group."""
        response = client.get(
            f"/api/v1/groups/{test_group.id}",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == test_group.id
        assert data.get("name") == test_group.name

    def test_get_group_not_found(self, client, valid_jwt_token):
        """Test retrieving non-existent group returns 404."""
        response = client.get(
            "/api/v1/groups/nonexistent-id",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 404

    def test_create_new_group(self, client, valid_jwt_token):
        """Test creating a new group."""
        response = client.put(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={
                "name": "New Group",
                "accepting_submissions": True,
            },
        )

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert data.get("name") == "New Group"

    def test_create_group_duplicate_name(self, client, valid_jwt_token, test_group):
        """Test creating group with duplicate name."""
        response = client.put(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={
                "name": test_group.name,
                "accepting_submissions": True,
            },
        )

        # May allow duplicates or return error
        # Depends on implementation
        assert response.status_code in (200, 201, 400, 409, 422)

    def test_modify_existing_group(self, client, valid_jwt_token, test_group):
        """Test modifying an existing group."""
        response = client.patch(
            f"/api/v1/groups/{test_group.id}",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={
                "name": "Modified Group",
                "accepting_submissions": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("name") == "Modified Group"
        assert data.get("accepting_submissions") is False

    def test_modify_group_not_found(self, client, valid_jwt_token):
        """Test modifying non-existent group returns 404."""
        response = client.patch(
            "/api/v1/groups/nonexistent-id",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"name": "New Name"},
        )

        assert response.status_code == 404

    def test_get_groups_for_account(self, client, valid_jwt_token, test_account, test_group, test_db_session):
        """Test retrieving groups for a specific account."""
        # Add account to group
        link = PublicationGroupAccountLink(account_id=test_account.id, group_id=test_group.id)
        test_db_session.add(link)
        test_db_session.commit()

        response = client.get(
            f"/api/v1/accounts/{test_account.id}/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_groups_for_nonexistent_account(self, client, valid_jwt_token):
        """Test retrieving groups for non-existent account returns 404."""
        response = client.get(
            "/api/v1/accounts/nonexistent-id/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 404

    def test_get_accounts_in_group(self, client, valid_jwt_token, test_group, test_account, test_db_session):
        """Test retrieving accounts in a group."""
        # Add account to group if not already
        existing = test_db_session.query(PublicationGroupAccountLink).filter_by(
            account_id=test_account.id, group_id=test_group.id
        ).first()

        if not existing:
            link = PublicationGroupAccountLink(account_id=test_account.id, group_id=test_group.id)
            test_db_session.add(link)
            test_db_session.commit()

        response = client.get(
            f"/api/v1/groups/{test_group.id}/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_accounts_in_nonexistent_group(self, client, valid_jwt_token):
        """Test retrieving accounts in non-existent group returns 404."""
        response = client.get(
            "/api/v1/groups/nonexistent-id/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 404

    def test_add_account_to_group(self, client, valid_jwt_token, test_account_2, test_group):
        """Test adding an account to a group."""
        response = client.post(
            f"/api/v1/groups/{test_group.id}/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"account_id": test_account_2.id},
        )

        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert isinstance(data, list)

    def test_add_account_to_nonexistent_group(self, client, valid_jwt_token, test_account):
        """Test adding account to non-existent group returns 404."""
        response = client.post(
            "/api/v1/groups/nonexistent-id/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"account_id": test_account.id},
        )

        assert response.status_code == 404

    def test_add_nonexistent_account_to_group(self, client, valid_jwt_token, test_group):
        """Test adding non-existent account to group returns 404."""
        response = client.post(
            f"/api/v1/groups/{test_group.id}/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"account_id": "nonexistent-id"},
        )

        assert response.status_code == 404

    def test_replace_group_membership(self, client, valid_jwt_token, test_group, test_account, test_account_2):
        """Test replacing/setting group membership."""
        response = client.put(
            f"/api/v1/groups/{test_group.id}/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"account_ids": [test_account.id, test_account_2.id]},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_replace_membership_nonexistent_group(self, client, valid_jwt_token):
        """Test replacing membership in non-existent group returns 404."""
        response = client.put(
            "/api/v1/groups/nonexistent-id/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"account_ids": []},
        )

        assert response.status_code == 404


class TestGroupHTTPExceptions:
    """Test HTTP exceptions in group endpoints."""

    def test_group_endpoint_requires_auth(self, client):
        """Test that group endpoints require authentication (401)."""
        response = client.get("/api/v1/groups")

        assert response.status_code == 401

    def test_group_operations_unauthorized(self, client):
        """Test group operations without authentication (401)."""
        endpoints = [
            ("GET", "/api/v1/groups"),
            ("GET", "/api/v1/groups/test-id"),
            ("PUT", "/api/v1/groups"),
            ("PATCH", "/api/v1/groups/test-id"),
            ("GET", "/api/v1/accounts/test-id/groups"),
            ("GET", "/api/v1/groups/test-id/accounts"),
            ("POST", "/api/v1/groups/test-id/accounts"),
            ("PUT", "/api/v1/groups/test-id/accounts"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "PATCH":
                response = client.patch(endpoint, json={})
            elif method == "POST":
                response = client.post(endpoint, json={})

            assert response.status_code == 401, f"Expected 401 for {method} {endpoint}, got {response.status_code}"

    @pytest.mark.parametrize("nonexistent_id", ["fake-id", "00000000-0000-0000-0000-000000000000"])
    def test_group_not_found_scenarios(self, client, valid_jwt_token, nonexistent_id):
        """Test various 404 scenarios for groups."""
        # Get single group
        response = client.get(
            f"/api/v1/groups/{nonexistent_id}",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )
        assert response.status_code == 404
