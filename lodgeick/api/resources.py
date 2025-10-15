"""
Resources API for Lodgeick
Fetches available resources (mailboxes, tables, objects) from connected apps using n8n
"""

import frappe
from frappe import _
from lodgeick.services.n8n_client import get_n8n_client


@frappe.whitelist()
def get_app_resources(app_id):
	"""
	Get available resources for a connected app using n8n's resource discovery

	Args:
		app_id: The app identifier (e.g., 'gmail', 'google_sheets')

	Returns:
		dict: List of available resources for the app
	"""
	user = frappe.session.user

	# Check if user has this app connected with n8n credential
	connection = frappe.db.get_value(
		"App Connection",
		{
			"user": user,
			"app_id": app_id,
			"is_active": 1
		},
		["name", "n8n_credential_id"],
		as_dict=True
	)

	if not connection:
		return {
			"success": False,
			"error": f"App '{app_id}' is not connected. Please connect it from the integrations page."
		}

	if not connection.get("n8n_credential_id"):
		return {
			"success": False,
			"error": f"App '{app_id}' credential not synced to n8n yet. Please try again."
		}

	try:
		# Get n8n node configuration for this app
		node_config = get_app_n8n_config(app_id)

		if not node_config:
			# Fallback to hardcoded resources for apps without n8n discovery
			resources = get_fallback_resources(app_id)
			return {
				"success": True,
				"app_id": app_id,
				"resources": resources
			}

		# Use n8n dynamic parameter loading
		n8n = get_n8n_client()
		options = n8n.get_node_parameter_options(
			node_type=node_config["node_type"],
			method_name=node_config["resource_method"],
			credential_id=connection.n8n_credential_id
		)

		# Transform n8n options to our format
		resources = transform_n8n_options(options, app_id)

		return {
			"success": True,
			"app_id": app_id,
			"resources": resources
		}

	except Exception as e:
		frappe.log_error(f"Error fetching resources for {app_id}: {str(e)}", "Resource Discovery Error")
		# Return fallback resources on error
		return {
			"success": True,
			"app_id": app_id,
			"resources": get_fallback_resources(app_id)
		}


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
		["name", "n8n_credential_id"],
		as_dict=True
	)

	if not connection:
		return {
			"success": False,
			"error": f"App '{app_id}' is not connected for this user"
		}

	try:
		# Get field schema from n8n or use fallback
		fields = get_app_fields_schema(app_id, resource_id)

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


def get_app_n8n_config(app_id):
	"""
	Get n8n node type and resource method for an app

	Returns:
		dict: Configuration for n8n resource discovery
	"""
	configs = {
		"gmail": {
			"node_type": "n8n-nodes-base.gmail",
			"resource_method": "getLabels"
		},
		"google_sheets": {
			"node_type": "n8n-nodes-base.googleSheets",
			"resource_method": "getSheets"
		},
		"slack": {
			"node_type": "n8n-nodes-base.slack",
			"resource_method": "getChannels"
		},
		"salesforce": {
			"node_type": "n8n-nodes-base.salesforce",
			"resource_method": "getCustomObjects"
		},
		"hubspot": {
			"node_type": "n8n-nodes-base.hubspot",
			"resource_method": "getObjects"
		},
		"jira": {
			"node_type": "n8n-nodes-base.jira",
			"resource_method": "getProjects"
		}
	}
	return configs.get(app_id)


def transform_n8n_options(options, app_id):
	"""
	Transform n8n option format to Lodgeick resource format

	Args:
		options: n8n options array [{"name": "...", "value": "..."}]
		app_id: App identifier for context

	Returns:
		list: Transformed resources
	"""
	resources = []

	for option in options:
		resource = {
			"id": option.get("value", option.get("name")),
			"name": option.get("name", option.get("value")),
			"type": get_resource_type(app_id)
		}
		resources.append(resource)

	return resources


def get_resource_type(app_id):
	"""Get display type for resources"""
	types = {
		"gmail": "mailbox",
		"google_sheets": "spreadsheet",
		"slack": "channel",
		"salesforce": "object",
		"hubspot": "object",
		"jira": "project",
		"xero": "organization",
		"mailchimp": "list"
	}
	return types.get(app_id, "resource")


