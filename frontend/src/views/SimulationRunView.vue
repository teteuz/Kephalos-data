<template>
  <div class="main-view">
    <!-- Header -->
    <header class="app-header">
      <div class="header-left">
        <img src="/kephalos-logo.png" alt="KEPHALOS" class="mv-logo" @click="router.push('/')" />
      </div>

      <div class="header-center"></div>

      <div class="header-right">
        <span class="mv-step-tag">
          <span class="mv-step-n">3/5</span>
          Start Simulation
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
          :currentPhase="3"
          :isSimulating="isSimulating"
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
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GraphPanel from '../components/GraphPanel.vue'
import Step3Simulation from '../components/Step3Simulation.vue'
import { getProject, getGraphData } from '../api/graph'
import { getSimulation, getSimulationConfig, stopSimulation, closeSimulationEnv, getEnvStatus } from '../api/simulation'

const route = useRoute()
const router = useRouter()

// Props
const props = defineProps({
  simulationId: String
})

// Layout State
const panelExpanded = ref(false)

// Data State
const currentSimulationId = ref(route.params.simulationId)
// ç›´æŽ¥åœ¨åˆå§‹åŒ–æ—¶ä»Ž query å‚æ•°èŽ·å– maxRoundsï¼Œç¡®ä¿å­ç»„ä»¶èƒ½ç«‹å³èŽ·å–åˆ°å€¼
const maxRounds = ref(route.query.maxRounds ? parseInt(route.query.maxRounds) : null)
const minutesPerRound = ref(30) // é»˜è®¤æ¯è½®30åˆ†é’Ÿ
const projectData = ref(null)
const graphData = ref(null)
const graphLoading = ref(false)
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
  if (currentStatus.value === 'error') return 'Error'
  if (currentStatus.value === 'completed') return 'Completed'
  return 'Running'
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
    } else {
      addLog(`åŠ è½½æ¨¡æ‹Ÿæ•°æ®å¤±è´¥: ${simRes.error || 'æœªçŸ¥é”™è¯¯'}`)
    }
  } catch (err) {
    addLog(`åŠ è½½å¼‚å¸¸: ${err.message}`)
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
  addLog('SimulationRunView åˆå§‹åŒ–')
  
  // è®°å½• maxRounds é…ç½®ï¼ˆå€¼å·²åœ¨åˆå§‹åŒ–æ—¶ä»Ž query å‚æ•°èŽ·å–ï¼‰
  if (maxRounds.value) {
    addLog(`è‡ªå®šä¹‰æ¨¡æ‹Ÿè½®æ•°: ${maxRounds.value}`)
  }
  
  loadSimulationData()
})

onUnmounted(() => {
  stopGraphRefresh()
})
</script>

<style scoped>
.main-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #080808;
  overflow: hidden;
  font-family: 'Roboto Mono', 'JetBrains Mono', monospace;
}

/* Header */
.app-header {
  flex-shrink: 0;
  height: 52px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(8,8,8,0.97);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 10;
}

.mv-logo {
  height: 40px; width: auto; cursor: pointer; display: block;
  opacity: 0.9; transition: opacity 0.12s;
}
.mv-logo:hover { opacity: 1; }

.header-center { position: absolute; left: 50%; transform: translateX(-50%); }

.header-right { display: flex; align-items: center; gap: 14px; }

.mv-step-tag {
  font-family: 'Roboto Mono', monospace; font-size: 0.7rem;
  color: rgba(255,255,255,0.4); display: flex; align-items: center; gap: 8px;
}
.mv-step-n { color: rgba(255,255,255,0.2); }

.mv-sep { width: 1px; height: 14px; background: rgba(255,255,255,0.08); }

.mv-status {
  display: flex; align-items: center; gap: 6px;
  font-family: 'Roboto Mono', monospace; font-size: 0.66rem;
  color: rgba(255,255,255,0.35); letter-spacing: 0.06em;
}
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: rgba(255,255,255,0.2); }
.mv-status.processing .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.completed .mv-dot { background: #BDEBB5; }
.mv-status.error .mv-dot { background: #ef4444; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Content */
.mv-content { flex: 1; display: flex; overflow: hidden; }

.mv-panel {
  height: 100%; overflow: hidden;
  transition: width 0.4s cubic-bezier(0.25,0.8,0.25,1), opacity 0.3s;
}
.mv-panel.left { border-right: 1px solid rgba(255,255,255,0.06); }

.mv-panel.right.floating {
  position: fixed !important;
  bottom: 20px !important; right: 20px !important;
  width: 240px !important; height: auto !important;
  z-index: 50 !important;
  border-radius: 12px;
  background: rgba(8,8,8,0.4) !important;
  backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.12);
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  overflow: hidden; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25,0.8,0.25,1);
}
.mv-panel.right.floating:hover {
  background: rgba(8,8,8,0.5) !important;
  border-color: rgba(255,255,255,0.2);
  box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}

.mv-float-tab {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 16px 12px; gap: 8px; width: 100%; height: 100%;
}
.mv-tab-icon { font-size: 20px; color: rgba(255,255,255,0.6); transition: all 0.3s ease; }
.mv-float-tab:hover .mv-tab-icon { color: rgba(255,255,255,0.9); transform: translateY(2px); }
.mv-tab-text {
  font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em;
  color: rgba(255,255,255,0.5); text-align: center; transition: color 0.3s ease;
}
.mv-float-tab:hover .mv-tab-text { color: rgba(255,255,255,0.8); }

.mv-panel.right.expanded {
  position: static !important; width: 100% !important; height: 100% !important;
  background: #080808 !important; backdrop-filter: none;
  border: none; border-left: 1px solid rgba(255,255,255,0.06);
  box-shadow: none; border-radius: 0;
}

.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }

.mv-close-panel {
  position: absolute; top: 10px; right: 10px;
  width: 28px; height: 28px;
  background: transparent; border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.6); font-size: 18px; cursor: pointer;
  border-radius: 4px; display: flex; align-items: center; justify-content: center;
  z-index: 100; transition: all 0.2s ease;
}
.mv-close-panel:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.4); color: rgba(255,255,255,0.9);
}
</style>




