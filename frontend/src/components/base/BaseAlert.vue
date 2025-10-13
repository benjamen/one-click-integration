<template>
  <div
    v-if="modelValue"
    :class="alertClasses"
    role="alert"
  >
    <div class="flex items-start">
      <!-- Icon -->
      <div v-if="!hideIcon" class="flex-shrink-0">
        <i :class="iconClass"></i>
      </div>

      <!-- Content -->
      <div class="flex-1" :class="{ 'ml-3': !hideIcon }">
        <slot />
      </div>

      <!-- Dismiss Button -->
      <div v-if="dismissible" class="flex-shrink-0 ml-3">
        <button
          type="button"
          @click="dismiss"
          class="inline-flex rounded-md p-1.5 hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-offset-2"
          :class="dismissButtonClass"
        >
          <span class="sr-only">Dismiss</span>
          <i class="fas fa-times text-sm"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: true
  },
  variant: {
    type: String,
    default: 'info',
    validator: (value) => [
      'primary',
      'secondary',
      'success',
      'danger',
      'warning',
      'info',
      'light',
      'dark'
    ].includes(value)
  },
  dismissible: {
    type: Boolean,
    default: false
  },
  hideIcon: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'dismiss'])

const alertClasses = computed(() => {
  const classes = ['rounded-lg', 'p-4', 'border']

  // Variant colors
  const variantMap = {
    primary: 'bg-blue-50 border-blue-200 text-blue-800',
    secondary: 'bg-gray-50 border-gray-200 text-gray-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    danger: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    light: 'bg-gray-50 border-gray-100 text-gray-600',
    dark: 'bg-gray-800 border-gray-700 text-gray-100'
  }
  classes.push(variantMap[props.variant])

  return classes.join(' ')
})

const iconClass = computed(() => {
  const iconMap = {
    primary: 'fas fa-info-circle text-blue-500',
    secondary: 'fas fa-info-circle text-gray-500',
    success: 'fas fa-check-circle text-green-500',
    danger: 'fas fa-exclamation-circle text-red-500',
    warning: 'fas fa-exclamation-triangle text-yellow-500',
    info: 'fas fa-info-circle text-blue-500',
    light: 'fas fa-info-circle text-gray-400',
    dark: 'fas fa-info-circle text-gray-300'
  }
  return iconMap[props.variant]
})

const dismissButtonClass = computed(() => {
  const colorMap = {
    primary: 'text-blue-600 focus:ring-blue-600',
    secondary: 'text-gray-600 focus:ring-gray-600',
    success: 'text-green-600 focus:ring-green-600',
    danger: 'text-red-600 focus:ring-red-600',
    warning: 'text-yellow-600 focus:ring-yellow-600',
    info: 'text-blue-600 focus:ring-blue-600',
    light: 'text-gray-500 focus:ring-gray-500',
    dark: 'text-gray-300 focus:ring-gray-300'
  }
  return colorMap[props.variant]
})

function dismiss() {
  emit('update:modelValue', false)
  emit('dismiss')
}
</script>
