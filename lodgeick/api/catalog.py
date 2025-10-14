"""
App Catalog API for Lodgeick
Provides catalog of available apps and use cases
"""

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_app_catalog(category=None):
	"""
	Get list of available apps

	Args:
		category: Optional category filter

	Returns:
		dict: List of apps with their use cases
	"""
	filters = {"is_active": 1}

	if category:
		filters["category"] = category

	try:
		apps = frappe.get_all(
			"App Catalog",
			filters=filters,
			fields=[
				"name",
				"app_name",
				"display_name",
				"logo_url",
				"description",
				"category",
				"oauth_provider"
			],
			order_by="display_name asc"
		)

		# Skip use cases for now to avoid query hangs
		# for app in apps:
		# 	use_cases = frappe.get_all(
		# 		"App Use Case",
		# 		filters={"parent": app.name},
		# 		fields=["use_case_name", "description", "workflow_template_id"],
		# 		order_by="idx asc"
		# 	)
		# 	app["use_cases"] = use_cases
		for app in apps:
			app["use_cases"] = []

		return {
			"success": True,
			"apps": apps
		}
	except Exception as e:
		frappe.log_error(f"Error in get_app_catalog: {str(e)}")
		return {
			"success": False,
			"error": str(e),
			"apps": []
		}


@frappe.whitelist(allow_guest=True)
def get_app_details(app_name):
	"""
	Get detailed information about an app

	Args:
		app_name: App name

	Returns:
		dict: App details with use cases
	"""
	try:
		app = frappe.get_doc("App Catalog", app_name)

		use_cases = []
		for uc in app.use_cases:
			use_cases.append({
				"use_case_name": uc.use_case_name,
				"description": uc.description,
				"workflow_template_id": uc.workflow_template_id
			})

		return {
			"success": True,
			"app": {
				"app_name": app.app_name,
				"display_name": app.display_name,
				"logo_url": app.logo_url,
				"description": app.description,
				"category": app.category,
				"oauth_provider": app.oauth_provider,
				"use_cases": use_cases
			}
		}
	except frappe.DoesNotExistError:
		return {
			"success": False,
			"error": f"App '{app_name}' not found"
		}


@frappe.whitelist(allow_guest=True)
def get_categories():
	"""
	Get list of app categories

	Returns:
		dict: List of categories with app counts
	"""
	categories = frappe.get_all(
		"App Catalog",
		filters={"is_active": 1},
		fields=["category"],
		group_by="category"
	)

	category_counts = {}
	for cat in categories:
		if cat.category:
			count = frappe.db.count("App Catalog", {
				"category": cat.category,
				"is_active": 1
			})
			category_counts[cat.category] = count

	return {
		"success": True,
		"categories": category_counts
	}


@frappe.whitelist()
def search_apps(query):
	"""
	Search for apps by name or description

	Args:
		query: Search query

	Returns:
		dict: Matching apps
	"""
	if not query:
		return get_app_catalog()

	apps = frappe.get_all(
		"App Catalog",
		filters={
			"is_active": 1
		},
		or_filters=[
			["display_name", "like", f"%{query}%"],
			["description", "like", f"%{query}%"],
			["app_name", "like", f"%{query}%"]
		],
		fields=[
			"name",
			"app_name",
			"display_name",
			"logo_url",
			"description",
			"category",
			"oauth_provider"
		],
		order_by="display_name asc"
	)

	# Get use cases for each app
	for app in apps:
		use_cases = frappe.get_all(
			"App Use Case",
			filters={"parent": app.name},
			fields=["use_case_name", "description", "workflow_template_id"],
			order_by="idx asc"
		)
		app["use_cases"] = use_cases

	return {
		"success": True,
		"apps": apps,
		"query": query
	}
