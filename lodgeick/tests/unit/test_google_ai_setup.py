"""
Unit tests for lodgeick.api.google_ai_setup module
Tests AI-powered Google Cloud project setup
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.google_ai_setup import (
    parse_intent,
    create_project,
    setup_oauth_credentials,
    get_setup_status,
    list_user_projects,
    _store_user_project,
    _sync_credentials_to_n8n
)
from lodgeick.tests.fixtures.test_data import (
    MOCK_AI_INTENT_RESPONSE,
    MOCK_GOOGLE_PROJECT
)


class TestParseIntent(FrappeTestCase):
    """Test parse_intent function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.services.ai_parser.get_ai_parser')
    def test_parse_intent_success(self, mock_get_parser):
        """Test successful intent parsing"""
        mock_parser = Mock()
        mock_parser.parse_intent.return_value = {
            "apis": [
                {
                    "name": "gmail",
                    "display_name": "Gmail API",
                    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
                    "description": "Read emails"
                }
            ],
            "billing_required": False,
            "billing_apis": [],
            "reasoning": "User wants to read Gmail"
        }
        mock_get_parser.return_value = mock_parser

        result = parse_intent(intent="I want to sync my Gmail emails")

        self.assertTrue(result['success'])
        self.assertIn('apis', result)
        self.assertIn('reasoning', result)
        self.assertIn('next_step', result)
        self.assertEqual(result['next_step'], 'project_setup')

    @patch('lodgeick.services.ai_parser.get_ai_parser')
    def test_parse_intent_with_billing(self, mock_get_parser):
        """Test intent parsing when billing required"""
        mock_parser = Mock()
        mock_parser.parse_intent.return_value = {
            "apis": [
                {
                    "name": "maps",
                    "display_name": "Maps API",
                    "scopes": [],
                    "description": "Maps functionality"
                }
            ],
            "billing_required": True,
            "billing_apis": ["maps"],
            "reasoning": "Maps API requires billing"
        }
        mock_get_parser.return_value = mock_parser

        result = parse_intent(intent="I want to use Google Maps")

        self.assertTrue(result['success'])
        self.assertTrue(result['billing_required'])
        self.assertEqual(result['next_step'], 'billing_setup')
        self.assertIn('billing_apis', result)

    @patch('lodgeick.services.ai_parser.get_ai_parser')
    def test_parse_intent_error(self, mock_get_parser):
        """Test intent parsing error handling"""
        mock_parser = Mock()
        mock_parser.parse_intent.side_effect = Exception("AI service unavailable")
        mock_get_parser.return_value = mock_parser

        result = parse_intent(intent="test intent")

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCreateProject(FrappeTestCase):
    """Test create_project function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.api.google_ai_setup._store_user_project')
    @patch('lodgeick.api.google_cloud.get_google_cloud_client')
    def test_create_project_success(self, mock_get_client, mock_store):
        """Test successful project creation"""
        # Mock Google Cloud client
        mock_client = Mock()
        mock_client.create_project.return_value = {"projectId": "test-project-123"}
        mock_client.enable_apis.return_value = {
            "enabled": ["gmail", "sheets"],
            "failed": []
        }
        mock_get_client.return_value = mock_client

        intent_data = {
            "apis": [
                {"name": "gmail", "display_name": "Gmail API"},
                {"name": "sheets", "display_name": "Sheets API"}
            ]
        }

        result = create_project(
            project_name="Test Project",
            intent_data=json.dumps(intent_data)
        )

        self.assertTrue(result['success'])
        self.assertIn('project_id', result)
        self.assertIn('project_name', result)
        self.assertIn('apis_enabled', result)
        self.assertEqual(len(result['apis_enabled']), 2)
        self.assertEqual(result['next_step'], 'oauth_setup')

    @patch('lodgeick.api.google_cloud.get_google_cloud_client')
    def test_create_project_sanitizes_name(self, mock_get_client):
        """Test project name is sanitized for GCP"""
        mock_client = Mock()
        mock_client.create_project.return_value = {"projectId": "my-test-project"}
        mock_client.enable_apis.return_value = {"enabled": [], "failed": []}
        mock_get_client.return_value = mock_client

        result = create_project(
            project_name="My Test Project!@#$%",
            intent_data=json.dumps({"apis": []})
        )

        # Verify project_id is sanitized (lowercase, hyphens, no special chars)
        self.assertTrue(result['success'])
        project_id = result['project_id']
        self.assertTrue(project_id.islower() or '-' in project_id)
        self.assertFalse(any(c in project_id for c in '!@#$%'))

    @patch('lodgeick.api.google_ai_setup._store_user_project')
    @patch('lodgeick.api.google_cloud.get_google_cloud_client')
    def test_create_project_with_failed_apis(self, mock_get_client, mock_store):
        """Test project creation when some APIs fail to enable"""
        mock_client = Mock()
        mock_client.create_project.return_value = {"projectId": "test-project"}
        mock_client.enable_apis.return_value = {
            "enabled": ["gmail"],
            "failed": [{"name": "sheets", "error": "Permission denied"}]
        }
        mock_get_client.return_value = mock_client

        intent_data = {
            "apis": [
                {"name": "gmail", "display_name": "Gmail API"},
                {"name": "sheets", "display_name": "Sheets API"}
            ]
        }

        result = create_project(
            project_name="Test Project",
            intent_data=json.dumps(intent_data)
        )

        self.assertTrue(result['success'])
        self.assertEqual(len(result['apis_enabled']), 1)
        self.assertEqual(len(result['apis_failed']), 1)

    @patch('lodgeick.api.google_cloud.get_google_cloud_client')
    def test_create_project_error(self, mock_get_client):
        """Test project creation error handling"""
        mock_client = Mock()
        mock_client.create_project.side_effect = Exception("GCP API error")
        mock_get_client.return_value = mock_client

        result = create_project(
            project_name="Test Project",
            intent_data=json.dumps({"apis": []})
        )

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestSetupOAuthCredentials(FrappeTestCase):
    """Test setup_oauth_credentials function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.api.google_ai_setup._sync_credentials_to_n8n')
    @patch('lodgeick.api.oauth.save_oauth_credentials')
    def test_setup_oauth_credentials_success(self, mock_save_creds, mock_sync):
        """Test successful OAuth credentials setup"""
        mock_save_creds.return_value = {"success": True}
        mock_sync.return_value = {
            "success": True,
            "credential_id": "n8n_cred_123"
        }

        result = setup_oauth_credentials(
            project_id="test-project-123",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )

        self.assertTrue(result['success'])
        self.assertIn('n8n_credential_id', result)
        self.assertEqual(result['next_step'], 'complete')

    @patch('lodgeick.api.oauth.save_oauth_credentials')
    def test_setup_oauth_credentials_save_failure(self, mock_save_creds):
        """Test OAuth setup when credential save fails"""
        mock_save_creds.return_value = {
            "success": False,
            "error": "Failed to save credentials"
        }

        result = setup_oauth_credentials(
            project_id="test-project",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )

        self.assertFalse(result['success'])

    @patch('lodgeick.api.google_ai_setup._sync_credentials_to_n8n')
    @patch('lodgeick.api.oauth.save_oauth_credentials')
    def test_setup_oauth_credentials_error(self, mock_save_creds, mock_sync):
        """Test OAuth setup error handling"""
        mock_save_creds.side_effect = Exception("Database error")

        result = setup_oauth_credentials(
            project_id="test-project",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestGetSetupStatus(FrappeTestCase):
    """Test get_setup_status function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.get_doc')
    def test_get_setup_status_success(self, mock_get_doc):
        """Test retrieving project setup status"""
        mock_project = Mock()
        mock_project.project_id = "test-project-123"
        mock_project.project_name = "Test Project"
        mock_project.status = "Complete"
        mock_project.apis_enabled = json.dumps(["gmail", "sheets"])
        mock_project.creation = "2025-01-10 10:00:00"
        mock_project.oauth_client_id = "test_client_id"
        mock_get_doc.return_value = mock_project

        result = get_setup_status(project_id="test-project-123")

        self.assertTrue(result['success'])
        self.assertIn('project', result)
        self.assertEqual(result['project']['id'], "test-project-123")
        self.assertTrue(result['project']['has_oauth'])

    @patch('frappe.get_doc')
    def test_get_setup_status_not_found(self, mock_get_doc):
        """Test retrieving status for non-existent project"""
        mock_get_doc.side_effect = frappe.DoesNotExistError()

        result = get_setup_status(project_id="nonexistent")

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('not found', result['error'].lower())

    @patch('frappe.get_doc')
    def test_get_setup_status_no_oauth(self, mock_get_doc):
        """Test status when OAuth not yet set up"""
        mock_project = Mock()
        mock_project.project_id = "test-project"
        mock_project.project_name = "Test"
        mock_project.status = "APIs Enabled"
        mock_project.apis_enabled = json.dumps(["gmail"])
        mock_project.creation = "2025-01-10 10:00:00"
        mock_project.oauth_client_id = None
        mock_get_doc.return_value = mock_project

        result = get_setup_status(project_id="test-project")

        self.assertTrue(result['success'])
        self.assertFalse(result['project']['has_oauth'])


class TestListUserProjects(FrappeTestCase):
    """Test list_user_projects function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.get_all')
    def test_list_user_projects_success(self, mock_get_all):
        """Test listing user's Google Cloud projects"""
        mock_projects = [
            {
                "project_id": "project-1",
                "project_name": "Project 1",
                "status": "Complete",
                "creation": "2025-01-10 10:00:00",
                "apis_enabled": json.dumps(["gmail"])
            },
            {
                "project_id": "project-2",
                "project_name": "Project 2",
                "status": "APIs Enabled",
                "creation": "2025-01-09 10:00:00",
                "apis_enabled": json.dumps(["sheets"])
            }
        ]
        mock_get_all.return_value = mock_projects

        result = list_user_projects()

        self.assertTrue(result['success'])
        self.assertIn('projects', result)
        self.assertEqual(len(result['projects']), 2)
        # Check APIs are parsed
        self.assertIsInstance(result['projects'][0]['apis_enabled'], list)

    @patch('frappe.get_all')
    def test_list_user_projects_empty(self, mock_get_all):
        """Test listing when user has no projects"""
        mock_get_all.return_value = []

        result = list_user_projects()

        self.assertTrue(result['success'])
        self.assertEqual(len(result['projects']), 0)

    @patch('frappe.get_all')
    def test_list_user_projects_error(self, mock_get_all):
        """Test error handling in list projects"""
        mock_get_all.side_effect = Exception("Database error")

        result = list_user_projects()

        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestStoreUserProject(FrappeTestCase):
    """Test _store_user_project helper function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.new_doc')
    @patch('frappe.db.exists')
    def test_store_user_project_new(self, mock_exists, mock_new_doc):
        """Test storing new project"""
        mock_exists.return_value = False
        mock_doc = Mock()
        mock_new_doc.return_value = mock_doc

        intent_data = {"apis": [{"name": "gmail"}]}
        enable_result = {"enabled": ["gmail"], "failed": []}

        _store_user_project(
            project_id="test-project",
            project_name="Test Project",
            intent_data=intent_data,
            enable_result=enable_result
        )

        mock_doc.save.assert_called_once()
        self.assertEqual(mock_doc.status, "APIs Enabled")

    @patch('frappe.get_doc')
    @patch('frappe.db.exists')
    def test_store_user_project_update_existing(self, mock_exists, mock_get_doc):
        """Test updating existing project"""
        mock_exists.return_value = True
        mock_doc = Mock()
        mock_get_doc.return_value = mock_doc

        intent_data = {"apis": [{"name": "gmail"}]}
        enable_result = {"enabled": ["gmail"], "failed": []}

        _store_user_project(
            project_id="test-project",
            project_name="Test Project",
            intent_data=intent_data,
            enable_result=enable_result
        )

        mock_doc.save.assert_called_once()


class TestSyncCredentialsToN8n(FrappeTestCase):
    """Test _sync_credentials_to_n8n helper function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.get_doc')
    @patch('lodgeick.services.n8n_client.get_n8n_client')
    def test_sync_credentials_success(self, mock_get_client, mock_get_doc):
        """Test successful credential sync to n8n"""
        # Mock n8n client
        mock_client = Mock()
        mock_client.create_credential.return_value = {"id": "n8n_cred_123"}
        mock_get_client.return_value = mock_client

        # Mock project doc
        mock_project = Mock()
        mock_get_doc.return_value = mock_project

        result = _sync_credentials_to_n8n(
            project_id="test-project",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['credential_id'], "n8n_cred_123")
        mock_project.save.assert_called_once()
        self.assertEqual(mock_project.status, "Complete")

    @patch('lodgeick.services.n8n_client.get_n8n_client')
    def test_sync_credentials_n8n_error(self, mock_get_client):
        """Test credential sync when n8n fails (should not fail overall setup)"""
        mock_client = Mock()
        mock_client.create_credential.side_effect = Exception("n8n error")
        mock_get_client.return_value = mock_client

        result = _sync_credentials_to_n8n(
            project_id="test-project",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )

        # Should return failure but not raise
        self.assertFalse(result['success'])
        self.assertIsNone(result['credential_id'])


if __name__ == '__main__':
    unittest.main()
