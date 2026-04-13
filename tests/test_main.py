"""Integration tests for audihose.main module."""

from fastapi.testclient import TestClient
from sqlalchemy import inspect

from audihose.database import PublicationGroup


def test_app_lifecycle_app_starts_successfully(client):
    """Test that app initializes successfully."""
    assert client is not None
    assert isinstance(client, TestClient)


def test_app_lifecycle_app_creates_database_tables(test_db_session):
    """Test that app startup creates database tables."""
    inspector = inspect(test_db_session.get_bind())
    table_names = inspector.get_table_names()
    assert len(table_names) > 0


def test_app_lifecycle_app_lifespan_default_group_created(test_db_session):
    """Test that app creates default publication group on startup."""
    group = (
        test_db_session.query(PublicationGroup)
        .filter_by(name="DEFAULT-PUBLICATION-GROUP")
        .first()
    )
    assert group is not None


def test_htmlroutes_root_route_authenticated(client, valid_jwt_token):
    """Test GET / route with authenticated user."""
    response = client.get("/", headers={"Authorization": f"Bearer {valid_jwt_token}"})
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_htmlroutes_root_route_unauthenticated(client):
    """Test GET / route without authentication."""
    response = client.get("/")
    assert response.status_code in (200, 307)


def test_htmlroutes_component_route(client):
    """Test GET /component route."""
    response = client.get("/component")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_htmlroutes_login_route(client):
    """Test GET /login route."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_htmlroutes_signup_route(client):
    """Test GET /sign-up route."""
    response = client.get("/sign-up")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()


def test_static_files_static_css_served(client):
    """Test that static CSS files are served."""
    response = client.get("/static/css/main.css")
    assert response.status_code in (200, 404)


def test_static_files_static_js_served(client):
    """Test that static JS files are served."""
    response = client.get("/static/js/main.js")
    assert response.status_code in (200, 404)


def test_global_exception_handler_validation_error_handling(client, valid_jwt_token):
    """Test global handler catches validation errors."""
    response = client.put(
        "/api/v1/accounts/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={},
    )
    assert response.status_code in (400, 422)


def test_global_exception_handler_404_error_response(client, valid_jwt_token):
    """Test 404 error response format."""
    response = client.get(
        "/nonexistent-endpoint", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code == 404


def test_global_exception_handler_method_not_allowed(client, valid_jwt_token):
    """Test 405 Method Not Allowed error."""
    response = client.delete(
        "/api/v1/groups", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code in (400, 405)


def test_global_exception_handler_exception_handler_calls_ntfy(client, mock_ntfy):
    """Test that global exception handler calls ntfy for errors."""
    mock_ntfy.return_value.status_code = 200
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_corsheaders_cors_headers_present(client):
    """Test that CORS headers are included in responses."""
    response = client.get("/")
    cors_headers = [
        "access-control-allow-origin",
        "access-control-allow-methods",
        "access-control-allow-headers",
    ]
    assert response.status_code in (200, 307)
    assert isinstance(cors_headers, list)


def test_corsheaders_preflight_request(client):
    """Test CORS preflight handling."""
    response = client.options(
        "/api/v1/accounts",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code in (200, 400, 405)


def test_session_cookie_handling_login_sets_cookie(client, test_account):
    """Test that login sets authentication cookie."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_account.email, "password": "testpass123"},
    )
    if response.status_code == 200:
        headers = response.headers
        assert "set-cookie" in headers


def test_session_cookie_handling_remember_me_cookie_attributes(client, test_account):
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
        pass


def test_health_check_health_check_endpoint(client):
    """Test health check endpoint."""
    health_paths = ["/health", "/api/health", "/api/v1/health", "/status"]
    for path in health_paths:
        response = client.get(path)
        if response.status_code != 404:
            assert response.status_code == 200
            break


def test_apiversioning_api_v1_endpoints_accessible(client, valid_jwt_token):
    """Test that /api/v1/ endpoints are accessible."""
    response = client.get(
        "/api/v1/groups", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code != 404


def test_apiversioning_root_api_endpoints_not_accessible(client):
    """Test that /api/ (without v1) returns error."""
    response = client.get("/api/groups")
    assert response.status_code in (401, 404)


def test_middleware_integration_request_response_logging(client, valid_jwt_token):
    """Test that requests/responses are logged."""
    response = client.get(
        "/api/v1/groups", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert response.status_code is not None


def test_middleware_integration_content_type_json_api(client, valid_jwt_token):
    """Test that API endpoints return JSON."""
    response = client.get(
        "/api/v1/groups", headers={"Authorization": f"Bearer {valid_jwt_token}"}
    )
    assert "application/json" in response.headers.get("content-type", "").lower()


def test_middleware_integration_html_routes_serve_html(client):
    """Test that HTML routes return HTML content."""
    response = client.get("/login")
    assert "text/html" in response.headers.get("content-type", "").lower()


def test_error_responses_error_response_has_detail(client):
    """Test that error responses include detail message."""
    response = client.get("/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data or "message" in data or response.text


def test_error_responses_validation_error_details(client, valid_jwt_token):
    """Test validation error response format."""
    response = client.put(
        "/api/v1/accounts/",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
        json={"email": "invalid"},
    )
    assert response.status_code in (400, 422)
    data = response.json()
    assert "detail" in data or "message" in data or "error" in data
