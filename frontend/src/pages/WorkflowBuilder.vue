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
      <!-- Progress Steps -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div
            v-for="(step, index) in steps"
            :key="step.id"
            class="flex items-center"
            :class="{ 'flex-1': index < steps.length - 1 }"
          >
            <!-- Step Circle -->
            <div class="flex items-center">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all"
                :class="getStepClass(index)"
              >
                <span v-if="index < currentStepIndex">✓</span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="ml-3">
                <div class="text-sm font-medium" :class="index <= currentStepIndex ? 'text-gray-900' : 'text-gray-500'">
                  {{ step.title }}
                </div>
              </div>
            </div>

            <!-- Connector Line -->
            <div
              v-if="index < steps.length - 1"
              class="flex-1 h-0.5 mx-4"
              :class="index < currentStepIndex ? 'bg-blue-600' : 'bg-gray-300'"
            ></div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="bg-white rounded-xl shadow-lg p-8">
        <!-- Step 1: Select Source -->
        <div v-if="currentStep === 'source'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Data Source</h2>
          <p class="text-gray-600 mb-6">Choose which app and resource you want to pull data from</p>

          <!-- Connected Apps Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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

          <!-- Resource Selection (if app selected) -->
          <div v-if="workflow.sourceApp" class="mt-6 p-4 bg-gray-50 rounded-lg">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Select {{ workflow.sourceApp.resourceType || 'Resource' }}
            </label>
            <select
              v-model="workflow.sourceResource"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">-- Choose {{ workflow.sourceApp.resourceType || 'resource' }} --</option>
              <option v-for="resource in availableSourceResources" :key="resource.id" :value="resource">
                {{ resource.name }}
              </option>
            </select>
            <p class="text-xs text-gray-500 mt-2">
              We'll fetch this list from your {{ workflow.sourceApp.name }} account
            </p>
          </div>
        </div>

        <!-- Step 2: Select Destination -->
        <div v-if="currentStep === 'destination'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Select Destination</h2>
          <p class="text-gray-600 mb-6">Choose where you want to send the data</p>

          <!-- Connected Apps Grid (excluding source) -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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

          <!-- Destination Resource Selection -->
          <div v-if="workflow.destinationApp" class="mt-6 p-4 bg-gray-50 rounded-lg">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Select {{ workflow.destinationApp.resourceType || 'Resource' }}
            </label>
            <select
              v-model="workflow.destinationResource"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">-- Choose {{ workflow.destinationApp.resourceType || 'resource' }} --</option>
              <option v-for="resource in availableDestinationResources" :key="resource.id" :value="resource">
                {{ resource.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Step 3: Map Fields -->
        <div v-if="currentStep === 'mapping'">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Map Fields</h2>
          <p class="text-gray-600 mb-6">Connect fields from {{ workflow.sourceApp?.name }} to {{ workflow.destinationApp?.name }}</p>

          <!-- Field Mapping Preview -->
          <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-center justify-between text-sm">
              <div class="font-medium text-blue-900">
                {{ workflow.sourceResource?.name }} ({{ workflow.sourceApp?.name }})
              </div>
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <div class="font-medium text-blue-900">
                {{ workflow.destinationResource?.name }} ({{ workflow.destinationApp?.name }})
              </div>
            </div>
          </div>

          <!-- Field Mappings -->
          <div class="space-y-4">
            <div
              v-for="(mapping, index) in workflow.fieldMappings"
              :key="index"
              class="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg"
            >
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">
                  From {{ workflow.sourceApp?.name }}
                </label>
                <select
                  v-model="mapping.sourceField"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select field --</option>
                  <option v-for="field in sourceFields" :key="field" :value="field">
                    {{ field }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">
                  To {{ workflow.destinationApp?.name }}
                </label>
                <select
                  v-model="mapping.destinationField"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                >
                  <option value="">-- Select field --</option>
                  <option v-for="field in destinationFields" :key="field" :value="field">
                    {{ field }}
                  </option>
                </select>
              </div>
            </div>

            <button
              @click="addFieldMapping"
              class="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-all"
            >
              + Add Field Mapping
            </button>
          </div>
        </div>

        <!-- Step 4: Configure Sync -->
        <div v-if="currentStep === 'sync'">
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
                placeholder="e.g., Sync Leads from Sheets to CRM"
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

        <!-- Navigation Buttons -->
        <div class="mt-8 flex justify-between">
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
  { id: 'source', title: 'Source' },
  { id: 'destination', title: 'Destination' },
  { id: 'mapping', title: 'Field Mapping' },
  { id: 'sync', title: 'Sync Settings' }
])

const currentStep = ref('source')

const currentStepIndex = computed(() => {
  return steps.value.findIndex(s => s.id === currentStep.value)
})

// Workflow state
const workflow = ref({
  name: '',
  sourceApp: null,
  sourceResource: null,
  destinationApp: null,
  destinationResource: null,
  fieldMappings: [
    { sourceField: '', destinationField: '' }
  ],
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
}

function selectDestinationApp(app) {
  workflow.value.destinationApp = app
  workflow.value.destinationResource = null
}

function addFieldMapping() {
  workflow.value.fieldMappings.push({ sourceField: '', destinationField: '' })
}

const canProceed = computed(() => {
  switch (currentStep.value) {
    case 'source':
      return workflow.value.sourceApp && workflow.value.sourceResource
    case 'destination':
      return workflow.value.destinationApp && workflow.value.destinationResource
    case 'mapping':
      return workflow.value.fieldMappings.some(m => m.sourceField && m.destinationField)
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
