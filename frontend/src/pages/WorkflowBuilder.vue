<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <router-link to="/dashboard" class="text-gray-600 hover:text-gray-900">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </router-link>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Create Workflow</h1>
              <p class="text-sm text-gray-600">Connect your data sources and define how they sync</p>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Progress Steps (only show when user has 2+ apps) -->
      <div v-if="connectedApps.length >= 2" class="mb-8 overflow-x-auto">
        <div class="flex items-center min-w-max">
          <div
            v-for="(step, index) in steps"
            :key="step.id"
            class="flex items-center"
          >
            <!-- Step Circle -->
            <div class="flex items-center flex-shrink-0">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all"
                :class="getStepClass(index)"
              >
                <span v-if="index < currentStepIndex">✓</span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="ml-2 hidden sm:block">
                <div class="text-xs font-medium whitespace-nowrap" :class="index <= currentStepIndex ? 'text-gray-900' : 'text-gray-500'">
                  {{ step.title }}
                </div>
              </div>
            </div>

            <!-- Connector Line -->
            <div
              v-if="index < steps.length - 1"
              class="w-12 sm:w-16 h-0.5 mx-2"
              :class="index < currentStepIndex ? 'bg-blue-600' : 'bg-gray-300'"
            ></div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="bg-white rounded-xl shadow-lg p-8">
        <!-- Empty State: No Apps Connected -->
        <div v-if="connectedApps.length === 0" class="text-center py-12">
          <div class="mb-6">
            <div class="w-24 h-24 mx-auto bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center">
              <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>

          <h3 class="text-xl font-bold text-gray-900 mb-2">
            No Apps Connected Yet
          </h3>
          <p class="text-gray-600 mb-6 max-w-md mx-auto">
            You need to connect at least 2 apps before you can create a workflow. Apps allow you to sync data between different platforms.
          </p>

          <router-link
            to="/connect"
            class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg hover:scale-105 transition-all no-underline"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Connect Your First App
          </router-link>
        </div>

        <!-- Empty State: Only One App Connected -->
        <div v-else-if="connectedApps.length === 1" class="text-center py-12">
          <div class="mb-6">
            <div class="w-24 h-24 mx-auto bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
              <div class="text-4xl">{{ connectedApps[0].icon }}</div>
            </div>
          </div>

          <h3 class="text-xl font-bold text-gray-900 mb-2">
            Connect One More App
          </h3>
          <p class="text-gray-600 mb-6 max-w-md mx-auto">
            You have <strong>{{ connectedApps[0].name }}</strong> connected. Connect at least one more app to create data sync workflows.
          </p>

          <router-link
            to="/connect"
            class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg hover:scale-105 transition-all no-underline"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Connect Another App
          </router-link>
        </div>

        <!-- Step 1: Select Source App -->
        <div v-else-if="currentStep === 'source_app'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Source App</h2>
          <p class="text-gray-600 mb-6">Choose which app you want to pull data from</p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="app in connectedApps"
              :key="app.id"
              @click="selectSourceApp(app)"
              class="border-2 rounded-lg p-4 cursor-pointer transition-all"
              :class="workflow.sourceApp?.id === app.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="flex items-center gap-3">
                <div class="text-3xl">{{ app.icon }}</div>
                <div class="flex-1">
                  <div class="font-semibold text-gray-900">{{ app.name }}</div>
                  <div class="text-sm text-gray-600">{{ app.description }}</div>
                </div>
                <div v-if="workflow.sourceApp?.id === app.id" class="text-blue-600">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Select Source Resource -->
        <div v-else-if="currentStep === 'source_resource'">
          <div class="mb-4 flex items-center gap-2 text-sm text-gray-600">
            <div class="text-2xl">{{ workflow.sourceApp?.icon }}</div>
            <span class="font-medium">{{ workflow.sourceApp?.name }}</span>
          </div>

          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Source {{ workflow.sourceApp?.resourceType || 'Resource' }}</h2>
          <p class="text-gray-600 mb-6">Choose the specific {{ workflow.sourceApp?.resourceType?.toLowerCase() || 'resource' }} to pull data from</p>

          <div class="space-y-3">
            <div
              v-for="resource in availableSourceResources"
              :key="resource.id"
              @click="workflow.sourceResource = resource"
              class="border-2 rounded-lg p-4 cursor-pointer transition-all"
              :class="workflow.sourceResource?.id === resource.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="flex items-center justify-between">
                <div class="font-semibold text-gray-900">{{ resource.name }}</div>
                <div v-if="workflow.sourceResource?.id === resource.id" class="text-blue-600">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Select Source Fields -->
        <div v-else-if="currentStep === 'source_fields'">
          <div class="mb-4 flex items-center gap-2 text-sm text-gray-600">
            <div class="text-2xl">{{ workflow.sourceApp?.icon }}</div>
            <span class="font-medium">{{ workflow.sourceApp?.name }}</span>
            <span>→</span>
            <span class="font-medium">{{ workflow.sourceResource?.name }}</span>
          </div>

          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Source Fields</h2>
          <p class="text-gray-600 mb-6">Choose which fields to include from {{ workflow.sourceResource?.name }}</p>

          <div class="space-y-2">
            <label
              v-for="field in sourceFields"
              :key="field"
              class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-all"
              :class="workflow.sourceFields.includes(field) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <input
                type="checkbox"
                :value="field"
                v-model="workflow.sourceFields"
                class="mr-3 w-4 h-4"
              />
              <span class="font-medium text-gray-900">{{ field }}</span>
            </label>
          </div>
        </div>

        <!-- Step 4: Select Destination App -->
        <div v-else-if="currentStep === 'destination_app'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Destination App</h2>
          <p class="text-gray-600 mb-6">Choose where you want to send the data</p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="app in availableDestinationApps"
              :key="app.id"
              @click="selectDestinationApp(app)"
              class="border-2 rounded-lg p-4 cursor-pointer transition-all"
              :class="workflow.destinationApp?.id === app.id ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-green-300'"
            >
              <div class="flex items-center gap-3">
                <div class="text-3xl">{{ app.icon }}</div>
                <div class="flex-1">
                  <div class="font-semibold text-gray-900">{{ app.name }}</div>
                  <div class="text-sm text-gray-600">{{ app.description }}</div>
                </div>
                <div v-if="workflow.destinationApp?.id === app.id" class="text-green-600">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 5: Select Destination Resource -->
        <div v-else-if="currentStep === 'destination_resource'">
          <div class="mb-4 flex items-center gap-2 text-sm text-gray-600">
            <div class="text-2xl">{{ workflow.destinationApp?.icon }}</div>
            <span class="font-medium">{{ workflow.destinationApp?.name }}</span>
          </div>

          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Destination {{ workflow.destinationApp?.resourceType || 'Resource' }}</h2>
          <p class="text-gray-600 mb-6">Choose the specific {{ workflow.destinationApp?.resourceType?.toLowerCase() || 'resource' }} to send data to</p>

          <div class="space-y-3">
            <div
              v-for="resource in availableDestinationResources"
              :key="resource.id"
              @click="workflow.destinationResource = resource"
              class="border-2 rounded-lg p-4 cursor-pointer transition-all"
              :class="workflow.destinationResource?.id === resource.id ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-green-300'"
            >
              <div class="flex items-center justify-between">
                <div class="font-semibold text-gray-900">{{ resource.name }}</div>
                <div v-if="workflow.destinationResource?.id === resource.id" class="text-green-600">
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 6: Map Fields -->
        <div v-else-if="currentStep === 'field_mapping'">
          <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-center justify-between text-sm">
              <div class="flex items-center gap-2">
                <div class="text-2xl">{{ workflow.sourceApp?.icon }}</div>
                <div>
                  <div class="font-medium text-blue-900">{{ workflow.sourceResource?.name }}</div>
                  <div class="text-xs text-blue-700">{{ workflow.sourceFields.length }} fields selected</div>
                </div>
              </div>
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <div class="flex items-center gap-2">
                <div class="text-2xl">{{ workflow.destinationApp?.icon }}</div>
                <div>
                  <div class="font-medium text-blue-900">{{ workflow.destinationResource?.name }}</div>
                </div>
              </div>
            </div>
          </div>

          <h2 class="text-2xl font-bold text-gray-900 mb-2">Map Fields</h2>
          <p class="text-gray-600 mb-6">Connect source fields to destination fields</p>

          <div class="space-y-3">
            <div
              v-for="(sourceField, index) in workflow.sourceFields"
              :key="index"
              class="p-4 bg-gray-50 rounded-lg"
            >
              <div class="grid grid-cols-2 gap-4 items-center">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">From Source</label>
                  <div class="px-3 py-2 bg-white border border-gray-300 rounded-lg font-medium text-gray-900">
                    {{ sourceField }}
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">To Destination</label>
                  <select
                    v-model="workflow.fieldMappings[index]"
                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                  >
                    <option value="">-- Select destination field --</option>
                    <option v-for="field in destinationFields" :key="field" :value="field">
                      {{ field }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 7: Configure Sync -->
        <div v-else-if="currentStep === 'sync'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Configure Sync</h2>
          <p class="text-gray-600 mb-6">Set up when and how often data should sync</p>

          <div class="space-y-6">
            <!-- Workflow Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Workflow Name
              </label>
              <input
                v-model="workflow.name"
                type="text"
                :placeholder="`Sync ${workflow.sourceResource?.name} to ${workflow.destinationResource?.name}`"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <!-- Sync Trigger -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                When should this sync run?
              </label>
              <div class="space-y-3">
                <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all" :class="workflow.trigger === 'manual' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
                  <input v-model="workflow.trigger" type="radio" value="manual" class="mr-3" />
                  <div>
                    <div class="font-medium text-gray-900">Manual</div>
                    <div class="text-sm text-gray-600">Run this workflow manually whenever you want</div>
                  </div>
                </label>

                <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all" :class="workflow.trigger === 'schedule' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
                  <input v-model="workflow.trigger" type="radio" value="schedule" class="mr-3" />
                  <div>
                    <div class="font-medium text-gray-900">Schedule</div>
                    <div class="text-sm text-gray-600">Run automatically on a schedule</div>
                  </div>
                </label>

                <label class="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all" :class="workflow.trigger === 'realtime' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'">
                  <input v-model="workflow.trigger" type="radio" value="realtime" class="mr-3" />
                  <div class="flex-1">
                    <div class="font-medium text-gray-900">Real-time (Webhook)</div>
                    <div class="text-sm text-gray-600">Sync immediately when data changes</div>
                  </div>
                  <span class="px-2 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">Pro</span>
                </label>
              </div>
            </div>

            <!-- Schedule Options (if schedule selected) -->
            <div v-if="workflow.trigger === 'schedule'" class="p-4 bg-gray-50 rounded-lg">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Sync Frequency
              </label>
              <select
                v-model="workflow.schedule"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="15min">Every 15 minutes</option>
                <option value="hourly">Every hour</option>
                <option value="daily">Once a day</option>
                <option value="weekly">Once a week</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Navigation Buttons (only show when user has 2+ apps) -->
        <div v-if="connectedApps.length >= 2" class="mt-8 flex justify-between">
          <button
            v-if="currentStepIndex > 0"
            @click="previousStep"
            class="px-6 py-2 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-all"
          >
            ← Back
          </button>
          <div v-else></div>

          <button
            v-if="currentStepIndex < steps.length - 1"
            @click="nextStep"
            :disabled="!canProceed"
            class="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all"
          >
            Continue →
          </button>
          <button
            v-else
            @click="createWorkflow"
            :disabled="!canProceed"
            class="px-6 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all"
          >
            ✓ Create Workflow
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useOnboardingStore } from '@/stores/onboarding'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const onboardingStore = useOnboardingStore()
const toast = useToast()

