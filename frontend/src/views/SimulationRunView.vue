<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <AppLogo class="mv-logo" @click="router.push('/')" style="cursor:pointer" />
      </div>

      <div class="header-center">
        <span class="mv-crumb">
          <span class="mv-crumb-project">{{ projectData?.project_name || 'Simulação' }}</span>
          <span class="mv-crumb-sep">/</span>
          <span class="mv-crumb-step">Executando</span>
        </span>
      </div>

      <div class="header-right">
        <span class="mv-status" :class="statusClass">
          <span class="mv-dot"></span>{{ statusText }}
        </span>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="mv-content" :class="{ 'mobile-mode': isMobileView }">
      <!-- Mobile tab bar -->
      <div v-if="isMobileView" class="mobile-tabs">
        <button class="mtab" :class="{ active: mobileTab === 'graph' }" @click="mobileTab = 'graph'">
          <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="8" cy="8" r="2.5"/><circle cx="3" cy="4" r="1.5"/><circle cx="13" cy="4" r="1.5"/><circle cx="3" cy="12" r="1.5"/><circle cx="13" cy="12" r="1.5"/></svg>
          Grafo
        </button>
        <button class="mtab" :class="{ active: mobileTab === 'sim' }" @click="mobileTab = 'sim'">
          <svg viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="1.8"><polygon points="4 2 12 8 4 14"/></svg>
          Simulação
          <span v-if="isSimulating" class="mtab-pulse"></span>
        </button>
      </div>

      <!-- Desktop: left console panel (Step3) -->
      <div v-if="!isMobileView" class="mv-panel console">
        <div class="mv-panel-content">
          <Step3Simulation
            :simulationId="currentSimulationId"
            :maxRounds="maxRounds"
            :minutesPerRound="minutesPerRound"
            :projectData="projectData"
            :graphData="graphData"
            :systemLogs="systemLogs"
            @go-back="handleGoBack"
            @next-step="handleNextStep"
            @add-log="addLog"
            @update-status="updateStatus"
          />
        </div>
      </div>

      <!-- Graph canvas (right on desktop, tab on mobile) -->
      <div
        class="mv-panel canvas"
        :class="{ 'mobile-hidden': isMobileView && mobileTab !== 'graph' }"
      >
        <GraphPanel
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="3"
          :isSimulating="isSimulating"
          :agentProfiles="agentProfiles"
          @refresh="refreshGraph"
        />
      </div>

      <!-- Mobile: simulation full-screen tab -->
      <div
        v-if="isMobileView"
        class="mv-panel mobile-sim-panel"
        :class="{ 'mobile-hidden': mobileTab !== 'sim' }"
      >
        <Step3Simulation
          :simulationId="currentSimulationId"
          :maxRounds="maxRounds"
          :minutesPerRound="minutesPerRound"
          :projectData="projectData"
          :graphData="graphData"
          :systemLogs="systemLogs"
          @go-back="handleGoBack"
          @next-step="handleNextStep"
          @add-log="addLog"
          @update-status="updateStatus"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step3Simulation from '../components/Step3Simulation.vue'
import AppLogo from '../components/AppLogo.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation, getSimulationConfig, stopSimulation, closeSimulationEnv, getEnvStatus, getSimulationProfiles } from '../api/simulation'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  simulationId: String
})

// Layout State
const isMobileView = ref(false)
const mobileTab = ref('graph')

const handleViewResize = () => { isMobileView.value = window.innerWidth < 768 }

// Data State
const currentSimulationId = ref(route.params.simulationId)
// maxRounds vem do query param
const maxRounds = ref(route.query.maxRounds ? parseInt(route.query.maxRounds) : null)
const minutesPerRound = ref(30)
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const agentProfiles = ref([])
const systemLogs = ref([])
const currentStatus = ref('processing') // processing | completed | error


// --- Status Computed ---
const statusClass = computed(() => {
  return currentStatus.value
})

const statusText = computed(() => {
  if (currentStatus.value === 'error') return 'Erro'
  if (currentStatus.value === 'completed') return 'Concluído'
  return 'Rodando'
})

