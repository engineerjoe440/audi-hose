"""Unit tests for audihose.database module."""

# pylint: disable=line-too-long,import-outside-toplevel,no-member
# pylint: disable=too-many-function-args,wrong-import-order

import pytest
from datetime import datetime

from audihose.database import (
    Account,
    Login,
    PublicationGroup,
    Recording,
    PublicationGroupAccountLink,
    generate_identifier,
    ensure_default_publication_group,
    to_account_summary,
    to_group_summary,
    to_recording_read,
    to_account_with_groups,
)


class TestIdentifierGeneration:
    """Test UUID generation utility."""

    def test_generate_identifier_returns_string(self):
        """Test that generate_identifier returns a string."""
        identifier = generate_identifier()
        assert isinstance(identifier, str)

    def test_generate_identifier_non_empty(self):
        """Test that generated identifier is non-empty."""
        identifier = generate_identifier()
        assert len(identifier) > 0

    def test_generate_identifier_uniqueness(self):
        """Test that generated identifiers are unique."""
        id1 = generate_identifier()
        id2 = generate_identifier()
        assert id1 != id2

    def test_generate_identifier_format(self):
        """Test that generated identifier has valid UUID format."""
        identifier = generate_identifier()
        # UUIDs typically have dashes and hex characters
        # or are 32 hex characters without dashes
        assert all(c in "0123456789abcdef-" for c in identifier.lower())


class TestAccountModel:
    """Test Account model."""

    def test_account_creation(self, test_db_session):
        """Test creating an Account."""
        account = Account(name="Test User", email="test@example.com")

        test_db_session.add(account)
        test_db_session.commit()
        test_db_session.refresh(account)

        assert account.id is not None
        assert account.name == "Test User"
        assert account.email == "test@example.com"

    def test_account_unique_email(self, test_db_session, test_account):
        """Test that account emails are unique."""
        # Try to create duplicate email
        duplicate = Account(name="Another", email=test_account.email)
        test_db_session.add(duplicate)

        with pytest.raises(Exception):  # Should raise integrity error
            test_db_session.commit()

    def test_account_groups_relationship(self, test_db_session, test_account, test_group):
        """Test Account-Group relationship."""
        # Add account to group
        link = PublicationGroupAccountLink(account_id=test_account.id, group_id=test_group.id)
        test_db_session.add(link)
        test_db_session.commit()

        # Verify relationship
        test_db_session.refresh(test_account)
        assert len(test_account.groups) > 0


class TestLoginModel:
    """Test Login model."""

    def test_login_creation(self, test_db_session, test_account):
        """Test creating a Login record."""
        from audihose.security import get_hashed_password

        login = Login(account_id=test_account.id, hashed_password=get_hashed_password("password123"))
        test_db_session.add(login)
        test_db_session.commit()
        test_db_session.refresh(login)

        assert login.id is not None
        assert login.account_id == test_account.id
        assert login.hashed_password is not None

    def test_login_account_relationship(self, test_db_session, test_account):
        """Test Login-Account relationship."""
        from audihose.security import get_hashed_password

        login = Login(account_id=test_account.id, hashed_password=get_hashed_password("password123"))
        test_db_session.add(login)
        test_db_session.commit()
        test_db_session.refresh(login)

        # Verify relationship
        assert login.account is not None
        assert login.account.email == test_account.email


class TestPublicationGroupModel:
    """Test PublicationGroup model."""

    def test_publication_group_creation(self, test_db_session):
        """Test creating a PublicationGroup."""
        group = PublicationGroup(name="Test Group", accepting_submissions=True)
        test_db_session.add(group)
        test_db_session.commit()
        test_db_session.refresh(group)

        assert group.id is not None
        assert group.name == "Test Group"
        assert group.accepting_submissions is True

    def test_publication_group_accounts_relationship(self, test_db_session, test_account, test_group):
        """Test PublicationGroup-Account relationship."""
        link = PublicationGroupAccountLink(account_id=test_account.id, group_id=test_group.id)
        test_db_session.add(link)
        test_db_session.commit()

        test_db_session.refresh(test_group)
        assert len(test_group.accounts) > 0

    def test_publication_group_accepting_submissions_flag(self, test_db_session):
        """Test accepting_submissions flag."""
        group = PublicationGroup(name="Closed Group", accepting_submissions=False)
        test_db_session.add(group)
        test_db_session.commit()
        test_db_session.refresh(group)

        assert group.accepting_submissions is False


