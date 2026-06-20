<template>
  <nav class="anav" role="navigation" aria-label="Navegação principal">
    <router-link to="/" class="anav-logo">
      <AppLogo style="height:28px" />
    </router-link>

    <div class="anav-right">
      <!-- GUEST -->
      <template v-if="!isAuthenticated">
        <router-link to="/pricing" class="anav-link">Preços</router-link>
        <router-link to="/login"   class="anav-link">Entrar</router-link>
        <router-link to="/register" class="anav-cta">Começar</router-link>
      </template>

      <!-- AUTH -->
      <template v-else>
        <!-- Upgrade chip — only for free users after subscription is known -->
        <router-link
          v-if="!loadingSubscription && !isSubscribed"
          to="/pricing"
          class="anav-upgrade"
        >
          <span class="anav-sparkle">✦</span>
          <span class="anav-upgrade-label">Fazer upgrade</span>
        </router-link>

        <!-- User card + dropdown -->
        <div class="anav-user" v-click-outside="() => open = false">
          <button
            class="anav-user-btn"
            :aria-expanded="open"
            aria-haspopup="true"
            aria-label="Menu da conta"
            @click="open = !open"
            @keydown.escape="open = false"
          >
            <div class="anav-avatar" :style="{ background: avatarColor.bg, color: avatarColor.color, borderColor: avatarColor.border }">{{ initials }}</div>
            <div class="anav-info">
              <span class="anav-email">{{ truncEmail }}</span>
              <span class="anav-plan" :class="isSubscribed ? 'pro' : 'free'">
                {{ isSubscribed ? planName : 'Free' }}
              </span>
            </div>
            <svg class="anav-chevron" :class="{ open }" viewBox="0 0 16 16" width="11" fill="none" stroke="currentColor" stroke-width="2.2">
              <polyline points="4 6 8 10 12 6"/>
            </svg>
          </button>

          <Transition name="anav-drop">
            <div v-if="open" class="anav-dropdown" role="menu">
              <div class="anav-drop-head">
                <div class="anav-drop-avatar" :style="{ background: avatarColor.bg, color: avatarColor.color, borderColor: avatarColor.border }">{{ initials }}</div>
                <div>
                  <div class="anav-drop-email">{{ userEmail }}</div>
                  <div class="anav-drop-planrow">
                    <span class="anav-plan-dot" :class="isSubscribed ? 'pro' : 'free'"></span>
                    {{ isSubscribed ? planName : 'Plano Gratuito' }}
                  </div>
                </div>
              </div>

              <div class="anav-div"></div>

              <router-link to="/simular" class="anav-item" role="menuitem" @click="open=false">
                <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8">
                  <polygon points="4 2 12 8 4 14"/>
                </svg>
                Nova Simulação
              </router-link>
              <router-link to="/dashboard" class="anav-item" @click="open=false">
                <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8">
                  <rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9" y="2" width="5" height="5" rx="1"/>
                  <rect x="2" y="9" width="5" height="5" rx="1"/><rect x="9" y="9" width="5" height="5" rx="1"/>
                </svg>
                Painel
              </router-link>
              <router-link to="/pricing" class="anav-item" @click="open=false">
                <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M8 1L9.8 5.2H14L10.6 7.8L11.8 12L8 9.4L4.2 12L5.4 7.8L2 5.2H6.2Z"/>
                </svg>
                Assinatura
              </router-link>

              <div class="anav-div"></div>

              <button class="anav-item anav-danger" @click="handleSignOut">
                <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M6 2H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>
                  <polyline points="11 11 14 8 11 5"/><line x1="14" y1="8" x2="6" y2="8"/>
                </svg>
                Sair
              </button>
            </div>
          </Transition>
        </div>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useSubscription } from '../composables/useSubscription'
import AppLogo from './AppLogo.vue'

const vClickOutside = {
  mounted(el, b) {
    el._co = (e) => { if (!el.contains(e.target)) b.value(e) }
    document.addEventListener('click', el._co)
  },
  unmounted(el) { document.removeEventListener('click', el._co) }
}

const router = useRouter()
const open = ref(false)

const { userEmail, isAuthenticated, signOut } = useAuth()
const { isSubscribed, planName, loadingSubscription, fetchSubscription } = useSubscription()

onMounted(fetchSubscription)

const initials = computed(() => {
  if (!userEmail.value) return '?'
  return userEmail.value.slice(0, 2).toUpperCase()
})

const truncEmail = computed(() => {
  if (!userEmail.value) return ''
  const local = userEmail.value.split('@')[0]
  return local.length > 11 ? local.slice(0, 11) + '…' : local
})

const avatarColor = computed(() => {
  if (!userEmail.value) return { bg: 'var(--surface-2)', color: 'var(--text2)', border: 'var(--border2)' }
  let hash = 0
  for (let i = 0; i < userEmail.value.length; i++) {
    hash = userEmail.value.charCodeAt(i) + ((hash << 5) - hash)
    hash = hash & hash
  }
  const hue = Math.abs(hash) % 360
  return {
    bg: `hsl(${hue},55%,90%)`,
    color: `hsl(${hue},55%,32%)`,
    border: `hsl(${hue},45%,78%)`
  }
})

const handleSignOut = async () => {
  open.value = false
  await signOut()
  router.push('/')
}
</script>

