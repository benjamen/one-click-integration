"""
Unit tests for lodgeick.api.oauth module
Tests OAuth flow, token management, and credential handling
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime, timedelta
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.oauth import (
    initiate_oauth,
    oauth_callback,
    get_provider_config,
    save_oauth_credentials,
    build_auth_url,
    exchange_code_for_tokens,
    calculate_expiry,
    save_user_oauth_setup,
    refresh_token
)
from lodgeick.tests.fixtures.test_data import (
    MOCK_PROVIDER_CONFIGS,
    MOCK_OAUTH_TOKENS,
    MOCK_OAUTH_STATE
)


class TestInitiateOAuth(FrappeTestCase):
    """Test initiate_oauth function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.api.oauth.get_provider_config')
    @patch('lodgeick.api.oauth.build_auth_url')
    def test_initiate_oauth_success(self, mock_build_url, mock_get_config):
        """Test successful OAuth initiation"""
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS['google']
        mock_build_url.return_value = "https://accounts.google.com/o/oauth2/v2/auth?state=test_state"

        result = initiate_oauth(provider='google', redirect_uri='/app')

        self.assertTrue(result['success'])
        self.assertIn('authorization_url', result)
        self.assertIn('state', result)
        mock_get_config.assert_called_once_with('google')

    @patch('lodgeick.api.oauth.get_provider_config')
    def test_initiate_oauth_missing_provider(self, mock_get_config):
        """Test OAuth initiation with missing provider"""
        mock_get_config.return_value = None

        with self.assertRaises(frappe.exceptions.ValidationError):
            initiate_oauth(provider='invalid_provider')

    @patch('lodgeick.api.oauth.get_provider_config')
    def test_initiate_oauth_missing_credentials(self, mock_get_config):
        """Test OAuth initiation with missing credentials"""
        mock_get_config.return_value = {
            "client_id": None,
            "client_secret": None
        }

        with self.assertRaises(frappe.exceptions.ValidationError):
            initiate_oauth(provider='google')