class TestRecordingModel:
    """Test Recording model."""

    def test_recording_creation(self, test_db_session, test_account, test_group):
        """Test creating a Recording."""
        recording = Recording(
            subject="Test Podcast",
            email=test_account.email,
            file_path="/tmp/test_recording.wav",
            group_id=test_group.id,
        )
        test_db_session.add(recording)
        test_db_session.commit()
        test_db_session.refresh(recording)

        assert recording.id is not None
        assert recording.subject == "Test Podcast"
        assert recording.email == test_account.email
        assert recording.time is not None

    def test_recording_group_relationship(self, test_db_session, test_account, test_group):
        """Test Recording-Group relationship."""
        recording = Recording(
            subject="Test Podcast",
            email=test_account.email,
            file_path="/tmp/test_recording.wav",
            group_id=test_group.id,
        )
        test_db_session.add(recording)
        test_db_session.commit()
        test_db_session.refresh(recording)

        # Verify relationship
        assert recording.group is not None
        assert recording.group.id == test_group.id

    def test_recording_time_auto_set(self, test_db_session, test_account, test_group):
        """Test that recording time is auto-set."""
        recording = Recording(
            subject="Test Podcast",
            email=test_account.email,
            file_path="/tmp/test_recording.wav",
            group_id=test_group.id,
        )

        before_time = datetime.utcnow()
        test_db_session.add(recording)
        test_db_session.commit()
        test_db_session.refresh(recording)
        after_time = datetime.utcnow()

        # Time should be between before and after
        assert before_time <= recording.time <= after_time


class TestModelConversions:
    """Test model-to-Pydantic response conversions."""

    def test_to_account_summary(self, test_account):
        """Test converting Account to AccountSummary."""
        summary = to_account_summary(test_account)

        assert summary is not None
        assert summary.id == test_account.id
        assert summary.name == test_account.name
        assert summary.email == test_account.email

    def test_to_group_summary(self, test_group):
        """Test converting PublicationGroup to GroupSummary."""
        summary = to_group_summary(test_group)

        assert summary is not None
        assert summary.id == test_group.id
        assert summary.name == test_group.name
        assert summary.accepting_submissions == test_group.accepting_submissions

    def test_to_recording_read(self, test_recording):
        """Test converting Recording to RecordingRead."""
        read = to_recording_read(test_recording)

        assert read is not None
        assert read.id == test_recording.id
        assert read.subject == test_recording.subject
        assert read.email == test_recording.email

    def test_to_account_with_groups(self, test_db_session, test_account, test_group):
        """Test converting Account with eager-loaded groups."""
        # Add account to group
        link = PublicationGroupAccountLink(account_id=test_account.id, group_id=test_group.id)
        test_db_session.add(link)
        test_db_session.commit()
        test_db_session.refresh(test_account)

        result = to_account_with_groups(test_account)

        assert result is not None
        assert result.id == test_account.id
        assert len(result.groups) > 0


class TestDefaultPublicationGroup:
    """Test default publication group creation."""

    def test_ensure_default_publication_group_creates_once(self, test_db_session):
        """Test that ensure_default_publication_group creates group once."""
        # First call
        ensure_default_publication_group(test_db_session)

        # Count groups
        groups1 = test_db_session.query(PublicationGroup).filter_by(
            name="DEFAULT-PUBLICATION-GROUP"
        ).all()
        count1 = len(groups1)

        # Second call
        ensure_default_publication_group(test_db_session)

        # Count again
        groups2 = test_db_session.query(PublicationGroup).filter_by(
            name="DEFAULT-PUBLICATION-GROUP"
        ).all()
        count2 = len(groups2)

        # Should be the same (idempotent)
        assert count1 == count2 == 1

    def test_ensure_default_publication_group_properties(self, test_db_session):
        """Test that default publication group has correct properties."""
        ensure_default_publication_group(test_db_session)

        group = test_db_session.query(PublicationGroup).filter_by(
            name="DEFAULT-PUBLICATION-GROUP"
        ).first()

        assert group is not None
        assert group.name == "DEFAULT-PUBLICATION-GROUP"
        # Default group should accept submissions
        assert group.accepting_submissions in (True, None)


class TestCreateDatabaseTables:
    """Test database table creation."""

    def test_create_database_tables_no_error(self, test_db_session):
        """Test that create_database_tables runs without error."""
        # Tables are already created by test_db_session fixture
        # This test verifies the implicit behavior

        # Tables should exist
        from sqlalchemy import inspect
        inspector = inspect(test_db_session.get_bind())
        table_names = inspector.get_table_names()

        # Should have at least Account, Login, PublicationGroup, Recording tables
        assert len(table_names) > 0

    def test_create_database_tables_creates_all_models(self, test_db_session):
        """Test that all model tables are created."""
        from sqlalchemy import inspect
        inspector = inspect(test_db_session.get_bind())
        table_names = inspector.get_table_names()

        # Verify tables exist (names might vary slightly)
        # Check for lowercase versions
        table_names_lower = [t.lower() for t in table_names]

        assert any("account" in t for t in table_names_lower)
        assert any("login" in t for t in table_names_lower)
        assert any("publicationgroup" in t for t in table_names_lower) or any("publication" in t for t in table_names_lower)
        assert any("recording" in t for t in table_names_lower)
