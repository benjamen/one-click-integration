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
        <div class="modal-header bg-gradient-primary">
          <div>
            <h5 class="modal-title text-white font-weight-bold mb-0">
              <i class="fas fa-magic me-2"></i>
              OAuth Setup Wizard
            </h5>
            <p class="text-white-50 small mb-0 mt-1">{{ providerName }}</p>
          </div>
          <button
            type="button"
            class="btn-close btn-close-white"
            @click="closeWizard"
          ></button>
        </div>

        <!-- Body -->
        <div class="modal-body p-4">
          <!-- Loading State -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="text-muted">Loading setup options...</p>
          </div>

          <!-- Progress Steps (Only shown after tier selection) -->
          <div v-if="!loading && setupMethod && currentStep > 0" class="row mb-4">
            <div class="col-12">
              <div class="d-flex justify-content-between align-items-center">
                <div
                  v-for="(step, index) in filteredSteps"
                  :key="index"
                  class="flex-fill text-center position-relative"
                >
                  <div
                    class="step-circle mx-auto mb-2"
                    :class="{
                      'active': currentStep === index + 1,
                      'completed': currentStep > index + 1
                    }"
                  >
                    <i v-if="currentStep > index + 1" class="fas fa-check"></i>
                    <span v-else>{{ index + 1 }}</span>
                  </div>
                  <small class="d-block text-muted">{{ step.title }}</small>
                  <div
                    v-if="index < filteredSteps.length - 1"
                    class="step-line"
                    :class="{ 'completed': currentStep > index + 1 }"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step Content -->
          <div v-if="!loading" class="step-content">

            <!-- Step 0: Tier Selection (Enhanced) -->
            <div v-if="currentStep === 0" class="step">
              <!-- Header with Context -->
              <div class="text-center mb-4">
                <h5 class="font-weight-bold mb-2">
                  <i class="fas fa-route text-primary me-2"></i>
                  Choose Your Setup Method
                </h5>
                <p class="text-muted">
                  Select the best option for your needs. You can always change this later.
                </p>
              </div>

              <!-- Comparison Toggle (if multiple tiers) -->
              <div v-if="availableTiers.length > 1" class="text-center mb-4">
                <div class="btn-group btn-group-sm" role="group">
                  <button
                    type="button"
                    class="btn"
                    :class="viewMode === 'cards' ? 'btn-primary' : 'btn-outline-secondary'"
                    @click="viewMode = 'cards'"
                  >
                    <i class="fas fa-th-large me-1"></i> Cards
                  </button>
                  <button
                    type="button"
                    class="btn"
                    :class="viewMode === 'compare' ? 'btn-primary' : 'btn-outline-secondary'"
                    @click="viewMode = 'compare'"
                  >
                    <i class="fas fa-columns me-1"></i> Compare
                  </button>
                </div>
              </div>

              <!-- Cards View -->
              <div v-if="viewMode === 'cards'" class="row g-4">
                <div
                  v-for="tier in availableTiers"
                  :key="tier.key"
                  :class="tierColumnClass"
                >
                  <div
                    class="card h-100 setup-option position-relative"
                    :class="{
                      'border-primary selected': setupMethod === tier.key,
                      'recommended-tier': tier.config.recommended
                    }"
                    @click="selectTier(tier.key)"
                    role="button"
                    tabindex="0"
                    @keypress.enter="selectTier(tier.key)"
                  >
                    <!-- Recommended Badge -->
                    <div v-if="tier.config.recommended" class="recommended-badge">
                      <i class="fas fa-star me-1"></i> Recommended
                    </div>

                    <div class="card-body p-4">
                      <!-- Icon -->
                      <div class="tier-icon mb-3">
                        <i :class="tier.iconClass"></i>
                      </div>

                      <!-- Title -->
                      <h5 class="card-title font-weight-bold mb-2">
                        {{ tier.config.icon }} {{ tier.config.label }}
                      </h5>

                      <!-- Description -->
                      <p class="card-text text-muted small mb-3">
                        {{ tier.config.description }}
                      </p>

                      <!-- Badges -->
                      <div class="mb-3">
                        <span
                          v-for="badge in tier.badges"
                          :key="badge.text"
                          class="badge me-1 mb-1"
                          :class="badge.class"
                        >
                          {{ badge.text }}
                        </span>
                      </div>

                      <!-- Pros -->
                      <div class="text-start mb-3">
                        <div class="small fw-bold text-success mb-2">
                          <i class="fas fa-check-circle me-1"></i> What you get:
                        </div>
                        <ul class="tier-list">
                          <li v-for="adv in tier.config.advantages.slice(0, 3)" :key="adv">
                            {{ adv }}
                          </li>
                        </ul>
                      </div>

                      <!-- Limitations (if any) -->
                      <div v-if="tier.config.limitations && tier.config.limitations.length > 0" class="text-start">
                        <div class="small fw-bold text-warning mb-2">
                          <i class="fas fa-exclamation-circle me-1"></i> Limitations:
                        </div>
                        <ul class="tier-list">
                          <li v-for="lim in tier.config.limitations.slice(0, 2)" :key="lim">
                            {{ lim }}
                          </li>
                        </ul>
                      </div>

                      <!-- Learn More Link -->
                      <div v-if="tier.config.advantages.length > 3 || (tier.config.limitations && tier.config.limitations.length > 2)" class="text-start mt-2">
                        <a
                          href="#"
                          class="small text-primary"
                          @click.prevent="showTierDetails(tier.key)"
                        >
                          <i class="fas fa-info-circle me-1"></i> Learn more
                        </a>
                      </div>
                    </div>

                    <!-- Selection Indicator -->
                    <div v-if="setupMethod === tier.key" class="selected-indicator">
                      <i class="fas fa-check-circle"></i>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Comparison Table View -->
              <div v-if="viewMode === 'compare'" class="table-responsive">
                <table class="table table-bordered comparison-table">
                  <thead>
                    <tr>
                      <th class="text-muted">Feature</th>
                      <th v-for="tier in availableTiers" :key="tier.key" class="text-center">
                        <div class="fw-bold">{{ tier.config.label }}</div>
                        <div class="small text-muted">{{ tier.config.icon }}</div>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td class="fw-bold">Setup Time</td>
                      <td v-for="tier in availableTiers" :key="`time-${tier.key}`" class="text-center">
                        {{ tier.config.setup_time }}
                      </td>
                    </tr>
                    <tr>
                      <td class="fw-bold">Rate Limits</td>
                      <td v-for="tier in availableTiers" :key="`limits-${tier.key}`" class="text-center">
                        <span v-if="tier.config.rate_limits">
                          <i class="fas fa-exclamation-triangle text-warning"></i> Limited
                        </span>
                        <span v-else class="text-success">
                          <i class="fas fa-infinity"></i> Unlimited
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td class="fw-bold">Billing APIs</td>
                      <td v-for="tier in availableTiers" :key="`billing-${tier.key}`" class="text-center">
                        {{ tier.config.allowed_apis === 'all' ? '✅ Yes' : '❌ No' }}
                      </td>
                    </tr>
                    <tr>
                      <td class="fw-bold">Requirements</td>
                      <td v-for="tier in availableTiers" :key="`req-${tier.key}`" class="text-center small">
                        <span v-if="!tier.config.requires || tier.config.requires.length === 0">
                          None
                        </span>
                        <span v-else>
                          {{ tier.config.requires.join(', ') }}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td></td>
                      <td v-for="tier in availableTiers" :key="`select-${tier.key}`" class="text-center">
                        <BaseButton
                          size="sm"
                          :variant="setupMethod === tier.key ? 'primary' : 'outline-primary'"
                          @click="selectTier(tier.key)"
                        >
                          {{ setupMethod === tier.key ? '✓ Selected' : 'Select' }}
                        </BaseButton>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Empty State -->
              <div v-if="availableTiers.length === 0" class="text-center py-5">
                <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                <h5 class="text-muted">No Setup Options Available</h5>
                <p class="text-muted small">
                  Please contact your administrator to configure OAuth options for {{ providerName }}.
                </p>
              </div>

              <!-- Continue Button -->
              <div class="text-center mt-4" v-if="availableTiers.length > 0">
                <BaseButton
                  variant="primary"
                  size="lg"
                  class="px-5"
                  @click="proceedWithSetupMethod"
                  :disabled="!setupMethod || processing"
                  :loading="processing"
                  loading-text="Processing..."
                  icon-left="fas fa-arrow-right"
                >
                  Continue with {{ setupMethodLabel }}
                </BaseButton>
              </div>

              <!-- Help Text -->
              <div class="text-center mt-3">
                <small class="text-muted">
                  <i class="fas fa-question-circle me-1"></i>
                  Need help choosing? <a href="#" @click.prevent="showHelpModal">See our recommendation guide</a>
                </small>
              </div>
            </div>

            <!-- Manual Setup Steps (1-5) - Keep existing implementation -->
            <!-- These remain the same as your current implementation -->

          </div>

          <!-- Error Alert -->
          <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Error:</strong> {{ errorMessage }}
            <button type="button" class="btn-close" @click="errorMessage = null"></button>
          </div>

          <!-- Success Alert -->
          <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            {{ successMessage }}
            <button type="button" class="btn-close" @click="successMessage = null"></button>
          </div>
        </div>

        <!-- Footer -->
        <div class="modal-footer border-top">
          <BaseButton
            v-if="currentStep > 0 && currentStep < 5 && setupMethod !== 'default'"
            variant="outline-secondary"
            @click="previousStep"
            icon-left="fas fa-arrow-left"
          >
            Previous
          </BaseButton>
          <BaseButton
            v-if="currentStep > 0 && setupMethod !== 'default'"
            variant="link"
            @click="resetWizard"
            icon-left="fas fa-redo"
          >
            Start Over
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Tier Details Modal -->
    <TierDetailsModal
      v-if="showingTierDetails"
      :tier="tierConfig?.tiers?.[selectedTierForDetails]"
      :tier-name="selectedTierForDetails"
      @close="showingTierDetails = false"
    />

    <!-- Help Modal -->
    <HelpModal
      v-if="showingHelp"
      :provider="provider"
      @close="showingHelp = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { createResource, call } from "frappe-ui"
