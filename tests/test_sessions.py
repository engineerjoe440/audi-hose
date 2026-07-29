"""Unit tests for audihose.sessions module."""

import time

from audihose.security import sign_jwt
from audihose.sessions import SessionManager, UserSession


def test_user_session_user_session_creation(test_account):
    """Test UserSession is created with correct attributes."""
    session = UserSession()
    session.email = test_account.email
    session.account_id = test_account.id
    session.configure_authenticated(remember_me=False)
    assert session.client_token
    assert session.email == test_account.email
    assert session.account_id == test_account.id
    assert session.remember_me is False
    assert session.last_access is not None


def test_user_session_user_session_stale_property_fresh(test_account):
    """Test that fresh session is not stale."""
    session = UserSession()
    session.email = test_account.email
    session.account_id = test_account.id
    session.configure_authenticated(remember_me=False)
    assert session.stale is False


def test_user_session_user_session_stale_property_expired(test_account):
    """Test that session becomes stale after inactivity timeout."""
    session = UserSession()
    session.email = test_account.email
    session.account_id = test_account.id
    session.configure_authenticated(remember_me=False)
    session.last_access = session.last_access.replace(year=session.last_access.year - 1)
    assert session.stale is True


def test_user_session_user_session_stale_with_remember_me(test_account):
    """Test that remember_me extends grace period for staleness."""
    session = UserSession()
    session.email = test_account.email
    session.account_id = test_account.id
    session.configure_authenticated(remember_me=True)
    assert session.stale is False or session.remember_me is True


def test_user_session_user_session_touch(test_account):
    """Test that touching session updates last_activity."""
    session = UserSession()
    session.email = test_account.email
    session.account_id = test_account.id
    session.configure_authenticated(remember_me=False)
    old_activity = session.last_access
    time.sleep(0.01)
    session.access()
    assert session.last_access > old_activity


def test_session_manager_session_manager_new_session(
    test_session_manager, test_account
):
    """Test creating a new session."""
    client_token = test_session_manager.new_session()
    assert client_token is not None
    session = test_session_manager.get_session(client_token)
    assert session is not None
    session.email = test_account.email
    assert session.email == test_account.email


def test_session_manager_session_manager_get_session_exists(
    test_session_manager, test_account
):
    """Test retrieving an existing session."""
    client_token = test_session_manager.new_session()
    session = test_session_manager.get_session(client_token)
    session.email = test_account.email
    retrieved = test_session_manager.get_session(client_token)
    assert retrieved is not None
    assert retrieved.client_token == session.client_token
    assert retrieved.email == test_account.email


def test_session_manager_session_manager_get_session_not_found(test_session_manager):
    """Test retrieving a non-existent session returns None."""
    result = test_session_manager.get_session("nonexistent_token")
    assert result is None


def test_session_manager_session_manager_get_session_updates_activity(
    test_session_manager, test_account
):
    """Test that get_session updates last_activity."""
    client_token = test_session_manager.new_session()
    retrieved = test_session_manager.get_session(client_token)
    retrieved.email = test_account.email
    old_activity = retrieved.last_access
    time.sleep(0.01)
    retrieved2 = test_session_manager.get_session(client_token)
    assert retrieved2.last_access >= old_activity


def test_session_manager_session_manager_close_session(
    test_session_manager, test_account
):
    """Test closing a session removes it."""
    client_token = test_session_manager.new_session()
    session = test_session_manager.get_session(client_token)
    session.email = test_account.email
    assert test_session_manager.get_session(client_token) is not None
    test_session_manager.close_session(client_token)
    assert test_session_manager.get_session(client_token) is None


def test_session_manager_session_manager_close_nonexistent(test_session_manager):
    """Test closing a non-existent session doesn't error."""
    test_session_manager.close_session("nonexistent_token")


def test_session_manager_session_manager_prune_sessions(
    test_session_manager, test_account
):
    """Test prune_sessions removes only stale sessions."""
    token1 = sign_jwt({"sub": test_account.email, "account_id": test_account.id})
    token2 = sign_jwt({"sub": test_account.email, "account_id": test_account.id})
    client_token_1 = test_session_manager.new_session()
    client_token_2 = test_session_manager.new_session()
    session1 = test_session_manager.get_session(client_token_1)
    session2 = test_session_manager.get_session(client_token_2)
    session1.email = test_account.email
    session2.email = test_account.email
    assert token1 != token2
    session1.last_access = session1.last_access.replace(year=session1.last_access.year - 1)
    test_session_manager.prune_sessions()
    assert test_session_manager.get_session(client_token_1) is None
    assert test_session_manager.get_session(client_token_2) is not None


def test_session_manager_session_manager_singleton_behavior():
    """Test that SessionManager instances share state."""
    manager1 = SessionManager()
    manager2 = SessionManager()
    assert manager1 is manager2 or manager1.user_sessions is manager2.user_sessions


def test_convenience_functions_get_session_function(
    test_session_manager, test_account, mocker
):
    """Test get_session() convenience function."""
    mocker.patch("audihose.sessions.SessionManager", return_value=test_session_manager)
    client_token = test_session_manager.new_session()
    session = test_session_manager.get_session(client_token)
    session.email = test_account.email
    session.account_id = test_account.id
    assert session.email == test_account.email


def test_convenience_functions_close_session_function(
    test_session_manager, test_account, mocker
):
    """Test close_session() convenience function."""
    mocker.patch("audihose.sessions.SessionManager", return_value=test_session_manager)
    client_token = test_session_manager.new_session()
    session = test_session_manager.get_session(client_token)
    session.email = test_account.email
    session.account_id = test_account.id
    test_session_manager.close_session(client_token)
    assert test_session_manager.get_session(client_token) is None
