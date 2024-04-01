################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################


from typing import Union
from uuid import uuid4
from datetime import datetime, timedelta


ALLOWED_INACTIVITY_PERIOD = timedelta(minutes=30)


class UserSession:
    """Control Object for a Single Client Instance."""
    client_token: str
    last_access: datetime
    _image_bytes: bytes

    def __init__(self):
        """Record the Client Token for this Session."""
        self.client_token = str(uuid4())
        self.zsuite_session = None
        self.temp_directory = None
        self._image_bytes = None
        self._accessed()

    def __eq__(self, __value: object) -> bool:
        """Equivalence is Based on `client_token` of Object."""
        if isinstance(__value, UserSession):
            return __value.client_token == self.client_token
        elif isinstance(__value, str):
            return __value == self.client_token

    def _accessed(self):
        """Record the Access Time."""
        self.last_access = datetime.now()

    @property
    def stale(self) -> bool:
        """Indicator that User Session has Remained Unused for Some Time."""
        if (datetime.now() - self.last_access) > ALLOWED_INACTIVITY_PERIOD:
            return True
        return False

    def close(self) -> bool:
        """Close the Active Session."""
        self.zsuite_session.logout()
        self.zsuite_session = None
        self.temp_directory.cleanup()
        self.temp_directory = None


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
        self.user_sessions = SESSIONS # Use a Global, Mutable Object

    @staticmethod
    def create_session() -> str:
        """Create a Session Using the Session Manager."""
        manager = SessionManager()
        return manager.new_session()

    def new_session(self):
        """Create a New Session and Provide its Unique ID."""
        self.user_sessions.append(UserSession())
        return self.user_sessions[-1].client_token

    def get_session(self, client_token: str) -> Union[UserSession, None]:
        """Get the Specific User Session Based on the Client Token."""
        for session in self.user_sessions:
            if session == client_token:
                return session
        # Nothing Found
        return None

    def close_session(self, client_token: str) -> bool:
        """Log out and Close Session."""
        for idx, session in enumerate(self.user_sessions):
            if session == client_token:
                session.close()
                del self.user_sessions[idx]
                return

    def prune_sessions(self):
        """Prune all Stale Sessions."""
        idx = 0
        while idx < len(self.user_sessions):
            if self.user_sessions[idx].stale:
                self.user_sessions[idx].close()
                del self.user_sessions[idx]
                continue
            idx += 1 # increment if session was not stale

def get_session(client_token: str) -> Union[UserSession, None]:
    """Get a Session from the Global Reference Without the Manager."""
    temp_manager = SessionManager()
    return temp_manager.get_session(client_token=client_token)
