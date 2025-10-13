<template>
  <div class="auth-page">
    <div class="container">
      <div class="flex justify-center">
        <div class="col-lg-5 col-md-7">
          <div class="card shadow-lg border-0 mt-5">
            <div class="card-header bg-gradient-primary p-4 text-center">
              <h3 class="text-white font-bold mb-0">Welcome Back</h3>
              <p class="text-white opacity-8 mb-0 mt-2">Sign in to connect your apps</p>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="submit">
                <div class="mb-3">
                  <label class="form-label font-bold">Email or Username</label>
                  <input
                    name="email"
                    type="text"
                    class="form-control"
                    placeholder="john@example.com or Administrator"
                    required
                  />
                  <small class="text-gray-600">You can log in with your email address or username</small>
                </div>
                <div class="mb-3">
                  <label class="form-label font-bold">Password</label>
                  <input
                    name="password"
                    type="password"
                    class="form-control"
                    placeholder="••••••••"
                    required
                  />
                </div>

                <BaseAlert v-if="error" variant="danger" class="mb-3">
                  {{ error }}
                </BaseAlert>

                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-3"
                  :disabled="session.login.loading"
                >
                  <span v-if="session.login.loading" class="spinner-border spinner-border-sm mr-2"></span>
                  {{ session.login.loading ? 'Signing In...' : 'Sign In' }}
                </button>

                <div class="text-center">
                  <p class="text-gray-600 mb-2">
                    Don't have an account?
                    <router-link to="/account/signup" class="text-primary-600 font-bold">
                      Create Account
                    </router-link>
                  </p>
                  <p class="text-gray-600 mb-2">
                    <a href="/desk" class="text-gray-600 text-decoration-none">
                      <small>Administrator? Access Frappe Desk →</small>
                    </a>
                  </p>
                  <router-link to="/" class="text-gray-600 text-sm no-underline">
                    <svg class="back-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                    Back to Home
                  </router-link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { session } from "../data/session"

const error = ref("")

async function submit(e) {
	error.value = ""
	const formData = new FormData(e.target)

	// Submit login
	await session.login.submit({
		email: formData.get("email"),
		password: formData.get("password"),
	})

	// frappe-ui's createResource stores errors in resource.error
	// Check if there was an error after submission
	if (session.login.error) {
		error.value = "Invalid username/email or password"
	}
}
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

.form-control {
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  border: 1px solid #d2d6da;
}

.form-control:focus {
  border-color: #7928CA;
  box-shadow: 0 0 0 0.2rem rgba(121, 40, 202, 0.25);
}

.btn-primary {
  background: linear-gradient(310deg, #7928CA 0%, #FF0080 100%);
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(121, 40, 202, 0.4);
}

.back-icon {
  width: 16px;
  height: 16px;
  display: inline-block;
  margin-right: 0.25rem;
  vertical-align: middle;
}

.no-underline {
  text-decoration: none !important;
}

.no-underline:hover {
  text-decoration: underline !important;
}
</style>
