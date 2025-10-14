<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    @click.self="closeWizard"
  >
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col mx-4">
      <!-- Header -->
      <div class="bg-blue-600 px-6 py-4 rounded-t-2xl flex items-center justify-between">
        <div>
          <h2 class="text-white text-xl font-semibold">{{ providerName }} Setup</h2>
          <p class="text-blue-100 text-sm mt-1">Connect your {{ providerName }} account to Lodgeick</p>
        </div>
        <button
          @click="closeWizard"
          class="text-white/80 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-lg"
          aria-label="Close setup wizard"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Progress Steps (only show after method selection) -->
      <div v-if="setupMethod && setupMethod === 'manual'" class="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div class="flex items-center justify-between max-w-3xl mx-auto">
          <div
            v-for="(step, index) in manualSteps"
            :key="index"
            class="flex items-center"
            :class="{ 'flex-1': index < manualSteps.length - 1 }"
          >
            <div class="flex flex-col items-center">
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all"
                :class="{
                  'bg-blue-600 text-white': currentStep === index + 1,
                  'bg-green-600 text-white': currentStep > index + 1,
                  'bg-gray-200 text-gray-500': currentStep < index + 1
                }"
              >
                <svg v-if="currentStep > index + 1" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <span class="text-xs text-gray-600 mt-2 text-center whitespace-nowrap">{{ step.title }}</span>
            </div>
            <div
              v-if="index < manualSteps.length - 1"
              class="flex-1 h-0.5 mx-4 transition-all"
              :class="currentStep > index + 1 ? 'bg-green-600' : 'bg-gray-200'"
            ></div>
          </div>
        </div>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto px-6 py-6">
        <!-- Step 0: Method Selection -->
        <div v-if="currentStep === 0" class="max-w-4xl mx-auto">
          <div class="text-center mb-8">
            <h3 class="text-2xl font-bold text-gray-900 mb-2">Choose Setup Method</h3>
            <p class="text-gray-600">Select how you'd like to connect {{ providerName }}</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Quick Start Option -->
            <div
              v-if="tierConfig?.tiers?.default?.enabled"
              @click="setupMethod = 'default'"
              class="relative border-2 rounded-xl p-6 cursor-pointer transition-all hover:shadow-lg"
              :class="setupMethod === 'default' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="absolute top-4 right-4">
                <div
                  class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
                  :class="setupMethod === 'default' ? 'border-blue-600 bg-blue-600' : 'border-gray-300'"
                >
                  <svg v-if="setupMethod === 'default'" class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>

              <div class="text-center mb-4">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">Quick Start</h4>
                <p class="text-sm text-gray-600 mb-4">Use Lodgeick's shared OAuth app</p>
                <div class="flex items-center justify-center gap-2 mb-4">
                  <span class="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">Instant</span>
                  <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">No setup</span>
                </div>
              </div>

              <div class="space-y-2 text-sm">
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Ready in seconds</span>
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">No configuration needed</span>
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Perfect for testing</span>
                </div>
              </div>

              <div class="mt-4 pt-4 border-t border-gray-200">
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-xs text-gray-600">Shared rate limits apply</span>
                </div>
              </div>
            </div>

            <!-- AI-Powered Option -->
            <div
              v-if="tierConfig?.tiers?.ai"
              @click="tierConfig.tiers.ai.enabled ? setupMethod = 'ai' : null"
              class="relative border-2 rounded-xl p-6 transition-all"
              :class="{
                'cursor-pointer hover:shadow-lg': tierConfig.tiers.ai.enabled,
                'cursor-not-allowed opacity-60': !tierConfig.tiers.ai.enabled,
                'border-blue-600 bg-blue-50': setupMethod === 'ai' && tierConfig.tiers.ai.enabled,
                'border-gray-200 hover:border-blue-300': setupMethod !== 'ai' && tierConfig.tiers.ai.enabled,
                'border-gray-200': !tierConfig.tiers.ai.enabled
              }"
            >
              <div v-if="tierConfig.tiers.ai.upgrade_required" class="absolute top-4 right-4">
                <span class="px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full flex items-center gap-1">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                  </svg>
                  Pro
                </span>
              </div>
              <div v-else class="absolute top-4 right-4">
                <div
                  class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
                  :class="setupMethod === 'ai' ? 'border-blue-600 bg-blue-600' : 'border-gray-300'"
                >
                  <svg v-if="setupMethod === 'ai'" class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>

              <div class="text-center mb-4">
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">AI-Powered Setup</h4>
                <p class="text-sm text-gray-600 mb-4">Claude guides you through setup</p>
                <div class="flex items-center justify-center gap-2 mb-4">
                  <span v-if="tierConfig.tiers.ai.enabled" class="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">Recommended</span>
                  <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">~5 minutes</span>
                </div>
              </div>

              <div v-if="tierConfig.tiers.ai.upgrade_required" class="space-y-3">
                <div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-center">
                  <p class="text-sm text-amber-800 font-medium">{{ tierConfig.tiers.ai.upgrade_message }}</p>
                </div>
                <button
                  @click.stop="showUpgradeModal"
                  class="w-full px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-lg transition-colors"
                >
                  Upgrade to {{ tierConfig.tiers.ai.upgrade_tier }}
                </button>
              </div>
              <div v-else class="space-y-2 text-sm">
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">AI guides each step</span>
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Auto-creates Google project</span>
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Configures everything</span>
                </div>
              </div>
            </div>

            <!-- Manual Setup Option -->
            <div
              v-if="tierConfig?.tiers?.manual?.enabled"
              @click="setupMethod = 'manual'"
              class="relative border-2 rounded-xl p-6 cursor-pointer transition-all hover:shadow-lg"
              :class="setupMethod === 'manual' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300'"
            >
              <div class="absolute top-4 right-4">
                <div
                  class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
                  :class="setupMethod === 'manual' ? 'border-blue-600 bg-blue-600' : 'border-gray-300'"
                >
                  <svg v-if="setupMethod === 'manual'" class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>

              <div class="text-center mb-4">
                <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg class="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <h4 class="text-lg font-semibold text-gray-900 mb-2">Manual Setup</h4>
                <p class="text-sm text-gray-600 mb-4">Step-by-step instructions</p>
                <div class="flex items-center justify-center gap-2 mb-4">
                  <span class="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">Advanced</span>
                  <span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">~10 minutes</span>
                </div>
              </div>

              <div class="space-y-2 text-sm">
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Full control over setup</span>
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Use your own credentials</span>
                </div>
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span class="text-gray-700">Unlimited rate limits</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Manual Setup Steps -->
        <div v-if="setupMethod === 'manual' && currentStep > 0" class="max-w-3xl mx-auto">
          <!-- Step 1: Create Project -->
          <div v-if="currentStep === 1">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              Create Google Cloud Project
            </h3>

            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
                <div>
                  <p class="font-medium text-blue-900 mb-1">Before you begin</p>
                  <p class="text-sm text-blue-800">You'll need a Google account to create a Cloud project</p>
                </div>
              </div>
            </div>

            <ol class="space-y-4">
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">1</span>
                <div>
                  <p class="text-gray-900 font-medium mb-1">Go to Google Cloud Console</p>
                  <a href="https://console.cloud.google.com" target="_blank" class="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    Open Google Cloud Console
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">2</span>
                <div>
                  <p class="text-gray-900 font-medium">Click the project dropdown at the top of the page</p>
                  <p class="text-sm text-gray-600 mt-1">It usually shows your current project name or "Select a project"</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">3</span>
                <div>
                  <p class="text-gray-900 font-medium">Click "New Project" in the dialog</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">4</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Enter a project name</p>
                  <code class="px-3 py-1 bg-gray-100 text-gray-800 rounded text-sm">Lodgeick Integration</code>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">5</span>
                <div>
                  <p class="text-gray-900 font-medium">Click "Create" and wait for the project to be created</p>
                  <p class="text-sm text-gray-600 mt-1">This usually takes 10-20 seconds</p>
                </div>
              </li>
            </ol>
          </div>

          <!-- Step 2: Enable APIs -->
          <div v-if="currentStep === 2">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              Enable Required APIs
            </h3>

            <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
              <div class="flex items-start gap-3">
                <svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <div>
                  <p class="font-medium text-amber-900 mb-1">Important</p>
                  <p class="text-sm text-amber-800">Make sure your new project is selected in the project dropdown!</p>
                </div>
              </div>
            </div>

            <div class="mb-6">
              <p class="text-gray-700 mb-3">You'll need to enable these APIs for {{ providerName }}:</p>
              <div class="flex flex-wrap gap-2">
                <span class="px-3 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium text-sm">Gmail API</span>
                <span class="px-3 py-2 bg-green-100 text-green-700 rounded-lg font-medium text-sm">Google Sheets API</span>
                <span class="px-3 py-2 bg-purple-100 text-purple-700 rounded-lg font-medium text-sm">Google Drive API</span>
              </div>
            </div>

            <ol class="space-y-4">
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">1</span>
                <div>
                  <p class="text-gray-900 font-medium mb-1">Go to the API Library</p>
                  <a href="https://console.cloud.google.com/apis/library" target="_blank" class="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    Open API Library
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">2</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Search for each API and click "Enable"</p>
                  <ul class="space-y-2 ml-4">
                    <li class="flex items-center gap-2 text-sm text-gray-700">
                      <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                      Search "Gmail API" → Click the result → Click "Enable"
                    </li>
                    <li class="flex items-center gap-2 text-sm text-gray-700">
                      <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                      Search "Google Sheets API" → Click the result → Click "Enable"
                    </li>
                    <li class="flex items-center gap-2 text-sm text-gray-700">
                      <svg class="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                      </svg>
                      Search "Google Drive API" → Click the result → Click "Enable"
                    </li>
                  </ul>
                  <p class="text-sm text-gray-600 mt-2">Each API takes a few seconds to enable</p>
                </div>
              </li>
            </ol>
          </div>

          <!-- Step 3: OAuth Consent Screen -->
          <div v-if="currentStep === 3">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              Configure OAuth Consent Screen
            </h3>

            <ol class="space-y-4">
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">1</span>
                <div>
                  <p class="text-gray-900 font-medium mb-1">Go to OAuth consent screen</p>
                  <a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank" class="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    Open OAuth consent screen
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">2</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Select "External" user type</p>
                  <p class="text-sm text-gray-600">This allows you to use any Google account for testing</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">3</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Fill in the app information</p>
                  <div class="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-600">App name:</span>
                      <span class="font-medium text-gray-900">Lodgeick</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">User support email:</span>
                      <span class="font-medium text-gray-900">Your email</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">Developer contact:</span>
                      <span class="font-medium text-gray-900">Your email</span>
                    </div>
                  </div>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">4</span>
                <div>
                  <p class="text-gray-900 font-medium">Click "Save and Continue"</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">5</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Add OAuth scopes</p>
                  <p class="text-sm text-gray-600 mb-2">Click "Add or Remove Scopes" and add these:</p>
                  <div class="bg-gray-50 rounded-lg p-3 space-y-1 text-xs font-mono">
                    <div class="text-gray-800">https://www.googleapis.com/auth/gmail.readonly</div>
                    <div class="text-gray-800">https://www.googleapis.com/auth/gmail.send</div>
                    <div class="text-gray-800">https://www.googleapis.com/auth/spreadsheets</div>
                    <div class="text-gray-800">https://www.googleapis.com/auth/drive.file</div>
                  </div>
                  <p class="text-sm text-gray-600 mt-2">Click "Update" then "Save and Continue"</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">6</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Add test users</p>
                  <p class="text-sm text-gray-600">Click "Add Users" and enter your Gmail address (the one you'll use for testing)</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">7</span>
                <div>
                  <p class="text-gray-900 font-medium">Click "Save and Continue" through the remaining steps</p>
                </div>
              </li>
            </ol>
          </div>

          <!-- Step 4: Create Credentials -->
          <div v-if="currentStep === 4">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
              </div>
              Create OAuth Credentials
            </h3>

            <ol class="space-y-4">
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">1</span>
                <div>
                  <p class="text-gray-900 font-medium mb-1">Go to Credentials page</p>
                  <a href="https://console.cloud.google.com/apis/credentials" target="_blank" class="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    Open Credentials page
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">2</span>
                <div>
                  <p class="text-gray-900 font-medium">Click "Create Credentials" → "OAuth 2.0 Client ID"</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">3</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Configure the OAuth client</p>
                  <div class="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-600">Application type:</span>
                      <span class="font-medium text-gray-900">Web application</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-600">Name:</span>
                      <span class="font-medium text-gray-900">Lodgeick Local</span>
                    </div>
                  </div>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">4</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Add authorized redirect URI</p>
                  <p class="text-sm text-gray-600 mb-2">Under "Authorized redirect URIs", click "Add URI" and paste this exact URL:</p>
                  <div class="flex items-center gap-2">
                    <input
                      type="text"
                      :value="redirectUri"
                      readonly
                      class="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm font-mono text-gray-800"
                    />
                    <button
                      @click="copyToClipboard(redirectUri)"
                      class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy
                    </button>
                  </div>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">5</span>
                <div>
                  <p class="text-gray-900 font-medium">Click "Create"</p>
                </div>
              </li>
              <li class="flex items-start gap-3">
                <span class="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold">6</span>
                <div>
                  <p class="text-gray-900 font-medium mb-2">Copy your credentials</p>
                  <div class="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <div class="flex items-start gap-2">
                      <svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                      </svg>
                      <p class="text-sm text-amber-800">A dialog will show your <strong>Client ID</strong> and <strong>Client Secret</strong>. Copy both - you'll need them in the next step!</p>
                    </div>
                  </div>
                </div>
              </li>
            </ol>
          </div>

          <!-- Step 5: Enter Credentials -->
          <div v-if="currentStep === 5">
            <h3 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              Enter Your Credentials
            </h3>

            <p class="text-gray-600 mb-6">Paste the OAuth credentials you copied from Google Cloud Console</p>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Client ID</label>
                <input
                  v-model="clientId"
                  type="text"
                  placeholder="1234567890-abc123def456.apps.googleusercontent.com"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                />
                <p class="text-xs text-gray-500 mt-1">Should end with .apps.googleusercontent.com</p>
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">Client Secret</label>
                <div class="relative">
                  <input
                    v-model="clientSecret"
                    :type="showSecret ? 'text' : 'password'"
                    placeholder="GOCSPX-xxxxxxxxxxxxx"
                    class="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  />
                  <button
                    @click="showSecret = !showSecret"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    type="button"
                  >
                    <svg v-if="showSecret" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                </div>
                <p class="text-xs text-gray-500 mt-1">Usually starts with GOCSPX-</p>
              </div>

              <div v-if="clientId && clientSecret" class="bg-green-50 border border-green-200 rounded-lg p-4">
                <div class="flex items-start gap-3">
                  <svg class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <div>
                    <p class="font-medium text-green-900">Credentials look good!</p>
                    <p class="text-sm text-green-800 mt-1">Click "Save & Test Connection" to complete the setup</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 6: Complete -->
          <div v-if="currentStep === 6">
            <div class="text-center py-8">
              <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-10 h-10 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
              </div>
              <h3 class="text-2xl font-bold text-gray-900 mb-3">Setup Complete!</h3>
              <p class="text-gray-600 mb-6">Your {{ providerName }} OAuth credentials have been configured successfully</p>

              <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                <div class="flex items-start gap-3">
                  <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                  <div class="text-left">
                    <p class="font-medium text-blue-900 mb-1">Next steps</p>
                    <p class="text-sm text-blue-800">Close this wizard and click "Connect App" to authenticate with {{ providerName }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="border-t border-gray-200 px-6 py-4 flex items-center justify-between bg-gray-50 rounded-b-2xl">
        <button
          v-if="currentStep > 0 && setupMethod === 'manual'"
          @click="previousStep"
          class="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>
        <div v-else></div>

        <div class="flex items-center gap-3">
          <button
            v-if="currentStep === 0"
            @click="closeWizard"
            class="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium transition-colors"
          >
            Cancel
          </button>

          <button
            v-if="currentStep === 0 && setupMethod"
            @click="proceedWithSetupMethod"
            :disabled="saving"
            class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <span v-if="saving">Connecting...</span>
            <span v-else>Continue</span>
            <svg v-if="!saving" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            v-if="currentStep > 0 && currentStep < 5 && setupMethod === 'manual'"
            @click="nextStep"
            class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            Next
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>

          <button
            v-if="currentStep === 5 && setupMethod === 'manual'"
            @click="saveCredentials"
            :disabled="!clientId || !clientSecret || saving"
            class="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <svg v-if="!saving" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span v-if="saving">Saving...</span>
            <span v-else>Save & Test Connection</span>
          </button>

          <button
            v-if="currentStep === 6"
            @click="closeWizard"
            class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Done
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { call } from "frappe-ui"
import { useToast } from "@/composables/useToast"

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  provider: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'success', 'launchAIWizard'])

