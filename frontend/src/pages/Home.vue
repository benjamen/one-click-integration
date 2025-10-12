<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200 shadow-sm">
      <div class="max-w-7xl mx-auto px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-3 group no-underline">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <span class="text-white font-bold text-xl">L</span>
            </div>
            <span class="text-2xl font-bold text-gray-900">Lodgeick</span>
          </router-link>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">Features</a>
            <a href="#integrations" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">Integrations</a>
            <a href="#how-it-works" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">How It Works</a>
            <router-link to="/pricing" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">Pricing</router-link>

            <div v-if="session.isLoggedIn" class="flex items-center gap-4">
              <router-link
                to="/account/profile"
                class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline"
              >
                {{ session.user }}
              </router-link>
              <button
                @click="session.logout.submit()"
                class="text-gray-700 hover:text-red-600 font-medium transition-colors"
              >
                Logout
              </button>
            </div>

            <div v-else class="flex items-center gap-4">
              <router-link
                to="/account/login"
                class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline"
              >
                Log In
              </router-link>
              <router-link
                to="/account/signup"
                class="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 no-underline"
              >
                Get Started
              </router-link>
            </div>
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
            :aria-label="mobileMenuOpen ? 'Close menu' : 'Open menu'"
            aria-expanded="mobileMenuOpen"
          >
            <svg v-if="!mobileMenuOpen" class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
            <svg v-else class="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <transition
        enter-active-class="transition-all duration-200"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 bg-white">
          <div class="px-6 py-4 space-y-3">
            <a href="#features" @click="mobileMenuOpen = false" class="block text-gray-700 hover:text-blue-600 font-medium py-2 no-underline">Features</a>
            <a href="#integrations" @click="mobileMenuOpen = false" class="block text-gray-700 hover:text-blue-600 font-medium py-2 no-underline">Integrations</a>
            <a href="#how-it-works" @click="mobileMenuOpen = false" class="block text-gray-700 hover:text-blue-600 font-medium py-2 no-underline">How It Works</a>
            <router-link to="/pricing" @click="mobileMenuOpen = false" class="block text-gray-700 hover:text-blue-600 font-medium py-2 no-underline">Pricing</router-link>

            <div v-if="session.isLoggedIn" class="space-y-3 pt-3 border-t border-gray-200">
              <router-link
                to="/account/profile"
                class="block text-gray-700 hover:text-blue-600 font-medium py-2 no-underline"
              >
                {{ session.user }}
              </router-link>
              <button
                @click="session.logout.submit()"
                class="w-full text-left text-gray-700 hover:text-red-600 font-medium py-2"
              >
                Logout
              </button>
            </div>

            <div v-else class="space-y-3 pt-3 border-t border-gray-200">
              <router-link
                to="/account/login"
                class="block text-gray-700 hover:text-blue-600 font-medium py-2 no-underline"
              >
                Log In
              </router-link>
              <router-link
                to="/account/signup"
                class="block w-full text-center px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg no-underline"
              >
                Get Started
              </router-link>
            </div>
          </div>
        </div>
      </transition>
    </nav>

    <!-- Main Content -->
    <main>
      <HeroSection />

      <div id="features">
        <FeatureGrid />
      </div>

      <div id="how-it-works">
        <StepsSection />
      </div>

      <div id="integrations">
        <IntegrationsGrid />
      </div>

      <CallToAction />
    </main>

    <!-- Footer -->
    <AppFooter />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { session } from '../data/session'
import { useOnboardingStore } from '@/stores/onboarding'
import HeroSection from '../components/HeroSection.vue'
import FeatureGrid from '../components/FeatureGrid.vue'
import StepsSection from '../components/StepsSection.vue'
import IntegrationsGrid from '../components/IntegrationsGrid.vue'
import CallToAction from '../components/CallToAction.vue'
import AppFooter from '../components/AppFooter.vue'

const router = useRouter()
const onboardingStore = useOnboardingStore()

const mobileMenuOpen = ref(false)
const isLoggedIn = computed(() => session.isLoggedIn)

// Redirect logged-in users to dashboard or onboarding
onMounted(() => {
  if (isLoggedIn.value) {
    if (onboardingStore.isCompleted || onboardingStore.connectedApps.length > 0) {
      router.push('/dashboard')
    } else {
      router.push('/connect')
    }
  }
})
</script>
