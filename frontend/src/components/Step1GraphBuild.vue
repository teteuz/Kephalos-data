<template>
  <div class="wb">
    <div class="wb-scroll">

      <!-- Fase 01 -->
      <div class="wb-phase" :class="{ active: currentPhase === 0, done: currentPhase > 0 }">
        <div class="wb-phase-head">
          <div class="wb-phase-left">
            <div class="wb-phase-indicator">
              <div class="wb-phase-ring" :class="{ spinning: currentPhase === 0, complete: currentPhase > 0 }">
                <svg v-if="currentPhase > 0" viewBox="0 0 16 16" width="10" fill="none" stroke="#BDEBB5" stroke-width="2.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
                <span v-else class="wb-phase-dot"></span>
              </div>
            </div>
            <div class="wb-phase-meta">
              <span class="wb-phase-num">FASE 01</span>
              <span class="wb-phase-title">Geração de Ontologia</span>
            </div>
          </div>
          <div class="wb-phase-status">
            <span v-if="currentPhase > 0" class="wb-pill wb-pill--done">CONCLUÍDO</span>
            <span v-else-if="currentPhase === 0" class="wb-pill wb-pill--live">
              <span class="wb-live-dot"></span>PROCESSANDO
            </span>
            <span v-else class="wb-pill wb-pill--idle">AGUARDANDO</span>
          </div>
        </div>

        <div class="wb-phase-body">
          <div v-if="currentPhase === 0 && ontologyProgress" class="wb-activity">
            <div class="wb-activity-bar">
              <div class="wb-activity-fill"></div>
            </div>
            <span class="wb-activity-msg">{{ ontologyProgress.message || 'Analisando documentos...' }}</span>
          </div>

          <!-- Overlay de detalhe -->
          <div v-if="selectedOntologyItem" class="wb-detail">
            <div class="wb-detail-head">
              <div class="wb-detail-type">
                {{ selectedOntologyItem.itemType === 'entity' ? 'ENTIDADE' : 'RELAÇÃO' }}
              </div>
              <span class="wb-detail-name">{{ selectedOntologyItem.name }}</span>
              <button class="wb-detail-close" @click="selectedOntologyItem = null">
                <svg viewBox="0 0 16 16" width="12" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="3" x2="13" y2="13"/><line x1="13" y1="3" x2="3" y2="13"/></svg>
              </button>
            </div>
            <p class="wb-detail-desc">{{ selectedOntologyItem.description }}</p>
            <div v-if="selectedOntologyItem.attributes?.length" class="wb-detail-section">
              <span class="wb-detail-label">ATRIBUTOS</span>
              <div class="wb-attr-grid">
                <div v-for="a in selectedOntologyItem.attributes" :key="a.name" class="wb-attr-row">
                  <span class="wb-attr-name">{{ a.name }}</span>
                  <span class="wb-attr-type">{{ a.type }}</span>
                  <span class="wb-attr-desc">{{ a.description }}</span>
                </div>
              </div>
            </div>
            <div v-if="selectedOntologyItem.examples?.length" class="wb-detail-section">
              <span class="wb-detail-label">EXEMPLOS</span>
              <div class="wb-chips">
                <span v-for="ex in selectedOntologyItem.examples" :key="ex" class="wb-chip">{{ ex }}</span>
              </div>
            </div>
            <div v-if="selectedOntologyItem.source_targets?.length" class="wb-detail-section">
              <span class="wb-detail-label">CONEXÕES</span>
              <div class="wb-conn-list">
                <div v-for="(c, i) in selectedOntologyItem.source_targets" :key="i" class="wb-conn-row">
                  <span class="wb-conn-node">{{ c.source }}</span>
                  <div class="wb-conn-line">
                    <div class="wb-conn-arrow-line"></div>
                    <svg viewBox="0 0 8 8" width="6" fill="#BDEBB5"><polygon points="0,0 8,4 0,8"/></svg>
                  </div>
                  <span class="wb-conn-node">{{ c.target }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tags de ontologia -->
          <div v-if="currentPhase > 0 && projectData?.ontology" class="wb-ontology">
            <div class="wb-ontology-group">
              <span class="wb-ontology-label">
                <svg viewBox="0 0 12 12" width="9" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"><circle cx="6" cy="6" r="4"/></svg>
                ENTIDADES
              </span>
              <div class="wb-tag-row">
                <button
                  v-for="e in projectData.ontology.entity_types"
                  :key="e.name"
                  class="wb-tag wb-tag--entity"
                  @click="selectOntologyItem(e, 'entity')"
                >{{ e.name }}</button>
              </div>
            </div>
            <div class="wb-ontology-group">
              <span class="wb-ontology-label">
                <svg viewBox="0 0 12 12" width="9" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"><line x1="2" y1="6" x2="10" y2="6"/><polyline points="7 3 10 6 7 9"/></svg>
                RELAÇÕES
              </span>
              <div class="wb-tag-row">
                <button
                  v-for="r in projectData.ontology.relation_types"
                  :key="r.name"
                  class="wb-tag wb-tag--relation"
                  @click="selectOntologyItem(r, 'relation')"
                >{{ r.name }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fase 02 -->
      <div class="wb-phase" :class="{ active: currentPhase === 1, done: currentPhase > 1 }">
        <div class="wb-phase-head">
          <div class="wb-phase-left">
            <div class="wb-phase-indicator">
              <div class="wb-phase-ring" :class="{ spinning: currentPhase === 1, complete: currentPhase > 1 }">
                <svg v-if="currentPhase > 1" viewBox="0 0 16 16" width="10" fill="none" stroke="#BDEBB5" stroke-width="2.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
                <span v-else class="wb-phase-dot"></span>
              </div>
            </div>
            <div class="wb-phase-meta">
              <span class="wb-phase-num">FASE 02</span>
              <span class="wb-phase-title">Mapeamento de Cenário</span>
            </div>
          </div>
          <div class="wb-phase-status">
            <span v-if="currentPhase > 1" class="wb-pill wb-pill--done">CONCLUÍDO</span>
            <span v-else-if="currentPhase === 1" class="wb-pill wb-pill--live">
              <span class="wb-live-dot"></span>{{ buildProgress?.progress || 0 }}%
            </span>
            <span v-else class="wb-pill wb-pill--idle">AGUARDANDO</span>
          </div>
        </div>

        <div class="wb-phase-body">
          <!-- Métricas do grafo -->
          <div class="wb-metrics">
            <div class="wb-metric">
              <div class="wb-metric-value">{{ graphStats.nodes }}</div>
              <div class="wb-metric-label">NÓS</div>
              <div class="wb-metric-bar" :style="{ '--fill': Math.min(graphStats.nodes / 100, 1) }"></div>
            </div>
            <div class="wb-metric-divider"></div>
            <div class="wb-metric">
              <div class="wb-metric-value">{{ graphStats.edges }}</div>
              <div class="wb-metric-label">ARESTAS</div>
              <div class="wb-metric-bar" :style="{ '--fill': Math.min(graphStats.edges / 200, 1) }"></div>
            </div>
            <div class="wb-metric-divider"></div>
            <div class="wb-metric">
              <div class="wb-metric-value">{{ graphStats.types }}</div>
              <div class="wb-metric-label">TIPOS</div>
              <div class="wb-metric-bar" :style="{ '--fill': Math.min(graphStats.types / 20, 1) }"></div>
            </div>
          </div>

          <!-- Barra de progresso -->
          <div v-if="currentPhase === 1 && buildProgress" class="wb-progress-track">
            <div class="wb-progress-header">
              <span class="wb-progress-label">MAPEANDO REDE DE ENTIDADES</span>
              <span class="wb-progress-pct">{{ buildProgress.progress || 0 }}%</span>
            </div>
            <div class="wb-progress-bar">
              <div class="wb-progress-fill" :style="{ width: (buildProgress.progress || 0) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fase 03 -->
      <div class="wb-phase" :class="{ active: currentPhase >= 2 }">
        <div class="wb-phase-head">
          <div class="wb-phase-left">
            <div class="wb-phase-indicator">
              <div class="wb-phase-ring" :class="{ complete: currentPhase >= 2 }">
                <svg v-if="currentPhase >= 2" viewBox="0 0 16 16" width="10" fill="none" stroke="#BDEBB5" stroke-width="2.5"><polyline points="3 8 6.5 11.5 13 4"/></svg>
                <span v-else class="wb-phase-dot"></span>
              </div>
            </div>
            <div class="wb-phase-meta">
              <span class="wb-phase-num">FASE 03</span>
              <span class="wb-phase-title">Rede Mapeada</span>
            </div>
          </div>
          <div class="wb-phase-status">
            <span v-if="currentPhase >= 2" class="wb-pill wb-pill--ready">
              <svg viewBox="0 0 12 12" width="9" fill="none" stroke="#BDEBB5" stroke-width="2"><polyline points="2 6 5 9 10 3"/></svg>
              PRONTO
            </span>
          </div>
        </div>
        <div class="wb-phase-body" v-if="currentPhase >= 2">
          <div class="wb-ready-banner">
            <div class="wb-ready-icon">
              <svg viewBox="0 0 24 24" width="18" fill="none" stroke="#BDEBB5" stroke-width="1.5">
                <circle cx="12" cy="12" r="3"/><circle cx="4" cy="6" r="2"/><circle cx="20" cy="6" r="2"/>
                <circle cx="4" cy="18" r="2"/><circle cx="20" cy="18" r="2"/>
                <line x1="6" y1="6" x2="10" y2="11"/><line x1="18" y1="6" x2="14" y2="11"/>
                <line x1="6" y1="18" x2="10" y2="13"/><line x1="18" y1="18" x2="14" y2="13"/>
              </svg>
            </div>
            <div class="wb-ready-text">
              <div class="wb-ready-title">Rede de entidades mapeada com sucesso</div>
              <div class="wb-ready-sub">{{ graphStats.nodes }} nós · {{ graphStats.edges }} arestas · {{ graphStats.types }} tipos de entidade</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Barra de ação -->
    <div v-if="currentPhase >= 2" class="wb-action-bar">
      <button class="wb-action" :disabled="creatingSimulation" @click="handleEnterEnvSetup">
        <span v-if="creatingSimulation" class="wb-btn-spinner"></span>
        <span>{{ creatingSimulation ? 'Criando simulação...' : 'Configurar Ambiente' }}</span>
        <svg v-if="!creatingSimulation" viewBox="0 0 16 16" width="13" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
      </button>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { createSimulation } from '../api/simulation'

const router = useRouter()

const props = defineProps({
  currentPhase: { type: Number, default: 0 },
  projectData: Object,
  ontologyProgress: Object,
  buildProgress: Object,
  graphData: Object,
  systemLogs: { type: Array, default: () => [] }
})

defineEmits(['next-step'])

const selectedOntologyItem = ref(null)
const logContent = ref(null)
const creatingSimulation = ref(false)

const handleEnterEnvSetup = async () => {
  if (!props.projectData?.project_id || !props.projectData?.graph_id) return
  creatingSimulation.value = true
  try {
    const res = await createSimulation({
      project_id: props.projectData.project_id,
      graph_id: props.projectData.graph_id,
      enable_twitter: true,
      enable_reddit: true
    })
    if (res.success && res.data?.simulation_id) {
      router.push({ name: 'Simulation', params: { simulationId: res.data.simulation_id } })
    } else {
      alert('Erro ao criar simulação: ' + (res.error || 'Erro desconhecido'))
    }
  } catch (err) {
    alert('Exceção: ' + err.message)
  } finally {
    creatingSimulation.value = false
  }
}

const selectOntologyItem = (item, type) => {
  selectedOntologyItem.value = { ...item, itemType: type }
}

const graphStats = computed(() => ({
  nodes: props.graphData?.node_count || props.graphData?.nodes?.length || 0,
  edges: props.graphData?.edge_count || props.graphData?.edges?.length || 0,
  types: props.projectData?.ontology?.entity_types?.length || 0
}))

watch(() => props.systemLogs.length, () => {
  nextTick(() => { if (logContent.value) logContent.value.scrollTop = logContent.value.scrollHeight })
})
</script>

<style scoped>
/* ── BASE ── */
.wb {
  height: 100%;
  background: var(--bg);
  display: flex; flex-direction: column;
  font-family: 'Roboto Mono', 'JetBrains Mono', monospace;
  overflow: hidden;
}

.wb-scroll {
  flex: 1; overflow-y: auto;
  padding: 12px; display: flex; flex-direction: column; gap: 6px;
}
.wb-scroll::-webkit-scrollbar { width: 2px; }
.wb-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); }