import BaseButton from "./BaseButton.vue"
import TierDetailsModal from './TierDetailsModal.vue'
import HelpModal from './HelpModal.vue'

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

// State
const currentStep = ref(0)
const setupMethod = ref(null)
const viewMode = ref('cards') // 'cards' or 'compare'
const clientId = ref('')
const clientSecret = ref('')
const showSecret = ref(false)
const loading = ref(true)
const processing = ref(false)
const saving = ref(false)
const tierConfig = ref(null)
const errorMessage = ref(null)
const successMessage = ref(null)
const showingTierDetails = ref(false)
const selectedTierForDetails = ref(null)
const showingHelp = ref(false)

// Load tier configuration
onMounted(async () => {
  try {
    loading.value = true
    const config = await call('lodgeick.api.oauth_tiers.get_tier_config', {
      provider: props.provider
    })
    tierConfig.value = config
  } catch (error) {
    errorMessage.value = `Failed to load setup options: ${error.message}`
  } finally {
    loading.value = false
  }
})

// Computed
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

const availableTiers = computed(() => {
  if (!tierConfig.value?.tiers) return []

  const tiers = []

  if (tierConfig.value.tiers.default?.enabled) {
    tiers.push({
      key: 'default',
      config: tierConfig.value.tiers.default,
      iconClass: 'fas fa-bolt fa-3x text-warning',
      badges: [
        { text: tierConfig.value.tiers.default.setup_time, class: 'bg-success' },
        { text: 'No Setup', class: 'bg-info' }
      ]
    })
  }

  if (tierConfig.value.tiers.ai?.enabled) {
    tiers.push({
      key: 'ai',
      config: { ...tierConfig.value.tiers.ai, recommended: true },
      iconClass: 'fas fa-robot fa-3x text-primary',
      badges: [
        { text: 'Recommended', class: 'bg-success' },
        { text: tierConfig.value.tiers.ai.setup_time, class: 'bg-primary' }
      ]
    })
  }

  if (tierConfig.value.tiers.manual?.enabled) {
    tiers.push({
      key: 'manual',
      config: tierConfig.value.tiers.manual,
      iconClass: 'fas fa-tools fa-3x text-secondary',
      badges: [
        { text: 'Advanced', class: 'bg-secondary' },
        { text: tierConfig.value.tiers.manual.setup_time, class: 'bg-info' }
      ]
    })
  }

  return tiers
})

