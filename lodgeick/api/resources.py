"""
Resources API for Lodgeick
Fetches available resources from n8n node definitions
Uses n8n's node parameter structure to get resource types
"""

import frappe
from frappe import _
from lodgeick.services.n8n_client import get_n8n_client


@frappe.whitelist()
def get_app_templates(app_id):
	"""
	Get available workflow templates for an app
	Templates are pre-built n8n workflows like "Email triage agent"

	Args:
		app_id: The app identifier (e.g., 'gmail', 'google_sheets')

	Returns:
		dict: List of available templates and custom integration option
	"""
	user = frappe.session.user

	# Check if user has this app connected (has Integration Token)
	token = frappe.db.get_value(
		"Integration Token",
		{
			"user": user,
			"provider": app_id
		},
		["name", "provider"],
		as_dict=True
	)

	if not token:
		return {
			"success": False,
			"error": f"App '{app_id}' is not connected. Please connect it from the integrations page."
		}

	try:
		# Get templates from n8n or use fallback
		templates = get_app_template_list(app_id)

		return {
			"success": True,
			"app_id": app_id,
			"templates": templates
		}

	except Exception as e:
		frappe.log_error(f"Error fetching templates for {app_id}: {str(e)[:200]}", "Template Discovery Error")
		return {
			"success": True,
			"app_id": app_id,
			"templates": get_app_template_list(app_id)
		}


@frappe.whitelist()
def get_app_resources(app_id):
	"""
	Get available resource types for an app from n8n node definition

	Args:
		app_id: The app identifier (e.g., 'gmail', 'google_sheets')

	Returns:
		dict: List of available resource types (e.g., 'message', 'draft', 'label')
	"""
	user = frappe.session.user

	# Check if user has this app connected (has Integration Token)
	token = frappe.db.get_value(
		"Integration Token",
		{
			"user": user,
			"provider": app_id
		},
		["name", "provider"],
		as_dict=True
	)

	if not token:
		return {
			"success": False,
			"error": f"App '{app_id}' is not connected. Please connect it from the integrations page."
		}

	try:
		# Get n8n node type for this app
		node_type = get_node_type_for_app(app_id)

		if not node_type:
			# Fallback to static resources
			resources = get_fallback_resources(app_id)
			return {
				"success": True,
				"app_id": app_id,
				"resources": resources
			}

		# Query n8n for node definition
		n8n = get_n8n_client()

		if not n8n.is_enabled():
			# n8n not available, use fallback
			resources = get_fallback_resources(app_id)
			return {
				"success": True,
				"app_id": app_id,
				"resources": resources
			}

		# Get node type definition from n8n
		node_def = n8n.get_node_type(node_type)

		# Extract resource options from node definition
		resources = extract_resources_from_node(node_def, app_id)

		return {
			"success": True,
			"app_id": app_id,
			"resources": resources
		}

	except Exception as e:
		frappe.log_error(f"Error fetching resources for {app_id}: {str(e)[:200]}", "Resource Discovery Error")
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

	# Check if user has this app connected (has Integration Token)
	token = frappe.db.get_value(
		"Integration Token",
		{
			"user": user,
			"provider": app_id
		},
		["name", "provider"],
		as_dict=True
	)

	if not token:
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


def get_node_type_for_app(app_id):
	"""
	Map app ID to n8n node type name
	Uses latest n8n node versions
	"""
	node_types = {
		"gmail": "n8n-nodes-base.gmail",
		"google_sheets": "n8n-nodes-base.googleSheets",
		"google_drive": "n8n-nodes-base.googleDrive",
		"slack": "n8n-nodes-base.slack",
		"salesforce": "n8n-nodes-base.salesforce",
		"hubspot": "n8n-nodes-base.hubSpot",
		"jira": "n8n-nodes-base.jira",
		"xero": "n8n-nodes-base.xero",
		"notion": "n8n-nodes-base.notion",
		"mailchimp": "n8n-nodes-base.mailchimp",
		"airtable": "n8n-nodes-base.airtable"
	}
	return node_types.get(app_id)