/* ── PHASE CARD ── */
.wb-phase {
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.05);
  background: rgba(255,255,255,0.015);
  overflow: hidden;
  transition: border-color 0.3s, background 0.3s;
}
.wb-phase.active {
  border-color: rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.03);
}
.wb-phase.done {
  border-color: rgba(189,235,181,0.12);
  background: rgba(189,235,181,0.015);
}

/* ── PHASE HEAD ── */
.wb-phase-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
}

.wb-phase-left { display: flex; align-items: center; gap: 12px; }

/* Phase ring indicator */
.wb-phase-indicator { flex-shrink: 0; }
.wb-phase-ring {
  width: 28px; height: 28px; border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  transition: border-color 0.3s;
}
.wb-phase-ring.spinning {
  border-color: transparent;
  border-top-color: rgba(255,255,255,0.4);
  animation: spin 1s linear infinite;
}
.wb-phase-ring.complete {
  border-color: rgba(189,235,181,0.4);
  background: rgba(189,235,181,0.06);
}
@keyframes spin { to { transform: rotate(360deg); } }

.wb-phase-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: rgba(255,255,255,0.15);
}

.wb-phase-meta { display: flex; flex-direction: column; gap: 2px; }
.wb-phase-num {
  font-size: 0.52rem; font-weight: 700; letter-spacing: 0.16em;
  color: rgba(255,255,255,0.2);
}
.wb-phase.active .wb-phase-num { color: rgba(189,235,181,0.5); }
.wb-phase.done .wb-phase-num { color: rgba(189,235,181,0.35); }

