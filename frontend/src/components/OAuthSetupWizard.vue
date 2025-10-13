<template>
  <div
    class="modal fade"
    :class="{ show: show, 'block': show }"
    tabindex="-1"
    :style="{ backgroundColor: show ? 'rgba(0,0,0,0.5)' : '' }"
    @click.self="closeWizard"
  >
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <!-- Header -->
        <div class="modal-header bg-gradient-primary">
          <div class="w-100">
            <!-- Breadcrumbs (Tailwind) -->
            <nav aria-label="breadcrumb" class="mb-2">
              <ol class="flex items-center gap-2 text-sm">
                <li class="flex items-center">
                  <a href="#" class="text-white/75 hover:text-white transition-colors flex items-center gap-1" @click.prevent="closeWizard">
                    <i class="fas fa-home"></i>
                    <span>Home</span>
                  </a>
                </li>
                <li class="text-white/50">/</li>
                <li class="flex items-center">
                  <span class="text-white/75">Integrations</span>
                </li>
                <li class="text-white/50">/</li>
                <li class="flex items-center" aria-current="page">
                  <span class="text-white font-medium">{{ providerName }} Setup</span>
                </li>
              </ol>
            </nav>
            <h5 class="modal-title text-white font-bold mb-0">
              <i class="fas fa-magic mr-2"></i>
              OAuth Setup Wizard
            </h5>
          </div>
          <button
            type="button"
            class="btn-close btn-close-white"
            aria-label="Close OAuth setup wizard"
            @click="closeWizard"
          ></button>
        </div>

        <!-- Body -->
        <div class="modal-body p-4">
          <!-- Progress Steps -->
          <div class="mb-4">
            <div>
              <div class="flex justify-between items-center">
                <div
                  v-for="(step, index) in steps"
                  :key="index"
                  class="flex-1 text-center relative"
                >
                  <div
                    class="step-circle mx-auto mb-2"
                    :class="{
                      'active': currentStep === index,
                      'completed': currentStep > index
                    }"
                  >
                    <i v-if="currentStep > index" class="fas fa-check"></i>
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                  <small class="block text-gray-600">{{ step.title }}</small>
                  <div
                    v-if="index < steps.length - 1"
                    class="step-line"
                    :class="{ 'completed': currentStep > index }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step Content -->
          <div class="step-content">
            <!-- Step 0: Setup Method Choice -->
            <div v-if="currentStep === 0" class="step">
              <h5 class="font-bold text-gray-900 mb-3 text-center">
                <i class="fas fa-route text-primary-600 mr-2"></i>
                Choose Your Setup Method
              </h5>
              <p class="text-center text-gray-600 mb-4">
                Select how you'd like to set up your {{ providerName }} integration
              </p>

              <div class="row g-4">
                <!-- Quick Start (Default/Shared App) Option -->
                <div v-if="tierConfig?.tiers?.default?.enabled" class="col-md-4">
                  <div
                    class="card h-100 setup-option"
                    :class="{ 'border-primary selected': setupMethod === 'default' }"
                    @click="setupMethod = 'default'"
                    style="cursor: pointer;"
                  >
                    <div class="card-body text-center p-4">
                      <div class="mb-3">
                        <i class="fas fa-bolt fa-3x text-warning"></i>
                      </div>
                      <h5 class="card-title font-bold text-gray-900">
                        {{ tierConfig.tiers.default.icon }} {{ tierConfig.tiers.default.label }}
                      </h5>
                      <p class="card-text text-gray-600 text-sm">
                        {{ tierConfig.tiers.default.description }}
                      </p>
                      <div class="mt-3">
                        <BaseBadge variant="success" class="mr-1">{{ tierConfig.tiers.default.setup_time }}</BaseBadge>
                        <BaseBadge variant="info">No Setup</BaseBadge>
                      </div>
                      <hr class="my-3">
                      <div class="text-left">
                        <div class="text-sm text-green-600 mb-2">
                          <i class="fas fa-check-circle mr-1"></i> <strong>Pros:</strong>
                        </div>
                        <ul class="text-sm text-gray-600 mb-2" style="font-size: 0.85rem;">
                          <li v-for="adv in tierConfig.tiers.default.advantages.slice(0,3)" :key="adv">{{ adv }}</li>
                        </ul>
                        <div class="text-sm text-yellow-600 mb-2">
                          <i class="fas fa-exclamation-circle mr-1"></i> <strong>Limits:</strong>
                        </div>
                        <ul class="text-sm text-gray-600" style="font-size: 0.85rem;">
                          <li v-for="lim in tierConfig.tiers.default.limitations.slice(0,2)" :key="lim">{{ lim }}</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- AI-Powered Setup Option -->
                <div v-if="tierConfig?.tiers?.ai" class="col-md-4">
                  <div
                    class="card h-100 setup-option"
                    :class="{
                      'border-primary selected': setupMethod === 'ai',
                      'locked-tier': tierConfig.tiers.ai.upgrade_required
                    }"
                    @click="tierConfig.tiers.ai.enabled ? setupMethod = 'ai' : null"
                    :style="{ cursor: tierConfig.tiers.ai.enabled ? 'pointer' : 'not-allowed', opacity: tierConfig.tiers.ai.enabled ? 1 : 0.7 }"
                  >
                    <div class="card-body text-center p-4 relative">
                      <!-- Upgrade Badge (if locked) -->
                      <div v-if="tierConfig.tiers.ai.upgrade_required" class="absolute top-0 right-0 p-2">
                        <BaseBadge variant="warning">
                          <i class="fas fa-lock mr-1"></i>
                          {{ tierConfig.tiers.ai.upgrade_tier }} Only
                        </BaseBadge>
                      </div>

                      <div class="mb-3">
                        <i class="fas fa-robot fa-3x text-primary-600"></i>
                      </div>
                      <h5 class="card-title font-bold text-gray-900">
                        {{ tierConfig.tiers.ai.icon }} {{ tierConfig.tiers.ai.label }}
                      </h5>
                      <p class="card-text text-gray-600 text-sm">
                        {{ tierConfig.tiers.ai.description }}
                      </p>
                      <div class="mt-3">
                        <BaseBadge v-if="tierConfig.tiers.ai.enabled" variant="success" class="mr-1">Recommended</BaseBadge>
                        <BaseBadge variant="primary">{{ tierConfig.tiers.ai.setup_time }}</BaseBadge>
                      </div>
                      <hr class="my-3">

                      <!-- Upgrade Message (if locked) -->
                      <BaseAlert v-if="tierConfig.tiers.ai.upgrade_required" variant="warning" hide-icon class="text-sm mb-2">
                        <i class="fas fa-star mr-1"></i>
                        {{ tierConfig.tiers.ai.upgrade_message }}
                      </BaseAlert>

                      <div class="text-left">
                        <div class="text-sm text-green-600 mb-2">
                          <i class="fas fa-check-circle mr-1"></i> <strong>Pros:</strong>
                        </div>
                        <ul class="text-sm text-gray-600 mb-2" style="font-size: 0.85rem;">
                          <li v-for="adv in tierConfig.tiers.ai.advantages.slice(0,3)" :key="adv">{{ adv }}</li>
                        </ul>
                      </div>

                      <!-- Upgrade Button (if locked) -->
                      <div v-if="tierConfig.tiers.ai.upgrade_required" class="mt-3">
                        <BaseButton
                          variant="warning"
                          size="sm"
                          full-width
                          @click.stop="showUpgradeModal"
                          icon-left="fas fa-arrow-up"
                        >
                          Upgrade to {{ tierConfig.tiers.ai.upgrade_tier }}
                        </BaseButton>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Manual Setup Option -->
                <div v-if="tierConfig?.tiers?.manual?.enabled" :class="tierConfig?.tiers?.ai?.enabled ? 'col-md-4' : 'col-md-6'">
                  <div
                    class="card h-100 setup-option"
                    :class="{ 'border-primary selected': setupMethod === 'manual' }"
                    @click="setupMethod = 'manual'"
                    style="cursor: pointer;"
                  >
                    <div class="card-body text-center p-4">
                      <div class="mb-3">
                        <i class="fas fa-tools fa-3x text-secondary"></i>
                      </div>
                      <h5 class="card-title font-bold text-gray-900">
                        {{ tierConfig?.tiers?.manual?.icon || '🔧' }} {{ tierConfig?.tiers?.manual?.label || 'Manual Setup' }}
                      </h5>
                      <p class="card-text text-gray-600 text-sm">
                        {{ tierConfig?.tiers?.manual?.description || 'Step-by-step setup' }}
                      </p>
                      <div class="mt-3">
                        <BaseBadge variant="secondary">Advanced</BaseBadge>
                        <BaseBadge variant="info">{{ tierConfig?.tiers?.manual?.setup_time || '~10 min' }}</BaseBadge>
                      </div>
                      <hr class="my-3">
                      <div class="text-left">
                        <div class="text-sm text-green-600 mb-2">
                          <i class="fas fa-check-circle mr-1"></i> <strong>Pros:</strong>
                        </div>
                        <ul class="text-sm text-gray-600 mb-2" style="font-size: 0.85rem;">
                          <li v-for="adv in (tierConfig?.tiers?.manual?.advantages || []).slice(0,3)" :key="adv">{{ adv }}</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="text-center mt-4">
                <BaseButton
                  variant="primary"
                  size="lg"
                  @click="proceedWithSetupMethod"
                  :disabled="!setupMethod"
                  icon-right="fas fa-arrow-right"
                >
                  Continue with {{ setupMethodLabel }}
                </BaseButton>
              </div>
            </div>

            <!-- Step 0 (Non-Google): Create Google Cloud Project -->
            <div v-if="currentStep === 0 && provider !== 'google'" class="step">
              <h5 class="font-bold text-gray-900 mb-3">
                <i class="fab fa-google text-primary-600 mr-2"></i>
                Create Google Cloud Project
              </h5>
              <BaseAlert variant="info" hide-icon>
                <i class="fas fa-info-circle mr-2"></i>
                You'll need a Google account to create a Cloud project.
              </BaseAlert>
              <ol class="setup-steps">
                <li class="mb-3">
                  Go to <a href="https://console.cloud.google.com" target="_blank" class="text-primary-600">
                    <strong>Google Cloud Console</strong>
                    <i class="fas fa-external-link-alt ml-1 text-sm"></i>
                  </a>
                </li>
                <li class="mb-3">
                  Click the project dropdown at the top
                  <br><small class="text-gray-600">It usually says "Select a project" or shows your current project</small>
                </li>
                <li class="mb-3">
                  Click <strong>"New Project"</strong> in the top right
                </li>
                <li class="mb-3">
                  Name your project (e.g., "Lodgeick Integration")
                </li>
                <li class="mb-3">
                  Click <strong>"Create"</strong> and wait for the project to be created
                </li>
              </ol>
              <div class="text-center mt-4">
                <img
                  src="https://cloud.google.com/static/images/social-icon-google-cloud-1200-630.png"
                  alt="Google Cloud"
                  class="img-fluid rounded shadow"
                  style="max-height: 200px;"
                >
              </div>
            </div>

            <!-- Step 1: Enable APIs -->
            <div v-if="currentStep === 1" class="step">
              <h5 class="font-bold text-gray-900 mb-3">
                <i class="fas fa-toggle-on text-green-600 mr-2"></i>
                Enable Required APIs
              </h5>
              <BaseAlert variant="warning" hide-icon>
                <i class="fas fa-exclamation-triangle mr-2"></i>
                Make sure your new project is selected in the project dropdown!
              </BaseAlert>
              <ol class="setup-steps">
                <li class="mb-3">
                  Go to <a href="https://console.cloud.google.com/apis/library" target="_blank" class="text-primary-600">
                    <strong>APIs & Services > Library</strong>
                    <i class="fas fa-external-link-alt ml-1 text-sm"></i>
                  </a>
                </li>
                <li class="mb-3">
                  Search for and enable these APIs:
                  <div class="mt-2">
                    <BaseBadge variant="primary" class="mr-2 mb-2">Gmail API</BaseBadge>
                    <BaseBadge variant="info" class="mr-2 mb-2">Google Sheets API</BaseBadge>
                    <BaseBadge variant="success" class="mr-2 mb-2">Google Drive API</BaseBadge>
                  </div>
                </li>
                <li class="mb-3">
                  For each API:
                  <ul class="mt-2">
                    <li>Click on the API name</li>
                    <li>Click the blue <strong>"Enable"</strong> button</li>
                    <li>Wait for it to activate (takes a few seconds)</li>
                  </ul>
                </li>
              </ol>
            </div>

            <!-- Step 2: Configure OAuth Consent Screen -->
            <div v-if="currentStep === 2" class="step">
              <h5 class="font-bold text-gray-900 mb-3">
                <i class="fas fa-shield-alt text-yellow-500 mr-2"></i>
                Configure OAuth Consent Screen
              </h5>
              <ol class="setup-steps">
                <li class="mb-3">
                  Go to <a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank" class="text-primary-600">
                    <strong>APIs & Services > OAuth consent screen</strong>
                    <i class="fas fa-external-link-alt ml-1 text-sm"></i>
                  </a>
                </li>
                <li class="mb-3">
                  Select <strong>"External"</strong> user type
                  <br><small class="text-gray-600">This allows you to use any Google account for testing</small>
                </li>
                <li class="mb-3">
                  Click <strong>"Create"</strong>
                </li>
                <li class="mb-3">
                  Fill in the required fields:
                  <div class="card mt-2 bg-light">
                    <div class="card-body">
                      <div class="mb-2"><strong>App name:</strong> Lodgeick</div>
                      <div class="mb-2"><strong>User support email:</strong> Your email</div>
                      <div class="mb-2"><strong>Developer contact:</strong> Your email</div>
                    </div>
                  </div>
                </li>
                <li class="mb-3">
                  Click <strong>"Save and Continue"</strong>
                </li>
                <li class="mb-3">
                  On the "Scopes" page, click <strong>"Add or Remove Scopes"</strong>
                </li>
                <li class="mb-3">
                  Search for and select these scopes:
                  <div class="card mt-2 bg-light">
                    <div class="card-body small">
                      <div class="mb-1"><code>https://www.googleapis.com/auth/gmail.readonly</code></div>
                      <div class="mb-1"><code>https://www.googleapis.com/auth/gmail.send</code></div>
                      <div class="mb-1"><code>https://www.googleapis.com/auth/spreadsheets</code></div>
                      <div class="mb-1"><code>https://www.googleapis.com/auth/drive.file</code></div>
                    </div>
                  </div>
                </li>
                <li class="mb-3">
                  Click <strong>"Update"</strong> then <strong>"Save and Continue"</strong>
                </li>
                <li class="mb-3">
                  On the "Test users" page, click <strong>"Add Users"</strong>
                </li>
                <li class="mb-3">
                  Add your Gmail address (the one you'll test with)
                </li>
                <li class="mb-3">
                  Click <strong>"Save and Continue"</strong> through the remaining steps
                </li>
              </ol>
            </div>

            <!-- Step 3: Create OAuth Credentials -->
            <div v-if="currentStep === 3" class="step">
              <h5 class="font-bold text-gray-900 mb-3">
                <i class="fas fa-key text-red-600 mr-2"></i>
                Create OAuth 2.0 Credentials
              </h5>
              <ol class="setup-steps">
                <li class="mb-3">
                  Go to <a href="https://console.cloud.google.com/apis/credentials" target="_blank" class="text-primary-600">
                    <strong>APIs & Services > Credentials</strong>
                    <i class="fas fa-external-link-alt ml-1 text-sm"></i>
                  </a>
                </li>
                <li class="mb-3">
                  Click <strong>"Create Credentials"</strong> at the top
                </li>
                <li class="mb-3">
                  Select <strong>"OAuth 2.0 Client ID"</strong>
                </li>
                <li class="mb-3">
                  Application type: <strong>"Web application"</strong>
                </li>
                <li class="mb-3">
                  Name: <strong>"Lodgeick Local"</strong> (or any name you prefer)
                </li>
                <li class="mb-3">
                  Under <strong>"Authorized redirect URIs"</strong>, click <strong>"Add URI"</strong>
                </li>
                <li class="mb-3">
                  Add this exact URI:
                  <div class="input-group mt-2">
                    <input
                      type="text"
                      class="form-control"
                      :value="redirectUri"
                      readonly
                    >
                    <BaseButton
                      variant="outline-secondary"
                      size="md"
                      aria-label="Copy redirect URI to clipboard"
                      @click="copyToClipboard(redirectUri)"
                      icon-left="fas fa-copy"
                    >
                    </BaseButton>
                  </div>
                  <small class="text-gray-600">Click the copy button to copy the URI</small>
                </li>
                <li class="mb-3">
                  Click <strong>"Create"</strong>
                </li>
                <li class="mb-3">
                  A dialog will appear showing your credentials
                  <BaseAlert variant="warning" hide-icon class="mt-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    <strong>Important:</strong> Copy both the Client ID and Client Secret - you'll need them in the next step!
                  </BaseAlert>
                </li>
              </ol>
            </div>

            <!-- Step 4: Configure Lodgeick -->
            <div v-if="currentStep === 4" class="step">
              <h5 class="font-bold text-gray-900 mb-3">
                <i class="fas fa-cog text-blue-500 mr-2"></i>
                Configure Lodgeick
              </h5>
              <p>Enter your OAuth credentials from Google Cloud Console:</p>

              <BaseInput
                v-model="clientId"
                label="Client ID"
                type="text"
                placeholder="1234567890-abc123def456.apps.googleusercontent.com"
                helper-text="Ends with .apps.googleusercontent.com"
                required
                class="mb-4"
              />

              <BaseInput
                v-model="clientSecret"
                label="Client Secret"
                :type="showSecret ? 'text' : 'password'"
                placeholder="GOCSPX-xxxxxxxxxxxxx"
                helper-text="Usually starts with GOCSPX-"
                required
                class="mb-4"
              >
                <template #append>
                  <button
                    @click="showSecret = !showSecret"
                    class="text-gray-400 hover:text-gray-600"
                    :aria-label="showSecret ? 'Hide client secret' : 'Show client secret'"
                  >
                    <i :class="showSecret ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                  </button>
                </template>
              </BaseInput>

              <BaseAlert v-if="clientId && clientSecret" variant="success" hide-icon>
                <i class="fas fa-check-circle mr-2"></i>
                Credentials look good! Click "Save & Test Connection" to finish.
              </BaseAlert>
            </div>

            <!-- Step 5: Complete -->
            <div v-if="currentStep === 5" class="step text-center">
              <div class="icon icon-shape bg-gradient-success shadow-success mx-auto mb-4" style="width: 80px; height: 80px;">
                <i class="fas fa-check text-white" style="font-size: 2.5rem;"></i>
              </div>
              <h4 class="font-bold text-gray-900 mb-3">Setup Complete!</h4>
              <p class="text-gray-600 mb-4">
                Your OAuth credentials have been configured successfully.
              </p>
              <BaseAlert variant="info" hide-icon>
                <i class="fas fa-lightbulb mr-2"></i>
                You can now close this wizard and click "Connect App" to authenticate with {{ providerName }}.
              </BaseAlert>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <BaseButton
            v-if="currentStep > 0 && currentStep < 5"
            variant="secondary"
            @click="previousStep"
            icon-left="fas fa-arrow-left"
          >
            Previous
          </BaseButton>
          <BaseButton
            v-if="currentStep < 4"
            variant="primary"
            @click="nextStep"
            icon-right="fas fa-arrow-right"
          >
            Next
          </BaseButton>
          <BaseButton
            v-if="currentStep === 4"
            variant="success"
            @click="saveCredentials"
            :disabled="!clientId || !clientSecret || saving"
            :loading="saving"
            loading-text="Saving..."
            icon-left="fas fa-save"
          >
            Save & Test Connection
          </BaseButton>
          <BaseButton
            v-if="currentStep === 5"
            variant="primary"
            @click="closeWizard"
            icon-left="fas fa-check"
          >
            Done
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { createResource, call } from "frappe-ui"
import { useToast } from "@/composables/useToast"
import BaseButton from "./BaseButton.vue"
import BaseInput from "./BaseInput.vue"
import BaseBadge from "./base/BaseBadge.vue"

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  provider: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'success', 'launchAIWizard'])

