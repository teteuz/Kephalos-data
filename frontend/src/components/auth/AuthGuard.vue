<template>
  <!-- While session is loading, show a minimal spinner -->
  <div v-if="loading" class="auth-guard-loading">
    <div class="auth-guard-spinner"></div>
  </div>

  <!-- Session confirmed — render the slot -->
  <slot v-else-if="isAuthenticated" />

  <!-- No session — router guard should redirect, but this is a safety net -->
  <div v-else class="auth-guard-fallback">
    <router-link to="/login" class="auth-guard-link">← Sign in to continue</router-link>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { loading, isAuthenticated } = useAuth()
</script>

<style scoped>
.auth-guard-loading {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}
.auth-guard-spinner {
  width: 20px; height: 20px;
  border: 2px solid var(--border2);
  border-top-color: var(--green);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.auth-guard-fallback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}
.auth-guard-link {
  font-size: 13px;
  color: var(--text2);
  text-decoration: none;
}
.auth-guard-link:hover { color: var(--green); }
</style>