const isSimulating = computed(() => currentStatus.value === 'processing')

// Auto-switch to sim tab on mobile when simulation is running
watch(isSimulating, (val) => {
  if (val && isMobileView.value) mobileTab.value = 'sim'
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 200) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

const handleGoBack = async () => {
  // Encerrar simulacao antes de retornar ao Step 2
  addLog('Preparando retorno para Etapa 2, encerrando simulacao...')
  

  stopGraphRefresh()
  
  try {

    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog('Encerrando ambiente de simulacao...')
      try {
        await closeSimulationEnv({ 
          simulation_id: currentSimulationId.value,
          timeout: 10
        })
        addLog('Ambiente encerrado com sucesso')
      } catch (closeErr) {
        addLog('Falha ao encerrar, forcando parada...')
        try {
          await stopSimulation({ simulation_id: currentSimulationId.value })
          addLog('Simulacao encerrada forcadamente')
        } catch (stopErr) {
          addLog(`Erro ao forcar parada: ${stopErr.message}`)
        }
      }
    } else {

      if (isSimulating.value) {
      addLog('Encerrando processo de simulacao...')
        try {
          await stopSimulation({ simulation_id: currentSimulationId.value })
        addLog('Simulacao encerrada')
        } catch (err) {
        addLog(`Erro ao encerrar: ${err.message}`)
        }
      }
    }
  } catch (err) {
    addLog(`Erro ao verificar status: ${err.message}`)
  }
  

  router.push({ name: 'Simulation', params: { simulationId: currentSimulationId.value } })
}

const handleNextStep = () => {


  addLog('Avancando para Etapa 4: Gerar Relatorio')
}

// --- Data Logic ---
const loadSimulationData = async () => {
  try {
    addLog(`Carregando simulacao: ${currentSimulationId.value}`)
    

    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data
      

      try {
        const configRes = await getSimulationConfig(currentSimulationId.value)
        if (configRes.success && configRes.data?.time_config?.minutes_per_round) {
          minutesPerRound.value = configRes.data.time_config.minutes_per_round
          addLog(`Config: ${minutesPerRound.value} min/rodada`)
        }
      } catch (configErr) {
        addLog(`Usando configuracao padrao: ${minutesPerRound.value} min/rodada`)
      }
      

      if (simData.project_id) {
        const projRes = await getProject(simData.project_id)
        if (projRes.success && projRes.data) {
          projectData.value = projRes.data
          addLog(`Projeto: ${projRes.data.project_id}`)
          

          if (projRes.data.graph_id) {
            await loadGraph(projRes.data.graph_id)
          }
        }
      }
      // Load agent profiles for graph node enrichment
      loadAgentProfiles()
    } else {
      addLog(`Falha: ${simRes.error || 'erro desconhecido'}`)
    }
  } catch (err) {
    addLog(`Erro: ${err.message}`)
  }
}

const loadAgentProfiles = async () => {
  try {
    const [twitterRes, redditRes] = await Promise.allSettled([
      getSimulationProfiles(currentSimulationId.value, 'twitter'),
      getSimulationProfiles(currentSimulationId.value, 'reddit')
    ])
    const combined = []
    if (twitterRes.status === 'fulfilled' && twitterRes.value?.success) {
      combined.push(...(twitterRes.value.data || []))
    }
    if (redditRes.status === 'fulfilled' && redditRes.value?.success) {
      combined.push(...(redditRes.value.data || []))
    }
    if (combined.length > 0) agentProfiles.value = combined
  } catch (err) {
    // profiles are optional
  }
}

