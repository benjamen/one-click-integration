<template>
  <div class="min-h-screen bg-gray-50">
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
            <router-link to="/" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">Home</router-link>
            <router-link to="/pricing" class="text-blue-600 font-medium no-underline">Pricing</router-link>
            <router-link to="/api" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">API</router-link>

            <router-link
              to="/auth"
              class="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg hover:shadow-lg hover:scale-105 transition-all duration-200 no-underline"
            >
              Get Started
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <div class="container mx-auto px-4 py-16 pt-24">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-4">
          Simple, Transparent Pricing
        </h1>
        <p class="text-xl text-gray-600 max-w-2xl mx-auto">
          Choose the plan that fits your business needs. No hidden fees, no surprises.
        </p>
      </div>

      <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
        <!-- Free Plan -->
        <div class="bg-white rounded-2xl shadow-lg p-8 border-2 border-gray-200 hover:border-blue-500 transition-all">
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Free</h3>
          <div class="mb-6">
            <span class="text-4xl font-bold text-gray-900">$0</span>
            <span class="text-gray-600">/month</span>
          </div>
          <ul class="space-y-3 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">Up to 3 integrations</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">1,000 workflow executions/month</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">Quick Start + Manual OAuth</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">Community support</span>
            </li>
          </ul>
          <router-link
            to="/account/signup"
            class="block w-full text-center py-3 px-6 rounded-lg bg-gray-100 text-gray-900 font-semibold hover:bg-gray-200 transition-colors no-underline"
          >
            Get Started
          </router-link>
        </div>

        <!-- Pro Plan (Featured) -->
        <div class="bg-blue-600 rounded-2xl shadow-xl p-8 border-2 border-blue-600 transform scale-105">
          <div class="text-center mb-2">
            <span class="inline-block px-3 py-1 bg-white bg-opacity-20 rounded-full text-white text-sm font-semibold">
              Most Popular
            </span>
          </div>
          <h3 class="text-2xl font-bold text-white mb-2">Pro</h3>
          <div class="mb-6">
            <span class="text-4xl font-bold text-white">$29</span>
            <span class="text-blue-100">/month</span>
          </div>
          <ul class="space-y-3 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-white mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-blue-50">Up to 10 integrations</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-white mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-blue-50">10,000 workflow executions/month</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-white mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-blue-50">AI-powered OAuth setup</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-white mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-blue-50">Premium integrations</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-white mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-blue-50">Priority support</span>
            </li>
          </ul>
          <router-link
            to="/account/signup"
            class="block w-full text-center py-3 px-6 rounded-lg bg-white text-blue-600 font-semibold hover:bg-gray-100 transition-colors no-underline"
          >
            Get Started
          </router-link>
        </div>

        <!-- Enterprise Plan -->
        <div class="bg-white rounded-2xl shadow-lg p-8 border-2 border-gray-200 hover:border-blue-500 transition-all">
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Enterprise</h3>
          <div class="mb-6">
            <span class="text-4xl font-bold text-gray-900">Custom</span>
          </div>
          <ul class="space-y-3 mb-8">
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">Unlimited everything</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">Dedicated support</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">SLA guarantee</span>
            </li>
            <li class="flex items-start">
              <svg class="w-5 h-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
              </svg>
              <span class="text-gray-600">Custom integrations</span>
            </li>
          </ul>
          <a
            href="mailto:sales@lodgeick.com"
            class="block w-full text-center py-3 px-6 rounded-lg bg-gray-100 text-gray-900 font-semibold hover:bg-gray-200 transition-colors no-underline"
          >
            Contact Sales
          </a>
        </div>
      </div>

      <div class="text-center mt-16">
        <p class="text-gray-700 mb-4">Start with the Free plan. Upgrade anytime as your needs grow.</p>
        <p class="text-gray-600 text-sm">All paid plans include a 14-day money-back guarantee.</p>
      </div>
    </div>

    <AppFooter />
  </div>
</template>

<script setup>
import AppFooter from '@/components/AppFooter.vue'
</script>