// Steps
const steps = ref([
  { id: 'source_app', title: 'Source App' },
  { id: 'source_resource', title: 'Source Table' },
  { id: 'source_fields', title: 'Source Fields' },
  { id: 'destination_app', title: 'Destination App' },
  { id: 'destination_resource', title: 'Destination Table' },
  { id: 'field_mapping', title: 'Field Mapping' },
  { id: 'sync', title: 'Sync Settings' }
])

const currentStep = ref('source_app')

const currentStepIndex = computed(() => {
  return steps.value.findIndex(s => s.id === currentStep.value)
})

// Workflow state
const workflow = ref({
  name: '',
  sourceApp: null,
  sourceResource: null,
  sourceFields: [],
  destinationApp: null,
  destinationResource: null,
  destinationFields: [],
  fieldMappings: [],
  trigger: 'manual',
  schedule: 'hourly'
})

// Connected apps
const connectedApps = computed(() => {
  return onboardingStore.connectedApps
    .map(id => onboardingStore.availableApps.find(app => app.id === id))
    .filter(Boolean)
    .map(app => ({
      ...app,
      resourceType: getResourceType(app.id)
    }))
})

function getResourceType(appId) {
  const types = {
    'google_sheets': 'Spreadsheet',
    'airtable': 'Base',
    'notion': 'Database',
    'salesforce': 'Object',
    'hubspot': 'Object',
    'xero': 'Organization'
  }
  return types[appId] || 'Resource'
}

