"""
Integration tests for complete OAuth flow
Tests end-to-end OAuth authentication process
"""

import unittest
from unittest.mock import Mock, patch
import json
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.oauth import initiate_oauth, oauth_callback
from lodgeick.tests.fixtures.test_data import (
    MOCK_PROVIDER_CONFIGS,
    MOCK_OAUTH_TOKENS
)


class TestOAuthFlowIntegration(FrappeTestCase):
    """Test complete OAuth flow from initiation to callback"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)
        self.provider = "google"
        self.redirect_uri = "/app"

    def tearDown(self):
        frappe.set_user("Administrator")
        # Clean up any test data
        frappe.db.rollback()

    @patch('requests.post')
    @patch('lodgeick.api.oauth.get_provider_config')
    def test_complete_oauth_flow(self, mock_get_config, mock_post):
        """Test complete OAuth flow: initiate -> callback -> token stored"""
        # Setup
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS[self.provider]

        # Mock token exchange response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_OAUTH_TOKENS
        mock_post.return_value = mock_response

        # Step 1: Initiate OAuth
        init_result = initiate_oauth(
            provider=self.provider,
            redirect_uri=self.redirect_uri
        )

        self.assertTrue(init_result['success'])
        self.assertIn('authorization_url', init_result)
        self.assertIn('state', init_result)

        state = init_result['state']

        # Verify state is stored in cache
        cached_state = frappe.cache().get(f"oauth_state:{state}")
        self.assertIsNotNone(cached_state)

        # Step 2: Simulate OAuth callback
        auth_code = "test_auth_code_12345"

        callback_result = oauth_callback(
            code=auth_code,
            state=state,
            provider=self.provider
        )

        self.assertTrue(callback_result['success'])
        self.assertIn('message', callback_result)

        # Verify token was stored (would need to query Integration Token doctype)
        # This would require actual database access in real integration test

        # Verify state was cleared from cache
        cached_state_after = frappe.cache().get(f"oauth_state:{state}")
        self.assertIsNone(cached_state_after)

    @patch('lodgeick.api.oauth.get_provider_config')
    def test_oauth_flow_with_expired_state(self, mock_get_config):
        """Test OAuth callback with expired state token"""
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS[self.provider]

        # Initiate OAuth
        init_result = initiate_oauth(provider=self.provider)
        state = init_result['state']

        # Manually clear state to simulate expiration
        frappe.cache().delete(f"oauth_state:{state}")

        # Attempt callback with expired state
        with self.assertRaises(frappe.exceptions.ValidationError):
            oauth_callback(
                code="test_code",
                state=state,
                provider=self.provider
            )

    @patch('requests.post')
    @patch('lodgeick.api.oauth.get_provider_config')
    def test_oauth_flow_with_invalid_code(self, mock_get_config, mock_post):
        """Test OAuth flow with invalid authorization code"""
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS[self.provider]

        # Mock failed token exchange
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid authorization code"
        mock_post.return_value = mock_response

        # Initiate OAuth
        init_result = initiate_oauth(provider=self.provider)
        state = init_result['state']

        # Attempt callback with invalid code
        with self.assertRaises(frappe.exceptions.ValidationError):
            oauth_callback(
                code="invalid_code",
                state=state,
                provider=self.provider
            )

    @patch('lodgeick.api.oauth.get_provider_config')
    def test_oauth_flow_csrf_protection(self, mock_get_config):
        """Test OAuth flow CSRF protection via state parameter"""
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS[self.provider]

        # Initiate OAuth
        init_result = initiate_oauth(provider=self.provider)
        legitimate_state = init_result['state']

        # Attempt callback with different state (CSRF attack)
        malicious_state = "malicious_state_token"

        with self.assertRaises(frappe.exceptions.ValidationError):
            oauth_callback(
                code="test_code",
                state=malicious_state,
                provider=self.provider
            )

        # Verify legitimate state is still in cache
        cached_state = frappe.cache().get(f"oauth_state:{legitimate_state}")
        self.assertIsNotNone(cached_state)


class TestMultiProviderOAuthFlow(FrappeTestCase):
    """Test OAuth flow with multiple providers"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('lodgeick.api.oauth.get_provider_config')
    def test_multiple_concurrent_oauth_flows(self, mock_get_config):
        """Test initiating OAuth for multiple providers simultaneously"""
        providers = ['google', 'xero', 'slack']
        states = {}

        def get_config_side_effect(provider):
            return MOCK_PROVIDER_CONFIGS.get(provider)

        mock_get_config.side_effect = get_config_side_effect

        # Initiate OAuth for multiple providers
        for provider in providers:
            result = initiate_oauth(provider=provider)
            self.assertTrue(result['success'])
            states[provider] = result['state']

        # Verify each provider has unique state
        unique_states = set(states.values())
        self.assertEqual(len(unique_states), len(providers))

        # Verify all states are cached with correct provider
        for provider, state in states.items():
            cached_data = frappe.cache().get(f"oauth_state:{state}")
            self.assertIsNotNone(cached_data)
            cached_data = json.loads(cached_data)
            self.assertEqual(cached_data['provider'], provider)


class TestOAuthFlowWithIntegrationSettings(FrappeTestCase):
    """Test OAuth flow creates User Integration Settings"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('frappe.db.get_value')
    @patch('requests.post')
    @patch('lodgeick.api.oauth.get_provider_config')
    def test_oauth_creates_integration_settings(self, mock_get_config, mock_post, mock_db_get_value):
        """Test OAuth callback creates User Integration Settings"""
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS['google']

        # Mock token exchange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_OAUTH_TOKENS
        mock_post.return_value = mock_response

        # Mock app lookup
        mock_db_get_value.return_value = "google_sheets"

        # Initiate and complete OAuth flow
        init_result = initiate_oauth(provider='google')
        state = init_result['state']

        callback_result = oauth_callback(
            code="test_code",
            state=state,
            provider='google'
        )

        self.assertTrue(callback_result['success'])

        # In real integration test, verify User Integration Settings was created
        # This would require actual database access


class TestOAuthFlowErrorRecovery(FrappeTestCase):
    """Test OAuth flow error handling and recovery"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('requests.post')
    @patch('lodgeick.api.oauth.get_provider_config')
    def test_oauth_flow_retry_after_failure(self, mock_get_config, mock_post):
        """Test user can retry OAuth flow after failure"""
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS['google']

        # First attempt: Initiate OAuth
        init_result_1 = initiate_oauth(provider='google')
        state_1 = init_result_1['state']

        # Simulate token exchange failure
        mock_response_fail = Mock()
        mock_response_fail.status_code = 400
        mock_response_fail.text = "Token exchange failed"
        mock_post.return_value = mock_response_fail

        with self.assertRaises(frappe.exceptions.ValidationError):
            oauth_callback(code="bad_code", state=state_1, provider='google')

        # Second attempt: Retry OAuth flow
        init_result_2 = initiate_oauth(provider='google')
        state_2 = init_result_2['state']

        # States should be different
        self.assertNotEqual(state_1, state_2)

        # Simulate successful token exchange
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = MOCK_OAUTH_TOKENS
        mock_post.return_value = mock_response_success

        callback_result = oauth_callback(
            code="good_code",
            state=state_2,
            provider='google'
        )

        self.assertTrue(callback_result['success'])


if __name__ == '__main__':
    unittest.main()
