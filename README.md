# Lodgeick - One-Click Integration Platform

**Lodgeick** is a modern SaaS integration platform that provides simple, one-click integrations between popular business applications. Built on Frappe Framework with a Vue.js frontend and n8n workflow orchestration.

## 🎯 Overview

Lodgeick eliminates the complexity of connecting your favorite business tools. Users select an app, choose a use case, authorize their accounts, and let the platform handle the rest.

### Key Features

- ✅ **One-Click Integration Setup** - No workflow building required
- 🎯 **Three-Tier OAuth System** - Choose your setup style: Quick Start, AI-Powered, or Manual
- 🤖 **AI-Powered Google Setup** - Natural language to Google Cloud integration
- 🔐 **Secure OAuth Authentication** - Enterprise-grade token management
- 📊 **Real-time Monitoring** - Track integration status and execution logs
- ⚡ **Smart Rate Limiting** - Automatic usage tracking and quota management
- 🎨 **Beautiful Vue.js Frontend** - Modern, responsive UI with Tailwind CSS
- 🔄 **n8n Workflow Engine** - Powerful automation behind the scenes
- 🚀 **50+ App Catalog** - Popular business applications ready to connect
- 💡 **Smart Billing Detection** - Only prompts for billing when actually required
- ⚙️ **Integration Management** - Easy configuration and monitoring of connected apps
- 🔀 **Visual Workflow Builder** - Step-by-step wizard for creating custom data sync workflows with field mapping

## 🏗️ Architecture

```
Vue Frontend → Frappe Backend → n8n Workflows
  (UI/UX)      (API/OAuth/DB)    (Orchestration)
```

### Tech Stack

- **Frontend**: Vue 3 + Vite + Tailwind CSS + frappe-ui
- **Backend**: Frappe Framework (Python)
- **Database**: MariaDB
- **Orchestration**: n8n

## 📦 Quick Start

### Install

```bash
# Get the app
bench get-app https://github.com/benjamen/lodgeick
bench --site lodgeick.com install-app lodgeick

# Install Python dependencies
pip install -r apps/lodgeick/requirements.txt
```

### Configuration

```json
// Add to site_config.json
{
  "anthropic_api_key": "sk-ant-api03-...",  // For AI-powered setup
  "google_cloud_service_account": {...},    // For automated project creation
  "n8n_base_url": "http://localhost:5678",
  "n8n_api_key": "your-api-key"
}
```

### Development

```bash
cd apps/lodgeick/frontend
yarn install
yarn dev
```

## 📋 Core DocTypes

- **Integration Token** - Secure OAuth token storage
- **User Integration** - Active integration tracking
- **User Google Project** - AI-created Google Cloud projects
- **App Catalog** - Available apps and use cases
- **Integration Log** - Execution logs

## 🔌 API Endpoints

### OAuth & Authentication
- `/api/method/lodgeick.api.oauth.*` - OAuth flows
- `/api/method/lodgeick.api.integrations.*` - Integration management

### AI-Powered Setup
- `/api/method/lodgeick.api.google_ai_setup.parse_intent` - Parse natural language
- `/api/method/lodgeick.api.google_ai_setup.create_project` - Create GCP project
- `/api/method/lodgeick.api.google_ai_setup.setup_oauth_credentials` - Setup OAuth

### Catalog
- `/api/method/lodgeick.api.catalog.*` - App catalog

## 🤖 AI-Powered Google Setup

Lodgeick includes an intelligent setup wizard for Google Cloud integrations:

1. **Natural Language Input**: "I want to read emails from Gmail and create spreadsheets"
2. **AI Analysis**: Claude AI determines required APIs and scopes
3. **Smart Setup**: Choose automated (new project) or manual (existing project)
4. **Auto n8n Sync**: Credentials automatically available in workflows

See [AI_SETUP_GUIDE.md](./AI_SETUP_GUIDE.md) for detailed documentation.

## 🎯 Three-Tier OAuth System

Lodgeick offers three flexible OAuth setup options:

### 1. Quick Start (Default Tier) ⚡
- **Setup Time**: Instant
- **Use Case**: Testing, personal projects
- **Rate Limits**: Shared (100-500 requests/day depending on API)
- **Providers**: Google, Slack, Xero, Microsoft 365, HubSpot

### 2. AI-Powered Setup (Recommended) 🤖
- **Setup Time**: ~2 minutes
- **Use Case**: Most users, production workflows
- **Rate Limits**: Unlimited (your own quotas)
- **Providers**: Google (with AI assistance)

### 3. Manual Setup (Advanced) 🔧
- **Setup Time**: ~10 minutes
- **Use Case**: Enterprises, custom configurations
- **Rate Limits**: Unlimited
- **Providers**: All supported providers

See [OAuth Tiers Guide](./OAUTH_TIERS_GUIDE.md) for detailed comparison and setup instructions.

## 🔀 Visual Workflow Builder

Lodgeick includes a powerful visual workflow builder for creating custom data sync workflows:

### Features
- **4-Step Wizard Interface** - Intuitive step-by-step workflow creation
- **Source Selection** - Choose from connected apps (Google Sheets, Airtable, Notion, etc.)
- **Destination Selection** - Pick where to send your data
- **Field Mapping** - Visual drag-and-drop field mapping between source and destination
- **Sync Configuration** - Set trigger type (manual, scheduled, real-time webhook) and frequency

### How to Use
1. Navigate to Dashboard and click "Create Workflow"
2. Select your source app and resource (e.g., Google Sheets → "Sales Leads Q1")
3. Choose your destination app and resource (e.g., Salesforce → "Leads")
4. Map fields from source to destination (e.g., "Full Name" → "First Name")
5. Configure sync trigger and frequency
6. Click "Create Workflow" to activate

### Access
- **Route**: `/workflow/create`
- **Prerequisites**: Must have 2+ apps connected
- **Authentication**: Required

## 📖 Additional Documentation

- [OAuth Tiers Guide](./OAUTH_TIERS_GUIDE.md) - Three-tier OAuth system overview
- [AI Setup Guide](./AI_SETUP_GUIDE.md) - AI-powered Google integration setup
- [OAuth Setup](./OAUTH_SETUP.md) - Manual OAuth configuration
- [N8N Integration](./N8N_INTEGRATION.md) - n8n workflow sync

## 📄 License

MIT