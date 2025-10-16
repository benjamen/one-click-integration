"""
Resources API for Lodgeick
Fetches available resources from n8n node definitions
Uses n8n's node parameter structure to get resource types
"""

import frappe
from frappe import _
from lodgeick.services.n8n_client import get_n8n_client
from lodgeick.services.n8n_cache import (
	get_cached_node_types,
	set_cached_node_types,
	get_cached_node_definition,
	set_cached_node_definition
)


@frappe.whitelist()
def get_available_apps():
	"""
	Get list of available apps from n8n node types
	Caches results for 24 hours

	Returns:
		dict: List of apps with icons, names, descriptions
	"""
	try:
		# Try to get from cache first
		cached_apps = get_cached_node_types()

		if cached_apps:
			frappe.logger().info(f"Loaded {len(cached_apps)} apps from cache")
			return {
				"success": True,
				"apps": cached_apps,
				"from_cache": True
			}

		# Fetch from n8n
		n8n = get_n8n_client()

		if not n8n.is_enabled():
			# n8n not available, use fallback
			apps = get_fallback_app_list()
			return {
				"success": True,
				"apps": apps,
				"from_cache": False,
				"fallback": True
			}

		# Get all node types from n8n
		node_types = n8n.get_node_types()

		# Filter and transform to app list
		apps = extract_apps_from_nodes(node_types)

		# Cache the results
		set_cached_node_types(apps)

		frappe.logger().info(f"Fetched {len(apps)} apps from n8n")

		return {
			"success": True,
			"apps": apps,
			"from_cache": False
		}

	except Exception as e:
		frappe.log_error(f"Error fetching available apps: {str(e)[:200]}", "App Discovery Error")
		return {
			"success": True,
			"apps": get_fallback_app_list(),
			"from_cache": False,
			"fallback": True,
			"error": str(e)[:200]
		}


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


def extract_apps_from_nodes(node_types):
	"""
	Extract app list from n8n node types
	Filters for trigger/regular nodes and formats for Lodgeick UI

	Args:
		node_types: List of n8n node type objects

	Returns:
		list: App objects with id, name, icon, description
	"""
	apps = []
	app_icons = get_app_icons()

	# Filter for integration nodes (not core nodes like Set, If, etc.)
	for node in node_types:
		node_name = node.get("name", "")
		display_name = node.get("displayName", "")
		description = node.get("description", "")

		# Skip core/utility nodes
		if not node_name.startswith("n8n-nodes-base."):
			continue

		# Extract app ID from node name (e.g., "n8n-nodes-base.gmail" -> "gmail")
		app_id = node_name.replace("n8n-nodes-base.", "").lower()

		# Skip utility nodes
		skip_nodes = ["set", "if", "switch", "merge", "split", "function", "code", "http", "webhook", "wait"]
		if app_id in skip_nodes:
			continue

		# Create app object
		app = {
			"id": app_id,
			"name": display_name,
			"description": description or f"Connect to {display_name}",
			"icon": app_icons.get(app_id, "🔗"),
			"node_type": node_name
		}

		apps.append(app)

	# Sort by name
	apps.sort(key=lambda x: x["name"])

	return apps


def get_app_icons():
	"""
	Map app IDs to emoji icons
	"""
	return {
		"gmail": "📧",
		"googlesheets": "📊",
		"googledrive": "📁",
		"slack": "💬",
		"salesforce": "☁️",
		"hubspot": "🎯",
		"jira": "📋",
		"xero": "💰",
		"notion": "📝",
		"mailchimp": "📬",
		"airtable": "🗂️",
		"trello": "📌",
		"asana": "✅",
		"github": "🐙",
		"gitlab": "🦊",
		"stripe": "💳",
		"shopify": "🛍️",
		"wordpress": "📰",
		"zoom": "🎥",
		"calendly": "📅",
		"intercom": "💭",
		"zendesk": "🎫"
	}


def get_fallback_app_list():
	"""
	Fallback app list when n8n is unavailable
	"""
	icons = get_app_icons()

	return [
		{"id": "gmail", "name": "Gmail", "description": "Send and receive emails", "icon": icons.get("gmail", "📧")},
		{"id": "googlesheets", "name": "Google Sheets", "description": "Manage spreadsheets", "icon": icons.get("googlesheets", "📊")},
		{"id": "slack", "name": "Slack", "description": "Send messages and notifications", "icon": icons.get("slack", "💬")},
		{"id": "salesforce", "name": "Salesforce", "description": "Manage CRM data", "icon": icons.get("salesforce", "☁️")},
		{"id": "hubspot", "name": "HubSpot", "description": "Manage contacts and deals", "icon": icons.get("hubspot", "🎯")},
		{"id": "jira", "name": "Jira", "description": "Manage issues and projects", "icon": icons.get("jira", "📋")}
	]


