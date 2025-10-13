<template>
  <span :class="badgeClasses">
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
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
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  pill: {
    type: Boolean,
    default: false
  }
})

const badgeClasses = computed(() => {
  const classes = ['inline-flex', 'items-center', 'justify-center', 'font-semibold']

  // Size classes
  const sizeMap = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-sm',
    lg: 'px-3 py-1 text-base'
  }
  classes.push(sizeMap[props.size])

  // Variant colors
  const variantMap = {
    primary: 'bg-primary-100 text-primary-800 ring-1 ring-inset ring-primary-600/20',
    secondary: 'bg-gray-100 text-gray-800 ring-1 ring-inset ring-gray-600/20',
    success: 'bg-green-100 text-green-800 ring-1 ring-inset ring-green-600/20',
    danger: 'bg-red-100 text-red-800 ring-1 ring-inset ring-red-600/20',
    warning: 'bg-yellow-100 text-yellow-800 ring-1 ring-inset ring-yellow-600/20',
    info: 'bg-blue-100 text-blue-800 ring-1 ring-inset ring-blue-600/20',
    light: 'bg-gray-50 text-gray-600 ring-1 ring-inset ring-gray-500/10',
    dark: 'bg-gray-800 text-gray-100 ring-1 ring-inset ring-gray-700/10'
  }
  classes.push(variantMap[props.variant])

  // Shape
  if (props.pill) {
    classes.push('rounded-full')
  } else {
    classes.push('rounded-md')
  }

  return classes.join(' ')
})
</script>
