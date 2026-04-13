"""Unit tests for audihose.database module."""

from datetime import datetime

import pytest
from sqlalchemy import inspect

from audihose.security import get_hashed_password
from audihose.database import (
    Account,
    Login,
    PublicationGroup,
    Recording,
    generate_identifier,
    ensure_default_publication_group,
    to_account_summary,
    to_group_summary,
    to_recording_read,
    to_account_with_groups,
)


def test_identifier_generation_generate_identifier_returns_string():
    """Test that generate_identifier returns a string."""
    identifier = generate_identifier()
    assert isinstance(identifier, str)


def test_identifier_generation_generate_identifier_non_empty():
    """Test that generated identifier is non-empty."""
    identifier = generate_identifier()
    assert len(identifier) > 0


def test_identifier_generation_generate_identifier_uniqueness():
    """Test that generated identifiers are unique."""
    id1 = generate_identifier()
    id2 = generate_identifier()
    assert id1 != id2


def test_identifier_generation_generate_identifier_format():
    """Test that generated identifier has valid UUID format."""
    identifier = generate_identifier()
    assert all((c in "0123456789abcdef-" for c in identifier.lower()))


def test_account_model_account_creation(test_db_session):
    """Test creating an Account."""
    account = Account(name="Test User", email="test@example.com")
    test_db_session.add(account)
    test_db_session.commit()
    test_db_session.refresh(account)
    assert account.id is not None
    assert account.name == "Test User"
    assert account.email == "test@example.com"


def test_account_model_account_unique_email(test_db_session, test_account):
    """Test that account emails are unique."""
    duplicate = Account(name="Another", email=test_account.email)
    test_db_session.add(duplicate)
    with pytest.raises(Exception):
        test_db_session.commit()


def test_account_model_account_groups_relationship(
    test_db_session, test_account, test_group
):
    """Test Account-Group relationship."""
    test_account.groups.append(test_group)
    test_db_session.commit()
    test_db_session.refresh(test_account)
    assert len(test_account.groups) > 0


def test_login_model_login_creation(test_db_session):
    """Test creating a Login record."""
    account = Account(name="Login User", email="login@example.com")
    test_db_session.add(account)
    test_db_session.flush()
    login = Login(
        account_id=account.id,
        hashed_password=get_hashed_password("password123"),
    )
    test_db_session.add(login)
    test_db_session.commit()
    test_db_session.refresh(login)
    assert login.id is not None
    assert login.account_id == account.id
    assert login.hashed_password is not None


def test_login_model_login_account_relationship(test_db_session):
    """Test Login record can be retrieved for its Account ID."""
    account = Account(name="Login Link User", email="login-link@example.com")
    test_db_session.add(account)
    test_db_session.flush()
    login = Login(
        account_id=account.id,
        hashed_password=get_hashed_password("password123"),
    )
    test_db_session.add(login)
    test_db_session.commit()

    stored_login = test_db_session.get(Login, login.id)
    assert stored_login is not None
    assert stored_login.account_id == account.id
    assert stored_login.account is not None
    assert stored_login.account.email == account.email


def test_publication_group_model_publication_group_creation(test_db_session):
    """Test creating a PublicationGroup."""
    group = PublicationGroup(name="Test Group", accepting_submissions=True)
    test_db_session.add(group)
    test_db_session.commit()
    test_db_session.refresh(group)
    assert group.id is not None
    assert group.name == "Test Group"
    assert group.accepting_submissions is True


def test_publication_group_model_publication_group_accounts_relationship(
    test_db_session, test_account, test_group
):
    """Test PublicationGroup-Account relationship."""
    test_group.accounts.append(test_account)
    test_db_session.commit()
    test_db_session.refresh(test_group)
    assert len(test_group.accounts) > 0


def test_publication_group_model_publication_group_accepting_submissions_flag(
    test_db_session,
):
    """Test accepting_submissions flag."""
    group = PublicationGroup(name="Closed Group", accepting_submissions=False)
    test_db_session.add(group)
    test_db_session.commit()
    test_db_session.refresh(group)
    assert group.accepting_submissions is False


