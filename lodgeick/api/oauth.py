"""
OAuth authentication handler for Lodgeick integrations
Handles OAuth flows for various providers
"""

import frappe
from frappe import _
import requests
import json
from datetime import datetime, timedelta


@frappe.whitelist(allow_guest=True)
def initiate_oauth(provider, redirect_uri=None):
	"""
	Initiate OAuth flow for a provider

	Args:
		provider: Provider name (e.g., 'xero', 'google', 'slack')
		redirect_uri: Optional redirect URI after OAuth

	Returns:
		dict: Authorization URL and state token
	"""
	# Get provider config
	provider_config = get_provider_config(provider)

	if not provider_config:
		frappe.throw(_("Provider {0} not configured").format(provider))

	# Check if credentials are configured
	if not provider_config.get("client_id") or not provider_config.get("client_secret"):
		frappe.throw(_("OAuth credentials for {0} not configured. Please set up OAuth credentials first.").format(provider))

	# Generate state token for CSRF protection
	state = frappe.generate_hash(length=32)

	# Store state in cache (expires in 10 minutes)
	frappe.cache().setex(f"oauth_state:{state}", 600, json.dumps({
		"provider": provider,
		"user": frappe.session.user,
		"redirect_uri": redirect_uri
	}))

	# Build authorization URL
	auth_url = build_auth_url(provider_config, state, redirect_uri)

	return {
		"success": True,
		"authorization_url": auth_url,
		"state": state
	}


@frappe.whitelist(allow_guest=True)
def oauth_callback(code, state, provider):
	"""
	Handle OAuth callback

	Args:
		code: Authorization code from provider
		state: State token for CSRF protection
		provider: Provider name

	Returns:
		dict: Success status and redirect URL
	"""
	# Verify state token
	state_data = frappe.cache().get(f"oauth_state:{state}")

	if not state_data:
		frappe.throw(_("Invalid or expired OAuth state"))

	state_data = json.loads(state_data)

	if state_data.get("provider") != provider:
		frappe.throw(_("Provider mismatch"))

	# Exchange code for tokens
	provider_config = get_provider_config(provider)
	tokens = exchange_code_for_tokens(provider_config, code, state_data.get("redirect_uri"))

	# Store tokens in Integration Token doctype
	token_doc = frappe.get_doc({
		"doctype": "Integration Token",
		"user": state_data.get("user"),
		"provider": provider,
		"access_token": tokens.get("access_token"),
		"refresh_token": tokens.get("refresh_token"),
		"expires_at": calculate_expiry(tokens.get("expires_in")),
		"token_data": json.dumps(tokens)
	})
	token_doc.insert(ignore_permissions=True)

	# Create or update User Integration Settings
	try:
		# Find the app that uses this provider
		app = frappe.db.get_value("App Catalog", {"oauth_provider": provider}, "name")

		if app:
			# Check if settings already exist
			existing_settings = frappe.db.get_value(
				"User Integration Settings",
				{"user": state_data.get("user"), "app_name": app},
				"name"
			)

			if existing_settings:
				# Update existing
				settings_doc = frappe.get_doc("User Integration Settings", existing_settings)
				settings_doc.is_active = 1
				settings_doc.save(ignore_permissions=True)
			else:
				# Create new
				settings_doc = frappe.get_doc({
					"doctype": "User Integration Settings",
					"user": state_data.get("user"),
					"app_name": app,
					"is_active": 1,
					"settings": json.dumps({
						"connected_at": datetime.now().isoformat(),
						"provider": provider
					})
				})
				settings_doc.insert(ignore_permissions=True)
	except Exception as e:
		# Don't fail the OAuth flow if settings creation fails
		frappe.log_error(f"Failed to create User Integration Settings: {str(e)}")

	frappe.db.commit()

	# Clear state from cache
	frappe.cache().delete(f"oauth_state:{state}")

	return {
		"success": True,
		"message": "OAuth authentication successful",
		"redirect_uri": state_data.get("redirect_uri") or "/app"
	}


