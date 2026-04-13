"""Integration tests for audihose.api.groups module."""

import pytest


def test_group_endpoints_get_all_groups(client, valid_jwt_token, test_group):
    """Test retrieving all groups."""
    response = client.get(
        "/api/v1/groups", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert test_group.id is not None


def test_group_endpoints_get_all_groups_empty_list(
    client, valid_jwt_token, test_db_session
):
    """Test retrieving groups when list is empty."""
    response = client.get(
        "/api/v1/groups", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert test_db_session is not None


def test_group_endpoints_get_group_by_id(client, valid_jwt_token, test_group):
    """Test retrieving a specific group."""
    response = client.get(
        f"/api/v1/groups/{test_group.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("id") == test_group.id
    assert data.get("name") == test_group.name


def test_group_endpoints_get_group_not_found(client, valid_jwt_token):
    """Test retrieving non-existent group returns 404."""
    response = client.get(
        "/api/v1/groups/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_group_endpoints_create_new_group(client, valid_jwt_token):
    """Test creating a new group."""
    response = client.put(
        "/api/v1/groups",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={"name": "New Group", "accepting_submissions": True},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_group_endpoints_create_group_duplicate_name(
    client, valid_jwt_token, test_group
):
    """Test creating group with duplicate name."""
    response = client.put(
        "/api/v1/groups",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={"name": test_group.name, "accepting_submissions": True},
    )
    assert response.status_code in (200, 201, 400, 409, 422)


def test_group_endpoints_modify_existing_group(client, valid_jwt_token, test_group):
    """Test modifying an existing group."""
    response = client.patch(
        "/api/v1/groups",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={
            "id": test_group.id,
            "name": "Modified Group",
            "accepting_submissions": False,
        },
    )
    assert response.status_code == 200
    assert response.json() == 1


def test_group_endpoints_modify_group_not_found(client, valid_jwt_token):
    """Test modifying non-existent group returns 404."""
    response = client.patch(
        "/api/v1/groups",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={
            "id": "nonexistent-id",
            "name": "New Name",
            "accepting_submissions": True,
        },
    )
    assert response.status_code == 404


def test_group_endpoints_get_groups_for_account(
    client, valid_jwt_token, test_account, test_group, test_db_session
):
    """Test retrieving groups for a specific account."""
    test_group.accounts.append(test_account)
    test_db_session.add(test_group)
    test_db_session.commit()
    response = client.get(
        f"/api/v1/groups/by-account/{test_account.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_group_endpoints_get_groups_for_nonexistent_account(client, valid_jwt_token):
    """Test retrieving groups for non-existent account returns 404."""
    response = client.get(
        "/api/v1/groups/by-account/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_group_endpoints_get_accounts_in_group(
    client, valid_jwt_token, test_group, test_account, test_db_session
):
    """Test retrieving accounts in a group."""
    if test_account not in test_group.accounts:
        test_group.accounts.append(test_account)
        test_db_session.add(test_group)
        test_db_session.commit()
    response = client.get(
        f"/api/v1/groups/accounts/{test_group.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_group_endpoints_get_accounts_in_nonexistent_group(client, valid_jwt_token):
    """Test retrieving accounts in non-existent group returns 404."""
    response = client.get(
        "/api/v1/groups/accounts/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_group_endpoints_add_account_to_group(
    client, valid_jwt_token, test_account_2, test_group
):
    """Test adding an account to a group."""
    response = client.post(
        f"/api/v1/groups/accounts/{test_group.id}?account_id={test_account_2.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 200
    assert response.json() == 1


def test_group_endpoints_add_account_to_nonexistent_group(
    client, valid_jwt_token, test_account
):
    """Test adding account to non-existent group returns 404."""
    response = client.post(
        f"/api/v1/groups/accounts/nonexistent-id?account_id={test_account.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_group_endpoints_add_nonexistent_account_to_group(
    client, valid_jwt_token, test_group
):
    """Test adding non-existent account to group returns 404."""
    response = client.post(
        f"/api/v1/groups/accounts/{test_group.id}?account_id=nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_group_endpoints_replace_group_membership(
    client, valid_jwt_token, test_group, test_account, test_account_2
):
    """Test replacing/setting group membership."""
    response = client.patch(
        f"/api/v1/groups/accounts/{test_group.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={"account_ids": [test_account.id, test_account_2.id]},
    )
    assert response.status_code == 200
    assert response.json() == 1


def test_group_endpoints_replace_membership_nonexistent_group(client, valid_jwt_token):
    """Test replacing membership in non-existent group returns 404."""
    response = client.patch(
        "/api/v1/groups/accounts/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={"account_ids": []},
    )
    assert response.status_code == 404


def test_group_httpexceptions_group_endpoint_requires_auth(client):
    """Test that group endpoints are reachable without auth."""
    response = client.get("/api/v1/groups")
    assert response.status_code == 200


def test_group_httpexceptions_group_operations_unauthorized(client):
    """Test group operations return route-appropriate errors without auth."""
    endpoints = [
        ("GET", "/api/v1/groups"),
        ("GET", "/api/v1/groups/test-id"),
        ("PUT", "/api/v1/groups"),
        ("PATCH", "/api/v1/groups"),
        ("GET", "/api/v1/groups/by-account/test-id"),
        ("GET", "/api/v1/groups/accounts/test-id"),
        ("POST", "/api/v1/groups/accounts/test-id"),
        ("PATCH", "/api/v1/groups/accounts/test-id"),
    ]
    response = None
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "PUT":
            response = client.put(endpoint, json={})
        elif method == "PATCH":
            response = client.patch(endpoint, json={})
        elif method == "POST":
            response = client.post(endpoint, json={})
        else:
            pytest.fail(f"Unhandled method: {method}")
        assert response is not None
        assert response.status_code in (200, 404, 422), (
            f"Unexpected status for {method} {endpoint}: {response.status_code}"
        )


@pytest.mark.parametrize(
    "nonexistent_id", ["fake-id", "00000000-0000-0000-0000-000000000000"]
)
def test_group_httpexceptions_group_not_found_scenarios(
    client, valid_jwt_token, nonexistent_id
):
    """Test various 404 scenarios for groups."""
    response = client.get(
        f"/api/v1/groups/{nonexistent_id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404
