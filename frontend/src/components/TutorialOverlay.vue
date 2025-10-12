<template>
  <!-- Tutorial Overlay -->
  <teleport to="body">
    <transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isActive && currentStepData"
        class="fixed inset-0 z-[9999]"
        @click.self="handleOverlayClick"
      >
        <!-- Backdrop with spotlight effect -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>

        <!-- Spotlight hole (transparent area around target element) -->
        <div
          v-if="spotlightStyle"
          class="absolute rounded-lg ring-4 ring-blue-500/50 ring-offset-4 ring-offset-black/50 pointer-events-none transition-all duration-300"
          :style="spotlightStyle"
        ></div>

        <!-- Tutorial Card -->
        <transition
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition-all duration-200"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="cardStyle"
            class="absolute bg-white rounded-xl shadow-2xl max-w-md transition-all duration-300"
            :style="cardStyle"
          >
            <!-- Header -->
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Step {{ currentStep + 1 }} of {{ steps.length }}
                    </span>
                    <span v-if="currentStepData.isOptional" class="text-xs text-gray-500">
                      (Optional)
                    </span>
                  </div>
                  <h3 class="text-lg font-bold text-gray-900">
                    {{ currentStepData.title }}
                  </h3>
                </div>
                <button
                  @click="skip"
                  aria-label="Close tutorial"
                  class="text-gray-400 hover:text-gray-600 transition-colors ml-2"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Content -->
            <div class="px-6 py-4">
              <p class="text-gray-700 leading-relaxed">
                {{ currentStepData.description }}
              </p>

              <!-- Action hint -->
              <div v-if="currentStepData.actionHint" class="mt-4 flex items-start gap-2 p-3 bg-blue-50 rounded-lg">
                <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                </svg>
                <span class="text-sm text-blue-900">
                  {{ currentStepData.actionHint }}
                </span>
              </div>

              <!-- Custom content slot -->
              <div v-if="$slots[`step-${currentStep}`]" class="mt-4">
                <slot :name="`step-${currentStep}`" :step="currentStepData"></slot>
              </div>
            </div>

            <!-- Footer -->
            <div class="px-6 py-4 bg-gray-50 rounded-b-xl">
              <!-- Progress dots -->
              <div class="flex items-center justify-center gap-2 mb-4">
                <button
                  v-for="(step, index) in steps"
                  :key="index"
                  @click="goToStep(index)"
                  :aria-label="`Go to step ${index + 1}`"
                  class="transition-all"
                  :class="[
                    index === currentStep
                      ? 'w-8 h-2 bg-blue-600'
                      : index < currentStep
                        ? 'w-2 h-2 bg-green-500'
                        : 'w-2 h-2 bg-gray-300',
                    'rounded-full'
                  ]"
                ></button>
              </div>

              <!-- Navigation buttons -->
              <div class="flex items-center justify-between gap-3">
                <button
                  v-if="currentStep > 0"
                  @click="previous"
                  class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Back
                </button>
                <div v-else></div>

                <div class="flex items-center gap-2">
                  <button
                    @click="skip"
                    class="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    {{ isLastStep ? 'Close' : 'Skip Tutorial' }}
                  </button>

                  <button
                    @click="next"
                    class="px-6 py-2 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:shadow-lg hover:scale-105 transition-all"
                  >
                    {{ isLastStep ? 'Finish' : 'Next' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  steps: {
    type: Array,
    required: true,
    validator: (steps) => {
      return steps.every(step =>
        step.target &&
        step.title &&
        step.description
      )
    }
  },
  modelValue: {
    type: Boolean,
    default: false
  },
  autoStart: {
    type: Boolean,
    default: false
  },
  allowSkip: {
    type: Boolean,
    default: true
  },
  storageKey: {
    type: String,
    default: 'tutorial_completed'
  }
})

const emit = defineEmits(['update:modelValue', 'complete', 'skip', 'step-change'])

const currentStep = ref(0)
const isActive = ref(props.modelValue)
const spotlightStyle = ref(null)
const cardStyle = ref(null)
const targetElement = ref(null)

