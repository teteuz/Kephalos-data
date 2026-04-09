<template>
  <div class="mv">
    <header class="mv-header">
      <div class="mv-header-left">
        <img
          src="/kephalos-logo.png"
          alt="KEPHALOS"
          class="mv-logo"
          @click="router.push('/')"
        />
      </div>

      <div class="mv-header-center">
      </div>

      <div class="mv-header-right">
        <span class="mv-step-tag">
          <span class="mv-step-n">{{ currentStep }}/5</span>
          {{ stepNames[currentStep - 1] }}
        </span>
        <span class="mv-sep"></span>
        <span class="mv-status" :class="statusClass">
          <span class="mv-dot"></span>{{ statusText }}
        </span>
      </div>
    </header>

    <main class="mv-content">
      <div class="mv-panel left" :style="leftPanelStyle">
        <GraphPanel
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="currentPhase"
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
          <button 
            class="mv-close-panel" 
            @click.stop="panelExpanded = false"
            title="Collapse to floating tab"
          >×</button>
          <Step1GraphBuild
            v-if="currentStep === 1"
            :currentPhase="currentPhase"
            :projectData="projectData"
            :ontologyProgress="ontologyProgress"
            :buildProgress="buildProgress"
            :graphData="graphData"
            :systemLogs="systemLogs"
            @next-step="handleNextStep"
          />
          <Step2EnvSetup
            v-else-if="currentStep === 2"
            :projectData="projectData"
            :graphData="graphData"
            :systemLogs="systemLogs"
            @go-back="handleGoBack"
            @next-step="handleNextStep"
            @add-log="addLog"
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
import Step1GraphBuild from '../components/Step1GraphBuild.vue'
import Step2EnvSetup from '../components/Step2EnvSetup.vue'
import { generateOntology, getProject, buildGraph, getTaskStatus, getGraphData } from '../api/graph'
import { getPendingUpload, clearPendingUpload } from '../store/pendingUpload'

const route = useRoute()
const router = useRouter()
const panelExpanded = ref(false)
const currentStep = ref(1)
const stepNames = ['Graph Build', 'Environment Setup', 'Start Simulation', 'Report Generation', 'Deep Interaction']
const currentProjectId = ref(route.params.projectId)
const loading = ref(false)
const graphLoading = ref(false)
const error = ref('')
const projectData = ref(null)
const graphData = ref(null)
const currentPhase = ref(-1)
const ontologyProgress = ref(null)
const buildProgress = ref(null)
const systemLogs = ref([])
let pollTimer = null
let graphPollTimer = null

const leftPanelStyle = computed(() => {
  return { width: '100%', opacity: 1 }
})
const rightPanelStyle = computed(() => {
  if (panelExpanded.value === false) {
    return { position: 'fixed', bottom: '20px', right: '20px', width: '240px', height: 'auto', zIndex: 50 }
  }
  return { width: '50%', opacity: 1, position: 'static' }
})
const statusClass = computed(() => error.value ? 'err' : currentPhase.value >= 2 ? 'ok' : 'proc')
const statusText = computed(() => {
  if (error.value) return 'Error'
  if (currentPhase.value >= 2) return 'Ready'
  if (currentPhase.value === 1) return 'Building Graph'
  if (currentPhase.value === 0) return 'Analyzing'
  return 'Initializing'
})

const addLog = (msg) => {
  const now = new Date()
  const time = now.toLocaleTimeString('en-US', { hour12: false }) + '.' + String(now.getMilliseconds()).padStart(3, '0')
  systemLogs.value.push({ time, msg })
  if (systemLogs.value.length > 100) systemLogs.value.shift()
}
const handleNextStep = (params = {}) => {
  if (currentStep.value < 5) {
    currentStep.value++
    addLog(`Step ${currentStep.value}: ${stepNames[currentStep.value - 1]}`)
  }
}
const handleGoBack = () => {
  if (currentStep.value > 1) { currentStep.value--; addLog(`Back to Step ${currentStep.value}`) }
}

