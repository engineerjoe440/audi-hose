"""Unit tests for audihose.notifier module."""

from types import SimpleNamespace
from unittest.mock import MagicMock
from audihose.notifier import _append_recipient, render_markdown, send_notifications


def _make_recording(file_path: str = "/tmp/test.wav", subject: str = "Test Subject"):
    """Return a minimal Recording-like object."""
    return SimpleNamespace(file_path=file_path, subject=subject)


def _make_account(email: str):
    """Return a minimal Account-like object."""
    return SimpleNamespace(email=email)


def _channel(url: str, *, per_account: bool = False, attach_audio: bool = False):
    """Return a channel config dict as simple_toml_configurator would provide."""
    return {"url": url, "per_account": per_account, "attach_audio": attach_audio}


def test_markdown_rendering_render_markdown_basic():
    """Test basic variable substitution."""
    template = "Hello {{ name }}, welcome to {{ platform }}!"
    result = render_markdown(template, name="User", platform="Audi-Hose")
    assert "User" in result
    assert "Audi-Hose" in result
    assert "{{ name }}" not in result


def test_markdown_rendering_render_markdown_with_markdown_formatting():
    """Test markdown content is passed through."""
    template = "# Header\n\n{{ message }}"
    result = render_markdown(template, message="This is a **bold** message")
    assert "Header" in result
    assert "bold" in result


def test_markdown_rendering_render_markdown_empty_template():
    """Rendering an empty template returns a non-None value."""
    result = render_markdown("")
    assert result is not None


def test_markdown_rendering_render_markdown_missing_variable():
    """Missing template variables are handled gracefully (Jinja2 default: empty string)."""
    template = "Hello {{ name }}!"
    result = render_markdown(template)
    assert result is not None


def test_markdown_rendering_render_markdown_multiple_variables():
    """Multiple keyword variables are all substituted."""
    template = "{{ greeting }}, {{ name }}! Subject: {{ subject }}"
    result = render_markdown(
        template, greeting="Hi", name="John", subject="Test Recording"
    )
    assert "Hi" in result
    assert "John" in result
    assert "Test Recording" in result


def test_markdown_rendering_render_markdown_special_characters():
    """Special characters (e.g. @) survive rendering."""
    template = "Recipients: {{ emails }}"
    result = render_markdown(template, emails="user@example.com")
    assert "@" in result


def test_append_recipient_appends_to_param():
    """Recipient email is appended to the URL query string."""
    url = "mailtos://user:pass@smtp.example.com?from=noreply@example.com"
    result = _append_recipient(url, "person@example.com")
    assert "to=person%40example.com" in result or "to=person@example.com" in result


def test_append_recipient_overwrites_existing_to_param():
    """An existing to= query value is replaced."""
    url = "mailtos://user:pass@smtp.example.com?to=old@example.com"
    result = _append_recipient(url, "new@example.com")
    assert "new" in result
    assert "old" not in result


def test_append_recipient_preserves_other_params():
    """Unrelated URL query parameters are preserved."""
    url = "mailtos://user:pass@smtp.example.com?from=noreply@example.com"
    result = _append_recipient(url, "person@example.com")
    assert "from" in result


def test_apprise_notifications_empty_notifications_list_is_noop(mocker):
    """No Apprise instance should be created when the notifications list is empty."""
    mock_apprise = mocker.patch("audihose.notifier.apprise.Apprise")
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    mocker.patch("audihose.notifier.JINJA_ENV")
    recording = _make_recording()
    send_notifications(recording, "New Recording!")
    mock_apprise.assert_not_called()


def test_apprise_notifications_system_level_channel_notified_once(mocker):
    """A channel without per_account=True triggers a single notify call."""
    mock_instance = MagicMock()
    mock_apprise_cls = mocker.patch(
        "audihose.notifier.apprise.Apprise", return_value=mock_instance
    )
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[_channel("slack://TokenA/TokenB/TokenC/channel")],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    recording = _make_recording()
    send_notifications(recording, "New Recording!")
    mock_apprise_cls.assert_called_once()
    mock_instance.notify.assert_called_once()


