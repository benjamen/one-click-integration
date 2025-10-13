"""
Unit tests for lodgeick.api.integrations module
Tests integration activation, status, and management
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.integrations import (
    activate_integration,
    get_integration_status,
    list_user_integrations,
    pause_integration,
    delete_integration,
    get_user_token,
    get_workflow_template,
    create_n8n_workflow,
    n8n_webhook_callback
)
from lodgeick.tests.fixtures.test_data import (
    MOCK_USER_INTEGRATION,
    MOCK_N8N_WORKFLOW
)


class TestActivateIntegration(FrappeTestCase):
    """Test activate_integration function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.api.integrations.create_n8n_workflow')
    @patch('lodgeick.api.integrations.get_workflow_template')
    @patch('lodgeick.api.integrations.get_user_token')
    def test_activate_integration_success(self, mock_get_token, mock_get_template, mock_create_workflow):
        """Test successful integration activation"""
        # Mock tokens
        mock_source_token = Mock()
        mock_target_token = Mock()
        mock_get_token.side_effect = [mock_source_token, mock_target_token]

        # Mock workflow template
        mock_get_template.return_value = "template_12345"

        # Mock workflow creation
        mock_create_workflow.return_value = "workflow_abc123"

        result = activate_integration(
            flow_name="Invoice Sync",
            source_app="xero",
            target_app="google_sheets",
            config={"frequency": "daily"}
        )

        self.assertTrue(result['success'])
        self.assertIn('integration_id', result)
        self.assertIn('workflow_id', result)
        self.assertEqual(result['workflow_id'], "workflow_abc123")

    @patch('lodgeick.api.integrations.get_user_token')
    def test_activate_integration_missing_source_token(self, mock_get_token):
        """Test activation fails when source token is missing"""
        mock_get_token.return_value = None

        result = activate_integration(
            flow_name="Invoice Sync",
            source_app="xero",
            target_app="google_sheets"
        )

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('xero', result['error'])

    @patch('lodgeick.api.integrations.get_user_token')
    def test_activate_integration_missing_target_token(self, mock_get_token):
        """Test activation fails when target token is missing"""
        mock_source_token = Mock()
        mock_get_token.side_effect = [mock_source_token, None]

        result = activate_integration(
            flow_name="Invoice Sync",
            source_app="xero",
            target_app="google_sheets"
        )

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('google_sheets', result['error'])

    @patch('lodgeick.api.integrations.get_workflow_template')
    @patch('lodgeick.api.integrations.get_user_token')
    def test_activate_integration_missing_template(self, mock_get_token, mock_get_template):
        """Test activation fails when workflow template not found"""
        mock_source_token = Mock()
        mock_target_token = Mock()
        mock_get_token.side_effect = [mock_source_token, mock_target_token]
        mock_get_template.return_value = None

        result = activate_integration(
            flow_name="Unknown Flow",
            source_app="xero",
            target_app="google_sheets"
        )

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('template not found', result['error'].lower())


class TestGetIntegrationStatus(FrappeTestCase):
    """Test get_integration_status function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.get_all')
    @patch('frappe.get_doc')
    def test_get_integration_status_success(self, mock_get_doc, mock_get_all):
        """Test retrieving integration status"""
        # Mock integration doc
        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.flow_name = "Invoice Sync"
        mock_integration.source_app = "xero"
        mock_integration.target_app = "google_sheets"
        mock_integration.status = "Active"
        mock_integration.last_run = "2025-01-10 10:00:00"
        mock_integration.error_message = None
        mock_integration.user = self.test_user
        mock_get_doc.return_value = mock_integration

        # Mock logs
        mock_get_all.return_value = [
            {
                "status": "Success",
                "message": "Integration executed",
                "timestamp": "2025-01-10 10:00:00"
            }
        ]

        result = get_integration_status("INT-0001")

        self.assertTrue(result['success'])
        self.assertIn('integration', result)
        self.assertEqual(result['integration']['name'], "INT-0001")
        self.assertIn('logs', result)

    @patch('frappe.get_doc')
    def test_get_integration_status_permission_denied(self, mock_get_doc):
        """Test permission denied when accessing other user's integration"""
        mock_integration = Mock()
        mock_integration.user = "other@example.com"
        mock_get_doc.return_value = mock_integration

        with patch('frappe.has_permission', return_value=False):
            with self.assertRaises(frappe.exceptions.PermissionError):
                get_integration_status("INT-0001")


