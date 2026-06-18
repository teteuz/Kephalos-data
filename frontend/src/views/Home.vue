<template>
  <div class="k">


    <!-- NAV -->
    <nav class="k-nav">
      <div class="k-brand">
        <AppLogo class="k-logo-img" />
      </div>

      <div class="k-nav-right">
        <!-- Guest nav -->
        <template v-if="!isAuthenticated">
          <router-link to="/pricing" class="k-nav-link">Preços</router-link>
          <router-link to="/login" class="k-nav-link">Entrar</router-link>
          <router-link to="/register" class="k-nav-btn-outline">Começar</router-link>
        </template>

        <!-- Auth nav -->
        <template v-else>
          <router-link v-if="!isSubscribed" to="/pricing" class="k-nav-upgrade k-nav-hide-mobile"><span class="k-nav-sparkle">✦</span>Fazer upgrade</router-link>
          <router-link to="/dashboard" class="k-nav-link k-nav-hide-mobile">Painel</router-link>
          <button class="k-nav-btn k-nav-hide-mobile" @click="router.push('/simular')">Rodar Simulação</button>
          
          <div class="k-profile-wrap" v-click-outside="() => profileOpen = false">
            <div class="k-nav-avatar" @click="profileOpen = !profileOpen">
              {{ userInitials }}
            </div>
            <Transition name="profile-drop">
              <div v-if="profileOpen" class="k-profile-dropdown">
                <div class="k-profile-email">{{ userEmail }}</div>
                <div class="k-profile-divider"></div>
                <div class="k-profile-plan">
                  <span class="k-plan-dot" :class="isSubscribed ? 'active' : 'free'"></span>
                  <span>{{ isSubscribed ? 'Plano ' + planName : 'Plano Gratuito' }}</span>
                  <router-link v-if="!isSubscribed" to="/pricing" class="k-plan-upgrade-chip" @click="profileOpen=false">Upgrade</router-link>
                </div>
                <div class="k-profile-divider"></div>
                <router-link to="/dashboard" class="k-profile-item" @click="profileOpen=false">
                  <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9" y="2" width="5" height="5" rx="1"/><rect x="2" y="9" width="5" height="5" rx="1"/><rect x="9" y="9" width="5" height="5" rx="1"/></svg>
                  Painel
                </router-link>
                <router-link to="/pricing" class="k-profile-item" @click="profileOpen=false">
                  <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2 4h12v9a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4z"/><path d="M5 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"/></svg>
                  Assinatura
                </router-link>
                <div class="k-profile-divider"></div>
                <button class="k-profile-item k-profile-theme" @click="toggleTheme">
                  <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="8" cy="8" r="4"/><line x1="8" y1="1" x2="8" y2="3"/><line x1="8" y1="13" x2="8" y2="15"/>
                    <line x1="1" y1="8" x2="3" y2="8"/><line x1="13" y1="8" x2="15" y2="8"/>
                    <line x1="2.9" y1="2.9" x2="4.3" y2="4.3"/><line x1="11.7" y1="11.7" x2="13.1" y2="13.1"/>
                    <line x1="2.9" y1="13.1" x2="4.3" y2="11.7"/><line x1="11.7" y1="4.3" x2="13.1" y2="2.9"/>
                  </svg>
                  {{ isDark ? 'Modo Claro' : 'Modo Escuro' }}
                </button>
                <div class="k-profile-divider"></div>
                <button class="k-profile-item k-profile-signout" @click="handleSignOut">
                  <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 2H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/><polyline points="11 11 14 8 11 5"/><line x1="14" y1="8" x2="6" y2="8"/></svg>
                  Sair
                </button>
              </div>
            </Transition>
          </div>
        </template>
      </div>
    </nav>

    <!-- HERO -->
    <section class="k-hero">
      <canvas ref="heroCanvas" class="k-canvas"></canvas>

      <div class="k-hero-body">
        <h1 class="k-title">
          <span class="k-title-glow">O que as pessoas farão</span><br>
          <span class="k-title-dim">Quando Acontecer ?</span>
        </h1>

        <p class="k-subtitle">
          Qualquer cenário. Qualquer decisão. O KEPHALOS executa milhares de agentes autônomos no seu contexto e entrega a inteligência que transforma incerteza em vantagem. Antes que o momento chegue.
        </p>

        <div class="k-hero-cta">
          <button v-if="isAuthenticated" class="k-btn-run" @click="router.push('/simular')">
            Rodar simulação
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
          </button>
          <template v-else>
            <router-link to="/register" class="k-btn-run">
              Começar Free
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
            </router-link>
            <router-link to="/login" class="k-btn-secondary">Entrar</router-link>
          </template>
        </div>
      </div>

      <video src="/ai orb 2.webm" class="k-brain-image" autoplay loop muted playsinline preload="auto"></video>
    </section>

    <!-- USE CASES -->
    <section class="k-usecases">
      <div class="k-uc-header">
        <span class="k-label">QUEM USA</span>
        <h2 class="k-uc-title">Se a decisão importa,<br>a simulação vale.</h2>
        <p class="k-uc-sub">Não importa o setor. Se você precisa prever como pessoas, mercados ou sistemas vão reagir a algo, o KEPHALOS foi feito para você.</p>
      </div>
      <div class="k-uc-grid">
        <div class="k-uc-card" v-for="uc in useCases" :key="uc.id" :class="{ 'k-uc-card--active': activeUC === uc.id }" @mouseenter="activeUC = uc.id" @mouseleave="activeUC = null">
          <div class="k-uc-icon" v-html="uc.icon"></div>
          <div class="k-uc-sector">{{ uc.sector }}</div>
          <div class="k-uc-headline">{{ uc.headline }}</div>
          <div class="k-uc-body">{{ uc.body }}</div>
          <div class="k-uc-tags">
            <span class="k-uc-tag" v-for="tag in uc.tags" :key="tag">{{ tag }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- STATS BAND -->
    <section class="k-stats-band">
      <div class="k-stat" v-for="stat in trustStats" :key="stat.label">
        <div class="k-stat-accent"></div>
        <div class="k-stat-value">{{ stat.value }}</div>
        <div class="k-stat-label">{{ stat.label }}</div>
        <div class="k-stat-note">{{ stat.note }}</div>
      </div>
    </section>

    <!-- TRUST — COMO FUNCIONA -->
    <section class="k-how">
      <div class="k-how-header">
        <span class="k-label">COMO FUNCIONA</span>
        <h2 class="k-how-title">Do cenário à inteligência<br><span class="k-how-dim">em ~30 minutos reais.</span></h2>
      </div>
      <div class="k-how-steps">
        <div class="k-how-step" v-for="(step, i) in howSteps" :key="i">
          <div class="k-how-num">{{ String(i+1).padStart(2,'0') }}</div>
          <div class="k-how-step-icon" v-html="step.icon"></div>
          <div class="k-how-step-title">{{ step.title }}</div>
          <div class="k-how-step-desc">{{ step.desc }}</div>
        </div>
      </div>
    </section>


    <!-- SOCIAL PROOF + REVENUE CTA -->
    <section class="k-revenue-cta">
      <div class="k-revenue-inner">
        <div class="k-revenue-left">
          <span class="k-label">POR QUE FAZER UPGRADE</span>
          <h2 class="k-revenue-title">Você um passo à frente.<br>Sempre.</h2>
          <p class="k-revenue-sub">Enquanto qualquer outro ainda está debatendo hipóteses, você já rodou o cenário, viu o resultado e ajustou a estratégia. O Pro remove todos os limites. Rode quantas simulações suas decisões exigirem.</p>
          <div class="k-revenue-features">
            <div class="k-rf-item">
              <div class="k-rf-icon">
                <svg viewBox="0 0 16 16" width="14" fill="none" stroke="#BDEBB5" stroke-width="1.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
              </div>
              <div>
                <div class="k-rf-title">Execuções ilimitadas</div>
                <div class="k-rf-desc">Sem limites mensais. Execute quantos cenários suas decisões exigirem.</div>
              </div>
            </div>
            <div class="k-rf-item">
              <div class="k-rf-icon">
                <svg viewBox="0 0 16 16" width="14" fill="none" stroke="#BDEBB5" stroke-width="1.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
              </div>
              <div>
                <div class="k-rf-title">Agentes ilimitados por execução</div>
                <div class="k-rf-desc">Mais agentes significa mais comportamento emergente, previsões mais ricas, melhores decisões.</div>
              </div>
            </div>
            <div class="k-rf-item">
              <div class="k-rf-icon">
                <svg viewBox="0 0 16 16" width="14" fill="none" stroke="#BDEBB5" stroke-width="1.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
              </div>
              <div>
                <div class="k-rf-title">Suite completa de relatórios + modo interação</div>
                <div class="k-rf-desc">Relatórios profundos de atribuição e interação ao vivo com agentes. Disponível só no Pro.</div>
              </div>
            </div>
          </div>
          <div class="k-revenue-cta-row">
            <router-link to="/pricing" class="k-btn-run" v-if="!isAuthenticated || !isSubscribed">
              Assinar Pro por R$34,99/mês
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
            </router-link>
            <span class="k-revenue-cancel">Cancele quando quiser. Sem contratos.</span>
          </div>
        </div>
        <div class="k-revenue-right">
          <div class="k-compare-card">
            <div class="k-compare-header">
              <span class="k-compare-col-label">Recurso</span>
              <span class="k-compare-col-label">Free</span>
              <span class="k-compare-col-label k-compare-col-pro">Pro</span>
            </div>
            <div class="k-compare-row" v-for="row in compareRows" :key="row.feature">
              <span class="k-compare-feature">{{ row.feature }}</span>
              <span class="k-compare-val" v-html="row.free"></span>
              <span class="k-compare-val k-compare-val-pro" v-html="row.pro"></span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- PRICING CTA (only for guests) -->
    <section v-if="!isAuthenticated" class="k-pricing-cta">
      <div class="k-pricing-cta-inner">
        <span class="k-label">PLANOS</span>
        <h2 class="k-pricing-cta-title">Comece explorando. Escale quando precisar.</h2>
        <p class="k-pricing-cta-sub">Qualquer pessoa pode começar grátis com 2 simulações/mês. Quando suas decisões exigirem mais, o Pro libera tudo por R$34,99/mês.</p>
        <div class="k-pricing-cta-btns">
          <router-link to="/register" class="k-btn-run">
            Criar conta grátis
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
          </router-link>
          <router-link to="/pricing" class="k-btn-secondary">Ver planos</router-link>
        </div>
      </div>
    </section>

    <!-- UPGRADE CTA (only for logged-in free users) -->
    <section v-if="isAuthenticated && !isSubscribed" class="k-pricing-cta">
      <div class="k-pricing-cta-inner">
        <span class="k-label">PRO PLAN</span>
        <h2 class="k-pricing-cta-title">Sem limites. Sem espera.</h2>
        <p class="k-pricing-cta-sub">Rode quantos cenários precisar, com o máximo de agentes, e acesse a suíte completa de relatórios e modo de interação. Tudo liberado no Pro.</p>
        <div class="k-pricing-cta-btns">
          <router-link to="/pricing" class="k-btn-run">
            Upgrade para Pro por R$34,99/mês
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
          </router-link>
        </div>
      </div>
    </section>

    <!-- CTA FINAL: iniciar simulação -->
    <section class="k-launch-section">
      <div class="k-launch-inner">
        <span class="k-label">COMECE AGORA</span>
        <h2 class="k-launch-title">Descreva o cenário.<br><span class="k-launch-dim">Esteja um passo à frente.</span></h2>
        <p class="k-launch-sub">Não importa o que você precisa prever: reação de mercado, comportamento de público, impacto de uma decisão. Descreva em linguagem natural, anexe contexto e rode. O resultado chega em ~30 minutos.</p>
        <div class="k-launch-btns">
          <router-link v-if="isAuthenticated" to="/simular" class="k-btn-run">
            Abrir console de simulação
            <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
          </router-link>
          <template v-else>
            <router-link to="/register" class="k-btn-run">
              Criar conta grátis
              <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
            </router-link>
            <router-link to="/login" class="k-btn-secondary">Entrar</router-link>
          </template>
        </div>
        <!-- Mini spec strip -->
        <div class="k-launch-spec">
          <span>2 plataformas em paralelo</span>
          <span class="k-spec-dot">·</span>
          <span>72h de comportamento social simulado</span>
          <span class="k-spec-dot">·</span>
          <span>~30 min de execução real</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { useSubscription } from '../composables/useSubscription'
import { useTheme } from '../composables/useTheme'
import AppLogo from '../components/AppLogo.vue'

const router = useRouter()
const heroCanvas = ref(null)

const { isAuthenticated, userEmail, signOut } = useAuth()
const { isSubscribed, planName, fetchSubscription, manageSubscription } = useSubscription()
const { isDark, toggleTheme } = useTheme()

const userInitials = computed(() => {
  if (!userEmail.value) return '?'
  return userEmail.value.slice(0, 2).toUpperCase()
})

const handleSignOut = async () => {
  await signOut()
}

onMounted(() => {
  if (isAuthenticated.value) fetchSubscription()
})

const capabilities = [
  {
    id: '01',
    title: 'Teste hipóteses sem riscos reais',
    desc: 'Ensaios clínicos, testes de estresse em engenharia, decisões de política. Execute em simulação antes de se comprometer com o mundo real.',
    iconViewBox: '0 0 24 24',
    iconPath: '<path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2v-4M9 21H5a2 2 0 0 1-2-2v-4m0 0h18"/>'
  },
  {
    id: '02',
    title: 'Execute cenários "e se"',
    desc: 'Mude uma variável e observe os efeitos em cascata em todo o sistema, dos agentes individuais até os resultados macro.',
    iconViewBox: '0 0 24 24',
    iconPath: '<circle cx="6" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7M6 9v3a2 2 0 0 0 2 2h3"/>'
  },
  {
    id: '03',
    title: 'Otimize sistemas em escala',
    desc: 'Simule milhares de configurações em paralelo para encontrar a melhor estratégia. Muito mais rápido do que qualquer ciclo de iteração real.',
    iconViewBox: '0 0 24 24',
    iconPath: '<path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/>'
  },
  {
    id: '04',
    title: 'Preveja estados futuros',
    desc: 'Modele como um mercado, doença ou clima pode evoluir. Obtenha previsões probabilísticas baseadas no comportamento real das entidades.',
    iconViewBox: '0 0 24 24',
    iconPath: '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>'
  },
]

const trustStats = [
  { value: '2', label: 'Plataformas em paralelo', note: 'Feed público + Comunidade de tópicos, simultaneamente' },
  { value: '72h', label: 'De vida social simulada', note: '3 dias de posts, reações, tendências e debates entre agentes, por execução' },
  { value: '~30min', label: 'Tempo real de execução', note: 'Para rodar 72h completas de dinâmica social comprimida' },
  { value: '60:1', label: 'Compressão temporal', note: '1 minuto de cômputo equivale a 60 minutos de atividade social' },
]

const trustArticles = [
  {
    id: 'a1',
    tag: 'EMBASAMENTO CIENTÍFICO',
    title: 'Modelos baseados em agentes superam previsões tradicionais',
    desc: 'Estudos em ciência social computacional mostram que simulações multiagente capturam comportamentos emergentes que modelos de regressão e históricos não detectam.',
    graphic: {
      viewBox: '0 0 40 40',
      path: '<polyline points="4,32 12,20 20,24 28,10 36,14" stroke="#BDEBB5" stroke-width="1.8" fill="none"/><circle cx="12" cy="20" r="2" fill="#BDEBB5"/><circle cx="20" cy="24" r="2" fill="#BDEBB5"/><circle cx="28" cy="10" r="2" fill="#BDEBB5"/>'
    }
  },
  {
    id: 'a2',
    tag: 'COMPROVADO NA PRÁTICA',
    title: 'Usado por defesa, farmacêutica e instituições financeiras',
    desc: 'O suporte a decisões baseado em simulação é prática padrão em domínios de alto risco onde erros são irreversíveis e experimentos reais são impossíveis.',
    graphic: {
      viewBox: '0 0 40 40',
      path: '<rect x="4" y="24" width="6" height="12" rx="1" fill="rgba(189,235,181,0.15)" stroke="#BDEBB5"/><rect x="14" y="16" width="6" height="20" rx="1" fill="rgba(189,235,181,0.15)" stroke="#BDEBB5"/><rect x="24" y="8" width="6" height="28" rx="1" fill="rgba(189,235,181,0.15)" stroke="#BDEBB5"/>'
    }
  },
  {
    id: 'a3',
    tag: 'COMPRESSÃO DE TEMPO',
    title: 'Comprima anos de incerteza em minutos',
    desc: 'Um piloto de política real leva 18 meses. Uma simulação roda o mesmo cenário com dezenas de arquétipos de agentes em ~30 minutos de cômputo — 3 dias de dinâmica social comprimidos.',
    graphic: {
      viewBox: '0 0 40 40',
      path: '<circle cx="20" cy="20" r="14" stroke="rgba(255,255,255,0.12)"/><circle cx="20" cy="20" r="14" stroke="#BDEBB5" stroke-dasharray="44 44" stroke-dashoffset="22"/><line x1="20" y1="20" x2="20" y2="8" stroke="#BDEBB5" stroke-width="1.5" stroke-linecap="round"/><line x1="20" y1="20" x2="28" y2="24" stroke="rgba(255,255,255,0.4)" stroke-width="1.2" stroke-linecap="round"/><circle cx="20" cy="20" r="2" fill="#BDEBB5"/>'
    }
  },
]

const profileOpen = ref(false)

// v-click-outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => { if (!el.contains(e.target)) binding.value(e) }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) { document.removeEventListener('click', el._clickOutside) }
}