.wb-phase-title {
  font-size: 0.76rem; font-weight: 600;
  color: rgba(255,255,255,0.25); letter-spacing: 0.02em;
  font-family: var(--font);
}
.wb-phase.active .wb-phase-title { color: rgba(255,255,255,0.88); }
.wb-phase.done .wb-phase-title { color: rgba(255,255,255,0.5); }

/* ── PILLS ── */
.wb-pill {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.52rem; font-weight: 700; letter-spacing: 0.12em;
  padding: 3px 10px; border-radius: 20px;
}
.wb-pill--idle {
  background: rgba(255,255,255,0.03);
  color: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.06);
}
.wb-pill--live {
  background: rgba(255,255,255,0.04);
  color: rgba(255,255,255,0.55);
  border: 1px solid rgba(255,255,255,0.1);
}
.wb-pill--done {
  background: rgba(189,235,181,0.07);
  color: rgba(189,235,181,0.7);
  border: 1px solid rgba(189,235,181,0.15);
}
.wb-pill--ready {
  background: rgba(189,235,181,0.08);
  color: #BDEBB5;
  border: 1px solid rgba(189,235,181,0.25);
}

.wb-live-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: rgba(255,255,255,0.5);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* ── PHASE BODY ── */
.wb-phase-body {
  padding: 12px 16px 14px;
  border-top: 1px solid rgba(255,255,255,0.04);
  display: flex; flex-direction: column; gap: 10px;
}