const toast = useToast()

const currentStep = ref(0)
const setupMethod = ref('default') // Default to 'default' (Quick Start) for better UX
const clientId = ref('')
const clientSecret = ref('')
const showSecret = ref(false)
const saving = ref(false)
const loading = ref(true)
const tierConfig = ref(null)
const errorMessage = ref(null)
const successMessage = ref(null)

// Load tier configuration for this provider
onMounted(async () => {
  try {
    loading.value = true
    const config = await call('lodgeick.api.oauth_tiers.get_tier_config', {
      provider: props.provider
    })
    tierConfig.value = config

    // Load saved progress from localStorage
    loadProgress()
  } catch (error) {
    errorMessage.value = `Failed to load setup options: ${error.message}`
    toast.error(`Failed to load setup options: ${error.message || 'Please try again'}`)
  } finally {
    loading.value = false
  }
})

// Save and load progress functions
function saveProgress() {
  const progress = {
    provider: props.provider,
    setupMethod: setupMethod.value,
    currentStep: currentStep.value,
    clientId: clientId.value,
    clientSecret: clientSecret.value,
    timestamp: Date.now()
  }
  localStorage.setItem(`oauth_progress_${props.provider}`, JSON.stringify(progress))
}

function loadProgress() {
  const saved = localStorage.getItem(`oauth_progress_${props.provider}`)
  if (saved) {
    try {
      const progress = JSON.parse(saved)
      // Only load if saved less than 24 hours ago
      const hoursSinceSave = (Date.now() - progress.timestamp) / (1000 * 60 * 60)
      if (hoursSinceSave < 24) {
        setupMethod.value = progress.setupMethod || 'default'
        currentStep.value = progress.currentStep || 0
        clientId.value = progress.clientId || ''
        clientSecret.value = progress.clientSecret || ''
        toast.info('Resumed your previous OAuth setup', { timeout: 4000 })
      } else {
        // Clear old progress
        clearProgress()
      }
    } catch (e) {
      console.error('Failed to load progress:', e)
    }
  }
}

