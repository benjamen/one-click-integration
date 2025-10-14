"""
Resources API for Lodgeick
Fetches available resources (mailboxes, tables, objects) from connected apps
"""

import frappe
from frappe import _


@frappe.whitelist()
def get_app_resources(app_id):
	"""
	Get available resources for a connected app

	Args:
		app_id: The app identifier (e.g., 'gmail', 'google_sheets')

	Returns:
		dict: List of available resources for the app
	"""
	user = frappe.session.user

	# Check if user has this app connected
	connection = frappe.db.get_value(
		"App Connection",
		{
			"user": user,
			"app_id": app_id,
			"is_active": 1
		},
		["name", "access_token", "refresh_token"],
		as_dict=True
	)

	if not connection:
		return {
			"success": False,
			"error": f"App '{app_id}' is not connected for this user"
		}

	try:
		# Fetch resources based on app type
		resources = []

		if app_id == "gmail":
			resources = get_gmail_mailboxes(connection)
		elif app_id == "google_sheets":
			resources = get_google_sheets_spreadsheets(connection)
		elif app_id == "salesforce":
			resources = get_salesforce_objects(connection)
		elif app_id == "hubspot":
			resources = get_hubspot_objects(connection)
		elif app_id == "slack":
			resources = get_slack_channels(connection)
		elif app_id == "xero":
			resources = get_xero_resources(connection)
		elif app_id == "mailchimp":
			resources = get_mailchimp_lists(connection)
		elif app_id == "jira":
			resources = get_jira_projects(connection)
		else:
			return {
				"success": False,
				"error": f"Unsupported app type: {app_id}"
			}

		return {
			"success": True,
			"app_id": app_id,
			"resources": resources
		}

	except Exception as e:
		frappe.log_error(f"Error fetching resources for {app_id}: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


def get_gmail_mailboxes(connection):
	"""Get Gmail mailboxes/labels"""
	# TODO: Implement actual Gmail API call using connection.access_token
	# For now, return structure for frontend to implement
	return [
		{"id": "INBOX", "name": "Inbox", "type": "mailbox"},
		{"id": "SENT", "name": "Sent Mail", "type": "mailbox"},
		{"id": "DRAFT", "name": "Drafts", "type": "mailbox"},
		{"id": "STARRED", "name": "Starred", "type": "label"}
	]


def get_google_sheets_spreadsheets(connection):
	"""Get Google Sheets spreadsheets"""
	# TODO: Implement actual Google Sheets API call
	return []


def get_salesforce_objects(connection):
	"""Get Salesforce objects"""
	# TODO: Implement actual Salesforce API call
	return []


def get_hubspot_objects(connection):
	"""Get HubSpot objects"""
	# TODO: Implement actual HubSpot API call
	return []


def get_slack_channels(connection):
	"""Get Slack channels"""
	# TODO: Implement actual Slack API call
	return []


def get_xero_resources(connection):
	"""Get Xero resources"""
	# TODO: Implement actual Xero API call
	return []


def get_mailchimp_lists(connection):
	"""Get Mailchimp lists"""
	# TODO: Implement actual Mailchimp API call
	return []


def get_jira_projects(connection):
	"""Get Jira projects"""
	# TODO: Implement actual Jira API call
	return []


@frappe.whitelist()
def get_resource_fields(app_id, resource_id):
	"""
	Get available fields/columns for a specific resource

	Args:
		app_id: The app identifier
		resource_id: The resource identifier (e.g., mailbox id, spreadsheet id)

	Returns:
		dict: List of available fields for the resource
	"""
	user = frappe.session.user

	# Check if user has this app connected
	connection = frappe.db.get_value(
		"App Connection",
		{
			"user": user,
			"app_id": app_id,
			"is_active": 1
		},
		["name", "access_token", "refresh_token"],
		as_dict=True
	)

	if not connection:
		return {
			"success": False,
			"error": f"App '{app_id}' is not connected for this user"
		}

	try:
		# Fetch fields based on app type and resource
		fields = []

		if app_id == "gmail":
			fields = get_gmail_fields(resource_id)
		elif app_id == "google_sheets":
			fields = get_google_sheets_fields(connection, resource_id)
		elif app_id == "salesforce":
			fields = get_salesforce_fields(connection, resource_id)
		elif app_id == "hubspot":
			fields = get_hubspot_fields(connection, resource_id)
		else:
			# Generic fields for other apps
			fields = [
				{"id": "id", "name": "ID", "type": "string"},
				{"id": "name", "name": "Name", "type": "string"},
				{"id": "created_at", "name": "Created At", "type": "datetime"}
			]

		return {
			"success": True,
			"app_id": app_id,
			"resource_id": resource_id,
			"fields": fields
		}

	except Exception as e:
		frappe.log_error(f"Error fetching fields for {app_id}/{resource_id}: {str(e)}")
		return {
			"success": False,
			"error": str(e)
		}


def get_gmail_fields(mailbox_id):
	"""Get fields available in Gmail messages"""
	return [
		{"id": "from", "name": "From", "type": "email"},
		{"id": "to", "name": "To", "type": "email"},
		{"id": "subject", "name": "Subject", "type": "string"},
		{"id": "body", "name": "Body", "type": "text"},
		{"id": "date", "name": "Date", "type": "datetime"},
		{"id": "labels", "name": "Labels", "type": "array"}
	]


def get_google_sheets_fields(connection, spreadsheet_id):
	"""Get columns from a Google Sheets spreadsheet"""
	# TODO: Implement actual Google Sheets API call to get headers
	return []


def get_salesforce_fields(connection, object_name):
	"""Get fields from a Salesforce object"""
	# TODO: Implement actual Salesforce API call
	return []


def get_hubspot_fields(connection, object_type):
	"""Get fields from a HubSpot object"""
	# TODO: Implement actual HubSpot API call
	return []
