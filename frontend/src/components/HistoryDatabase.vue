<template>
  <div class="hdb" ref="historyContainer">
    <div class="hdb-header">
      <span class="hdb-label">SIMULATION HISTORY</span>
      <span class="hdb-count" v-if="projects.length">{{ projects.length }} runs</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="hdb-loading">
      <span class="hdb-spinner"></span>
      <span>Loading history...</span>
    </div>

    <!-- Empty -->
    <div v-else-if="!projects.length" class="hdb-empty">
      <div class="hdb-empty-icon">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.2">
          <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/>
          <line x1="9" y1="21" x2="9" y2="9"/>
        </svg>
      </div>
      <span>No simulations yet. Run your first one above.</span>
    </div>

    <!-- Log table -->
    <div v-else class="hdb-table">
      <div class="hdb-thead">
        <span class="hdb-th" style="width:120px">ID</span>
        <span class="hdb-th" style="flex:1">DIRECTIVE</span>
        <span class="hdb-th" style="width:80px">FILES</span>
        <span class="hdb-th" style="width:100px">ROUNDS</span>
        <span class="hdb-th" style="width:90px">STATUS</span>
        <span class="hdb-th" style="width:120px">DATE</span>
        <span class="hdb-th" style="width:80px">OPEN</span>
      </div>

      <div
        v-for="(p, i) in projects"
        :key="p.simulation_id"
        class="hdb-row"
        @click="selectedProject = p"
      >
        <span class="hdb-cell hdb-id" style="width:120px">
          {{ formatSimulationId(p.simulation_id) }}
        </span>
        <span class="hdb-cell hdb-directive" style="flex:1">
          {{ truncateText(p.simulation_requirement, 60) || '—' }}
        </span>
        <span class="hdb-cell" style="width:80px; color: rgba(255,255,255,0.35);">
          {{ p.files?.length || 0 }} file{{ p.files?.length !== 1 ? 's' : '' }}
        </span>
        <span class="hdb-cell hdb-mono" style="width:100px">
          {{ formatRounds(p) }}
        </span>
        <span class="hdb-cell" style="width:90px">
          <span class="hdb-status" :class="getProgressClass(p)">
            {{ getStatusLabel(p) }}
          </span>
        </span>
        <span class="hdb-cell hdb-mono hdb-date" style="width:120px">
          {{ formatDate(p.created_at) }}
        </span>
        <span class="hdb-cell" style="width:80px">
          <span class="hdb-open-btn">Open →</span>
        </span>
      </div>
    </div>

    <!-- Detail modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedProject" class="hdb-modal-bg" @click.self="closeModal">
          <div class="hdb-modal">
            <div class="hdb-modal-top">
              <div class="hdb-modal-id">{{ formatSimulationId(selectedProject.simulation_id) }}</div>
              <div class="hdb-modal-meta">
                <span class="hdb-status" :class="getProgressClass(selectedProject)">{{ getStatusLabel(selectedProject) }}</span>
                <span class="hdb-mono" style="font-size:0.7rem;color:rgba(255,255,255,0.3)">{{ formatDate(selectedProject.created_at) }} {{ formatTime(selectedProject.created_at) }}</span>
              </div>
              <button class="hdb-modal-close" @click="closeModal">×</button>
            </div>

            <div class="hdb-modal-body">
              <div class="hdb-modal-section">
                <div class="hdb-modal-label">DIRECTIVE</div>
                <div class="hdb-modal-text">{{ selectedProject.simulation_requirement || 'None' }}</div>
              </div>

              <div class="hdb-modal-section" v-if="selectedProject.files?.length">
                <div class="hdb-modal-label">FILES</div>
                <div class="hdb-modal-files">
                  <span v-for="(f, i) in selectedProject.files" :key="i" class="hdb-modal-file">
                    {{ f.filename }}
                  </span>
                </div>
              </div>
            </div>

            <div class="hdb-modal-footer">
              <button class="hdb-modal-btn" @click="goToProject" :disabled="!selectedProject.project_id">
                <span>01</span> Graph Build
              </button>
              <button class="hdb-modal-btn" @click="goToSimulation">
                <span>02</span> Environment
              </button>
              <button class="hdb-modal-btn" @click="goToReport" :disabled="!selectedProject.report_id">
                <span>04</span> Report
              </button>
            </div>

            <div class="hdb-modal-hint">
              Step 3 (Simulation) and Step 5 (Deep Interaction) require a live environment and do not support replay.
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onActivated, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getSimulationHistory } from '../api/simulation'

