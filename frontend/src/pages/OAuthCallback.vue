<template>
  <div class="oauth-callback-page flex items-center justify-center min-vh-100 bg-gradient-dark">
    <div class="container">
      <div class="flex justify-center">
        <div class="col-md-6">
          <div class="card shadow-lg">
            <div class="card-body p-5 text-center">
              <!-- Loading State -->
              <div v-if="loading">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                  <span class="visually-hidden">Processing...</span>
                </div>
                <h4 class="font-bold mb-2">Connecting your account</h4>
                <p class="text-gray-600">Please wait while we complete the authentication...</p>
              </div>

              <!-- Success State -->
              <div v-else-if="success">
                <div class="icon icon-shape bg-gradient-success shadow-success mx-auto mb-4" style="width: 80px; height: 80px;">
                  <i class="fas fa-check text-white" style="font-size: 2rem;"></i>
                </div>
                <h4 class="font-bold mb-2">Successfully Connected!</h4>
                <p class="text-gray-600 mb-4">Your account has been linked successfully.</p>
                <p class="text-sm text-gray-600">This window will close automatically...</p>
              </div>

              <!-- Error State -->
              <div v-else-if="error">
                <div class="icon icon-shape bg-gradient-danger shadow-danger mx-auto mb-4" style="width: 80px; height: 80px;">
                  <i class="fas fa-times text-white" style="font-size: 2rem;"></i>
                </div>
                <h4 class="font-bold mb-2">Connection Failed</h4>
                <p class="text-gray-600 mb-4">{{ error }}</p>
                <button @click="closeWindow" class="btn btn-primary">
                  Close Window
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { createResource } from "frappe-ui"
import { useRoute } from "vue-router"

const route = useRoute()
const loading = ref(true)
const success = ref(false)
const error = ref(null)

// OAuth callback resource
const oauthCallback = createResource({
  url: "lodgeick.api.oauth.oauth_callback",
  makeParams(values) {
    return {
      code: values.code,
      state: values.state,
      provider: values.provider
    }
  },
  onSuccess(data) {
    loading.value = false
    success.value = true
    // Close window after 2 seconds
    setTimeout(() => {
      window.close()
    }, 2000)
  },
  onError(err) {
    loading.value = false
    error.value = err.message || "Failed to complete OAuth flow"
  }
})

onMounted(() => {
  const code = route.query.code
  const state = route.query.state
  const provider = route.query.provider

  if (!code || !state || !provider) {
    loading.value = false
    error.value = "Missing OAuth parameters"
    return
  }

  oauthCallback.submit({
    code,
    state,
    provider
  })
})

function closeWindow() {
  window.close()
}
</script>

<style scoped>
.oauth-callback-page {
  background: linear-gradient(310deg, #141727 0%, #3A416F 100%);
}

.bg-gradient-success {
  background: linear-gradient(310deg, #17AD37 0%, #98EC2D 100%);
}

.bg-gradient-danger {
  background: linear-gradient(310deg, #EA0606 0%, #FF667C 100%);
}

.shadow-success {
  box-shadow: 0 4px 20px 0 rgba(23, 173, 55, 0.4) !important;
}

.shadow-danger {
  box-shadow: 0 4px 20px 0 rgba(234, 6, 6, 0.4) !important;
}

.icon-shape {
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

</style>
