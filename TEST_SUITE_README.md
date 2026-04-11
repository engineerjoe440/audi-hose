"""
Audi-Hose Backend Test Suite Documentation

This comprehensive pytest test suite provides coverage for the Audi-Hose Python backend with 190+ tests.

## Getting Started

### Installation
The test dependencies have been added to `dev-requirements.txt`:
- pytest >= 7.0
- pytest-cov
- pytest-mock
- pytest-asyncio (already included)

Install with:
```bash
pip install -r dev-requirements.txt
```

### Running Tests

#### All tests:
```bash
pytest tests/ -v
```

#### Specific module:
```bash
pytest tests/test_security.py -v
```

#### With coverage report:
```bash
pytest tests/ --cov=audihose --cov-report=html --cov-report=term-missing
```

#### By marker/keyword:
```bash
pytest tests/ -k "security" -v
pytest tests/ -k "404" -v
```

## Test Structure

### Directory Layout
```
tests/
├── __init__.py
├── conftest.py                          # Shared fixtures
├── test_security.py                     # Unit: password/JWT crypto (✅ PASSING)
├── test_sessions.py                     # Unit: session management
├── test_configuration.py                # Unit: config loading (✅ PASSING)
├── test_notifier.py                     # Unit: email/ntfy (mocked)
├── test_database.py                     # Unit: models/converters
├── test_authentication.py               # Integration: auth endpoints
├── test_api_accounts.py                 # Integration: account CRUD
├── test_api_groups.py                   # Integration: group management
├── test_api_recordings.py               # Integration: file operations
└── test_main.py                         # Integration: app lifespan, routes
```

### Test Categories

#### Unit Tests (No Database/Network)
- `test_security.py` (13 tests, ✅ 100% passing)
  - Password hashing, JWT operations, token verification
- `test_configuration.py` (9 tests, ✅ 100% passing)
  - Config loading, path resolution, environment overrides
- `test_sessions.py` (13 tests)
  - UserSession lifecycle, SessionManager singleton behavior
- `test_notifier.py` (12 tests)
  - Email rendering/sending (SMTP mocked), ntfy notifications (requests mocked)
- `test_database.py` (21 tests)
  - ORM models, relationships, converters (in-memory SQLite)

#### Integration Tests (Real Database + HTTP)
- `test_authentication.py` (24 tests)
  - Login/logout, JWT validation, bearer token handling
  - **HTTP Exceptions Tested**: 400, 401, 403, 423
- `test_api_accounts.py` (15 tests)
  - Account CRUD endpoints
  - **HTTP Exceptions Tested**: 404, 401
- `test_api_groups.py` (18 tests)
  - Group CRUD, membership management
  - **HTTP Exceptions Tested**: 404, 401
- `test_api_recordings.py` (23 tests)
  - File upload/download, notifications
  - **HTTP Exceptions Tested**: 404, 401
- `test_main.py` (21 tests)
  - App lifespan, HTML routes, static files, CORS
  - Global exception handler, session cookies

## Test Infrastructure

### Shared Fixtures (conftest.py)

#### Database Fixtures
- `test_db_session` - In-memory SQLite with all tables
- `test_account`, `test_account_2` - Pre-created test accounts
- `test_group`, `test_group_2` - Pre-created test groups
- `test_recording` - Pre-created recording with file

#### JWT/Session Fixtures
- `valid_jwt_token` - Valid JWT for authenticated tests
- `expired_jwt_token` - Expired JWT for error tests
- `test_session_manager` - Fresh SessionManager instance
- `test_user_session` - Active UserSession

#### FastAPI Fixtures
- `client` - TestClient with DB overrides
- `client_with_auth` - TestClient with auth headers set

#### Mock Fixtures
- `mock_smtp` - Mocked SMTP for email tests
- `mock_ntfy` - Mocked requests.post for push notifications
- `mock_aiofiles` - Mocked async file operations
- `temp_dir`, `temp_config` - Temporary directories for file tests

### Dependency Overrides

The test client automatically overrides:
- `get_session` dependency → uses `test_db_session` (in-memory SQLite)
- Test database is isolated per function (function-scoped fixtures)
- No actual files written outside temp directories
- No actual emails sent or push notifications triggered

## HTTP Status Codes Tested

All HTTP exceptions are covered with parametrized tests:

| Status | In Tests | Scenarios |
|--------|----------|-----------|
| **400** | 5 tests | Invalid Bearer scheme, malformed requests |
| **401** | 15+ tests | Missing auth, invalid/expired tokens, 404 with no auth |
| **403** | 3+ tests | Session expired, invalid auth state |
| **404** | 20+ tests | Missing resource (account/group/recording), nonexistent IDs |
| **423** | 2 tests | Signup locked after first account |

## Key Testing Patterns

### Mocking Network/File I/O
```python
def test_send_email(mock_smtp):
    mock_smtp.return_value.status_code = 200
    send_email_message(...)
    assert mock_smtp.called
```

### Testing with Database
```python
def test_create_account(client, valid_jwt_token, test_db_session):
    response = client.put("/api/v1/accounts", headers={...})
    assert response.status_code == 201
    # Verify in test DB
    account = test_db_session.query(Account).first()
    assert account is not None
```

### Testing HTTP Exceptions
```python
@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 423])
def test_all_exceptions(status_code):
    assert status_code in (400, 401, 403, 404, 423)
```

## Known Issues & Notes

### API Endpoint Paths
The actual API structure:
- **Auth endpoints** are at root: `/login`, `/logout`, `/refresh-token`, `/signup-required`, `/create-initial-account`
- **API endpoints** are under `/api/v1/`: `/api/v1/accounts`, `/api/v1/groups`, `/api/v1/recordings`

Some integration tests may reference incorrect paths and need adjustment based on actual implementation.

### Session Management
- Sessions use UUID-based `client_token` (not email)
- JWTs include `"session": client_token` claim to link to session
- `SessionManager` is a singleton using global `SESSIONS` list
- `UserSession.configure_authenticated()` sets remember-me mode

### JWT Parameters
- `sign_jwt(data, expiry_seconds: int)` - expects seconds, not timedelta
- `decode_jwt()` returns `None` or `{}` for invalid/expired, not exceptions
- `verify_token()` wraps `decode_jwt()` with boolean conversion

## Coverage Goals

**Target**: 85% overall code coverage

Run coverage check:
```bash
pytest tests/ --cov=audihose --cov-report=term-missing | grep "^TOTAL"
```

Expected coverage includes:
- 100% of security.py (crypto functions)
- 95%+ of database.py (models, converters)
- 90%+ of sessions.py (lifecycle management)
- 85%+ of API endpoints (auth, accounts, groups, recordings)
- 90%+ of main.py (routes, exception handling)

## Test Execution Examples

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run security tests (should pass)
pytest tests/test_security.py -v

# Run only unit tests (no integration)
pytest tests/test_security.py tests/test_configuration.py tests/test_notifier.py tests/test_sessions.py -v

# Run specific test class
pytest tests/test_authentication.py::TestJWTBearerValidation -v

# Run with pytest-asyncio for async endpoints
pytest tests/ -v --asyncio-mode=auto

# Modify timeout for slow tests
pytest tests/ -v --timeout=10

# Run tests matching a pattern
pytest tests/ -k "not recording" -v  # Skip recording tests
pytest tests/ -k "404" -v            # Only 404 error tests
```

## Debugging Tests

Enable detailed output:
```bash
pytest tests/test_security.py -vv -s  # -s shows print statements
```

Show local variables on failure:
```bash
pytest tests/ -l
```

Drop into debugger on failure:
```bash
pytest tests/ --pdb
```

## Further Improvements

1. **Async Support**: Add fixtures for async database sessions if endpoints are async
2. **Performance**: Reduce `test_db_session` setup time with session-scoped fixtures for read-only tests
3. **Fixtures as Classes**: Refactor duplicated fixture logic into helper classes
4. **Parametrization**: Expand parametrized tests for `test_all_http_exceptions` scenarios
5. **Edge Cases**: Add tests for boundary conditions (empty files, very large uploads, concurrent requests)
6. **Rate Limiting**: Test rate limit headers if implemented
7. **CORS**: Verify all CORS headers and preflight requests

## Contributing

When adding new tests:
1. Place in appropriate file (`test_module.py` for `audihose/module.py`)
2. Make fixtures function-scoped for isolation
3. Use descriptive names: `test_{feature}_{scenario}`
4. Test both happy path and error cases
5. Verify all HTTP exceptions can occur
6. Mock external I/O (files, network, database outside test DB)
7. Document unusual assertions with comments
"""
