"""
Integration tests for n8n webhook integration
Tests workflow execution callbacks and status updates
"""

import unittest
from unittest.mock import Mock, patch
import json
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.integrations import (
    n8n_webhook_callback,
    activate_integration
)
from lodgeick.tests.fixtures.test_data import MOCK_USER_INTEGRATION


class TestN8nWebhookIntegration(FrappeTestCase):
    """Test n8n webhook callback integration"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('frappe.get_doc')
    @patch('frappe.get_all')
    def test_webhook_success_updates_integration(self, mock_get_all, mock_get_doc):
        """Test successful webhook updates integration status"""
        # Mock integration lookup
        mock_get_all.return_value = [{"name": "INT-0001"}]

        # Mock integration doc
        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.mark_completed = Mock()
        mock_get_doc.return_value = mock_integration

        # Simulate n8n webhook callback
        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "success",
            "message": "Integration executed successfully",
            "execution_time": 2.5
        }):
            result = n8n_webhook_callback()

        self.assertTrue(result['success'])
        mock_integration.mark_completed.assert_called_once()

    @patch('frappe.get_doc')
    @patch('frappe.get_all')
    def test_webhook_error_updates_integration(self, mock_get_all, mock_get_doc):
        """Test error webhook updates integration error status"""
        mock_get_all.return_value = [{"name": "INT-0001"}]

        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.mark_error = Mock()
        mock_get_doc.return_value = mock_integration

        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "error",
            "message": "API rate limit exceeded",
            "execution_time": 0.3
        }):
            result = n8n_webhook_callback()

        self.assertTrue(result['success'])
        mock_integration.mark_error.assert_called_once_with("API rate limit exceeded")

    @patch('frappe.get_all')
    def test_webhook_with_unknown_workflow(self, mock_get_all):
        """Test webhook callback for unknown workflow ID"""
        mock_get_all.return_value = []  # No integration found

        with patch('frappe.local.form_dict', {
            "workflow_id": "unknown_workflow",
            "status": "success",
            "message": "Test"
        }):
            result = n8n_webhook_callback()

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    @patch('frappe.get_doc')
    @patch('frappe.get_all')
    def test_webhook_creates_integration_log(self, mock_get_all, mock_get_doc):
        """Test webhook callback creates integration log entry"""
        mock_get_all.return_value = [{"name": "INT-0001"}]

        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.mark_completed = Mock()
        mock_get_doc.return_value = mock_integration

        execution_time = 1.75

        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "success",
            "message": "Processed 50 records",
            "execution_time": execution_time
        }):
            with patch('lodgeick.lodgeick.doctype.integration_log.integration_log.IntegrationLog.create_log') as mock_create_log:
                result = n8n_webhook_callback()

                self.assertTrue(result['success'])
                # Verify log was created
                mock_create_log.assert_called_once()


class TestIntegrationWithN8nWorkflow(FrappeTestCase):
    """Test integration activation with n8n workflow creation"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('lodgeick.api.integrations.create_n8n_workflow')
    @patch('lodgeick.api.integrations.get_workflow_template')
    @patch('lodgeick.api.integrations.get_user_token')
    def test_integration_creates_n8n_workflow(self, mock_get_token, mock_get_template, mock_create_workflow):
        """Test integration activation creates n8n workflow"""
        # Mock tokens
        mock_source_token = Mock()
        mock_target_token = Mock()
        mock_get_token.side_effect = [mock_source_token, mock_target_token]

        # Mock template
        mock_get_template.return_value = "template_invoice_sync"

        # Mock workflow creation
        workflow_id = "workflow_abc123"
        mock_create_workflow.return_value = workflow_id

        result = activate_integration(
            flow_name="Invoice Sync",
            source_app="xero",
            target_app="google_sheets",
            config={"frequency": "daily"}
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['workflow_id'], workflow_id)

        # Verify workflow was created with correct parameters
        mock_create_workflow.assert_called_once()
        call_args = mock_create_workflow.call_args[0]
        self.assertEqual(call_args[0], "template_invoice_sync")


