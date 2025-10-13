# Lodgeick Test Suite

Comprehensive test suite for the Lodgeick integration platform covering unit tests, integration tests, and end-to-end scenarios.

## Test Structure

```
lodgeick/tests/
├── __init__.py
├── fixtures/
│   └── test_data.py          # Mock data and test fixtures
├── unit/
│   ├── test_oauth.py         # OAuth authentication tests
│   ├── test_integrations.py  # Integration management tests
│   ├── test_catalog.py       # App catalog tests
│   └── test_google_ai_setup.py # AI-powered setup tests
└── integration/
    ├── test_oauth_flow.py    # End-to-end OAuth flow tests
    └── test_n8n_webhooks.py  # n8n workflow integration tests
```

## Running Tests

### Run All Tests

```bash
# From Frappe bench directory
cd /workspace/development/frappe-bench

# Run all Lodgeick tests
bench --site home.localhost run-tests --app lodgeick

# Run tests in Docker container
docker exec frappe_docker_devcontainer-frappe-1 bash -c \
  "cd /workspace/development/frappe-bench && bench --site home.localhost run-tests --app lodgeick"
```

### Run Specific Test Modules

```bash
# Run only unit tests
bench --site home.localhost run-tests --app lodgeick --module lodgeick.tests.unit

# Run specific test file
bench --site home.localhost run-tests --app lodgeick --module lodgeick.tests.unit.test_oauth

# Run specific test class
bench --site home.localhost run-tests --app lodgeick --module lodgeick.tests.unit.test_oauth.TestInitiateOAuth
```

### Run Tests with Coverage

```bash
# Install coverage
bench --site home.localhost pip install coverage

# Run tests with coverage report
coverage run --source=lodgeick -m unittest discover -s lodgeick/tests
coverage report
coverage html  # Generate HTML report
```

### Run Tests in Parallel

```bash
# Install pytest for parallel execution
bench --site home.localhost pip install pytest pytest-xdist

# Run tests in parallel
pytest lodgeick/tests -n auto
```

## Test Categories

### Unit Tests (`unit/`)

Test individual functions and modules in isolation using mocks.

#### test_oauth.py (398 lines)
- `TestInitiateOAuth` - OAuth flow initiation
- `TestOAuthCallback` - OAuth callback handling
- `TestGetProviderConfig` - Provider configuration retrieval
- `TestSaveOAuthCredentials` - Credential storage
- `TestBuildAuthUrl` - Authorization URL generation
- `TestExchangeCodeForTokens` - Token exchange
- `TestCalculateExpiry` - Token expiry calculation
- `TestSaveUserOAuthSetup` - OAuth tier selection
- `TestRefreshToken` - Token refresh logic

**Coverage:** 9 test classes, 25+ test cases

#### test_integrations.py (459 lines)
- `TestActivateIntegration` - Integration activation
- `TestGetIntegrationStatus` - Status retrieval
- `TestListUserIntegrations` - User integration listing
- `TestPauseIntegration` - Integration pausing
- `TestDeleteIntegration` - Integration deletion
- `TestGetUserToken` - Token retrieval helper
- `TestGetWorkflowTemplate` - Template lookup
- `TestCreateN8nWorkflow` - Workflow creation
- `TestN8nWebhookCallback` - Webhook handling

**Coverage:** 9 test classes, 20+ test cases

#### test_catalog.py (357 lines)
- `TestGetAppCatalog` - Catalog retrieval
- `TestGetAppDetails` - App details
- `TestGetCategories` - Category listing
- `TestSearchApps` - App search
- `TestCatalogFiltering` - Edge cases

**Coverage:** 5 test classes, 18+ test cases

#### test_google_ai_setup.py (439 lines)
- `TestParseIntent` - AI intent parsing
- `TestCreateProject` - Google Cloud project creation
- `TestSetupOAuthCredentials` - OAuth setup
- `TestGetSetupStatus` - Setup status
- `TestListUserProjects` - Project listing
- `TestStoreUserProject` - Project storage
- `TestSyncCredentialsToN8n` - n8n credential sync

**Coverage:** 7 test classes, 20+ test cases

### Integration Tests (`integration/`)

Test multiple components working together.

#### test_oauth_flow.py (284 lines)
- `TestOAuthFlowIntegration` - Complete OAuth flow
- `TestMultiProviderOAuthFlow` - Multi-provider scenarios
- `TestOAuthFlowWithIntegrationSettings` - Settings creation
- `TestOAuthFlowErrorRecovery` - Error handling and retry

**Coverage:** 4 test classes, 10+ test cases

#### test_n8n_webhooks.py (302 lines)
- `TestN8nWebhookIntegration` - Webhook callbacks
- `TestIntegrationWithN8nWorkflow` - Workflow integration
- `TestN8nWebhookRetry` - Retry logic
- `TestN8nWebhookSecurity` - Security validation
- `TestN8nWorkflowLifecycle` - Full lifecycle tests

**Coverage:** 5 test classes, 12+ test cases

## Test Fixtures

### Mock Data (`fixtures/test_data.py`)

