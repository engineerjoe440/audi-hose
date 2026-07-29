################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################
# pylint: disable=no-member

from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import apprise
from jinja2 import Environment, FileSystemLoader

from .configuration import settings

JINJA_ENV = Environment(
    loader=FileSystemLoader(
        str(Path(__file__).parent / "templates")
    ),
    extensions=['jinja_markdown.MarkdownExtension'],
)

_NOTIFICATION_TEMPLATE = "new_recording.html"


def render_markdown(markdown: str, **kwargs) -> str:
    """Use the Markdown Content to Render Variables in Place."""
    return JINJA_ENV.from_string(markdown).render(**kwargs)


def _append_recipient(base_url: str, email: str) -> str:
    """Return a copy of *base_url* with the given email appended as ?to=."""
    parsed = urlparse(base_url)
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    params["to"] = email
    return urlunparse(parsed._replace(query=urlencode(params)))


def _channel_value(channel, key: str, default=None):
    """Read a channel field from either a dict or an attribute-based object."""
    if isinstance(channel, dict):
        return channel.get(key, default)
    return getattr(channel, key, default)


def send_notifications(recording, title: str, accounts=None) -> None:
    """Dispatch notifications for a new recording across all configured channels.

    Each entry in ``settings.notifications`` is an Apprise-URL-based channel
    descriptor with the following fields:

    - ``url``         (str, required) — Apprise-compatible notification URL.
    - ``name``        (str, optional) — Human-readable label for logging.
    - ``attach_audio``(bool, default False) — Attach the source audio file
                      to the notification (honoured only by services that
                      support attachments, e.g. email, Telegram, Discord).
    - ``per_account`` (bool, default False) — When True, one notification is
                      sent per subscribed account by appending ``?to=<email>``
                      to the base URL.  Use this for ``mailto://`` entries
                      where each account should receive an individual email.

    The notification body is rendered from the ``new_recording.html`` Jinja2
    template and delivered as HTML.  Non-email Apprise plugins discard the
    HTML tags automatically.
    """
    channel_configs = getattr(settings, "notifications", []) or []
    if not channel_configs:
        return

    body = JINJA_ENV.get_template(_NOTIFICATION_TEMPLATE).render(
        site_url=settings.application.site_url,
        recording=recording,
        title=title,
    )

    attachment = recording.file_path if getattr(recording, "file_path", None) else None

    for channel in channel_configs:
        url = _channel_value(channel, "url")
        if not url:
            continue
        attach_audio = _channel_value(channel, "attach_audio", False)
        per_account = _channel_value(channel, "per_account", False)
        attach_arg = attachment if (attach_audio and attachment) else None

        if per_account:
            if not accounts:
                continue
            for account in accounts:
                recipient_url = _append_recipient(url, account.email)
                notifier = apprise.Apprise()
                notifier.add(recipient_url)
                notifier.notify(
                    title=title,
                    body=body,
                    body_format=apprise.NotifyFormat.HTML,
                    attach=attach_arg,
                )
        else:
            notifier = apprise.Apprise()
            notifier.add(url)
            notifier.notify(
                title=title,
                body=body,
                body_format=apprise.NotifyFormat.HTML,
                attach=attach_arg,
            )


def ntfy_publish(
    message: str,
    title: str = f"{settings.application.site_url} Alert",
    publish_message: str | None = None,
    priority: str = "default",
    tags: list[str] | None = None,
):
    """Backwards-compatible alert publisher using configured Apprise channels.

    This keeps the historical interface used in exception handlers while
    routing delivery through the unified [[notifications]] configuration.
    The ``priority`` and ``tags`` arguments are accepted for compatibility.
    """
    del priority, tags, publish_message
    channel_configs = getattr(settings, "notifications", []) or []
    for channel in channel_configs:
        if _channel_value(channel, "per_account", False):
            continue
        url = _channel_value(channel, "url")
        if not url:
            continue
        notifier = apprise.Apprise()
        notifier.add(url)
        notifier.notify(
            title=title,
            body=message,
            body_format=apprise.NotifyFormat.TEXT,
        )