class TestListUserIntegrations(FrappeTestCase):
    """Test list_user_integrations function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('frappe.get_all')
    def test_list_user_integrations_success(self, mock_get_all):
        """Test listing user integrations"""
        mock_integrations = [
            {
                "name": "INT-0001",
                "flow_name": "Invoice Sync",
                "source_app": "xero",
                "target_app": "google_sheets",
                "status": "Active",
                "last_run": "2025-01-10 10:00:00",
                "modified": "2025-01-10 09:00:00"
            },
            {
                "name": "INT-0002",
                "flow_name": "Contact Export",
                "source_app": "xero",
                "target_app": "slack",
                "status": "Paused",
                "last_run": "2025-01-09 10:00:00",
                "modified": "2025-01-09 09:00:00"
            }
        ]
        mock_get_all.return_value = mock_integrations

        result = list_user_integrations()

        self.assertTrue(result['success'])
        self.assertIn('integrations', result)
        self.assertEqual(len(result['integrations']), 2)

    @patch('frappe.get_all')
    def test_list_user_integrations_empty(self, mock_get_all):
        """Test listing when user has no integrations"""
        mock_get_all.return_value = []

        result = list_user_integrations()

        self.assertTrue(result['success'])
        self.assertEqual(len(result['integrations']), 0)


class TestPauseIntegration(FrappeTestCase):
    """Test pause_integration function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.api.integrations.deactivate_n8n_workflow')
    @patch('frappe.get_doc')
    def test_pause_integration_success(self, mock_get_doc, mock_deactivate):
        """Test successfully pausing an integration"""
        # Mock integration doc
        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.user = self.test_user
        mock_integration.workflow_id = "workflow_123"
        mock_integration.status = "Active"
        mock_get_doc.return_value = mock_integration

        result = pause_integration("INT-0001")

        self.assertTrue(result['success'])
        self.assertIn('message', result)
        mock_deactivate.assert_called_once_with("workflow_123")
        self.assertEqual(mock_integration.status, "Paused")

    @patch('frappe.get_doc')
    def test_pause_integration_permission_denied(self, mock_get_doc):
        """Test permission denied when pausing other user's integration"""
        mock_integration = Mock()
        mock_integration.user = "other@example.com"
        mock_get_doc.return_value = mock_integration

        with patch('frappe.has_permission', return_value=False):
            with self.assertRaises(frappe.exceptions.PermissionError):
                pause_integration("INT-0001")


class TestDeleteIntegration(FrappeTestCase):
    """Test delete_integration function"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")

    @patch('lodgeick.api.integrations.delete_n8n_workflow')
    @patch('frappe.delete_doc')
    @patch('frappe.get_doc')
    def test_delete_integration_success(self, mock_get_doc, mock_delete_doc, mock_delete_workflow):
        """Test successfully deleting an integration"""
        # Mock integration doc
        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.user = self.test_user
        mock_integration.workflow_id = "workflow_123"
        mock_integration.flow_name = "Invoice Sync"
        mock_get_doc.return_value = mock_integration

        result = delete_integration("INT-0001")

        self.assertTrue(result['success'])
        self.assertIn('Invoice Sync', result['message'])
        mock_delete_workflow.assert_called_once_with("workflow_123")
        mock_delete_doc.assert_called_once()

    @patch('frappe.get_doc')
    def test_delete_integration_permission_denied(self, mock_get_doc):
        """Test permission denied when deleting other user's integration"""
        mock_integration = Mock()
        mock_integration.user = "other@example.com"
        mock_get_doc.return_value = mock_integration

        with patch('frappe.has_permission', return_value=False):
            with self.assertRaises(frappe.exceptions.PermissionError):
                delete_integration("INT-0001")