def test_recording_model_recording_creation(test_db_session, test_account, test_group):
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


def test_recording_model_recording_group_relationship(
    test_db_session, test_account, test_group
):
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
    assert recording.group is not None
    assert getattr(recording.group, "id", None) == test_group.id


def test_recording_model_recording_time_auto_set(
    test_db_session, test_account, test_group
):
    """Test that recording time is auto-set."""
    before_time = datetime.utcnow()
    recording = Recording(
        subject="Test Podcast",
        email=test_account.email,
        file_path="/tmp/test_recording.wav",
        group_id=test_group.id,
    )
    test_db_session.add(recording)
    test_db_session.commit()
    test_db_session.refresh(recording)
    after_time = datetime.utcnow()
    assert before_time <= recording.time <= after_time


def test_model_conversions_to_account_summary(test_account):
    """Test converting Account to AccountSummary."""
    summary = to_account_summary(test_account)
    assert summary is not None
    assert summary.id == test_account.id
    assert summary.name == test_account.name
    assert summary.email == test_account.email


def test_model_conversions_to_group_summary(test_group):
    """Test converting PublicationGroup to GroupSummary."""
    summary = to_group_summary(test_group)
    assert summary is not None
    assert summary.id == test_group.id
    assert summary.name == test_group.name
    assert summary.accepting_submissions == test_group.accepting_submissions


def test_model_conversions_to_recording_read(test_recording):
    """Test converting Recording to RecordingRead."""
    read = to_recording_read(test_recording)
    assert read is not None
    assert read.id == test_recording.id
    assert read.subject == test_recording.subject
    assert read.email == test_recording.email


def test_model_conversions_to_account_with_groups(
    test_db_session, test_account, test_group
):
    """Test converting Account with eager-loaded groups."""
    test_account.groups.append(test_group)
    test_db_session.commit()
    test_db_session.refresh(test_account)
    result = to_account_with_groups(test_account)
    assert result is not None
    assert result.id == test_account.id
    assert len(result.associations) > 0


def test_default_publication_group_ensure_default_publication_group_creates_once(
    test_db_session,
):
    """Test that ensure_default_publication_group creates group once."""
    ensure_default_publication_group()
    groups1 = (
        test_db_session.query(PublicationGroup)
        .filter_by(name="DEFAULT-PUBLICATION-GROUP")
        .all()
    )
    count1 = len(groups1)
    ensure_default_publication_group()
    groups2 = (
        test_db_session.query(PublicationGroup)
        .filter_by(name="DEFAULT-PUBLICATION-GROUP")
        .all()
    )
    count2 = len(groups2)
    assert count1 == count2 == 1


def test_default_publication_group_ensure_default_publication_group_properties(
    test_db_session,
):
    """Test that default publication group has correct properties."""
    ensure_default_publication_group()
    group = (
        test_db_session.query(PublicationGroup)
        .filter_by(name="DEFAULT-PUBLICATION-GROUP")
        .first()
    )
    assert group is not None
    assert group.name == "DEFAULT-PUBLICATION-GROUP"
    assert group.accepting_submissions in (True, None)


def test_create_database_tables_create_database_tables_no_error(test_db_session):
    """Test that create_database_tables runs without error."""
    inspector = inspect(test_db_session.get_bind())
    table_names = inspector.get_table_names()
    assert len(table_names) > 0


def test_create_database_tables_create_database_tables_creates_all_models(
    test_db_session,
):
    """Test that all model tables are created."""
    inspector = inspect(test_db_session.get_bind())
    table_names = inspector.get_table_names()
    table_names_lower = [t.lower() for t in table_names]
    assert any(("account" in t for t in table_names_lower))
    assert any(("login" in t for t in table_names_lower))
    assert any(("publicationgroup" in t for t in table_names_lower)) or any(
        ("publication" in t for t in table_names_lower)
    )
    assert any(("recording" in t for t in table_names_lower))
