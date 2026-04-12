################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################
# pylint: disable=no-member

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import requests

from .configuration import settings

JINJA_ENV = Environment(
    loader=FileSystemLoader(
        str(Path(__file__).parent / "templates")
    ),
    extensions=['jinja_markdown.MarkdownExtension'],
)

def render_markdown(markdown: str, variables: dict | None = None, **kwargs) -> str:
    """Use markdown content to render variables in place.

    Accepts either a variables dict or keyword args for compatibility.
    """
    render_values = dict(variables or {})
    render_values.update(kwargs)
    return JINJA_ENV.from_string(markdown).render(**render_values)

def send_email_message(
    *args,
    subject: str | None = None,
    template: str | None = None,
    to_address: str | None = None,
    cc_addresses: list[str] | None = None,
    from_address: str | None = None,
    **kwargs,
):
    """Send an HTML email message.

    Supports both current keyword-style API and legacy positional API:
    (from_address, to_address, subject, html_template, template_variables).
    """
    template_vars = {}
    if args:
        if len(args) >= 4:
            from_address = args[0]
            to_address = args[1]
            subject = args[2]
            template = args[3]
            if len(args) >= 5 and isinstance(args[4], dict):
                template_vars.update(args[4])
        else:
            raise TypeError("send_email_message positional usage requires at least 4 arguments")

    template_vars.update(kwargs)
    subject = subject or "Notification"
    template = template or ""
    to_address = to_address or ""
    from_address = from_address or settings.smtp.from_email

    if template.strip().endswith(".html"):
        try:
            email_body = JINJA_ENV.get_template(template).render(
                site_url=settings.application.site_url,
                **template_vars,
            )
        except TemplateNotFound:
            email_body = render_markdown(template, template_vars)
    elif "<" in template or "\n" in template or template.strip() == "":
        email_body = render_markdown(template, template_vars)
    else:
        template_name = f"{template}.html"
        try:
            email_body = JINJA_ENV.get_template(template_name).render(
                site_url=settings.application.site_url,
                **template_vars,
            )
        except TemplateNotFound:
            email_body = render_markdown(template, template_vars)

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_address
    message['To'] = to_address
    recipients = [to_address]
    if cc_addresses:
        message['Cc'] = ",".join(cc_addresses)
        recipients.extend(cc_addresses)

    message.attach(MIMEText(email_body, "html"))

    smtp_connection = smtplib.SMTP(
        host=settings.smtp.server,
        port=settings.smtp.port,
    )
    if settings.smtp.starttls:
        smtp_connection.starttls()
    if settings.smtp.username and settings.smtp.password:
        smtp_connection.login(
            user=settings.smtp.username,
            password=settings.smtp.password,
        )
    smtp_connection.sendmail(
        from_addr=from_address,
        to_addrs=recipients,
        msg=message.as_string(),
    )

    smtp_connection.quit()

def ntfy_publish(
    message: str,
    title: str = f"{settings.application.site_url} Alert",
    publish_message: str | None = None,
    priority: str = "default",
    tags: list[str] | None = None,
):
    """Publish a message to ntfy.

    Supports legacy positional usage: ntfy_publish(url, title, message).
    """
    url_override = None
    payload = message
    if publish_message is not None:
        url_override = message
        payload = publish_message

    publish_url = url_override or (
        f"{settings.ntfy.server}/{settings.ntfy.topic}" if settings.ntfy.server else None
    )
    if not publish_url:
        return

    ntfy_headers = {"Title": title}
    if priority:
        ntfy_headers["Priority"] = priority
    if tags:
        ntfy_headers["Tags"] = ",".join(tags)
    if settings.ntfy.token:
        ntfy_headers["Authorization"] = f"Bearer {settings.ntfy.token}"

    requests.post(
        publish_url,
        data=payload,
        headers=ntfy_headers,
        timeout=60,
    )