const router = useRouter()
const route = useRoute()

const projects = ref([])
const loading = ref(true)
const selectedProject = ref(null)
const historyContainer = ref(null)

const getProgressClass = (s) => {
  const cur = s.current_round || 0
  const tot = s.total_rounds || 0
  if (tot === 0 || cur === 0) return 'st-idle'
  if (cur >= tot) return 'st-done'
  return 'st-running'
}

const getStatusLabel = (s) => {
  const cur = s.current_round || 0
  const tot = s.total_rounds || 0
  if (tot === 0 || cur === 0) return 'idle'
  if (cur >= tot) return 'complete'
  return 'running'
}

const formatDate = (d) => {
  if (!d) return '—'
  try { return new Date(d).toISOString().slice(0, 10) } catch { return d?.slice(0,10) || '—' }
}
const formatTime = (d) => {
  if (!d) return ''
  try {
    const dt = new Date(d)
    return `${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}`
  } catch { return '' }
}
const truncateText = (t, n) => !t ? '' : t.length > n ? t.slice(0,n) + '…' : t
const formatSimulationId = (id) => {
  if (!id) return 'SIM_???'
  return `SIM_${id.replace('sim_','').slice(0,6).toUpperCase()}`
}
const formatRounds = (s) => {
  const cur = s.current_round || 0
  const tot = s.total_rounds || 0
  if (tot === 0) return '—'
  return `${cur} / ${tot}`
}

const closeModal = () => { selectedProject.value = null }

const goToProject = () => {
  if (selectedProject.value?.project_id) {
    router.push({ name: 'Process', params: { projectId: selectedProject.value.project_id } })
    closeModal()
  }
}
const goToSimulation = () => {
  if (selectedProject.value?.simulation_id) {
    router.push({ name: 'Simulation', params: { simulationId: selectedProject.value.simulation_id } })
    closeModal()
  }
}
const goToReport = () => {
  if (selectedProject.value?.report_id) {
    router.push({ name: 'Report', params: { reportId: selectedProject.value.report_id } })
    closeModal()
  }
}

const loadHistory = async () => {
  try {
    loading.value = true
    const r = await getSimulationHistory(20)
    if (r.success) projects.value = r.data || []
  } catch { projects.value = [] }
  finally { loading.value = false }
}

watch(() => route.path, (p) => { if (p === '/') loadHistory() })
onMounted(loadHistory)
onActivated(loadHistory)
</script>

<style scoped>
.hdb {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 64px 80px;
  font-family: 'Plus Jakarta Sans', 'Manrope', system-ui, sans-serif;
}

.hdb-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 24px;
}
.hdb-label {
  font-family: 'DM Mono', 'JetBrains Mono', monospace;
  font-size: 0.62rem; letter-spacing: 0.16em;
  color: rgba(255,255,255,0.25);
}
.hdb-count {
  font-family: 'DM Mono', monospace; font-size: 0.62rem;
  color: rgba(255,255,255,0.2);
}

