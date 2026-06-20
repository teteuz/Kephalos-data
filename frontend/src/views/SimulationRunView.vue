<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <AppLogo class="mv-logo" @click="router.push('/')" style="cursor:pointer" />
      </div>

      <div class="header-center">
        <div class="mv-progress">
          <div class="mv-prog-step done"><span class="mv-prog-num">01</span><span class="mv-prog-line"></span></div>
          <div class="mv-prog-step done"><span class="mv-prog-num">02</span><span class="mv-prog-line"></span></div>
          <div class="mv-prog-step active"><span class="mv-prog-num">03</span><span class="mv-prog-line"></span></div>
          <div class="mv-prog-step"><span class="mv-prog-num">04</span><span class="mv-prog-line"></span></div>
          <div class="mv-prog-step"><span class="mv-prog-num">05</span></div>
        </div>
      </div>

      <div class="header-right">
        <span class="mv-step-tag">
          <span class="mv-step-n">3/5</span>
          Iniciar Simulação
        </span>
        <span class="mv-sep"></span>
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

      <!-- Graph panel -->
      <div
        class="mv-panel left"
        :class="{ 'mobile-hidden': isMobileView && mobileTab !== 'graph' }"
        :style="isMobileView ? {} : leftPanelStyle"
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

      <!-- Desktop: floating/expanded right panel -->
      <div
        v-if="!isMobileView"
        class="mv-panel right"
        :class="{ floating: !panelExpanded, expanded: panelExpanded }"
        :style="rightPanelStyle"
        @click="panelExpanded = true"
      >
        <div v-if="!panelExpanded" class="mv-float-tab">
          <div class="mv-tab-step-num">03</div>
          <div class="mv-tab-name">Simulação</div>
          <div class="mv-tab-expand">ABRIR ↑</div>
        </div>
        <div v-else class="mv-panel-content">
          <button class="mv-close-panel" @click.stop="panelExpanded = false" title="Collapse to floating tab">×</button>
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
const panelExpanded = ref(false)
const isMobileView = ref(false)
const mobileTab = ref('graph')

// Auto-switch to sim tab on mobile when simulation is running
watch(isSimulating, (val) => {
  if (val && isMobileView.value) mobileTab.value = 'sim'
})

const handleViewResize = () => { isMobileView.value = window.innerWidth < 768 }

// Data State
const currentSimulationId = ref(route.params.simulationId)
// ç›´æŽ¥åœ¨åˆå§‹åŒ–æ—¶ä»Ž query å‚æ•°èŽ·å– maxRoundsï¼Œç¡®ä¿å­ç»„ä»¶èƒ½ç«‹å³èŽ·å–åˆ°å€¼
const maxRounds = ref(route.query.maxRounds ? parseInt(route.query.maxRounds) : null)
const minutesPerRound = ref(30) // é»˜è®¤æ¯è½®30åˆ†é’Ÿ
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
const agentProfiles = ref([])
const systemLogs = ref([])
const currentStatus = ref('processing') // processing | completed | error

// --- Computed Layout Styles ---
const leftPanelStyle = computed(() => ({ width: '100%', opacity: 1 }))

