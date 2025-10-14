import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'

export const useOnboardingStore = defineStore('onboarding', () => {
  // Load persisted state from localStorage
  const loadPersistedState = () => {
    try {
      const saved = localStorage.getItem('lodgeick_onboarding')
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (e) {
      console.error('Failed to load persisted onboarding state:', e)
    }
    return {
      currentStep: 1,
      connectedApps: [],
      selectedIntegrations: [],
      fieldMappings: {}
    }
  }

  const persisted = loadPersistedState()

  // State
  const currentStep = ref(persisted.currentStep || 1)
  const totalSteps = ref(2) // Simplified: 1. Select Apps, 2. Connect Apps
  const isCompleted = ref(false)
  const connectedApps = ref(persisted.connectedApps || [])
  const selectedIntegrations = ref(persisted.selectedIntegrations || [])
  const fieldMappings = ref(persisted.fieldMappings || {})
  const isLoadingApps = ref(false)

  // Available apps for integration (loaded from backend)
  const availableApps = ref([])

  // Persist state to localStorage whenever it changes
  const persistState = () => {
    try {
      localStorage.setItem('lodgeick_onboarding', JSON.stringify({
        currentStep: currentStep.value,
        connectedApps: connectedApps.value,
        selectedIntegrations: selectedIntegrations.value,
        fieldMappings: fieldMappings.value
      }))
    } catch (e) {
      console.error('Failed to persist onboarding state:', e)
    }
  }

  // Computed
  const progress = computed(() => (currentStep.value / totalSteps.value) * 100)
  const canContinue = computed(() => {
    switch (currentStep.value) {
      case 1: // Select Apps
        return connectedApps.value.length > 0
      case 2: // Connect Apps (OAuth)
        return true // Can proceed after connecting
      default:
        return false
    }
  })

  const hasConnectedApps = computed(() => connectedApps.value.length > 0)

  // Actions
  async function loadApps() {
    if (availableApps.value.length > 0) return // Already loaded

    isLoadingApps.value = true
    try {
      const response = await call('lodgeick.api.catalog.get_app_catalog')

      if (response.success && response.apps) {
        availableApps.value = response.apps.map(app => ({
          id: app.app_name,
          name: app.display_name || app.app_name,
          description: app.description,
          icon: getAppIcon(app.app_name),
          color: getAppColor(app.category),
          logo_url: app.logo_url,
          category: app.category,
          oauth_provider: app.oauth_provider,
          // Restore connected state from persisted connectedApps array
          isConnected: connectedApps.value.includes(app.app_name),
          use_cases: app.use_cases || []
        }))
      }
    } catch (error) {
      console.error('Failed to load apps:', error)
      console.error('Error details:', error)
    } finally {
      isLoadingApps.value = false
    }
  }

  function getAppIcon(appName) {
    const icons = {
      'jira': '🎯',
      'slack': '💬',
      'hubspot': '🎨',
      'google_sheets': '📊',
      'salesforce': '☁️',
      'mailchimp': '✉️',
      'xero': '💼',
    }
    return icons[appName] || '🔌'
  }

  function getAppColor(category) {
    const colors = {
      'CRM': 'bg-orange-500',
      'Communication': 'bg-purple-500',
      'Productivity': 'bg-green-500',
      'Finance': 'bg-blue-600',
      'Marketing': 'bg-yellow-500',
      'Project Management': 'bg-blue-500',
    }
    return colors[category] || 'bg-gray-500'
  }

  function setStep(step) {
    currentStep.value = step
    persistState()
  }

  function nextStep() {
    if (currentStep.value < totalSteps.value) {
      currentStep.value++
      persistState()
    }
  }

  function previousStep() {
    if (currentStep.value > 1) {
      currentStep.value--
      persistState()
    }
  }

  function connectApp(appId) {
    const app = availableApps.value.find(a => a.id === appId)
    if (app && !app.isConnected) {
      app.isConnected = true
      if (!connectedApps.value.includes(appId)) {
        connectedApps.value.push(appId)
      }
      persistState()
    }
  }

  function disconnectApp(appId) {
    const app = availableApps.value.find(a => a.id === appId)
    if (app) {
      app.isConnected = false
      connectedApps.value = connectedApps.value.filter(id => id !== appId)
      selectedIntegrations.value = selectedIntegrations.value.filter(
        integration => !integration.includes(appId)
      )
      persistState()
    }
  }

  function addIntegration(fromApp, toApp) {
    const integrationKey = `${fromApp}-${toApp}`
    if (!selectedIntegrations.value.includes(integrationKey)) {
      selectedIntegrations.value.push(integrationKey)
      persistState()
    }
  }

  function removeIntegration(integrationKey) {
    selectedIntegrations.value = selectedIntegrations.value.filter(
      key => key !== integrationKey
    )
    persistState()
  }

  function saveFieldMapping(integrationKey, mapping) {
    fieldMappings.value[integrationKey] = mapping
    persistState()
  }

  function completeOnboarding() {
    isCompleted.value = true
    // Clear persisted state when onboarding is complete
    localStorage.removeItem('lodgeick_onboarding')
    // Reset for next time if needed
    currentStep.value = 1
  }

  function resetOnboarding() {
    currentStep.value = 1
    isCompleted.value = false
    connectedApps.value = []
    selectedIntegrations.value = []
    fieldMappings.value = {}
    availableApps.value.forEach(app => {
      app.isConnected = false
    })
    // Clear persisted state
    localStorage.removeItem('lodgeick_onboarding')
  }

  return {
    // State
    currentStep,
    totalSteps,
    isCompleted,
    connectedApps,
    selectedIntegrations,
    fieldMappings,
    availableApps,
    isLoadingApps,

    // Computed
    progress,
    canContinue,
    hasConnectedApps,

    // Actions
    loadApps,
    setStep,
    nextStep,
    previousStep,
    connectApp,
    disconnectApp,
    addIntegration,
    removeIntegration,
    saveFieldMapping,
    completeOnboarding,
    resetOnboarding,
  }
})
