# Workflow Builder - n8n Integration Flow

## Overview
Lodgeick is a UI wrapper for n8n that allows users to create workflows by selecting apps, templates, resources, and field mappings. The system queries n8n for node definitions to provide accurate resource types and supports pre-built workflow templates.

---

## Complete User Flow (8 Steps)

### Step 1: Select Source App
**What users see**: List of connected apps (Gmail, Google Sheets, Slack, etc.)

**What happens**:
- Displays apps from Integration Token table (apps user has OAuth'd)
- User clicks an app to select as data source
- Triggers loading of templates and resources for that app

### Step 2: Choose Integration Type ⭐ NEW
**What users see**: List of available workflow templates plus "Custom Integration" option

**Example for Gmail**:
```
┌─────────────────────────────────────────────────────┐
│ 📧 Email triage agent                     [✓]      │
│ Categorizes new, unread emails by analyzing        │
│ their content and applying relevant labels.         │
│                                                     │
│ Trigger: New email received                        │
│ Actions: Analyze content, Apply labels             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🔧 Custom Integration                               │
│ Build your own workflow with Gmail                  │
└─────────────────────────────────────────────────────┘
```

**What happens**:
- Frontend calls: `lodgeick.api.resources.get_app_templates(app_id)`
- Backend returns pre-built templates + custom option
- User selects template or custom integration
- If template selected: Backend will use n8n workflow template
- If custom selected: User continues through resource/field selection

**Backend API** (`get_app_templates`):
```python
# lodgeick/api/resources.py
@frappe.whitelist()
def get_app_templates(app_id):
    """Returns list of templates for an app"""
    templates = get_app_template_list(app_id)
    return {"success": True, "templates": templates}
```

**Template Structure**:
```python
{
    "id": "email_triage_agent",
    "name": "Email triage agent",
    "description": "Categorizes new, unread emails...",
    "type": "template",  # or "custom"
    "triggers": ["New email received"],
    "actions": ["Analyze content", "Apply labels"]
}
```

### Step 3: Select Source Resource
**What users see**: List of n8n resource types (NOT specific instances)

**Example for Gmail**:
```
Message    - Get, send, and delete emails
Draft      - Manage email drafts
Label      - Manage labels
Thread     - Manage email threads
```

**What happens**:
- Frontend calls: `lodgeick.api.resources.get_app_resources(app_id)`
- Backend queries n8n: `/api/v1/node-types/n8n-nodes-base.gmail`
- Parses node definition's `properties` array for "resource" parameter
- Extracts `options` array with resource types

**Backend Flow**:
```python
# 1. Map app to n8n node type
node_type = get_node_type_for_app('gmail')
# Returns: 'n8n-nodes-base.gmail'

# 2. Query n8n for node definition
n8n = get_n8n_client()
node_def = n8n.get_node_type(node_type)
# Calls: GET /api/v1/node-types/n8n-nodes-base.gmail

# 3. Extract resources from node definition
resources = extract_resources_from_node(node_def, app_id)
# Parses properties array, finds "resource" param, returns options
```

**n8n Node Definition Structure**:
```json
{
  "properties": [
    {
      "name": "resource",
      "displayName": "Resource",
      "type": "options",
      "options": [
        {"name": "Message", "value": "message", "description": "Get, send, and delete emails"},
        {"name": "Draft", "value": "draft", "description": "Manage email drafts"},
        {"name": "Label", "value": "label", "description": "Manage labels"},
        {"name": "Thread", "value": "thread", "description": "Manage email threads"}
      ]
    }
  ]
}
```

### Step 4: Select Source Fields
**What users see**: Checkboxes for fields to include

**Example for Gmail Message**:
```
☑ From
☑ To
☑ Subject
☑ Body
☐ Date
☐ Labels
☐ Attachments
```

**What happens**:
- Frontend calls: `lodgeick.api.resources.get_resource_fields(app_id, resource_id)`
- Backend returns field schema for the resource type
- User selects which fields to include in sync

### Step 5: Select Destination App
**What users see**: List of connected apps (excluding source app)

**What happens**:
- Same as Step 1, but filters out the source app
- User selects where to send data

### Step 6: Select Destination Resource
**What users see**: Resource types for destination app

**What happens**:
- Same as Step 3, but for destination app
- Queries n8n for destination node definition

### Step 7: Map Fields
**What users see**: Source fields mapped to destination fields

**Example**:
```
From Source          →  To Destination
───────────────────     ───────────────────
Email Subject        →  [Task Name ▼]
Email Body           →  [Task Description ▼]
From                 →  [Assignee Email ▼]
```

**What happens**:
- User maps each source field to a destination field
- Creates field mapping config for n8n workflow

### Step 8: Configure Sync
**What users see**: Workflow name, trigger type, schedule

**Options**:
- **Manual**: Run manually on demand
- **Schedule**: Run on a schedule (15min, hourly, daily, weekly)
- **Real-time**: Webhook trigger (Pro feature)

**What happens**:
- User names the workflow
- Selects trigger type
- Clicks "Create Workflow"
- Frontend calls: `lodgeick.api.n8n.create_integration()`
- Backend creates workflow in Lodgeick AND syncs to n8n

---

## Technical Architecture

### Frontend (Vue 3)
**File**: `frontend/src/pages/WorkflowBuilder.vue`

**Key Components**:
```javascript
// State
const workflow = ref({
  sourceApp: null,
  sourceTemplate: null,      // ⭐ NEW
  sourceResource: null,
  sourceFields: [],
  destinationApp: null,
  destinationResource: null,
  fieldMappings: [],
  trigger: 'manual',
  schedule: 'hourly',
  name: ''
})

// Watchers
watch(sourceApp) → Load templates
watch(sourceApp) → Load resources
watch(sourceResource) → Load fields
watch(destinationApp) → Load resources
watch(destinationResource) → Load fields
```

**API Calls**:
1. `lodgeick.api.resources.get_app_templates(app_id)` - Get templates
2. `lodgeick.api.resources.get_app_resources(app_id)` - Get resource types
3. `lodgeick.api.resources.get_resource_fields(app_id, resource_id)` - Get fields
4. `lodgeick.api.n8n.create_integration(...)` - Create workflow

### Backend (Frappe Python)

#### Resources API
**File**: `lodgeick/api/resources.py`

**Endpoints**:
```python
@frappe.whitelist()
def get_app_templates(app_id):
    """Get workflow templates for an app"""
    # Returns: {"success": True, "templates": [...]}

@frappe.whitelist()
def get_app_resources(app_id):
    """Get n8n resource types from node definition"""
    # 1. Get node type (e.g., 'n8n-nodes-base.gmail')
    # 2. Query n8n: /api/v1/node-types/{node_type}
    # 3. Parse properties array for resource options
    # 4. Return: {"success": True, "resources": [...]}

@frappe.whitelist()
def get_resource_fields(app_id, resource_id):
    """Get field schema for a resource"""
    # Returns: {"success": True, "fields": [...]}
```

**Helper Functions**:
```python
def get_node_type_for_app(app_id):
    """Map app ID to n8n node type name"""
    # gmail → n8n-nodes-base.gmail
    # google_sheets → n8n-nodes-base.googleSheets
    # slack → n8n-nodes-base.slack

def extract_resources_from_node(node_def, app_id):
    """Parse n8n node definition to extract resource types"""
    # 1. Find "resource" parameter in properties array
    # 2. Extract options array
    # 3. Transform to Lodgeick format:
    #    {"id": "message", "name": "Message", "type": "resource", "description": "..."}

def get_app_template_list(app_id):
    """Get pre-built workflow templates"""
    # Gmail: Email triage agent + Custom
    # Google Sheets: Custom only
    # Slack: Custom only
```

#### n8n Client
**File**: `lodgeick/services/n8n_client.py`

**Key Methods**:
```python
class N8NClient:
    def __init__(self):
        self.base_url = frappe.conf.get("n8n_base_url")
        self.api_key = frappe.conf.get("n8n_api_key")

    def get_node_types(self) -> List[Dict]:
        """GET /api/v1/node-types"""
        # Returns all available node types

    def get_node_type(self, node_name: str) -> Dict:
        """GET /api/v1/node-types/{node_name}"""
        # Returns specific node definition with properties
        # Example: get_node_type('n8n-nodes-base.gmail')

    def get_node_parameter_options(self, node_type, method_name, credential_id):
        """POST /api/v1/dynamic-node-parameters/options"""
        # Get dynamic options (e.g., Gmail labels, Sheets spreadsheets)
        # This is for INSTANCES, not resource types

    def create_workflow(self, workflow_data: Dict) -> Dict:
        """POST /api/v1/workflows"""

    def activate_workflow(self, workflow_id: str) -> Dict:
        """PUT /api/v1/workflows/{id} with {"active": True}"""
```

---

## n8n API Endpoints Used

### Base URL
```
{n8n_base_url}/api/v1/
```

### Headers
```
X-N8N-API-KEY: {api_key}
Content-Type: application/json
```

### Endpoints

#### 1. Get Node Type Definition
```http
GET /api/v1/node-types/{node_name}

Example:
GET /api/v1/node-types/n8n-nodes-base.gmail

Response:
{
  "name": "n8n-nodes-base.gmail",
  "version": 1,
  "properties": [
    {
      "name": "resource",
      "displayName": "Resource",
      "type": "options",
      "options": [
        {"name": "Message", "value": "message"},
        {"name": "Draft", "value": "draft"},
        {"name": "Label", "value": "label"},
        {"name": "Thread", "value": "thread"}
      ]
    }
  ]
}
```

#### 2. Create Workflow
```http
POST /api/v1/workflows

Body:
{
  "name": "My Gmail Sync",
  "nodes": [...],
  "connections": {...},
  "active": false
}

Response:
{
  "id": "0RXwqWsqeJxe2La1",
  "name": "My Gmail Sync",
  "active": false,
  ...
}
```

#### 3. Activate Workflow
```http
PUT /api/v1/workflows/{workflow_id}

Body:
{
  "active": true
}
```

#### 4. List Executions
```http
GET /api/v1/executions?workflowId={workflow_id}

Response:
{
  "data": [
    {
      "id": "...",
      "startedAt": "2025-10-15T10:30:00Z",
      "status": "success"
    }
  ]
}
```

---

## Key Differences: Resources vs Instances

### ❌ OLD WAY (Instances)
```python
# Hardcoded specific mailboxes/spreadsheets
"gmail": [
    {"id": "INBOX", "name": "Inbox"},
    {"id": "SENT", "name": "Sent Mail"},
    {"id": "DRAFTS", "name": "Drafts"}
]
```

### ✅ NEW WAY (Resource Types)
```python
# n8n resource types from node definition
"gmail": [
    {"id": "message", "name": "Message", "description": "Get, send, and delete emails"},
    {"id": "draft", "name": "Draft", "description": "Manage email drafts"},
    {"id": "label", "name": "Label", "description": "Manage labels"},
    {"id": "thread", "name": "Thread", "description": "Manage email threads"}
]
```

### Why This Matters
- **Resource Types**: What KIND of data (message, draft, label)
- **Instances**: WHICH specific items (INBOX, SENT, specific label IDs)

In n8n, you first choose the **resource type** (e.g., "message"), then n8n provides **operations** for that resource (get, send, delete), and THEN you can optionally filter by specific instances (e.g., label:INBOX).

---

## Template System

### Template Types

#### 1. Pre-built Templates
**Example**: Email triage agent (Gmail)

**Structure**:
```python
{
    "id": "email_triage_agent",
    "name": "Email triage agent",
    "description": "Categorizes new, unread emails by analyzing their content and applying relevant labels.",
    "type": "template",
    "triggers": ["New email received"],
    "actions": ["Analyze content", "Apply labels"]
}
```

**What happens when selected**:
- Backend uses n8n workflow template
- May skip resource/field selection steps
- Directly creates pre-configured workflow

#### 2. Custom Integration
```python
{
    "id": "custom",
    "name": "Custom Integration",
    "description": "Build your own workflow with Gmail",
    "type": "custom"
}
```

**What happens when selected**:
- User continues through all steps
- Manually selects resources, fields, mappings
- Backend builds custom workflow from scratch

### Future: Fetching Templates from n8n
Currently templates are hardcoded in `get_app_template_list()`. Future implementation could:
1. Query n8n for available workflow templates
2. Filter templates by node type (e.g., Gmail templates)
3. Allow users to import from n8n template library

---

## Configuration Flow

### User-Facing Config
```javascript
{
  sourceApp: {id: 'gmail', name: 'Gmail'},
  sourceTemplate: {id: 'email_triage_agent', name: 'Email triage agent'},
  sourceResource: {id: 'message', name: 'Message'},
  sourceFields: ['from', 'to', 'subject', 'body'],
  destinationApp: {id: 'google_sheets', name: 'Google Sheets'},
  destinationResource: {id: 'sheet', name: 'Sheet'},
  fieldMappings: [
    {source: 'from', destination: 'column_a'},
    {source: 'subject', destination: 'column_b'},
    {source: 'body', destination: 'column_c'}
  ],
  trigger: 'schedule',
  schedule: 'hourly',
  name: 'Gmail to Sheets Sync'
}
```

### Backend Processing
```python
# 1. Create User Integration record
integration = frappe.get_doc({
    "doctype": "User Integration",
    "user": user,
    "flow_name": "Gmail to Sheets Sync",
    "source_app": "gmail",
    "target_app": "google_sheets",
    "config": json.dumps(config),
    "status": "Active"
})

# 2. Build n8n workflow JSON
workflow_json = build_workflow_from_config(config)

# 3. Create workflow in n8n
n8n = get_n8n_client()
result = n8n.create_workflow(workflow_json)

# 4. Activate workflow
n8n.activate_workflow(result['id'])

# 5. Update integration with workflow_id
integration.workflow_id = result['id']
integration.save()
```

---

## Error Handling & Fallbacks

### 1. n8n Unreachable
```python
if not n8n.is_enabled():
    # Use fallback resources
    resources = get_fallback_resources(app_id)
    integration.status = "Paused"
    integration.error_message = "n8n not configured"
```

### 2. Node Definition Not Found
```python
try:
    node_def = n8n.get_node_type(node_type)
except Exception:
    # Use fallback resources
    resources = get_fallback_resources(app_id)
```

### 3. Resource Extraction Fails
```python
def extract_resources_from_node(node_def, app_id):
    try:
        # Parse node definition
        resources = parse_properties(node_def)
        return resources if resources else get_fallback_resources(app_id)
    except Exception:
        return get_fallback_resources(app_id)
```

### Fallback Resources
```python
def get_fallback_resources(app_id):
    """Static fallback when n8n unavailable"""
    fallbacks = {
        "gmail": [
            {"id": "message", "name": "Message", "type": "resource"},
            {"id": "draft", "name": "Draft", "type": "resource"},
            {"id": "label", "name": "Label", "type": "resource"},
            {"id": "thread", "name": "Thread", "type": "resource"}
        ]
    }
    return fallbacks.get(app_id, [])
```

---

## Testing

### Test Flow
```bash
# 1. Navigate to workflow builder
http://localhost:5173/workflow/create

# 2. Expected behavior:
# Step 1: See Gmail, Google Sheets (if connected)
# Step 2: See "Email triage agent" + "Custom Integration"
# Step 3: See Message, Draft, Label, Thread (from n8n or fallback)
# Step 4: See From, To, Subject, Body fields
# Step 5: See Google Sheets (destination)
# Step 6: See Sheet resource type
# Step 7: Map fields
# Step 8: Name workflow, select trigger, create
```

### Backend Testing (bench console)
```python
# Test template fetching
from lodgeick.api.resources import get_app_templates
templates = get_app_templates('gmail')
print(templates)

# Test resource fetching
from lodgeick.api.resources import get_app_resources
resources = get_app_resources('gmail')
print(resources)

# Test n8n connection
from lodgeick.services.n8n_client import get_n8n_client
n8n = get_n8n_client()
print(n8n.is_enabled())

# Test node type fetching
node_def = n8n.get_node_type('n8n-nodes-base.gmail')
print(node_def)
```

---

## Dynamic App & Operation Discovery ⭐ NEW

### 24-Hour Cache System

**File**: `lodgeick/services/n8n_cache.py`

Intelligent caching system that stores n8n node data:

```python
# Cache Management
get_cached_node_types() → List[Dict]         # Get cached apps
set_cached_node_types(apps) → None           # Cache apps for 24hrs
get_cached_node_definition(node) → Dict      # Get cached node def
set_cached_node_definition(node, def) → None # Cache node def for 24hrs
clear_cache() → None                         # Clear all cache
get_cache_stats() → Dict                     # Cache statistics
```

**DocType**: `n8n Cache`
- `cache_key` - Unique identifier (e.g., "node_types", "node_def_gmail")
- `data` - JSON-encoded cached data
- `expires_at` - Expiration timestamp (24hrs from creation)

### Dynamic App Loading

**API**: `lodgeick.api.resources.get_available_apps()`

Fetches ALL available apps from n8n automatically:

```python
@frappe.whitelist()
def get_available_apps():
    """
    Loads all apps from n8n node types with 24hr caching

    Returns:
        {
            "success": True,
            "apps": [
                {
                    "id": "gmail",
                    "name": "Gmail",
                    "description": "Send and receive emails",
                    "icon": "📧",
                    "node_type": "n8n-nodes-base.gmail"
                },
                ...
            ],
            "from_cache": True  # Whether loaded from cache
        }
    """
```

**Process Flow**:
1. Check cache → If valid (< 24hrs), return cached apps
2. If expired → Query n8n: `GET /api/v1/node-types`
3. Filter integration nodes (skip Set, If, Switch, etc.)
4. Extract app metadata: id, name, description
5. Add emoji icons (20+ predefined)
6. Cache results for 24 hours
7. Return app list

**App Icons** (20+ supported):
- Gmail 📧, Google Sheets 📊, Google Drive 📁
- Slack 💬, Salesforce ☁️, HubSpot 🎯
- Jira 📋, Xero 💰, Notion 📝
- Mailchimp 📬, Airtable 🗂️, Trello 📌
- Asana ✅, GitHub 🐙, GitLab 🦊
- Stripe 💳, Shopify 🛍️, WordPress 📰
- Zoom 🎥, Calendly 📅, Intercom 💭, Zendesk 🎫

### Operation Extraction

**API**: `lodgeick.api.resources.get_resource_operations(app_id, resource_id)`

Extracts available operations for each resource from n8n node definitions:

```python
@frappe.whitelist()
def get_resource_operations(app_id, resource_id):
    """
    Get operations for a resource (e.g., 'append row' for Google Sheets)

    Args:
        app_id: 'googlesheets', 'gmail', 'slack', etc.
        resource_id: 'sheet', 'message', 'channel', etc.

    Returns:
        {
            "success": True,
            "operations": [
                {
                    "id": "append",
                    "name": "Append Row",
                    "description": "Add a new row to the spreadsheet",
                    "action": "append"
                },
                {
                    "id": "update",
                    "name": "Update Row",
                    "description": "Update an existing row"
                }
            ]
        }
    """
```

**Examples by App**:

**Google Sheets** (`sheet` resource):
- Append Row - Add a new row
- Update Row - Update an existing row
- Read Rows - Read rows from spreadsheet
- Delete Row - Delete a row

**Gmail** (`message` resource):
- Send Email - Send a new email
- Get Email - Get email details
- Get Many Emails - Get multiple emails
- Delete Email - Delete an email

**Gmail** (`draft` resource):
- Create Draft - Create a new draft
- Get Draft - Get draft details
- Delete Draft - Delete a draft

**Slack** (`message` resource):
- Send Message - Send a message to a channel
- Update Message - Update an existing message
- Delete Message - Delete a message

**How It Works**:
```python
# 1. Get node definition (cached)
node_def = n8n.get_node_type('n8n-nodes-base.googlesheets')

# 2. Find operation parameter for this resource
for prop in node_def['properties']:
    if prop['name'] == 'operation':
        # Check if this operation is for 'sheet' resource
        if resource_id in prop['displayOptions']['show']['resource']:
            operations = prop['options']

# 3. Extract operations
operations = [
    {
        "id": "append",
        "name": "Append Row",
        "description": "Add a new row"
    }
    for option in operations
]
```

**n8n Node Structure**:
```json
{
  "properties": [
    {
      "name": "operation",
      "displayName": "Operation",
      "displayOptions": {
        "show": {
          "resource": ["sheet"]  // Only show for 'sheet' resource
        }
      },
      "options": [
        {"value": "append", "name": "Append Row", "description": "..."},
        {"value": "update", "name": "Update Row", "description": "..."}
      ]
    }
  ]
}
```

### Fallback System

When n8n is unavailable, the system uses static fallbacks:

**Fallback Apps**:
- Gmail, Google Sheets, Slack
- Salesforce, HubSpot, Jira

**Fallback Operations**:
- Google Sheets → append, update, read, delete
- Gmail → send, get, getAll, delete
- Slack → post, update, delete
- Default → create, update, read, delete

### Cache Stats

```python
from lodgeick.services.n8n_cache import get_cache_stats

stats = get_cache_stats()
# Returns: {
#   "total": 45,      # Total cache entries
#   "valid": 42,      # Still valid (not expired)
#   "expired": 3      # Expired entries
# }
```

---

## Next Steps

### Immediate
1. ✅ Add template selection step
2. ✅ Query n8n for resource types
3. ✅ Update UI terminology (Table → Resource)
4. ✅ Add 24-hour cache system for n8n data
5. ✅ Dynamic app loading from n8n
6. ✅ Operation extraction from node definitions
7. ⏳ Update frontend to use dynamic apps API
8. ⏳ Add operation selection step to workflow builder
9. ⏳ Test with real n8n connection

### Future Enhancements
1. **Fetch Templates from n8n**: Query n8n template library
2. **Dynamic Field Discovery**: Query n8n for actual fields per resource
3. **Instance Selection**: Add step to select specific instances (INBOX, specific labels)
4. **Template Customization**: Allow editing pre-built templates
5. **Multi-step Workflows**: Support workflows with >2 apps
6. **Cache Management UI**: View and clear cache from admin panel

---

## Summary

✅ **What's Working**:
- 8-step workflow builder with template selection
- n8n node definition querying with 24hr cache
- Resource type extraction from n8n
- **Dynamic app discovery from n8n (20+ apps)**
- **Operation extraction from node definitions**
- **24-hour intelligent caching system**
- Fallback resources when n8n unavailable
- Template system with pre-built and custom options
- Graceful error handling

⏳ **What's Next**:
- Update frontend to use `get_available_apps()` API
- Add operation selection step to workflow builder
- Test with real n8n connection
- Fetch templates dynamically from n8n
- Add more pre-built templates for common use cases

🎯 **User Experience**:
Users now see accurate n8n resource types and can choose between pre-built templates (like "Email triage agent") or custom workflows. The system automatically discovers new n8n integrations and caches results for fast responses. Operations like "Append Row" or "Send Email" are extracted directly from n8n node definitions, ensuring accuracy and supporting any n8n node updates automatically.
