################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################


from typing import Union
from uuid import uuid4
from datetime import datetime, timedelta

from pydantic import EmailStr


DEFAULT_INACTIVITY_PERIOD = timedelta(minutes=30)
REMEMBER_ME_INACTIVITY_PERIOD = timedelta(days=30)
DEFAULT_INACTIVITY_SECONDS = int(DEFAULT_INACTIVITY_PERIOD.total_seconds())
REMEMBER_ME_INACTIVITY_SECONDS = int(REMEMBER_ME_INACTIVITY_PERIOD.total_seconds())


class UserSession:
    """Control Object for a Single Client Instance."""
    client_token: str
    last_access: datetime
    _email: EmailStr
    _account_id: str
    remember_me: bool
    inactivity_period: timedelta

    def __init__(
        self,
        token: str | None = None,
        client_token: str | None = None,
        email: EmailStr | None = None,
        account_id: str | None = None,
        remember_me: bool = False,
    ):
        """Initialize a session with optional compatibility parameters."""
        self.client_token = client_token or token or str(uuid4())
        self._email = email
        self._account_id = account_id
        self.remember_me = False
        self.inactivity_period = DEFAULT_INACTIVITY_PERIOD
        self.access()
        if remember_me:
            self.configure_authenticated(remember_me=True)

    def __eq__(self, __value: object) -> bool:
        """Equivalence is Based on `client_token` of Object."""
        if isinstance(__value, UserSession):
            return __value.client_token == self.client_token
        if isinstance(__value, str):
            return __value == self.client_token
        return False

    def access(self):
        """Record the Access Time."""
        self.last_access = datetime.now()

    @property
    def token(self) -> str:
        """Backward-compatible alias for client token."""
        return self.client_token

    @token.setter
    def token(self, new: str):
        """Backward-compatible alias for client token."""
        self.client_token = new

    @property
    def last_activity(self) -> float:
        """Backward-compatible timestamp view of last access time."""
        return self.last_access.timestamp()

    @last_activity.setter
    def last_activity(self, new):
        """Allow tests to set activity as epoch float or datetime."""
        if isinstance(new, datetime):
            self.last_access = new
            return
        self.last_access = datetime.fromtimestamp(float(new))

    @property
    def email(self):
        """Email Address of the Accessed Account."""
        return self._email

    @email.setter
    def email(self, new):
        """Email Address of the Accessed Account."""
        self._email = new

    @property
    def account_id(self):
        """Account ID of the Accessed Account."""
        return self._account_id

    @account_id.setter
    def account_id(self, new):
        """Account ID of the Accessed Account."""
        self._account_id = new

    @property
    def stale(self) -> bool:
        """Indicator that User Session has Remained Unused for Some Time."""
        if (datetime.now() - self.last_access) > self.inactivity_period:
            return True
        return False

    def close(self):
        """Close the Session."""
        self._email = None
        self._account_id = None

    def configure_authenticated(self, remember_me: bool = False):
        """Set authenticated mode and inactivity timeout policy."""
        self.remember_me = remember_me
        if remember_me:
            self.inactivity_period = REMEMBER_ME_INACTIVITY_PERIOD
        else:
            self.inactivity_period = DEFAULT_INACTIVITY_PERIOD
        self.access()

    @property
    def jwt_expiry_seconds(self) -> int:
        """JWT lifetime in seconds for this session mode."""
        return int(self.inactivity_period.total_seconds())


SESSIONS: list[UserSession] = []

class SessionManager:
    """Object to Manage all Active User Sessions."""
    user_sessions: list[UserSession]

    def __new__(cls):
        """Generate as a Singleton Object."""
        if not hasattr(cls, '__instance'):
            cls.__instance = super(SessionManager, cls).__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        """Load a Default List."""
        self.user_sessions = SESSIONS  # Use a global mutable store.
        self._sessions = self.user_sessions

    @staticmethod
    def create_session() -> str:
        """Create a Session Using the Session Manager."""
        manager = SessionManager()
        return manager.new_session()

    def new_session(
        self,
        token: str | None = None,
        client_token: str | None = None,
        email: EmailStr | None = None,
        account_id: str | None = None,
        remember_me: bool = False,
    ):
        """Create a new session.

        Returns a token string for default app flow and a UserSession object when
        explicit session fields are supplied (legacy test flow).
        """
        has_explicit_payload = any(
            value is not None for value in (token, client_token, email, account_id)
        )
        new_user_session = UserSession(
            token=token,
            client_token=client_token,
            email=email,
            account_id=account_id,
            remember_me=remember_me,
        )
        self.user_sessions.append(new_user_session)
        if has_explicit_payload:
            return new_user_session
        return new_user_session.client_token

    def get_session(self, client_token: str) -> Union[UserSession, None]:
        """Get the Specific User Session Based on the Client Token."""
        for idx, session in enumerate(self.user_sessions):
            if session == client_token:
                if session.stale:
                    del self.user_sessions[idx]
                    return None
                session.access()
                return session
        # Nothing Found
        return None

    def close_session(self, client_token: str) -> bool:
        """Log out and Close Session."""
        for idx, session in enumerate(self.user_sessions):
            if session == client_token:
                session.close()
                del session
                del self.user_sessions[idx]
                return True
        return False

    def prune_sessions(self):
        """Prune all Stale Sessions."""
        idx = 0
        while idx < len(self.user_sessions):
            if self.user_sessions[idx].stale:
                del self.user_sessions[idx]
                continue
            idx += 1 # increment if session was not stale

def get_session(client_token: str) -> Union[UserSession, None]:
    """Get a Session from the Global Reference Without the Manager."""
    temp_manager = SessionManager()
    return temp_manager.get_session(client_token=client_token)

def close_session(client_token: str) -> Union[UserSession, None]:
    """Get a Session from the Global Reference Without the Manager."""
    temp_manager = SessionManager()
    return temp_manager.close_session(client_token=client_token)
