<template>
  <div class="dash">

    <NavBar />

    <!-- Body -->
    <div class="dash-body">

      <!-- Page title -->
      <div class="dash-header">
        <h1 class="dash-title">Painel</h1>
        <p class="dash-sub">Suas simulações e configurações</p>
      </div>

      <!-- Navigation cards (Claude-style) -->
      <div class="dash-nav-cards">
        <router-link to="/simular" class="dash-card dash-card-primary">
          <div class="dash-card-icon">
            <svg viewBox="0 0 20 20" width="18" fill="none" stroke="currentColor" stroke-width="1.5">
              <polygon points="4 2 16 10 4 18"/>
            </svg>
          </div>
          <div class="dash-card-text">
            <div class="dash-card-title">Nova Simulação</div>
            <div class="dash-card-desc">Configure e execute uma nova previsão social</div>
          </div>
          <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2" class="dash-card-arrow">
            <line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/>
          </svg>
        </router-link>

        <router-link to="/pricing" class="dash-card">
          <div class="dash-card-icon">
            <svg viewBox="0 0 20 20" width="18" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M10 2L12.5 7.5H18L13.5 11L15.5 17L10 13.5L4.5 17L6.5 11L2 7.5H7.5L10 2Z"/>
            </svg>
          </div>
          <div class="dash-card-text">
            <div class="dash-card-title">Assinatura</div>
            <div class="dash-card-desc">
              <span v-if="isSubscribed">{{ planName }} · Renova {{ subscriptionEnd }}</span>
              <span v-else>Gratuito · 2 simulações/mês</span>
            </div>
          </div>
          <span v-if="isSubscribed" class="dash-pro-badge">PRO</span>
          <svg v-else viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2" class="dash-card-arrow">
            <line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/>
          </svg>
        </router-link>
      </div>

      <!-- Plan status (if free show upgrade nudge) -->
      <div v-if="!isSubscribed && !loadingSubscription" class="dash-free-banner">
        <div class="dash-free-left">
          <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="8" cy="8" r="6"/><line x1="8" y1="5.5" x2="8" y2="8.5"/>
            <circle cx="8" cy="11" r="0.6" fill="currentColor" stroke="none"/>
          </svg>
          <span>Limite de <strong>2 simulações</strong> no plano gratuito</span>
        </div>
        <router-link to="/pricing" class="dash-upgrade-btn">Upgrade para Pro →</router-link>
      </div>

      <!-- Stats row (visible if subscribed) -->
      <div v-if="isSubscribed" class="dash-stats">
        <div class="dash-stat">
          <div class="dash-stat-val">∞</div>
          <div class="dash-stat-lbl">Simulações / mês</div>
        </div>
        <div class="dash-stat">
          <div class="dash-stat-val">∞</div>
          <div class="dash-stat-lbl">Agentes máx.</div>
        </div>
        <div class="dash-stat">
          <div class="dash-stat-val dash-stat-green">Completa</div>
          <div class="dash-stat-lbl">Suite de relatórios</div>
        </div>
      </div>

      <!-- Recent simulations -->
      <div class="dash-recent">
        <div class="dash-recent-head">
          <span class="dash-recent-title">Recentes</span>
        </div>
        <div class="dash-recent-empty">
          <svg viewBox="0 0 40 40" width="36" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.25">
            <rect x="6" y="10" width="28" height="22" rx="2"/>
            <line x1="6" y1="16" x2="34" y2="16"/>
            <line x1="13" y1="22" x2="21" y2="22"/>
            <line x1="13" y1="26" x2="18" y2="26"/>
          </svg>
          <p class="dash-empty-text">Nenhuma simulação ainda</p>
          <p class="dash-empty-sub">Execute uma simulação para ver o histórico aqui</p>
        </div>
      </div>

    </div>

    <!-- Bottom: New Simulation fixed button -->
    <div class="dash-bottom-bar">
      <router-link to="/simular" class="dash-new-btn">
        <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2.2">
          <line x1="8" y1="3" x2="8" y2="13"/><line x1="3" y1="8" x2="13" y2="8"/>
        </svg>
        Nova Simulação
      </router-link>
    </div>

  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSubscription } from '../composables/useSubscription'
import NavBar from '../components/NavBar.vue'

const { isSubscribed, planName, subscriptionEnd, loadingSubscription, fetchSubscription, manageSubscription } = useSubscription()

onMounted(fetchSubscription)
</script>

