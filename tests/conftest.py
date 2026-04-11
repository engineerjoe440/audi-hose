"""Shared pytest fixtures for Audi-Hose backend tests."""

# pylint: disable=redefined-outer-name,import-outside-toplevel,protected-access
# pylint: disable=no-member,unexpected-keyword-arg,unused-argument
# pylint: disable=line-too-long,too-many-function-args

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session as SQLModelSession

from audihose.main import app
from audihose.authentication import JWTBearer
from audihose.database import Account, Login, PublicationGroup, Recording, get_session, ensure_default_publication_group
from audihose.security import get_hashed_password, sign_jwt
from audihose.sessions import SessionManager, UserSession
from audihose.configuration import ConfigurationSettings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_config(temp_dir):
    """Create a ConfigurationSettings instance with temporary recordings path."""
    # Create a mock config that uses temp directory
    config = MagicMock(spec=ConfigurationSettings)
    config.recordings_file_path = Path(temp_dir) / "recordings"
    config.recordings_file_path.mkdir(parents=True, exist_ok=True)
    return config


@pytest.fixture
def test_db_session():
    """Create an in-memory SQLite database session for testing."""
    # Use sqlite:///:memory: for in-memory SQLite
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    with SQLModelSession(engine) as session:
        # Ensure default publication group exists
        ensure_default_publication_group(session)
        yield session


@pytest.fixture
def test_account(test_db_session):
    """Create a test account in the database."""
    account = Account(name="Test User", email="test@example.com")
    login = Login(account=account, hashed_password=get_hashed_password("testpass123"))

    test_db_session.add(account)
    test_db_session.add(login)
    test_db_session.commit()
    test_db_session.refresh(account)

    return account


@pytest.fixture
def test_account_2(test_db_session):
    """Create a second test account in the database."""
    account = Account(name="Another User", email="another@example.com")
    login = Login(account=account, hashed_password=get_hashed_password("anotherpass123"))

    test_db_session.add(account)
    test_db_session.add(login)
    test_db_session.commit()
    test_db_session.refresh(account)

    return account


@pytest.fixture
def test_group(test_db_session):
    """Create a test publication group in the database."""
    # Fetch the default group instead of creating a new one
    group = test_db_session.query(PublicationGroup).filter_by(name="DEFAULT-PUBLICATION-GROUP").first()

    if not group:
        group = PublicationGroup(name="DEFAULT-PUBLICATION-GROUP", accepting_submissions=True)
        test_db_session.add(group)
        test_db_session.commit()
        test_db_session.refresh(group)

    return group


@pytest.fixture
def test_group_2(test_db_session):
    """Create a second test publication group in the database."""
    group = PublicationGroup(name="Test Group 2", accepting_submissions=True)
    test_db_session.add(group)
    test_db_session.commit()
    test_db_session.refresh(group)

    return group


@pytest.fixture
def test_recording(test_db_session, test_account, test_group, temp_dir):
    """Create a test recording in the database."""
    # Create a temporary audio file
    file_path = Path(temp_dir) / "test_recording.wav"
    file_path.write_bytes(b"fake audio data")

    recording = Recording(
        subject="Test Recording",
        email=test_account.email,
        file_path=str(file_path),
        group_id=test_group.id,
    )
    test_db_session.add(recording)
    test_db_session.commit()
    test_db_session.refresh(recording)

    return recording


@pytest.fixture
def valid_jwt_token(test_user_session):
    """Create a valid JWT token for a test account."""
    from audihose.sessions import REMEMBER_ME_INACTIVITY_SECONDS
    token = sign_jwt(
        {"email": test_user_session.email, "id": test_user_session.account_id, "session": test_user_session.client_token},
        expiry_seconds=REMEMBER_ME_INACTIVITY_SECONDS
    )
    return token


@pytest.fixture
def expired_jwt_token(test_account):
    """Create an expired JWT token for a test account."""
    # Create a token that's already expired (expiry_seconds=0 means expires immediately)
    token = sign_jwt(
        {"email": test_account.email, "id": test_account.id, "session": "fake_session"},
        expiry_seconds=0  # Already expired
    )
    return token


@pytest.fixture
def test_session_manager():
    """Create a fresh SessionManager instance for testing."""
    manager = SessionManager()
    manager._sessions.clear()  # Ensure it's empty
    return manager


@pytest.fixture
def test_user_session(test_account):
    """Create a test UserSession."""
    # Create a session without JWT token for now
    session = UserSession(
        client_token="test_client_token_123",
        email=test_account.email,
        account_id=test_account.id,
        remember_me=False,
    )
    return session


@pytest.fixture
def mock_smtp(mocker):
    """Mock the SMTP client."""
    return mocker.patch("smtplib.SMTP")


@pytest.fixture
def mock_ntfy(mocker):
    """Mock the requests.post for ntfy."""
    return mocker.patch("requests.post")


@pytest.fixture
def mock_aiofiles(mocker):
    """Mock aiofiles for async file operations."""
    mock_open = mocker.patch("aiofiles.open")
    mock_file = MagicMock()
    mock_file.write = MagicMock(return_value=None)
    mock_file.read = MagicMock(return_value=b"fake audio data")
    mock_open.return_value.__aenter__.return_value = mock_file
    return mock_open


@pytest.fixture
def client(test_db_session):
    """Create a FastAPI TestClient with dependency overrides."""

    # Override get_session dependency
    def override_get_session():
        return test_db_session

    app.dependency_overrides[get_session] = override_get_session

    # Create test client
    client = TestClient(app)

    yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_auth(client, test_account, valid_jwt_token, mocker):
    """Create a FastAPI TestClient with authenticated user."""
    # Mock JWTBearer dependency to accept any Bearer token
    def override_jwt_bearer():
        return test_account

    app.dependency_overrides[JWTBearer()] = override_jwt_bearer

    # Set up the client with Authorization header
    client.headers.update({"Authorization": f"Bearer {valid_jwt_token}"})

    yield client

    # Clean up
    app.dependency_overrides.clear()
    if "Authorization" in client.headers:
        del client.headers["Authorization"]
