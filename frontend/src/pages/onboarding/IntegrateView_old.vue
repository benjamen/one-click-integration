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
          Set up OAuth credentials and authorize each app to enable seamless integrations
        </p>
      </div>

      <!-- Apps Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div
          v-for="appId in onboardingStore.connectedApps"
          :key="appId"
          class="bg-white rounded-2xl shadow-lg p-6 transition-all duration-200 hover:shadow-xl"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-4">
              <div
                class="w-16 h-16 rounded-lg flex items-center justify-center text-3xl"
                :class="getAppById(appId)?.color"
              >
                {{ getAppById(appId)?.icon }}
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900">
                  {{ getAppById(appId)?.name }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ getAppById(appId)?.description }}
                </p>
              </div>
            </div>
            <div
              class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
              :class="getConnectionStatus(appId) === 'connected' ? 'bg-green-100' : getConnectionStatus(appId) === 'credentials' ? 'bg-yellow-100' : 'bg-gray-100'"
            >
              <svg
                v-if="getConnectionStatus(appId) === 'connected'"
                class="w-5 h-5 text-green-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <svg
                v-else-if="getConnectionStatus(appId) === 'credentials'"
                class="w-5 h-5 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <svg
                v-else
                class="w-5 h-5 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
          </div>

          <!-- Connection Steps -->
          <div class="space-y-3">
            <!-- Step 1: Set up OAuth Credentials -->
            <div class="flex items-center gap-3">
              <div
                class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="hasCredentials(appId) ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
              >
                {{ hasCredentials(appId) ? '✓' : '1' }}
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  OAuth Credentials
                </p>
                <button
                  v-if="!hasCredentials(appId)"
                  @click="openWizard(appId)"
                  class="text-xs text-blue-600 hover:text-blue-700 font-medium"
                >
                  Set up credentials →
                </button>
                <p v-else class="text-xs text-green-600">
                  Configured
                </p>
              </div>
            </div>

            <!-- Step 2: Authorize -->
            <div class="flex items-center gap-3">
              <div
                class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="isAuthorized(appId) ? 'bg-green-500 text-white' : hasCredentials(appId) ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-700'"
              >
                {{ isAuthorized(appId) ? '✓' : '2' }}
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  Authorize Access
                </p>
                <button
                  v-if="hasCredentials(appId) && !isAuthorized(appId)"
                  @click="authorizeApp(appId)"
                  :disabled="authorizingApp === appId"
                  class="text-xs text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
                >
                  {{ authorizingApp === appId ? 'Authorizing...' : 'Authorize now →' }}
                </button>
                <p v-else-if="isAuthorized(appId)" class="text-xs text-green-600">
                  Authorized
                </p>
                <p v-else class="text-xs text-gray-500">
                  Complete step 1 first
                </p>
              </div>
            </div>

            <!-- Step 3: Test Connection -->
            <div class="flex items-center gap-3">
              <div
                class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                :class="connectionTested[appId] ? 'bg-green-500 text-white' : isAuthorized(appId) ? 'bg-blue-500 text-white' : 'bg-gray-300 text-gray-700'"
              >
                {{ connectionTested[appId] ? '✓' : '3' }}
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  Test Connection
                </p>
                <button
                  v-if="isAuthorized(appId) && !connectionTested[appId]"
                  @click="testConnection(appId)"
                  :disabled="testingConnection === appId"
                  class="text-xs text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
                >
                  {{ testingConnection === appId ? 'Testing...' : 'Test now →' }}
                </button>
                <p v-else-if="connectionTested[appId]" class="text-xs text-green-600">
                  Connection verified
                </p>
                <p v-else class="text-xs text-gray-500">
                  Complete step 2 first
                </p>
              </div>
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

    <!-- OAuth Setup Wizard Modal -->
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
import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useOnboardingStore } from '@/stores/onboarding'
import StepProgressBar from '@/components/onboarding/StepProgressBar.vue'
import PrimaryButton from '@/components/onboarding/PrimaryButton.vue'
import SecondaryButton from '@/components/onboarding/SecondaryButton.vue'
import OAuthSetupWizard from '@/components/OAuthSetupWizard.vue'
import GoogleAISetupWizard from '@/components/GoogleAISetupWizard.vue'

const router = useRouter()
const onboardingStore = useOnboardingStore()

const handleLogout = () => {
  session.logout.submit()
}

// State
const wizardVisible = ref(false)
const aiWizardVisible = ref(false)
const selectedProvider = ref('')
const authorizingApp = ref(null)
const testingConnection = ref(null)
const connectionTested = ref({})
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

// Get connection status
const getConnectionStatus = (appId) => {
  if (isAuthorized(appId) && connectionTested.value[appId]) {
    return 'connected'
  } else if (hasCredentials(appId)) {
    return 'credentials'
  }
  return 'not-connected'
}

// Check if all apps are connected
const allAppsConnected = computed(() => {
  return onboardingStore.connectedApps.every(appId =>
    isAuthorized(appId) && connectionTested.value[appId]
  )
})

// Open OAuth wizard for an app
const openWizard = (appId) => {
  const app = getAppById(appId)
  if (app) {
    selectedProvider.value = app.oauth_provider || appId
    wizardVisible.value = true
  }
}

// Handle credentials saved
const handleCredentialsSaved = (data) => {
  wizardVisible.value = false
  // Mark credentials as saved for this provider
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
  // Mark Google as having credentials
  const googleAppId = onboardingStore.connectedApps.find(id => {
    const app = getAppById(id)
    return app && (app.oauth_provider === 'google' || app.id === 'google')
  })
  if (googleAppId) {
    appCredentials.value[googleAppId] = true
  }
  // Show success message
  alert('Google Cloud integration setup complete! You can now authorize access.')
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
      // Redirect to OAuth provider
      window.location.href = response.authorization_url
    }
  } catch (error) {
    console.error('Failed to initiate OAuth:', error)
    alert('Failed to start authorization. Please check your credentials.')
  } finally {
    authorizingApp.value = null
  }
}

// Test connection
const testConnection = async (appId) => {
  const app = getAppById(appId)
  if (!app) return

  testingConnection.value = appId
  const provider = app.oauth_provider || appId

  try {
    // Simulate connection test (replace with actual API call)
    await new Promise(resolve => setTimeout(resolve, 1500))
    connectionTested.value[appId] = true

    // In a real implementation, you would call an API like:
    // const response = await testConnectionResource.submit({ provider })
    // connectionTested.value[appId] = response.success
  } catch (error) {
    console.error('Connection test failed:', error)
    alert('Connection test failed. Please try authorizing again.')
  } finally {
    testingConnection.value = null
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
  // If no apps connected, redirect back
  if (onboardingStore.connectedApps.length === 0) {
    router.push({ name: 'ConnectApps' })
    return
  }

  // Check if returning from OAuth callback
  const urlParams = new URLSearchParams(window.location.search)
  const success = urlParams.get('oauth_success')
  const provider = urlParams.get('provider')

  if (success === 'true' && provider) {
    // Find the app with this provider
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