const loadGraph = async (graphId) => {


  if (!isSimulating.value) {
    graphLoading.value = true
  }
  
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      if (!isSimulating.value) {
        addLog('Graph data loaded successfully')
      }
    }
  } catch (err) {
    addLog(`Failed to load graph: ${err.message}`)
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

// --- Auto Refresh Logic ---
let graphRefreshTimer = null

const startGraphRefresh = () => {
  if (graphRefreshTimer) return
  addLog('Enable real-time graph refresh (30s)')

  graphRefreshTimer = setInterval(refreshGraph, 30000)
}

const stopGraphRefresh = () => {
  if (graphRefreshTimer) {
    clearInterval(graphRefreshTimer)
    graphRefreshTimer = null
    addLog('Stop real-time graph refresh')
  }
}

watch(isSimulating, (newValue) => {
  if (newValue) {
    startGraphRefresh()
  } else {
    stopGraphRefresh()
  }
}, { immediate: true })

onMounted(() => {
  isMobileView.value = window.innerWidth < 768
  window.addEventListener('resize', handleViewResize)
  addLog('SimulationRunView initialized')
  if (maxRounds.value) {
    addLog('Custom rounds: ' + maxRounds.value)
  }
  loadSimulationData()
})

onUnmounted(() => {
  stopGraphRefresh()
  window.removeEventListener("resize", handleViewResize)
})
</script>

<style scoped>
.main-view {
  height: 100vh; display: flex; flex-direction: column;
  background: var(--bg); overflow: hidden;
  font-family: var(--font);
}
.app-header {
  flex-shrink: 0; height: 52px;
  border-bottom: 1px solid var(--border);
  background: var(--nav-bg); backdrop-filter: blur(16px);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; position: relative; z-index: 10;
}
.mv-logo { height: 32px; width: auto; cursor: pointer; opacity: 0.9; transition: opacity 0.12s; }
.mv-logo:hover { opacity: 1; }
.header-center { flex: 1; display: flex; align-items: center; justify-content: center; }
.header-right { display: flex; align-items: center; gap: 14px; }

/* ── BREADCRUMB ── */
.mv-crumb { display: flex; align-items: center; gap: 8px; }
.mv-crumb-project {
  font-size: 0.72rem; font-weight: 600; color: var(--text);
  max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.mv-crumb-sep { color: var(--border2); font-size: 0.72rem; }
.mv-crumb-step { font-size: 0.72rem; color: var(--text3); }

.mv-status { display: flex; align-items: center; gap: 6px; font-size: 0.64rem; color: var(--text2); letter-spacing: 0.06em; }
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text3); }
.mv-status.processing .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.completed .mv-dot { background: var(--green); }
.mv-status.error .mv-dot { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.mv-content { flex: 1; display: flex; overflow: hidden; }
.mv-panel { height: 100%; overflow: hidden; }

.mv-panel.console {
  width: 400px; min-width: 360px; flex-shrink: 0;
  background: var(--bg);
  border-right: 1px solid var(--border);
}
.mv-panel.canvas { flex: 1; min-width: 0; }
.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }

/* ── MOBILE LAYOUT ── */
.mv-content.mobile-mode {
  flex-direction: column;
  position: relative;
}
.mv-content.mobile-mode .mv-panel.canvas {
  width: 100% !important;
  height: calc(100% - 52px);
  border-right: none;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.mv-panel.mobile-hidden { display: none !important; }
.mv-panel.mobile-sim-panel {
  width: 100%;
  height: calc(100% - 52px);
  overflow: hidden;
  flex-shrink: 0;
}

/* Mobile tab bar */
.mobile-tabs {
  display: flex;
  height: 52px;
  border-bottom: 1px solid var(--border);
  background: var(--nav-bg);
  backdrop-filter: blur(16px);
  flex-shrink: 0;
  order: -1;
}
.mtab {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  background: none; border: none; border-bottom: 2px solid transparent;
  color: var(--text3); font-family: var(--font); font-size: 12px;
  cursor: pointer; transition: all 0.15s; position: relative;
}
.mtab.active {
  color: var(--text);
  border-bottom-color: var(--green);
}
.mtab-pulse {
  position: absolute;
  top: 10px; right: calc(50% - 28px);
  width: 5px; height: 5px; border-radius: 50%;
  background: #3b82f6;
  animation: blink 1.2s infinite;
}

@media (min-width: 768px) {
  .mobile-tabs { display: none; }
}
</style>




