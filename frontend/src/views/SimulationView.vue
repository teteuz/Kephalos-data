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
          <span class="mv-crumb-step">Configurar Ambiente</span>
        </span>
      </div>

      <div class="header-right">
        <span class="mv-status" :class="statusClass">
          <span class="mv-dot"></span>{{ statusText }}
        </span>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="mv-content">
      <div class="mv-panel console">
        <div class="mv-panel-content">
          <Step2EnvSetup
            :simulationId="currentSimulationId"
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
      <div class="mv-panel canvas">
        <GraphPanel
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="2"
          :agentProfiles="agentProfiles"
          @refresh="refreshGraph"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step2EnvSetup from '../components/Step2EnvSetup.vue'
import AppLogo from '../components/AppLogo.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation, stopSimulation, getEnvStatus, closeSimulationEnv, getSimulationProfiles } from '../api/simulation'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  simulationId: String
})

// Layout State
const isMobileView = ref(false)
const handleViewResize = () => { isMobileView.value = window.innerWidth < 768 }

// Data State
const currentSimulationId = ref(route.params.simulationId)
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
  if (currentStatus.value === 'completed') return 'Pronto'
  return 'Preparando'
})

// --- Helpers ---
const addLog = (msg) => {
  const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) + '.' + new Date().getMilliseconds().toString().padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 100) {
    systemLogs.value.shift()
  }
}

const updateStatus = (status) => {
  currentStatus.value = status
}

const handleGoBack = () => {
  // Navegar de volta ao projeto
  if (projectData.value?.project_id) {
    router.push({ name: 'Process', params: { projectId: projectData.value.project_id } })
  } else {
    router.push('/')
  }
}

const handleNextStep = (params = {}) => {
  addLog('Iniciando Etapa 3: Executar Simulacao')
  

  if (params.maxRounds) {
    addLog(`Rodadas personalizadas: ${params.maxRounds}`)
  } else {
    addLog('Usando configuracao automatica de rodadas')
  }
  

  const routeParams = {
    name: 'SimulationRun',
    params: { simulationId: currentSimulationId.value }
  }
  

  if (params.maxRounds) {
    routeParams.query = { maxRounds: params.maxRounds }
  }
  

  router.push(routeParams)
}

// --- Data Logic ---

/**
 * Verificar e encerrar simulacao em execucao
 * chamado quando usuario volta do Step 3
 */
const checkAndStopRunningSimulation = async () => {
  if (!currentSimulationId.value) return
  
  try {
    // Verificar se o ambiente de simulacao esta ativo
    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog('Encerrando ambiente de simulacao ativo...')
      
      // Tentar encerrar o ambiente com elegancia
      try {
        const closeRes = await closeSimulationEnv({ 
          simulation_id: currentSimulationId.value,
          timeout: 10
        })
        
        if (closeRes.success) {
          addLog('Ambiente de simulacao encerrado')
        } else {
          addLog(`Falha ao encerrar ambiente: ${closeRes.error || 'erro desconhecido'}`)
          // Tentar forcar parada se encerramento falhou
          await forceStopSimulation()
        }
      } catch (closeErr) {
        addLog(`Excecao ao encerrar ambiente: ${closeErr.message}`)
        // Tentar forcar parada se excecao ocorreu
        await forceStopSimulation()
      }
    } else {
      // Ambiente inativo, verificar status da simulacao
      const simRes = await getSimulation(currentSimulationId.value)
      if (simRes.success && simRes.data?.status === 'running') {
        addLog('Simulacao em execucao detectada, parando...')
        await forceStopSimulation()
      }
    }
  } catch (err) {
    // Falha na verificacao nao impede o fluxo
    console.warn('Falha ao verificar status da simulacao:', err)
  }
}

/**
 * Forccar parada da simulacao
 */
const forceStopSimulation = async () => {
  try {
    const stopRes = await stopSimulation({ simulation_id: currentSimulationId.value })
    if (stopRes.success) {
      addLog('Simulacao encerrada forcadamente')
    } else {
      addLog(`Falha ao forcar parada: ${stopRes.error || 'erro desconhecido'}`)
    }
  } catch (err) {
    addLog(`Excecao ao forcar parada: ${err.message}`)
  }
}

const loadSimulationData = async () => {
  try {
    addLog(`Carregando simulacao: ${currentSimulationId.value}`)
    
    // Buscar informacoes da simulacao
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data
      
      // Buscar informacoes do projeto
      if (simData.project_id) {
        const projRes = await getProject(simData.project_id)
        if (projRes.success && projRes.data) {
          projectData.value = projRes.data
          addLog(`Projeto carregado: ${projRes.data.project_id}`)
          
          // Buscar dados do grafo
          if (projRes.data.graph_id) {
            await loadGraph(projRes.data.graph_id)
          }
        }
      }
      // Load agent profiles for graph node enrichment
      loadAgentProfiles()
    } else {
      addLog(`Falha ao carregar simulacao: ${simRes.error || 'erro desconhecido'}`)
    }
  } catch (err) {
    addLog(`Erro ao carregar: ${err.message}`)
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
  graphLoading.value = true
  try {
    const res = await getGraphData(graphId)
    if (res.success) {
      graphData.value = res.data
      addLog('Grafo carregado com sucesso')
    }
  } catch (err) {
    addLog(`Erro ao carregar grafo: ${err.message}`)
  } finally {
    graphLoading.value = false
  }
}

const refreshGraph = () => {
  if (projectData.value?.graph_id) {
    loadGraph(projectData.value.graph_id)
  }
}

onMounted(async () => {
  isMobileView.value = window.innerWidth < 768
  window.addEventListener('resize', handleViewResize)
  addLog('Carregando configuracao de ambiente...')
  
  // Verificar e encerrar simulacoes ativas (ao retornar do Step 3)
  await checkAndStopRunningSimulation()
  
  // Carregar dados da simulacao
  loadSimulationData()
})
onUnmounted(() => {
  window.removeEventListener('resize', handleViewResize)
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
  overflow: hidden;
  font-family: var(--font);
}

/* Header */
.app-header {
  flex-shrink: 0;
  height: 52px;
  border-bottom: 1px solid var(--border);
  background: var(--nav-bg);
  backdrop-filter: blur(16px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 10;
}

.mv-logo {
  height: 32px; width: auto; cursor: pointer; display: block;
  opacity: 0.9; transition: opacity 0.12s;
}
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

.mv-status {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.64rem; color: var(--text2); letter-spacing: 0.06em;
}
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text3); }
.mv-status.processing .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.completed .mv-dot { background: var(--green); }
.mv-status.error .mv-dot { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.mv-content { flex: 1; display: flex; overflow: hidden; }
.mv-panel { height: 100%; overflow: hidden; }

.mv-panel.console {
  width: 420px; min-width: 380px; flex-shrink: 0;
  background: var(--bg);
  border-right: 1px solid var(--border);
  overflow: hidden;
}
.mv-panel.canvas { flex: 1; min-width: 0; }
.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }
</style>




