<template>
  <BaseModal
    :model-value="true"
    title="Which Setup Method Should I Choose?"
    size="lg"
    hide-confirm-button
    cancel-text="Got it, thanks!"
    @close="$emit('close')"
  >
    <template #default>
          <!-- Decision Flow -->
          <div class="decision-flow mb-4">
            <h6 class="font-bold text-gray-900 mb-3">Quick Decision Guide:</h6>

            <div class="flow-item mb-3">
              <div class="flow-question">
                <i class="fas fa-question-circle text-primary-600 mr-2"></i>
                Just testing or exploring?
              </div>
              <div class="flow-answer ml-4">
                <i class="fas fa-arrow-right text-green-600 mr-2"></i>
                Choose <strong>Quick Start</strong> - Get started in seconds!
              </div>
            </div>

            <div class="flow-item mb-3">
              <div class="flow-question">
                <i class="fas fa-question-circle text-primary-600 mr-2"></i>
                Need this for real work or production use?
              </div>
              <div class="flow-answer ml-4">
                <i class="fas fa-arrow-right text-green-600 mr-2"></i>
                Choose <strong>AI-Powered Setup</strong> - Get unlimited quotas with guidance
              </div>
            </div>

            <div class="flow-item mb-3">
              <div class="flow-question">
                <i class="fas fa-question-circle text-primary-600 mr-2"></i>
                Already have a Google Cloud project or need custom configuration?
              </div>
              <div class="flow-answer ml-4">
                <i class="fas fa-arrow-right text-green-600 mr-2"></i>
                Choose <strong>Manual Setup</strong> - Full control over your setup
              </div>
            </div>

            <div class="flow-item">
              <div class="flow-question">
                <i class="fas fa-question-circle text-primary-600 mr-2"></i>
                Need billing-required APIs (Maps, Vision AI, Translation)?
              </div>
              <div class="flow-answer ml-4">
                <i class="fas fa-arrow-right text-green-600 mr-2"></i>
                Choose <strong>AI-Powered</strong> or <strong>Manual Setup</strong> - Quick Start doesn't support billing APIs
              </div>
            </div>
          </div>

          <hr class="my-4 border-gray-200">

          <!-- Comparison by Use Case -->
          <h6 class="font-bold text-gray-900 mb-3">Recommended by Use Case:</h6>

          <div class="use-case-grid row g-3">
            <div class="col-md-6">
              <div class="card border-success">
                <div class="card-body">
                  <h6 class="card-title">
                    <i class="fas fa-flask text-success me-2"></i>
                    Testing & Learning
                  </h6>
                  <p class="card-text text-sm text-gray-600">
                    Trying out integrations, learning how they work, personal projects
                  </p>
                  <div class="badge bg-success">Quick Start</div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card border-primary">
                <div class="card-body">
                  <h6 class="card-title">
                    <i class="fas fa-briefcase text-primary me-2"></i>
                    Business Use
                  </h6>
                  <p class="card-text text-sm text-gray-600">
                    Daily workflows, team collaboration, reliable automation
                  </p>
                  <div class="badge bg-primary">AI-Powered Setup</div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card border-info">
                <div class="card-body">
                  <h6 class="card-title">
                    <i class="fas fa-chart-line text-info me-2"></i>
                    High Volume
                  </h6>
                  <p class="card-text text-sm text-gray-600">
                    Processing hundreds of emails, large datasets, frequent API calls
                  </p>
                  <div class="badge bg-primary">AI-Powered Setup</div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card border-secondary">
                <div class="card-body">
                  <h6 class="card-title">
                    <i class="fas fa-building text-secondary me-2"></i>
                    Enterprise
                  </h6>
                  <p class="card-text text-sm text-gray-600">
                    Compliance requirements, existing infrastructure, custom configs
                  </p>
                  <div class="badge bg-secondary">Manual Setup</div>
                </div>
              </div>
            </div>
          </div>

          <hr class="my-4 border-gray-200">

          <!-- FAQ -->
          <h6 class="font-bold text-gray-900 mb-3">Frequently Asked Questions:</h6>

          <div class="accordion" id="faqAccordion">
            <div class="accordion-item">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#faq1"
                >
                  Can I upgrade from Quick Start to AI later?
                </button>
              </h2>
              <div id="faq1" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                <div class="accordion-body">
                  Yes! You can disconnect and reconnect with a different tier anytime.
                  Your integrations won't be affected - just the OAuth setup method.
                </div>
              </div>
            </div>

            <div class="accordion-item">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#faq2"
                >
                  What happens if I hit rate limits on Quick Start?
                </button>
              </h2>
              <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                <div class="accordion-body">
                  You'll receive a warning at 80% usage, and a notification when you hit the limit.
                  Your workflows will pause until the next reset period (daily/minute). We recommend upgrading to AI-Powered setup for unlimited quotas.
                </div>
              </div>
            </div>

            <div class="accordion-item">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#faq3"
                >
                  Is AI-Powered Setup really "AI"?
                </button>
              </h2>
              <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                <div class="accordion-body">
                  Yes! It uses Claude AI to understand your needs in plain English and automatically
                  determines which Google APIs and scopes you need. It can also create projects for you
                  or guide you through using an existing one.
                </div>
              </div>
            </div>

            <div class="accordion-item">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#faq4"
                >
                  Do I need a credit card for AI-Powered Setup?
                </button>
              </h2>
              <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                <div class="accordion-body">
                  Only if you want to use billing-required APIs like Google Maps, Vision AI, or Translation.
                  For Gmail, Sheets, Drive, and Calendar - no credit card needed!
                </div>
              </div>
            </div>
          </div>
    </template>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <small class="text-gray-500 flex items-center gap-1">
          <i class="fas fa-info-circle"></i>
          Still have questions? <a href="https://docs.example.com" target="_blank" class="text-primary-600 hover:text-primary-700">View full documentation</a>
        </small>
        <BaseButton
          variant="primary"
          @click="$emit('close')"
        >
          Got it, thanks!
        </BaseButton>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from "./BaseModal.vue"
import BaseButton from "./BaseButton.vue"

defineProps({
  provider: {
    type: String,
    required: true
  }
})

defineEmits(['close'])
</script>

<style scoped>
.flow-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
  border-left: 3px solid #007bff;
}

.flow-question {
  font-weight: 600;
  color: #495057;
}

.flow-answer {
  margin-top: 0.5rem;
  color: #6c757d;
}

.use-case-grid .card {
  height: 100%;
  transition: transform 0.2s ease;
}

.use-case-grid .card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.accordion-button:not(.collapsed) {
  background-color: #e7f1ff;
  color: #0056b3;
}
</style>