const toast = useToast()

const currentStep = ref(0)
const setupMethod = ref(null)
const clientId = ref('')
const clientSecret = ref('')
const showSecret = ref(false)
const saving = ref(false)
const loading = ref(true)
const tierConfig = ref(null)

// Manual setup steps
const manualSteps = [
  { title: 'Create Project' },
  { title: 'Enable APIs' },
  { title: 'Consent Screen' },
  { title: 'Credentials' },
  { title: 'Configure' },
  { title: 'Complete' }
]

// Load tier configuration
onMounted(async () => {
  try {
    loading.value = true
    const config = await call('lodgeick.api.oauth_tiers.get_tier_config', {
      provider: props.provider
    })
    console.log('[OAuth Wizard] Tier config received:', JSON.stringify(config, null, 2))
    console.log('[OAuth Wizard] Default tier enabled:', config?.tiers?.default?.enabled)
    console.log('[OAuth Wizard] AI tier:', config?.tiers?.ai)
    console.log('[OAuth Wizard] Manual tier enabled:', config?.tiers?.manual?.enabled)

    // Ensure tierConfig has proper structure with fallback
    if (config && config.tiers) {
      tierConfig.value = config
    } else {
      // Fallback to minimal config if API returns unexpected format
      console.warn('[OAuth Wizard] API returned unexpected format, using fallback')
      tierConfig.value = {
        provider_name: props.provider,
        tiers: {
          manual: {
            enabled: true,
            label: 'Manual Setup',
            description: 'Configure OAuth manually',
            setup_time: '~10 minutes'
          }
        }
      }
    }

    loadProgress()
  } catch (error) {
    console.error('[OAuth Wizard] Failed to load tier config:', error)
    toast.error(`Failed to load setup options: ${error.message || 'Please try again'}`)

    // Provide fallback config even on error so wizard is still usable
    tierConfig.value = {
      provider_name: props.provider,
      tiers: {
        manual: {
          enabled: true,
          label: 'Manual Setup',
          description: 'Configure OAuth manually',
          setup_time: '~10 minutes'
        }
      }
    }
  } finally {
    loading.value = false
  }
})

