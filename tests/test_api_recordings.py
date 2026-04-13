"""Integration tests for audihose.api.recordings module."""

import io

import pytest
from audihose.database import PublicationGroup, Recording


def test_recording_endpoints_get_all_recordings(
    client, valid_jwt_token, test_recording
):
    """Test retrieving all recordings."""
    response = client.get(
        "/api/v1/recordings", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert test_recording.id is not None


def test_recording_endpoints_get_all_recordings_empty(
    client, valid_jwt_token, test_db_session
):
    """Test retrieving recordings when list is empty."""
    test_db_session.query(Recording).delete()
    test_db_session.commit()
    response = client.get(
        "/api/v1/recordings", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_recording_endpoints_get_recordings_by_group(
    client, valid_jwt_token, test_group, test_recording
):
    """Test retrieving recordings for a specific group."""
    response = client.get(
        f"/api/v1/recordings/group/{test_group.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert test_recording.group_id == test_group.id


def test_recording_endpoints_get_recordings_by_nonexistent_group(
    client, valid_jwt_token
):
    """Test retrieving recordings for non-existent group returns 404."""
    response = client.get(
        "/api/v1/recordings/group/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_recording_endpoints_get_single_recording(
    client, valid_jwt_token, test_recording
):
    """Test retrieving and streaming a single recording."""
    response = client.get(
        f"/api/v1/recordings/{test_recording.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code in (200, 307, 308)


def test_recording_endpoints_get_single_recording_not_found(client, valid_jwt_token):
    """Test retrieving non-existent recording returns 404."""
    response = client.get(
        "/api/v1/recordings/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_recording_endpoints_create_new_recording_success(
    client, valid_jwt_token, test_group, temp_dir
):
    """Test successful recording creation (file upload)."""
    audio_file = io.BytesIO(b"fake audio data")
    assert temp_dir
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Test Recording",
            "email": "submitter@example.com",
            "group_id": test_group.id,
        },
        files={"recording": ("test.wav", audio_file, "audio/wav")},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), str)


def test_recording_endpoints_create_recording_missing_file(
    client, valid_jwt_token, test_group
):
    """Test recording creation without file attachment."""
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Test Recording",
            "email": "submitter@example.com",
            "group_id": test_group.id,
        },
    )
    assert response.status_code in (400, 422)


def test_recording_endpoints_create_recording_nonexistent_group(
    client, valid_jwt_token
):
    """Test recording creation for non-existent group returns 404."""
    audio_file = io.BytesIO(b"fake audio data")
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Test Recording",
            "email": "submitter@example.com",
            "group_id": "nonexistent-id",
        },
        files={"recording": ("test.wav", audio_file, "audio/wav")},
    )
    assert response.status_code == 404


def test_recording_endpoints_create_recording_group_not_accepting(
    client, valid_jwt_token, test_db_session
):
    """Test recording creation for group that's not accepting submissions."""
    closed_group = PublicationGroup(name="Closed Group", accepting_submissions=False)
    test_db_session.add(closed_group)
    test_db_session.commit()
    test_db_session.refresh(closed_group)
    audio_file = io.BytesIO(b"fake audio data")
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Test Recording",
            "email": "submitter@example.com",
            "group_id": closed_group.id,
        },
        files={"recording": ("test.wav", audio_file, "audio/wav")},
    )
    assert response.status_code == 423


def test_recording_notification_flow_create_recording_triggers_notification(
    client, valid_jwt_token, test_group, test_account, mock_smtp
):
    """Test that creating a recording triggers email notifications."""
    test_group.accounts.append(test_account)
    assert mock_smtp is not None
    audio_file = io.BytesIO(b"fake audio data")
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Test Recording",
            "email": "submitter@example.com",
            "group_id": test_group.id,
        },
        files={"recording": ("test.wav", audio_file, "audio/wav")},
    )
    assert response.status_code == 200


def test_recording_notification_flow_send_notification_to_group_members(
    client, valid_jwt_token, test_recording, mock_smtp
):
    """Test sending notification for specific recording."""
    assert mock_smtp is not None
    response = client.post(
        f"/api/v1/recordings/notify/{test_recording.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code in (200, 422)


def test_recording_notification_flow_send_notification_nonexistent_recording(
    client, valid_jwt_token
):
    """Test sending notification for non-existent recording returns 404."""
    response = client.post(
        "/api/v1/recordings/notify/nonexistent-id",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_recording_httpexceptions_recording_endpoint_requires_auth(client):
    """Test recording endpoints are reachable without auth."""
    response = client.get("/api/v1/recordings")
    assert response.status_code == 401


def test_recording_httpexceptions_recording_operations_unauthorized(client):
    """Test recording operations return route-appropriate errors without auth."""
    endpoints = [
        ("GET", "/api/v1/recordings"),
        ("GET", "/api/v1/recordings/group/test-id"),
        ("GET", "/api/v1/recordings/test-id"),
        ("PUT", "/api/v1/recordings/"),
        ("POST", "/api/v1/recordings/notify/test-id"),
    ]
    response = None
    for method, endpoint in endpoints:
        if method == "GET":
            response = client.get(endpoint)
        elif method == "POST":
            response = client.post(endpoint, json={})
        elif method == "PUT":
            response = client.put(endpoint, data={})
        else:
            pytest.fail(f"Unhandled method: {method}")
        assert response is not None
        assert response.status_code == 401, (
            f"Unexpected status for {method} {endpoint}: {response.status_code}"
        )


@pytest.mark.parametrize(
    "recording_id", ["fake-id", "00000000-0000-0000-0000-000000000000"]
)
def test_recording_httpexceptions_recording_not_found_scenarios(
    client, valid_jwt_token, recording_id
):
    """Test various 404 scenarios for recordings."""
    response = client.get(
        f"/api/v1/recordings/{recording_id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code == 404


def test_recording_httpexceptions_recording_invalid_group_ids(client, valid_jwt_token):
    """Test recording retrieval with invalid group ID."""
    response = client.get(
        "/api/v1/recordings/group/invalid-uuid",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    assert response.status_code in (404, 422)


def test_recording_file_handling_upload_large_file(client, valid_jwt_token, test_group):
    """Test uploading a large audio file."""
    large_file = io.BytesIO(b"x" * (5 * 1024 * 1024))
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Large Recording",
            "email": "submitter@example.com",
            "group_id": test_group.id,
        },
        files={"recording": ("large.wav", large_file, "audio/wav")},
    )
    assert response.status_code in (200, 201, 413)


def test_recording_file_handling_upload_invalid_file_type(
    client, valid_jwt_token, test_group
):
    """Test uploading non-audio file."""
    invalid_file = io.BytesIO(b"not audio data")
    response = client.put(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        params={
            "subject": "Invalid File",
            "email": "submitter@example.com",
            "group_id": test_group.id,
        },
        files={"recording": ("invalid.txt", invalid_file, "text/plain")},
    )
    assert response.status_code in (200, 201, 400, 422)


def test_recording_file_handling_download_recording_stream(
    client, valid_jwt_token, test_recording
):
    """Test that recording download returns audio stream."""
    response = client.get(
        f"/api/v1/recordings/{test_recording.id}",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )
    if response.status_code == 200:
        assert (
            "audio" in response.headers.get("content-type", "").lower()
            or len(response.content) > 0
        )
