<template>
  <div class="mv">
    <header class="mv-header">
      <div class="mv-header-left">
        <AppLogo class="mv-logo" @click="router.push('/')" style="cursor:pointer" />
      </div>

      <div class="mv-header-right">
        <span class="mv-status" :class="statusClass">
          <span class="mv-dot"></span>{{ statusText }}
        </span>
      </div>
    </header>

    <!-- Floating step progress pill -->
    <div class="mv-step-float">
      <div
        v-for="(name, i) in stepNames"
        :key="i"
        class="mv-sf-step"
        :class="{ active: currentStep === i+1, done: currentStep > i+1 }"
        :title="name"
      >
        <span class="mv-sf-num">{{ String(i+1).padStart(2,'0') }}</span>
        <span v-if="i < stepNames.length - 1" class="mv-sf-line"></span>
      </div>
    </div>

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
          <div class="mv-tab-step-num">{{ String(currentStep).padStart(2,'0') }}</div>
          <div class="mv-tab-name">{{ stepNames[currentStep-1] }}</div>
          <div class="mv-tab-expand">ABRIR ↑</div>
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
import AppLogo from '../components/AppLogo.vue'
import { generateOntology, getProject, buildGraph, getTaskStatus, getGraphData } from '../api/graph'
import { getPendingUpload, clearPendingUpload } from '../store/pendingUpload'

const route = useRoute()
const router = useRouter()
const panelExpanded = ref(false)
const currentStep = ref(1)
const stepNames = ['Mapear Cenário', 'Configurar Ambiente', 'Iniciar Simulação', 'Gerar Relatório', 'Interação Profunda']
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
  if (error.value) return 'Erro'
  if (currentPhase.value >= 2) return 'Pronto'
  if (currentPhase.value === 1) return 'Mapeando Rede'
  if (currentPhase.value === 0) return 'Analisando'
  return 'Inicializando'
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
  if (!pending.isPending) { error.value = 'No pending simulation data.'; return }
  try {
    loading.value = true; currentPhase.value = 0
    ontologyProgress.value = { message: 'Uploading and analyzing...' }
    addLog('Starting ontology generation...')
    const fd = new FormData()
    if (pending.files && pending.files.length > 0) {
      pending.files.forEach(f => fd.append('files', f))
    }
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
  background: var(--bg); overflow: hidden;
  font-family: var(--font);
}

/* ── HEADER ── */
.mv-header {
  flex-shrink: 0; height: 52px;
  border-bottom: 1px solid var(--border);
  background: var(--nav-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; position: relative; z-index: 10;
}
.mv-logo {
  height: 32px; width: auto; display: block;
  opacity: 0.9; transition: opacity 0.12s;
}
.mv-logo:hover { opacity: 1; }
.mv-header-right { display: flex; align-items: center; gap: 14px; }

.mv-status {
  display: flex; align-items: center; gap: 6px;
  font-family: var(--mono); font-size: 0.64rem;
  color: var(--text2); letter-spacing: 0.06em;
}
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text3); }
.mv-status.proc .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.ok .mv-dot { background: var(--green); }
.mv-status.err .mv-dot { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── FLOATING STEP PROGRESS PILL ── */
.mv-step-float {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 50;
  display: flex;
  align-items: center;
  background: var(--bg2);
  backdrop-filter: blur(14px) saturate(180%);
  -webkit-backdrop-filter: blur(14px) saturate(180%);
  border: 1px solid var(--border2);
  border-radius: 10px;
  box-shadow: var(--shadow-md);
  padding: 10px 16px;
  gap: 0;
  pointer-events: none;
}
.mv-sf-step { display: flex; align-items: center; gap: 0; }
.mv-sf-num {
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
  color: var(--text3);
  padding: 2px 6px; border-radius: 3px;
  transition: all 0.2s;
}
.mv-sf-step.done .mv-sf-num { color: var(--green-text); opacity: 0.55; }
.mv-sf-step.active .mv-sf-num {
  color: var(--green-text);
  background: var(--green-dim);
  border: 1px solid var(--green-border);
}
.mv-sf-line {
  display: inline-block;
  width: 18px; height: 1px;
  background: var(--border);
  margin: 0 2px;
}
.mv-sf-step.done .mv-sf-line { background: var(--green-border); opacity: 0.5; }

/* ── CONTENT LAYOUT ── */
.mv-content { flex: 1; display: flex; overflow: hidden; }
.mv-panel {
  height: 100%; overflow: hidden;
  transition: width 0.35s cubic-bezier(0.25,0.8,0.25,1);
}
.mv-panel.left { border-right: 1px solid var(--border); }

/* Floating workbench tab */
.mv-panel.right.floating {
  position: fixed !important;
  bottom: 20px !important; right: 20px !important;
  width: 200px !important; height: auto !important;
  z-index: 50 !important;
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
.mv-float-tab {
  display: flex; flex-direction: column;
  align-items: flex-start;
  padding: 14px 16px; gap: 3px;
  width: 100%; height: 100%;
}
.mv-tab-step-num {
  font-size: 1.1rem; font-weight: 700;
  color: var(--text3);
  line-height: 1;
}
.mv-tab-name {
  font-size: 0.7rem; font-weight: 600;
  color: var(--text);
  letter-spacing: 0.02em;
  line-height: 1.3;
}
.mv-tab-expand {
  font-size: 0.58rem; font-weight: 700;
  color: var(--green-text); opacity: 0.6;
  letter-spacing: 0.1em;
  margin-top: 4px;
}
.mv-panel.right.floating:hover .mv-tab-expand { opacity: 1; }
.mv-panel.right.floating:hover .mv-tab-step-num { color: var(--text2); }

/* Expanded workbench panel */
.mv-panel.right.expanded {
  position: static !important;
  width: 420px !important; min-width: 380px; height: 100% !important;
  background: var(--bg) !important; backdrop-filter: none;
  border: none; border-left: 1px solid var(--border);
  box-shadow: none; border-radius: 0; overflow: hidden;
  flex-shrink: 0;
}
.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }
.mv-close-panel {
  position: absolute; top: 12px; right: 12px;
  width: 26px; height: 26px;
  background: var(--surface-1); border: 1px solid var(--border2);
  color: var(--text2); font-size: 16px; cursor: pointer;
  border-radius: 5px; display: flex; align-items: center; justify-content: center;
  z-index: 100; transition: all 0.15s ease;
}
.mv-close-panel:hover {
  background: var(--surface-2);
  border-color: var(--text2); color: var(--text);
}
</style>