// Progress management
function saveProgress() {
  const progress = {
    provider: props.provider,
    setupMethod: setupMethod.value,
    currentStep: currentStep.value,
    clientId: clientId.value,
    clientSecret: clientSecret.value,
    timestamp: Date.now()
  }
  localStorage.setItem(`oauth_progress_${props.provider}`, JSON.stringify(progress))
}

function loadProgress() {
  const saved = localStorage.getItem(`oauth_progress_${props.provider}`)
  if (saved) {
    try {
      const progress = JSON.parse(saved)
      const hoursSinceSave = (Date.now() - progress.timestamp) / (1000 * 60 * 60)
      if (hoursSinceSave < 24) {
        setupMethod.value = progress.setupMethod || null
        currentStep.value = progress.currentStep || 0
        clientId.value = progress.clientId || ''
        clientSecret.value = progress.clientSecret || ''
        toast.info('Resumed your previous OAuth setup', { timeout: 4000 })
      } else {
        clearProgress()
      }
    } catch (e) {
      console.error('Failed to load progress:', e)
    }
  }
}

function clearProgress() {
  localStorage.removeItem(`oauth_progress_${props.provider}`)
}

// Auto-save progress
watch([setupMethod, currentStep, clientId, clientSecret], () => {
  if (currentStep.value > 0 && currentStep.value < 6) {
    saveProgress()
  }
}, { deep: true })

