<template>
  <div class="relative inline-block">
    <!-- Trigger Button -->
    <button
      @click="toggle"
      @mouseenter="showOnHover && show()"
      @mouseleave="showOnHover && hide()"
      :aria-label="ariaLabel || 'Help'"
      :aria-expanded="isVisible"
      class="inline-flex items-center justify-center transition-all"
      :class="buttonClass"
      type="button"
    >
      <slot name="trigger">
        <svg
          class="w-4 h-4"
          :class="iconClass"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
            clip-rule="evenodd"
          />
        </svg>
      </slot>
    </button>

    <!-- Tooltip Popup -->
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 scale-95 translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 translate-y-1"
    >
      <div
        v-if="isVisible"
        ref="tooltipRef"
        class="absolute z-50 mt-2 rounded-lg shadow-lg"
        :class="[
          positionClasses,
          widthClass,
          'bg-gray-900 text-white'
        ]"
        role="tooltip"
      >
        <!-- Arrow -->
        <div
          class="absolute w-3 h-3 bg-gray-900 transform rotate-45"
          :class="arrowClasses"
        ></div>

        <!-- Content -->
        <div class="relative p-4">
          <!-- Title (optional) -->
          <div v-if="title || $slots.title" class="mb-2">
            <h4 class="text-sm font-semibold text-white">
              <slot name="title">{{ title }}</slot>
            </h4>
          </div>

          <!-- Body -->
          <div class="text-sm text-gray-200">
            <slot>{{ content }}</slot>
          </div>

          <!-- Actions (optional) -->
          <div v-if="$slots.actions" class="mt-3 flex items-center gap-2">
            <slot name="actions"></slot>
          </div>

          <!-- Close button for click-triggered tooltips -->
          <button
            v-if="!showOnHover && showCloseButton"
            @click="hide"
            class="absolute top-2 right-2 text-gray-400 hover:text-white transition-colors"
            aria-label="Close tooltip"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  position: {
    type: String,
    default: 'bottom',
    validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
  },
  width: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  showOnHover: {
    type: Boolean,
    default: true
  },
  showCloseButton: {
    type: Boolean,
    default: true
  },
  buttonClass: {
    type: String,
    default: 'text-gray-400 hover:text-gray-600'
  },
  iconClass: {
    type: String,
    default: ''
  },
  ariaLabel: {
    type: String,
    default: ''
  }
})

const isVisible = ref(false)
const tooltipRef = ref(null)
let hideTimeout = null

// Computed classes
const widthClass = computed(() => {
  const widths = {
    sm: 'w-48',
    md: 'w-64',
    lg: 'w-80',
    xl: 'w-96'
  }
  return widths[props.width] || widths.md
})

const positionClasses = computed(() => {
  const positions = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  }
  return positions[props.position] || positions.bottom
})

const arrowClasses = computed(() => {
  const arrows = {
    top: 'top-full left-1/2 transform -translate-x-1/2 -mt-1',
    bottom: 'bottom-full left-1/2 transform -translate-x-1/2 -mb-1',
    left: 'left-full top-1/2 transform -translate-y-1/2 -ml-1',
    right: 'right-full top-1/2 transform -translate-y-1/2 -mr-1'
  }
  return arrows[props.position] || arrows.bottom
})

// Methods
function show() {
  if (hideTimeout) {
    clearTimeout(hideTimeout)
    hideTimeout = null
  }
  isVisible.value = true
}

function hide() {
  if (props.showOnHover) {
    // Add a small delay for hover tooltips to allow mouse movement
    hideTimeout = setTimeout(() => {
      isVisible.value = false
    }, 100)
  } else {
    isVisible.value = false
  }
}

function toggle() {
  if (!props.showOnHover) {
    isVisible.value = !isVisible.value
  }
}

// Click outside to close
function handleClickOutside(event) {
  if (tooltipRef.value && !tooltipRef.value.contains(event.target) && !props.showOnHover) {
    hide()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  if (hideTimeout) {
    clearTimeout(hideTimeout)
  }
})
</script>
