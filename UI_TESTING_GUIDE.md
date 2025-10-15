# Lodgeick UI Testing Guide

This guide shows you how to easily test all the new n8n integration features via the UI.

## Prerequisites

1. **Frontend running**: `http://home.localhost:8080`
2. **Backend running**: `http://home.localhost:8000`
3. **n8n configured** in site_config.json:
   ```json
   {
     "n8n_api_url": "http://n8n:5678/api/v1",
     "n8n_api_key": "your-api-key"
   }
   ```
4. **User logged in** to Lodgeick

---

## Test Flow: End-to-End Workflow Creation

### Step 1: Dashboard - View Real Stats 📊

**URL**: `http://home.localhost:8080/dashboard`

**What to Check**:
- [ ] **Connected Apps** count displays (from App Connection doctype)
- [ ] **Active Integrations** count displays (from User Integration doctype)
- [ ] **Data Synced Today** shows real number from n8n executions
- [ ] **Last Sync** shows relative time (e.g., "5 mins ago", "Never")

**How to Verify**:
```bash
# Check via backend console
bench --site home.localhost console

# Count connected apps
frappe.db.count('App Connection', {'user': 'your@email.com', 'is_active': 1})

# Count active integrations
frappe.db.count('User Integration', {'user': 'your@email.com', 'status': 'Active'})
```

**Expected Behavior**:
- Stats load automatically on page mount
- Numbers match backend data
- Loading state shows briefly, then real data appears

---

### Step 2: Connect Apps 🔌

**URL**: `http://home.localhost:8080/connect`

**Actions**:
1. Click **"Connect Apps"** button from dashboard
2. Browse the app catalog
3. Click on any app (e.g., **Gmail**, **Google Sheets**, **Slack**)
4. Follow OAuth flow to authorize

**What to Check**:
- [ ] App catalog loads
- [ ] OAuth popup opens
- [ ] After auth, app shows as "Connected" with green checkmark
- [ ] Dashboard stats update (Connected Apps +1)

**Backend Verification**:
```bash
bench --site home.localhost console

# Check App Connection created
frappe.get_all('App Connection',
    filters={'user': 'your@email.com'},
    fields=['app_id', 'is_active', 'n8n_credential_id']
)
```

**Expected Behavior**:
- OAuth credentials synced to n8n automatically
- `n8n_credential_id` populated in App Connection
- Can connect multiple apps before creating workflow

---

### Step 3: Create Workflow (The Big Test!) 🚀

**URL**: `http://home.localhost:8080/workflow/create`

**This tests the complete n8n integration!**

#### Step 3.1: Name Your Workflow
- Enter workflow name (e.g., "Gmail to Sheets Sync")
- Enter description (optional)
- Click **Next**

#### Step 3.2: Choose Source App
- Select source app from connected apps (e.g., **Gmail**)
- **🔍 TEST RESOURCE DISCOVERY**:
  - Click dropdown to see resources
  - Should load **real mailboxes** from your Gmail account via n8n
  - Check browser console for API call: `lodgeick.api.resources.get_app_resources`
- Select a resource (e.g., "INBOX")
- Click **Next**

**Backend Check**:
```bash
# Test resource discovery manually
bench --site home.localhost console

from lodgeick.api.resources import get_app_resources
result = get_app_resources('gmail')
print(result)  # Should show real mailboxes, not just hardcoded list
```

#### Step 3.3: Choose Destination App
- Select destination app (e.g., **Google Sheets**)
- **🔍 TEST RESOURCE DISCOVERY**:
  - Click dropdown to see resources
  - Should load **real spreadsheets** from your Google Drive via n8n
- Select a resource (e.g., specific spreadsheet)
- Click **Next**

#### Step 3.4: Select Source Fields
- **🔍 TEST FIELD DISCOVERY**:
  - Should show Gmail fields: from, to, subject, body, date, labels, attachments
  - These come from `get_resource_fields()` API
- Select fields to sync (e.g., "from", "subject", "date")
- Click **Next**