<style scoped>
.dash {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  display: flex;
  flex-direction: column;
}

/* ── Body ── */
.dash-body {
  flex: 1;
  max-width: 700px;
  margin: 0 auto;
  width: 100%;
  padding: 48px 24px 100px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* Header */
.dash-header { margin-bottom: 4px; }
.dash-title { font-size: 1.6rem; font-weight: 300; letter-spacing: -0.02em; margin: 0; }
.dash-sub { font-size: 0.7rem; color: var(--text3); margin: 6px 0 0; }

/* Navigation cards */
.dash-nav-cards { display: flex; flex-direction: column; gap: 8px; }
.dash-card {
  display: flex; align-items: center; gap: 14px;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px 20px;
  text-decoration: none; color: var(--text);
  transition: border-color 0.18s, background 0.18s;
  cursor: pointer;
}
.dash-card:hover { border-color: var(--border2); background: var(--bg2); }
.dash-card-primary { border-color: var(--green-border, rgba(189,235,181,0.15)); }
.dash-card-primary:hover { border-color: rgba(189,235,181,0.35); }
.dash-card-icon {
  width: 36px; height: 36px; border-radius: 8px;
  background: var(--bg4, #1e1e1e); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  color: var(--text2); flex-shrink: 0;
}
.dash-card-primary .dash-card-icon { background: var(--green-dim); color: var(--green-text); border-color: var(--green-border); }
.dash-card-text { flex: 1; min-width: 0; }
.dash-card-title { font-size: 0.78rem; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.dash-card-desc { font-size: 0.62rem; color: var(--text3); }
.dash-card-arrow { color: var(--text3); flex-shrink: 0; }
.dash-pro-badge {
  font-size: 0.55rem; font-weight: 700; letter-spacing: 0.12em;
  color: var(--green); background: var(--green-dim);
  border: 1px solid var(--green-border); border-radius: 4px;
  padding: 3px 7px; flex-shrink: 0;
}

/* Free plan banner */
.dash-free-banner {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(245,158,11,0.04); border: 1px solid rgba(245,158,11,0.15);
  border-radius: 8px; padding: 12px 16px;
  font-size: 0.68rem; color: var(--text2); gap: 12px; flex-wrap: wrap;
}
.dash-free-left { display: flex; align-items: center; gap: 8px; }
.dash-upgrade-btn {
  font-size: 0.65rem; font-weight: 600;
  color: var(--green-text); text-decoration: none;
  white-space: nowrap; opacity: 0.85;
  transition: opacity 0.15s;
}
.dash-upgrade-btn:hover { opacity: 1; }

/* Stats row (PRO only) */
.dash-stats {
  display: grid; grid-template-columns: repeat(3,1fr); gap: 10px;
}
.dash-stat {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 8px; padding: 16px 18px;
}
.dash-stat-val { font-size: 1.4rem; font-weight: 300; letter-spacing: -0.02em; margin-bottom: 4px; }
.dash-stat-green { color: var(--green); }
.dash-stat-lbl { font-size: 0.58rem; color: var(--text3); letter-spacing: 0.04em; }

/* Recent simulations */
.dash-recent {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden;
}
.dash-recent-head {
  padding: 12px 18px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.dash-recent-title { font-size: 0.68rem; font-weight: 600; color: var(--text); letter-spacing: 0.04em; }
.dash-recent-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 48px 24px; gap: 10px; color: var(--text3);
}
.dash-empty-text { font-size: 0.72rem; }
.dash-empty-sub { font-size: 0.62rem; opacity: 0.65; }

/* Bottom bar — fixed new sim button */
.dash-bottom-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 16px 24px;
  background: linear-gradient(to top, var(--bg) 70%, transparent);
  display: flex; justify-content: center;
  z-index: 40;
}
.dash-new-btn {
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--bg3); border: 1px solid var(--border2);
  color: var(--text2); border-radius: 100px;
  padding: 10px 22px; font-size: 0.7rem; font-family: var(--font);
  font-weight: 600; letter-spacing: 0.03em;
  text-decoration: none; transition: all 0.18s;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.dash-new-btn:hover { background: var(--green-dim); color: var(--green-text); border-color: var(--green-border); }

/* Transitions */
@media (max-width: 640px) {
  .dash-body { padding: 32px 16px 100px; gap: 20px; }
  .dash-title { font-size: 1.3rem; }
  .dash-stats { grid-template-columns: 1fr; }
}
</style>
