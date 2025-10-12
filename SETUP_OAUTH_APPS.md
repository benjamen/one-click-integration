# Quick Start: Create OAuth Apps for Default Tier

This guide walks you through creating OAuth applications for the Quick Start (Default Tier) feature.

---

## Why You Need This

The Quick Start tier allows users to test integrations instantly using **Lodgeick's shared OAuth application**. You need to create one OAuth app per provider and add the credentials to `site_config.json`.

---

## Step 1: Create Google OAuth App (10 minutes)

### 1.1 Go to Google Cloud Console
- Navigate to: https://console.cloud.google.com/
- Sign in with your Google account

### 1.2 Create a New Project
- Click project dropdown (top left)
- Click "New Project"
- **Project Name:** `Lodgeick Shared OAuth`
- Click "Create"
- Wait for project to be created (10-15 seconds)

### 1.3 Enable Required APIs
- Go to: https://console.cloud.google.com/apis/library
- Search and enable each:
  - ✅ **Gmail API**
  - ✅ **Google Sheets API**
  - ✅ **Google Drive API**
  - ✅ **Google Calendar API**

For each API:
1. Click on the API name
2. Click "Enable"
3. Wait 5 seconds

### 1.4 Configure OAuth Consent Screen
- Go to: https://console.cloud.google.com/apis/credentials/consent
- Click "Configure Consent Screen"
- Select **"External"** user type
- Click "Create"

**Fill in required fields:**
- **App name:** `Lodgeick`
- **User support email:** Your email
- **Developer contact:** Your email
- Click "Save and Continue"

**Add Scopes:**
- Click "Add or Remove Scopes"
- Search and add:
  ```
  https://www.googleapis.com/auth/gmail.send
  https://www.googleapis.com/auth/spreadsheets
  https://www.googleapis.com/auth/drive.file
  https://www.googleapis.com/auth/calendar
  ```
- Click "Update"
- Click "Save and Continue"

**Add Test Users (Important!):**
- Click "Add Users"
- Add your email address(es)
- Click "Save and Continue"
- Click "Back to Dashboard"

### 1.5 Create OAuth 2.0 Credentials
- Go to: https://console.cloud.google.com/apis/credentials
- Click "Create Credentials" → "OAuth 2.0 Client ID"
- **Application type:** Web application
- **Name:** `Lodgeick Shared - Local`

**Authorized redirect URIs:**
Add these URLs (one per line):
```
http://localhost:8090/api/method/lodgeick.api.oauth.oauth_callback
http://localhost:5173/oauth/callback
http://127.0.0.1:8090/api/method/lodgeick.api.oauth.oauth_callback
```

- Click "Create"

### 1.6 Copy Credentials
A dialog appears with your credentials:
- **Client ID:** `123456789-abc123def456.apps.googleusercontent.com`
- **Client Secret:** `GOCSPX-abc123xyz`

**⚠️ Important:** Copy both and save to a secure location!

---

## Step 2: Create Slack OAuth App (Optional - 5 minutes)

### 2.1 Go to Slack API
- Navigate to: https://api.slack.com/apps
- Click "Create New App"
- Choose "From scratch"

### 2.2 Create App
- **App Name:** `Lodgeick`
- **Workspace:** Select your workspace
- Click "Create App"

### 2.3 Configure OAuth
- In left sidebar, click "OAuth & Permissions"

**Redirect URLs:**
Add:
```
http://localhost:8090/api/method/lodgeick.api.oauth.oauth_callback
```

**Scopes (Bot Token Scopes):**
- `channels:read`
- `channels:write`
- `chat:write`

### 2.4 Copy Credentials
- In "Basic Information" tab
- **Client ID:** Found under "App Credentials"
- **Client Secret:** Found under "App Credentials" (click "Show")

---

## Step 3: Create Xero OAuth App (Optional - 5 minutes)

