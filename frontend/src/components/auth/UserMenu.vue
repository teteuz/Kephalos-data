<template>
  <div class="user-menu" v-if="isAuthenticated">
    <button class="user-trigger" @click="open = !open">
      <span class="user-avatar">{{ initials }}</span>
      <svg viewBox="0 0 16 16" width="10" fill="none" stroke="currentColor" stroke-width="2"
           :style="{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }">
        <polyline points="3 6 8 11 13 6"/>
      </svg>
    </button>

    <Transition name="menu-fade">
      <div v-if="open" class="user-dropdown" v-click-outside="() => open = false">
        <div class="user-dropdown-email">{{ userEmail }}</div>

        <div class="user-dropdown-divider"></div>

        <div v-if="loadingSubscription" class="user-dropdown-item user-dropdown-item--muted">
          Loading plan…
        </div>
        <div v-else class="user-dropdown-item">
          <span class="plan-dot" :class="isSubscribed ? 'plan-dot--active' : 'plan-dot--free'"></span>
          {{ isSubscribed ? planName : 'Free' }} Plan
          <router-link v-if="!isSubscribed" to="/pricing" class="upgrade-chip">Upgrade</router-link>
        </div>

        <div class="user-dropdown-divider"></div>

        <router-link to="/dashboard" class="user-dropdown-item user-dropdown-link">
          Dashboard
        </router-link>
        <router-link to="/pricing" class="user-dropdown-item user-dropdown-link">
          Billing
        </router-link>

        <div class="user-dropdown-divider"></div>

        <button class="user-dropdown-item user-dropdown-item--danger" @click="handleSignOut">
          Sign Out
        </button>
      </div>
    </Transition>
  </div>

  <div v-else class="user-menu-guest">
    <router-link to="/login" class="k-nav-link">Sign In</router-link>
    <router-link to="/register" class="k-nav-btn-sm">Get Started</router-link>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../../composables/useAuth'
import { useSubscription } from '../../composables/useSubscription'

const { isAuthenticated, userEmail, signOut } = useAuth()
const { isSubscribed, planName, loadingSubscription, fetchSubscription } = useSubscription()

const open = ref(false)

const initials = computed(() => {
  if (!userEmail.value) return '?'
  return userEmail.value.slice(0, 2).toUpperCase()
})

onMounted(fetchSubscription)

async function handleSignOut() {
  open.value = false
  await signOut()
}

// Simple v-click-outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => {
      if (!el.contains(e.target)) binding.value(e)
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  }
}
</script>

<style scoped>
.user-menu { position: relative; }

.user-trigger {
  display: flex; align-items: center; gap: 6px;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 4px; padding: 5px 10px; cursor: pointer;
  color: var(--text2); font-family: var(--font);
}
.user-trigger:hover { border-color: var(--border2); }

.user-avatar {
  width: 22px; height: 22px; border-radius: 50%;
  background: rgba(189,235,181,0.15); color: var(--green);
  font-size: 10px; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
}

.user-dropdown {
  position: absolute; right: 0; top: calc(100% + 8px);
  width: 220px; background: var(--bg3);
  border: 1px solid var(--border2); border-radius: 6px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  z-index: 1000; overflow: hidden;
}

.user-dropdown-email {
  padding: 12px 14px; font-size: 11px;
  color: var(--text3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.user-dropdown-divider { height: 1px; background: var(--border); }

.user-dropdown-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; font-size: 12px; color: var(--text2);
  cursor: default;
}
.user-dropdown-item--muted { color: var(--text3); }
.user-dropdown-item--danger { color: var(--red); cursor: pointer; background: none; border: none; width: 100%; font-family: var(--font); font-size: 12px; text-align: left; }
.user-dropdown-item--danger:hover { background: rgba(239,68,68,0.06); }

.user-dropdown-link { text-decoration: none; cursor: pointer; }
.user-dropdown-link:hover { background: var(--bg2); color: var(--text); }

.plan-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.plan-dot--active { background: var(--green); }
.plan-dot--free { background: var(--text3); }

.upgrade-chip {
  margin-left: auto; font-size: 10px; padding: 2px 8px;
  background: rgba(189,235,181,0.1); color: var(--green);
  border: 1px solid rgba(189,235,181,0.2); border-radius: 3px;
  text-decoration: none; letter-spacing: 0.5px;
}
.upgrade-chip:hover { background: rgba(189,235,181,0.2); }

/* Guest state */
.user-menu-guest { display: flex; align-items: center; gap: 12px; }
.k-nav-link { color: var(--text2); font-size: 13px; text-decoration: none; }
.k-nav-link:hover { color: var(--text); }
.k-nav-btn-sm {
  background: var(--green); color: #000; border-radius: 4px;
  padding: 7px 16px; font-size: 12px; font-weight: 600;
  text-decoration: none; font-family: var(--font);
}

/* Dropdown transition */
.menu-fade-enter-active, .menu-fade-leave-active { transition: opacity 0.15s, transform 0.15s; }
.menu-fade-enter-from, .menu-fade-leave-to { opacity: 0; transform: translateY(-6px); }
</style>
