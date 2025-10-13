<template>
  <div class="w-full">
    <!-- Label -->
    <label
      v-if="label"
      :for="textareaId"
      class="block text-sm font-semibold text-gray-700 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-600">*</span>
    </label>

    <!-- Textarea -->
    <textarea
      :id="textareaId"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :required="required"
      :rows="rows"
      :maxlength="maxlength"
      :class="textareaClasses"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    ></textarea>

    <!-- Character count and helper text -->
    <div v-if="helperText || errorMessage || (showCharCount && maxlength)" class="mt-2 flex items-center justify-between">
      <p
        class="text-sm"
        :class="errorMessage ? 'text-red-600' : 'text-gray-500'"
      >
        {{ errorMessage || helperText }}
      </p>
      <p
        v-if="showCharCount && maxlength"
        class="text-sm text-gray-500"
      >
        {{ modelValue?.length || 0 }} / {{ maxlength }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  errorMessage: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  rows: {
    type: Number,
    default: 4
  },
  maxlength: {
    type: Number,
    default: null
  },
  showCharCount: {
    type: Boolean,
    default: false
  },
  resize: {
    type: String,
    default: 'vertical',
    validator: (value) => ['none', 'vertical', 'horizontal', 'both'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const textareaId = computed(() => `textarea-${Math.random().toString(36).substr(2, 9)}`)

const textareaClasses = computed(() => {
  const classes = [
    'block w-full px-4 py-2 rounded-lg border text-base transition-colors',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-500'
  ]

  // Resize classes
  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize'
  }
  classes.push(resizeClasses[props.resize])

  // Error or normal state
  if (props.errorMessage) {
    classes.push('border-red-300 focus:border-red-500 focus:ring-red-500')
  } else {
    classes.push('border-gray-300 focus:border-blue-500 focus:ring-blue-500')
  }

  return classes.join(' ')
})

function handleInput(event) {
  emit('update:modelValue', event.target.value)
}

function handleBlur(event) {
  emit('blur', event)
}

function handleFocus(event) {
  emit('focus', event)
}
</script>