def get_fallback_resources(app_id):
	"""
	Fallback resources when n8n discovery not available
	Returns common/default resources for each app
	"""
	fallbacks = {
		"gmail": [
			{"id": "INBOX", "name": "Inbox", "type": "mailbox"},
			{"id": "SENT", "name": "Sent Mail", "type": "mailbox"},
			{"id": "DRAFT", "name": "Drafts", "type": "mailbox"},
			{"id": "STARRED", "name": "Starred", "type": "label"},
			{"id": "SPAM", "name": "Spam", "type": "mailbox"},
			{"id": "TRASH", "name": "Trash", "type": "mailbox"}
		],
		"google_sheets": [
			{"id": "spreadsheets", "name": "My Spreadsheets", "type": "spreadsheet"}
		],
		"slack": [
			{"id": "general", "name": "#general", "type": "channel"}
		],
		"salesforce": [
			{"id": "Contact", "name": "Contacts", "type": "object"},
			{"id": "Account", "name": "Accounts", "type": "object"},
			{"id": "Lead", "name": "Leads", "type": "object"},
			{"id": "Opportunity", "name": "Opportunities", "type": "object"}
		],
		"hubspot": [
			{"id": "contacts", "name": "Contacts", "type": "object"},
			{"id": "companies", "name": "Companies", "type": "object"},
			{"id": "deals", "name": "Deals", "type": "object"}
		],
		"jira": [
			{"id": "default", "name": "My Projects", "type": "project"}
		],
		"xero": [
			{"id": "default", "name": "My Organization", "type": "organization"}
		],
		"mailchimp": [
			{"id": "default", "name": "My Lists", "type": "list"}
		]
	}
	return fallbacks.get(app_id, [])


def get_app_fields_schema(app_id, resource_id):
	"""
	Get field schema for an app's resource
	Returns common fields for each app type
	"""
	schemas = {
		"gmail": [
			{"id": "from", "name": "From", "type": "email"},
			{"id": "to", "name": "To", "type": "email"},
			{"id": "subject", "name": "Subject", "type": "string"},
			{"id": "body", "name": "Body", "type": "text"},
			{"id": "date", "name": "Date", "type": "datetime"},
			{"id": "labels", "name": "Labels", "type": "array"},
			{"id": "attachments", "name": "Attachments", "type": "array"}
		],
		"google_sheets": [
			{"id": "row_number", "name": "Row Number", "type": "number"},
			{"id": "column_a", "name": "Column A", "type": "string"},
			{"id": "column_b", "name": "Column B", "type": "string"},
			{"id": "column_c", "name": "Column C", "type": "string"}
		],
		"slack": [
			{"id": "text", "name": "Message Text", "type": "string"},
			{"id": "user", "name": "User", "type": "string"},
			{"id": "timestamp", "name": "Timestamp", "type": "datetime"},
			{"id": "channel", "name": "Channel", "type": "string"}
		],
		"salesforce": [
			{"id": "Id", "name": "ID", "type": "string"},
			{"id": "Name", "name": "Name", "type": "string"},
			{"id": "Email", "name": "Email", "type": "email"},
			{"id": "Phone", "name": "Phone", "type": "string"},
			{"id": "CreatedDate", "name": "Created Date", "type": "datetime"}
		],
		"hubspot": [
			{"id": "id", "name": "ID", "type": "string"},
			{"id": "firstname", "name": "First Name", "type": "string"},
			{"id": "lastname", "name": "Last Name", "type": "string"},
			{"id": "email", "name": "Email", "type": "email"},
			{"id": "createdate", "name": "Created Date", "type": "datetime"}
		],
		"jira": [
			{"id": "key", "name": "Issue Key", "type": "string"},
			{"id": "summary", "name": "Summary", "type": "string"},
			{"id": "description", "name": "Description", "type": "text"},
			{"id": "status", "name": "Status", "type": "string"},
			{"id": "assignee", "name": "Assignee", "type": "string"}
		]
	}

	return schemas.get(app_id, [
		{"id": "id", "name": "ID", "type": "string"},
		{"id": "name", "name": "Name", "type": "string"},
		{"id": "created_at", "name": "Created At", "type": "datetime"}
	])
