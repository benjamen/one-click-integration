<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Header with Logo and Account Menu -->
    <div class="p-6">
      <div class="flex items-center justify-between">
        <router-link to="/" class="inline-flex items-center gap-3 group no-underline">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-xl">L</span>
          </div>
          <span class="text-2xl font-bold text-gray-900">Lodgeick</span>
        </router-link>

        <!-- User Menu -->
        <div class="flex items-center gap-4">
          <router-link
            to="/account/profile"
            class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            My Account
          </router-link>
          <button
            @click="handleLogout"
            class="text-gray-700 hover:text-red-600 font-medium transition-colors flex items-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Log Out
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
      <!-- Progress Bar -->
      <StepProgressBar :current-step="onboardingStore.currentStep" :total-steps="4" />

      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">
          Connect Your Apps
        </h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          Choose a setup method and authorize access to enable seamless integrations
        </p>
      </div>

      <!-- Apps List (Redesigned) -->
      <div class="space-y-8 mb-8">
        <div
          v-for="appId in onboardingStore.connectedApps"
          :key="appId"
          class="bg-white rounded-2xl shadow-lg p-8 transition-all duration-200"
        >
          <!-- App Header -->
          <div class="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
            <div class="flex items-center gap-4">
              <div
                class="w-16 h-16 rounded-lg flex items-center justify-center text-3xl"
                :class="getAppById(appId)?.color"
              >
                {{ getAppById(appId)?.icon }}
              </div>
              <div>
                <h3 class="text-2xl font-bold text-gray-900">
                  {{ getAppById(appId)?.name }}
                </h3>
                <p class="text-sm text-gray-600">
                  {{ getAppById(appId)?.description }}
                </p>
              </div>
            </div>
            <div
              v-if="isAuthorized(appId)"
              class="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg font-medium"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
              Connected
            </div>
          </div>

          <!-- If not yet set up: Show setup method selection inline -->
          <div v-if="!hasCredentials(appId)">
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Choose how to connect:</h4>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <!-- Quick Start -->
              <div
                @click="selectSetupMethod(appId, 'default')"
                class="border-2 border-gray-200 hover:border-green-400 rounded-xl p-5 cursor-pointer transition-all hover:shadow-md group"
              >
                <div class="flex flex-col items-center text-center">
                  <div class="w-14 h-14 bg-green-100 group-hover:bg-green-200 rounded-full flex items-center justify-center mb-3 transition-colors">
                    <svg class="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h5 class="font-bold text-gray-900 mb-1">Quick Start</h5>
                  <p class="text-xs text-gray-600 mb-2">Use shared Lodgeick app</p>
                  <span class="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">30 seconds</span>
                </div>
              </div>

              <!-- AI-Powered -->
              <div
                @click="selectSetupMethod(appId, 'ai')"
                class="border-2 border-gray-200 hover:border-purple-400 rounded-xl p-5 cursor-pointer transition-all hover:shadow-md group"
              >
                <div class="flex flex-col items-center text-center">
                  <div class="w-14 h-14 bg-purple-100 group-hover:bg-purple-200 rounded-full flex items-center justify-center mb-3 transition-colors">
                    <svg class="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h5 class="font-bold text-gray-900 mb-1">AI-Powered</h5>
                  <p class="text-xs text-gray-600 mb-2">Claude guides setup</p>
                  <span class="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">2 minutes</span>
                </div>
              </div>

              <!-- Manual -->
              <div
                @click="selectSetupMethod(appId, 'manual')"
                class="border-2 border-gray-200 hover:border-gray-400 rounded-xl p-5 cursor-pointer transition-all hover:shadow-md group"
              >
                <div class="flex flex-col items-center text-center">
                  <div class="w-14 h-14 bg-gray-100 group-hover:bg-gray-200 rounded-full flex items-center justify-center mb-3 transition-colors">
                    <svg class="w-7 h-7 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <h5 class="font-bold text-gray-900 mb-1">Manual Setup</h5>
                  <p class="text-xs text-gray-600 mb-2">Full control, your credentials</p>
                  <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">10 minutes</span>
                </div>
              </div>
            </div>
          </div>

          <!-- If setup method selected but not authorized: Show connect button -->
          <div v-else-if="hasCredentials(appId) && !isAuthorized(appId)">
            <div class="text-center py-6">
              <div class="mb-4">
                <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <h4 class="text-xl font-bold text-gray-900 mb-2">Ready to Connect</h4>
                <p class="text-gray-600 mb-6">Click below to authorize {{ getAppById(appId)?.name }} access</p>
              </div>
              <button
                @click="authorizeApp(appId)"
                :disabled="authorizingApp === appId"
                class="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors inline-flex items-center gap-2 text-lg"
              >
                <svg v-if="authorizingApp !== appId" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                {{ authorizingApp === appId ? 'Connecting...' : 'Connect ' + getAppById(appId)?.name }}
              </button>
            </div>
          </div>

          <!-- If authorized: Show success -->
          <div v-else-if="isAuthorized(appId)">
            <div class="text-center py-6">
              <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <h4 class="text-2xl font-bold text-gray-900 mb-2">{{ getAppById(appId)?.name }} Connected!</h4>
              <p class="text-gray-600">You're ready to use {{ getAppById(appId)?.name }} integrations</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-between items-center">
        <SecondaryButton
          label="Back"
          @click="goBack"
        >
          <template #icon>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </template>
        </SecondaryButton>

        <div class="flex gap-3">
          <SecondaryButton
            label="Skip for Now"
            @click="skipToCompletion"
          />

          <PrimaryButton
            label="Continue"
            :disabled="!allAppsConnected"
            @click="nextStep"
          >
            <template #iconRight>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </template>
          </PrimaryButton>
        </div>
      </div>
    </div>

    <!-- OAuth Setup Wizard Modal (only for manual setup) -->
    <OAuthSetupWizard
      :show="wizardVisible"
      :provider="selectedProvider"
      @close="wizardVisible = false"
      @success="handleCredentialsSaved"
      @launch-a-i-wizard="launchAIWizard"
    />

    <!-- Google AI Setup Wizard Modal -->
    <GoogleAISetupWizard
      :show="aiWizardVisible"
      @close="aiWizardVisible = false"
      @success="handleAISetupComplete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource, call } from 'frappe-ui'
