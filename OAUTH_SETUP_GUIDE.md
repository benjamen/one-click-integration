# OAuth Setup Guide for Quick Start Tier

Complete guide to setting up OAuth applications for Lodgeick's **Quick Start (Shared OAuth)** tier.

## Overview

The Quick Start tier allows users to quickly connect integrations using **Lodgeick's shared OAuth applications**, without creating their own Google Cloud projects or OAuth apps.

### Prerequisites

To enable Quick Start tier, you need to:
1. Create OAuth applications in each provider's console
2. Add credentials to Frappe site configuration
3. Configure redirect URIs correctly

---

## Google OAuth Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a project" → "NEW PROJECT"
3. Project name: **"Lodgeick Production"**
4. Click "CREATE"

### 2. Enable Required APIs

1. Navigate to **APIs & Services** → **Library**
2. Enable the following APIs:
   - Google+ API (for user profile)
   - Gmail API
   - Google Sheets API
   - Google Drive API
   - Google Calendar API (optional)
   - Google Contacts API (optional)

### 3. Create OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. User Type: **External**
3. Click "CREATE"

**App Information:**
- App name: `Lodgeick`
- User support email: `support@lodgeick.com`
- App logo: Upload Lodgeick logo (480x480px)
- Application home page: `https://lodgeick.com`
- Application privacy policy: `https://lodgeick.com/privacy`
- Application terms of service: `https://lodgeick.com/terms`

**Developer contact:**
- Email: `dev@lodgeick.com`

**Scopes:**
Add the following scopes:
- `.../auth/userinfo.email`
- `.../auth/userinfo.profile`
- `.../auth/gmail.readonly`
- `.../auth/gmail.send`
- `.../auth/spreadsheets`
- `.../auth/drive.file`

Click "SAVE AND CONTINUE"

**Test users (during development):**
- Add test email addresses
- For production, publish the app

### 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click "+ CREATE CREDENTIALS" → **OAuth client ID**
3. Application type: **Web application**
4. Name: `Lodgeick Web Client`

**Authorized JavaScript origins:**
```
https://lodgeick.com
https://tendercle.com (if using custom domain)
http://localhost:8080 (for local development)
```

**Authorized redirect URIs:**
```
https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback
https://tendercle.com/api/method/lodgeick.api.oauth.oauth_callback
http://localhost:8080/api/method/lodgeick.api.oauth.oauth_callback
```

5. Click "CREATE"
6. **Copy the Client ID and Client Secret** - you'll need these!

### 5. Request OAuth Verification (Production)

For production use with >100 users:

1. Go to **OAuth consent screen**
2. Click "PUBLISH APP"
3. Submit for verification:
   - Provide demo video showing OAuth flow
   - Explain scopes usage
   - Provide privacy policy
   - Wait 3-7 days for approval

---

## Slack OAuth Setup

### 1. Create Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. App Name: `Lodgeick`
5. Workspace: Select your development workspace
6. Click "Create App"

### 2. Configure OAuth & Permissions

1. Go to **OAuth & Permissions** in left sidebar

**Redirect URLs:**
```
https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback
https://tendercle.com/api/method/lodgeick.api.oauth.oauth_callback
http://localhost:8080/api/method/lodgeick.api.oauth.oauth_callback
```

**Bot Token Scopes:**
- `channels:read` - View basic channel info
- `channels:write` - Manage channels
- `chat:write` - Send messages
- `files:write` - Upload files
- `users:read` - View user info

**User Token Scopes:**
- `channels:read`
- `channels:write`
- `chat:write`

3. Click "Save URLs"

### 3. Install App to Workspace (Development)

1. Go to **Install App**
2. Click "Install to Workspace"
3. Authorize the app

### 4. Get OAuth Credentials

1. Go to **Basic Information**
2. Under **App Credentials**, find:
   - **Client ID** - Copy this
   - **Client Secret** - Click "Show" and copy

### 5. Distribute App (Production)

1. Go to **Manage Distribution**
2. Check all requirements are met
3. Click "Activate Public Distribution"
4. Your app will be listed in Slack App Directory

---

## Xero OAuth Setup

### 1. Create Xero App

