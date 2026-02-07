<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" :class="modalClass" @click.stop>
          <div class="modal-header">
            <div class="header-icon" :class="iconClass">
              <!-- Error/Block icon -->
              <svg v-if="type === 'error'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
              <!-- Warning icon -->
              <svg v-else-if="type === 'warning'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <!-- Info icon -->
              <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
            </div>
            <h3>{{ title }}</h3>
            <button class="close-btn" @click="$emit('close')" aria-label="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="message-content">
              <p v-for="(line, index) in messageLines" :key="index" class="message-line">
                {{ line }}
              </p>
            </div>
          </div>
          
          <div class="modal-footer">
            <button v-if="showCancel" class="btn btn-cancel" @click="$emit('close')">
              Cancel
            </button>
            <button v-if="showConfirm" class="btn btn-confirm" :class="confirmBtnClass" @click="$emit('confirm')">
              {{ confirmText }}
            </button>
            <button v-if="showOk" class="btn btn-ok" :class="okBtnClass" @click="$emit('close')">
              OK
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'info', // 'info', 'warning', 'error'
    validator: (v) => ['info', 'warning', 'error'].includes(v)
  },
  title: {
    type: String,
    default: 'Notice'
  },
  message: {
    type: String,
    default: ''
  },
  showConfirm: {
    type: Boolean,
    default: false
  },
  showCancel: {
    type: Boolean,
    default: false
  },
  showOk: {
    type: Boolean,
    default: true
  },
  confirmText: {
    type: String,
    default: 'Continue'
  }
})

defineEmits(['close', 'confirm'])

const messageLines = computed(() => {
  return props.message.split('\n\n').filter(line => line.trim())
})

const modalClass = computed(() => ({
  'modal-error': props.type === 'error',
  'modal-warning': props.type === 'warning',
  'modal-info': props.type === 'info'
}))

const iconClass = computed(() => ({
  'icon-error': props.type === 'error',
  'icon-warning': props.type === 'warning',
  'icon-info': props.type === 'info'
}))

const confirmBtnClass = computed(() => ({
  'btn-confirm-warning': props.type === 'warning'
}))

const okBtnClass = computed(() => ({
  'btn-ok-error': props.type === 'error',
  'btn-ok-warning': props.type === 'warning'
}))

const handleOverlayClick = () => {
  // Don't close on overlay click for errors
  if (props.type !== 'error') {
    // emit('close') - let user explicitly close
  }
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
  z-index: 10000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 480px;
  width: 100%;
  overflow: hidden;
}

.modal-container.modal-error {
  border-top: 4px solid #ef4444;
}

.modal-container.modal-warning {
  border-top: 4px solid #f59e0b;
}

.modal-container.modal-info {
  border-top: 4px solid #3b82f6;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-icon.icon-error {
  background: #fef2f2;
  color: #ef4444;
}

.header-icon.icon-warning {
  background: #fffbeb;
  color: #f59e0b;
}

.header-icon.icon-info {
  background: #eff6ff;
  color: #3b82f6;
}

.close-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: #9ca3af;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #4b5563;
}

.modal-body {
  padding: 20px 24px;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-line {
  margin: 0;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #e5e7eb;
}

.modal-error .message-line {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.modal-warning .message-line {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px 20px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-cancel {
  background: #f3f4f6;
  color: #4b5563;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-confirm-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.btn-confirm-warning:hover {
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.btn-ok {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.btn-ok:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-ok-error {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.btn-ok-error:hover {
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.btn-ok-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.btn-ok-warning:hover {
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}
</style>
