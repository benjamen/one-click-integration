<template>
  <div class="bg-white rounded-xl shadow-sm border-2 border-blue-200 p-6">
    <!-- Header -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1">
        <h3 class="text-lg font-bold text-gray-900 mb-1">Getting Started</h3>
        <p class="text-sm text-gray-600">Complete these steps to set up your integrations</p>
      </div>
      <button
        v-if="canDismiss && !isDismissed"
        @click="dismiss"
        aria-label="Dismiss checklist"
        class="text-gray-400 hover:text-gray-600 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Progress Bar -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">
          {{ completedCount }} of {{ totalCount }} completed
        </span>
        <span class="text-sm font-semibold text-blue-600">{{ progressPercentage }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-500 ease-out"
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </div>

    <!-- Checklist Items -->
    <div class="space-y-3">
      <div
        v-for="item in items"
        :key="item.id"
        class="flex items-start gap-3 p-3 rounded-lg transition-all"
        :class="[
          item.completed ? 'bg-green-50' : 'bg-gray-50 hover:bg-gray-100',
          item.isActive && !item.completed ? 'ring-2 ring-blue-500 bg-blue-50' : ''
        ]"
      >
        <!-- Checkbox -->
        <div class="flex-shrink-0 mt-0.5">
          <div
            class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
            :class="
              item.completed
                ? 'bg-green-500 border-green-500'
                : 'border-gray-300 bg-white'
            "
          >
            <svg
              v-if="item.completed"
              class="w-4 h-4 text-white"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clip-rule="evenodd"
              />
            </svg>
            <div
              v-else-if="item.isActive"
              class="w-2 h-2 rounded-full bg-blue-500 animate-pulse"
            ></div>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <h4
              class="text-sm font-semibold transition-all"
              :class="item.completed ? 'text-green-700 line-through' : 'text-gray-900'"
            >
              {{ item.title }}
            </h4>
            <span
              v-if="item.isOptional"
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-700"
            >
              Optional
            </span>
          </div>
          <p class="text-sm text-gray-600 mb-2">{{ item.description }}</p>

          <!-- Action Button -->
          <button
            v-if="!item.completed && item.actionLabel"
            @click="handleAction(item)"
            class="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          >
            {{ item.actionLabel }}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <!-- Completion Time -->
          <div
            v-if="item.completed && item.completedAt"
            class="text-xs text-green-600 mt-1"
          >
            Completed {{ formatTime(item.completedAt) }}
          </div>
        </div>

        <!-- Estimated Time -->
        <div v-if="!item.completed && item.estimatedTime" class="flex-shrink-0">
          <span class="text-xs text-gray-500">~{{ item.estimatedTime }}</span>
        </div>
      </div>
    </div>

    <!-- Celebration Message -->
    <div
      v-if="isCompleted && !isDismissed"
      class="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border-2 border-green-200"
    >
      <div class="flex items-start gap-3">
        <div class="text-2xl">🎉</div>
        <div class="flex-1">
          <h4 class="font-bold text-green-800 mb-1">Great job!</h4>
          <p class="text-sm text-green-700 mb-3">
            You've completed all the essential steps. Your integrations are ready to use!
          </p>
          <button
            @click="goToDashboard"
            class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition-colors"
          >
            Go to Dashboard
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    validator: (items) => {
      return items.every(item =>
        item.id &&
        item.title &&
        item.description &&
        typeof item.completed === 'boolean'
      )
    }
  },
  canDismiss: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['action', 'dismiss'])

const router = useRouter()
const isDismissed = ref(false)

// Computed
const completedCount = computed(() => {
  return props.items.filter(item => item.completed).length
})

const totalCount = computed(() => {
  return props.items.length
})

const progressPercentage = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

const isCompleted = computed(() => {
  return completedCount.value === totalCount.value && totalCount.value > 0
})

// Methods
function handleAction(item) {
  emit('action', item.id, item.actionRoute)
}

function dismiss() {
  isDismissed.value = true
  emit('dismiss')
}

function goToDashboard() {
  router.push('/dashboard')
}

function formatTime(timestamp) {
  if (!timestamp) return ''

  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'just now'
}

// Watch for completion and celebrate
watch(isCompleted, (newVal) => {
  if (newVal && !isDismissed.value) {
    // Could trigger confetti animation or sound here
    console.log('🎉 Onboarding completed!')
  }
})
</script>