function clearProgress() {
  localStorage.removeItem(`oauth_progress_${props.provider}`)
}

// Watch for changes and auto-save
watch([setupMethod, currentStep, clientId, clientSecret], () => {
  if (currentStep.value > 0 && currentStep.value < 5) {
    saveProgress()
  }
}, { deep: true })

// Watch for prop changes
watch(() => props.show, (newVal) => {
  if (newVal && !tierConfig.value) {
    onMounted()
  }
})

const providerName = computed(() => {
  const names = {
    google: 'Google (Gmail, Sheets, Drive)',
    xero: 'Xero',
    slack: 'Slack',
    microsoft: 'Microsoft 365',
    hubspot: 'HubSpot',
    salesforce: 'Salesforce',
    stripe: 'Stripe'
  }
  return names[props.provider] || props.provider
})

const setupMethodLabel = computed(() => {
  if (!setupMethod.value || !tierConfig.value) return ''
  const tier = tierConfig.value?.tiers?.[setupMethod.value]
  return tier?.label || setupMethod.value
})

const redirectUri = computed(() => {
  return window.location.origin + '/oauth/callback'
})

const steps = [
  { title: 'Create Project' },
  { title: 'Enable APIs' },
  { title: 'Consent Screen' },
  { title: 'Create Credentials' },
  { title: 'Configure' },
  { title: 'Complete' }
]

