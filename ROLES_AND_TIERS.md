# User Roles & Subscription Tiers

## Overview

Lodgeick uses a combination of **Frappe Roles** for access control and **OAuth Tiers** for usage-based limits. This document explains the role system, subscription levels, and feature access matrix.

---

## Frappe Roles

### Built-in Roles

#### 1. System Manager
**Access Level:** Full administrative access

**Permissions:**
- ✅ View all users' integrations
- ✅ Create/edit/delete any DocType record
- ✅ Access Frappe Desk
- ✅ Configure system settings
- ✅ View error logs
- ✅ Manage all OAuth credentials
- ✅ Override rate limits
- ✅ Access bench commands

**Use Cases:**
- System administrators
- DevOps team
- Support staff troubleshooting issues

#### 2. All (Guest/Authenticated User)
**Access Level:** Standard user access

**Permissions:**
- ✅ Create own integrations
- ✅ View own data only (user field filter)
- ✅ Update own settings
- ✅ Delete own integrations
- ❌ Cannot access Frappe Desk
- ❌ Cannot see other users' data
- ❌ Cannot modify system settings

**Use Cases:**
- End users
- Customers
- Self-service integration setup

**User Isolation:**
```python
# User Google Project DocType automatically filters by user
# User can only see their own projects
frappe.get_all('User Google Project', filters={'user': frappe.session.user})
```

### Custom Roles (Future Enhancement)

#### 3. Lodgeick Premium (Proposed)
**Access Level:** Enhanced user features

**Proposed Permissions:**
- ✅ All "All" role permissions
- ✅ Higher rate limits on default tier
- ✅ Priority AI parsing (faster Claude responses)
- ✅ Access to premium providers (Salesforce, etc.)
- ✅ Advanced analytics dashboard
- ✅ Custom workflow templates

#### 4. Lodgeick Enterprise (Proposed)
**Access Level:** Organization-wide management

**Proposed Permissions:**
- ✅ All "Lodgeick Premium" permissions
- ✅ Manage team members' integrations
- ✅ Organization-wide OAuth apps
- ✅ SSO/SAML authentication
- ✅ Audit logs
- ✅ Dedicated support

---

## OAuth Tiers (Usage-Based)

OAuth tiers are **independent from Frappe roles**. They control rate limits and features per provider, not overall system access.

### Tier 1: Quick Start (Default)

**Description:** Use Lodgeick's shared OAuth application

**Configuration:**
- Client ID/Secret: From `site_config.json` (shared across users)
- Rate Limiting: **Yes** (per user, per API)
- Billing APIs: **Not allowed**

**Rate Limits by Provider:**

| Provider | API | Daily Limit | Minute Limit |
|----------|-----|-------------|--------------|
| **Google** | Gmail | 100 | 5 |
| | Sheets | 500 | 50 |
| | Drive | 1000 | 100 |
| | Calendar | 500 | 50 |
| **Slack** | All APIs | 10,000 | 20 |
| **Xero** | All APIs | 5,000 | 60 |
| **Microsoft** | Outlook | 100 | 10 |
| | OneDrive | 1,000 | 100 |
| | Teams | 500 | 50 |
| **HubSpot** | All APIs | 250,000 | 100/10s |

**Advantages:**
- ⚡ Instant setup (0 minutes)
- 🎯 No provider account needed
- 🧪 Perfect for testing/demos
- 💰 Free (no provider billing)

**Limitations:**
- 🚦 Shared rate limits
- 🚫 Cannot use billing-required APIs (Maps, Vision, etc.)
- 👥 Shared with other Lodgeick users
- 📊 May show "via Lodgeick" in audit logs

**Best For:**
- Testing integrations
- Personal projects
- Low-volume workflows
- Proof of concepts