const compareRows = [
  { feature: 'Simulações / mês', free: '2', pro: '<span class="k-pro-hl">Ilimitadas</span>' },
  { feature: 'Agentes por execução', free: '50', pro: '<span class="k-pro-hl">500+</span>' },
  { feature: 'Suite de relatórios', free: 'Básico', pro: '<span class="k-pro-hl">Completo</span>' },
  { feature: 'Modo de interação', free: '✗', pro: '<span class="k-pro-hl">✓</span>' },
  { feature: 'Mapeamento de cenário', free: '✗', pro: '<span class="k-pro-hl">✓</span>' },
  { feature: 'Suporte prioritário', free: '✗', pro: '<span class="k-pro-hl">✓</span>' },
]


const activeUC = ref(null)

const useCases = [
  {
    id: 'marketing',
    sector: 'MARKETING',
    headline: 'Saiba como seu público vai reagir antes de lançar.',
    body: 'Simule campanhas em milhares de arquétipos de consumidores. Preveja propagação de narrativas, mudanças de sentimento e reações negativas — antes de gastar um centavo em mídia.',
    tags: ['Comportamento do consumidor', 'Previsão de sentimento', 'Teste de campanha', 'Propagação de narrativa'],
    icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#BDEBB5" stroke-width="1.4"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'
  },
  {
    id: 'finance',
    sector: 'FINANÇAS',
    headline: 'Modele o comportamento do mercado com precisão de agente.',
    body: 'Execute simulações macro e micro de comportamento de investidores, choques regulatórios e movimentos competitivos. Previsões probabilísticas baseadas em dinâmicas reais, não em médias históricas.',
    tags: ['Comportamento de mercado', 'Reação de investidores', 'Teste de estresse', 'Modelagem de risco'],
    icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#BDEBB5" stroke-width="1.4"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/><path d="M2 20h20"/></svg>'
  },
  {
    id: 'government',
    sector: 'GOVERNO & POLÍTICA',
    headline: 'Teste decisões antes de chegarem ao mundo real.',
    body: 'Simule como populações respondem a legislações, mudanças de infraestrutura ou comunicações de crise. Identifique consequências não intencionais e otimize o impacto antes da implementação.',
    tags: ['Simulação de políticas', 'Resposta da população', 'Modelagem de crise', 'Sentimento público'],
    icon: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#BDEBB5" stroke-width="1.4"><path d="M3 22V11l9-9 9 9v11"/><path d="M9 22V16h6v6"/></svg>'
  },
]

