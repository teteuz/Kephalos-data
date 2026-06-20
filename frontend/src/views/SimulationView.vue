<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <AppLogo class="mv-logo" @click="router.push('/')" style="cursor:pointer" />
      </div>

      <div class="header-center"></div>

      <div class="header-right">
        <span class="mv-step-tag">
          <span class="mv-step-n">2/5</span>
          Configurar Ambiente
        </span>
        <span class="mv-sep"></span>
        <span class="mv-status" :class="statusClass">
          <span class="mv-dot"></span>{{ statusText }}
        </span>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="mv-content">
      <div class="mv-panel left" :style="leftPanelStyle">
        <GraphPanel
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="2"
          :agentProfiles="agentProfiles"
          @refresh="refreshGraph"
        />
      </div>

      <div
        class="mv-panel right"
        :class="{ floating: !panelExpanded, expanded: panelExpanded }"
        :style="rightPanelStyle"
        @click="panelExpanded = true"
      >
        <div v-if="!panelExpanded" class="mv-float-tab">
          <div class="mv-tab-icon">◆</div>
          <div class="mv-tab-text">WORKBENCH</div>
        </div>
        <div v-else class="mv-panel-content">
          <button class="mv-close-panel" @click.stop="panelExpanded = false" title="Collapse to floating tab">×</button>
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
const panelExpanded = ref(false)
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

// --- Computed Layout Styles ---
const leftPanelStyle = computed(() => {
  if (panelExpanded.value && !isMobileView.value) return { flex: '1', minWidth: '0' }
  return { width: '100%' }
})

const rightPanelStyle = computed(() => {
  if (!panelExpanded.value) {
    return { position: 'fixed', bottom: '20px', right: '20px', width: '200px', height: 'auto', zIndex: 50 }
  }
  if (isMobileView.value) {
    return { position: 'fixed', top: '52px', left: '0', bottom: '0', right: '0', width: '100%', zIndex: 200 }
  }
  return { width: '420px', flexShrink: '0', position: 'static', height: '100%' }
})

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
  // è¿”å›žåˆ° process é¡µé¢
  if (projectData.value?.project_id) {
    router.push({ name: 'Process', params: { projectId: projectData.value.project_id } })
  } else {
    router.push('/')
  }
}

const handleNextStep = (params = {}) => {
  addLog('è¿›å…¥ Step 3: Start Simulation')
  
  // è®°å½•æ¨¡æ‹Ÿè½®æ•°é…ç½®
  if (params.maxRounds) {
    addLog(`è‡ªå®šä¹‰æ¨¡æ‹Ÿè½®æ•°: ${params.maxRounds} è½®`)
  } else {
    addLog('ä½¿ç”¨è‡ªåŠ¨é…ç½®çš„æ¨¡æ‹Ÿè½®æ•°')
  }
  
  // æž„å»ºè·¯ç”±å‚æ•°
  const routeParams = {
    name: 'SimulationRun',
    params: { simulationId: currentSimulationId.value }
  }
  
  // å¦‚æžœæœ‰è‡ªå®šä¹‰è½®æ•°ï¼Œé€šè¿‡ query å‚æ•°ä¼ é€’
  if (params.maxRounds) {
    routeParams.query = { maxRounds: params.maxRounds }
  }
  
  // è·³è½¬åˆ° Step 3 é¡µé¢
  router.push(routeParams)
}

// --- Data Logic ---

/**
 * æ£€æŸ¥å¹¶å…³é—­æ­£åœ¨è¿è¡Œçš„æ¨¡æ‹Ÿ
 * å½“ç”¨æˆ·ä»Ž Step 3 è¿”å›žåˆ° Step 2 æ—¶ï¼Œé»˜è®¤ç”¨æˆ·è¦é€€å‡ºæ¨¡æ‹Ÿ
 */