#### Step 3.5: Select Destination Fields
- Shows Google Sheets columns
- Select matching columns (e.g., Column A, Column B, Column C)
- Click **Next**

#### Step 3.6: Map Fields
- **Visual field mapping interface**
- Drag/connect source fields to destination fields
- Example mappings:
  - Gmail "from" → Sheets "Column A"
  - Gmail "subject" → Sheets "Column B"
  - Gmail "date" → Sheets "Column C"
- Click **Next**

#### Step 3.7: Configure Trigger
- **Choose trigger type**:
  - ⏱️ **Manual**: Run workflow manually
  - 📅 **Schedule**: Set interval (15min, hourly, daily, weekly)
  - ⚡ **Real-time**: Webhook-based instant sync
- Select schedule if using schedule trigger
- Click **Create Workflow**

---

### Step 4: Verify Workflow Creation ✅

**What Happens After "Create Workflow"**:

1. **Frontend** (`WorkflowBuilder.vue`):
   - Prepares config object with all selections
   - Calls `lodgeick.api.n8n.create_integration`
   - Shows success toast with workflow ID

2. **Backend** (`lodgeick/api/n8n.py`):
   - Creates User Integration doctype
   - Triggers `after_insert` hook

3. **N8N Sync** (`lodgeick/services/n8n_sync.py`):
   - Builds n8n workflow JSON from config
   - Creates nodes: Trigger → Source → Field Mapping → Target
   - Syncs to n8n via REST API
   - Returns n8n workflow ID

**Check UI**:
- [ ] Success message appears: "Workflow 'Gmail to Sheets Sync' created and synced to n8n! 🎉"
- [ ] Redirects to dashboard
- [ ] Dashboard stats update (Active Integrations +1)

**Check Backend**:
```bash
bench --site home.localhost console

# Check User Integration created
integration = frappe.get_last_doc('User Integration')
print(f"Flow Name: {integration.flow_name}")
print(f"Source: {integration.source_app}")
print(f"Target: {integration.target_app}")
print(f"n8n Workflow ID: {integration.workflow_id}")  # Should have ID!
print(f"Status: {integration.status}")
print(f"Config: {integration.config}")
```

**Check n8n Directly**:
1. Open n8n UI: `http://localhost:5678` (or your n8n URL)
2. Go to **Workflows** tab
3. Look for workflow named: **"Lodgeick: Gmail to Sheets Sync"**
4. Open the workflow
5. **Verify**:
   - [ ] Has 4 nodes: Trigger, Gmail Source, Field Mapping (Set node), Sheets Target
   - [ ] Nodes are connected correctly
   - [ ] Trigger node configured (Manual/Schedule/Webhook)
   - [ ] Gmail node has your credential attached
   - [ ] Sheets node has your credential attached
   - [ ] Set node has field mappings
   - [ ] Workflow is Active (if integration status is "Active")

---

## Test Scenarios

### Scenario A: Manual Workflow Test
1. Create workflow with **Manual trigger**
2. Go to n8n workflow
3. Click **"Execute Workflow"** button
4. Watch it fetch Gmail data → map fields → write to Sheets
5. Check Google Sheets - new rows should appear!
6. Go back to Lodgeick dashboard
7. **Data Synced Today** should increment by 1

### Scenario B: Scheduled Workflow Test
1. Create workflow with **Schedule trigger** (15min interval)
2. Wait 15 minutes
3. Check n8n execution history
4. Go to Lodgeick dashboard
5. **Data Synced Today** should show executions
6. **Last Sync** should show relative time

### Scenario C: Resource Discovery with No n8n
1. Stop n8n service
2. Try to create workflow
3. Should still work with fallback resources
4. Gmail shows: INBOX, SENT, DRAFTS, SPAM, TRASH (hardcoded fallbacks)
5. No errors, graceful degradation

### Scenario D: Multiple Workflows
1. Create 3 different workflows
2. Dashboard shows **Active Integrations: 3**
3. All workflows appear in n8n
4. Each has unique workflow ID
5. Dashboard aggregates executions from all workflows

---

## Debugging Tips

