<template>
  <div class="w-full">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-semibold text-gray-700 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-600">*</span>
    </label>

    <!-- Input Group -->
    <div class="relative" :class="{ 'input-group': $slots.prepend || $slots.append }">
      <!-- Prepend slot -->
      <div
        v-if="$slots.prepend"
        class="absolute left-0 inset-y-0 flex items-center pl-3 pointer-events-none"
      >
        <slot name="prepend"></slot>
      </div>

      <!-- Input -->
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Append slot (e.g., show/hide password button) -->
      <div
        v-if="$slots.append"
        class="absolute right-0 inset-y-0 flex items-center pr-3"
      >
        <slot name="append"></slot>
      </div>
    </div>

    <!-- Helper text or error message -->
    <p
      v-if="helperText || errorMessage"
      class="mt-2 text-sm"
      :class="errorMessage ? 'text-red-600' : 'text-gray-500'"
    >
      {{ errorMessage || helperText }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'password', 'email', 'number', 'tel', 'url', 'search'].includes(value)
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
  autocomplete: {
    type: String,
    default: 'off'
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus'])

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => {
  const classes = [
    'block w-full rounded-lg border transition-colors',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-500'
  ]

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-3 text-lg'
  }
  classes.push(sizeClasses[props.size])

  // Prepend/append padding adjustments
  if (props.$slots?.prepend) {
    classes.push('pl-10')
  }
  if (props.$slots?.append) {
    classes.push('pr-10')
  }

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