def get_provider_config(provider):
	"""
	Get OAuth configuration for a provider

	Args:
		provider: Provider name

	Returns:
		dict: Provider configuration
	"""
	# Try to get from OAuth Credentials Settings first
	try:
		settings = frappe.get_single("OAuth Credentials Settings")
		provider_settings = None

		for cred in settings.oauth_credentials:
			if cred.provider == provider:
				provider_settings = cred
				break

		if provider_settings and provider_settings.client_id and provider_settings.client_secret:
			# Provider-specific configurations
			provider_configs = {
				"xero": {
					"auth_url": "https://login.xero.com/identity/connect/authorize",
					"token_url": "https://identity.xero.com/connect/token",
					"scope": "accounting.transactions accounting.contacts offline_access"
				},
				"google": {
					"auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
					"token_url": "https://oauth2.googleapis.com/token",
					"scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file"
				},
				"slack": {
					"auth_url": "https://slack.com/oauth/v2/authorize",
					"token_url": "https://slack.com/api/oauth.v2.access",
					"scope": "channels:read channels:write chat:write"
				},
				"hubspot": {
					"auth_url": "https://app.hubspot.com/oauth/authorize",
					"token_url": "https://api.hubapi.com/oauth/v1/token",
					"scope": "crm.objects.contacts.read crm.objects.contacts.write"
				}
			}

			config = provider_configs.get(provider, {})
			config["client_id"] = provider_settings.client_id
			config["client_secret"] = provider_settings.client_secret
			return config
	except Exception as e:
		frappe.log_error(f"Error getting provider config from settings: {str(e)}")

	# Fallback to frappe.conf
	configs = {
		"xero": {
			"client_id": frappe.conf.get("xero_client_id"),
			"client_secret": frappe.conf.get("xero_client_secret"),
			"auth_url": "https://login.xero.com/identity/connect/authorize",
			"token_url": "https://identity.xero.com/connect/token",
			"scope": "accounting.transactions accounting.contacts offline_access"
		},
		"google": {
			"client_id": frappe.conf.get("google_client_id"),
			"client_secret": frappe.conf.get("google_client_secret"),
			"auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
			"token_url": "https://oauth2.googleapis.com/token",
			"scope": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file"
		},
		"slack": {
			"client_id": frappe.conf.get("slack_client_id"),
			"client_secret": frappe.conf.get("slack_client_secret"),
			"auth_url": "https://slack.com/oauth/v2/authorize",
			"token_url": "https://slack.com/api/oauth.v2.access",
			"scope": "channels:read channels:write chat:write"
		}
	}

	return configs.get(provider)


@frappe.whitelist()
def save_oauth_credentials(credentials):
	"""
	Save OAuth credentials to OAuth Credentials Settings

	Args:
		credentials: List of credentials [{provider, client_id, client_secret}]

	Returns:
		dict: Success status
	"""
	if isinstance(credentials, str):
		credentials = json.loads(credentials)

	# Get or create OAuth Credentials Settings
	if frappe.db.exists("OAuth Credentials Settings", "OAuth Credentials Settings"):
		settings = frappe.get_doc("OAuth Credentials Settings", "OAuth Credentials Settings")
	else:
		settings = frappe.get_doc({
			"doctype": "OAuth Credentials Settings"
		})

	# Clear existing credentials
	settings.oauth_credentials = []

	# Add new credentials
	for cred in credentials:
		settings.append("oauth_credentials", {
			"provider": cred.get("provider"),
			"client_id": cred.get("client_id"),
			"client_secret": cred.get("client_secret")
		})

	settings.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"message": "OAuth credentials saved successfully"
	}


def build_auth_url(config, state, redirect_uri=None):
	"""Build OAuth authorization URL"""
	if not redirect_uri:
		# Use the frontend OAuth callback route, not the API endpoint
		redirect_uri = frappe.utils.get_url("/oauth/callback")

	params = {
		"client_id": config["client_id"],
		"redirect_uri": redirect_uri,
		"scope": config["scope"],
		"state": state,
		"response_type": "code",
		"access_type": "offline",  # For refresh tokens
		"prompt": "consent"
	}

	from urllib.parse import urlencode
	return f"{config['auth_url']}?{urlencode(params)}"