/* ── ACTIVITY BAR ── */
.wb-activity { display: flex; flex-direction: column; gap: 7px; }
.wb-activity-bar {
  height: 1px; background: rgba(255,255,255,0.05); border-radius: 1px; overflow: hidden;
}
.wb-activity-fill {
  height: 100%; width: 40%;
  background: linear-gradient(to right, transparent, rgba(255,255,255,0.3), transparent);
  animation: sweep 1.8s ease-in-out infinite;
}
@keyframes sweep { 0%{transform:translateX(-200%)} 100%{transform:translateX(400%)} }
.wb-activity-msg { font-size: 0.66rem; color: rgba(255,255,255,0.28); }

/* ── ONTOLOGY TAGS ── */
.wb-ontology { display: flex; flex-direction: column; gap: 10px; }
.wb-ontology-group { display: flex; flex-direction: column; gap: 6px; }
.wb-ontology-label {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.54rem; color: rgba(255,255,255,0.2); letter-spacing: 0.12em;
}
.wb-tag-row { display: flex; flex-wrap: wrap; gap: 4px; }
.wb-tag {
  font-size: 0.64rem; padding: 3px 9px; border-radius: 4px;
  cursor: pointer; transition: all 0.15s; letter-spacing: 0.02em;
  font-family: inherit;
}
.wb-tag--entity {
  background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.4);
  border: 1px solid rgba(255,255,255,0.07);
}
.wb-tag--entity:hover {
  background: rgba(255,255,255,0.08); color: #fff;
  border-color: rgba(255,255,255,0.18);
}
.wb-tag--relation {
  background: transparent; color: rgba(255,255,255,0.25);
  border: 1px solid rgba(255,255,255,0.05);
}
.wb-tag--relation:hover {
  background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.55);
}

