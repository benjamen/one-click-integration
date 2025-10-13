<template>
  <div
    class="modal fade"
    :class="{ show: show, 'd-block': show }"
    tabindex="-1"
    :style="{ backgroundColor: show ? 'rgba(0,0,0,0.5)' : '' }"
    @click.self="closeWizard"
  >
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header bg-gradient-ai">
          <h5 class="modal-title text-white font-weight-bold">
            <i class="fas fa-robot me-2"></i>
            AI-Powered Google Integration Setup
          </h5>
          <button
            type="button"
            class="btn-close btn-close-white"
            @click="closeWizard"
          ></button>
        </div>

        <!-- Body -->
        <div class="modal-body p-4">
          <!-- Step 1: Intent Input -->
          <div v-if="currentStep === 'intent'" class="step">
            <h5 class="font-weight-bold mb-3">
              <i class="fas fa-comment-dots text-primary me-2"></i>
              What do you want to integrate?
            </h5>
            <p class="text-muted">
              Describe in plain English what Google services you want to connect.
              Our AI will figure out which APIs and permissions you need.
            </p>

            <div class="mb-3">
              <label class="form-label font-weight-bold">Your Integration Request</label>
              <textarea
                v-model="userIntent"
                class="form-control"
                rows="4"
                placeholder="Example: I want to read and send emails from Gmail, and create spreadsheets in Google Sheets"
                :disabled="parsing"
              ></textarea>
              <small class="text-muted">
                Try: "Connect to Google Drive and Gmail" or "Access Google Calendar and Sheets"
              </small>
            </div>

            <div v-if="parseError" class="alert alert-danger">
              <i class="fas fa-exclamation-circle me-2"></i>
              {{ parseError }}
            </div>

            <BaseButton
              variant="primary"
              size="lg"
              full-width
              @click="parseIntent"
              :disabled="!userIntent || parsing"
              :loading="parsing"
              loading-text="AI is analyzing your request..."
              icon-left="fas fa-magic"
            >
              Analyze with AI
            </BaseButton>
          </div>

          <!-- Step 2: API Preview & Billing Check -->
          <div v-if="currentStep === 'preview'" class="step">
            <h5 class="font-weight-bold mb-3">
              <i class="fas fa-list-check text-success me-2"></i>
              AI Analysis Results
            </h5>

            <div class="alert alert-info">
              <i class="fas fa-robot me-2"></i>
              <strong>AI Reasoning:</strong> {{ parsedData.reasoning }}
            </div>

            <h6 class="font-weight-bold mt-4 mb-3">Required Google APIs:</h6>
            <div class="list-group mb-4">
              <div
                v-for="api in parsedData.apis"
                :key="api.name"
                class="list-group-item"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="mb-1">
                      <i class="fab fa-google text-primary me-2"></i>
                      {{ api.display_name }}
                    </h6>
                    <p class="mb-1 text-muted small">{{ api.description }}</p>
                    <div class="mt-2">
                      <span
                        v-for="scope in api.scopes"
                        :key="scope"
                        class="badge bg-light text-dark me-1 mb-1"
                      >
                        <code class="small">{{ scope }}</code>
                      </span>
                    </div>
                  </div>
                  <span
                    v-if="parsedData.billing_apis && parsedData.billing_apis.includes(api.name)"
                    class="badge bg-warning text-dark"
                  >
                    <i class="fas fa-credit-card me-1"></i>
                    Billing Required
                  </span>
                </div>
              </div>
            </div>

            <!-- Billing Warning -->
            <div v-if="parsedData.billing_required" class="alert alert-warning">
              <i class="fas fa-exclamation-triangle me-2"></i>
              <strong>Billing Account Required</strong>
              <p class="mb-0 mt-2">
                The following APIs require a billing account to be linked to your Google Cloud project:
                <strong>{{ parsedData.billing_apis.join(', ') }}</strong>
              </p>
              <p class="mb-0 mt-2 small">
                Make sure your Google Cloud project has billing enabled before proceeding.
              </p>
            </div>

            <!-- Setup Method Selection -->
            <div class="card mt-4">
              <div class="card-body">
                <h6 class="font-weight-bold mb-3">
                  <i class="fas fa-route text-primary me-2"></i>
                  Choose Your Setup Method
                </h6>

                <div class="row g-3">
                  <!-- Option 1: Automated Setup -->
                  <div class="col-md-6">
                    <div class="border rounded p-3 h-100" :class="{ 'border-primary bg-light': setupMethod === 'auto' }">
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="radio"
                          name="setupMethod"
                          id="autoSetup"
                          value="auto"
                          v-model="setupMethod"
                        >
                        <label class="form-check-label font-weight-bold" for="autoSetup">
                          <i class="fas fa-magic text-primary me-2"></i>
                          Automated Setup (New Project)
                        </label>
                      </div>
                      <p class="small text-muted mt-2 mb-0">
                        Let Lodgeick create a new Google Cloud project and enable APIs for you automatically.
                      </p>
                      <div class="mt-2">
                        <span class="badge bg-success me-1">Recommended</span>
                        <span class="badge bg-info">Fastest</span>
                      </div>
                    </div>
                  </div>

                  <!-- Option 2: Manual Setup -->
                  <div class="col-md-6">
                    <div class="border rounded p-3 h-100" :class="{ 'border-primary bg-light': setupMethod === 'manual' }">
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="radio"
                          name="setupMethod"
                          id="manualSetup"
                          value="manual"
                          v-model="setupMethod"
                        >
                        <label class="form-check-label font-weight-bold" for="manualSetup">
                          <i class="fas fa-hand-pointer text-warning me-2"></i>
                          Manual Setup (Existing Project)
                        </label>
                      </div>
                      <p class="small text-muted mt-2 mb-0">
                        I already have a Google Cloud project and want to use my existing setup.
                      </p>
                      <div class="mt-2">
                        <span class="badge bg-secondary">Advanced</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex gap-2 mt-4">
              <BaseButton
                variant="secondary"
                @click="currentStep = 'intent'"
                icon-left="fas fa-arrow-left"
              >
                Back
              </BaseButton>
              <BaseButton
                variant="primary"
                full-width
                @click="proceedToSetup"
                :disabled="!setupMethod"
                icon-left="fas fa-arrow-right"
              >
                Continue with {{ setupMethod === 'auto' ? 'Automated' : 'Manual' }} Setup
              </BaseButton>
            </div>

            <!-- Project Name Input for Auto Setup -->
            <div v-if="showProjectNameInput && setupMethod === 'auto'" class="mt-3 p-3 border rounded bg-light">
              <h6 class="font-weight-bold mb-3">
                <i class="fas fa-folder-plus me-2"></i>
                Name Your New Project
              </h6>
              <input
                v-model="projectName"
                type="text"
                class="form-control mb-3"
                placeholder="e.g., My Lodgeick Integration"
              >
              <small class="text-muted d-block mb-3">
                A unique project ID will be generated automatically
              </small>
              <BaseButton
                variant="success"
                full-width
                @click="createProject"
                :disabled="!projectName || creatingProject"
                :loading="creatingProject"
                loading-text="Creating project and enabling APIs..."
                icon-left="fas fa-rocket"
              >
                Create Google Cloud Project
              </BaseButton>
            </div>
          </div>

          <!-- Step 2b: Manual Setup Instructions -->
          <div v-if="currentStep === 'manual_instructions'" class="step">
            <h5 class="font-weight-bold mb-3">
              <i class="fas fa-list-ol text-primary me-2"></i>
              Manual Setup Instructions
            </h5>

            <div class="alert alert-info">
              <i class="fas fa-info-circle me-2"></i>
              Follow these steps in your Google Cloud Console to set up the required APIs and OAuth credentials.
            </div>

            <div class="card mb-3">
              <div class="card-header bg-light">
                <h6 class="mb-0 font-weight-bold">
                  <i class="fas fa-project-diagram me-2"></i>
                  Step 1: Use Existing or Create New Project
                </h6>
              </div>
              <div class="card-body">
                <ol class="mb-0">
                  <li class="mb-2">
                    Go to
                    <a href="https://console.cloud.google.com" target="_blank" class="text-primary">
                      Google Cloud Console
                      <i class="fas fa-external-link-alt ms-1 small"></i>
                    </a>
                  </li>
                  <li class="mb-2">Select an existing project or create a new one</li>
                  <li>Copy your project ID (you'll need it later)</li>
                </ol>
              </div>
            </div>

            <div class="card mb-3">
              <div class="card-header bg-light">
                <h6 class="mb-0 font-weight-bold">
                  <i class="fas fa-toggle-on me-2"></i>
                  Step 2: Enable Required APIs
                </h6>
              </div>
              <div class="card-body">
                <ol class="mb-2">
                  <li class="mb-2">
                    Go to
                    <a href="https://console.cloud.google.com/apis/library" target="_blank" class="text-primary">
                      APIs & Services > Library
                      <i class="fas fa-external-link-alt ms-1 small"></i>
                    </a>
                  </li>
                  <li class="mb-2">Enable these APIs in your project:</li>
                </ol>
                <div class="mt-2">
                  <div v-for="api in parsedData.apis" :key="api.name" class="mb-2">
                    <span class="badge bg-primary me-2">{{ api.display_name }}</span>
                    <code class="small text-muted">{{ api.name }}</code>
                  </div>
                </div>
              </div>
            </div>

            <div class="card mb-3">
              <div class="card-header bg-light">
                <h6 class="mb-0 font-weight-bold">
                  <i class="fas fa-shield-alt me-2"></i>
                  Step 3: Configure OAuth Consent Screen
                </h6>
              </div>
              <div class="card-body">
                <ol class="mb-0">
                  <li class="mb-2">
                    Go to
                    <a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank" class="text-primary">
                      OAuth consent screen
                      <i class="fas fa-external-link-alt ms-1 small"></i>
                    </a>
                  </li>
                  <li class="mb-2">Choose "External" user type</li>
                  <li class="mb-2">Fill in app name: <strong>Lodgeick</strong></li>
                  <li class="mb-2">Add required scopes:</li>
                </ol>
                <div class="mt-2 p-2 bg-light rounded">
                  <div v-for="api in parsedData.apis" :key="api.name">
                    <code class="small d-block" v-for="scope in api.scopes" :key="scope">
                      {{ scope }}
                    </code>
                  </div>
                </div>
              </div>
            </div>

            <div class="card mb-3">
              <div class="card-header bg-light">
                <h6 class="mb-0 font-weight-bold">
                  <i class="fas fa-key me-2"></i>
                  Step 4: Create OAuth Credentials
                </h6>
              </div>
              <div class="card-body">
                <ol class="mb-2">
                  <li class="mb-2">
                    Go to
                    <a href="https://console.cloud.google.com/apis/credentials" target="_blank" class="text-primary">
                      Credentials
                      <i class="fas fa-external-link-alt ms-1 small"></i>
                    </a>
                  </li>
                  <li class="mb-2">Click "Create Credentials" → "OAuth 2.0 Client ID"</li>
                  <li class="mb-2">Application type: <strong>Web application</strong></li>
                  <li class="mb-2">Add authorized redirect URI:</li>
                </ol>
                <div class="input-group mt-2">
                  <input
                    type="text"
                    class="form-control font-monospace"
                    :value="redirectUri"
                    readonly
                  >
                  <BaseButton
                    variant="outline-secondary"
                    @click="copyToClipboard(redirectUri)"
                    icon-left="fas fa-copy"
                  >
                  </BaseButton>
                </div>
              </div>
            </div>

            <div class="flex gap-2 mt-4">
              <BaseButton
                variant="secondary"
                @click="currentStep = 'preview'"
                icon-left="fas fa-arrow-left"
              >
                Back
              </BaseButton>
              <BaseButton
                variant="primary"
                full-width
                @click="currentStep = 'oauth_input'"
                icon-right="fas fa-arrow-right"
              >
                I've Completed the Setup
              </BaseButton>
            </div>
          </div>

          <!-- Step 3: Project Created -->
          <div v-if="currentStep === 'project_created'" class="step">
            <div class="text-center mb-4">
              <div
                class="icon-shape bg-gradient-success shadow-success mx-auto mb-3"
                style="width: 80px; height: 80px;"
              >
                <i class="fas fa-check text-white" style="font-size: 2.5rem;"></i>
              </div>
              <h4 class="font-weight-bold">Project Created Successfully!</h4>
              <p class="text-muted">
                Google Cloud project <strong>{{ projectData.project_id }}</strong> is ready
              </p>
            </div>

            <div class="alert alert-success">
              <i class="fas fa-check-circle me-2"></i>
              <strong>{{ projectData.apis_enabled.length }} APIs Enabled:</strong>
              {{ projectData.apis_enabled.join(', ') }}
            </div>

            <div v-if="projectData.apis_failed && projectData.apis_failed.length > 0" class="alert alert-warning">
              <i class="fas fa-exclamation-triangle me-2"></i>
              <strong>Some APIs failed to enable:</strong>
              <ul class="mb-0 mt-2">
                <li v-for="failed in projectData.apis_failed" :key="failed.api">
                  {{ failed.api }}: {{ failed.error }}
                </li>
              </ul>
            </div>

            <div class="card bg-light mt-4">
              <div class="card-body">
                <h6 class="font-weight-bold mb-3">
                  <i class="fas fa-key text-warning me-2"></i>
                  Next: Create OAuth Credentials
                </h6>
                <p class="small text-muted mb-3">
                  You need to manually create OAuth credentials in Google Cloud Console.
                  Follow these steps:
                </p>
                <ol class="small">
                  <li class="mb-2">
                    Go to
                    <a
                      :href="`https://console.cloud.google.com/apis/credentials?project=${projectData.project_id}`"
                      target="_blank"
                      class="text-primary"
                    >
                      Google Cloud Console - Credentials
                      <i class="fas fa-external-link-alt ms-1"></i>
                    </a>
                  </li>
                  <li class="mb-2">Configure OAuth consent screen (if not done already)</li>
                  <li class="mb-2">Create OAuth 2.0 Client ID (Web application)</li>
                  <li class="mb-2">
                    Add redirect URI:
                    <code class="bg-white px-2 py-1 rounded">{{ redirectUri }}</code>
                    <BaseButton
                      variant="outline-secondary"
                      size="sm"
                      @click="copyToClipboard(redirectUri)"
                      icon-left="fas fa-copy"
                      class="ms-2"
                    >
                    </BaseButton>
                  </li>
                  <li>Copy the Client ID and Client Secret</li>
                </ol>
              </div>
            </div>

            <BaseButton
              variant="primary"
              full-width
              class="mt-3"
              @click="currentStep = 'oauth_input'"
              icon-left="fas fa-arrow-right"
            >
              I've Created OAuth Credentials
            </BaseButton>
          </div>

          <!-- Step 4: OAuth Credentials Input -->
          <div v-if="currentStep === 'oauth_input'" class="step">
            <h5 class="font-weight-bold mb-3">
              <i class="fas fa-key text-primary me-2"></i>
              Enter OAuth Credentials
            </h5>

            <div class="mb-3">
              <label class="form-label font-weight-bold">
                Client ID
                <span class="text-danger">*</span>
              </label>
              <input
                v-model="oauthClientId"
                type="text"
                class="form-control"
                placeholder="123456789-abc123def456.apps.googleusercontent.com"
              >
            </div>

            <div class="mb-3">
              <label class="form-label font-weight-bold">
                Client Secret
                <span class="text-danger">*</span>
              </label>
              <div class="input-group">
                <input
                  v-model="oauthClientSecret"
                  :type="showSecret ? 'text' : 'password'"
                  class="form-control"
                  placeholder="GOCSPX-xxxxxxxxxxxxx"
                >
                <BaseButton
                  variant="outline-secondary"
                  @click="showSecret = !showSecret"
                  :icon-left="showSecret ? 'fas fa-eye-slash' : 'fas fa-eye'"
                >
                </BaseButton>
              </div>
            </div>

            <BaseButton
              variant="success"
              full-width
              @click="saveOAuthCredentials"
              :disabled="!oauthClientId || !oauthClientSecret || savingOAuth"
              :loading="savingOAuth"
              loading-text="Saving & Syncing to n8n..."
              icon-left="fas fa-save"
            >
              Save & Sync to n8n
            </BaseButton>
          </div>

          <!-- Step 5: Complete -->
          <div v-if="currentStep === 'complete'" class="step text-center">
            <div
              class="icon-shape bg-gradient-success shadow-success mx-auto mb-4"
              style="width: 100px; height: 100px;"
            >
              <i class="fas fa-check-double text-white" style="font-size: 3rem;"></i>
            </div>
            <h4 class="font-weight-bold mb-3">Setup Complete!</h4>
            <p class="text-muted mb-4">
              Your Google Cloud integration is ready to use. Credentials have been synced to n8n.
            </p>

            <div class="alert alert-success">
              <i class="fas fa-info-circle me-2"></i>
              You can now use these credentials in your n8n workflows and Lodgeick integrations.
            </div>

            <BaseButton
              variant="primary"
              size="lg"
              @click="closeWizard"
              icon-left="fas fa-check"
            >
              Done
            </BaseButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"
import { createResource } from "frappe-ui"
import BaseButton from "./BaseButton.vue"

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'success'])

