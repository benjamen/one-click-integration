"""
Test fixtures and mock data for Lodgeick tests
"""

# Mock OAuth provider configurations
MOCK_PROVIDER_CONFIGS = {
    "google": {
        "client_id": "test_google_client_id",
        "client_secret": "test_google_client_secret",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scope": "https://www.googleapis.com/auth/gmail.readonly"
    },
    "xero": {
        "client_id": "test_xero_client_id",
        "client_secret": "test_xero_client_secret",
        "auth_url": "https://login.xero.com/identity/connect/authorize",
        "token_url": "https://identity.xero.com/connect/token",
        "scope": "accounting.transactions offline_access"
    },
    "slack": {
        "client_id": "test_slack_client_id",
        "client_secret": "test_slack_client_secret",
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scope": "channels:read chat:write"
    }
}

# Mock OAuth tokens
MOCK_OAUTH_TOKENS = {
    "access_token": "test_access_token_12345",
    "refresh_token": "test_refresh_token_67890",
    "expires_in": 3600,
    "token_type": "Bearer"
}

# Mock OAuth state
MOCK_OAUTH_STATE = {
    "provider": "google",
    "user": "test@example.com",
    "redirect_uri": "/app"
}

# Mock App Catalog data
MOCK_APP_CATALOG = [
    {
        "name": "xero",
        "app_name": "xero",
        "display_name": "Xero",
        "logo_url": "/assets/logos/xero.png",
        "description": "Cloud accounting software",
        "category": "Accounting",
        "oauth_provider": "xero",
        "is_active": 1
    },
    {
        "name": "google_sheets",
        "app_name": "google_sheets",
        "display_name": "Google Sheets",
        "logo_url": "/assets/logos/google_sheets.png",
        "description": "Cloud spreadsheet application",
        "category": "Productivity",
        "oauth_provider": "google",
        "is_active": 1
    },
    {
        "name": "slack",
        "app_name": "slack",
        "display_name": "Slack",
        "logo_url": "/assets/logos/slack.png",
        "description": "Team communication platform",
        "category": "Communication",
        "oauth_provider": "slack",
        "is_active": 1
    }
]

# Mock App Use Cases
MOCK_USE_CASES = {
    "xero": [
        {
            "use_case_name": "Invoice Sync",
            "description": "Sync Xero invoices to Google Sheets",
            "workflow_template_id": "template_invoice_sync"
        },
        {
            "use_case_name": "Contact Export",
            "description": "Export Xero contacts",
            "workflow_template_id": "template_contact_export"
        }
    ],
    "google_sheets": [
        {
            "use_case_name": "Data Import",
            "description": "Import data from sheets",
            "workflow_template_id": "template_data_import"
        }
    ]
}

# Mock User Integration
MOCK_USER_INTEGRATION = {
    "doctype": "User Integration",
    "user": "test@example.com",
    "flow_name": "Invoice Sync",
    "source_app": "xero",
    "target_app": "google_sheets",
    "workflow_id": "workflow_12345",
    "status": "Active"
}

# Mock Google AI Intent Response
MOCK_AI_INTENT_RESPONSE = {
    "success": True,
    "apis": [
        {
            "name": "gmail",
            "display_name": "Gmail API",
            "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
            "description": "Read emails from Gmail"
        },
        {
            "name": "sheets",
            "display_name": "Google Sheets API",
            "scopes": ["https://www.googleapis.com/auth/spreadsheets"],
            "description": "Read and write spreadsheets"
        }
    ],
    "billing_required": False,
    "billing_apis": [],
    "reasoning": "User wants to sync Gmail to Sheets, requires both APIs",
    "next_step": "project_setup"
}

# Mock Google Project
MOCK_GOOGLE_PROJECT = {
    "project_id": "test-project-123456",
    "project_name": "Test Project",
    "status": "Complete",
    "apis_enabled": ["gmail", "sheets"],
    "oauth_client_id": "test_client_id"
}

# Mock n8n workflow
MOCK_N8N_WORKFLOW = {
    "id": "workflow_abc123",
    "name": "Test Workflow",
    "active": True,
    "nodes": []
}

# Mock Integration Log
MOCK_INTEGRATION_LOG = {
    "doctype": "Integration Log",
    "integration": "INT-0001",
    "status": "Success",
    "message": "Integration executed successfully",
    "execution_time": 1.23
}
