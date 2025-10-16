"""
n8n Node Cache Service

Caches n8n node types and definitions to reduce API calls.
Cache expires after 24 hours.
"""

import frappe
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


CACHE_DURATION_HOURS = 24


def get_cached_node_types() -> Optional[List[Dict]]:
	"""
	Get cached node types from database
	Returns None if cache is expired or doesn't exist
	"""
	try:
		cache_doc = frappe.get_doc("n8n Cache", "node_types")

		# Check if cache is expired
		if cache_doc.expires_at and cache_doc.expires_at < datetime.now():
			frappe.logger().info("n8n node types cache expired")
			return None

		# Parse and return cached data
		if cache_doc.data:
			return json.loads(cache_doc.data)

		return None
	except frappe.DoesNotExistError:
		return None
	except Exception as e:
		frappe.logger().error(f"Error reading n8n cache: {str(e)[:200]}")
		return None


def set_cached_node_types(node_types: List[Dict]):
	"""
	Cache node types in database with 24hr expiry
	"""
	try:
		expires_at = datetime.now() + timedelta(hours=CACHE_DURATION_HOURS)

		try:
			# Update existing cache
			cache_doc = frappe.get_doc("n8n Cache", "node_types")
			cache_doc.data = json.dumps(node_types)
			cache_doc.expires_at = expires_at
			cache_doc.save(ignore_permissions=True)
		except frappe.DoesNotExistError:
			# Create new cache entry
			cache_doc = frappe.get_doc({
				"doctype": "n8n Cache",
				"name": "node_types",
				"cache_key": "node_types",
				"data": json.dumps(node_types),
				"expires_at": expires_at
			})
			cache_doc.insert(ignore_permissions=True)

		frappe.db.commit()
		frappe.logger().info(f"Cached {len(node_types)} n8n node types until {expires_at}")
	except Exception as e:
		frappe.logger().error(f"Error caching n8n node types: {str(e)[:200]}")


def get_cached_node_definition(node_name: str) -> Optional[Dict]:
	"""
	Get cached node definition from database
	Returns None if cache is expired or doesn't exist
	"""
	try:
		cache_key = f"node_def_{node_name}"
		cache_doc = frappe.get_doc("n8n Cache", cache_key)

		# Check if cache is expired
		if cache_doc.expires_at and cache_doc.expires_at < datetime.now():
			frappe.logger().info(f"n8n node definition cache expired for {node_name}")
			return None

		# Parse and return cached data
		if cache_doc.data:
			return json.loads(cache_doc.data)

		return None
	except frappe.DoesNotExistError:
		return None
	except Exception as e:
		frappe.logger().error(f"Error reading n8n cache for {node_name}: {str(e)[:200]}")
		return None


def set_cached_node_definition(node_name: str, node_def: Dict):
	"""
	Cache node definition in database with 24hr expiry
	"""
	try:
		cache_key = f"node_def_{node_name}"
		expires_at = datetime.now() + timedelta(hours=CACHE_DURATION_HOURS)

		try:
			# Update existing cache
			cache_doc = frappe.get_doc("n8n Cache", cache_key)
			cache_doc.data = json.dumps(node_def)
			cache_doc.expires_at = expires_at
			cache_doc.save(ignore_permissions=True)
		except frappe.DoesNotExistError:
			# Create new cache entry
			cache_doc = frappe.get_doc({
				"doctype": "n8n Cache",
				"name": cache_key,
				"cache_key": cache_key,
				"data": json.dumps(node_def),
				"expires_at": expires_at
			})
			cache_doc.insert(ignore_permissions=True)

		frappe.db.commit()
		frappe.logger().info(f"Cached n8n node definition for {node_name} until {expires_at}")
	except Exception as e:
		frappe.logger().error(f"Error caching n8n node definition for {node_name}: {str(e)[:200]}")


def clear_cache():
	"""Clear all n8n cache entries"""
	try:
		frappe.db.delete("n8n Cache")
		frappe.db.commit()
		frappe.logger().info("Cleared all n8n cache")
	except Exception as e:
		frappe.logger().error(f"Error clearing n8n cache: {str(e)[:200]}")


def get_cache_stats() -> Dict:
	"""Get cache statistics"""
	try:
		total = frappe.db.count("n8n Cache")
		expired = frappe.db.count("n8n Cache", {"expires_at": ["<", datetime.now()]})
		valid = total - expired

		return {
			"total": total,
			"valid": valid,
			"expired": expired
		}
	except Exception as e:
		frappe.logger().error(f"Error getting cache stats: {str(e)[:200]}")
		return {"total": 0, "valid": 0, "expired": 0}
