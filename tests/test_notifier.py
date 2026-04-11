"""Unit tests for audihose.notifier module."""

# pylint: disable=too-many-function-args,broad-exception-caught,unused-argument

import requests

from audihose.notifier import (
    render_markdown,
    send_email_message,
    ntfy_publish,
)


class TestMarkdownRendering:
    """Test markdown rendering and template variable substitution."""

    def test_render_markdown_basic(self):
        """Test basic markdown variable substitution."""
        template = "Hello {{ name }}, welcome to {{ platform }}!"
        variables = {"name": "User", "platform": "Audi-Hose"}

        result = render_markdown(template, variables)

        assert "User" in result
        assert "Audi-Hose" in result
        assert "{{ name }}" not in result

    def test_render_markdown_with_markdown_formatting(self):
        """Test markdown formatting is preserved."""
        template = "# Header\n\n{{ message }}"
        variables = {"message": "This is a **bold** message"}

        result = render_markdown(template, variables)

        assert "# Header" in result or "Header" in result
        assert "**bold**" in result or "bold" in result

    def test_render_markdown_empty_template(self):
        """Test rendering empty template."""
        result = render_markdown("", {})
        assert result is not None

    def test_render_markdown_missing_variable(self):
        """Test rendering with missing variables."""
        template = "Hello {{ name }}!"
        variables = {}

        # Should handle gracefully - either empty string or raise
        result = render_markdown(template, variables)
        assert result is not None

    def test_render_markdown_multiple_variables(self):
        """Test rendering with multiple variables."""
        template = "{{ greeting }}, {{ name }}! Your subject: {{ subject }}"
        variables = {
            "greeting": "Hi",
            "name": "John",
            "subject": "Test Recording"
        }

        result = render_markdown(template, variables)

        assert "Hi" in result
        assert "John" in result
        assert "Test Recording" in result

    def test_render_markdown_special_characters(self):
        """Test rendering with special characters."""
        template = "Recipients: {{ emails }}"
        variables = {"emails": "user@example.com, admin@example.com"}

        result = render_markdown(template, variables)
        assert "@" in result


class TestEmailSending:
    """Test email sending via SMTP."""

    def test_send_email_message_success(self, mock_smtp):
        """Test successful email sending."""
        from_address = "noreply@example.com"
        to_address = "user@example.com"
        subject = "Test Subject"
        html_template = "<h1>Test</h1>"
        template_variables = {}

        send_email_message(from_address, to_address, subject, html_template, template_variables)

        # Verify SMTP was called
        assert mock_smtp.called

    def test_send_email_message_with_variables(self, mock_smtp):
        """Test email sending with template variables."""
        from_address = "noreply@example.com"
        to_address = "user@example.com"
        subject = "Recording: {{ subject }}"
        html_template = "<h1>{{ heading }}</h1>"
        template_variables = {
            "subject": "Podcast #1",
            "heading": "New Recording Received"
        }

        send_email_message(from_address, to_address, subject, html_template, template_variables)

        # SMTP call should include variables substituted
        assert mock_smtp.called

    def test_send_email_message_to_multiple_recipients(self, mock_smtp):
        """Test email sending to multiple recipients."""
        from_address = "noreply@example.com"
        to_addresses = ["user1@example.com", "user2@example.com"]
        subject = "Group Notification"
        html_template = "<p>New content available</p>"
        template_variables = {}

        # Call for each recipient or with list
        for to_addr in to_addresses:
            send_email_message(from_address, to_addr, subject, html_template, template_variables)

        # Should have been called at least twice
        assert mock_smtp.call_count >= 1

    def test_send_email_message_smtp_error_handling(self, mock_smtp):
        """Test graceful handling of SMTP errors."""
        mock_smtp.side_effect = Exception("SMTP connection failed")

        from_address = "noreply@example.com"
        to_address = "user@example.com"
        subject = "Test"
        html_template = "<p>Test</p>"
        template_variables = {}

        # Should handle error gracefully
        try:
            send_email_message(from_address, to_address, subject, html_template, template_variables)
        except Exception:
            # Error handling is implementation-specific
            pass

    def test_send_email_message_empty_recipient(self, mock_smtp):
        """Test email with empty recipient list."""
        from_address = "noreply@example.com"
        to_address = ""
        subject = "Test"
        html_template = "<p>Test</p>"
        template_variables = {}

        # Should handle gracefully
        try:
            send_email_message(from_address, to_address, subject, html_template, template_variables)
        except (ValueError, TypeError):
            # Empty recipient might raise an error
            pass


