<template>
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" :key="$route.path" />
    </Transition>
  </RouterView>
  <ToastNotification />
</template>

<script setup>
import ToastNotification from './components/ToastNotification.vue'
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;700;800&display=swap');

.page-enter-active,
.page-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.page-enter-from { opacity: 0; transform: translateY(6px); }
.page-leave-to  { opacity: 0; transform: translateY(-4px); }
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --bg:   #080808;
  --bg2:  #0f0f0f;
  --bg3:  #161616;
  --bg4:  #1e1e1e;
  --border:  rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.12);
  --text:  #ffffff;
  --text2: rgba(255,255,255,0.55);
  --text3: rgba(255,255,255,0.28);
  --text4: rgba(255,255,255,0.12);
  --green: #BDEBB5;
  --red:   #ef4444;
  --amber: #f59e0b;
  --blue:  #3b82f6;
  --font:  'Roboto Mono', monospace;
  --mono:  'Roboto Mono', 'JetBrains Mono', monospace;
}
html, body { height: 100%; background: var(--bg); color: var(--text); }
#app { font-family: var(--font); -webkit-font-smoothing: antialiased; background: var(--bg); color: var(--text); }
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2, rgba(255,255,255,0.12)); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text3, rgba(255,255,255,0.28)); }
button { font-family: inherit; cursor: pointer; }
input, textarea, select { font-family: inherit; }
::selection { background: var(--green-dim, rgba(189,235,181,0.15)); color: inherit; }
:focus-visible { outline: 2px solid var(--green, #BDEBB5); outline-offset: 2px; border-radius: 3px; }
.step-card,.project-card,.modal-content,.card-content,.report-section-item,.timeline-content,.tools-card,.chat-panel,.survey-panel {
  background: var(--bg3) !important; border-color: var(--border) !important; color: var(--text) !important;
}
.card-header,.panel-header,.modal-header,.modal-actions,.modal-divider {
  background: var(--bg2) !important; border-color: var(--border) !important;
}
.card-title,.section-title,.step-title,.phase-title,.btn-text,.modal-id { color: var(--text) !important; }
.card-desc,.modal-label,.modal-file-name,.divider-text,.hint-text,.info-value { color: var(--text2) !important; }
.card-footer,.modal-requirement,.modal-empty,.file-item,.files-empty { background: var(--bg2) !important; border-color: var(--border) !important; }
</style>