def extract_resources_from_node(node_def, app_id):
	"""
	Extract available resource types from n8n node definition

	Args:
		node_def: n8n node type definition
		app_id: App identifier for context

	Returns:
		list: Resource options with id, name, type
	"""
	try:
		# n8n node definitions have a 'properties' array
		properties = node_def.get("properties", [])

		# Find the 'resource' parameter
		resource_param = None
		for prop in properties:
			if prop.get("name") == "resource" or prop.get("displayName") == "Resource":
				resource_param = prop
				break

		if not resource_param or "options" not in resource_param:
			# No resource parameter found, use fallback
			return get_fallback_resources(app_id)

		# Extract resource options
		resources = []
		for option in resource_param.get("options", []):
			resource = {
				"id": option.get("value", option.get("name", "")),
				"name": option.get("name", option.get("value", "")),
				"type": "resource",
				"description": option.get("description", "")
			}
			resources.append(resource)

		return resources if resources else get_fallback_resources(app_id)

	except Exception as e:
		frappe.logger().error(f"Failed to extract resources from node definition: {str(e)[:200]}")
		return get_fallback_resources(app_id)


def get_fallback_resources(app_id):
	"""
	Fallback resources when n8n discovery not available
	These are n8n resource types, not specific instances
	"""
	fallbacks = {
		"gmail": [
			{"id": "message", "name": "Message", "type": "resource", "description": "Get, send, and delete emails"},
			{"id": "draft", "name": "Draft", "type": "resource", "description": "Manage email drafts"},
			{"id": "label", "name": "Label", "type": "resource", "description": "Manage labels"},
			{"id": "thread", "name": "Thread", "type": "resource", "description": "Manage email threads"}
		],
		"google_sheets": [
			{"id": "sheet", "name": "Sheet", "type": "resource", "description": "Manage spreadsheet rows"},
			{"id": "spreadsheet", "name": "Spreadsheet", "type": "resource", "description": "Manage spreadsheets"}
		],
		"slack": [
			{"id": "channel", "name": "Channel", "type": "resource", "description": "Manage channels"},
			{"id": "message", "name": "Message", "type": "resource", "description": "Send and manage messages"},
			{"id": "user", "name": "User", "type": "resource", "description": "Manage users"}
		],
		"salesforce": [
			{"id": "contact", "name": "Contact", "type": "resource", "description": "Manage contacts"},
			{"id": "account", "name": "Account", "type": "resource", "description": "Manage accounts"},
			{"id": "lead", "name": "Lead", "type": "resource", "description": "Manage leads"},
			{"id": "opportunity", "name": "Opportunity", "type": "resource", "description": "Manage opportunities"}
		],
		"hubspot": [
			{"id": "contact", "name": "Contact", "type": "resource", "description": "Manage contacts"},
			{"id": "company", "name": "Company", "type": "resource", "description": "Manage companies"},
			{"id": "deal", "name": "Deal", "type": "resource", "description": "Manage deals"}
		],
		"jira": [
			{"id": "issue", "name": "Issue", "type": "resource", "description": "Manage issues"},
			{"id": "project", "name": "Project", "type": "resource", "description": "Manage projects"}
		],
		"xero": [
			{"id": "contact", "name": "Contact", "type": "resource", "description": "Manage contacts"},
			{"id": "invoice", "name": "Invoice", "type": "resource", "description": "Manage invoices"}
		],
		"mailchimp": [
			{"id": "list", "name": "List", "type": "resource", "description": "Manage lists"},
			{"id": "member", "name": "Member", "type": "resource", "description": "Manage list members"}
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


def get_app_template_list(app_id):
	"""
	Get list of available workflow templates for an app
	Includes pre-built templates and custom integration option
	"""
	templates = {
		"gmail": [
			{
				"id": "email_triage_agent",
				"name": "Email triage agent",
				"description": "Categorizes new, unread emails by analyzing their content and applying relevant labels.",
				"type": "template",
				"triggers": ["New email received"],
				"actions": ["Analyze content", "Apply labels"]
			},
			{
				"id": "custom",
				"name": "Custom Integration",
				"description": "Build your own workflow with Gmail",
				"type": "custom"
			}
		],
		"google_sheets": [
			{
				"id": "custom",
				"name": "Custom Integration",
				"description": "Build your own workflow with Google Sheets",
				"type": "custom"
			}
		],
		"slack": [
			{
				"id": "custom",
				"name": "Custom Integration",
				"description": "Build your own workflow with Slack",
				"type": "custom"
			}
		]
	}

	# All apps should have at least a custom option
	return templates.get(app_id, [
		{
			"id": "custom",
			"name": "Custom Integration",
			"description": f"Build your own workflow with {app_id}",
			"type": "custom"
		}
	])
