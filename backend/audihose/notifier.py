################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .configuration import settings

JINJA_ENV = Environment(
    loader=FileSystemLoader(
        str(Path(__file__).parent / "templates")
    ),
    extensions=['jinja_markdown.MarkdownExtension'],
)

def render_markdown(markdown: str, **kwargs) -> str:
    """Use the Markdown Content to Render Variables in Place."""
    return JINJA_ENV.from_string(markdown).render(**kwargs)

def send_email_message(
    subject: str,
    template: str,
    to_address: str,
    cc_addresses: list[str] | None = None,
    **kwargs,
):
    """Send an HTML Email Message."""
    if not template.endswith(".html"):
        template += ".html"
    email_body = JINJA_ENV.get_template(template).render(
        site_url=settings.application.site_url,
        **kwargs,
    )
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = settings.smtp.from_email
    message['To'] = to_address
    recipients = [to_address]
    if cc_addresses:
        message['Cc'] = ",".join(cc_addresses)
        recipients.extend(cc_addresses)

    message.attach(MIMEText(email_body, "html"))

    smtp_connection = SMTP(
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
        from_addr=settings.smtp.from_email,
        to_addrs=recipients,
        msg=message.as_string(),
    )

    smtp_connection.quit()