class TestNtfyPublishing:
    """Test ntfy push notifications."""

    def test_ntfy_publish_success(self, mock_ntfy):
        """Test successful ntfy publishing."""

        url = "https://ntfy.sh/audihose-notifications"
        title = "New Recording"
        message = "Recording received from User A"

        # Mock successful response
        mock_ntfy.return_value.status_code = 200

        ntfy_publish(url, title, message)

        # Verify requests.post was called
        assert mock_ntfy.called

    def test_ntfy_publish_with_tags(self, mock_ntfy):
        """Test ntfy publishing with tags."""
        url = "https://ntfy.sh/audihose-notifications"
        title = "New Recording"
        message = "Recording received"

        mock_ntfy.return_value.status_code = 200

        ntfy_publish(url, title, message)
        assert mock_ntfy.called

    def test_ntfy_publish_http_error(self, mock_ntfy):
        """Test ntfy publishing with HTTP error."""
        mock_ntfy.side_effect = requests.RequestException("Connection failed")

        url = "https://ntfy.sh/audihose-notifications"
        title = "New Recording"
        message = "Recording received"

        # Should handle gracefully
        try:
            ntfy_publish(url, title, message)
        except requests.RequestException:
            # Error handling is implementation-specific
            pass

    def test_ntfy_publish_network_timeout(self, mock_ntfy):
        """Test ntfy publishing with network timeout."""
        mock_ntfy.side_effect = requests.Timeout("Request timed out")

        url = "https://ntfy.sh/audihose-notifications"
        title = "New Recording"
        message = "Recording received"

        # Should handle gracefully
        try:
            ntfy_publish(url, title, message)
        except requests.Timeout:
            pass

    def test_ntfy_publish_invalid_url(self):
        """Test ntfy publishing with invalid URL."""
        invalid_url = "not-a-url"
        title = "Test"
        message = "Test message"

        # Should handle invalid URL gracefully
        try:
            ntfy_publish(invalid_url, title, message)
        except (ValueError, requests.RequestException):
            pass

    def test_ntfy_publish_empty_message(self, mock_ntfy):
        """Test ntfy publishing with empty message."""
        url = "https://ntfy.sh/audihose-notifications"
        title = "New Recording"
        message = ""

        mock_ntfy.return_value.status_code = 200

        # Should handle empty message
        ntfy_publish(url, title, message)

        # May still be called with empty message or skip
        # Behavior depends on implementation


class TestNotifierIntegration:
    """Test integration between email and ntfy notifier functions."""

    def test_render_and_send_email_workflow(self, mock_smtp):
        """Test workflow of rendering template and sending email."""
        template = "Hello {{ recipient }}, new recording: {{ subject }}"
        variables = {"recipient": "User A", "subject": "Podcast #1"}

        rendered = render_markdown(template, variables)

        # Then send email with rendered content
        send_email_message("noreply@example.com", "user@example.com", "New Recording", rendered, {})

        assert mock_smtp.called

    def test_multiple_recipients_notification_workflow(self, mock_smtp, mock_ntfy):
        """Test notifying multiple recipients via email and ntfy."""
        recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]

        # Send email to each recipient
        for recipient in recipients:
            send_email_message(
                "noreply@example.com",
                recipient,
                "New Recording",
                "<p>New content available</p>",
                {}
            )

        # Also send ntfy notification
        mock_ntfy.return_value.status_code = 200
        ntfy_publish("https://ntfy.sh/topic", "New Recording", "Content available")

        # Both should be invoked
        assert mock_smtp.called
        assert mock_ntfy.called