const providerName = computed(() => {
  const names = {
    google: 'Google (Gmail, Sheets, Drive)',
    xero: 'Xero',
    slack: 'Slack',
    microsoft: 'Microsoft 365',
    hubspot: 'HubSpot'
  }
  return names[props.provider] || props.provider
})

const redirectUri = computed(() => {
  return window.location.origin + '/oauth/callback'
})

async function proceedWithSetupMethod() {
  if (setupMethod.value === 'default') {
    saving.value = true
    try {
      await call('lodgeick.api.oauth.save_user_oauth_setup', {
        provider: props.provider,
        tier: 'default',
        use_default: true
      })
      toast.success('Using Lodgeick shared OAuth app! 🎉')
      emit('success', {
        provider: props.provider,
        tier: 'default',
        ready_to_connect: true
      })
      closeWizard()
    } catch (error) {
      toast.error(`Failed to setup: ${error.message || error}`, { timeout: 7000 })
    } finally {
      saving.value = false
    }
  } else if (setupMethod.value === 'ai') {
    emit('launchAIWizard')
    closeWizard()
  } else {
    currentStep.value = 1
  }
}

function nextStep() {
  if (currentStep.value < manualSteps.length) {
    currentStep.value++
  }
}

function previousStep() {
  if (currentStep.value > 0) {
    currentStep.value--
    // If going back to step 0, reset setupMethod to show method selection
    if (currentStep.value === 0) {
      setupMethod.value = null
    }
  }
}

