#!/usr/bin/env python3
"""
Create test data for Lodgeick to test the UI
Run with: bench --site home.localhost console < create_test_data.py
"""

import frappe
import json
from datetime import datetime

def create_test_data():
	"""Create test Integration Tokens and User Integrations"""

	# Get current user (or use a specific user)
	user = frappe.session.user
	if user == "Guest":
		user = "Administrator"

	print(f"Creating test data for user: {user}")

	# Create Integration Tokens for Gmail and Google Sheets
	providers = [
		{
			"provider": "gmail",
			"access_token": "test_gmail_token_123",
			"refresh_token": "test_gmail_refresh_456",
		},
		{
			"provider": "google_sheets",
			"access_token": "test_sheets_token_789",
			"refresh_token": "test_sheets_refresh_012",
		},
		{
			"provider": "slack",
			"access_token": "test_slack_token_345",
			"refresh_token": "test_slack_refresh_678",
		}
	]

	created_tokens = []
	for provider_data in providers:
		# Check if token already exists
		existing = frappe.db.exists("Integration Token", {
			"user": user,
			"provider": provider_data["provider"]
		})

		if existing:
			print(f"✓ Integration Token for {provider_data['provider']} already exists")
			created_tokens.append(provider_data["provider"])
			continue

		# Create token
		token = frappe.get_doc({
			"doctype": "Integration Token",
			"user": user,
			"provider": provider_data["provider"],
			"access_token": provider_data["access_token"],
			"refresh_token": provider_data["refresh_token"],
			"expires_at": datetime.now(),
			"token_data": json.dumps({
				"scope": "full",
				"token_type": "Bearer"
			})
		})
		token.insert()
		frappe.db.commit()
		created_tokens.append(provider_data["provider"])
		print(f"✓ Created Integration Token for {provider_data['provider']}")

	# Create a test User Integration (workflow)
	existing_integration = frappe.db.exists("User Integration", {
		"user": user,
		"flow_name": "Test Gmail to Sheets Sync"
	})

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
			"flow_name": "Test Gmail to Sheets Sync",
			"source_app": "gmail",
			"target_app": "google_sheets",
			"config": json.dumps(config),
			"workflow_id": "test_workflow_12345",
			"status": "Active",
			"last_run": datetime.now()
		})
		integration.insert()
		frappe.db.commit()
		print("✓ Created test User Integration")
	else:
		print("✓ Test User Integration already exists")

	print("\n" + "="*60)
	print("TEST DATA CREATED SUCCESSFULLY!")
	print("="*60)
	print(f"\nConnected Apps: {len(created_tokens)}")
	print(f"Apps: {', '.join(created_tokens)}")
	print("\nActive Integrations: 1")
	print("Integration: Gmail to Sheets Sync")
	print("\n" + "="*60)
	print("\nNow refresh your dashboard at:")
	print("http://localhost:5173/dashboard")
	print("\nYou should see:")
	print("- Connected Apps: 3")
	print("- Active Integrations: 1")
	print("- Data Synced Today: 0 (will need real n8n)")
	print("="*60)

if __name__ == "__main__":
	create_test_data()