const howSteps = [
  {
    title: 'Descreva seu cenário',
    desc: 'Carregue qualquer documento ou escreva livremente: notícia, pesquisa, plano de produto, rascunho de política, dado de mercado. O motor extrai entidades, atores e contexto.',
    icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.4"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>'
  },
  {
    title: 'Defina o que quer prever',
    desc: 'Em linguagem natural, diga o que te interessa saber. O motor configura os objetivos dos agentes, as variáveis do ambiente e os modelos de comportamento, sem precisar de código.',
    icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.4"><circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/></svg>'
  },
  {
    title: 'Agentes simulam 72h de comportamento',
    desc: 'Milhares de agentes autônomos, com memória, vieses e personalidades distintas, interagem em dois ambientes paralelos por 3 dias simulados. Tudo em ~30 minutos reais.',
    icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.4"><circle cx="8" cy="8" r="3"/><circle cx="16" cy="8" r="3"/><circle cx="12" cy="16" r="3"/><line x1="8" y1="11" x2="12" y2="13"/><line x1="16" y1="11" x2="12" y2="13"/></svg>'
  },
  {
    title: 'Receba a inteligência, tome a decisão',
    desc: 'Um relatório completo com atribuição de influência, análise em cascata, narrativas emergentes e recomendações concretas para você agir antes dos outros.',
    icon: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.4"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>'
  },
]

