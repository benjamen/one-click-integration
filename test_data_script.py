import frappe
import json
from datetime import datetime

user = "Administrator"

print("\n" + "="*60)
print(f"Creating test data for user: {user}")
print("="*60 + "\n")

# Create Integration Tokens
providers = ["gmail", "google_sheets", "slack"]
for provider in providers:
    existing = frappe.db.exists("Integration Token", {"user": user, "provider": provider})
    if not existing:
        token = frappe.get_doc({
            "doctype": "Integration Token",
            "user": user,
            "provider": provider,
            "access_token": f"test_{provider}_token",
            "refresh_token": f"test_{provider}_refresh",
            "expires_at": datetime.now(),
            "token_data": json.dumps({"scope": "full"})
        })
        token.insert()
        print(f"✓ Created Integration Token for {provider}")
    else:
        print(f"✓ Integration Token for {provider} already exists")

# Create test integration
existing_integration = frappe.db.exists("User Integration", {"user": user, "flow_name": "Test Gmail to Sheets"})
if not existing_integration:
    config = {
        "sourceResource": {"id": "INBOX", "name": "Inbox"},
        "sourceFields": ["from", "subject", "date"],
        "destinationResource": {"id": "spreadsheet_123", "name": "My Spreadsheet"},
        "destinationFields": ["Column A", "Column B", "Column C"],
        "fieldMappings": ["Column A", "Column B", "Column C"],
        "trigger": "schedule",
        "schedule": "hourly"
    }
    integration = frappe.get_doc({
        "doctype": "User Integration",
        "user": user,
        "flow_name": "Test Gmail to Sheets",
        "source_app": "gmail",
        "target_app": "google_sheets",
        "config": json.dumps(config),
        "workflow_id": "test_workflow_12345",
        "status": "Active",
        "last_run": datetime.now()
    })
    integration.insert()
    print("✓ Created test User Integration")
else:
    print("✓ User Integration already exists")

frappe.db.commit()

print("\n" + "="*60)
print("TEST DATA CREATED!")
print("="*60)
print("\nStats:")
print("- Connected Apps: 3 (gmail, google_sheets, slack)")
print("- Active Integrations: 1 (Test Gmail to Sheets)")
print("\n" + "="*60)
print("Refresh your browser at:")
print("http://localhost:5173/dashboard")
print("="*60 + "\n")