/* ── DETAIL PANEL ── */
.wb-detail {
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.08);
  border-left: 2px solid rgba(189,235,181,0.3);
  border-radius: 6px; padding: 12px;
  display: flex; flex-direction: column; gap: 10px;
  animation: slidein 0.15s ease;
}
@keyframes slidein { from { opacity:0; transform: translateY(-4px); } to { opacity:1; transform:none; } }

.wb-detail-head { display: flex; align-items: center; gap: 8px; }
.wb-detail-type {
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.14em;
  background: rgba(189,235,181,0.08); color: rgba(189,235,181,0.6);
  border: 1px solid rgba(189,235,181,0.15); padding: 2px 6px; border-radius: 3px;
}
.wb-detail-name { font-size: 0.8rem; font-weight: 600; color: #fff; flex: 1; }
.wb-detail-close {
  background: none; border: none; color: rgba(255,255,255,0.2);
  cursor: pointer; padding: 2px; transition: color 0.12s;
  display: flex; align-items: center;
}
.wb-detail-close:hover { color: rgba(255,255,255,0.7); }
.wb-detail-desc { font-size: 0.7rem; color: rgba(255,255,255,0.35); line-height: 1.65; }
.wb-detail-section { display: flex; flex-direction: column; gap: 6px; }
.wb-detail-label { font-size: 0.5rem; color: rgba(255,255,255,0.18); letter-spacing: 0.14em; }

.wb-attr-grid { display: flex; flex-direction: column; gap: 4px; }
.wb-attr-row { display: flex; align-items: baseline; gap: 8px; font-size: 0.68rem; }
.wb-attr-name { color: rgba(255,255,255,0.6); font-weight: 600; min-width: 80px; }
.wb-attr-type { color: rgba(189,235,181,0.4); font-size: 0.6rem; min-width: 50px; }
.wb-attr-desc { color: rgba(255,255,255,0.28); flex: 1; }

.wb-chips { display: flex; flex-wrap: wrap; gap: 4px; }
.wb-chip {
  font-size: 0.62rem; padding: 2px 8px;
  background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.35);
  border: 1px solid rgba(255,255,255,0.07); border-radius: 3px;
}