class TestN8nWebhookRetry(FrappeTestCase):
    """Test n8n webhook retry logic"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('frappe.get_doc')
    @patch('frappe.get_all')
    def test_webhook_multiple_status_updates(self, mock_get_all, mock_get_doc):
        """Test multiple webhook callbacks for same integration"""
        mock_get_all.return_value = [{"name": "INT-0001"}]

        mock_integration = Mock()
        mock_integration.name = "INT-0001"
        mock_integration.mark_error = Mock()
        mock_integration.mark_completed = Mock()
        mock_get_doc.return_value = mock_integration

        # First webhook: Error
        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "error",
            "message": "Temporary failure",
            "execution_time": 0.5
        }):
            result1 = n8n_webhook_callback()

        self.assertTrue(result1['success'])
        mock_integration.mark_error.assert_called_once()

        # Second webhook: Success (retry worked)
        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "success",
            "message": "Retry successful",
            "execution_time": 1.2
        }):
            result2 = n8n_webhook_callback()

        self.assertTrue(result2['success'])
        mock_integration.mark_completed.assert_called_once()


class TestN8nWebhookSecurity(FrappeTestCase):
    """Test n8n webhook security and validation"""

    def test_webhook_validates_required_fields(self):
        """Test webhook validates required payload fields"""
        # Missing workflow_id
        with patch('frappe.local.form_dict', {
            "status": "success",
            "message": "Test"
        }):
            result = n8n_webhook_callback()

        self.assertFalse(result['success'])

    @patch('frappe.get_all')
    def test_webhook_handles_malformed_data(self, mock_get_all):
        """Test webhook handles malformed callback data"""
        mock_get_all.return_value = [{"name": "INT-0001"}]

        # Malformed execution_time
        with patch('frappe.local.form_dict', {
            "workflow_id": "workflow_123",
            "status": "success",
            "message": "Test",
            "execution_time": "not_a_number"
        }):
            # Should handle gracefully
            with patch('frappe.get_doc'):
                result = n8n_webhook_callback()

        # Webhook should still process (execution_time is optional)
        self.assertTrue(result['success'])


class TestN8nWorkflowLifecycle(FrappeTestCase):
    """Test complete n8n workflow lifecycle"""

    def setUp(self):
        self.test_user = "test@example.com"
        frappe.set_user(self.test_user)

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    @patch('lodgeick.api.integrations.delete_n8n_workflow')
    @patch('lodgeick.api.integrations.deactivate_n8n_workflow')
    @patch('lodgeick.api.integrations.create_n8n_workflow')
    @patch('lodgeick.api.integrations.get_workflow_template')
    @patch('lodgeick.api.integrations.get_user_token')
    @patch('frappe.get_doc')
    def test_workflow_lifecycle_activate_pause_delete(self, mock_get_doc, mock_get_token,
                                                      mock_get_template, mock_create_workflow,
                                                      mock_deactivate, mock_delete):
        """Test full workflow lifecycle: activate -> pause -> delete"""
        from lodgeick.api.integrations import pause_integration, delete_integration

        # Setup mocks
        mock_source_token = Mock()
        mock_target_token = Mock()
        mock_get_token.side_effect = [mock_source_token, mock_target_token]
        mock_get_template.return_value = "template_123"
        mock_create_workflow.return_value = "workflow_123"

        # Step 1: Activate integration
        activate_result = activate_integration(
            flow_name="Test Flow",
            source_app="xero",
            target_app="google_sheets"
        )

        self.assertTrue(activate_result['success'])
        workflow_id = activate_result['workflow_id']

        # Step 2: Pause integration
        mock_integration = Mock()
        mock_integration.user = self.test_user
        mock_integration.workflow_id = workflow_id
        mock_integration.status = "Active"
        mock_get_doc.return_value = mock_integration

        pause_result = pause_integration(activate_result['integration_id'])

        self.assertTrue(pause_result['success'])
        mock_deactivate.assert_called_once_with(workflow_id)

        # Step 3: Delete integration
        mock_integration.flow_name = "Test Flow"
        delete_result = delete_integration(activate_result['integration_id'])

        self.assertTrue(delete_result['success'])
        mock_delete.assert_called_once_with(workflow_id)


if __name__ == '__main__':
    unittest.main()
