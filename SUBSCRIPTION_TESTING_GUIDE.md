# Subscription Tier System - Testing Guide

## Overview
The subscription tier system gates access to OAuth setup tiers based on user subscription level.

## System Architecture

### Backend Components
1. **Subscription DocType** (`lodgeick/lodgeick/doctype/subscription/`)
   - Stores user subscription data
   - Auto-provisions Free tier for new users
   - Tracks feature access and usage limits

2. **Tier Gating Logic** (`lodgeick/api/oauth_tiers.py`)
   - `get_user_subscription_tier()` - Returns user's tier (Free/Pro/Enterprise)
   - `get_tier_config()` - Returns tier config with gating applied
   - Free users: AI tier disabled with upgrade_required flag

3. **Frontend Integration** (`frontend/src/components/OAuthSetupWizard.vue`)
   - Displays locked tiers with visual indicators
   - Shows upgrade prompts and buttons
   - Prevents selection of locked tiers

## Testing Procedures

### 1. Test Free User (Default Tier)

**Expected Behavior:**
- User has Free tier subscription (auto-provisioned)
- Quick Start tier: Available
- AI-Powered tier: Locked with upgrade prompt
- Manual tier: Available

**Test Steps:**
1. Navigate to https://lodgeick.com/onboarding/integrate (or http://localhost:5173/onboarding/integrate for local)
2. Select a provider (e.g., Google)
3. Verify AI-Powered tier shows:
   - Lock badge with "Pro Only"
   - Yellow dashed border
   - Upgrade message: "Upgrade to Pro to enable AI-powered setup"
   - "Upgrade to Pro" button
4. Click AI-Powered tier card - should not be selectable
5. Quick Start and Manual tiers should be fully functional

**Backend Verification (via bench console):**
```python
from lodgeick.lodgeick.doctype.subscription.subscription import get_user_subscription

# Get subscription for current user
sub = get_user_subscription()
print(f"Tier: {sub.tier}")  # Should be "Free"
print(f"AI Enabled: {sub.ai_setup_enabled}")  # Should be 0

# Test API response
from lodgeick.api.oauth_tiers import get_tier_config
config = get_tier_config('google')
print(f"AI Enabled: {config['tiers']['ai']['enabled']}")  # Should be False
print(f"Upgrade Required: {config['tiers']['ai']['upgrade_required']}")  # Should be True
```

### 2. Test Pro User

**Setup:**
```python
# Via bench console on lodgeick.com
from lodgeick.lodgeick.doctype.subscription.subscription import get_user_subscription
sub = get_user_subscription('user@example.com')
sub.tier = 'Pro'
sub.save()
```

**Expected Behavior:**
- All three tiers available
- No upgrade prompts
- AI-Powered tier fully functional

**Test Steps:**
1. Login as Pro user
2. Navigate to /onboarding/integrate
3. Select any provider
4. Verify all three tiers are enabled and selectable
5. No lock badges or upgrade messages should appear

### 3. Test Enterprise User

**Setup:**
```python
sub = get_user_subscription('enterprise@example.com')
sub.tier = 'Enterprise'
sub.save()
```

**Expected Behavior:**
- Same as Pro tier (all features unlocked)
- Unlimited rate limits

### 4. Test API Endpoints

**Test get_tier_config:**
```bash
# From localhost or production
curl 'https://lodgeick.com/api/method/lodgeick.api.oauth_tiers.get_tier_config?provider=google' \
  -H 'Cookie: sid=<session_id>'
```

**Expected Response (Free user):**
```json
{
  "message": {
    "provider_name": "Google",
    "has_ai_setup": true,
    "user_tier": "Free",
    "tiers": {
      "quick_start": {
        "enabled": true,
        ...
      },
      "ai": {
        "enabled": false,
        "upgrade_required": true,
        "upgrade_message": "Upgrade to Pro to enable AI-powered setup",
        "upgrade_tier": "Pro",
        ...
      },
      "manual": {
        "enabled": true,
        ...
      }
    }
  }
}
```

### 5. Test Auto-Provisioning

**Test Steps:**
1. Create a new user account
2. First API call to get_tier_config should auto-create Free subscription
3. Verify subscription exists in database:
```python
frappe.db.exists("Subscription", "newuser@example.com")  # Should return True
```

### 6. Test Frontend Visual Elements

**Elements to Verify:**
- [ ] Lock badge appears on AI tier (Free users only)
- [ ] Yellow dashed border on locked tier
- [ ] Reduced opacity on locked tier (0.7)
- [ ] Upgrade message displays correctly
- [ ] "Upgrade to Pro" button appears
- [ ] Click on locked tier does nothing
- [ ] Cursor changes to "not-allowed" on locked tier
- [ ] Unlocked tiers remain fully interactive

### 7. Test Upgrade Flow (Placeholder)

**Current Status:**
- Upgrade button shows alert() with upgrade info
- TODO: Replace with proper upgrade modal/Stripe integration

**Test:**
1. Click "Upgrade to Pro" button
2. Verify alert displays:
   - Upgrade message
   - Pro tier features list
   - Contact support instruction

## Database Schema

### Subscription DocType Fields

| Field | Type | Description |
|-------|------|-------------|
| user | Link (User) | Unique - one subscription per user |
| tier | Select | Free / Pro / Enterprise |
| status | Select | Active / Expired / Cancelled / Trial |
| start_date | Date | Subscription start date |
| end_date | Date | Subscription end date |
| max_integrations | Int | 3 (Free), 10 (Pro), -1 (Enterprise) |
| max_workflow_executions | Int | 1000 / 10000 / unlimited |
| ai_setup_enabled | Check | 0 (Free), 1 (Pro+) |
| premium_providers_enabled | Check | 0 (Free), 1 (Pro+) |
| integrations_used | Int | Current usage count |
| workflow_executions_used | Int | Current usage count |
| stripe_customer_id | Data | For payment integration |
| stripe_subscription_id | Data | For payment integration |

## Deployment Status

**Commits:**
- `0e46230` - feat: Implement subscription-based tier gating system
- `c86af84` - feat: Build frontend with subscription tier gating UI

**Deployment:**
- GitHub Actions workflow: Deploy to Server #44
- Status: Running
- Target: https://lodgeick.com
- Auto-deploys on push to main branch

**Migration:**
- Subscription DocType created in database
- Migrations completed via `bench --site lodgeick.com migrate`

## Known Issues / TODOs

1. **Upgrade Flow:** Replace alert() with proper upgrade modal
2. **Stripe Integration:** Add payment processing
3. **Usage Tracking:** Implement actual usage counting
4. **Email Notifications:** Send emails on tier changes
5. **Admin Panel:** Create UI for managing user subscriptions
6. **Rate Limiting:** Enforce API rate limits based on tier
7. **Testing on Local Dev:** Database connection issues in dev container

## Files Modified

### Created:
- `lodgeick/lodgeick/doctype/subscription/subscription.json`
- `lodgeick/lodgeick/doctype/subscription/subscription.py`
- `lodgeick/lodgeick/doctype/subscription/__init__.py`
- `lodgeick/lodgeick/doctype/subscription/test_subscription.py`

### Modified:
- `lodgeick/api/oauth_tiers.py` - Added subscription gating logic
- `frontend/src/components/OAuthSetupWizard.vue` - Added upgrade UI
- All built frontend assets (hash changes)

## Support

For issues or questions:
- Check Frappe logs: `bench --site lodgeick.com console` or server logs
- Review API responses in browser DevTools Network tab
- Test backend logic directly via bench console
- Check GitHub Actions logs for deployment issues
