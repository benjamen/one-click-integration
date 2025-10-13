<template>
  <div class="auth-page">
    <div class="container">
      <div class="flex justify-center">
        <div class="col-lg-5 col-md-7">
          <div class="card shadow-lg border-0 mt-5">
            <div class="card-header bg-gradient-primary p-4 text-center">
              <div class="mb-3">
                <svg class="verification-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 class="text-white font-bold mb-0">Check Your Email</h3>
            </div>
            <div class="card-body p-4 text-center">
              <div class="mb-4">
                <p class="text-gray-600 mb-3">
                  We've sent a verification link to:
                </p>
                <p class="font-bold text-dark mb-3">
                  {{ email }}
                </p>
                <p class="text-gray-600 text-sm">
                  Click the link in the email to verify your account and complete your registration.
                </p>
              </div>

              <div class="alert alert-info mb-4">
                <svg class="info-icon" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <small>Didn't receive the email? Check your spam folder or wait a few minutes.</small>
              </div>

              <div class="d-grid gap-2">
                <button
                  @click="resendEmail"
                  class="btn btn-outline-primary"
                  :disabled="resending || countdown > 0"
                >
                  <span v-if="resending" class="spinner-border spinner-border-sm mr-2"></span>
                  {{ resending ? 'Sending...' : countdown > 0 ? `Resend in ${countdown}s` : 'Resend Email' }}
                </button>

                <router-link
                  to="/account/login"
                  class="btn btn-primary no-underline"
                >
                  Continue to Login
                </router-link>

                <router-link
                  to="/"
                  class="btn btn-link text-gray-600 no-underline"
                >
                  <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  Back to Home
                </router-link>
              </div>

              <div v-if="resendSuccess" class="alert alert-success mt-3">
                ✓ Verification email sent successfully!
              </div>

              <div v-if="resendError" class="alert alert-danger mt-3">
                {{ resendError }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { createResource } from 'frappe-ui'

const route = useRoute()
const email = ref(route.query.email || 'your email')
const resending = ref(false)
const resendSuccess = ref(false)
const resendError = ref('')
const countdown = ref(0)
let countdownInterval = null

const resendResource = createResource({
  url: 'frappe.core.doctype.user.user.sign_up',
  makeParams() {
    return {
      email: email.value,
      resend: 1
    }
  },
  onSuccess() {
    resending.value = false
    resendSuccess.value = true
    resendError.value = ''
    countdown.value = 60
    startCountdown()
    setTimeout(() => {
      resendSuccess.value = false
    }, 5000)
  },
  onError(err) {
    resending.value = false
    resendError.value = err.messages ? err.messages.join(', ') : 'Failed to resend email'
    setTimeout(() => {
      resendError.value = ''
    }, 5000)
  }
})

function resendEmail() {
  if (countdown.value > 0) return
  resending.value = true
  resendSuccess.value = false
  resendError.value = ''
  resendResource.submit()
}

function startCountdown() {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  countdownInterval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownInterval)
    }
  }, 1000)
}

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(310deg, #141727 0%, #3A416F 100%);
  display: flex;
  align-items: center;
  padding: 2rem 0;
}

.bg-gradient-primary {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
}

.card {
  border-radius: 1rem;
}

.card-header {
  border-radius: 1rem 1rem 0 0 !important;
}

.verification-icon {
  width: 64px;
  height: 64px;
  color: white;
  margin: 0 auto;
}

.info-icon {
  width: 18px;
  height: 18px;
  display: inline-block;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.back-icon {
  width: 18px;
  height: 18px;
  display: inline-block;
  margin-right: 0.5rem;
  vertical-align: middle;
}

.btn-primary {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(121, 40, 202, 0.4);
  color: white;
}

.btn-outline-primary {
  border: 2px solid #7928CA;
  color: #7928CA;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  background: transparent;
}

.btn-outline-primary:hover {
  background: #7928CA;
  color: white;
}

.btn-outline-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-link {
  text-decoration: none;
}

.no-underline {
  text-decoration: none !important;
}

</style>
