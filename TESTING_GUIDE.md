# OAuth Three-Tier System Testing Guide

## Prerequisites

### Required Configuration in `site_config.json`

```json
{
  // Required for AI-Powered Setup
  "anthropic_api_key": "sk-ant-api03-...",

  // Required for Automated Project Creation
  "google_cloud_service_account": {
    "type": "service_account",
    "project_id": "lodgeick-admin",
    "private_key_id": "abc123...",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...",
    "client_email": "automation@lodgeick-admin.iam.gserviceaccount.com",
    "client_id": "12345678901234567890",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  },

  // Required for Quick Start (Default Tier)
  "google_client_id": "123456789-abc.apps.googleusercontent.com",
  "google_client_secret": "GOCSPX-abc123xyz",
  "slack_client_id": "1234567890.1234567890",
  "slack_client_secret": "abc123def456ghi789",
  "xero_client_id": "ABC123DEF456",
  "xero_client_secret": "xyz789uvw456",
  "microsoft_client_id": "abcd1234-ef56-...",
  "microsoft_client_secret": "abc~123",

  // Required for n8n Integration
  "n8n_base_url": "http://localhost:5678",
  "n8n_api_key": "n8n_api_xxx"
}
```

### Google Cloud Service Account Setup

1. **Create Service Account:**
   ```bash
   # Go to Google Cloud Console
   https://console.cloud.google.com/iam-admin/serviceaccounts

   # Create new service account:
   Name: "Lodgeick Automation"
   ID: automation@lodgeick-admin.iam.gserviceaccount.com
   ```

2. **Grant Required Roles:**
   - `roles/resourcemanager.projectCreator` - Create new projects
   - `roles/serviceusage.serviceUsageAdmin` - Enable/disable APIs
   - `roles/iam.serviceAccountUser` - Use service account

3. **Download JSON Key:**
   ```bash
   # Click on service account → Keys → Add Key → Create new key → JSON
   # Save to: ~/service-account.json
   ```

4. **Add to site_config.json:**
   ```bash
   # Option 1: Inline JSON (recommended for production)
   nano ~/frappe_docker/development/frappe-bench/sites/home.localhost/site_config.json
   # Copy entire JSON content into google_cloud_service_account field

   # Option 2: File path (for development)
   "google_cloud_service_account": "/home/ben/service-account.json"
   ```

### Python Dependencies

```bash
# In Frappe bench container
docker exec -it frappe_docker_devcontainer-frappe-1 bash
cd /workspace/development/frappe-bench
source env/bin/activate

pip install anthropic google-auth google-auth-oauthlib google-api-python-client
```

### Database Migration

```bash
# Create required DocTypes
bench --site home.localhost migrate
```

---

## Test 1: Quick Start (Default Tier) - Google

**Goal:** Test shared OAuth app with rate limiting

### Step 1: Verify Default Credentials Configured

```bash
bench --site home.localhost console
```
```python
# In console
import frappe
print(frappe.conf.get('google_client_id'))  # Should print client ID
print(frappe.conf.get('google_client_secret'))  # Should print secret
```

### Step 2: Access Integrate View

1. Navigate to: `http://home.localhost:8080/onboarding/integrate`
2. Should see apps grid (Google, Slack, Xero, etc.)
3. Click "Set up credentials" on Google card

### Step 3: Select Quick Start

1. OAuth Setup Wizard opens
2. See 3 tier options:
   - ⚡ Quick Start (Lodgeick Shared App)
   - 🤖 AI-Powered Setup (Recommended)
   - 🔧 Manual Setup (Advanced)
3. **Click Quick Start card**
4. Review:
   - Pros: No Google account needed, Start in seconds, Perfect for testing
   - Limits: Shared rate limits, Gmail 100/day, Sheets 500/day
5. Click "Continue with Quick Start"

### Step 4: Backend Processing

**Expected Backend Flow:**
```python
# API call: lodgeick.api.oauth.save_user_oauth_setup
# Parameters: provider='google', tier='default', use_default=True

# Backend checks:
1. Loads google_client_id from site_config.json ✅
2. Loads google_client_secret from site_config.json ✅
3. Initializes OAuth Usage Log for rate limiting ✅
4. Returns: {"success": true, "tier": "default", "ready_to_connect": true}
```