const checkAndStopRunningSimulation = async () => {
  if (!currentSimulationId.value) return
  
  try {
    // å…ˆæ£€æŸ¥æ¨¡æ‹ŸçŽ¯å¢ƒæ˜¯å¦å­˜æ´»
    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog('æ£€æµ‹åˆ°æ¨¡æ‹ŸçŽ¯å¢ƒæ­£åœ¨è¿è¡Œï¼Œæ­£åœ¨å…³é—­...')
      
      // å°è¯•ä¼˜é›…å…³é—­æ¨¡æ‹ŸçŽ¯å¢ƒ
      try {
        const closeRes = await closeSimulationEnv({ 
          simulation_id: currentSimulationId.value,
          timeout: 10  // 10ç§’è¶…æ—¶
        })
        
        if (closeRes.success) {
          addLog('âœ“ æ¨¡æ‹ŸçŽ¯å¢ƒå·²å…³é—­')
        } else {
          addLog(`å…³é—­æ¨¡æ‹ŸçŽ¯å¢ƒå¤±è´¥: ${closeRes.error || 'æœªçŸ¥é”™è¯¯'}`)
          // å¦‚æžœä¼˜é›…å…³é—­å¤±è´¥ï¼Œå°è¯•å¼ºåˆ¶åœæ­¢
          await forceStopSimulation()
        }
      } catch (closeErr) {
        addLog(`å…³é—­æ¨¡æ‹ŸçŽ¯å¢ƒå¼‚å¸¸: ${closeErr.message}`)
        // å¦‚æžœä¼˜é›…å…³é—­å¼‚å¸¸ï¼Œå°è¯•å¼ºåˆ¶åœæ­¢
        await forceStopSimulation()
      }
    } else {
      // çŽ¯å¢ƒæœªè¿è¡Œï¼Œä½†å¯èƒ½è¿›ç¨‹è¿˜åœ¨ï¼Œæ£€æŸ¥æ¨¡æ‹ŸçŠ¶æ€
      const simRes = await getSimulation(currentSimulationId.value)
      if (simRes.success && simRes.data?.status === 'running') {
        addLog('æ£€æµ‹åˆ°æ¨¡æ‹ŸçŠ¶æ€ä¸ºè¿è¡Œä¸­ï¼Œæ­£åœ¨åœæ­¢...')
        await forceStopSimulation()
      }
    }
  } catch (err) {
    // æ£€æŸ¥çŽ¯å¢ƒçŠ¶æ€å¤±è´¥ä¸å½±å“åŽç»­æµç¨‹
    console.warn('æ£€æŸ¥æ¨¡æ‹ŸçŠ¶æ€å¤±è´¥:', err)
  }
}

/**
 * å¼ºåˆ¶åœæ­¢æ¨¡æ‹Ÿ
 */
const forceStopSimulation = async () => {
  try {
    const stopRes = await stopSimulation({ simulation_id: currentSimulationId.value })
    if (stopRes.success) {
      addLog('âœ“ æ¨¡æ‹Ÿå·²å¼ºåˆ¶åœæ­¢')
    } else {
      addLog(`å¼ºåˆ¶åœæ­¢æ¨¡æ‹Ÿå¤±è´¥: ${stopRes.error || 'æœªçŸ¥é”™è¯¯'}`)
    }
  } catch (err) {
    addLog(`å¼ºåˆ¶åœæ­¢æ¨¡æ‹Ÿå¼‚å¸¸: ${err.message}`)
  }
}