### 3.1 Go to Xero Developer Portal
- Navigate to: https://developer.xero.com/app/manage
- Sign in with your Xero account
- Click "New app"

### 3.2 Create App
- **App name:** `Lodgeick`
- **Integration type:** Web app
- **Company or application URL:** `http://localhost:5173`
- **Redirect URI:**
  ```
  http://localhost:8090/api/method/lodgeick.api.oauth.oauth_callback
  ```

### 3.3 Copy Credentials
- **Client ID:** Displayed on app page
- **Client Secret:** Click "Generate a secret"

---

## Step 4: Add Credentials to site_config.json

### 4.1 Edit Config File

```bash
# Local environment
docker exec -it frappe_docker_devcontainer-frappe-1 bash
cd /workspace/development/frappe-bench
nano sites/lodgeick.com/site_config.json
```

### 4.2 Add Credentials

Add these lines to the JSON (replace with your actual values):

```json
{
  "db_name": "...",
  "db_password": "...",

  "anthropic_api_key": "sk-ant-api03-...",
  "google_cloud_service_account": {...},
  "n8n_base_url": "...",
  "n8n_api_key": "...",

  "google_client_id": "123456789-abc123def456.apps.googleusercontent.com",
  "google_client_secret": "GOCSPX-abc123xyz",

  "slack_client_id": "1234567890.1234567890",
  "slack_client_secret": "abc123def456ghi789",

  "xero_client_id": "ABC123DEF456GHI789",
  "xero_client_secret": "xyz789uvw456rst123"
}
```

**⚠️ Important:** Ensure valid JSON syntax (commas, quotes, brackets)

### 4.3 Restart Bench

```bash
# Exit nano (Ctrl+X, Y, Enter)
# Restart to load new config
bench restart
```

---

## Step 5: Verify Configuration

### 5.1 Check Config Loaded

```bash
docker exec -w /workspace/development/frappe-bench frappe_docker_devcontainer-frappe-1 \
  bash -c "cat sites/lodgeick.com/site_config.json | python3 -c \"
import sys, json
config = json.load(sys.stdin)
print('✅ google_client_id:' if 'google_client_id' in config else '❌ google_client_id: MISSING')
print('✅ google_client_secret:' if 'google_client_secret' in config else '❌ google_client_secret: MISSING')
\""
```

Expected output:
```
✅ google_client_id:
✅ google_client_secret:
```

### 5.2 Test Quick Start API

```bash
docker exec -w /workspace/development/frappe-bench frappe_docker_devcontainer-frappe-1 \
  bash -c "source env/bin/activate && bench --site lodgeick.com console"
```

In console:
```python
import frappe

# Test default credentials exist
client_id = frappe.conf.get('google_client_id')
client_secret = frappe.conf.get('google_client_secret')

if client_id and client_secret:
    print("✅ Default Google OAuth credentials configured!")
    print(f"Client ID: {client_id[:30]}...")
else:
    print("❌ Credentials not found")
```

---

## Step 6: Test Frontend

### 6.1 Start Frontend Dev Server (if not running)

```bash
cd /home/ben/frappe_docker/development/frappe-bench/apps/lodgeick/frontend
yarn dev
```

### 6.2 Access Integration Page

- Open browser: http://localhost:5173/onboarding/integrate
- Click "Set up credentials" on Google
- **Verify:** You should see 3 tier options:
  - ⚡ Quick Start (Lodgeick Shared App)
  - 🤖 AI-Powered Setup (Recommended)
  - 🔧 Manual Setup (Advanced)

### 6.3 Test Quick Start Flow

1. Click **"Quick Start"** card
2. Click "Continue with Quick Start"
3. **Expected:**
   - Wizard closes
   - "OAuth Credentials" step shows ✅ checkmark
   - "Authorize" button becomes active
4. Click "Authorize now →"
5. **Expected:** Redirects to Google OAuth consent screen
6. Allow access
7. **Expected:** Returns to integration page with success

---