const rightPanelStyle = computed(() => {
  if (!panelExpanded.value) {
    return { position: 'fixed', bottom: '20px', right: '20px', width: '240px', height: 'auto', zIndex: 50 }
  }
  return { width: '50%', opacity: 1, position: 'static' }
})

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
  // åœ¨è¿”å›ž Step 2 ä¹‹å‰ï¼Œå…ˆå…³é—­æ­£åœ¨è¿è¡Œçš„æ¨¡æ‹Ÿ
  addLog('å‡†å¤‡è¿”å›ž Step 2ï¼Œæ­£åœ¨å…³é—­æ¨¡æ‹Ÿ...')
  
  // åœæ­¢è½®è¯¢
  stopGraphRefresh()
  
  try {
    // å…ˆå°è¯•ä¼˜é›…å…³é—­æ¨¡æ‹ŸçŽ¯å¢ƒ
    const envStatusRes = await getEnvStatus({ simulation_id: currentSimulationId.value })
    
    if (envStatusRes.success && envStatusRes.data?.env_alive) {
      addLog('æ­£åœ¨å…³é—­æ¨¡æ‹ŸçŽ¯å¢ƒ...')
      try {
        await closeSimulationEnv({ 
          simulation_id: currentSimulationId.value,
          timeout: 10
        })
        addLog('âœ“ æ¨¡æ‹ŸçŽ¯å¢ƒå·²å…³é—­')
      } catch (closeErr) {
        addLog(`å…³é—­æ¨¡æ‹ŸçŽ¯å¢ƒå¤±è´¥ï¼Œå°è¯•å¼ºåˆ¶åœæ­¢...`)
        try {
          await stopSimulation({ simulation_id: currentSimulationId.value })
          addLog('âœ“ æ¨¡æ‹Ÿå·²å¼ºåˆ¶åœæ­¢')
        } catch (stopErr) {
          addLog(`å¼ºåˆ¶åœæ­¢å¤±è´¥: ${stopErr.message}`)
        }
      }
    } else {
      // çŽ¯å¢ƒæœªè¿è¡Œï¼Œæ£€æŸ¥æ˜¯å¦éœ€è¦åœæ­¢è¿›ç¨‹
      if (isSimulating.value) {
        addLog('æ­£åœ¨åœæ­¢æ¨¡æ‹Ÿè¿›ç¨‹...')
        try {
          await stopSimulation({ simulation_id: currentSimulationId.value })
          addLog('âœ“ æ¨¡æ‹Ÿå·²åœæ­¢')
        } catch (err) {
          addLog(`åœæ­¢æ¨¡æ‹Ÿå¤±è´¥: ${err.message}`)
        }
      }
    }
  } catch (err) {
    addLog(`æ£€æŸ¥æ¨¡æ‹ŸçŠ¶æ€å¤±è´¥: ${err.message}`)
  }
  
  // è¿”å›žåˆ° Step 2 (Environment Setup)
  router.push({ name: 'Simulation', params: { simulationId: currentSimulationId.value } })
}

const handleNextStep = () => {
  // Step3Simulation ç»„ä»¶ä¼šç›´æŽ¥å¤„ç†Report Generationå’Œè·¯ç”±è·³è½¬
  // è¿™ä¸ªæ–¹æ³•ä»…ä½œä¸ºå¤‡ç”¨
  addLog('è¿›å…¥ Step 4: Report Generation')
}