const initProject = async () => {
  addLog('Initializing...')
  currentProjectId.value === 'new' ? await handleNewProject() : await loadProject()
}
const handleNewProject = async () => {
  const pending = getPendingUpload()
  if (!pending.isPending || !pending.files.length) { error.value = 'No pending files.'; return }
  try {
    loading.value = true; currentPhase.value = 0
    ontologyProgress.value = { message: 'Uploading and analyzing...' }
    addLog('Starting ontology generation...')
    const fd = new FormData()
    pending.files.forEach(f => fd.append('files', f))
    fd.append('simulation_requirement', pending.simulationRequirement)
    const res = await generateOntology(fd)
    if (res.success) {
      clearPendingUpload()
      currentProjectId.value = res.data.project_id
      projectData.value = res.data
      router.replace({ name: 'Process', params: { projectId: res.data.project_id } })
      ontologyProgress.value = null
      addLog(`Ontology generated: ${res.data.project_id}`)
      await startBuildGraph()
    } else { error.value = res.error || 'Failed'; addLog(`Error: ${error.value}`) }
  } catch (err) { error.value = err.message; addLog(`Exception: ${err.message}`) }
  finally { loading.value = false }
}
const loadProject = async () => {
  try {
    loading.value = true
    const res = await getProject(currentProjectId.value)
    if (res.success) {
      projectData.value = res.data
      updatePhaseByStatus(res.data.status)
      addLog(`Project loaded: ${res.data.status}`)
      if (res.data.status === 'ontology_generated' && !res.data.graph_id) await startBuildGraph()
      else if (res.data.status === 'graph_building') { currentPhase.value = 1; startPollingTask(res.data.graph_build_task_id); startGraphPolling() }
      else if (res.data.status === 'graph_completed' && res.data.graph_id) { currentPhase.value = 2; await loadGraph(res.data.graph_id) }
    } else { error.value = res.error; addLog(`Error: ${res.error}`) }
  } catch (err) { error.value = err.message }
  finally { loading.value = false }
}
const updatePhaseByStatus = (s) => {
  const m = { created: 0, ontology_generated: 0, graph_building: 1, graph_completed: 2 }
  if (s === 'failed') error.value = 'Failed'
  else currentPhase.value = m[s] ?? -1
}
const startBuildGraph = async () => {
  try {
    currentPhase.value = 1; buildProgress.value = { progress: 0 }
    addLog('Building graph...')
    const res = await buildGraph({ project_id: currentProjectId.value })
    if (res.success) { addLog(`Task: ${res.data.task_id}`); startGraphPolling(); startPollingTask(res.data.task_id) }
    else { error.value = res.error; addLog(`Error: ${res.error}`) }
  } catch (err) { error.value = err.message }
}
const startGraphPolling = () => { fetchGraphData(); graphPollTimer = setInterval(fetchGraphData, 10000) }
const fetchGraphData = async () => {
  try {
    const pr = await getProject(currentProjectId.value)
    if (pr.success && pr.data.graph_id) {
      const gr = await getGraphData(pr.data.graph_id)
      if (gr.success) { graphData.value = gr.data }
    }
  } catch (e) { console.warn(e) }
}
const startPollingTask = (id) => { pollTaskStatus(id); pollTimer = setInterval(() => pollTaskStatus(id), 2000) }
const pollTaskStatus = async (id) => {
  try {
    const res = await getTaskStatus(id)
    if (res.success) {
      const t = res.data
      if (t.message && t.message !== buildProgress.value?.message) addLog(t.message)
      buildProgress.value = { progress: t.progress || 0, message: t.message }
      if (t.status === 'completed') {
        addLog('Build complete.'); stopPolling(); stopGraphPolling(); currentPhase.value = 2
        const pr = await getProject(currentProjectId.value)
        if (pr.success && pr.data.graph_id) { projectData.value = pr.data; await loadGraph(pr.data.graph_id) }
      } else if (t.status === 'failed') { stopPolling(); error.value = t.error; addLog(`Failed: ${t.error}`) }
    }
  } catch (e) { console.error(e) }
}
const loadGraph = async (id) => {
  graphLoading.value = true
  try { const r = await getGraphData(id); if (r.success) { graphData.value = r.data; addLog('Graph loaded.') } }
  catch (e) { addLog(`Exception: ${e.message}`) }
  finally { graphLoading.value = false }
}
const refreshGraph = () => { if (projectData.value?.graph_id) loadGraph(projectData.value.graph_id) }
const stopPolling = () => { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }
const stopGraphPolling = () => { if (graphPollTimer) { clearInterval(graphPollTimer); graphPollTimer = null } }

onMounted(() => initProject())
onUnmounted(() => { stopPolling(); stopGraphPolling() })
</script>

<style scoped>
.mv {
  height: 100vh; display: flex; flex-direction: column;
  background: #080808; overflow: hidden;
  font-family: 'Roboto Mono', 'JetBrains Mono', monospace;
}

.mv-header {
  flex-shrink: 0; height: 52px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(8,8,8,0.97);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; position: relative; z-index: 10;
}

.mv-logo {
  height: 40px; width: auto; cursor: pointer; display: block;
  opacity: 0.9; transition: opacity 0.12s;
}
.mv-logo:hover { opacity: 1; }

.mv-header-center { position: absolute; left: 50%; transform: translateX(-50%); }

.mv-header-right { display: flex; align-items: center; gap: 14px; }

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
.mv-status.proc .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.ok .mv-dot { background: #BDEBB5; }
.mv-status.err .mv-dot { background: #ef4444; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.mv-content { flex: 1; display: flex; overflow: hidden; }

.mv-panel {
  height: 100%; overflow: hidden;
  transition: width 0.4s cubic-bezier(0.25,0.8,0.25,1), opacity 0.3s;
}
.mv-panel.left { border-right: 1px solid rgba(255,255,255,0.06); }

/* Floating Panel Styles */
.mv-panel.right.floating {
  position: fixed !important;
  bottom: 20px !important;
  right: 20px !important;
  width: 240px !important;
  height: auto !important;
  z-index: 50 !important;
  border-radius: 12px;
  background: rgba(8, 8, 8, 0.4) !important;
  backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.mv-panel.right.floating:hover {
  background: rgba(8, 8, 8, 0.5) !important;
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}

.mv-float-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px 12px;
  gap: 8px;
  width: 100%;
  height: 100%;
}

.mv-tab-icon {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.mv-float-tab:hover .mv-tab-icon {
  color: rgba(255, 255, 255, 0.9);
  transform: translateY(2px);
}

.mv-tab-text {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
  transition: color 0.3s ease;
}

.mv-float-tab:hover .mv-tab-text {
  color: rgba(255, 255, 255, 0.8);
}

.mv-panel.right.expanded {
  position: static !important;
  width: 100% !important;
  height: 100% !important;
  background: #080808 !important;
  backdrop-filter: none;
  border: none;
  border-left: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: none;
  border-radius: 0;
}

.mv-panel-content {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
}

.mv-close-panel {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 28px;
  height: 28px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  font-size: 18px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  transition: all 0.2s ease;
}

.mv-close-panel:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.4);
  color: rgba(255, 255, 255, 0.9);
}
</style>