// Save credentials resource
const saveCredentialsResource = createResource({
  url: "lodgeick.api.oauth.save_user_oauth_setup",
  makeParams(params) {
    if (params?.use_default) {
      return {
        provider: props.provider,
        tier: 'default',
        use_default: true
      }
    }
    return {
      provider: props.provider,
      tier: setupMethod.value || 'manual',
      client_id: clientId.value,
      client_secret: clientSecret.value
    }
  },
  onSuccess(data) {
    saving.value = false
    if (data.ready_to_connect) {
      currentStep.value = 5
      toast.success('OAuth credentials saved successfully! 🎉')
    }
    emit('success', {
      provider: props.provider,
      tier: setupMethod.value,
      ready_to_connect: data.ready_to_connect
    })
  },
  onError(error) {
    saving.value = false
    toast.error(`Failed to save credentials: ${error.message || error}`, {
      timeout: 7000
    })
  }
})

function proceedWithSetupMethod() {
  if (setupMethod.value === 'default') {
    // Use Lodgeick's shared OAuth app - no setup needed
    // This will use default credentials from site_config
    saving.value = true
    saveCredentialsResource.submit({
      provider: props.provider,
      tier: 'default',
      use_default: true
    })
  } else if (setupMethod.value === 'ai') {
    // Close this wizard and launch AI wizard
    emit('launchAIWizard')
    closeWizard()
  } else {
    // Continue with manual setup
    currentStep.value = 1
  }
}