**Verify in Console:**
```python
# Check usage log created
frappe.db.get_all('OAuth Usage Log',
    filters={'user': 'user@example.com', 'provider': 'google', 'tier': 'default'},
    fields=['*'])
# Should return 1 record with daily_limit, minute_limit set
```

### Step 5: Authorize

1. Wizard closes
2. Step 1 (OAuth Credentials) shows green ✓
3. Step 2 (Authorize) becomes active
4. Click "Authorize now →"
5. **Should redirect to Google OAuth consent**
6. Click "Allow"
7. **Should redirect back with success**

### Step 6: Test Connection

1. Step 2 shows green ✓
2. Step 3 (Test Connection) becomes active
3. Click "Test now →"
4. Should show "Testing..." spinner
5. After 1.5s, shows green ✓ "Connection verified"

### Step 7: Verify Rate Limiting

```bash
bench --site home.localhost console
```
```python
from lodgeick.lodgeick.doctype.oauth_usage_log.oauth_usage_log import check_rate_limit, record_api_request

# Check current limits
result = check_rate_limit('user@example.com', 'google', 'default', 'gmail.googleapis.com')
print(result)
# Expected: {"allowed": true, "remaining_today": 100, "remaining_minute": 5}

# Simulate 100 requests
for i in range(100):
    record_api_request('user@example.com', 'google', 'default', 'gmail.googleapis.com')

# Check again - should be at limit
result = check_rate_limit('user@example.com', 'google', 'default', 'gmail.googleapis.com')
print(result)
# Expected: {"allowed": false, "message": "Rate limit exceeded. Please upgrade..."}
```

**✅ PASS if:**
- Quick Start option visible
- Credentials auto-configured without user input
- OAuth flow completes successfully
- Rate limit tracking works
- Limit exceeded message shows at 100 requests

---

## Test 2: AI-Powered Setup - Google

**Goal:** Test Claude AI parsing and automated project creation

### Step 1: Verify AI Prerequisites

```bash
bench --site home.localhost console
```
```python
import frappe
# Check Anthropic API key
print(frappe.conf.get('anthropic_api_key'))  # Should print sk-ant-api03-...

# Check Google Cloud service account
service_account = frappe.conf.get('google_cloud_service_account')
print(type(service_account))  # Should be dict or str
if isinstance(service_account, dict):
    print(service_account.get('client_email'))  # Should print service account email
```

### Step 2: Open AI Wizard

1. On Integrate View, click "Set up credentials" on Google
2. OAuth Setup Wizard opens
3. **Click AI-Powered Setup card**
4. Review:
   - Icon: 🤖
   - Label: "AI-Powered Setup (Recommended)"
   - Setup time: ~2 minutes
   - Badge: "Recommended"
   - Pros: Unlimited API quota, Full control, AI guides you
5. Click "Continue with AI-Powered Setup"

### Step 3: AI Wizard Opens

1. OAuth wizard closes
2. **Google AI Setup Wizard opens** (purple gradient header)
3. See "What do you want to integrate?" screen
4. Text area with examples

### Step 4: Enter Natural Language Intent

**Test Input:**
```
I want to read and send emails from Gmail, and create spreadsheets in Google Sheets to track customer data
```

Click "Analyze with AI" button

### Step 5: AI Parsing (Claude)

**Expected Backend Flow:**
```python
# API: lodgeick.api.google_ai_setup.parse_intent
# Calls: lodgeick.services.ai_parser.parse_intent()
# Uses: Claude 3.5 Sonnet model

# Expected response:
{
  "success": true,
  "apis": [
    {
      "name": "gmail.googleapis.com",
      "display_name": "Gmail API",
      "scopes": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send"
      ],
      "description": "Read and send emails"
    },
    {
      "name": "sheets.googleapis.com",
      "display_name": "Google Sheets API",
      "scopes": [
        "https://www.googleapis.com/auth/spreadsheets"
      ],
      "description": "Create and manage spreadsheets"
    }
  ],
  "billing_required": false,
  "billing_apis": [],
  "reasoning": "Gmail API provides email access, Sheets API enables spreadsheet creation. Neither requires billing."
}
```