Provides consistent test data across all tests:

- `MOCK_PROVIDER_CONFIGS` - OAuth provider configurations
- `MOCK_OAUTH_TOKENS` - OAuth token responses
- `MOCK_APP_CATALOG` - App catalog data
- `MOCK_USE_CASES` - Integration use cases
- `MOCK_USER_INTEGRATION` - User integration data
- `MOCK_AI_INTENT_RESPONSE` - AI parser responses
- `MOCK_GOOGLE_PROJECT` - Google Cloud project data
- `MOCK_N8N_WORKFLOW` - n8n workflow data
- `MOCK_INTEGRATION_LOG` - Integration log entries

## Test Coverage

### Current Coverage (Phase 3A)

| Module | Unit Tests | Integration Tests | Total Coverage |
|--------|-----------|-------------------|----------------|
| `api/oauth.py` | ✅ 25 tests | ✅ 10 tests | **~90%** |
| `api/integrations.py` | ✅ 20 tests | ✅ 12 tests | **~85%** |
| `api/catalog.py` | ✅ 18 tests | N/A | **~95%** |
| `api/google_ai_setup.py` | ✅ 20 tests | N/A | **~80%** |

**Total:** 105+ test cases covering core backend functionality

### Uncovered Areas (Future Work)

- `services/ai_parser.py` - AI service integration
- `services/google_cloud.py` - Google Cloud API client
- `services/n8n_client.py` - n8n API client
- `services/n8n_sync.py` - n8n synchronization
- Frontend component tests (Vue 3)
- DocType validation tests

## Writing New Tests

### Unit Test Template

```python
"""
Unit tests for new_module
"""

import unittest
from unittest.mock import Mock, patch
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.new_module import function_to_test
from lodgeick.tests.fixtures.test_data import MOCK_DATA


class TestNewFunction(FrappeTestCase):
    """Test new_function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('lodgeick.api.new_module.dependency')
    def test_function_success(self, mock_dependency):
        """Test successful execution"""
        mock_dependency.return_value = MOCK_DATA

        result = function_to_test(arg1="value")

        self.assertTrue(result['success'])
        self.assertIn('expected_key', result)
```

### Integration Test Template

```python
"""
Integration tests for new_feature
"""

from frappe.tests.utils import FrappeTestCase
from lodgeick.api.module1 import function1
from lodgeick.api.module2 import function2


class TestFeatureIntegration(FrappeTestCase):
    """Test complete feature workflow"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    def test_complete_workflow(self):
        """Test end-to-end feature workflow"""
        # Step 1: Initialize
        result1 = function1()
        self.assertTrue(result1['success'])

        # Step 2: Process
        result2 = function2(result1['data'])
        self.assertTrue(result2['success'])

        # Verify final state
        self.assertIsNotNone(result2['output'])
```

## Testing Best Practices

### 1. Isolation
- Each test should be independent
- Use `setUp()` and `tearDown()` for clean state
- Always rollback database changes in `tearDown()`

### 2. Mocking
- Mock external dependencies (n8n, Google Cloud, OAuth providers)
- Use `@patch` decorator for function/method mocking
- Use fixtures for consistent test data

### 3. Assertions
- Use descriptive assertion messages
- Test both success and failure paths
- Verify side effects (database changes, logs, etc.)

### 4. Test Naming
- Use descriptive test names: `test_function_scenario`
- Group related tests in classes
- Document test purpose in docstrings

### 5. Coverage
- Aim for >80% code coverage
- Test edge cases and error conditions
- Don't test Frappe framework internals

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: |
          docker-compose exec frappe \
            bench --site home.localhost run-tests --app lodgeick
```

## Debugging Tests

### Enable Verbose Output

```bash
# Run with verbose output
bench --site home.localhost run-tests --app lodgeick --verbose

# Run with pdb debugger
bench --site home.localhost run-tests --app lodgeick --pdb-on-failure
```

### Check Test Logs

```bash
# View Frappe logs
tail -f sites/home.localhost/logs/frappe.log

# View test-specific logs
grep "test_oauth" sites/home.localhost/logs/frappe.log
```

## Performance Testing

### Benchmark Tests

```bash
# Install pytest-benchmark
bench --site home.localhost pip install pytest-benchmark

# Run with benchmarking
pytest lodgeick/tests --benchmark-only
```

## Security Testing

All tests follow security best practices:

- ✅ CSRF protection (state parameter in OAuth)
- ✅ Permission checks (user isolation)
- ✅ Input validation (malformed data handling)
- ✅ Token security (no tokens in logs)
- ✅ Database isolation (rollback after tests)

## Contributing

When adding new features:

1. Write unit tests first (TDD approach)
2. Add integration tests for workflows
3. Update this README with new test info
4. Ensure all tests pass before PR
5. Aim for >80% code coverage

## Test Results History

See `TEST_RESULTS.md` in project root for test execution history and known issues.

---

**Last Updated:** 2025-01-10
**Test Suite Version:** 1.0.0 (Phase 3A Complete)
**Total Tests:** 105+
**Coverage:** ~85% of core backend