<style scoped>
/* ─── Shell ─── */
.anav {
  height: 52px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px;
  border-bottom: 1px solid var(--border);
  background: var(--nav-bg, var(--bg));
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: sticky; top: 0; z-index: 100;
  flex-shrink: 0;
}
.anav-logo { display: flex; align-items: center; text-decoration: none; }
.anav-right { display: flex; align-items: center; gap: 8px; }

/* ─── Guest links ─── */
.anav-link {
  font-size: 0.69rem; color: var(--text2); text-decoration: none;
  letter-spacing: 0.04em; transition: color var(--dur-fast, 0.12s); padding: 0 6px;
}
.anav-link:hover { color: var(--text); }
.anav-link.router-link-active,
.anav-link.router-link-exact-active { color: var(--text); }
.anav-cta {
  font-size: 0.68rem; font-weight: 600; font-family: var(--font);
  color: var(--text); background: var(--bg3); border: 1px solid var(--border2);
  border-radius: 980px; padding: 6px 16px; text-decoration: none;
  transition: all 0.15s; letter-spacing: -0.01em;
}
.anav-cta:hover { background: var(--bg4, #1e1e1e); }

/* ─── Upgrade chip ─── */
.anav-upgrade {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.64rem; font-weight: 600; letter-spacing: -0.01em;
  color: var(--green-text);
  background: var(--green-dim);
  border: 1px solid var(--green-border);
  border-radius: 100px; padding: 5px 13px;
  text-decoration: none; transition: all 0.2s; white-space: nowrap;
}
.anav-upgrade:hover {
  background: var(--green-border);
  opacity: 0.9;
}
.anav-sparkle { font-size: 0.7rem; }

/* ─── User card ─── */
.anav-user { position: relative; }
.anav-user-btn {
  display: flex; align-items: center; gap: 8px;
  background: transparent; border: 1px solid var(--border);
  border-radius: 8px; padding: 4px 10px 4px 4px;
  cursor: pointer; font-family: var(--font);
  transition: all 0.18s; color: var(--text);
}
.anav-user-btn:hover { background: var(--bg3); border-color: var(--border2); }

.anav-avatar {
  width: 26px; height: 26px; border-radius: 6px;
  background: rgba(167,139,250,0.12);
  color: #a78bfa;
  font-size: 9.5px; font-weight: 700; letter-spacing: 0.04em;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 1px solid rgba(167,139,250,0.2);
  font-family: var(--font);
}
.anav-info {
  display: flex; flex-direction: column; gap: 1px; align-items: flex-start;
}
.anav-email {
  font-size: 0.62rem; color: var(--text); font-weight: 500; line-height: 1;
  max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.anav-plan {
  font-size: 0.52rem; font-weight: 700; letter-spacing: 0.08em; line-height: 1;
  text-transform: uppercase;
}
.anav-plan.free { color: var(--text3); }
.anav-plan.pro { color: #4ade80; }

.anav-chevron { color: var(--text3); transition: transform var(--dur-base, 0.18s) var(--ease, ease); flex-shrink: 0; }
.anav-chevron.open { transform: rotate(180deg); }

/* ─── Dropdown ─── */
.anav-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  min-width: 210px; z-index: 200;
  background: var(--bg3); border: 1px solid var(--border2);
  border-radius: 10px; padding: 4px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.55);
}
.anav-drop-head {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px 10px;
}
.anav-drop-avatar {
  width: 30px; height: 30px; border-radius: 7px; flex-shrink: 0;
  background: rgba(167,139,250,0.12); color: #a78bfa;
  font-size: 10px; font-weight: 700; font-family: var(--font);
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(167,139,250,0.2);
}
.anav-drop-email {
  font-size: 0.65rem; color: var(--text); font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px;
}
.anav-drop-planrow {
  display: flex; align-items: center; gap: 5px;
  font-size: 0.58rem; color: var(--text3); margin-top: 3px;
}
.anav-plan-dot {
  width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0;
}
.anav-plan-dot.free { background: var(--text3); }
.anav-plan-dot.pro  { background: #4ade80; }

.anav-div { height: 1px; background: var(--border); margin: 4px 0; }

.anav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 12px; font-size: 0.68rem; color: var(--text2);
  text-decoration: none; background: none; border: none;
  font-family: var(--font); cursor: pointer; width: 100%;
  border-radius: 6px; transition: all 0.12s; letter-spacing: 0.03em;
}
.anav-item:hover { background: rgba(255,255,255,0.04); color: var(--text); }
.anav-danger { color: #f87171; }
.anav-danger:hover { background: rgba(248,113,113,0.07); color: #f87171; }

/* ─── Transition ─── */
.anav-drop-enter-active { transition: opacity 0.16s var(--ease, ease), transform 0.16s var(--ease, ease); }
.anav-drop-leave-active { transition: opacity 0.1s ease, transform 0.1s ease; }
.anav-drop-enter-from { opacity: 0; transform: translateY(-6px) scale(0.97); }
.anav-drop-leave-to  { opacity: 0; transform: translateY(-4px) scale(0.98); }

/* ─── Mobile ─── */
@media (max-width: 640px) {
  .anav { padding: 0 16px; }
  .anav-upgrade-label { display: none; }
  .anav-upgrade { padding: 5px 9px; }
  .anav-info, .anav-chevron { display: none; }
  .anav-user-btn { border: none; background: transparent; padding: 2px; }
  .anav-user-btn:hover { background: transparent; }
  .anav-avatar { width: 30px; height: 30px; border-radius: 50%; font-size: 10.5px; }
}
</style>