**Verify AI Response:**
1. Should see "AI Analysis Results" screen
2. AI Reasoning box shows Claude's explanation
3. Two APIs listed: Gmail API, Google Sheets API
4. Each API shows scopes as badges
5. No billing warning (billing_required: false)

### Step 6: Choose Automated Setup

1. See two options:
   - **Automated Setup (New Project)** - Recommended, Fastest
   - Manual Setup (Existing Project) - Advanced
2. **Select "Automated Setup"** radio button
3. Click "Continue with Automated Setup"

### Step 7: Enter Project Name

1. Form expands to show "Name Your New Project"
2. Enter: `Lodgeick Test Integration`
3. Note: "A unique project ID will be generated automatically"
4. Click "Create Google Cloud Project"

### Step 8: Project Creation (Google Cloud APIs)

**Expected Backend Flow:**
```python
# API: lodgeick.api.google_ai_setup.create_project
# Parameters: project_name, intent_data (from Claude)

# Backend actions:
1. Generate project ID: lodgeick-test-integration-20250112154530
2. Initialize Google Cloud client with service account
3. Call: cloudresourcemanager.projects().create()
4. Wait for operation to complete (5-15 seconds)
5. Enable APIs: gmail.googleapis.com, sheets.googleapis.com
6. Call: serviceusage.services().enable() for each API
7. Store in User Google Project DocType
8. Return: {"success": true, "project_id": "...", "apis_enabled": [...]}
```

**Watch Console for Logs:**
```bash
# In another terminal
docker logs -f frappe_docker_devcontainer-frappe-1 | grep -i "google"
```

**Should see:**
```
Creating Google Cloud project: lodgeick-test-integration-20250112154530
Enabling APIs: gmail.googleapis.com, sheets.googleapis.com
Enabled API gmail.googleapis.com on project lodgeick-test-integration-20250112154530
Enabled API sheets.googleapis.com on project lodgeick-test-integration-20250112154530
```

### Step 9: Project Created Success

**UI Shows:**
1. ✅ Big green checkmark
2. "Project Created Successfully!"
3. Project ID: `lodgeick-test-integration-20250112154530`
4. Green success box: "2 APIs Enabled: gmail.googleapis.com, sheets.googleapis.com"
5. **Next: Create OAuth Credentials** card with:
   - Direct link to Google Cloud Console credentials page (opens with project pre-selected)
   - Step-by-step OAuth instructions
   - Redirect URI with copy button

### Step 10: Create OAuth Credentials Manually

1. Click link to Google Cloud Console (opens in new tab)
2. **Configure OAuth Consent Screen:**
   - User type: External
   - App name: Lodgeick
   - Add scopes shown in wizard
   - Add test user (your email)
3. **Create OAuth 2.0 Client ID:**
   - Type: Web application
   - Name: Lodgeick Local
   - Add redirect URI (copy from wizard)
   - Click Create
4. **Copy Client ID and Secret** from dialog
5. Return to wizard
6. Click "I've Created OAuth Credentials"

### Step 11: Enter Credentials

1. Paste **Client ID**: `123456789-abc123.apps.googleusercontent.com`
2. Paste **Client Secret**: `GOCSPX-abc123xyz` (use show/hide toggle)
3. Click "Save & Sync to n8n"

### Step 12: Save & n8n Sync

**Expected Backend Flow:**
```python
# API: lodgeick.api.google_ai_setup.setup_oauth_credentials

# Backend actions:
1. Save to OAuth Credentials Settings DocType
2. Create n8n credential via API:
   POST http://localhost:5678/api/v1/credentials
   {
     "name": "Google OAuth - user@example.com - {project_id}",
     "type": "googleOAuth2Api",
     "data": {
       "clientId": "...",
       "clientSecret": "...",
       "authUrl": "https://accounts.google.com/o/oauth2/v2/auth",
       "accessTokenUrl": "https://oauth2.googleapis.com/token"
     }
   }
3. Update User Google Project with n8n_credential_id
4. Set status to "Complete"
```