class TestOAuthCallback(FrappeTestCase):
    """Test oauth_callback function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)
        self.test_state = "test_state_12345"
        self.test_code = "test_auth_code"

    def tearDown(self):
        frappe.set_user("Administrator")
        # Clean up cache
        frappe.cache().delete(f"oauth_state:{self.test_state}")

    @patch('lodgeick.api.oauth.exchange_code_for_tokens')
    @patch('lodgeick.api.oauth.get_provider_config')
    def test_oauth_callback_success(self, mock_get_config, mock_exchange):
        """Test successful OAuth callback"""
        # Setup
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS['google']
        mock_exchange.return_value = MOCK_OAUTH_TOKENS

        # Store state in cache
        frappe.cache().setex(
            f"oauth_state:{self.test_state}",
            600,
            json.dumps(MOCK_OAUTH_STATE)
        )

        # Execute
        result = oauth_callback(
            code=self.test_code,
            state=self.test_state,
            provider='google'
        )

        # Assert
        self.assertTrue(result['success'])
        self.assertIn('message', result)
        self.assertIn('redirect_uri', result)

    def test_oauth_callback_invalid_state(self):
        """Test OAuth callback with invalid state"""
        with self.assertRaises(frappe.exceptions.ValidationError):
            oauth_callback(
                code=self.test_code,
                state="invalid_state",
                provider='google'
            )

    def test_oauth_callback_provider_mismatch(self):
        """Test OAuth callback with provider mismatch"""
        # Store state with different provider
        frappe.cache().setex(
            f"oauth_state:{self.test_state}",
            600,
            json.dumps({
                "provider": "xero",
                "user": self.test_user,
                "redirect_uri": "/app"
            })
        )

        with self.assertRaises(frappe.exceptions.ValidationError):
            oauth_callback(
                code=self.test_code,
                state=self.test_state,
                provider='google'
            )


class TestGetProviderConfig(FrappeTestCase):
    """Test get_provider_config function"""

    @patch('frappe.get_single')
    def test_get_provider_config_from_settings(self, mock_get_single):
        """Test retrieving provider config from OAuth Credentials Settings"""
        # Mock settings doc
        mock_settings = Mock()
        mock_credential = Mock()
        mock_credential.provider = 'google'
        mock_credential.client_id = 'test_client_id'
        mock_credential.client_secret = 'test_client_secret'
        mock_settings.oauth_credentials = [mock_credential]
        mock_get_single.return_value = mock_settings

        config = get_provider_config('google')

        self.assertIsNotNone(config)
        self.assertEqual(config['client_id'], 'test_client_id')
        self.assertEqual(config['client_secret'], 'test_client_secret')
        self.assertIn('auth_url', config)
        self.assertIn('token_url', config)

    @patch('frappe.conf.get')
    def test_get_provider_config_from_conf(self, mock_conf_get):
        """Test retrieving provider config from frappe.conf (fallback)"""
        def conf_side_effect(key):
            conf_map = {
                'google_client_id': 'conf_client_id',
                'google_client_secret': 'conf_client_secret'
            }
            return conf_map.get(key)

        mock_conf_get.side_effect = conf_side_effect

        # Make get_single raise to trigger fallback
        with patch('frappe.get_single', side_effect=Exception("Settings not found")):
            config = get_provider_config('google')

        self.assertIsNotNone(config)
        self.assertEqual(config['client_id'], 'conf_client_id')


class TestSaveOAuthCredentials(FrappeTestCase):
    """Test save_oauth_credentials function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        # Clean up OAuth Credentials Settings if created
        if frappe.db.exists("OAuth Credentials Settings", "OAuth Credentials Settings"):
            frappe.delete_doc("OAuth Credentials Settings", "OAuth Credentials Settings", force=True)

    def test_save_oauth_credentials_new(self):
        """Test saving new OAuth credentials"""
        credentials = [
            {
                "provider": "google",
                "client_id": "new_client_id",
                "client_secret": "new_client_secret"
            }
        ]

        result = save_oauth_credentials(credentials)

        self.assertTrue(result['success'])
        self.assertIn('message', result)

    def test_save_oauth_credentials_multiple(self):
        """Test saving multiple OAuth credentials"""
        credentials = [
            {
                "provider": "google",
                "client_id": "google_client_id",
                "client_secret": "google_client_secret"
            },
            {
                "provider": "xero",
                "client_id": "xero_client_id",
                "client_secret": "xero_client_secret"
            }
        ]

        result = save_oauth_credentials(credentials)

        self.assertTrue(result['success'])


class TestBuildAuthUrl(unittest.TestCase):
    """Test build_auth_url function"""

    def test_build_auth_url_basic(self):
        """Test building basic authorization URL"""
        config = MOCK_PROVIDER_CONFIGS['google']
        state = "test_state"
        redirect_uri = "https://example.com/callback"

        url = build_auth_url(config, state, redirect_uri)

        self.assertIn(config['auth_url'], url)
        self.assertIn(f"client_id={config['client_id']}", url)
        self.assertIn(f"state={state}", url)
        self.assertIn("redirect_uri=", url)
        self.assertIn("response_type=code", url)

    def test_build_auth_url_with_scope(self):
        """Test authorization URL includes scope"""
        config = MOCK_PROVIDER_CONFIGS['google']
        state = "test_state"

        url = build_auth_url(config, state)

        self.assertIn("scope=", url)