let raf = null
onMounted(() => {
  const c = heroCanvas.value
  if (!c) return
  const resize = () => { c.width = c.offsetWidth; c.height = c.offsetHeight }
  resize()
  window.addEventListener('resize', resize)
  const pts = Array.from({ length: 80 }, () => ({
    x: Math.random(), y: Math.random(),
    vx: (Math.random() - 0.5) * 0.0003,
    vy: (Math.random() - 0.5) * 0.0003,
    r: Math.random() * 0.8 + 0.2
  }))
  const draw = () => {
    if (!c) return
    const ctx = c.getContext('2d')
    const W = c.width, H = c.height
    const dark = document.documentElement.getAttribute('data-theme') === 'dark'
    ctx.clearRect(0, 0, W, H)
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy
      if (p.x < 0) p.x = 1; if (p.x > 1) p.x = 0
      if (p.y < 0) p.y = 1; if (p.y > 1) p.y = 0
    })
    pts.forEach((a, i) => {
      pts.forEach((b, j) => {
        if (j <= i) return
        const dx = (a.x - b.x) * W, dy = (a.y - b.y) * H
        const d = Math.sqrt(dx * dx + dy * dy)
        if (d > 140) return
        const alpha = (1 - d / 140) * (dark ? 0.02 : 0.025)
        ctx.beginPath(); ctx.moveTo(a.x * W, a.y * H); ctx.lineTo(b.x * W, b.y * H)
        ctx.strokeStyle = dark ? `rgba(255,255,255,${alpha})` : `rgba(0,0,0,${alpha})`
        ctx.lineWidth = 1; ctx.stroke()
      })
      ctx.beginPath(); ctx.arc(a.x * W, a.y * H, a.r, 0, Math.PI * 2)
      ctx.fillStyle = dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.05)'; ctx.fill()
    })
    raf = requestAnimationFrame(draw)
  }
  draw()
})
onUnmounted(() => { if (raf) cancelAnimationFrame(raf) })
</script>

