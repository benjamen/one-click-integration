import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'

export const useOnboardingStore = defineStore('onboarding', () => {
  // State
  const currentStep = ref(1)
  const totalSteps = ref(2) // Simplified: 1. Select Apps, 2. Connect Apps
  const isCompleted = ref(false)
  const connectedApps = ref([])
  const selectedIntegrations = ref([])
  const fieldMappings = ref({})
  const isLoadingApps = ref(false)

  // Available apps for integration (loaded from backend)
  const availableApps = ref([])

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
          isConnected: false,
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
  }

  function nextStep() {
    if (currentStep.value < totalSteps.value) {
      currentStep.value++
    }
  }

  function previousStep() {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  function connectApp(appId) {
    const app = availableApps.value.find(a => a.id === appId)
    if (app && !app.isConnected) {
      app.isConnected = true
      connectedApps.value.push(appId)
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
    }
  }

  function addIntegration(fromApp, toApp) {
    const integrationKey = `${fromApp}-${toApp}`
    if (!selectedIntegrations.value.includes(integrationKey)) {
      selectedIntegrations.value.push(integrationKey)
    }
  }

  function removeIntegration(integrationKey) {
    selectedIntegrations.value = selectedIntegrations.value.filter(
      key => key !== integrationKey
    )
  }

  function saveFieldMapping(integrationKey, mapping) {
    fieldMappings.value[integrationKey] = mapping
  }

  function completeOnboarding() {
    isCompleted.value = true
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