def test_apprise_notifications_per_account_channel_notified_once_per_account(mocker):
    """A per_account=True entry triggers one notify call per account."""
    instances = []

    def make_instance():
        inst = MagicMock()
        instances.append(inst)
        return inst

    mocker.patch("audihose.notifier.apprise.Apprise", side_effect=make_instance)
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[
            _channel(
                "mailtos://user:pass@smtp.example.com?from=noreply@example.com",
                per_account=True,
            )
        ],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    accounts = [_make_account("a@example.com"), _make_account("b@example.com")]
    recording = _make_recording()
    send_notifications(recording, "New Recording!", accounts=accounts)
    assert len(instances) == 2
    for inst in instances:
        inst.notify.assert_called_once()


def test_apprise_notifications_per_account_without_accounts_is_noop(mocker):
    """A per_account=True entry with no accounts provided sends nothing."""
    mock_instance = MagicMock()
    mock_apprise_cls = mocker.patch(
        "audihose.notifier.apprise.Apprise", return_value=mock_instance
    )
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[
            _channel("mailtos://user:pass@smtp.example.com", per_account=True)
        ],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    recording = _make_recording()
    send_notifications(recording, "New Recording!", accounts=None)
    mock_apprise_cls.assert_not_called()


def test_apprise_notifications_attach_audio_true_passes_attach_arg(mocker):
    """When attach_audio=True, the recording file path is passed to notify()."""
    mock_instance = MagicMock()
    mocker.patch("audihose.notifier.apprise.Apprise", return_value=mock_instance)
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[
            _channel("slack://TokenA/TokenB/TokenC/channel", attach_audio=True)
        ],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    recording = _make_recording(file_path="/srv/recordings/abc.wav")
    send_notifications(recording, "New Recording!")
    call_kwargs = mock_instance.notify.call_args.kwargs
    assert call_kwargs.get("attach") == "/srv/recordings/abc.wav"


def test_apprise_notifications_attach_audio_false_omits_attach_arg(mocker):
    """When attach_audio=False, attach is None (not sent)."""
    mock_instance = MagicMock()
    mocker.patch("audihose.notifier.apprise.Apprise", return_value=mock_instance)
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[
            _channel("slack://TokenA/TokenB/TokenC/channel", attach_audio=False)
        ],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    recording = _make_recording()
    send_notifications(recording, "New Recording!")
    call_kwargs = mock_instance.notify.call_args.kwargs
    assert call_kwargs.get("attach") is None


def test_apprise_notifications_multiple_channels_all_notified(mocker):
    """Multiple channel entries each produce their own Apprise call."""
    instances = []

    def make_instance():
        inst = MagicMock()
        instances.append(inst)
        return inst

    mocker.patch("audihose.notifier.apprise.Apprise", side_effect=make_instance)
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[
            _channel("slack://TokenA/TokenB/TokenC/channel"),
            _channel("ntfys://my-topic/"),
        ],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    recording = _make_recording()
    send_notifications(recording, "New Recording!")
    assert len(instances) == 2
    for inst in instances:
        inst.notify.assert_called_once()


def test_apprise_notifications_channel_missing_url_is_skipped(mocker):
    """A channel dict without a 'url' key is silently skipped."""
    mock_apprise_cls = mocker.patch("audihose.notifier.apprise.Apprise")
    mock_jinja = MagicMock()
    mock_jinja.get_template.return_value.render.return_value = "<p>body</p>"
    mocker.patch("audihose.notifier.JINJA_ENV", mock_jinja)
    mocker.patch(
        "audihose.notifier.settings",
        notifications=[{"name": "broken channel"}],
        application=SimpleNamespace(site_url="http://example.com"),
    )
    recording = _make_recording()
    send_notifications(recording, "New Recording!")
    mock_apprise_cls.assert_not_called()