const tierColumnClass = computed(() => {
  const count = availableTiers.value.length
  if (count === 1) return 'col-12'
  if (count === 2) return 'col-md-6'
  return 'col-md-4'
})

const setupMethodLabel = computed(() => {
  if (!setupMethod.value || !tierConfig.value) return ''
  const tier = tierConfig.value?.tiers?.[setupMethod.value]
  return tier?.label || setupMethod.value
})

const filteredSteps = computed(() => {
  if (setupMethod.value === 'default') {
    return [{ title: 'Complete' }]
  }
  return [
    { title: 'Create Project' },
    { title: 'Enable APIs' },
    { title: 'Consent Screen' },
    { title: 'Create Credentials' },
    { title: 'Configure' },
    { title: 'Complete' }
  ]
})

// Methods
function selectTier(tierKey) {
  setupMethod.value = tierKey
  errorMessage.value = null
}

function showTierDetails(tierKey) {
  selectedTierForDetails.value = tierKey
  showingTierDetails.value = true
}

function showHelpModal() {
  showingHelp.value = true
}

async function proceedWithSetupMethod() {
  if (!setupMethod.value) return

  try {
    processing.value = true
    errorMessage.value = null

    if (setupMethod.value === 'default') {
      // Use default tier
      const result = await call('lodgeick.api.oauth.save_user_oauth_setup', {
        provider: props.provider,
        tier: 'default',
        use_default: true
      })

      successMessage.value = result.message
      currentStep.value = 5

      emit('success', {
        provider: props.provider,
        tier: 'default',
        ready_to_connect: true
      })
    } else if (setupMethod.value === 'ai') {
      // Launch AI wizard
      emit('launchAIWizard')
      closeWizard()
    } else {
      // Continue with manual setup
      currentStep.value = 1
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to proceed with setup'
  } finally {
    processing.value = false
  }
}

function resetWizard() {
  currentStep.value = 0
  setupMethod.value = null
  clientId.value = ''
  clientSecret.value = ''
  errorMessage.value = null
  successMessage.value = null
}

function closeWizard() {
  resetWizard()
  emit('close')
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// Watch for prop changes
watch(() => props.show, (newVal) => {
  if (newVal && !tierConfig.value) {
    // Reload config when modal is shown
    onMounted()
  }
})
</script>

<style scoped>
/* Tier Selection Enhancements */
.tier-icon {
  text-align: center;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tier-list {
  margin: 0;
  padding-left: 1.25rem;
  font-size: 0.875rem;
  color: #6c757d;
  list-style-type: none;
}

.tier-list li {
  position: relative;
  padding-left: 1rem;
  margin-bottom: 0.5rem;
}

.tier-list li:before {
  content: "•";
  position: absolute;
  left: 0;
  color: #6c757d;
}

.setup-option {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid #e9ecef;
  cursor: pointer;
  overflow: hidden;
}

.setup-option:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #dee2e6;
}

.setup-option:focus {
  outline: 3px solid rgba(121, 40, 202, 0.3);
  outline-offset: 2px;
}

.setup-option.selected {
  border-color: #7928CA !important;
  box-shadow: 0 8px 24px rgba(121, 40, 202, 0.25);
  transform: scale(1.02);
}

.setup-option.recommended-tier {
  border-color: #17AD37;
}

.recommended-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(23, 173, 55, 0.3);
}

.selected-indicator {
  position: absolute;
  top: 12px;
  left: 12px;
  background: #7928CA;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(121, 40, 202, 0.4);
}

/* Comparison Table */
.comparison-table {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.comparison-table thead th {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  padding: 1rem;
  font-weight: 600;
}

.comparison-table tbody td {
  padding: 0.75rem 1rem;
  vertical-align: middle;
}

.comparison-table tbody tr:nth-child(even) {
  background: #f8f9fa;
}

/* Step Progress */
.step-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #e9ecef;
  color: #6c757d;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 2;
}

.step-circle.active {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
  color: white;
  box-shadow: 0 4px 20px 0 rgba(121, 40, 202, 0.4);
  transform: scale(1.1);
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
  height: 3px;
  background: #e9ecef;
  z-index: 1;
  transition: all 0.3s ease;
}

.step-line.completed {
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
}

/* Gradients */
.bg-gradient-primary {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
}

.bg-gradient-success {
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
}

/* Modal */
.modal.show {
  display: block;
}

.modal-dialog-scrollable .modal-body {
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .tier-icon {
    height: 60px;
  }

  .setup-option {
    margin-bottom: 1rem;
  }

  .comparison-table {
    font-size: 0.875rem;
  }
}

/* Accessibility */
.setup-option:focus-visible {
  outline: 3px solid #7928CA;
  outline-offset: 3px;
}

/* Loading Animation */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.skeleton {
  animation: pulse 1.5s ease-in-out infinite;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
}
</style>