// Computed
const currentStepData = computed(() => props.steps[currentStep.value])
const isLastStep = computed(() => currentStep.value === props.steps.length - 1)

// Watch for prop changes
watch(() => props.modelValue, (newVal) => {
  if (newVal && !isActive.value) {
    start()
  } else if (!newVal && isActive.value) {
    close()
  }
})

// Methods
function start() {
  const completed = localStorage.getItem(props.storageKey)
  if (completed === 'true' && !props.modelValue) {
    return
  }

  isActive.value = true
  currentStep.value = 0
  emit('update:modelValue', true)
  nextTick(() => {
    updatePositions()
  })
}

function close() {
  isActive.value = false
  emit('update:modelValue', false)
  spotlightStyle.value = null
  cardStyle.value = null
}

function next() {
  if (isLastStep.value) {
    complete()
  } else {
    currentStep.value++
    emit('step-change', currentStep.value, currentStepData.value)
    nextTick(() => {
      updatePositions()
    })
  }
}

function previous() {
  if (currentStep.value > 0) {
    currentStep.value--
    emit('step-change', currentStep.value, currentStepData.value)
    nextTick(() => {
      updatePositions()
    })
  }
}

function goToStep(index) {
  if (index >= 0 && index < props.steps.length) {
    currentStep.value = index
    emit('step-change', currentStep.value, currentStepData.value)
    nextTick(() => {
      updatePositions()
    })
  }
}

function complete() {
  localStorage.setItem(props.storageKey, 'true')
  emit('complete')
  close()
}

function skip() {
  if (props.allowSkip) {
    emit('skip')
    close()
  }
}

function handleOverlayClick() {
  if (props.allowSkip) {
    skip()
  }
}

function updatePositions() {
  if (!isActive.value || !currentStepData.value) return

  // Find target element
  const selector = currentStepData.value.target
  targetElement.value = document.querySelector(selector)

  if (!targetElement.value) {
    console.warn(`Tutorial target not found: ${selector}`)
    // Position card in center if target not found
    cardStyle.value = {
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)'
    }
    spotlightStyle.value = null
    return
  }

  // Get target element position
  const rect = targetElement.value.getBoundingClientRect()
  const padding = 16

  // Set spotlight style
  spotlightStyle.value = {
    top: `${rect.top - padding}px`,
    left: `${rect.left - padding}px`,
    width: `${rect.width + padding * 2}px`,
    height: `${rect.height + padding * 2}px`
  }

  // Position card
  const cardWidth = 400
  const cardMargin = 24
  const preferredPosition = currentStepData.value.position || 'bottom'

  let top, left

  switch (preferredPosition) {
    case 'top':
      top = rect.top - cardMargin - 200 // Approximate card height
      left = rect.left + rect.width / 2 - cardWidth / 2
      break
    case 'bottom':
      top = rect.bottom + cardMargin
      left = rect.left + rect.width / 2 - cardWidth / 2
      break
    case 'left':
      top = rect.top + rect.height / 2 - 150 // Approximate half card height
      left = rect.left - cardWidth - cardMargin
      break
    case 'right':
      top = rect.top + rect.height / 2 - 150
      left = rect.right + cardMargin
      break
    default:
      top = rect.bottom + cardMargin
      left = rect.left + rect.width / 2 - cardWidth / 2
  }

  // Keep card within viewport
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  if (left < 20) left = 20
  if (left + cardWidth > viewportWidth - 20) left = viewportWidth - cardWidth - 20
  if (top < 20) top = 20
  if (top > viewportHeight - 300) top = viewportHeight - 300

  cardStyle.value = {
    top: `${top}px`,
    left: `${left}px`
  }

  // Scroll target into view
  targetElement.value.scrollIntoView({
    behavior: 'smooth',
    block: 'center'
  })
}

// Handle window resize
function handleResize() {
  if (isActive.value) {
    updatePositions()
  }
}

onMounted(() => {
  if (props.autoStart) {
    start()
  }
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

// Expose methods for parent component
defineExpose({
  start,
  next,
  previous,
  goToStep,
  complete,
  skip
})
</script>