@frappe.whitelist()
def get_resource_operations(app_id, resource_id):
	"""
	Get available operations for a resource (e.g., 'append row', 'update row' for Google Sheets)
	Extracts from n8n node definition based on selected resource

	Args:
		app_id: App identifier
		resource_id: Resource type (e.g., 'sheet', 'message')

	Returns:
		dict: List of operations with id, name, description
	"""
	try:
		# Get node type for app
		node_type = get_node_type_for_app(app_id)

		if not node_type:
			return {
				"success": False,
				"error": "App not supported"
			}

		# Try cache first
		cached_def = get_cached_node_definition(node_type)
		node_def = cached_def

		if not cached_def:
			# Fetch from n8n
			n8n = get_n8n_client()

			if not n8n.is_enabled():
				return {
					"success": True,
					"operations": get_fallback_operations(app_id, resource_id)
				}

			node_def = n8n.get_node_type(node_type)

			# Cache it
			set_cached_node_definition(node_type, node_def)

		# Extract operations for this resource
		operations = extract_operations_from_node(node_def, resource_id)

		return {
			"success": True,
			"app_id": app_id,
			"resource_id": resource_id,
			"operations": operations
		}

	except Exception as e:
		frappe.log_error(f"Error fetching operations for {app_id}/{resource_id}: {str(e)[:200]}")
		return {
			"success": True,
			"operations": get_fallback_operations(app_id, resource_id)
		}


def extract_operations_from_node(node_def, resource_id):
	"""
	Extract available operations for a resource from n8n node definition

	Args:
		node_def: n8n node definition
		resource_id: Resource type (e.g., 'sheet', 'message')

	Returns:
		list: Operations with id, name, description
	"""
	try:
		properties = node_def.get("properties", [])

		# Find the 'operation' parameter
		operation_param = None
		for prop in properties:
			if prop.get("name") == "operation":
				# Check if this operation param is for the correct resource
				display_options = prop.get("displayOptions", {})
				show = display_options.get("show", {})

				# If it has resource filter, check if it matches
				if "resource" in show:
					resource_values = show["resource"]
					if resource_id not in resource_values:
						continue

				operation_param = prop
				break

		if not operation_param or "options" not in operation_param:
			return get_fallback_operations("unknown", resource_id)

		# Extract operations
		operations = []
		for option in operation_param.get("options", []):
			operation = {
				"id": option.get("value", option.get("name", "")),
				"name": option.get("name", option.get("value", "")),
				"description": option.get("description", ""),
				"action": option.get("action", "")
			}
			operations.append(operation)

		return operations

	except Exception as e:
		frappe.logger().error(f"Failed to extract operations: {str(e)[:200]}")
		return get_fallback_operations("unknown", resource_id)


def get_fallback_operations(app_id, resource_id):
	"""
	Fallback operations for common app/resource combinations
	"""
	operations = {
		"googlesheets": {
			"sheet": [
				{"id": "append", "name": "Append Row", "description": "Add a new row to the spreadsheet"},
				{"id": "update", "name": "Update Row", "description": "Update an existing row"},
				{"id": "read", "name": "Read Rows", "description": "Read rows from spreadsheet"},
				{"id": "delete", "name": "Delete Row", "description": "Delete a row from spreadsheet"}
			]
		},
		"gmail": {
			"message": [
				{"id": "send", "name": "Send Email", "description": "Send a new email"},
				{"id": "get", "name": "Get Email", "description": "Get email details"},
				{"id": "getAll", "name": "Get Many Emails", "description": "Get multiple emails"},
				{"id": "delete", "name": "Delete Email", "description": "Delete an email"}
			],
			"draft": [
				{"id": "create", "name": "Create Draft", "description": "Create a new draft"},
				{"id": "get", "name": "Get Draft", "description": "Get draft details"},
				{"id": "delete", "name": "Delete Draft", "description": "Delete a draft"}
			]
		},
		"slack": {
			"message": [
				{"id": "post", "name": "Send Message", "description": "Send a message to a channel"},
				{"id": "update", "name": "Update Message", "description": "Update an existing message"},
				{"id": "delete", "name": "Delete Message", "description": "Delete a message"}
			]
		}
	}

	app_ops = operations.get(app_id, {})
	return app_ops.get(resource_id, [
		{"id": "create", "name": "Create", "description": "Create a new item"},
		{"id": "update", "name": "Update", "description": "Update an existing item"},
		{"id": "read", "name": "Read", "description": "Read items"},
		{"id": "delete", "name": "Delete", "description": "Delete an item"}
	])
