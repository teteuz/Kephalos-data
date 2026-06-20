<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite" aria-atomic="false">
      <TransitionGroup name="toast" tag="div" class="toast-list">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast"
          :class="`toast-${t.type}`"
          @click="remove(t.id)"
          role="alert"
        >
          <span class="toast-icon">
            <svg v-if="t.type === 'success'" viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
            <svg v-else-if="t.type === 'error'" viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg>
            <svg v-else viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8" cy="8" r="6"/><line x1="8" y1="5.5" x2="8" y2="8.5"/><circle cx="8" cy="11" r="0.8" fill="currentColor" stroke="none"/></svg>
          </span>
          <span class="toast-msg">{{ t.message }}</span>
          <button class="toast-close" @click.stop="remove(t.id)" aria-label="Fechar">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '../composables/useToast'
const { toasts, remove } = useToast()
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  pointer-events: none;
}
.toast-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}
.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 14px 11px 13px;
  border-radius: 7px;
  font-size: 12.5px;
  font-family: var(--font, 'Roboto Mono', monospace);
  pointer-events: all;
  cursor: pointer;
  min-width: 220px;
  max-width: 360px;
  background: var(--bg2, #0f0f14);
  border: 1px solid var(--border2, rgba(255,255,255,0.12));
  box-shadow: 0 4px 20px rgba(0,0,0,0.35), 0 1px 4px rgba(0,0,0,0.2);
  backdrop-filter: blur(12px);
  color: var(--text, #fff);
}
.toast-success { border-color: rgba(189,235,181,0.3); }
.toast-error   { border-color: rgba(239,68,68,0.3); }
.toast-info    { border-color: rgba(59,130,246,0.3); }

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}
.toast-success .toast-icon { color: var(--green, #BDEBB5); }
.toast-error   .toast-icon { color: var(--red, #ef4444); }
.toast-info    .toast-icon { color: #60a5fa; }

.toast-msg {
  flex: 1;
  line-height: 1.4;
  font-size: 12px;
  color: var(--text, #fff);
}
.toast-close {
  background: none;
  border: none;
  color: var(--text3, rgba(255,255,255,0.28));
  font-size: 15px;
  cursor: pointer;
  line-height: 1;
  padding: 0 0 0 4px;
  flex-shrink: 0;
}
.toast-close:hover { color: var(--text, #fff); }

/* Transition */
.toast-enter-active  { transition: all 0.25s cubic-bezier(0.22,1,0.36,1); }
.toast-leave-active  { transition: all 0.2s ease; }
.toast-enter-from    { opacity: 0; transform: translateX(18px) scale(0.96); }
.toast-leave-to      { opacity: 0; transform: translateX(8px) scale(0.97); }
.toast-move          { transition: transform 0.25s ease; }

/* Light mode */
:root:not([data-theme="dark"]) .toast {
  background: rgba(255,255,255,0.97);
  border-color: rgba(0,0,0,0.1);
  box-shadow: 0 4px 20px rgba(0,0,0,0.12), 0 1px 4px rgba(0,0,0,0.06);
  color: #090909;
}
:root:not([data-theme="dark"]) .toast-msg { color: #090909; }
:root:not([data-theme="dark"]) .toast-close { color: rgba(0,0,0,0.3); }
:root:not([data-theme="dark"]) .toast-close:hover { color: #090909; }
:root:not([data-theme="dark"]) .toast-success { border-color: rgba(62,207,89,0.35); }
:root:not([data-theme="dark"]) .toast-success .toast-icon { color: #0d7a23; }
:root:not([data-theme="dark"]) .toast-error { border-color: rgba(220,38,38,0.3); }
:root:not([data-theme="dark"]) .toast-error .toast-icon { color: #dc2626; }
</style>