.wb-conn-list { display: flex; flex-direction: column; gap: 5px; }
.wb-conn-row { display: flex; align-items: center; gap: 8px; }
.wb-conn-node {
  font-size: 0.66rem; color: rgba(255,255,255,0.5);
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
  padding: 2px 8px; border-radius: 3px;
}
.wb-conn-line { display: flex; align-items: center; gap: 2px; flex: 1; }
.wb-conn-arrow-line {
  flex: 1; height: 1px;
  background: linear-gradient(to right, rgba(189,235,181,0.15), rgba(189,235,181,0.4));
}

/* ── METRICS ── */
.wb-metrics {
  display: flex; align-items: stretch;
  background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.05);
  border-radius: 7px; overflow: hidden;
}
.wb-metric {
  flex: 1; padding: 12px 14px;
  display: flex; flex-direction: column; gap: 4px;
}
.wb-metric-divider { width: 1px; background: rgba(255,255,255,0.05); flex-shrink: 0; }
.wb-metric-value {
  font-size: 1.5rem; font-weight: 700; color: #fff; line-height: 1;
  letter-spacing: -0.02em;
}
.wb-phase.active .wb-metric-value { color: #fff; }
.wb-metric-label {
  font-size: 0.5rem; color: rgba(255,255,255,0.2); letter-spacing: 0.14em;
}
.wb-metric-bar {
  margin-top: 6px; height: 2px;
  background: rgba(255,255,255,0.05); border-radius: 1px; overflow: hidden;
  position: relative;
}
.wb-metric-bar::after {
  content: ''; position: absolute; inset: 0;
  background: rgba(189,235,181,0.5);
  width: calc(var(--fill, 0) * 100%);
  transition: width 0.6s ease;
}

/* ── PROGRESS TRACK ── */
.wb-progress-track { display: flex; flex-direction: column; gap: 6px; }
.wb-progress-header {
  display: flex; justify-content: space-between; align-items: center;
}
.wb-progress-label { font-size: 0.52rem; color: rgba(255,255,255,0.2); letter-spacing: 0.12em; }
.wb-progress-pct { font-size: 0.62rem; color: rgba(189,235,181,0.6); font-weight: 700; }
.wb-progress-bar {
  height: 2px; background: rgba(255,255,255,0.05); border-radius: 1px; overflow: hidden;
}
.wb-progress-fill {
  height: 100%;
  background: linear-gradient(to right, rgba(189,235,181,0.3), rgba(189,235,181,0.7));
  border-radius: 1px; transition: width 0.5s ease;
}

/* ── READY BANNER ── */
.wb-ready-banner {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 10px 12px;
  background: rgba(189,235,181,0.04);
  border: 1px solid rgba(189,235,181,0.1);
  border-radius: 6px;
}
.wb-ready-icon {
  width: 36px; height: 36px; border-radius: 8px;
  background: rgba(189,235,181,0.06); border: 1px solid rgba(189,235,181,0.12);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.wb-ready-title { font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.8); margin-bottom: 4px; }
.wb-ready-sub { font-size: 0.62rem; color: rgba(255,255,255,0.3); }

/* ── ACTION BAR ── */
.wb-action-bar {
  flex-shrink: 0; padding: 10px 12px;
  background: rgba(6,6,6,0.8); backdrop-filter: blur(16px);
  border-top: 1px solid rgba(255,255,255,0.06);
}
.wb-action {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 11px 20px; border-radius: 6px; border: none;
  background: rgba(189,235,181,0.9); color: #000;
  font-family: 'Roboto Mono', monospace; font-size: 0.72rem; font-weight: 700;
  letter-spacing: 0.04em; cursor: pointer; transition: all 0.15s;
}
.wb-action:hover:not(:disabled) { background: #BDEBB5; }
.wb-action:disabled {
  background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.15); cursor: not-allowed;
}

.wb-btn-spinner {
  width: 11px; height: 11px; flex-shrink: 0;
  border: 1.5px solid rgba(0,0,0,0.2);
  border-top-color: #000; border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
