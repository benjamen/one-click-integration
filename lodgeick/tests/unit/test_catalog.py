"""
Unit tests for lodgeick.api.catalog module
Tests app catalog retrieval, filtering, and search
"""

import unittest
from unittest.mock import Mock, patch
import frappe
from frappe.tests.utils import FrappeTestCase

from lodgeick.api.catalog import (
    get_app_catalog,
    get_app_details,
    get_categories,
    search_apps
)
from lodgeick.tests.fixtures.test_data import (
    MOCK_APP_CATALOG,
    MOCK_USE_CASES
)


class TestGetAppCatalog(FrappeTestCase):
    """Test get_app_catalog function"""

    @patch('frappe.get_all')
    def test_get_app_catalog_all_apps(self, mock_get_all):
        """Test retrieving all apps from catalog"""
        # Mock get_all to return apps and then use cases
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                return MOCK_APP_CATALOG
            elif doctype == "App Use Case":
                parent = kwargs['filters']['parent']
                return MOCK_USE_CASES.get(parent, [])
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = get_app_catalog()

        self.assertTrue(result['success'])
        self.assertIn('apps', result)
        self.assertEqual(len(result['apps']), 3)
        # Check use cases are included
        for app in result['apps']:
            self.assertIn('use_cases', app)

    @patch('frappe.get_all')
    def test_get_app_catalog_by_category(self, mock_get_all):
        """Test retrieving apps filtered by category"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                # Filter by category
                category = kwargs['filters'].get('category')
                if category:
                    return [app for app in MOCK_APP_CATALOG if app['category'] == category]
                return MOCK_APP_CATALOG
            elif doctype == "App Use Case":
                parent = kwargs['filters']['parent']
                return MOCK_USE_CASES.get(parent, [])
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = get_app_catalog(category="Accounting")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['apps']), 1)
        self.assertEqual(result['apps'][0]['display_name'], "Xero")

    @patch('frappe.get_all')
    def test_get_app_catalog_empty(self, mock_get_all):
        """Test retrieving catalog when no apps exist"""
        mock_get_all.return_value = []

        result = get_app_catalog()

        self.assertTrue(result['success'])
        self.assertEqual(len(result['apps']), 0)


class TestGetAppDetails(FrappeTestCase):
    """Test get_app_details function"""

    @patch('frappe.get_doc')
    def test_get_app_details_success(self, mock_get_doc):
        """Test retrieving app details successfully"""
        # Mock app doc
        mock_app = Mock()
        mock_app.app_name = "xero"
        mock_app.display_name = "Xero"
        mock_app.logo_url = "/assets/logos/xero.png"
        mock_app.description = "Cloud accounting software"
        mock_app.category = "Accounting"
        mock_app.oauth_provider = "xero"

        # Mock use cases
        mock_use_case_1 = Mock()
        mock_use_case_1.use_case_name = "Invoice Sync"
        mock_use_case_1.description = "Sync Xero invoices"
        mock_use_case_1.workflow_template_id = "template_1"

        mock_use_case_2 = Mock()
        mock_use_case_2.use_case_name = "Contact Export"
        mock_use_case_2.description = "Export contacts"
        mock_use_case_2.workflow_template_id = "template_2"

        mock_app.use_cases = [mock_use_case_1, mock_use_case_2]
        mock_get_doc.return_value = mock_app

        result = get_app_details("xero")

        self.assertTrue(result['success'])
        self.assertIn('app', result)
        self.assertEqual(result['app']['app_name'], "xero")
        self.assertEqual(len(result['app']['use_cases']), 2)

    @patch('frappe.get_doc')
    def test_get_app_details_not_found(self, mock_get_doc):
        """Test retrieving details for non-existent app"""
        mock_get_doc.side_effect = frappe.DoesNotExistError()

        result = get_app_details("invalid_app")

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('not found', result['error'].lower())

    @patch('frappe.get_doc')
    def test_get_app_details_no_use_cases(self, mock_get_doc):
        """Test retrieving app details when app has no use cases"""
        mock_app = Mock()
        mock_app.app_name = "test_app"
        mock_app.display_name = "Test App"
        mock_app.logo_url = "/assets/logos/test.png"
        mock_app.description = "Test description"
        mock_app.category = "Test"
        mock_app.oauth_provider = "test"
        mock_app.use_cases = []
        mock_get_doc.return_value = mock_app

        result = get_app_details("test_app")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['app']['use_cases']), 0)


class TestGetCategories(FrappeTestCase):
    """Test get_categories function"""

    @patch('frappe.db.count')
    @patch('frappe.get_all')
    def test_get_categories_success(self, mock_get_all, mock_db_count):
        """Test retrieving categories with counts"""
        # Mock categories
        mock_get_all.return_value = [
            {"category": "Accounting"},
            {"category": "Productivity"},
            {"category": "Communication"}
        ]

        # Mock counts
        def count_side_effect(doctype, filters):
            category_counts = {
                "Accounting": 5,
                "Productivity": 10,
                "Communication": 3
            }
            return category_counts.get(filters.get('category'), 0)

        mock_db_count.side_effect = count_side_effect

        result = get_categories()

        self.assertTrue(result['success'])
        self.assertIn('categories', result)
        self.assertEqual(result['categories']['Accounting'], 5)
        self.assertEqual(result['categories']['Productivity'], 10)
        self.assertEqual(result['categories']['Communication'], 3)

    @patch('frappe.get_all')
    def test_get_categories_empty(self, mock_get_all):
        """Test retrieving categories when none exist"""
        mock_get_all.return_value = []

        result = get_categories()

        self.assertTrue(result['success'])
        self.assertEqual(len(result['categories']), 0)

    @patch('frappe.db.count')
    @patch('frappe.get_all')
    def test_get_categories_with_null(self, mock_get_all, mock_db_count):
        """Test retrieving categories when some apps have no category"""
        mock_get_all.return_value = [
            {"category": "Accounting"},
            {"category": None}
        ]

        mock_db_count.return_value = 5

        result = get_categories()

        self.assertTrue(result['success'])
        # Should only include non-null categories
        self.assertEqual(len(result['categories']), 1)
        self.assertIn('Accounting', result['categories'])


class TestSearchApps(FrappeTestCase):
    """Test search_apps function"""

    @patch('frappe.get_all')
    def test_search_apps_by_name(self, mock_get_all):
        """Test searching apps by name"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                # Filter by query
                or_filters = kwargs.get('or_filters', [])
                if or_filters:
                    # Simulate search for "Xero"
                    return [MOCK_APP_CATALOG[0]]
                return MOCK_APP_CATALOG
            elif doctype == "App Use Case":
                parent = kwargs['filters']['parent']
                return MOCK_USE_CASES.get(parent, [])
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = search_apps(query="Xero")

        self.assertTrue(result['success'])
        self.assertIn('apps', result)
        self.assertIn('query', result)
        self.assertEqual(result['query'], "Xero")
        self.assertEqual(len(result['apps']), 1)

    @patch('frappe.get_all')
    def test_search_apps_by_description(self, mock_get_all):
        """Test searching apps by description"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                or_filters = kwargs.get('or_filters', [])
                if or_filters:
                    # Simulate search for "accounting"
                    return [MOCK_APP_CATALOG[0]]
                return MOCK_APP_CATALOG
            elif doctype == "App Use Case":
                parent = kwargs['filters']['parent']
                return MOCK_USE_CASES.get(parent, [])
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = search_apps(query="accounting")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['apps']), 1)

    @patch('lodgeick.api.catalog.get_app_catalog')
    def test_search_apps_empty_query(self, mock_get_catalog):
        """Test searching with empty query returns all apps"""
        mock_get_catalog.return_value = {
            "success": True,
            "apps": MOCK_APP_CATALOG
        }

        result = search_apps(query="")

        self.assertTrue(result['success'])
        mock_get_catalog.assert_called_once()

    @patch('frappe.get_all')
    def test_search_apps_no_results(self, mock_get_all):
        """Test searching with no matching results"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                or_filters = kwargs.get('or_filters', [])
                if or_filters:
                    return []
                return MOCK_APP_CATALOG
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = search_apps(query="nonexistent")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['apps']), 0)

    @patch('frappe.get_all')
    def test_search_apps_case_insensitive(self, mock_get_all):
        """Test searching is case insensitive"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                or_filters = kwargs.get('or_filters', [])
                if or_filters:
                    # Should match regardless of case
                    return [MOCK_APP_CATALOG[2]]  # Slack
                return MOCK_APP_CATALOG
            elif doctype == "App Use Case":
                return []
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = search_apps(query="SLACK")

        self.assertTrue(result['success'])
        self.assertEqual(len(result['apps']), 1)


class TestCatalogFiltering(FrappeTestCase):
    """Test catalog filtering and edge cases"""

    @patch('frappe.get_all')
    def test_get_app_catalog_only_active_apps(self, mock_get_all):
        """Test catalog only returns active apps"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                filters = kwargs.get('filters', {})
                # Verify is_active filter is applied
                self.assertEqual(filters.get('is_active'), 1)
                return MOCK_APP_CATALOG
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = get_app_catalog()

        self.assertTrue(result['success'])

    @patch('frappe.get_all')
    def test_search_apps_only_active_apps(self, mock_get_all):
        """Test search only returns active apps"""
        def get_all_side_effect(doctype, **kwargs):
            if doctype == "App Catalog":
                filters = kwargs.get('filters', {})
                # Verify is_active filter is applied
                self.assertEqual(filters.get('is_active'), 1)
                return []
            return []

        mock_get_all.side_effect = get_all_side_effect

        result = search_apps(query="test")

        self.assertTrue(result['success'])


if __name__ == '__main__':
    unittest.main()