const loadSimulationData = async () => {
  try {
    addLog(`åŠ è½½æ¨¡æ‹Ÿæ•°æ®: ${currentSimulationId.value}`)
    
    // èŽ·å– simulation ä¿¡æ¯
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data
      
      // èŽ·å– project ä¿¡æ¯
      if (simData.project_id) {
        const projRes = await getProject(simData.project_id)
        if (projRes.success && projRes.data) {
          projectData.value = projRes.data
          addLog(`é¡¹ç›®åŠ è½½æˆåŠŸ: ${projRes.data.project_id}`)
          
          // èŽ·å– graph æ•°æ®
          if (projRes.data.graph_id) {
            await loadGraph(projRes.data.graph_id)
          }
        }
      }
      // Load agent profiles for graph node enrichment
      loadAgentProfiles()
    } else {
      addLog(`åŠ è½½æ¨¡æ‹Ÿæ•°æ®å¤±è´¥: ${simRes.error || 'æœªçŸ¥é”™è¯¯'}`)
    }
  } catch (err) {
    addLog(`åŠ è½½å¼‚å¸¸: ${err.message}`)
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
      addLog('Graph data loaded successfully')
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

onMounted(async () => {
  isMobileView.value = window.innerWidth < 768
  window.addEventListener('resize', handleViewResize)
  addLog('SimulationView åˆå§‹åŒ–')
  
  // æ£€æŸ¥å¹¶å…³é—­æ­£åœ¨è¿è¡Œçš„æ¨¡æ‹Ÿï¼ˆç”¨æˆ·ä»Ž Step 3 è¿”å›žæ—¶ï¼‰
  await checkAndStopRunningSimulation()
  
  // åŠ è½½æ¨¡æ‹Ÿæ•°æ®
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

.header-center { position: absolute; left: 50%; transform: translateX(-50%); }

.header-right { display: flex; align-items: center; gap: 14px; }

.mv-step-tag {
  font-family: var(--mono); font-size: 0.7rem;
  color: var(--text2); display: flex; align-items: center; gap: 8px;
}
.mv-step-n { color: var(--text3); }

.mv-sep { width: 1px; height: 14px; background: var(--border2); }

.mv-status {
  display: flex; align-items: center; gap: 6px;
  font-family: var(--mono); font-size: 0.66rem;
  color: var(--text2); letter-spacing: 0.06em;
}
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text3); }
.mv-status.processing .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.completed .mv-dot { background: var(--green); }
.mv-status.error .mv-dot { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Content */
.mv-content { flex: 1; display: flex; overflow: hidden; }

.mv-panel {
  height: 100%; overflow: hidden;
  transition: width 0.4s cubic-bezier(0.25,0.8,0.25,1), opacity 0.3s;
}
.mv-panel.left { border-right: 1px solid var(--border); }

.mv-panel.right.floating {
  position: fixed !important;
  bottom: 20px !important; right: 20px !important;
  width: 240px !important; height: auto !important;
  z-index: 50 !important;
  border-radius: 12px;
  background: var(--bg2) !important;
  backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid var(--border2);
  box-shadow: var(--shadow-md);
  overflow: hidden; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25,0.8,0.25,1);
}
.mv-panel.right.floating:hover {
  border-color: var(--green-border);
  box-shadow: var(--shadow-md);
}

.mv-float-tab {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 16px 12px; gap: 8px; width: 100%; height: 100%;
}
.mv-tab-icon { font-size: 20px; color: var(--text2); transition: all 0.3s ease; }
.mv-float-tab:hover .mv-tab-icon { color: var(--text); transform: translateY(2px); }
.mv-tab-text {
  font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em;
  color: var(--text2); text-align: center; transition: color 0.3s ease;
}
.mv-float-tab:hover .mv-tab-text { color: var(--text); }

.mv-panel.right.expanded {
  position: static;
  height: 100%;
  background: var(--bg);
  backdrop-filter: none;
  border: none;
  border-left: 1px solid var(--border);
  box-shadow: none;
  border-radius: 0;
}

@media (max-width: 767px) {
  .mv-panel.right.floating { width: 160px !important; }
  .mv-panel.right.expanded { border-left: none; border-top: 1px solid var(--border); }
}

.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }

.mv-close-panel {
  position: absolute; top: 10px; right: 10px;
  width: 28px; height: 28px;
  background: transparent; border: 1px solid var(--border2);
  color: var(--text2); font-size: 18px; cursor: pointer;
  border-radius: 4px; display: flex; align-items: center; justify-content: center;
  z-index: 100; transition: all 0.2s ease;
}
.mv-close-panel:hover {
  background: var(--surface-2);
  border-color: var(--text2); color: var(--text);
}
</style>




