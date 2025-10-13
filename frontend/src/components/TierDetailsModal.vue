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
              <h6 class="fw-bold">Description</h6>
              <p class="text-muted">{{ tier.description }}</p>
            </div>

            <!-- Setup Time -->
            <div class="mb-4">
              <h6 class="fw-bold">Setup Time</h6>
              <p class="text-muted">{{ tier.setup_time }}</p>
            </div>

            <!-- Advantages -->
            <div class="mb-4">
              <h6 class="fw-bold text-success">
                <i class="fas fa-check-circle me-1"></i> Advantages
              </h6>
              <ul class="mb-0">
                <li v-for="adv in tier.advantages" :key="adv" class="mb-2">
                  {{ adv }}
                </li>
              </ul>
            </div>

            <!-- Limitations -->
            <div v-if="tier.limitations && tier.limitations.length > 0" class="mb-4">
              <h6 class="fw-bold text-warning">
                <i class="fas fa-exclamation-circle me-1"></i> Limitations
              </h6>
              <ul class="mb-0">
                <li v-for="lim in tier.limitations" :key="lim" class="mb-2">
                  {{ lim }}
                </li>
              </ul>
            </div>

            <!-- Requirements -->
            <div v-if="tier.requires && tier.requires.length > 0" class="mb-4">
              <h6 class="fw-bold">Requirements</h6>
              <ul class="mb-0">
                <li v-for="req in tier.requires" :key="req">
                  {{ req }}
                </li>
              </ul>
            </div>

            <!-- Rate Limits (if applicable) -->
            <div v-if="tier.rate_limits" class="mb-4">
              <h6 class="fw-bold">Rate Limits</h6>
              <div v-if="typeof tier.rate_limits === 'object' && !Array.isArray(tier.rate_limits)">
                <div v-for="(limits, api) in tier.rate_limits" :key="api" class="mb-2">
                  <div class="fw-bold small">{{ api }}</div>
                  <ul class="small text-muted mb-0">
                    <li v-if="limits.requests_per_minute">
                      {{ limits.requests_per_minute }} requests/minute
                    </li>
                    <li v-if="limits.requests_per_day">
                      {{ limits.requests_per_day }} requests/day
                    </li>
                  </ul>
                </div>
              </div>
              <p v-else class="text-muted small">
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