class TestExchangeCodeForTokens(unittest.TestCase):
    """Test exchange_code_for_tokens function"""

    @patch('requests.post')
    def test_exchange_code_success(self, mock_post):
        """Test successful token exchange"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_OAUTH_TOKENS
        mock_post.return_value = mock_response

        config = MOCK_PROVIDER_CONFIGS['google']
        code = "test_auth_code"
        redirect_uri = "https://example.com/callback"

        tokens = exchange_code_for_tokens(config, code, redirect_uri)

        self.assertEqual(tokens['access_token'], MOCK_OAUTH_TOKENS['access_token'])
        self.assertEqual(tokens['refresh_token'], MOCK_OAUTH_TOKENS['refresh_token'])
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_exchange_code_failure(self, mock_post):
        """Test failed token exchange"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid authorization code"
        mock_post.return_value = mock_response

        config = MOCK_PROVIDER_CONFIGS['google']
        code = "invalid_code"

        with self.assertRaises(frappe.exceptions.ValidationError):
            exchange_code_for_tokens(config, code, None)


class TestCalculateExpiry(unittest.TestCase):
    """Test calculate_expiry function"""

    def test_calculate_expiry_with_expires_in(self):
        """Test calculating expiry datetime"""
        expires_in = 3600  # 1 hour
        before_time = datetime.now()

        expiry = calculate_expiry(expires_in)

        after_time = datetime.now() + timedelta(seconds=expires_in)

        self.assertIsNotNone(expiry)
        self.assertGreater(expiry, before_time)
        self.assertLessEqual(expiry, after_time + timedelta(seconds=1))

    def test_calculate_expiry_none(self):
        """Test calculate_expiry with None"""
        expiry = calculate_expiry(None)
        self.assertIsNone(expiry)


class TestSaveUserOAuthSetup(FrappeTestCase):
    """Test save_user_oauth_setup function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.conf.get')
    def test_save_user_oauth_default_tier(self, mock_conf_get):
        """Test saving OAuth setup with default tier"""
        def conf_side_effect(key):
            return f"{key}_value"

        mock_conf_get.side_effect = conf_side_effect

        result = save_user_oauth_setup(
            provider='google',
            tier='default',
            use_default=True
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['tier'], 'default')
        self.assertTrue(result['ready_to_connect'])

    def test_save_user_oauth_manual_tier(self):
        """Test saving OAuth setup with manual tier"""
        result = save_user_oauth_setup(
            provider='google',
            tier='manual',
            client_id='manual_client_id',
            client_secret='manual_client_secret'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['tier'], 'manual')
        self.assertTrue(result['ready_to_connect'])

    def test_save_user_oauth_manual_tier_missing_credentials(self):
        """Test manual tier without credentials"""
        with self.assertRaises(frappe.exceptions.ValidationError):
            save_user_oauth_setup(
                provider='google',
                tier='manual',
                client_id=None,
                client_secret=None
            )

    def test_save_user_oauth_ai_tier(self):
        """Test saving OAuth setup with AI tier"""
        result = save_user_oauth_setup(
            provider='google',
            tier='ai'
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['tier'], 'ai')


class TestRefreshToken(FrappeTestCase):
    """Test refresh_token function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('requests.post')
    @patch('lodgeick.api.oauth.get_provider_config')
    @patch('frappe.get_doc')
    def test_refresh_token_success(self, mock_get_doc, mock_get_config, mock_post):
        """Test successful token refresh"""
        # Mock existing token
        mock_token_doc = Mock()
        mock_token_doc.refresh_token = "test_refresh_token"
        mock_token_doc.get_password.return_value = "test_refresh_token"
        mock_get_doc.return_value = mock_token_doc

        # Mock provider config
        mock_get_config.return_value = MOCK_PROVIDER_CONFIGS['google']

        # Mock token refresh response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        result = refresh_token(provider='google', user=self.test_user)

        self.assertTrue(result['success'])
        self.assertIn('message', result)
        mock_post.assert_called_once()

    @patch('frappe.get_doc')
    def test_refresh_token_no_refresh_token(self, mock_get_doc):
        """Test refresh when no refresh token available"""
        mock_token_doc = Mock()
        mock_token_doc.refresh_token = None
        mock_get_doc.return_value = mock_token_doc

        with self.assertRaises(frappe.exceptions.ValidationError):
            refresh_token(provider='google', user=self.test_user)


if __name__ == '__main__':
    unittest.main()
