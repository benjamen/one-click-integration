# Copyright (c) 2025, Lodgeick and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class Subscription(Document):
	def before_save(self):
		"""Auto-set features based on tier"""
		self.set_tier_features()

	def set_tier_features(self):
		"""Set feature flags based on subscription tier"""
		tier_features = {
			"Free": {
				"max_integrations": 3,
				"max_workflow_executions": 1000,
				"ai_setup_enabled": 0,
				"premium_providers_enabled": 0
			},
			"Pro": {
				"max_integrations": 10,
				"max_workflow_executions": 10000,
				"ai_setup_enabled": 1,
				"premium_providers_enabled": 1
			},
			"Enterprise": {
				"max_integrations": -1,  # Unlimited
				"max_workflow_executions": -1,  # Unlimited
				"ai_setup_enabled": 1,
				"premium_providers_enabled": 1
			}
		}

		if self.tier in tier_features:
			features = tier_features[self.tier]
			for key, value in features.items():
				self.set(key, value)


def get_user_subscription(user=None):
	"""
	Get subscription for a user (or current user)

	Args:
		user: User email (defaults to current session user)

	Returns:
		Subscription document or None
	"""
	if not user:
		user = frappe.session.user

	# Check if subscription exists
	if frappe.db.exists("Subscription", user):
		return frappe.get_doc("Subscription", user)

	# Create default Free tier subscription for new users
	subscription = frappe.get_doc({
		"doctype": "Subscription",
		"user": user,
		"tier": "Free",
		"status": "Active",
		"start_date": datetime.now().date(),
		"end_date": (datetime.now() + timedelta(days=365)).date()  # 1 year free
	})
	subscription.insert(ignore_permissions=True)
	frappe.db.commit()

	return subscription


def check_feature_access(feature, user=None):
	"""
	Check if user has access to a specific feature

	Args:
		feature: Feature name (ai_setup_enabled, premium_providers_enabled, etc.)
		user: User email (defaults to current session user)

	Returns:
		bool: True if user has access, False otherwise
	"""
	subscription = get_user_subscription(user)

	if not subscription:
		return False

	# Check if subscription is active
	if subscription.status != "Active":
		return False

	# Check if subscription has expired
	if subscription.end_date and subscription.end_date < datetime.now().date():
		return False

	# Check feature flag
	return subscription.get(feature) == 1


def check_usage_limit(limit_field, usage_field, user=None):
	"""
	Check if user has reached their usage limit

	Args:
		limit_field: Field name for limit (max_integrations, max_workflow_executions)
		usage_field: Field name for current usage (integrations_used, workflow_executions_used)
		user: User email (defaults to current session user)

	Returns:
		dict: {
			"allowed": bool,
			"current": int,
			"limit": int,
			"upgrade_required": bool
		}
	"""
	subscription = get_user_subscription(user)

	if not subscription:
		return {
			"allowed": False,
			"current": 0,
			"limit": 0,
			"upgrade_required": True
		}

	limit = subscription.get(limit_field) or 0
	current = subscription.get(usage_field) or 0

	# -1 means unlimited
	if limit == -1:
		return {
			"allowed": True,
			"current": current,
			"limit": -1,
			"upgrade_required": False
		}

	return {
		"allowed": current < limit,
		"current": current,
		"limit": limit,
		"upgrade_required": current >= limit
	}


def increment_usage(usage_field, amount=1, user=None):
	"""
	Increment usage counter for a user

	Args:
		usage_field: Field to increment (integrations_used, workflow_executions_used)
		amount: Amount to increment by
		user: User email (defaults to current session user)
	"""
	subscription = get_user_subscription(user)

	if subscription:
		current = subscription.get(usage_field) or 0
		subscription.set(usage_field, current + amount)
		subscription.save(ignore_permissions=True)
		frappe.db.commit()


@frappe.whitelist()
def get_my_subscription():
	"""API endpoint to get current user's subscription"""
	subscription = get_user_subscription()

	if not subscription:
		return None

	return {
		"tier": subscription.tier,
		"status": subscription.status,
		"features": {
			"max_integrations": subscription.max_integrations,
			"max_workflow_executions": subscription.max_workflow_executions,
			"ai_setup_enabled": subscription.ai_setup_enabled,
			"premium_providers_enabled": subscription.premium_providers_enabled
		},
		"usage": {
			"integrations_used": subscription.integrations_used,
			"workflow_executions_used": subscription.workflow_executions_used
		},
		"dates": {
			"start_date": subscription.start_date,
			"end_date": subscription.end_date
		}
	}


@frappe.whitelist()
def upgrade_subscription(tier):
	"""
	API endpoint to upgrade subscription

	Args:
		tier: New tier (Pro, Enterprise)
	"""
	if tier not in ["Pro", "Enterprise"]:
		frappe.throw("Invalid tier")

	subscription = get_user_subscription()

	if not subscription:
		frappe.throw("Subscription not found")

	subscription.tier = tier
	subscription.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"message": f"Subscription upgraded to {tier}",
		"subscription": get_my_subscription()
	}