// State
const currentStep = ref('intent')
const setupMethod = ref('auto') // 'auto' or 'manual'
const userIntent = ref('')
const parsedData = ref(null)
const projectName = ref('')
const projectData = ref(null)
const oauthClientId = ref('')
const oauthClientSecret = ref('')
const showSecret = ref(false)
const showProjectNameInput = ref(false)

// Loading states
const parsing = ref(false)
const creatingProject = ref(false)
const savingOAuth = ref(false)

// Errors
const parseError = ref(null)

const redirectUri = computed(() => {
  return window.location.origin + '/api/method/lodgeick.api.oauth.oauth_callback'
})

// Parse intent resource
const parseIntentResource = createResource({
  url: "lodgeick.api.google_ai_setup.parse_intent",
  makeParams() {
    return { intent: userIntent.value }
  },
  onSuccess(data) {
    parsing.value = false
    if (data.success) {
      parsedData.value = data
      currentStep.value = 'preview'
      parseError.value = null
    } else {
      parseError.value = data.error || 'Failed to parse intent'
    }
  },
  onError(error) {
    parsing.value = false
    parseError.value = error.message || error
  }
})

// Create project resource
const createProjectResource = createResource({
  url: "lodgeick.api.google_ai_setup.create_project",
  makeParams() {
    return {
      project_name: projectName.value,
      intent_data: JSON.stringify(parsedData.value)
    }
  },
  onSuccess(data) {
    creatingProject.value = false
    if (data.success) {
      projectData.value = data
      currentStep.value = 'project_created'
    } else {
      alert('Failed to create project: ' + (data.error || 'Unknown error'))
    }
  },
  onError(error) {
    creatingProject.value = false
    alert('Error creating project: ' + (error.message || error))
  }
})