## Troubleshooting

### Error: "Default OAuth app for google not configured"

**Solution:** Credentials not in site_config.json
```bash
# Check config
cat sites/lodgeick.com/site_config.json | grep google_client

# If empty, add credentials and restart
bench restart
```

### Error: "redirect_uri_mismatch"

**Solution:** Redirect URI not added to Google Console
- Go to https://console.cloud.google.com/apis/credentials
- Click your OAuth 2.0 Client ID
- Add exact redirect URI from error message
- Save

### Error: "This app is in testing mode"

**Solution:** Add yourself as test user
- Go to OAuth consent screen
- Click "Test users"
- Add your email
- Try again

### Frontend shows only 2 tiers (no Quick Start)

**Solution:**
1. Check tier config endpoint working:
   ```bash
   curl http://localhost:8090/api/method/lodgeick.api.oauth_tiers.get_tier_config?provider=google
   ```
2. Check default tier enabled in `oauth_tiers.py`:
   ```python
   "default": {
       "enabled": True,  # Make sure this is True
       ...
   }
   ```

---

## Security Best Practices

### Local Development
- ✅ Use test Google accounts
- ✅ Add only trusted users to test users list
- ✅ Use localhost redirect URIs
- ✅ Don't commit credentials to git

### Production
- ✅ Use separate OAuth app for production
- ✅ Add production domain to redirect URIs
- ✅ Use environment variables or secrets manager
- ✅ Enable rate limiting and monitoring
- ✅ Regularly rotate secrets
- ✅ Submit app for Google verification (if public)

---

## Production Deployment

### Create Production OAuth Apps

Follow Steps 1-3 above, but:
- Use production domain in redirect URIs
- **Example:** `https://lodgeick.com/api/method/lodgeick.api.oauth.oauth_callback`
- Create separate apps (don't reuse local apps)
- Store credentials in production site_config.json

### Add to Production Config

```bash
# SSH to production server
ssh root@tendercle.com

# Edit config
cd ~/frappe_docker
docker exec frappe_docker_devcontainer-frappe-1 bash
cd /workspace/development/frappe-bench
nano sites/tendercle.com/site_config.json

# Add production credentials
{
  "google_client_id": "prod-client-id.apps.googleusercontent.com",
  "google_client_secret": "GOCSPX-prod-secret",
  ...
}

# Restart
bench restart
```

---

## Next Steps

After completing this setup:

1. ✅ Quick Start tier will be functional
2. ✅ Users can test integrations instantly
3. ✅ Rate limiting will be enforced
4. ✅ All three tiers available

Continue to:
- **TESTING_GUIDE.md** - Run comprehensive tests
- **ROLES_AND_TIERS.md** - Understand subscription model
- **TEST_RESULTS.md** - View test results

---

## Quick Reference

### Credentials Checklist

| Provider | Client ID | Client Secret | Status |
|----------|-----------|---------------|--------|
| Google | `google_client_id` | `google_client_secret` | ⬜ |
| Slack | `slack_client_id` | `slack_client_secret` | ⬜ |
| Xero | `xero_client_id` | `xero_client_secret` | ⬜ |
| Microsoft | `microsoft_client_id` | `microsoft_client_secret` | ⬜ |
| HubSpot | `hubspot_client_id` | `hubspot_client_secret` | ⬜ |

### Test Commands

```bash
# Check config
cat sites/lodgeick.com/site_config.json | grep -E "client_id|client_secret"

# Test in console
bench --site lodgeick.com console
>>> import frappe
>>> print(frappe.conf.get('google_client_id'))

# Test API endpoint
curl http://localhost:8090/api/method/lodgeick.api.oauth_tiers.get_tier_config?provider=google

# Test frontend
# Browser: http://localhost:5173/onboarding/integrate
```

---

**Setup Time:** ~30 minutes for all providers
**Difficulty:** Easy-Medium
**Required:** Google account (for Google OAuth)