**Verify in Console:**
```python
# Check project created
frappe.db.get_all('User Google Project',
    filters={'project_id': 'lodgeick-test-integration-20250112154530'},
    fields=['*'])
# Should show: status='Complete', n8n_credential_id set, oauth_client_id set
```

### Step 13: Completion

1. Shows ✅✅ "Setup Complete!"
2. "Credentials have been synced to n8n"
3. Click "Done"
4. Returns to Integrate View
5. Google app Step 1 shows green ✓

**✅ PASS if:**
- Claude AI correctly parses intent
- Project created in Google Cloud
- APIs enabled automatically
- OAuth credentials saved
- n8n credential created
- User Google Project DocType populated

---

## Test 3: Manual Setup - Slack

**Goal:** Test step-by-step manual wizard

### Step 1: Open Wizard

1. On Integrate View, click "Set up credentials" on Slack
2. OAuth Setup Wizard opens
3. See tier options (Quick Start, Manual only - no AI for Slack)
4. **Click Manual Setup card**
5. Click "Continue with Manual Setup"

### Step 2: Multi-Step Instructions

**Wizard shows 6 steps with progress circles:**
- Step 0: Create Project *(if not Google)*
- Step 1: Enable APIs
- Step 2: Configure OAuth Consent Screen
- Step 3: Create OAuth Credentials
- Step 4: Enter Credentials
- Step 5: Complete

**For Slack, starts at Step 1 (no project creation needed)**

### Step 3: Follow Instructions

1. Click through each step
2. Each step shows:
   - Numbered instructions
   - External links to provider console
   - Code snippets to copy
   - Screenshots/visual aids
3. At Step 4, enter credentials manually
4. Click "Save & Test Connection"

### Step 4: Verify

**Backend:**
```python
# API: lodgeick.api.oauth.save_user_oauth_setup
# Parameters: provider='slack', tier='manual', client_id, client_secret

# Saves to OAuth Credentials Settings
```

**✅ PASS if:**
- Step-by-step instructions clear
- External links work
- Copy buttons functional
- Credentials save successfully
- Wizard progresses through all steps

---

## Test 4: Rate Limit Enforcement

**Goal:** Verify default tier rate limits prevent abuse

### Setup

```bash
bench --site home.localhost console
```
```python
from lodgeick.lodgeick.doctype.oauth_usage_log.oauth_usage_log import check_rate_limit, record_api_request

# Use Quick Start for Google
# Rate limits: Gmail = 100/day, 5/min
```

### Test Daily Limit

```python
user = 'test@example.com'
provider = 'google'
tier = 'default'
api = 'gmail.googleapis.com'

# Simulate 100 requests
for i in range(100):
    record_api_request(user, provider, tier, api)
    if i % 10 == 0:
        print(f"Request {i}/100")

# Check limit
result = check_rate_limit(user, provider, tier, api)
print(result)
# Expected: {"allowed": false, "remaining_today": 0, "message": "Rate limit exceeded..."}

# Try 101st request
result = check_rate_limit(user, provider, tier, api)
assert result['allowed'] == False
print("✅ Daily limit enforced")
```

### Test Minute Limit

```python
import time

# Reset by creating new log
frappe.db.delete('OAuth Usage Log', {
    'user': user,
    'provider': provider,
    'tier': tier,
    'api_name': api
})

# Simulate 5 requests in < 1 minute
for i in range(5):
    record_api_request(user, provider, tier, api)
    time.sleep(0.1)  # 100ms between requests

# Check - should still be allowed
result = check_rate_limit(user, provider, tier, api)
print(f"After 5 requests: {result['allowed']}")  # True

# 6th request should fail
record_api_request(user, provider, tier, api)
result = check_rate_limit(user, provider, tier, api)
print(f"After 6 requests: {result['allowed']}")  # False
assert result['allowed'] == False
print("✅ Minute limit enforced")
```

### Test Unlimited (AI Tier)

```python
# AI/Manual tiers have no limits
result = check_rate_limit(user, 'google', 'ai', 'gmail.googleapis.com')
assert result['allowed'] == True
assert result['remaining_today'] == None
print("✅ AI tier unlimited")
```