class TestGetUserToken(unittest.TestCase):
    """Test get_user_token helper function"""

    @patch('frappe.get_doc')
    def test_get_user_token_exists(self, mock_get_doc):
        """Test retrieving existing user token"""
        mock_token = Mock()
        mock_token.provider = "google"
        mock_token.access_token = "test_token"
        mock_get_doc.return_value = mock_token

        token = get_user_token("test@example.com", "google")

        self.assertIsNotNone(token)
        self.assertEqual(token.provider, "google")

    @patch('frappe.get_doc')
    def test_get_user_token_not_exists(self, mock_get_doc):
        """Test retrieving non-existent token"""
        mock_get_doc.side_effect = frappe.DoesNotExistError()

        token = get_user_token("test@example.com", "invalid_provider")

        self.assertIsNone(token)


class TestGetWorkflowTemplate(unittest.TestCase):
    """Test get_workflow_template helper function"""

    @patch('frappe.get_doc')
    def test_get_workflow_template_found(self, mock_get_doc):
        """Test finding workflow template"""
        # Mock app catalog doc
        mock_app = Mock()
        mock_use_case = Mock()
        mock_use_case.use_case_name = "Invoice Sync"
        mock_use_case.workflow_template_id = "template_12345"
        mock_app.use_cases = [mock_use_case]
        mock_get_doc.return_value = mock_app

        template_id = get_workflow_template("Invoice Sync", "xero", "google_sheets")

        self.assertEqual(template_id, "template_12345")

    @patch('frappe.get_doc')
    def test_get_workflow_template_not_found(self, mock_get_doc):
        """Test workflow template not found"""
        mock_app = Mock()
        mock_app.use_cases = []
        mock_get_doc.return_value = mock_app

        template_id = get_workflow_template("Unknown Flow", "xero", "google_sheets")

        self.assertIsNone(template_id)

    @patch('frappe.get_doc')
    def test_get_workflow_template_app_not_exists(self, mock_get_doc):
        """Test workflow template when app doesn't exist"""
        mock_get_doc.side_effect = frappe.DoesNotExistError()

        template_id = get_workflow_template("Invoice Sync", "invalid_app", "google_sheets")

        self.assertIsNone(template_id)


class TestCreateN8nWorkflow(unittest.TestCase):
    """Test create_n8n_workflow helper function"""

    @patch('frappe.conf.get')
    def test_create_n8n_workflow_not_configured(self, mock_conf_get):
        """Test creating workflow when n8n not configured"""
        mock_conf_get.return_value = None

        workflow_id = create_n8n_workflow(
            template_id="template_123",
            source_token=Mock(),
            target_token=Mock(),
            config={}
        )

        # Should return fallback workflow ID
        self.assertIsNotNone(workflow_id)
        self.assertIn("workflow_", workflow_id)


class TestN8nWebhookCallback(FrappeTestCase):
    """Test n8n_webhook_callback function"""

    @patch('frappe.get_all')
    @patch('frappe.get_doc')
    def test_webhook_callback_success_status(self, mock_get_doc, mock_get_all):
        """Test webhook callback with success status"""
        # Mock integration lookup
        mock_get_all.return_value = [{"name": "INT-0001"}]

        # Mock integration doc
        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.mark_completed = Mock()
        mock_get_doc.return_value = mock_integration

        # Mock webhook data
        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "success",
            "message": "Workflow executed successfully",
            "execution_time": 1.23
        }):
            result = n8n_webhook_callback()

        self.assertTrue(result['success'])
        mock_integration.mark_completed.assert_called_once()

    @patch('frappe.get_all')
    @patch('frappe.get_doc')
    def test_webhook_callback_error_status(self, mock_get_doc, mock_get_all):
        """Test webhook callback with error status"""
        # Mock integration lookup
        mock_get_all.return_value = [{"name": "INT-0001"}]

        # Mock integration doc
        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.mark_error = Mock()
        mock_get_doc.return_value = mock_integration

        # Mock webhook data
        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "error",
            "message": "Workflow failed",
            "execution_time": 0.5
        }):
            result = n8n_webhook_callback()

        self.assertTrue(result['success'])
        mock_integration.mark_error.assert_called_once_with("Workflow failed")

    @patch('frappe.get_all')
    def test_webhook_callback_integration_not_found(self, mock_get_all):
        """Test webhook callback when integration not found"""
        mock_get_all.return_value = []

        with patch('frappe.local.form_dict', {
            "workflow_id": "invalid_workflow",
            "status": "success",
            "message": "Test"
        }):
            result = n8n_webhook_callback()

        self.assertFalse(result['success'])
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()
