<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex justify-between items-center">
          <!-- Logo -->
          <router-link to="/" class="inline-flex items-center gap-3 group no-underline">
            <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-xl">L</span>
            </div>
            <span class="text-2xl font-bold text-gray-900">Lodgeick</span>
          </router-link>

          <!-- Navigation -->
          <nav class="flex items-center gap-6">
            <router-link to="/dashboard" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">
              Dashboard
            </router-link>
            <router-link to="/account/integrations" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">
              Integrations
            </router-link>
            <router-link to="/account/settings" class="text-gray-700 hover:text-blue-600 font-medium transition-colors no-underline">
              Settings
            </router-link>
            <router-link to="/account" class="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors no-underline">
              <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-blue-600 font-medium text-sm">
                  {{ userInitials }}
                </span>
              </div>
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Banner -->
      <div class="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-xl p-8 text-white mb-8">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold mb-2">
              Welcome back, {{ userName }}! 👋
            </h1>
            <p class="text-blue-100 text-lg">
              {{ connectedAppsCount > 0
                ? `You have ${connectedAppsCount} app${connectedAppsCount > 1 ? 's' : ''} connected and ${activeIntegrationsCount} integration${activeIntegrationsCount !== 1 ? 's' : ''} running.`
                : 'Get started by connecting your first app below.'
              }}
            </p>
          </div>
          <div class="hidden md:block">
            <svg class="w-32 h-32 text-blue-400 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Onboarding Checklist (only show if not completed or dismissed) -->
      <div v-if="showOnboardingChecklist" class="mb-8 onboarding-checklist">
        <OnboardingChecklist
          :items="checklistItems"
          @action="handleChecklistAction"
          @dismiss="dismissChecklist"
        />
      </div>

      <!-- Stats Grid - Now clickable -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8" data-tutorial="stats">
        <router-link
          to="/account/integrations"
          class="bg-white rounded-xl shadow-sm p-6 hover:shadow-lg transition-all cursor-pointer no-underline"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 mb-1">Connected Apps</p>
              <p class="text-3xl font-bold text-gray-900">{{ connectedAppsCount }}</p>
              <p class="text-xs text-blue-600 mt-2 font-medium">View all apps →</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
          </div>
        </router-link>

        <router-link
          to="/configure"
          class="bg-white rounded-xl shadow-sm p-6 hover:shadow-lg transition-all cursor-pointer no-underline"
        >
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 mb-1">Active Integrations</p>
              <p class="text-3xl font-bold text-gray-900">{{ activeIntegrationsCount }}</p>
              <p class="text-xs text-green-600 mt-2 font-medium">Configure fields →</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
        </router-link>

        <div class="bg-white rounded-xl shadow-sm p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 mb-1">Data Synced Today</p>
              <p class="text-3xl font-bold text-gray-900">{{ dataSyncedCount }}</p>
              <p class="text-xs text-gray-500 mt-2">Last sync: {{ lastSyncTime }}</p>
            </div>
            <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Featured Action: Create Workflow -->
      <div v-if="connectedAppsCount >= 2" class="mb-8">
        <router-link
          to="/workflow/create"
          class="block bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-6 hover:shadow-xl transition-all group no-underline"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-white bg-opacity-20 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white mb-1">Create a Workflow</h3>
                <p class="text-blue-100">Connect your apps and automate data sync with field mapping</p>
              </div>
            </div>
            <svg class="w-6 h-6 text-white group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </router-link>
      </div>

      <!-- Quick Actions -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900">Quick Actions</h2>
          <HelpTooltip
            title="Quick Actions"
            content="These shortcuts give you quick access to the most common tasks. Click any action to get started."
            width="lg"
          />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" data-tutorial="quick-actions">
          <!-- Create Workflow (Primary Action) -->
          <router-link
            v-if="connectedAppsCount >= 2"
            to="/workflow/create"
            class="p-4 border-2 border-purple-300 bg-purple-50 rounded-lg hover:border-purple-500 hover:bg-purple-100 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Create Workflow</div>
            <div class="text-sm text-gray-600">Build automated data sync</div>
          </router-link>

          <!-- Connect Apps -->
          <router-link
            to="/connect"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left group no-underline"
            data-tutorial="connect-app"
          >
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Connect Apps</div>
            <div class="text-sm text-gray-600">Add new integrations</div>
          </router-link>

          <!-- Manage OAuth -->
          <router-link
            to="/integrate"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">OAuth Setup</div>
            <div class="text-sm text-gray-600">Configure credentials</div>
          </router-link>

          <!-- Configure Fields -->
          <router-link
            to="/configure"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Field Mapping</div>
            <div class="text-sm text-gray-600">Map data fields</div>
          </router-link>

          <!-- Account Settings -->
          <router-link
            to="/account/settings"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-orange-500 hover:bg-orange-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Settings</div>
            <div class="text-sm text-gray-600">Account preferences</div>
          </router-link>

          <!-- View Integrations -->
          <router-link
            to="/account/integrations"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">View Integrations</div>
            <div class="text-sm text-gray-600">Manage connections</div>
          </router-link>

          <!-- Security -->
          <router-link
            to="/account/security"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Security</div>
            <div class="text-sm text-gray-600">Passwords & auth</div>
          </router-link>

          <!-- Subscription -->
          <router-link
            to="/account/subscription"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-teal-500 hover:bg-teal-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-teal-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Subscription</div>
            <div class="text-sm text-gray-600">Billing & plans</div>
          </router-link>

          <!-- Documentation -->
          <a
            href="https://docs.lodgeick.com"
            target="_blank"
            rel="noopener noreferrer"
            class="p-4 border-2 border-gray-200 rounded-lg hover:border-gray-500 hover:bg-gray-50 transition-all text-left group no-underline"
          >
            <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div class="font-semibold text-gray-900 mb-1">Documentation</div>
            <div class="text-sm text-gray-600 flex items-center gap-1">
              Learn more
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
          </a>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-900">Recent Activity</h2>
          <button class="text-sm text-blue-600 hover:text-blue-700 font-medium">
            View all →
          </button>
        </div>
        <div class="space-y-4">
          <div v-if="connectedAppsCount === 0" class="text-center py-12">
            <!-- Enhanced Empty State with Illustration -->
            <div class="mb-6">
              <div class="w-24 h-24 mx-auto bg-gradient-to-br from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
                <svg class="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>

            <h3 class="text-lg font-bold text-gray-900 mb-2">
              No activity yet
            </h3>
            <p class="text-gray-600 mb-6 max-w-md mx-auto">
              Your activity feed will show integration events, data syncs, and important updates once you connect your first app.
            </p>

            <!-- Quick Start Buttons -->
            <div class="flex justify-center gap-3">
              <router-link
                to="/connect"
                class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg hover:scale-105 transition-all no-underline"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Connect Your First App
              </router-link>

              <a
                href="https://docs.lodgeick.com"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-gray-400 hover:bg-gray-50 transition-all no-underline"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                View Documentation
              </a>
            </div>

            <!-- Helpful Tips -->
            <div class="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200 max-w-2xl mx-auto">
              <div class="flex items-start gap-3 text-left">
                <div class="flex-shrink-0 mt-0.5">
                  <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="flex-1">
                  <h4 class="font-semibold text-blue-900 mb-1">Pro Tip</h4>
                  <p class="text-sm text-blue-800">
                    Start with popular apps like Slack, Google Sheets, or Salesforce. Our Quick Start mode makes OAuth setup a breeze!
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
            <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="font-medium text-gray-900">Integration activated</p>
              <p class="text-sm text-gray-600">Successfully connected your apps</p>
              <p class="text-xs text-gray-500 mt-1">Just now</p>
            </div>
          </div>

          <div class="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="flex-1">
              <p class="font-medium text-gray-900">Account created</p>
              <p class="text-sm text-gray-600">Welcome to Lodgeick!</p>
              <p class="text-xs text-gray-500 mt-1">A few minutes ago</p>
            </div>
          </div>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useOnboardingStore } from '@/stores/onboarding'
