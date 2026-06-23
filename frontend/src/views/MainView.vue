<template>
  <div class="mv">
    <header class="mv-header">
      <div class="mv-header-left">
        <AppLogo class="mv-logo" @click="router.push('/')" style="cursor:pointer" />
      </div>

      <div class="mv-header-center">
        <span class="mv-crumb">
          <span class="mv-crumb-project">{{ projectData?.project_name || 'Novo Cenário' }}</span>
          <span class="mv-crumb-sep">/</span>
          <span class="mv-crumb-step">{{ stepNames[currentStep - 1] }}</span>
        </span>
      </div>

      <div class="mv-header-right">
        <span class="mv-status" :class="statusClass">
          <span class="mv-dot"></span>{{ statusText }}
        </span>
      </div>
    </header>

    <main class="mv-content">
      <div class="mv-panel console">
        <div class="mv-panel-content">
          <Transition name="step" mode="out-in">
            <Step1GraphBuild
              v-if="currentStep === 1"
              :key="1"
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
              :key="2"
              :projectData="projectData"
              :graphData="graphData"
              :systemLogs="systemLogs"
              @go-back="handleGoBack"
              @next-step="handleNextStep"
              @add-log="addLog"
            />
          </Transition>
        </div>
      </div>
      <div class="mv-panel canvas">
        <GraphPanel
          :graphData="graphData"
          :loading="graphLoading"
          :currentPhase="currentPhase"
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
import Step1GraphBuild from '../components/Step1GraphBuild.vue'
import Step2EnvSetup from '../components/Step2EnvSetup.vue'
import AppLogo from '../components/AppLogo.vue'
import { generateOntology, getProject, buildGraph, getTaskStatus, getGraphData } from '../api/graph'
import { getPendingUpload, clearPendingUpload } from '../store/pendingUpload'

const route = useRoute()
const router = useRouter()
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
    addLog(`Etapa ${currentStep.value}: ${stepNames[currentStep.value - 1]}`)
  }
}
const handleGoBack = () => {
  if (currentStep.value > 1) { currentStep.value--; addLog(`Voltando para Etapa ${currentStep.value}`) }
}

const initProject = async () => {
  addLog('Carregando dados do projeto...')
  currentProjectId.value === 'new' ? await handleNewProject() : await loadProject()
}
const handleNewProject = async () => {
  const pending = getPendingUpload()
  if (!pending.isPending) { error.value = 'Nenhum dado de simulação pendente.'; return }
  try {
    loading.value = true; currentPhase.value = 0
    ontologyProgress.value = { message: 'Enviando e analisando documentos...' }
    addLog('Iniciando geração de ontologia... isso pode levar 1-2 minutos')
    const fd = new FormData()
    if (pending.files && pending.files.length > 0) {
      pending.files.forEach(f => fd.append('files', f))
    }
    fd.append('simulation_requirement', pending.simulationRequirement)
    if (pending.projectName) fd.append('project_name', pending.projectName)
    const res = await generateOntology(fd)
    if (res.success) {
      clearPendingUpload()
      currentProjectId.value = res.data.project_id
      projectData.value = res.data
      router.replace({ name: 'Process', params: { projectId: res.data.project_id } })
      ontologyProgress.value = null
      addLog('✓ Ontologia gerada com sucesso')
      await startBuildGraph()
    } else { error.value = res.error || 'Falha na geração'; addLog(`Erro: ${error.value}`) }
  } catch (err) { error.value = err.message; addLog(`Erro inesperado: ${err.message}`) }
  finally { loading.value = false }
}
const loadProject = async () => {
  try {
    loading.value = true
    const res = await getProject(currentProjectId.value)
    if (res.success) {
      projectData.value = res.data
      updatePhaseByStatus(res.data.status)
      addLog('✓ Projeto carregado')
      if (res.data.status === 'ontology_generated' && !res.data.graph_id) await startBuildGraph()
      else if (res.data.status === 'graph_building') { currentPhase.value = 1; startPollingTask(res.data.graph_build_task_id); startGraphPolling() }
      else if (res.data.status === 'graph_completed' && res.data.graph_id) { currentPhase.value = 2; await loadGraph(res.data.graph_id) }
    } else { error.value = res.error; addLog(`Erro ao carregar: ${res.error}`) }
  } catch (err) { error.value = err.message }
  finally { loading.value = false }
}
const updatePhaseByStatus = (s) => {
  const m = { created: 0, ontology_generated: 0, graph_building: 1, graph_completed: 2 }
  if (s === 'failed') error.value = 'Falha no processamento'
  else currentPhase.value = m[s] ?? -1
}
const startBuildGraph = async () => {
  try {
    currentPhase.value = 1; buildProgress.value = { progress: 0 }
    addLog('Construindo rede de entidades... aguarde')
    const res = await buildGraph({ project_id: currentProjectId.value })
    if (res.success) { startGraphPolling(); startPollingTask(res.data.task_id) }
    else { error.value = res.error; addLog(`Erro: ${res.error}`) }
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
        addLog('✓ Rede de entidades construída com sucesso!'); stopPolling(); stopGraphPolling(); currentPhase.value = 2
        const pr = await getProject(currentProjectId.value)
        if (pr.success && pr.data.graph_id) { projectData.value = pr.data; await loadGraph(pr.data.graph_id) }
      } else if (t.status === 'failed') { stopPolling(); error.value = t.error; addLog(`Falha: ${t.error}`) }
    }
  } catch (e) { console.error(e) }
}
const loadGraph = async (id) => {
  graphLoading.value = true
  try { const r = await getGraphData(id); if (r.success) { graphData.value = r.data; addLog('✓ Grafo carregado') } }
  catch (e) { addLog(`Erro ao carregar grafo: ${e.message}`) }
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
.mv-header-center { flex: 1; display: flex; align-items: center; justify-content: center; }
.mv-header-right { display: flex; align-items: center; gap: 14px; }

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
  font-family: var(--mono); font-size: 0.64rem;
  color: var(--text2); letter-spacing: 0.06em;
}
.mv-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text3); }
.mv-status.proc .mv-dot { background: #3b82f6; animation: blink 1.2s infinite; }
.mv-status.ok .mv-dot { background: var(--green); }
.mv-status.err .mv-dot { background: var(--red); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── CONTENT LAYOUT ── */
.mv-content { flex: 1; display: flex; overflow: hidden; }
.mv-panel { height: 100%; overflow: hidden; }

.mv-panel.console {
  width: 380px; min-width: 360px; flex-shrink: 0;
  background: var(--bg);
  border-right: 1px solid var(--border);
  overflow: hidden;
}
.mv-panel.canvas { flex: 1; min-width: 0; }
.mv-panel-content { width: 100%; height: 100%; overflow: hidden; position: relative; }

/* ── STEP TRANSITION ── */
.step-enter-active, .step-leave-active {
  transition: opacity 0.18s ease, transform 0.2s ease;
}
.step-enter-from { opacity: 0; transform: translateX(14px); }
.step-leave-to   { opacity: 0; transform: translateX(-14px); }
</style>