async function saveCredentials() {
  if (!clientId.value || !clientSecret.value) {
    toast.warning('Please enter both Client ID and Client Secret')
    return
  }

  saving.value = true
  try {
    await call('lodgeick.api.oauth.save_user_oauth_setup', {
      provider: props.provider,
      tier: 'manual',
      client_id: clientId.value,
      client_secret: clientSecret.value
    })
    currentStep.value = 6
    toast.success('OAuth credentials saved successfully! 🎉')
    emit('success', {
      provider: props.provider,
      tier: 'manual',
      ready_to_connect: true
    })
  } catch (error) {
    toast.error(`Failed to save credentials: ${error.message || error}`, { timeout: 7000 })
  } finally {
    saving.value = false
  }
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    toast.success('Copied to clipboard!')
  }).catch(() => {
    toast.error('Failed to copy to clipboard')
  })
}

function closeWizard() {
  if (currentStep.value === 6) {
    clearProgress()
  }
  currentStep.value = 0
  setupMethod.value = null
  clientId.value = ''
  clientSecret.value = ''
  showSecret.value = false
  emit('close')
}

function showUpgradeModal() {
  const tier = tierConfig.value?.tiers?.ai?.upgrade_tier || 'Pro'
  toast.info(
    `Upgrade to ${tier} to unlock AI-powered OAuth setup!`,
    { timeout: 10000 }
  )
}
</script>
