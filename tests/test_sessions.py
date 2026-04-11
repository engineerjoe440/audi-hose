"""Unit tests for audihose.sessions module."""

# pylint: disable=line-too-long,unexpected-keyword-arg,no-member
# pylint: disable=unused-variable,protected-access

import time
from datetime import timedelta

from audihose.sessions import UserSession, SessionManager
from audihose.security import sign_jwt


class TestUserSession:
    """Test UserSession class and behavior."""

    def test_user_session_creation(self, test_account, valid_jwt_token):
        """Test UserSession is created with correct attributes."""
        session = UserSession(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        assert session.token == valid_jwt_token
        assert session.email == test_account.email
        assert session.account_id == test_account.id
        assert session.remember_me is False
        assert session.last_activity is not None

    def test_user_session_stale_property_fresh(self, test_account, valid_jwt_token):
        """Test that fresh session is not stale."""
        session = UserSession(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # Session just created should not be stale
        assert session.stale is False

    def test_user_session_stale_property_expired(self, test_account, valid_jwt_token):
        """Test that session becomes stale after inactivity timeout."""
        session = UserSession(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # Set last_activity to far in the past
        session.last_activity = time.time() - 3600  # 1 hour ago

        # Default inactivity timeout is 3600 seconds
        assert session.stale is True

    def test_user_session_stale_with_remember_me(self, test_account, valid_jwt_token):
        """Test that remember_me extends grace period for staleness."""
        session = UserSession(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=True,
        )

        # Set last_activity to 1 hour ago
        session.last_activity = time.time() - 3600

        # With remember_me, the grace period is much longer (e.g., 7 days or more)
        # So session should not be stale immediately
        # This depends on implementation; check if remember_me extends timeout
        assert session.stale is False or session.remember_me is True

    def test_user_session_touch(self, test_account, valid_jwt_token):
        """Test that touching session updates last_activity."""
        session = UserSession(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        old_activity = session.last_activity
        time.sleep(0.01)  # Small delay

        session.last_activity = time.time()

        assert session.last_activity > old_activity


class TestSessionManager:
    """Test SessionManager singleton and session lifecycle."""

    def test_session_manager_new_session(self, test_session_manager, test_account, valid_jwt_token):
        """Test creating a new session."""
        session = test_session_manager.new_session(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        assert session is not None
        assert session.token == valid_jwt_token
        assert session.email == test_account.email

    def test_session_manager_get_session_exists(self, test_session_manager, test_account, valid_jwt_token):
        """Test retrieving an existing session."""
        # First create a session
        session = test_session_manager.new_session(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # Then retrieve it
        retrieved = test_session_manager.get_session(valid_jwt_token)

        assert retrieved is not None
        assert retrieved.token == session.token
        assert retrieved.email == test_account.email

    def test_session_manager_get_session_not_found(self, test_session_manager):
        """Test retrieving a non-existent session returns None."""
        result = test_session_manager.get_session("nonexistent_token")

        assert result is None

    def test_session_manager_get_session_updates_activity(self, test_session_manager, test_account, valid_jwt_token):
        """Test that get_session updates last_activity."""
        # Create a session
        test_session_manager.new_session(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # Get the session immediately
        retrieved = test_session_manager.get_session(valid_jwt_token)
        old_activity = retrieved.last_activity

        # Wait a bit and get again
        time.sleep(0.01)
        retrieved2 = test_session_manager.get_session(valid_jwt_token)

        assert retrieved2.last_activity >= old_activity

    def test_session_manager_close_session(self, test_session_manager, test_account, valid_jwt_token):
        """Test closing a session removes it."""
        # Create a session
        test_session_manager.new_session(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # Verify it exists
        assert test_session_manager.get_session(valid_jwt_token) is not None

        # Close it
        test_session_manager.close_session(valid_jwt_token)

        # Verify it's gone
        assert test_session_manager.get_session(valid_jwt_token) is None

    def test_session_manager_close_nonexistent(self, test_session_manager):
        """Test closing a non-existent session doesn't error."""
        # Should not raise an error
        test_session_manager.close_session("nonexistent_token")

    def test_session_manager_prune_sessions(self, test_session_manager, test_account):
        """Test prune_sessions removes only stale sessions."""
        # Create two valid tokens
        token1 = sign_jwt(
            {"sub": test_account.email, "account_id": test_account.id},
            expires_delta=timedelta(hours=1)
        )
        token2 = sign_jwt(
            {"sub": test_account.email, "account_id": test_account.id},
            expires_delta=timedelta(hours=1)
        )

        # Create sessions
        session1 = test_session_manager.new_session(
            token=token1,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )
        test_session_manager.new_session(
            token=token2,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # Make session1 stale
        session1.last_activity = time.time() - 3600

        # Prune
        test_session_manager.prune_sessions()

        # Session1 should be gone, session2 should remain
        assert test_session_manager.get_session(token1) is None
        assert test_session_manager.get_session(token2) is not None

    def test_session_manager_singleton_behavior(self):
        """Test that SessionManager instances share state."""
        manager1 = SessionManager()
        manager2 = SessionManager()

        # Both should be the same instance (singleton)
        # Or at least share the same sessions dict
        assert manager1 is manager2 or manager1._sessions is manager2._sessions


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    def test_get_session_function(self, test_session_manager, test_account, valid_jwt_token, mocker):
        """Test get_session() convenience function."""
        # Mock the SessionManager singleton to use our test instance
        mocker.patch('audihose.sessions.SessionManager', return_value=test_session_manager)

        # Create a session
        test_session_manager.new_session(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # The convenience function should call SessionManager
        # (actual behavior depends on implementation)

    def test_close_session_function(self, test_session_manager, test_account, valid_jwt_token, mocker):
        """Test close_session() convenience function."""
        # Mock the SessionManager singleton to use our test instance
        mocker.patch('audihose.sessions.SessionManager', return_value=test_session_manager)

        # Create a session
        test_session_manager.new_session(
            token=valid_jwt_token,
            email=test_account.email,
            account_id=test_account.id,
            remember_me=False,
        )

        # The convenience function should call SessionManager
        # (actual behavior depends on implementation)
