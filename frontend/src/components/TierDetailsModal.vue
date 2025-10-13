<template>
  <BaseModal
    :model-value="true"
    :title="`${tier?.icon} ${tier?.label} - Details`"
    size="md"
    @close="$emit('close')"
  >
    <template #default>
          <div v-if="tier">
            <!-- Description -->
            <div class="mb-4">
              <h6 class="font-bold text-gray-900">Description</h6>
              <p class="text-gray-600">{{ tier.description }}</p>
            </div>

            <!-- Setup Time -->
            <div class="mb-4">
              <h6 class="font-bold text-gray-900">Setup Time</h6>
              <p class="text-gray-600">{{ tier.setup_time }}</p>
            </div>

            <!-- Advantages -->
            <div class="mb-4">
              <h6 class="font-bold text-green-600">
                <i class="fas fa-check-circle mr-1"></i> Advantages
              </h6>
              <ul class="mb-0">
                <li v-for="adv in tier.advantages" :key="adv" class="mb-2">
                  {{ adv }}
                </li>
              </ul>
            </div>

            <!-- Limitations -->
            <div v-if="tier.limitations && tier.limitations.length > 0" class="mb-4">
              <h6 class="font-bold text-yellow-600">
                <i class="fas fa-exclamation-circle mr-1"></i> Limitations
              </h6>
              <ul class="mb-0">
                <li v-for="lim in tier.limitations" :key="lim" class="mb-2">
                  {{ lim }}
                </li>
              </ul>
            </div>

            <!-- Requirements -->
            <div v-if="tier.requires && tier.requires.length > 0" class="mb-4">
              <h6 class="font-bold text-gray-900">Requirements</h6>
              <ul class="mb-0">
                <li v-for="req in tier.requires" :key="req">
                  {{ req }}
                </li>
              </ul>
            </div>

            <!-- Rate Limits (if applicable) -->
            <div v-if="tier.rate_limits" class="mb-4">
              <h6 class="font-bold text-gray-900">Rate Limits</h6>
              <div v-if="typeof tier.rate_limits === 'object' && !Array.isArray(tier.rate_limits)">
                <div v-for="(limits, api) in tier.rate_limits" :key="api" class="mb-2">
                  <div class="font-bold text-sm">{{ api }}</div>
                  <ul class="text-sm text-gray-600 mb-0">
                    <li v-if="limits.requests_per_minute">
                      {{ limits.requests_per_minute }} requests/minute
                    </li>
                    <li v-if="limits.requests_per_day">
                      {{ limits.requests_per_day }} requests/day
                    </li>
                  </ul>
                </div>
              </div>
              <p v-else class="text-gray-600 text-sm">
                Rate limits apply - see tier description for details
              </p>
            </div>
          </div>
    </template>

    <template #footer>
      <BaseButton
        variant="secondary"
        @click="$emit('close')"
      >
        Close
      </BaseButton>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseButton from "./BaseButton.vue"
import BaseModal from "./BaseModal.vue"

defineProps({
  tier: {
    type: Object,
    required: true
  },
  tierName: {
    type: String,
    required: true
  }
})

defineEmits(['close'])
</script>