<style scoped>

.k {
  min-height: 100vh;
  overflow-x: hidden;
  background:
    radial-gradient(ellipse 120% 55% at 50% -5%, var(--green-dim) 0%, transparent 58%),
    radial-gradient(ellipse 60% 30% at 80% 110%, var(--green-dim) 0%, transparent 50%),
    var(--bg);
  color: var(--text);
  font-family: var(--font);
  --page-x: 80px; --section-y: 112px;
}

/* NAV */
.k-nav {
  position: sticky; top: 0; z-index: 100;
  height: 56px; border-bottom: 1px solid var(--border);
  background: var(--nav-bg); backdrop-filter: blur(24px); box-shadow: 0 1px 0 var(--border);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 var(--page-x);
}
.k-brand { display: flex; align-items: center; cursor: pointer; }
.k-logo-img { height: 34px; width: auto; display: block; }
.k-nav-right { display: flex; align-items: center; gap: 20px; }

.k-status {
  display: flex; align-items: center; gap: 7px;
  font-family: var(--mono); font-size: 0.66rem;
  letter-spacing: 0.06em; color: rgba(255,255,255,0.3);
}
.k-status-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #BDEBB5; box-shadow: 0 0 6px #BDEBB5;
  animation: pulse 2.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:.8} 50%{opacity:.3} }

.k-nav-link {
  font-family: var(--font); font-size: 0.78rem; letter-spacing: 0.03em;
  color: var(--text2); text-decoration: none; transition: color 0.15s;
}
.k-nav-link:hover { color: var(--text); }

.k-nav-btn-outline {
  font-family: var(--font); font-size: 0.78rem;
  color: var(--text2); background: transparent;
  border: 1px solid var(--border2); border-radius: 6px;
  padding: 6px 16px; cursor: pointer; text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}
.k-nav-btn-outline:hover { border-color: var(--text2); color: var(--text); }

.k-nav-btn {
  font-family: var(--font); font-size: 0.78rem;
  background: var(--surface-2); color: var(--text2);
  border: 1px solid var(--border2); border-radius: 6px;
  padding: 6px 16px; cursor: pointer; transition: all 0.15s;
}
.k-nav-btn:hover { background: var(--surface-3); color: var(--text); }

.k-nav-upgrade {
  display: inline-flex; align-items: center; gap: 5px;
  font-family: var(--font); font-size: 0.64rem; font-weight: 600;
  color: #a78bfa; text-decoration: none;
  background: rgba(167,139,250,0.07); border: 1px solid rgba(167,139,250,0.2);
  border-radius: 100px; padding: 5px 13px; transition: all 0.2s; white-space: nowrap;
  letter-spacing: 0.04em;
}
.k-nav-upgrade:hover { background: rgba(167,139,250,0.14); border-color: rgba(167,139,250,0.38); color: #c4b5fd; }
.k-nav-sparkle { font-size: 0.7rem; }
.k-nav-upgrade:hover { background: var(--green-dim); opacity: 0.85; }

.k-nav-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--green-dim); color: var(--green-text);
  font-size: 10px; font-weight: 700; letter-spacing: 0.05em;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 1px solid var(--green-border);
  transition: all 0.15s;
}
.k-nav-avatar:hover { opacity: 0.8; }

/* SYSTEM STATUS BADGE */
.k-sys-badge {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.14em;
  color: rgba(189,235,181,0.55);
  background: rgba(189,235,181,0.04);
  border: 1px solid rgba(189,235,181,0.13);
  padding: 6px 13px; border-radius: 20px;
  margin-bottom: 22px;
}
.k-sys-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #BDEBB5; box-shadow: 0 0 8px rgba(189,235,181,0.8);
  animation: pulse 2.4s ease-in-out infinite;
  flex-shrink: 0;
}