import { session } from '@/data/session'
import OnboardingChecklist from '@/components/OnboardingChecklist.vue'
import HelpTooltip from '@/components/HelpTooltip.vue'

const router = useRouter()
const onboardingStore = useOnboardingStore()

const connectedAppsCount = computed(() => onboardingStore.connectedApps.length)
const activeIntegrationsCount = computed(() => onboardingStore.selectedIntegrations.length)

// Onboarding checklist state
const checklistDismissed = ref(false)
const checklistItems = ref([])

// Load checklist dismissal state from localStorage
onMounted(() => {
  const dismissed = localStorage.getItem('onboarding_checklist_dismissed')
  if (dismissed === 'true') {
    checklistDismissed.value = true
  }
  updateChecklistItems()
})

// Update checklist items based on current state
function updateChecklistItems() {
  checklistItems.value = [
    {
      id: 'connect_app',
      title: 'Connect your first app',
      description: 'Choose an app from our catalog to get started with integrations',
      completed: connectedAppsCount.value > 0,
      completedAt: connectedAppsCount.value > 0 ? Date.now() : null,
      actionLabel: 'Connect App',
      actionRoute: '/connect',
      estimatedTime: '2 min',
      isActive: connectedAppsCount.value === 0,
      isOptional: false
    },
    {
      id: 'setup_oauth',
      title: 'Set up OAuth credentials',
      description: 'Configure OAuth for secure app connections',
      completed: onboardingStore.connectedApps.length > 0 && hasOAuthSetup.value,
      completedAt: hasOAuthSetup.value ? Date.now() : null,
      actionLabel: 'Setup OAuth',
      actionRoute: '/integrate',
      estimatedTime: '5 min',
      isActive: connectedAppsCount.value > 0 && !hasOAuthSetup.value,
      isOptional: false
    },
    {
      id: 'create_integration',
      title: 'Create your first integration',
      description: 'Connect two apps to start automating your workflows',
      completed: activeIntegrationsCount.value > 0,
      completedAt: activeIntegrationsCount.value > 0 ? Date.now() : null,
      actionLabel: 'Create Integration',
      actionRoute: '/configure',
      estimatedTime: '3 min',
      isActive: connectedAppsCount.value > 0 && activeIntegrationsCount.value === 0,
      isOptional: false
    },
    {
      id: 'configure_fields',
      title: 'Map your data fields',
      description: 'Customize how data flows between your apps',
      completed: hasFieldMappings.value,
      completedAt: hasFieldMappings.value ? Date.now() : null,
      actionLabel: 'Configure Fields',
      actionRoute: '/configure',
      estimatedTime: '3 min',
      isActive: activeIntegrationsCount.value > 0 && !hasFieldMappings.value,
      isOptional: true
    },
    {
      id: 'upgrade_plan',
      title: 'Explore Pro features',
      description: 'Upgrade to Pro for AI-powered OAuth and more integrations',
      completed: hasPaidPlan.value,
      completedAt: hasPaidPlan.value ? Date.now() : null,
      actionLabel: 'View Plans',
      actionRoute: '/pricing',
      estimatedTime: '1 min',
      isActive: false,
      isOptional: true
    }
  ]
}

