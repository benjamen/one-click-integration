<template>
  <teleport to="body">
    <transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @click.self="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          :class="backdropClass"
        ></div>

        <!-- Modal -->
        <transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition-all duration-200"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="modelValue"
            class="relative bg-white rounded-2xl shadow-2xl max-h-[90vh] flex flex-col"
            :class="[sizeClasses, modalClass]"
            role="dialog"
            :aria-labelledby="titleId"
            aria-modal="true"
          >
            <!-- Header -->
            <div
              v-if="!hideHeader"
              class="flex items-center justify-between px-6 py-4 border-b border-gray-200"
              :class="headerClass"
            >
              <div class="flex-1">
                <slot name="header">
                  <h3 :id="titleId" class="text-xl font-bold text-gray-900">
                    {{ title }}
                  </h3>
                  <p v-if="subtitle" class="text-sm text-gray-500 mt-1">
                    {{ subtitle }}
                  </p>
                </slot>
              </div>
              <button
                v-if="!hideClose"
                type="button"
                class="inline-flex items-center justify-center w-8 h-8 ml-4 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-100"
                @click="close"
                aria-label="Close modal"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- Body -->
            <div
              class="flex-1 overflow-y-auto px-6 py-4"
              :class="bodyClass"
            >
              <slot></slot>
            </div>

            <!-- Footer -->
            <div
              v-if="!hideFooter || $slots.footer"
              class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200"
              :class="footerClass"
            >
              <slot name="footer">
                <BaseButton
                  v-if="!hideCancelButton"
                  variant="secondary"
                  @click="close"
                >
                  {{ cancelText }}
                </BaseButton>
                <BaseButton
                  v-if="!hideConfirmButton"
                  :variant="confirmVariant"
                  @click="confirm"
                  :loading="loading"
                  :disabled="confirmDisabled"
                >
                  {{ confirmText }}
                </BaseButton>
              </slot>
            </div>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed, watch, onMounted, onUnmounted } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl', 'full'].includes(value)
  },
  hideHeader: {
    type: Boolean,
    default: false
  },
  hideFooter: {
    type: Boolean,
    default: false
  },
  hideClose: {
    type: Boolean,
    default: false
  },
  hideCancelButton: {
    type: Boolean,
    default: false
  },
  hideConfirmButton: {
    type: Boolean,
    default: false
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  confirmVariant: {
    type: String,
    default: 'primary'
  },
  confirmDisabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  closeOnEscape: {
    type: Boolean,
    default: true
  },
  scrollable: {
    type: Boolean,
    default: true
  },
  modalClass: {
    type: String,
    default: ''
  },
  headerClass: {
    type: String,
    default: ''
  },
  bodyClass: {
    type: String,
    default: ''
  },
  footerClass: {
    type: String,
    default: ''
  },
  backdropClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'confirm'])

const titleId = computed(() => `modal-title-${Math.random().toString(36).substr(2, 9)}`)

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'w-full max-w-md',
    md: 'w-full max-w-lg',
    lg: 'w-full max-w-2xl',
    xl: 'w-full max-w-4xl',
    '2xl': 'w-full max-w-6xl',
    full: 'w-[95vw] h-[95vh]'
  }
  return sizes[props.size]
})

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function confirm() {
  emit('confirm')
}

function handleBackdropClick() {
  if (props.closeOnBackdrop) {
    close()
  }
}

function handleEscape(event) {
  if (event.key === 'Escape' && props.closeOnEscape && props.modelValue) {
    close()
  }
}

// Handle body scroll lock
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// Keyboard events
onMounted(() => {
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* Ensure modal scrolls properly */
.overflow-y-auto {
  overscroll-behavior: contain;
}
</style>