/* HERO */
.k-hero {
  min-height: 96vh; display: grid;
  grid-template-columns: 1fr 480px; align-items: center;
  padding: 80px var(--page-x); gap: 60px; position: relative; overflow: hidden;
}
.k-canvas { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
.k-hero-body { position: relative; z-index: 1; max-width: 580px; }
.k-title { font-size: 3.6rem; font-weight: 800; line-height: 1.12; letter-spacing: -0.04em; margin-bottom: 24px; }
.k-title-dim { color: var(--text3); }
.k-title-glow {
  background: linear-gradient(100deg, var(--text) 30%, var(--green) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.k-subtitle { font-size: 0.88rem; line-height: 1.85; color: var(--text2); max-width: 480px; margin-bottom: 40px; }
.k-hero-cta { display: flex; align-items: center; gap: 14px; }
.k-btn-run {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--green-bright); color: #000; border: none; border-radius: 8px;
  padding: 12px 24px; font-family: var(--font); font-size: 0.82rem;
  font-weight: 700; cursor: pointer;
  text-decoration: none; transition: opacity 0.15s, transform 0.1s;
  box-shadow: var(--shadow-sm);
}
.k-btn-run:hover { opacity: 0.88; transform: translateY(-1px); }
.k-btn-secondary {
  display: inline-flex; align-items: center;
  color: var(--text2); font-family: var(--font); font-size: 0.8rem;
  text-decoration: none; transition: color 0.15s, border-color 0.15s;
  border: 1px solid var(--border2); border-radius: 8px; padding: 12px 18px;
}
.k-btn-secondary:hover { color: var(--text); border-color: var(--text2); }

.k-brain-image {
  position: relative; z-index: 1; width: 100%; max-width: 480px;
  border-radius: 16px; opacity: 0.85;
  mix-blend-mode: screen;
  background: transparent;
}
@media (max-width: 1100px) {
  .k-brain-image { display: none !important; }
}

/* CAPABILITIES */


/* TRUST */


/* PRICING CTA */
.k-pricing-cta {
  border-top: 1px solid var(--border);
  padding: var(--section-y) var(--page-x);
}
.k-pricing-cta-inner {
  max-width: 560px; margin: 0 auto; text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 16px;
}
.k-pricing-cta-title { font-size: 2rem; font-weight: 700; color: var(--text); }
.k-pricing-cta-sub { font-size: 0.78rem; color: var(--text2); line-height: 1.7; }
.k-pricing-cta-btns { display: flex; align-items: center; gap: 14px; margin-top: 8px; }

/* LAUNCH SECTION */
.k-launch-section {
  padding: var(--section-y) var(--page-x);
  border-top: 1px solid var(--border);
}
.k-launch-inner {
  max-width: 640px; margin: 0 auto; text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 20px;
}
.k-launch-title { font-size: 2.2rem; font-weight: 700; line-height: 1.25; margin: 0; color: var(--text); }
.k-launch-dim { color: var(--text3); }
.k-launch-sub { font-size: 0.78rem; color: var(--text2); line-height: 1.75; max-width: 480px; margin: 0; }
.k-launch-btns { display: flex; align-items: center; gap: 14px; margin-top: 4px; }
.k-launch-spec {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap; justify-content: center;
  font-size: 0.6rem; color: var(--text3); letter-spacing: 0.06em; margin-top: 4px;
}
.k-spec-dot { color: var(--text3); opacity: 0.5; }

/* RESPONSIVE */
@media (max-width: 1100px) {
  .k { --page-x: 40px; --section-y: 80px; }
  .k-hero { grid-template-columns: 1fr; padding: 72px 40px 56px; min-height: auto; }
  .k-brain-image { display: none !important; }
  .k-cap-grid { grid-template-columns: 1fr 1fr; row-gap: 36px; }
  .k-trust-stats { grid-template-columns: repeat(2, 1fr); }
  .k-trust-articles { grid-template-columns: 1fr; gap: 40px; }
  .k-title { font-size: 2.8rem; }
}

@media (max-width: 640px) {
  .k { --page-x: 22px; --section-y: 56px; }

  /* Nav */
  .k-nav { padding: 0 20px; }
  .k-logo-img { height: 28px; }
  .k-nav-right { gap: 12px; }
  .k-status { display: none; }
  .k-nav-hide-mobile { display: none !important; }
  .k-nav-btn-outline { padding: 6px 14px; font-size: 0.76rem; }

  /* Hero — tall e impactante no mobile */
  .k-hero { padding: 56px 22px 52px; min-height: auto; gap: 0; }
  .k-title { font-size: 2.5rem; line-height: 1.12; margin-bottom: 20px; letter-spacing: -0.025em; }
  .k-subtitle { font-size: 0.84rem; line-height: 1.75; margin-bottom: 32px; max-width: 100%; }
  .k-sys-badge { font-size: 0.55rem; padding: 5px 10px; margin-bottom: 18px; }

  /* Botões empilhados em coluna */
  .k-hero-cta { flex-direction: column !important; align-items: stretch !important; gap: 10px; }
  .k-btn-run { width: 100%; justify-content: center; padding: 14px 24px; font-size: 0.88rem; }
  .k-btn-secondary { width: 100%; justify-content: center; padding: 13px 24px; font-size: 0.84rem; }

  /* Sections */
  .k-uc-grid { grid-template-columns: 1fr !important; gap: 12px; }
  .k-how-steps { grid-template-columns: 1fr !important; gap: 20px; }
  .k-trust-stats { grid-template-columns: 1fr 1fr; gap: 16px; }
  .k-stat-value { font-size: 1.6rem; }
  .k-stat-label { font-size: 0.65rem; }

  /* Compare table */
  .compare-table { font-size: 0.72rem; }

  /* Revenue CTA */
  .k-revenue-inner { flex-direction: column !important; gap: 32px; }
  .k-revenue-left, .k-revenue-right { max-width: 100% !important; }
  .k-revenue-cta-row { flex-direction: column; align-items: stretch; gap: 10px; }
  .k-revenue-cta-row .k-btn-run,
  .k-revenue-cta-row .k-btn-secondary { width: 100%; justify-content: center; }

  /* Launch / Pricing CTA */
  .k-launch-btns { flex-direction: column !important; align-items: stretch !important; gap: 10px; }
  .k-launch-btns .k-btn-run,
  .k-launch-btns .k-btn-secondary { width: 100%; justify-content: center; }
  .k-launch-title { font-size: 1.8rem; }
  .k-pricing-cta-btns { flex-direction: column !important; align-items: stretch !important; gap: 10px; }
  .k-pricing-cta-btns .k-btn-run,
  .k-pricing-cta-btns .k-btn-secondary { width: 100%; justify-content: center; }

  /* Footer */
  .k-footer-inner { flex-direction: column !important; gap: 20px; align-items: flex-start; }
  .k-footer-links { flex-wrap: wrap; gap: 12px; }
}

@media (min-width: 641px) {
  .k-nav-show-mobile { display: none !important; }
}


/* Profile dropdown */
.k-profile-wrap { position: relative; }

.k-nav-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--green-dim); color: var(--green-text);
  font-size: 10px; font-weight: 700; letter-spacing: 0.05em;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 1px solid var(--green-border);
  transition: all 0.15s; user-select: none;
}
.k-nav-avatar:hover { opacity: 0.8; }

