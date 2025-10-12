"""
OAuth Tiers API
Exposes tier configuration and setup functions to frontend
"""

import frappe
from lodgeick.config.oauth_tiers import OAUTH_TIER_CONFIG, get_available_tiers, is_tier_allowed_for_api


def get_user_subscription_tier():
	"""Get current user's subscription tier"""
	try:
		from lodgeick.lodgeick.doctype.subscription.subscription import get_user_subscription
		subscription = get_user_subscription()
		return subscription.tier if subscription else "Free"
	except:
		# If subscription system not yet installed, default to Free
		return "Free"


@frappe.whitelist()
def get_tier_config(provider: str) -> dict:
	"""
	Get tier configuration for a provider with subscription-based gating

	Args:
		provider: Provider name (google, slack, xero, etc.)

	Returns:
		Tier configuration dict with subscription gating applied
	"""
	config = get_available_tiers(provider)

	if not config:
		return {
			"provider_name": provider.title(),
			"has_ai_setup": False,
			"tiers": {
				"manual": {
					"enabled": True,
					"label": "Manual Setup",
					"description": "Set up your own OAuth credentials",
					"setup_time": "~10 minutes",
					"icon": "🔧",
					"advantages": [
						"Full control over configuration",
						"Use your own billing",
						"Unlimited rate limits"
					],
					"limitations": [],
					"requires": ["Account with " + provider.title()]
				}
			}
		}

	# Apply subscription gating
	user_tier = get_user_subscription_tier()

	# Free tier users: disable AI tier
	if user_tier == "Free" and "ai" in config.get("tiers", {}):
		config["tiers"]["ai"]["enabled"] = False
		config["tiers"]["ai"]["upgrade_required"] = True
		config["tiers"]["ai"]["upgrade_message"] = "Upgrade to Pro to enable AI-powered setup"
		config["tiers"]["ai"]["upgrade_tier"] = "Pro"

	# Add user's current tier to response
	config["user_tier"] = user_tier

	return config


@frappe.whitelist()
def check_default_credentials_available(provider: str) -> dict:
	"""
	Check if default OAuth credentials are configured for a provider

	Args:
		provider: Provider name

	Returns:
		{
			"available": bool,
			"client_id": str (if available),
			"message": str
		}
	"""
	# Check site_config for default credentials
	client_id_key = f"{provider}_client_id"
	client_secret_key = f"{provider}_client_secret"

	client_id = frappe.conf.get(client_id_key)
	client_secret = frappe.conf.get(client_secret_key)

	if client_id and client_secret:
		return {
			"available": True,
			"client_id": client_id,
			"message": f"Default {provider.title()} OAuth app is configured"
		}

	return {
		"available": False,
		"message": f"No default {provider.title()} OAuth credentials configured. Please use AI or Manual setup."
	}