1. Go to [Xero Developer](https://developer.xero.com/app/manage)
2. Click "New app"
3. App name: `Lodgeick`
4. Company/application URL: `https://lodgeick.com`
5. OAuth 2.0 redirect URI:
   ```
   https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback
   http://localhost:8080/api/method/lodgeick.api.oauth.oauth_callback
   ```

6. Click "Create app"

### 2. Configure Scopes

In app settings, enable scopes:
- **Accounting:**
  - `accounting.transactions` - Read and write transactions
  - `accounting.contacts` - Read and write contacts
  - `accounting.settings` - Read org settings
- **Offline access:**
  - `offline_access` - Refresh tokens

### 3. Get OAuth Credentials

1. In app details, find:
   - **Client ID**
   - **Client secret** - Generate if not shown

2. Copy both values

---

## Microsoft/Azure AD OAuth Setup (Optional)

### 1. Register Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click "New registration"
4. Name: `Lodgeick`
5. Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
6. Redirect URI:
   - Platform: **Web**
   - URI: `https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback`
7. Click "Register"

### 2. Configure API Permissions

1. Go to **API permissions**
2. Click "Add a permission"
3. Choose **Microsoft Graph**
4. Select **Delegated permissions**:
   - `User.Read`
   - `Mail.Read`
   - `Mail.Send`
   - `Files.ReadWrite`
   - `Calendars.ReadWrite`

5. Click "Add permissions"
6. Click "Grant admin consent" (if admin)

### 3. Create Client Secret

1. Go to **Certificates & secrets**
2. Click "New client secret"
3. Description: `Lodgeick Production`
4. Expires: 24 months (or custom)
5. Click "Add"
6. **Copy the secret value immediately** - won't be shown again!

### 4. Get OAuth Credentials

- **Client ID (Application ID)**: Found in app overview
- **Client Secret**: The value you just copied

---

## HubSpot OAuth Setup (Optional)

### 1. Create HubSpot App

1. Go to [HubSpot Developers](https://developers.hubspot.com/)
2. Navigate to **Apps** → **Create app**
3. App name: `Lodgeick`
4. Description: Integration platform for business apps

### 2. Configure OAuth

1. Go to **Auth** tab
2. Redirect URL:
   ```
   https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback
   ```

3. Required scopes:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.companies.read`
   - `crm.objects.companies.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`

### 3. Get OAuth Credentials

1. Go to **Auth** tab
2. Copy:
   - **Client ID**
   - **Client secret**

---

## Adding Credentials to Frappe

### 1. Edit site_config.json

```bash
# On production server
ssh root@tendercle.com
cd ~/frappe_docker

# Enter container
docker exec -it frappe_docker_devcontainer-frappe-1 bash

# Edit site config
cd /workspace/development/frappe-bench
nano sites/tendercle.com/site_config.json
```

### 2. Add OAuth Credentials

```json
{
  "db_name": "...",
  "db_password": "...",

  "google_client_id": "123456789-abc123def456.apps.googleusercontent.com",
  "google_client_secret": "GOCSPX-abc123xyz789",

  "slack_client_id": "1234567890.1234567890123",
  "slack_client_secret": "abc123def456ghi789jkl012",

  "xero_client_id": "ABC123DEF456GHI789JKL012MNO",
  "xero_client_secret": "xyz789uvw456rst123",

  "microsoft_client_id": "abcd1234-ef56-7890-ghij-klmnopqrstuv",
  "microsoft_client_secret": "abc~123.DEF_456-ghi789",

  "hubspot_client_id": "12345678-abcd-1234-abcd-123456789abc",
  "hubspot_client_secret": "abc123def456-ghi789-jkl012-mno345",

  "anthropic_api_key": "...",
  "google_cloud_service_account": {...},
  "n8n_base_url": "...",
  "n8n_api_key": "..."
}
```

### 3. Secure the File

```bash
# Set proper permissions
chmod 600 sites/tendercle.com/site_config.json

# Verify ownership
chown frappe:frappe sites/tendercle.com/site_config.json
```

### 4. Restart Bench

```bash
bench restart
```

---

## Testing OAuth Setup

### 1. Test Configuration Loaded

```bash
bench --site tendercle.com console
```

```python
import frappe

# Check credentials are loaded
providers = ['google', 'slack', 'xero', 'microsoft', 'hubspot']

for provider in providers:
    client_id = frappe.conf.get(f'{provider}_client_id')
    client_secret = frappe.conf.get(f'{provider}_client_secret')

    if client_id and client_secret:
        print(f"✅ {provider.title()}: Configured")
        print(f"   Client ID: {client_id[:20]}...")
    else:
        print(f"❌ {provider.title()}: Not configured")
```

### 2. Test OAuth Flow

1. Navigate to: `https://tendercle.com/lodgeick`
2. Go to integration setup
3. Click "Set up credentials" for Google
4. Select **Quick Start** tier
5. Click "Connect with Google"
6. You should be redirected to Google OAuth consent screen
7. Authorize the app
8. You should be redirected back with success message

### 3. Verify Token Stored

```bash
bench --site tendercle.com console
```

```python
import frappe

# Check if token was created
tokens = frappe.get_all(
    'Integration Token',
    fields=['provider', 'user', 'creation'],
    limit=5,
    order_by='creation desc'
)

for token in tokens:
    print(f"✅ {token.provider} token for {token.user} - {token.creation}")
```

---

## Rate Limiting Configuration

Quick Start tier uses rate limiting to prevent abuse:

### 1. Configure Rate Limits

Edit `lodgeick/config/oauth_tiers.py`:

```python
TIER_LIMITS = {
    'default': {
        'requests_per_day': 1000,
        'requests_per_hour': 100,
        'max_active_integrations': 5
    }
}
```

### 2. Monitor Usage

```bash
bench --site tendercle.com console
```

```python
import frappe

# Check usage logs
usage = frappe.get_all(
    'OAuth Usage Log',
    fields=['user', 'provider', 'timestamp'],
    filters={'tier': 'default'},
    limit=20,
    order_by='timestamp desc'
)

for log in usage:
    print(f"{log.user} - {log.provider} - {log.timestamp}")
```

---

## Security Best Practices

### 1. Credential Storage

- ✅ Store in `site_config.json` (not in code)
- ✅ Use `chmod 600` for config file
- ✅ Never commit credentials to git
- ✅ Use environment variables for Docker deployments

### 2. OAuth Scope Minimization

- ✅ Request only necessary scopes
- ✅ Explain scope usage to users
- ✅ Support incremental authorization

### 3. Token Management

- ✅ Store tokens encrypted (Frappe password fields)
- ✅ Implement token refresh logic
- ✅ Delete tokens when integration disconnected
- ✅ Monitor for suspicious activity

### 4. Redirect URI Validation

- ✅ Use HTTPS in production
- ✅ Validate state parameter (CSRF protection)
- ✅ Whitelist exact redirect URIs
- ✅ No wildcard URIs

---

## Troubleshooting

### Issue: "redirect_uri_mismatch"

**Cause:** OAuth provider doesn't recognize redirect URI

**Solution:**
1. Check redirect URI in provider console exactly matches:
   ```
   https://your-site.com/api/method/lodgeick.api.oauth.oauth_callback
   ```
2. No trailing slashes
3. Exact protocol (http vs https)
4. Case-sensitive

### Issue: "Invalid client_id"

**Cause:** Credentials not loaded or incorrect

**Solution:**
```bash
bench --site your-site.com console

# Check config
import frappe
client_id = frappe.conf.get('google_client_id')
print(f"Loaded: {client_id is not None}")
print(f"Value: {client_id}")
```

### Issue: "Scopes not granted"

**Cause:** User didn't grant all requested scopes

**Solution:**
- Check OAuth consent screen shows all scopes
- Re-authenticate with correct scopes
- Check provider's scope syntax

---

## Maintenance

### Rotate Credentials (Recommended: Every 90 Days)

1. Generate new OAuth credentials in provider console
2. Update `site_config.json`
3. Keep old credentials active for 24 hours (grace period)
4. Remove old credentials after migration
5. Restart bench

### Monitor OAuth Health

```bash
# Check recent OAuth activities
bench --site your-site.com console
```

```python
import frappe
from datetime import datetime, timedelta

# Check success rate
start_date = datetime.now() - timedelta(days=7)

logs = frappe.get_all(
    'Integration Log',
    filters={
        'timestamp': ['>=', start_date],
        'status': ['in', ['Success', 'Error']]
    },
    fields=['status']
)

total = len(logs)
success = len([l for l in logs if l.status == 'Success'])
rate = (success / total * 100) if total > 0 else 0

print(f"OAuth Success Rate (7 days): {rate:.1f}%")
print(f"Total attempts: {total}")
print(f"Successful: {success}")
print(f"Failed: {total - success}")
```

---

## Support

For OAuth setup issues:
- **Documentation:** https://docs.lodgeick.com/oauth
- **Support:** support@lodgeick.com
- **GitHub Issues:** https://github.com/yourusername/lodgeick/issues

---

**Last Updated:** 2025-01-10
**Version:** 1.0.0