import { session } from '@/data/session'
import { useOnboardingStore } from '@/stores/onboarding'
import StepProgressBar from '@/components/onboarding/StepProgressBar.vue'
import PrimaryButton from '@/components/onboarding/PrimaryButton.vue'
import SecondaryButton from '@/components/onboarding/SecondaryButton.vue'
import OAuthSetupWizard from '@/components/OAuthSetupWizard.vue'
import GoogleAISetupWizard from '@/components/GoogleAISetupWizard.vue'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const onboardingStore = useOnboardingStore()
const toast = useToast()

const handleLogout = () => {
  session.logout.submit()
}

// State
const wizardVisible = ref(false)
const aiWizardVisible = ref(false)
const selectedProvider = ref('')
const authorizingApp = ref(null)
const appCredentials = ref({}) // Track which apps have credentials
const appTokens = ref({}) // Track which apps have tokens

// Get app by ID
const getAppById = (appId) => {
  return onboardingStore.availableApps.find(app => app.id === appId)
}

// Check if app has credentials
const hasCredentials = (appId) => {
  return appCredentials.value[appId] === true
}

// Check if app is authorized (has token)
const isAuthorized = (appId) => {
  return appTokens.value[appId] === true
}

// Check if all apps are connected (NO MORE TEST STEP!)
const allAppsConnected = computed(() => {
  return onboardingStore.connectedApps.every(appId => isAuthorized(appId))
})