**Access Control:**
```python
# lodgeick/api/oauth.py:329-349
# Backend checks site_config for default credentials
default_client_id = frappe.conf.get(f"{provider}_client_id")
default_client_secret = frappe.conf.get(f"{provider}_client_secret")

# Initializes rate limiting
from lodgeick.lodgeick.doctype.oauth_usage_log.oauth_usage_log import check_rate_limit
check_rate_limit(user, provider, 'default')
```

---

### Tier 2: AI-Powered (Recommended)

**Description:** Claude AI creates a new Google Cloud project for you

**Configuration:**
- Project: Auto-created by Lodgeick (user-owned)
- Client ID/Secret: User creates in Google Console
- Rate Limiting: **No** (uses user's own quota)
- Billing APIs: **Allowed** (if user enables billing)

**Setup Process:**
1. User describes intent in natural language
2. Claude AI parses and determines required APIs
3. Lodgeick creates Google Cloud project via service account
4. APIs enabled automatically
5. User creates OAuth credentials manually
6. Credentials synced to n8n automatically

**Project Naming:**
```
Format: {project-name}-{timestamp}
Example: lodgeick-customer-integration-20250112154530
Max Length: 30 characters
```

**Advantages:**
- 🤖 AI determines correct APIs/scopes
- ⚡ Project creation automated (5-15 seconds)
- 🎯 APIs enabled automatically
- 🔓 Unlimited API quota (user's own project)
- 📊 Full access to billing-required APIs
- 🔐 Complete control over project

**Limitations:**
- ⏱️ ~2 minute setup time
- 🌐 Requires Google account
- 💰 User responsible for any API costs
- 🔧 Must create OAuth credentials manually (Google limitation)

**Best For:**
- Production deployments
- High-volume integrations
- Billing-required APIs (Maps, Vision, etc.)
- Business/enterprise use

**Requirements:**
```json
// site_config.json
{
  "anthropic_api_key": "sk-ant-api03-...",
  "google_cloud_service_account": {
    "type": "service_account",
    "project_id": "lodgeick-admin",
    "private_key": "...",
    "client_email": "automation@lodgeick-admin.iam.gserviceaccount.com"
  }
}
```

**Backend Implementation:**
```python
# lodgeick/api/google_ai_setup.py
# 1. Parse intent with Claude AI
result = parser.parse_intent(user_intent)

# 2. Create project
project = client.create_project(project_id, project_name)

# 3. Enable APIs
enable_result = client.enable_apis(project_id, api_names)

# 4. Store in database
frappe.get_doc({
    'doctype': 'User Google Project',
    'user': frappe.session.user,
    'project_id': project_id,
    'status': 'APIs Enabled'
}).insert()
```

---

### Tier 3: Manual Setup (Advanced)

**Description:** Step-by-step wizard for existing provider accounts

**Configuration:**
- Project: User's existing project
- Client ID/Secret: User provides
- Rate Limiting: **No** (uses user's own quota)
- Billing APIs: **Allowed**

**Setup Process:**
1. User follows detailed step-by-step instructions
2. Creates/configures provider account manually
3. Enters credentials in Lodgeick
4. Credentials saved to database

**Advantages:**
- 🎯 Full control over configuration
- 🏢 Use existing organization account
- 💼 Enterprise-grade setup
- 🔓 Unlimited API quota

**Limitations:**
- ⏱️ ~10 minute setup time
- 🧠 Technical knowledge required
- 📚 Must read provider documentation

**Best For:**
- Existing provider accounts
- Enterprise organizations
- Advanced users
- Custom configurations

**Backend Implementation:**
```python
# lodgeick/api/oauth.py:351-368
# Save user credentials to database
save_oauth_credentials([{
    'provider': provider,
    'client_id': client_id,
    'client_secret': client_secret
}])

# OAuth Credentials Settings DocType stores encrypted credentials
```

---

## Subscription Tiers (Proposed)

> **Note:** Currently, all users have the same access. These tiers are proposed for future monetization.

### Free Tier

**Price:** $0/month

**Features:**
- ✅ Quick Start (default) OAuth tier
- ✅ Rate-limited API access
- ✅ Basic integrations (Google, Slack, Xero)
- ✅ Community support
- ✅ Up to 3 active integrations
- ✅ 1,000 workflow executions/month

**Rate Limits:**
- Gmail: 100 emails/day
- Sheets: 500 requests/day
- Slack: 10,000 requests/day

**Use Cases:**
- Personal projects
- Testing/learning
- Small automation needs

---

### Pro Tier

**Price:** $29/month

**Features:**
- ✅ All Free features
- ✅ AI-Powered OAuth setup
- ✅ Unlimited API quota (own projects)
- ✅ Premium integrations (HubSpot, Salesforce)
- ✅ Priority support
- ✅ Up to 10 active integrations
- ✅ 10,000 workflow executions/month
- ✅ Advanced analytics
- ✅ Custom n8n templates

**Additional:**
- 🤖 AI-powered intent parsing
- 📊 Usage analytics dashboard
- 🔔 Real-time alerts
- 🎨 Custom branding

**Use Cases:**
- Freelancers
- Small businesses
- Growing automation needs

---

### Enterprise Tier

**Price:** Custom pricing

**Features:**
- ✅ All Pro features
- ✅ Unlimited integrations
- ✅ Unlimited workflow executions
- ✅ Dedicated service account
- ✅ SSO/SAML authentication
- ✅ Team management
- ✅ Organization-wide OAuth apps
- ✅ Audit logs & compliance
- ✅ SLA guarantees
- ✅ Dedicated support

**Additional:**
- 🏢 Multi-tenant support
- 🔒 Advanced security controls
- 📈 Enterprise analytics
- 🛠️ Custom integrations
- 👨‍💼 Account manager

**Use Cases:**
- Large organizations
- Regulated industries
- High-volume automation
- White-label solutions

---

## Feature Access Matrix

| Feature | Free | Pro | Enterprise | System Manager |
|---------|------|-----|------------|----------------|
| **OAuth Tiers** |
| Quick Start (Default) | ✅ | ✅ | ✅ | ✅ |
| AI-Powered Setup | ❌ | ✅ | ✅ | ✅ |
| Manual Setup | ✅ | ✅ | ✅ | ✅ |
| **Rate Limits** |
| Shared (Rate Limited) | ✅ | ✅ | ✅ | N/A |
| Unlimited (Own Project) | ❌ | ✅ | ✅ | ✅ |
| **Integrations** |
| Basic (Google, Slack) | ✅ | ✅ | ✅ | ✅ |
| Premium (HubSpot, Salesforce) | ❌ | ✅ | ✅ | ✅ |
| Custom | ❌ | ❌ | ✅ | ✅ |
| **Support** |
| Community | ✅ | ❌ | ❌ | ✅ |
| Priority Email | ❌ | ✅ | ❌ | ✅ |
| Dedicated + SLA | ❌ | ❌ | ✅ | ✅ |
| **Management** |
| Self-Service | ✅ | ✅ | ✅ | ✅ |
| Team Management | ❌ | ❌ | ✅ | ✅ |
| Organization-Wide | ❌ | ❌ | ✅ | ✅ |
| System Administration | ❌ | ❌ | ❌ | ✅ |

---

## Implementation Plan

### Phase 1: Current State (Implemented)

- ✅ Three OAuth tiers (Quick Start, AI-Powered, Manual)
- ✅ Rate limiting for default tier
- ✅ Role-based access (System Manager, All)
- ✅ User data isolation
- ✅ AI-powered setup for Google

**All users currently have access to all features (no subscription paywall)**

### Phase 2: Subscription Gates (Future)

1. **Create Subscription DocType**
   ```python
   # lodgeick/lodgeick/doctype/subscription/subscription.json
   {
     "user": "user@example.com",
     "tier": "free|pro|enterprise",
     "status": "active|expired|cancelled",
     "start_date": "2025-01-01",
     "end_date": "2025-12-31",
     "features": {
       "ai_setup": true,
       "max_integrations": 10,
       "max_executions": 10000
     }
   }
   ```

2. **Add Permission Checks**
   ```python
   # lodgeick/api/oauth_tiers.py
   @frappe.whitelist()
   def get_tier_config(provider: str) -> dict:
       user_subscription = get_user_subscription(frappe.session.user)

       # Filter tiers based on subscription
       if user_subscription.tier == 'free':
           # Hide AI tier option
           config['tiers'].pop('ai', None)

       return config
   ```

3. **Usage Tracking**
   ```python
   # Track workflow executions
   # Track API calls
   # Track storage usage
   # Generate monthly invoices
   ```

### Phase 3: Billing Integration (Future)

- Stripe integration for payments
- Usage-based billing
- Automatic tier upgrades/downgrades
- Invoicing and receipts

---

## Configuration Examples

### Allow AI Setup for All Users (Current)

```json
// site_config.json
{
  "anthropic_api_key": "sk-ant-api03-...",
  "google_cloud_service_account": {...}
}
```

All users see AI-Powered option in wizard.

### Restrict AI Setup to Pro+ (Future)

```python
# lodgeick/api/oauth_tiers.py
def get_tier_config(provider: str) -> dict:
    config = OAUTH_TIER_CONFIG.get(provider, {})

    # Check subscription
    subscription = frappe.get_value('Subscription',
        {'user': frappe.session.user, 'status': 'active'},
        'tier')

    # Hide AI tier for free users
    if subscription == 'free' and 'ai' in config.get('tiers', {}):
        config['tiers']['ai']['enabled'] = False

    return config
```

### Override Rate Limits for Premium Users (Future)

```python
# lodgeick/lodgeick/doctype/oauth_usage_log/oauth_usage_log.py
def get_rate_limit(provider, tier, api_name):
    # Check if user has premium subscription
    subscription = frappe.get_value('Subscription',
        {'user': frappe.session.user, 'status': 'active'},
        ['tier', 'features'])

    if subscription.tier in ['pro', 'enterprise']:
        # 10x higher limits for premium users
        return {
            'requests_per_day': standard_limit * 10,
            'requests_per_minute': standard_limit_minute * 10
        }

    return standard_limit
```

---

## Testing Roles & Tiers

### Test User Isolation

```bash
bench --site home.localhost console
```

```python
# Create two test users
users = ['user1@test.com', 'user2@test.com']
for email in users:
    if not frappe.db.exists('User', email):
        user = frappe.new_doc('User')
        user.email = email
        user.first_name = email.split('@')[0]
        user.send_welcome_email = 0
        user.insert()

# User 1 creates a project
frappe.set_user('user1@test.com')
project = frappe.get_doc({
    'doctype': 'User Google Project',
    'user': 'user1@test.com',
    'project_id': 'user1-project',
    'project_name': 'User 1 Project',
    'status': 'Created'
})
project.insert()

# User 2 tries to see User 1's project
frappe.set_user('user2@test.com')
visible = frappe.get_all('User Google Project',
    filters={'project_id': 'user1-project'})
print(f"User 2 can see User 1's project: {len(visible) > 0}")
# Should print: False

# System Manager can see all
frappe.set_user('Administrator')
all_projects = frappe.get_all('User Google Project')
print(f"System Manager sees {len(all_projects)} projects")
# Should show all projects
```

---

## Summary

**Current State:**
- ✅ Role-based access control (System Manager, All)
- ✅ User data isolation
- ✅ Three OAuth tiers available to all users
- ✅ Rate limiting enforced on default tier

**Future State:**
- 🔜 Subscription-based feature gates
- 🔜 Billing integration
- 🔜 Usage-based pricing
- 🔜 Premium roles (Lodgeick Premium, Enterprise)

**Key Point:** OAuth tiers (Quick Start, AI-Powered, Manual) are separate from user roles. A "Free" user with "All" role can still choose Manual setup and get unlimited quota (using their own OAuth app).