// Computed properties for checklist logic
const hasOAuthSetup = computed(() => {
  // TODO: Check if user has completed OAuth setup
  return connectedAppsCount.value > 0
})

const hasFieldMappings = computed(() => {
  return Object.keys(onboardingStore.fieldMappings).length > 0
})

const hasPaidPlan = computed(() => {
  // TODO: Check user's subscription tier from API
  return false
})

const showOnboardingChecklist = computed(() => {
  return !checklistDismissed.value && !allChecklistItemsCompleted.value
})

const allChecklistItemsCompleted = computed(() => {
  const requiredItems = checklistItems.value.filter(item => !item.isOptional)
  return requiredItems.every(item => item.completed)
})

// Checklist actions
function handleChecklistAction(itemId, route) {
  if (route) {
    router.push(route)
  }
}

function dismissChecklist() {
  checklistDismissed.value = true
  localStorage.setItem('onboarding_checklist_dismissed', 'true')
}

// Real data - no fake random numbers
const dataSyncedCount = computed(() => {
  // TODO: Replace with real API call to get actual sync count
  return 0
})

const lastSyncTime = computed(() => {
  if (connectedAppsCount.value === 0) return 'Never'
  // TODO: Replace with real last sync timestamp from API
  return 'Never'
})

const userName = computed(() => {
  const user = session.user
  if (!user || user === 'Guest') return 'User'

  // Extract first name from email or full name
  if (user.includes('@')) {
    return user.split('@')[0].charAt(0).toUpperCase() + user.split('@')[0].slice(1)
  }

  const parts = user.split(' ')
  return parts[0]
})

const userInitials = computed(() => {
  const user = session.user
  if (!user || user === 'Guest') return 'U'

  const parts = user.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return user[0].toUpperCase()
})
</script>