def exchange_code_for_tokens(config, code, redirect_uri):
	"""Exchange authorization code for access and refresh tokens"""
	if not redirect_uri:
		# Use the frontend OAuth callback route, not the API endpoint
		redirect_uri = frappe.utils.get_url("/oauth/callback")

	data = {
		"client_id": config["client_id"],
		"client_secret": config["client_secret"],
		"code": code,
		"grant_type": "authorization_code",
		"redirect_uri": redirect_uri
	}

	response = requests.post(config["token_url"], data=data)

	if response.status_code != 200:
		frappe.throw(_("Failed to exchange code for tokens: {0}").format(response.text))

	return response.json()


def calculate_expiry(expires_in):
	"""Calculate token expiry datetime"""
	if not expires_in:
		return None

	return datetime.now() + timedelta(seconds=int(expires_in))


@frappe.whitelist()
def save_user_oauth_setup(provider, tier='manual', client_id=None, client_secret=None, use_default=False):
	"""
	Save user's OAuth setup choice (tier selection)

	Args:
		provider: Provider name (e.g., 'google', 'xero', 'slack')
		tier: Setup tier ('default', 'ai', 'manual')
		client_id: OAuth client ID (for manual tier)
		client_secret: OAuth client secret (for manual tier)
		use_default: Whether to use default Lodgeick OAuth app

	Returns:
		dict: Success status
	"""
	user = frappe.session.user

	# Handle default tier (use Lodgeick's shared OAuth app)
	if tier == 'default' or use_default:
		# Check if default credentials are available
		default_client_id = frappe.conf.get(f"{provider}_client_id")
		default_client_secret = frappe.conf.get(f"{provider}_client_secret")

		if not default_client_id or not default_client_secret:
			frappe.throw(_(f"Default OAuth app for {provider} is not configured. Please use AI or Manual setup."))

		# Create usage tracking record for rate limiting
		from lodgeick.lodgeick.doctype.oauth_usage_log.oauth_usage_log import check_rate_limit

		# Initialize usage log
		check_rate_limit(user, provider, 'default')

		return {
			"success": True,
			"message": f"Using Lodgeick's shared {provider.title()} app",
			"tier": "default",
			"ready_to_connect": True
		}

	# Handle manual tier (user provides their own credentials)
	elif tier == 'manual':
		if not client_id or not client_secret:
			frappe.throw(_("Client ID and Client Secret are required for manual setup"))

		# Save to OAuth Credentials Settings (user-specific)
		save_oauth_credentials([{
			"provider": provider,
			"client_id": client_id,
			"client_secret": client_secret
		}])

		return {
			"success": True,
			"message": f"OAuth credentials for {provider} saved successfully",
			"tier": "manual",
			"ready_to_connect": True
		}

	# AI tier is handled by the AI wizard separately
	else:
		return {
			"success": True,
			"message": "AI setup will be handled by AI wizard",
			"tier": "ai"
		}


@frappe.whitelist()
def refresh_token(provider, user=None):
	"""
	Refresh an expired OAuth token

	Args:
		provider: Provider name
		user: User (defaults to current user)

	Returns:
		dict: New token data
	"""
	if not user:
		user = frappe.session.user

	# Get existing token
	token_doc = frappe.get_doc("Integration Token", {
		"user": user,
		"provider": provider
	})

	if not token_doc.refresh_token:
		frappe.throw(_("No refresh token available"))

	provider_config = get_provider_config(provider)

	# Request new access token
	data = {
		"client_id": provider_config["client_id"],
		"client_secret": provider_config["client_secret"],
		"refresh_token": token_doc.get_password("refresh_token"),
		"grant_type": "refresh_token"
	}

	response = requests.post(provider_config["token_url"], data=data)

	if response.status_code != 200:
		frappe.throw(_("Failed to refresh token: {0}").format(response.text))

	tokens = response.json()

	# Update token document
	token_doc.access_token = tokens.get("access_token")
	if tokens.get("refresh_token"):
		token_doc.refresh_token = tokens.get("refresh_token")
	token_doc.expires_at = calculate_expiry(tokens.get("expires_in"))
	token_doc.token_data = json.dumps(tokens)
	token_doc.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"success": True,
		"message": "Token refreshed successfully"
	}