// Available destination apps (exclude source)
const availableDestinationApps = computed(() => {
  return connectedApps.value.filter(app => app.id !== workflow.value.sourceApp?.id)
})

// Mock resources (in real app, fetch from API)
const availableSourceResources = computed(() => {
  if (!workflow.value.sourceApp) return []

  // Mock data based on app type
  if (workflow.value.sourceApp.id === 'google_sheets') {
    return [
      { id: '1', name: 'Customer Database 2025' },
      { id: '2', name: 'Sales Leads Q1' },
      { id: '3', name: 'Invoice Tracker' }
    ]
  }
  return []
})

const availableDestinationResources = computed(() => {
  if (!workflow.value.destinationApp) return []

  // Mock data
  if (workflow.value.destinationApp.id === 'salesforce') {
    return [
      { id: '1', name: 'Leads' },
      { id: '2', name: 'Contacts' },
      { id: '3', name: 'Opportunities' }
    ]
  }
  return []
})

// Mock fields (in real app, fetch from selected resource)
const sourceFields = computed(() => {
  if (!workflow.value.sourceResource) return []
  return ['Full Name', 'Email Address', 'Phone Number', 'Company', 'Status', 'Notes']
})

const destinationFields = computed(() => {
  if (!workflow.value.destinationResource) return []
  return ['First Name', 'Last Name', 'Email', 'Phone', 'Company Name', 'Lead Status', 'Description']
})