.k-profile-dropdown {
  position: absolute; right: 0; top: calc(100% + 10px);
  width: 230px; background: var(--bg2);
  border: 1px solid var(--border2); border-radius: 8px;
  box-shadow: var(--shadow-md);
  z-index: 1000; overflow: hidden;
}

.k-profile-email {
  padding: 13px 16px; font-size: 11px;
  color: var(--text2);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.k-profile-divider { height: 1px; background: var(--border); }

.k-profile-plan {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px; font-size: 12px; color: var(--text2);
}
.k-plan-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
}
.k-plan-dot.active { background: var(--green); box-shadow: 0 0 6px var(--green); }
.k-plan-dot.free { background: var(--text3); }

.k-plan-upgrade-chip {
  margin-left: auto; font-size: 10px; padding: 2px 8px;
  background: var(--green-dim); color: var(--green-text);
  border: 1px solid var(--green-border); border-radius: 3px;
  text-decoration: none; letter-spacing: 0.5px; transition: all 0.15s;
}
.k-plan-upgrade-chip:hover { opacity: 0.8; }

.k-profile-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; font-size: 12px; color: var(--text2);
  text-decoration: none; cursor: pointer; transition: all 0.15s;
  background: none; border: none; width: 100%; font-family: var(--mono);
  text-align: left;
}
.k-profile-item:hover { background: var(--surface-h); color: var(--text); }

.k-profile-signout { color: var(--red); opacity: 0.65; }
.k-profile-signout:hover { background: rgba(239,68,68,0.06); opacity: 1; }

.profile-drop-enter-active, .profile-drop-leave-active { transition: opacity 0.15s, transform 0.15s; }
.profile-drop-enter-from, .profile-drop-leave-to { opacity: 0; transform: translateY(-6px); }

/* Remove old k-status styles if any */
.k-status { display: none; }
.k-status-dot { display: none; }

/* REVENUE CTA */
.k-revenue-cta {
  padding: var(--section-y) var(--page-x);
  border-top: 1px solid var(--border);
}
.k-revenue-inner {
  display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: start;
}
.k-revenue-left { display: flex; flex-direction: column; gap: 28px; }
.k-revenue-title { font-size: 2rem; font-weight: 700; line-height: 1.3; color: var(--text); }
.k-revenue-sub { font-size: 0.78rem; color: var(--text2); line-height: 1.8; }

