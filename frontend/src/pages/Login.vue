<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-8 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
    <div class="w-full max-w-md">
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-6 text-center">
          <h3 class="text-white text-2xl font-bold mb-0">Welcome Back</h3>
          <p class="text-white/90 text-sm mt-2">Sign in to connect your apps</p>
        </div>
        <div class="px-8 py-6">
          <form @submit.prevent="submit">
            <div class="mb-4">
              <label class="block text-sm font-semibold text-gray-700 mb-2">Email or Username</label>
              <input
                name="email"
                type="text"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all outline-none"
                placeholder="john@example.com or Administrator"
                required
              />
              <p class="text-xs text-gray-600 mt-1">You can log in with your email address or username</p>
            </div>
            <div class="mb-4">
              <label class="block text-sm font-semibold text-gray-700 mb-2">Password</label>
              <input
                name="password"
                type="password"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all outline-none"
                placeholder="••••••••"
                required
              />
            </div>

            <BaseAlert v-if="error" variant="danger" class="mb-4">
              {{ error }}
            </BaseAlert>

            <button
              type="submit"
              class="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="session.login.loading"
            >
              <span v-if="session.login.loading" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
              {{ session.login.loading ? 'Signing In...' : 'Sign In' }}
            </button>

            <div class="mt-6 text-center space-y-3">
              <p class="text-sm text-gray-600">
                Don't have an account?
                <router-link to="/account/signup" class="text-blue-600 font-semibold hover:text-blue-700 transition-colors">
                  Create Account
                </router-link>
              </p>
              <p class="text-xs text-gray-600">
                <a href="/desk" class="text-gray-600 hover:text-gray-800 transition-colors">
                  Administrator? Access Frappe Desk →
                </a>
              </p>
              <router-link to="/" class="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-gray-800 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
/* All styling handled by Tailwind CSS */
</style>