// --- Data Logic ---
const loadSimulationData = async () => {
  try {
    addLog(`åŠ è½½æ¨¡æ‹Ÿæ•°æ®: ${currentSimulationId.value}`)
    
    // èŽ·å– simulation ä¿¡æ¯
    const simRes = await getSimulation(currentSimulationId.value)
    if (simRes.success && simRes.data) {
      const simData = simRes.data
      
      // èŽ·å– simulation config ä»¥èŽ·å– minutes_per_round
      try {
        const configRes = await getSimulationConfig(currentSimulationId.value)
        if (configRes.success && configRes.data?.time_config?.minutes_per_round) {
          minutesPerRound.value = configRes.data.time_config.minutes_per_round
          addLog(`æ—¶é—´é…ç½®: æ¯è½® ${minutesPerRound.value} åˆ†é’Ÿ`)
        }
      } catch (configErr) {
        addLog(`èŽ·å–æ—¶é—´é…ç½®å¤±è´¥ï¼Œä½¿ç”¨é»˜è®¤å€¼: ${minutesPerRound.value}åˆ†é’Ÿ/è½®`)
      }
      
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
  // å½“æ­£åœ¨æ¨¡æ‹Ÿæ—¶ï¼Œè‡ªåŠ¨åˆ·æ–°ä¸æ˜¾ç¤ºå…¨å± loadingï¼Œä»¥å…é—ªçƒ
  // æ‰‹åŠ¨åˆ·æ–°æˆ–åˆå§‹åŠ è½½æ—¶æ˜¾ç¤º loading
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
  // ç«‹å³åˆ·æ–°ä¸€æ¬¡ï¼Œç„¶åŽæ¯30ç§’åˆ·æ–°
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
.header-center { position: absolute; left: 50%; transform: translateX(-50%); }
.header-right { display: flex; align-items: center; gap: 14px; }

.mv-progress { display: flex; align-items: center; gap: 0; }
.mv-prog-step { display: flex; align-items: center; gap: 0; }
.mv-prog-num {
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
  color: var(--text3); padding: 2px 6px; border-radius: 3px; transition: all 0.2s;
}
.mv-prog-step.done .mv-prog-num { color: var(--green-text); opacity: 0.6; }
.mv-prog-step.active .mv-prog-num {
  color: var(--green-text); background: var(--green-dim); border: 1px solid var(--green-border);
}
.mv-prog-line { display: inline-block; width: 18px; height: 1px; background: var(--border); margin: 0 3px; }
.mv-prog-step.done .mv-prog-line { background: var(--green-border); }

.mv-step-tag { font-size: 0.68rem; color: var(--text2); display: flex; align-items: center; gap: 8px; }
.mv-step-n { color: var(--text3); }
.mv-sep { width: 1px; height: 13px; background: var(--border2); }
.mv-status { display: flex; align-items: center; gap: 6px; font-size: 0.64rem; color: var(--text2); letter-spacing: 0.06em; }
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text3); }
.mv-status.processing .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.completed .mv-dot { background: var(--green); }
.mv-status.error .mv-dot { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.mv-content { flex: 1; display: flex; overflow: hidden; }
.mv-panel { height: 100%; overflow: hidden; transition: width 0.35s cubic-bezier(0.25,0.8,0.25,1); }
.mv-panel.left { border-right: 1px solid var(--border); }

.mv-panel.right.floating {
  position: fixed !important; bottom: 20px !important; right: 20px !important;
  width: 200px !important; height: auto !important; z-index: 50 !important;
  border-radius: 10px;
  background: var(--bg2) !important;
  backdrop-filter: blur(14px) saturate(180%);
  border: 1px solid var(--border2);
  box-shadow: var(--shadow-md);
  overflow: hidden; cursor: pointer;
  transition: all 0.25s cubic-bezier(0.25,0.8,0.25,1);
}
.mv-panel.right.floating:hover {
  border-color: var(--green-border);
  transform: translateY(-2px);
}
.mv-float-tab { display: flex; flex-direction: column; align-items: flex-start; padding: 14px 16px; gap: 3px; width: 100%; height: 100%; }
.mv-tab-step-num { font-size: 1.1rem; font-weight: 700; color: var(--text3); line-height: 1; }
.mv-tab-name { font-size: 0.7rem; font-weight: 600; color: var(--text); letter-spacing: 0.02em; line-height: 1.3; }
.mv-tab-expand { font-size: 0.58rem; font-weight: 700; color: var(--green-text); opacity: 0.6; letter-spacing: 0.1em; margin-top: 4px; }
.mv-panel.right.floating:hover .mv-tab-expand { opacity: 1; }
.mv-panel.right.floating:hover .mv-tab-step-num { color: var(--text2); }

.mv-panel.right.expanded {
  position: static !important; width: 420px !important; min-width: 380px; height: 100% !important;
  background: var(--bg) !important; backdrop-filter: none;
  border: none; border-left: 1px solid var(--border);
  box-shadow: none; border-radius: 0; flex-shrink: 0;
}
.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }
.mv-close-panel {
  position: absolute; top: 12px; right: 12px;
  width: 26px; height: 26px;
  background: var(--surface-1); border: 1px solid var(--border2);
  color: var(--text2); font-size: 16px; cursor: pointer;
  border-radius: 5px; display: flex; align-items: center; justify-content: center;
  z-index: 100; transition: all 0.15s;
}
.mv-close-panel:hover { background: var(--surface-2); border-color: var(--text2); color: var(--text); }

/* ── MOBILE LAYOUT ── */
.mv-content.mobile-mode {
  flex-direction: column;
  position: relative;
}
.mv-content.mobile-mode .mv-panel.left {
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