.k-revenue-features { display: flex; flex-direction: column; gap: 18px; }
.k-rf-item { display: flex; gap: 14px; align-items: flex-start; }
.k-rf-icon {
  width: 24px; height: 24px; border-radius: 50%;
  background: var(--green-dim); border: 1px solid var(--green-border);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px;
}
.k-rf-icon svg { stroke: var(--green) !important; }
.k-rf-title { font-size: 0.76rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.k-rf-desc { font-size: 0.7rem; color: var(--text2); line-height: 1.6; }

.k-revenue-cta-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.k-revenue-cancel { font-size: 0.68rem; color: var(--text3); }

/* Compare card */
.k-compare-card {
  background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden;
}
.k-compare-header {
  display: grid; grid-template-columns: 1fr 80px 80px;
  padding: 12px 20px; background: var(--surface-2);
  border-bottom: 1px solid var(--border);
}
.k-compare-col-label { font-size: 0.58rem; font-weight: 700; letter-spacing: 0.12em; color: var(--text3); text-align: center; }
.k-compare-col-label:first-child { text-align: left; }
.k-compare-col-pro { color: var(--green-text); }

.k-compare-row {
  display: grid; grid-template-columns: 1fr 80px 80px;
  padding: 11px 20px; border-bottom: 1px solid var(--border);
  transition: background 0.12s;
}
.k-compare-row:last-child { border-bottom: none; }
.k-compare-row:hover { background: var(--surface-h); }
.k-compare-feature { font-size: 0.72rem; color: var(--text2); }
.k-compare-val { font-size: 0.72rem; color: var(--text3); text-align: center; }
.k-compare-val-pro { color: var(--green-text); }
.k-compare-val-pro :deep(span) { color: var(--green-text) !important; }

@media (max-width: 1100px) {
  .k-revenue-inner { grid-template-columns: 1fr; gap: 40px; }
}

/* ─── USE CASES ─── */
.k-usecases {
  padding: var(--section-y) var(--page-x);
  border-top: 1px solid var(--border);
}
.k-uc-header { margin-bottom: 52px; max-width: 560px; }
.k-uc-title { font-size: 2.2rem; font-weight: 700; line-height: 1.25; margin: 12px 0 10px; color: var(--text); }
.k-uc-sub { font-size: 0.82rem; color: var(--text2); line-height: 1.7; }

.k-uc-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}
.k-uc-card {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 32px 28px;
  display: flex; flex-direction: column; gap: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  cursor: default; box-shadow: var(--shadow-sm);
}
.k-uc-card--active {
  border-color: var(--green-border);
  box-shadow: var(--shadow-md);
}
.k-uc-icon { margin-bottom: 4px; }
.k-uc-sector {
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.18em;
  color: var(--green-text);
}
.k-uc-headline {
  font-size: 0.92rem; font-weight: 600; color: var(--text);
  line-height: 1.4;
}
.k-uc-body {
  font-size: 0.75rem; color: var(--text2); line-height: 1.75; flex: 1;
}
.k-uc-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.k-uc-tag {
  font-size: 0.58rem; letter-spacing: 0.07em;
  padding: 3px 8px; border-radius: 4px;
  background: var(--surface-2); border: 1px solid var(--border);
  color: var(--text3);
}

/* ─── STATS BAND ─── */
.k-stats-band {
  display: grid; grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
}
.k-stat {
  display: flex; flex-direction: column; gap: 8px;
  padding: 44px 32px 36px;
  border-right: 1px solid var(--border);
  position: relative;
}
.k-stat:last-child { border-right: none; }
.k-stat-accent {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(to right, var(--green), transparent);
  opacity: 0.45;
}
.k-stat-value { font-size: 3.2rem; font-weight: 200; letter-spacing: -0.04em; color: var(--text); line-height: 1; }
.k-stat-label { font-size: 0.68rem; color: var(--text2); letter-spacing: 0.04em; font-weight: 500; }
.k-stat-note { font-size: 0.6rem; color: var(--text3); line-height: 1.6; max-width: 200px; }

/* ─── COMO FUNCIONA ─── */
.k-how {
  padding: var(--section-y) var(--page-x);
  border-top: 1px solid var(--border);
}
.k-how-header { margin-bottom: 56px; }
.k-how-title { font-size: 2.2rem; font-weight: 300; line-height: 1.3; margin-top: 12px; color: var(--text); }
.k-how-dim { color: var(--text3); }

.k-how-steps {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 32px;
  position: relative;
}
.k-how-steps::before { display: none; }
.k-how-step {
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px 22px;
  display: flex; flex-direction: column; gap: 14px; position: relative;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-shadow: var(--shadow-sm);
}
.k-how-step:hover {
  border-color: var(--green-border);
  box-shadow: var(--shadow-md);
}
.k-how-num {
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.12em;
  color: var(--green-text);
}
.k-how-step-icon {
  width: 44px; height: 44px; border: 1px solid var(--border2);
  border-radius: 10px; background: var(--bg3);
  display: flex; align-items: center; justify-content: center;
}
.k-how-step-title { font-size: 0.82rem; font-weight: 600; color: var(--text); line-height: 1.4; }
.k-how-step-desc { font-size: 0.73rem; color: var(--text2); line-height: 1.7; }

/* Label overline */
.k-label {
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.18em;
  color: var(--green-text); text-transform: uppercase;
}

/* Pro highlight in compare table */
.k-pro-hl { color: var(--green-text); }

/* Icon color overrides for SVGs with hardcoded stroke (v-html requires :deep) */
.k-uc-icon :deep(svg) { stroke: var(--green) !important; fill: none !important; }
.k-how-step-icon :deep(svg) { stroke: var(--text2) !important; fill: none !important; }

/* responsive additions */
@media (max-width: 1100px) {
  .k-uc-grid { grid-template-columns: 1fr; }
  .k-stats-band { grid-template-columns: repeat(2, 1fr); gap: 24px; }
  .k-stat + .k-stat { border-left: none; }
  .k-how-steps { grid-template-columns: 1fr 1fr; }
  .k-how-steps::before { display: none; }
}
@media (max-width: 640px) {
  .k-stats-band { grid-template-columns: 1fr 1fr; }
  .k-stat { padding: 20px 14px 18px; }
  .k-stat-value { font-size: clamp(1.6rem, 6.5vw, 2.2rem); letter-spacing: -0.03em; }
  .k-stat-label { font-size: 0.6rem; }
  .k-stat-note { font-size: 0.56rem; line-height: 1.5; }
  .k-how-steps { grid-template-columns: 1fr; }
}

</style>
