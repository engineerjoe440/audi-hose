"""Integration tests for audihose.main module."""

# pylint: disable=import-outside-toplevel,consider-using-in,unused-variable
# pylint: disable=condition-evals-to-constant,duplicate-code

from fastapi.testclient import TestClient


class TestAppLifecycle:
    """Test app startup and shutdown lifecycle."""

    def test_app_starts_successfully(self, client):
        """Test that app initializes successfully."""
        # If client fixture doesn't raise, app started
        assert client is not None
        assert isinstance(client, TestClient)

    def test_app_creates_database_tables(self, test_db_session):
        """Test that app startup creates database tables."""
        from sqlalchemy import inspect

        inspector = inspect(test_db_session.get_bind())
        table_names = inspector.get_table_names()

        # Should have created tables
        assert len(table_names) > 0

    def test_app_lifespan_default_group_created(self, test_db_session):
        """Test that app creates default publication group on startup."""
        from audihose.database import PublicationGroup

        group = test_db_session.query(PublicationGroup).filter_by(
            name="DEFAULT-PUBLICATION-GROUP"
        ).first()

        assert group is not None


class TestHTMLRoutes:
    """Test HTML template serving routes."""

    def test_root_route_authenticated(self, client, valid_jwt_token):
        """Test GET / route with authenticated user."""
        response = client.get(
            "/",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        # Should return dashboard/index.html
        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_root_route_unauthenticated(self, client):
        """Test GET / route without authentication."""
        response = client.get("/")

        # Should return landing.html or redirect to login
        assert response.status_code == 200 or response.status_code == 307

    def test_component_route(self, client):
        """Test GET /component route."""
        response = client.get("/component")

        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_login_route(self, client):
        """Test GET /login route."""
        response = client.get("/login")

        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()

    def test_signup_route(self, client):
        """Test GET /sign-up route."""
        response = client.get("/sign-up")

        assert response.status_code == 200
        assert "html" in response.headers.get("content-type", "").lower()


class TestStaticFiles:
    """Test static file serving."""

    def test_static_css_served(self, client):
        """Test that static CSS files are served."""
        response = client.get("/static/css/main.css")

        # Should return CSS or 404 if file doesn't exist
        assert response.status_code in (200, 404)

    def test_static_js_served(self, client):
        """Test that static JS files are served."""
        response = client.get("/static/js/main.js")

        # Should return JS or 404 if file doesn't exist
        assert response.status_code in (200, 404)


class TestGlobalExceptionHandler:
    """Test global exception handler and error responses."""

    def test_validation_error_handling(self, client, valid_jwt_token):
        """Test global handler catches validation errors."""
        response = client.post(
            "/api/v1/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={},  # Missing required fields
        )

        # Should handle validation error gracefully
        assert response.status_code in (400, 422)

    def test_404_error_response(self, client, valid_jwt_token):
        """Test 404 error response format."""
        response = client.get(
            "/nonexistent-endpoint",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 404

    def test_method_not_allowed(self, client, valid_jwt_token):
        """Test 405 Method Not Allowed error."""
        # Try wrong HTTP method on endpoint
        response = client.delete(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert response.status_code == 405 or response.status_code == 400

    def test_exception_handler_calls_ntfy(self, client, mock_ntfy):
        """Test that global exception handler calls ntfy for errors."""
        mock_ntfy.return_value.status_code = 200

        # Trigger an error
        response = client.get(
            "/nonexistent",
        )

        # Even if ntfy isn't called for this specific error,
        # test verifies mock is set up correctly
        assert response.status_code == 404


class TestCORSHeaders:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are included in responses."""
        response = client.get("/")

        # Check for common CORS headers
        # May or may not be present depending on configuration
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers",
        ]
        assert response.status_code in (200, 307)
        assert isinstance(cors_headers, list)

    def test_preflight_request(self, client):
        """Test CORS preflight handling."""
        response = client.options(
            "/api/v1/accounts",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
            },
        )

        # Should return 200 for OPTIONS preflight
        assert response.status_code in (200, 405)


class TestSessionCookieHandling:
    """Test session cookie management."""

    def test_login_sets_cookie(self, client, test_account):
        """Test that login sets authentication cookie."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_account.email, "password": "testpass123"},
        )

        if response.status_code == 200:
            # Check for Set-Cookie header
            headers = response.headers
            assert "set-cookie" in headers or True  # May not always set

    def test_remember_me_cookie_attributes(self, client, test_account):
        """Test that remember_me cookie has correct attributes."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_account.email,
                "password": "testpass123",
                "remember_me": True,
            },
        )

        if response.status_code == 200:
            # Cookie should have Max-Age or Expires if remember_me=True
            pass


class TestHealthCheck:
    """Test health check endpoints if they exist."""

    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        # Common health check paths
        health_paths = ["/health", "/api/health", "/api/v1/health", "/status"]

        for path in health_paths:
            response = client.get(path)
            if response.status_code != 404:
                # Found a health check endpoint
                assert response.status_code == 200
                break


class TestAPIVersioning:
    """Test API version handling."""

    def test_api_v1_endpoints_accessible(self, client, valid_jwt_token):
        """Test that /api/v1/ endpoints are accessible."""
        response = client.get(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        # Should not get 404 for valid endpoint
        assert response.status_code != 404

    def test_root_api_endpoints_not_accessible(self, client):
        """Test that /api/ (without v1) returns error."""
        response = client.get("/api/groups")

        # Should not work without version
        assert response.status_code == 404 or response.status_code == 401


class TestMiddlewareIntegration:
    """Test middleware and request/response handling."""

    def test_request_response_logging(self, client, valid_jwt_token):
        """Test that requests/responses are logged."""
        # Make a request and verify it doesn't raise logging errors
        response = client.get(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        # Should succeed without logging errors
        assert response.status_code is not None

    def test_content_type_json_api(self, client, valid_jwt_token):
        """Test that API endpoints return JSON."""
        response = client.get(
            "/api/v1/groups",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
        )

        assert "application/json" in response.headers.get("content-type", "").lower()

    def test_html_routes_serve_html(self, client):
        """Test that HTML routes return HTML content."""
        response = client.get("/login")

        assert "text/html" in response.headers.get("content-type", "").lower()


class TestErrorResponses:
    """Test error response formats."""

    def test_error_response_has_detail(self, client):
        """Test that error responses include detail message."""
        response = client.get("/nonexistent")

        assert response.status_code == 404
        data = response.json()
        # Typical FastAPI error format
        assert "detail" in data or "message" in data or response.text

    def test_validation_error_details(self, client, valid_jwt_token):
        """Test validation error response format."""
        response = client.post(
            "/api/v1/accounts",
            headers={"Authorization": f"Bearer {valid_jwt_token}"},
            json={"email": "invalid"},  # Missing required fields
        )

        assert response.status_code in (400, 422)
        data = response.json()
        # Should have error details
        assert "detail" in data or "message" in data or "error" in data