### Check Browser Console
```javascript
// Should see these API calls:
// 1. Dashboard stats
GET lodgeick.api.integrations.get_dashboard_stats

// 2. Resource discovery
GET lodgeick.api.resources.get_app_resources?app_id=gmail

// 3. Field schema
GET lodgeick.api.resources.get_resource_fields?app_id=gmail&resource_id=INBOX

// 4. Workflow creation
POST lodgeick.api.n8n.create_integration
```

### Check Backend Logs
```bash
# Watch logs in real-time
tail -f /home/ben/frappe_docker/development/frappe-bench/logs/web.log

# Look for:
# - "Created n8n workflow {id} for integration {name}"
# - "Synced {provider} credentials to n8n for user {user}"
# - Any errors in n8n_sync or n8n_client
```

### Check n8n API Directly
```bash
# Test n8n API connection
curl -H "X-N8N-API-KEY: your-api-key" http://localhost:5678/api/v1/workflows

# Get workflow details
curl -H "X-N8N-API-KEY: your-api-key" http://localhost:5678/api/v1/workflows/{workflow_id}

# Get executions
curl -H "X-N8N-API-KEY: your-api-key" http://localhost:5678/api/v1/executions?workflowId={workflow_id}
```

### Common Issues

**Issue**: Dashboard stats show 0 even with workflows
- **Fix**: Check n8n API connection in site_config.json
- **Fix**: Verify workflows have `workflow_id` field populated
- **Fix**: Check error logs for n8n API errors

**Issue**: Resource discovery shows fallback data instead of real data
- **Fix**: Verify `n8n_credential_id` exists in App Connection
- **Fix**: Check OAuth token synced to n8n
- **Fix**: Verify n8n API key has correct permissions

**Issue**: Workflow created but not in n8n
- **Fix**: Check User Integration `workflow_id` field
- **Fix**: Check n8n_sync.py logs for errors
- **Fix**: Verify n8n API URL is correct

---

## Quick Test Checklist

Use this for rapid testing:

- [ ] Dashboard loads and shows stats
- [ ] Connect 2 apps (Gmail, Google Sheets)
- [ ] Both apps show n8n_credential_id
- [ ] Create workflow button appears on dashboard
- [ ] Click "Create Workflow"
- [ ] Step 2: Gmail resources load from n8n (not just INBOX/SENT)
- [ ] Step 3: Google Sheets resources load from n8n
- [ ] Step 4: Source fields appear
- [ ] Step 5: Destination fields appear
- [ ] Step 6: Field mapping interface works
- [ ] Step 7: Trigger options appear
- [ ] Click "Create Workflow"
- [ ] Success message shows with workflow ID
- [ ] Dashboard stats increment
- [ ] n8n has new workflow with correct nodes
- [ ] Execute workflow in n8n - data syncs!
- [ ] Dashboard "Data Synced Today" increments

---

## Expected Results Summary

### ✅ What Should Work Now

1. **Real Resource Discovery**: Gmail mailboxes, Google Sheets, Slack channels from n8n API
2. **Complete Workflow Creation**: Creates actual n8n workflows with all nodes
3. **Trigger Support**: Manual, Schedule (cron), Webhook triggers
4. **Field Mapping**: Lodgeick mappings become n8n Set nodes
5. **Dashboard Stats**: Real execution counts and timestamps from n8n
6. **Graceful Fallback**: Works with sensible defaults if n8n unavailable

### 🎯 Key Success Indicators

- User Integration has `workflow_id` populated
- n8n UI shows "Lodgeick: {workflow_name}" workflows
- Workflows have 4 connected nodes
- Credentials attached to nodes
- Executions appear in n8n history
- Dashboard stats match n8n execution data

---

## Need Help?

If something doesn't work:

1. Check browser console for errors
2. Check backend logs: `logs/web.log`
3. Test n8n API manually with curl
4. Verify site_config.json has correct n8n settings
5. Check User Integration and App Connection doctypes in backend

**Everything is now reading from, updating, and implementing in n8n!** 🎉
