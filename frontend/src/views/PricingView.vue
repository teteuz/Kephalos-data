<template>
  <div class="pricing-page">
    <NavBar />

    <div class="pricing-body">
      <div class="pricing-header">
        <span class="k-label">PLANOS</span>
        <h1 class="pricing-title">Simples e transparente</h1>
        <p class="pricing-sub">Simulações ilimitadas. Cancele quando quiser.</p>
      </div>

      <div class="plans-grid">
        <div class="plan-card">
          <div class="plan-badge">GRATUITO</div>
          <div class="plan-price"><span class="plan-amount">R$0</span>/mês</div>
          <div class="plan-desc">Explore a plataforma com execuções limitadas.</div>
          <ul class="plan-features">
            <li>2 simulações / mês</li>
            <li>Até 50 agentes</li>
            <li>Relatórios básicos</li>
          </ul>
          <router-link to="/register" class="plan-btn plan-btn-outline">Começar grátis</router-link>
        </div>

        <div class="plan-card plan-card-featured">
          <div class="plan-badge plan-badge-green">PRO</div>
          <div class="plan-price"><span class="plan-amount">R$34,99</span>/mês</div>
          <div class="plan-desc">Acesso completo para indivíduos e pequenas equipes.</div>
          <ul class="plan-features">
            <li>Simulações ilimitadas</li>
            <li>Agentes ilimitados</li>
            <li>Suíte completa de relatórios</li>
            <li>Modo de interação</li>
            <li>Suporte prioritário</li>
          </ul>
          <button
            class="plan-btn plan-btn-primary"
            :disabled="loadingSub || (isSubscribed && planName === 'Pro')"
            @click="handleSubscribe(PRICE_PRO)"
          >
            <span v-if="loadingSub" class="spinner"></span>
            <span v-else-if="isSubscribed && planName === 'Pro'">Plano atual</span>
            <span v-else>Assinar — R$34,99/mês</span>
          </button>
        </div>
      </div>

      <div v-if="checkoutError" class="checkout-error">{{ checkoutError }}</div>

      <div v-if="isSubscribed" class="manage-sub">
        <span>Você tem uma assinatura <strong>{{ planName }}</strong> ativa.</span>
        <button class="manage-btn" @click="manageSubscription">Gerenciar / Cancelar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useSubscription } from '../composables/useSubscription'
import NavBar from '../components/NavBar.vue'

const PRICE_PRO = import.meta.env.VITE_STRIPE_PRICE_PRO

const { isAuthenticated } = useAuth()
const { isSubscribed, planName, loadingSubscription: loadingSub, fetchSubscription, subscribe, manageSubscription } = useSubscription()

const checkoutError = ref('')

onMounted(fetchSubscription)

async function handleSubscribe(priceId) {
  checkoutError.value = ''

  if (!isAuthenticated.value) {
    window.location.href = '/register'
    return
  }

  try {
    await subscribe(priceId)
  } catch (err) {
    checkoutError.value = err.message || 'Erro ao iniciar checkout. Tente novamente.'
    console.error('Checkout error:', err)
  }
}
</script>

<style scoped>
.pricing-page { min-height: 100vh; background: var(--bg); color: var(--text); }
.pricing-body { max-width: 680px; margin: 0 auto; padding: 72px 24px; }
.pricing-header { text-align: center; margin-bottom: 56px; }
.k-label { font-size: 10px; letter-spacing: 2px; color: var(--green); }
.pricing-title { font-size: 32px; font-weight: 400; margin: 12px 0 10px; }
.pricing-sub { font-size: 14px; color: var(--text2); }
.plans-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 560px) { .plans-grid { grid-template-columns: 1fr; } }
.plan-card { background: var(--bg3); border: 1px solid var(--border); border-radius: 8px; padding: 32px 28px; display: flex; flex-direction: column; gap: 16px; }
.plan-card-featured { border-color: var(--green); }
.plan-badge { font-size: 10px; letter-spacing: 1.5px; color: var(--text3); }
.plan-badge-green { color: var(--green); }
.plan-price { font-size: 14px; color: var(--text2); }
.plan-amount { font-size: 36px; color: var(--text); font-weight: 300; }
.plan-desc { font-size: 13px; color: var(--text2); line-height: 1.5; }
.plan-features { list-style: none; display: flex; flex-direction: column; gap: 8px; flex: 1; margin-top: 4px; }
.plan-features li { font-size: 12px; color: var(--text2); padding-left: 14px; position: relative; }
.plan-features li::before { content: '—'; position: absolute; left: 0; color: var(--text3); }
.plan-btn { display: block; text-align: center; border-radius: 4px; padding: 10px; font-size: 13px; font-family: var(--font); cursor: pointer; text-decoration: none; transition: opacity 0.2s; border: none; }
.plan-btn-outline { background: transparent; border: 1px solid var(--border2); color: var(--text2); }
.plan-btn-outline:hover { border-color: var(--green); color: var(--green); }
.plan-btn-primary { background: var(--green); color: #000; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; }
.plan-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.spinner { width: 13px; height: 13px; border: 2px solid rgba(0,0,0,0.3); border-top-color: #000; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.manage-sub { margin-top: 40px; text-align: center; font-size: 13px; color: var(--text2); display: flex; align-items: center; justify-content: center; gap: 16px; }
.manage-btn { background: transparent; border: 1px solid var(--border2); color: var(--text2); font-family: var(--font); font-size: 12px; border-radius: 4px; padding: 6px 14px; cursor: pointer; }
.manage-btn:hover { border-color: var(--red); color: var(--red); }
.checkout-error { margin-top: 24px; text-align: center; font-size: 12px; color: var(--red); background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.15); border-radius: 4px; padding: 10px 16px; }
</style>