function nextStep() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function saveCredentials() {
  if (!clientId.value || !clientSecret.value) {
    toast.warning('Please enter both Client ID and Client Secret')
    return
  }

  saving.value = true
  saveCredentialsResource.submit()
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    toast.success('Copied to clipboard!')
    const button = event.target.closest('button')
    const icon = button.querySelector('i')
    icon.className = 'fas fa-check'
    setTimeout(() => {
      icon.className = 'fas fa-copy'
    }, 2000)
  }).catch(() => {
    toast.error('Failed to copy to clipboard')
  })
}

function closeWizard() {
  // Only clear progress if wizard was completed (step 5)
  if (currentStep.value === 5) {
    clearProgress()
  }

  currentStep.value = 0
  setupMethod.value = 'default'
  clientId.value = ''
  clientSecret.value = ''
  showSecret.value = false
  emit('close')
}

function showUpgradeModal() {
  const tier = tierConfig.value?.tiers?.ai?.upgrade_tier || 'Pro'

  // Show upgrade info with toast for now - TODO: Create proper upgrade modal with Stripe
  toast.info(
    `Upgrade to ${tier} to unlock AI-powered OAuth setup! Includes: Unlimited API quota, AI-powered setup (2 min), Access to all APIs, Priority support.`,
    {
      timeout: 10000
    }
  )

  // TODO: Replace with proper modal component with pricing breakdown and Stripe checkout
  // For now, could redirect to pricing page
  // router.push('/pricing')
}
</script>

<style scoped>
.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e9ecef;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.3s ease;
}

.step-circle.active {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
  color: white;
  box-shadow: 0 4px 20px 0 rgba(121, 40, 202, 0.4);
}

.step-circle.completed {
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
  color: white;
}

.step-line {
  position: absolute;
  top: 24px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e9ecef;
  z-index: -1;
  transition: all 0.3s ease;
}

.step-line.completed {
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
}

.setup-steps {
  padding-left: 1.5rem;
}

.setup-steps li {
  line-height: 1.8;
}

.bg-gradient-primary {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
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

.modal.show {
  display: block;
}

.modal-dialog-scrollable .modal-body {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.setup-option {
  transition: all 0.3s ease;
  border: 2px solid #e9ecef;
}

.setup-option:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.setup-option.selected {
  border-color: #7928CA !important;
  box-shadow: 0 4px 20px rgba(121, 40, 202, 0.2);
}

.setup-option.locked-tier {
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05) 0%, rgba(255, 255, 255, 1) 100%);
  border: 2px dashed #ffc107 !important;
}

.setup-option.locked-tier:hover {
  transform: none;
  box-shadow: 0 4px 20px rgba(255, 193, 7, 0.2);
}

/* Breadcrumb styles handled by Tailwind */
</style>