// Step functions
function getStepClass(index) {
  if (index < currentStepIndex.value) {
    return 'bg-blue-600 text-white'
  } else if (index === currentStepIndex.value) {
    return 'bg-blue-100 text-blue-600 ring-2 ring-blue-600'
  } else {
    return 'bg-gray-200 text-gray-600'
  }
}

function selectSourceApp(app) {
  workflow.value.sourceApp = app
  workflow.value.sourceResource = null
  workflow.value.sourceFields = []
}

function selectDestinationApp(app) {
  workflow.value.destinationApp = app
  workflow.value.destinationResource = null
  workflow.value.destinationFields = []
}

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 'source_app':
      return workflow.value.sourceApp !== null
    case 'source_resource':
      return workflow.value.sourceResource !== null
    case 'source_fields':
      return workflow.value.sourceFields.length > 0
    case 'destination_app':
      return workflow.value.destinationApp !== null
    case 'destination_resource':
      return workflow.value.destinationResource !== null
    case 'field_mapping':
      return workflow.value.fieldMappings.some(m => m !== '')
    case 'sync':
      return workflow.value.name && workflow.value.trigger
    default:
      return false
  }
})

function nextStep() {
  if (canProceed.value && currentStepIndex.value < steps.value.length - 1) {
    currentStep.value = steps.value[currentStepIndex.value + 1].id
  }
}

function previousStep() {
  if (currentStepIndex.value > 0) {
    currentStep.value = steps.value[currentStepIndex.value - 1].id
  }
}

function createWorkflow() {
  // TODO: Save workflow to backend via API
  console.log('Creating workflow:', workflow.value)

  toast.success('Workflow created successfully! 🎉')
  router.push({ name: 'Dashboard' })
}
</script>
