<script setup>
import { useConfirmStore } from '@/stores/useConfirmStore';
import { storeToRefs } from 'pinia';

const confirmStore = useConfirmStore();
const { isOpen, title, message, confirmText, cancelText, type } = storeToRefs(confirmStore);

// Helper to determine background/text colors for icons and confirm buttons
const typeClasses = {
  danger: {
    bg: 'rgba(178, 60, 60, 0.1)',
    color: '#b23c3c',
    btnClass: 'btn--danger',
  },
  warning: {
    bg: 'rgba(125, 100, 48, 0.1)',
    color: '#7d6430',
    btnClass: 'btn--warning',
  },
  success: {
    bg: 'rgba(74, 103, 65, 0.1)',
    color: '#4a6741',
    btnClass: 'btn--success',
  },
  info: {
    bg: 'rgba(194, 167, 105, 0.1)',
    color: '#c2a769',
    btnClass: 'btn--brand',
  },
};
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="modal-backdrop" @click="confirmStore.handleCancel">
        <Transition name="zoom" appear>
          <div class="modal-card" @click.stop>
            <div class="modal-card__header">
              <!-- Icon Container -->
              <div 
                class="modal-card__icon-wrapper" 
                :style="{ backgroundColor: typeClasses[type]?.bg, color: typeClasses[type]?.color }"
              >
                <!-- Warning / Alert SVG -->
                <svg v-if="type === 'warning' || type === 'danger'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <!-- Success SVG -->
                <svg v-else-if="type === 'success'" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="m9 12 2 2 4-4"/>
                </svg>
                <!-- Info / Default SVG -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 16v-4"/>
                  <path d="M12 8h.01"/>
                </svg>
              </div>
              <h3 class="modal-card__title">{{ title }}</h3>
            </div>
            
            <div class="modal-card__body">
              <p class="modal-card__message">{{ message }}</p>
            </div>
            
            <div class="modal-card__footer">
              <button 
                class="btn btn--outline" 
                type="button" 
                @click="confirmStore.handleCancel"
              >
                {{ cancelText }}
              </button>
              <button 
                class="btn" 
                :class="typeClasses[type]?.btnClass || 'btn--brand'" 
                type="button" 
                @click="confirmStore.handleConfirm"
              >
                {{ confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(28, 26, 20, 0.4);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 20px;
  box-sizing: border-box;
}

.modal-card {
  background: var(--surface-strong, #ffffff);
  border: 1px solid var(--border-strong, rgba(194, 167, 105, 0.35));
  border-radius: var(--radius-lg, 12px);
  box-shadow: var(--shadow, 0 18px 50px rgba(28, 26, 20, 0.09));
  max-width: 450px;
  width: 100%;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transform: scale(1);
}

.modal-card__header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.modal-card__icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}

.modal-card__title {
  font-family: var(--sans, sans-serif);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-strong, #171717);
  margin: 0;
}

.modal-card__body {
  margin: 0;
}

.modal-card__message {
  font-family: var(--sans, sans-serif);
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--text, #3d3d3d);
  margin: 0;
}

.modal-card__footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

/* Custom button classes to match types */
.btn {
  padding: 10px 20px;
  border-radius: var(--radius-md, 8px);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  font-family: var(--sans, sans-serif);
}

.btn--outline {
  background: transparent;
  border-color: var(--brand, #c2a769);
  color: var(--text, #3d3d3d);
}

.btn--outline:hover {
  background: var(--surface-soft, #f7f1e6);
}

.btn--brand {
  background: var(--brand, #c2a769);
  color: #fff;
}

.btn--brand:hover {
  background: var(--brand-strong, #a8893f);
}

.btn--danger {
  background: var(--danger, #b23c3c);
  color: #fff;
}

.btn--danger:hover {
  background: #962f2f;
}

.btn--warning {
  background: var(--warning, #7d6430);
  color: #fff;
}

.btn--warning:hover {
  background: #634f24;
}

.btn--success {
  background: var(--success, #4a6741);
  color: #fff;
}

.btn--success:hover {
  background: #395032;
}

/* Vue transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.zoom-enter-active,
.zoom-leave-active {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s ease;
}

.zoom-enter-from,
.zoom-leave-to {
  transform: scale(0.95);
  opacity: 0;
}
</style>
