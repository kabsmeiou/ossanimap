<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3>Confirm Download</h3>
            <button class="close-btn" @click="$emit('close')" aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="info-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>
            <p class="message">
              This download will be provided by <strong>chimu.moe</strong>, a third-party beatmap mirror service.
            </p>
            <p class="submessage">
              By continuing, you acknowledge that the download is handled by an external service.
            </p>
            <label class="checkbox-container">
              <input type="checkbox" v-model="dontShowAgain" />
              <span class="checkbox-label">Don't show this again for this session</span>
            </label>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-cancel" @click="$emit('close')">
              Cancel
            </button>
            <button class="btn btn-confirm" @click="handleConfirm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              Continue Download
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'confirm'])

const dontShowAgain = ref(false)

const handleOverlayClick = () => {
  emit('close')
}

const handleConfirm = () => {
  if (dontShowAgain.value) {
    sessionStorage.setItem('skipDownloadModal', 'true')
  }
  emit('confirm')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 480px;
  width: 100%;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
}

.close-btn {
  background: transparent;
  border: none;
  color: #718096;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f7fafc;
  color: #2d3748;
}

.modal-body {
  padding: 32px 24px;
  text-align: center;
}

.info-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  color: #667eea;
}

.message {
  font-size: 16px;
  color: #2d3748;
  margin: 0 0 12px;
  line-height: 1.6;
}

.message strong {
  color: #667eea;
  font-weight: 600;
}

.submessage {
  font-size: 14px;
  color: #718096;
  margin: 0;
  line-height: 1.5;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
  cursor: pointer;
  user-select: none;
}

.checkbox-container input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
}

.checkbox-label {
  font-size: 14px;
  color: #4a5568;
  line-height: 1.4;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px 24px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel {
  background: #f7fafc;
  color: #4a5568;
}

.btn-cancel:hover {
  background: #edf2f7;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-confirm:active {
  transform: translateY(0);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 480px) {
  .modal-container {
    margin: 0 16px;
  }
  
  .modal-footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