**✅ PASS if:**
- Daily limit prevents 101st request
- Minute limit prevents 6th request in same minute
- AI/Manual tiers show unlimited
- Error message suggests upgrading

---

## Test 5: Role & Permission Testing

**Goal:** Verify DocType permissions work correctly

### Test System Manager

```bash
bench --site home.localhost console
```
```python
frappe.set_user('Administrator')

# Should have full access
doc = frappe.new_doc('User Google Project')
doc.user = 'test@example.com'
doc.project_id = 'test-123'
doc.project_name = 'Test'
doc.status = 'Created'
doc.insert()
print("✅ System Manager can create")

doc.delete()
print("✅ System Manager can delete")
```

### Test Regular User (All role)

```python
# Create test user
if not frappe.db.exists('User', 'testuser@example.com'):
    user = frappe.new_doc('User')
    user.email = 'testuser@example.com'
    user.first_name = 'Test'
    user.send_welcome_email = 0
    user.insert()

frappe.set_user('testuser@example.com')

# Should be able to create own projects
doc = frappe.new_doc('User Google Project')
doc.user = 'testuser@example.com'
doc.project_id = 'test-user-123'
doc.project_name = 'User Test'
doc.status = 'Created'
doc.insert()
print("✅ Regular user can create own projects")

# Should NOT see other users' projects
other_projects = frappe.get_all('User Google Project',
    filters={'user': ['!=', 'testuser@example.com']})
print(f"Other user projects visible: {len(other_projects)}")
# Should be 0 (unless user has System Manager role)

frappe.set_user('Administrator')
```

**✅ PASS if:**
- System Manager has full CRUD access
- Regular users can create own projects
- Users cannot see other users' projects

---

## Troubleshooting

### Error: "Anthropic API key not configured"

```bash
bench --site home.localhost console
```
```python
import frappe
frappe.db.set_value('Singles', 'System Settings', 'anthropic_api_key', 'sk-ant-api03-...')
frappe.db.commit()
```
Or add to `site_config.json`:
```json
{
  "anthropic_api_key": "sk-ant-api03-..."
}
```

### Error: "Google Cloud service account not configured"

```bash
# Verify service account JSON is valid
cat ~/service-account.json | python -m json.tool
# Should output formatted JSON without errors

# Add to site_config.json
nano ~/frappe_docker/development/frappe-bench/sites/home.localhost/site_config.json
```

### Error: "Failed to create project"

Common causes:
1. **Service account lacks permissions**
   - Solution: Grant `roles/resourcemanager.projectCreator`
2. **Organization quota exceeded**
   - Solution: Delete old test projects or request quota increase
3. **Invalid project ID format**
   - Solution: Project ID must be lowercase, hyphens only, 6-30 chars

### Error: "n8n credential sync failed"

```bash
# Check n8n is running
curl http://localhost:5678/api/v1/workflows

# Check API key valid
curl -H "X-N8N-API-KEY: your-key" http://localhost:5678/api/v1/credentials
```

### Clear Test Data

```bash
bench --site home.localhost console
```
```python
# Delete all test projects
frappe.db.delete('User Google Project', {'project_name': ['like', '%Test%']})

# Delete all usage logs
frappe.db.delete('OAuth Usage Log', {'user': 'test@example.com'})

# Delete OAuth credentials
frappe.db.delete('OAuth Credentials Settings')

frappe.db.commit()
print("✅ Test data cleared")
```

---

## Success Criteria

| Test | Criteria | Status |
|------|----------|--------|
| Quick Start | Shared credentials work, rate limits enforced | ⬜ |
| AI-Powered | Claude parses intent, project created, APIs enabled | ⬜ |
| Manual Setup | Step-by-step wizard completes, credentials saved | ⬜ |
| Rate Limiting | Daily/minute limits enforced, AI tier unlimited | ⬜ |
| Permissions | System Manager full access, users isolated | ⬜ |
| n8n Sync | Credentials auto-synced to n8n | ⬜ |
| OAuth Flow | Authorization and token exchange work | ⬜ |

**All tests must pass before production deployment.**