// Save OAuth credentials resource
const saveOAuthResource = createResource({
  url: "lodgeick.api.google_ai_setup.setup_oauth_credentials",
  makeParams() {
    return {
      project_id: projectData.value.project_id,
      client_id: oauthClientId.value,
      client_secret: oauthClientSecret.value
    }
  },
  onSuccess(data) {
    savingOAuth.value = false
    if (data.success) {
      currentStep.value = 'complete'
      emit('success', {
        project: projectData.value,
        credentials: {
          client_id: oauthClientId.value,
          n8n_credential_id: data.n8n_credential_id
        }
      })
    } else {
      alert('Failed to save credentials: ' + (data.error || 'Unknown error'))
    }
  },
  onError(error) {
    savingOAuth.value = false
    alert('Error saving credentials: ' + (error.message || error))
  }
})

function parseIntent() {
  parsing.value = true
  parseError.value = null
  parseIntentResource.submit()
}

function proceedToSetup() {
  if (setupMethod.value === 'auto') {
    showProjectNameInput.value = true
  } else {
    currentStep.value = 'manual_instructions'
  }
}

function createProject() {
  creatingProject.value = true
  createProjectResource.submit()
}

function saveOAuthCredentials() {
  savingOAuth.value = true
  saveOAuthResource.submit()
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    const button = event.target.closest('button')
    const icon = button.querySelector('i')
    const originalClass = icon.className
    icon.className = 'fas fa-check'
    setTimeout(() => {
      icon.className = originalClass
    }, 2000)
  })
}

function closeWizard() {
  currentStep.value = 'intent'
  setupMethod.value = 'auto'
  userIntent.value = ''
  parsedData.value = null
  projectName.value = ''
  projectData.value = null
  oauthClientId.value = ''
  oauthClientSecret.value = ''
  showSecret.value = false
  showProjectNameInput.value = false
  parseError.value = null
  emit('close')
}
</script>

<style scoped>
.bg-gradient-ai {
  background: linear-gradient(310deg, #667eea 0%, #764ba2 100%);
}

.bg-gradient-success {
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
}

.shadow-success {
  box-shadow: 0 4px 20px 0 rgba(23, 173, 55, 0.4) !important;
}

.icon-shape {
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.font-weight-bold {
  font-weight: 700;
}

.modal.show {
  display: block;
}

.modal-dialog-scrollable .modal-body {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

code {
  font-size: 0.875rem;
}
</style>