// Select setup method (inline, no modal for initial selection)
const selectSetupMethod = async (appId, method) => {
  const app = getAppById(appId)
  if (!app) return

  const provider = app.oauth_provider || appId
  selectedProvider.value = provider

  if (method === 'default') {
    // Quick Start: Use shared Lodgeick OAuth app
    try {
      await call('lodgeick.api.oauth.save_user_oauth_setup', {
        provider,
        tier: 'default',
        use_default: true
      })
      appCredentials.value[appId] = true
      toast.success(`${app.name} is ready to connect! 🎉`)
    } catch (error) {
      toast.error(`Failed to setup: ${error.message || error}`)
    }
  } else if (method === 'ai') {
    // AI-Powered: Launch AI wizard
    aiWizardVisible.value = true
  } else if (method === 'manual') {
    // Manual: Open full wizard modal
    wizardVisible.value = true
  }
}

// Handle credentials saved (from manual wizard)
const handleCredentialsSaved = (data) => {
  wizardVisible.value = false
  const appId = onboardingStore.connectedApps.find(id => {
    const app = getAppById(id)
    return app && (app.oauth_provider === data.provider || app.id === data.provider)
  })
  if (appId) {
    appCredentials.value[appId] = true
  }
}

// Launch AI Setup Wizard
const launchAIWizard = () => {
  wizardVisible.value = false
  aiWizardVisible.value = true
}

// Handle AI setup complete
const handleAISetupComplete = (data) => {
  aiWizardVisible.value = false
  const googleAppId = onboardingStore.connectedApps.find(id => {
    const app = getAppById(id)
    return app && (app.oauth_provider === 'google' || app.id === 'google')
  })
  if (googleAppId) {
    appCredentials.value[googleAppId] = true
  }
  toast.success('Google Cloud setup complete! Ready to connect.')
}

// Authorize app - initiate OAuth flow
const authorizeApp = async (appId) => {
  const app = getAppById(appId)
  if (!app) return

  authorizingApp.value = appId
  const provider = app.oauth_provider || appId

  try {
    const response = await initiateOAuthResource.submit({ provider })
    if (response.success && response.authorization_url) {
      // Redirect to OAuth provider - authorization IS the connection test!
      window.location.href = response.authorization_url
    }
  } catch (error) {
    console.error('Failed to initiate OAuth:', error)
    toast.error('Failed to start authorization. Please check your setup.')
  } finally {
    authorizingApp.value = null
  }
}

// Initiate OAuth resource
const initiateOAuthResource = createResource({
  url: 'lodgeick.api.oauth.initiate_oauth',
  makeParams(values) {
    return {
      provider: values.provider,
      redirect_uri: window.location.origin + '/oauth/callback'
    }
  }
})

// Navigation
const nextStep = () => {
  onboardingStore.nextStep()
  router.push({ name: 'Configure' })
}

const skipToCompletion = () => {
  onboardingStore.completeOnboarding()
  router.push({ name: 'Dashboard' })
}

const goBack = () => {
  onboardingStore.previousStep()
  router.push({ name: 'ConnectApps' })
}

// Check for OAuth callback on mount
onMounted(() => {
  if (onboardingStore.connectedApps.length === 0) {
    router.push({ name: 'ConnectApps' })
    return
  }

  // Check if returning from OAuth callback
  const urlParams = new URLSearchParams(window.location.search)
  const success = urlParams.get('oauth_success')
  const provider = urlParams.get('provider')

  if (success === 'true' && provider) {
    const appId = onboardingStore.connectedApps.find(id => {
      const app = getAppById(id)
      return app && (app.oauth_provider === provider || app.id === provider)
    })

    if (appId) {
      appTokens.value[appId] = true
      appCredentials.value[appId] = true
    }

    // Clean up URL
    window.history.replaceState({}, document.title, window.location.pathname)
  }
})
</script>

<style scoped>
/* Add any custom styles here */
</style>
