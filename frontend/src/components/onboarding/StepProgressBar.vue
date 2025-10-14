<template>
  <div class="w-full max-w-2xl mx-auto mb-8">
    <!-- Step Labels -->
    <div class="flex justify-between mb-2">
      <div
        v-for="step in steps"
        :key="step.number"
        class="flex-1 text-center"
      >
        <div
          class="text-sm font-medium transition-colors"
          :class="
            step.number <= currentStep
              ? 'text-blue-600'
              : 'text-gray-400'
          "
        >
          {{ step.label }}
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="relative">
      <!-- Background -->
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <!-- Active Progress -->
        <div
          class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-500 ease-out"
          :style="{ width: `${progress}%` }"
        />
      </div>

      <!-- Step Indicators -->
      <div class="absolute top-1/2 left-0 right-0 flex justify-between -translate-y-1/2">
        <div
          v-for="step in steps"
          :key="step.number"
          class="flex items-center justify-center w-8 h-8 rounded-full border-2 bg-white transition-all duration-300"
          :class="
            step.number < currentStep
              ? 'border-blue-600 bg-blue-600'
              : step.number === currentStep
              ? 'border-blue-600 bg-white scale-110'
              : 'border-gray-300'
          "
        >
          <!-- Checkmark for completed steps -->
          <svg
            v-if="step.number < currentStep"
            class="w-4 h-4 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="3"
              d="M5 13l4 4L19 7"
            />
          </svg>
          <!-- Step number for current/future steps -->
          <span
            v-else
            class="text-xs font-semibold"
            :class="
              step.number === currentStep
                ? 'text-blue-600'
                : 'text-gray-400'
            "
          >
            {{ step.number }}
          </span>
        </div>
      </div>
    </div>

    <!-- Step Description -->
    <div class="text-center mt-4">
      <p class="text-sm text-gray-600">
        Step {{ currentStep }} of {{ totalSteps }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentStep: {
    type: Number,
    required: true,
  },
  totalSteps: {
    type: Number,
    default: 2,
  },
})

const steps = computed(() => [
  { number: 1, label: 'Connect Apps' },
  { number: 2, label: 'Setup OAuth' },
])

const progress = computed(() => {
  return ((props.currentStep - 1) / (props.totalSteps - 1)) * 100
})
</script>