/* Loading */
.hdb-loading {
  display: flex; align-items: center; gap: 10px;
  padding: 32px 0; color: rgba(255,255,255,0.25); font-size: 0.82rem;
}
.hdb-spinner {
  width: 14px; height: 14px;
  border: 1.5px solid rgba(255,255,255,0.1);
  border-top-color: rgba(255,255,255,0.4);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Empty */
.hdb-empty {
  display: flex; align-items: center; gap: 12px;
  padding: 40px 0; color: rgba(255,255,255,0.2); font-size: 0.82rem;
}
.hdb-empty-icon { color: rgba(255,255,255,0.15); }

/* Table */
.hdb-table { display: flex; flex-direction: column; }

.hdb-thead {
  display: flex; align-items: center;
  padding: 0 16px 10px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  gap: 0;
}
.hdb-th {
  font-family: 'DM Mono', monospace;
  font-size: 0.58rem; letter-spacing: 0.12em;
  color: rgba(255,255,255,0.2); flex-shrink: 0;
}

.hdb-row {
  display: flex; align-items: center;
  padding: 13px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  cursor: pointer; gap: 0;
  transition: background 0.12s;
}
.hdb-row:hover { background: rgba(255,255,255,0.03); }
.hdb-row:hover .hdb-open-btn { opacity: 1; }

.hdb-cell {
  font-size: 0.8rem; color: rgba(255,255,255,0.5);
  flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.hdb-id {
  font-family: 'DM Mono', monospace;
  font-size: 0.7rem; color: rgba(255,255,255,0.35);
}
.hdb-directive { color: rgba(255,255,255,0.6); }
.hdb-mono { font-family: 'DM Mono', monospace; font-size: 0.72rem; }
.hdb-date { color: rgba(255,255,255,0.25); }

.hdb-status {
  display: inline-block;
  font-family: 'DM Mono', monospace; font-size: 0.6rem;
  letter-spacing: 0.1em; padding: 2px 8px; border-radius: 3px; font-weight: 500;
}
.st-idle { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.3); }
.st-running { background: rgba(251,191,36,0.1); color: #fbbf24; }
.st-done { background: rgba(189,235,181,0.15); color: #BDEBB5; }

.hdb-open-btn {
  font-family: 'DM Mono', monospace; font-size: 0.68rem;
  color: rgba(255,255,255,0.3); opacity: 0; transition: opacity 0.12s;
  letter-spacing: 0.04em;
}

/* Modal */
.hdb-modal-bg {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center; padding: 24px;
}
.hdb-modal {
  background: #0f0f0f; border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; width: 100%; max-width: 540px;
  overflow: hidden;
}

.hdb-modal-top {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  display: flex; align-items: center; gap: 12px;
}
.hdb-modal-id {
  font-family: 'DM Mono', monospace; font-size: 0.78rem;
  color: rgba(255,255,255,0.6); font-weight: 500; flex-shrink: 0;
}
.hdb-modal-meta { display: flex; align-items: center; gap: 10px; flex: 1; }
.hdb-modal-close {
  background: none; border: none; color: rgba(255,255,255,0.3);
  font-size: 1.2rem; cursor: pointer; padding: 0; line-height: 1;
  transition: color 0.12s; margin-left: auto; flex-shrink: 0;
}
.hdb-modal-close:hover { color: #fff; }

.hdb-modal-body { padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.hdb-modal-section { display: flex; flex-direction: column; gap: 6px; }
.hdb-modal-label {
  font-family: 'DM Mono', monospace; font-size: 0.58rem;
  letter-spacing: 0.14em; color: rgba(255,255,255,0.25);
}
.hdb-modal-text { font-size: 0.85rem; color: rgba(255,255,255,0.65); line-height: 1.6; }
.hdb-modal-files { display: flex; flex-direction: column; gap: 4px; }
.hdb-modal-file {
  font-family: 'DM Mono', monospace; font-size: 0.72rem;
  color: rgba(255,255,255,0.4); padding: 4px 0;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}

.hdb-modal-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255,255,255,0.07);
  display: flex; gap: 8px;
}
.hdb-modal-btn {
  flex: 1; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px; padding: 10px 8px;
  font-size: 0.78rem; color: rgba(255,255,255,0.55);
  cursor: pointer; transition: all 0.12s;
  font-family: 'Plus Jakarta Sans', sans-serif;
  display: flex; flex-direction: column; align-items: center; gap: 4px;
}
.hdb-modal-btn span:first-child {
  font-family: 'DM Mono', monospace; font-size: 0.6rem;
  color: rgba(255,255,255,0.2); letter-spacing: 0.08em;
}
.hdb-modal-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.08); color: #fff;
  border-color: rgba(255,255,255,0.15);
}
.hdb-modal-btn:disabled { opacity: 0.35; cursor: not-allowed; }

.hdb-modal-hint {
  padding: 12px 24px;
  font-size: 0.72rem; color: rgba(255,255,255,0.2); line-height: 1.5;
  border-top: 1px solid rgba(255,255,255,0.05);
}

/* Modal transition */
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .hdb-modal, .modal-leave-active .hdb-modal { transition: transform 0.2s ease; }
.modal-enter-from .hdb-modal, .modal-leave-to .hdb-modal { transform: translateY(8px); }

@media (max-width: 900px) { .hdb { padding: 48px 24px; } }
</style>
