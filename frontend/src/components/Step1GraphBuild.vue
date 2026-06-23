<template>
  <div class="cl">
    <div class="cl-head">
      <span class="cl-head-title">Análise de Cenário</span>
    </div>

    <div class="cl-body">
      <div class="cl-timeline">

        <!-- ── Step 1: Extração de ontologia ── -->
        <div class="cl-row" :class="{ 'cl-row--done': currentPhase > 0, 'cl-row--active': currentPhase === 0 }">
          <div class="cl-track">
            <div class="cl-node">
              <svg v-if="currentPhase > 0" viewBox="0 0 14 14" width="8" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="2.5 7 5.5 10 11.5 3.5"/></svg>
              <span v-else-if="currentPhase === 0" class="cl-spin"></span>
            </div>
            <div class="cl-line"></div>
          </div>
          <div class="cl-col">
            <div class="cl-label">Extração de ontologia</div>

            <!-- Active: sweep progress -->
            <div v-if="currentPhase === 0 && ontologyProgress" class="cl-scan">
              <div class="cl-scan-bar"><div class="cl-scan-fill"></div></div>
              <span class="cl-scan-msg">{{ ontologyProgress.message || 'Analisando documentos...' }}</span>
            </div>

            <!-- Detail overlay when a tag is clicked -->
            <div v-if="selectedOntologyItem" class="cl-detail">
              <div class="cl-detail-hd">
                <span class="cl-detail-type">{{ selectedOntologyItem.itemType === 'entity' ? 'ENTIDADE' : 'RELAÇÃO' }}</span>
                <span class="cl-detail-name">{{ selectedOntologyItem.name }}</span>
                <button class="cl-detail-x" @click="selectedOntologyItem = null">
                  <svg viewBox="0 0 16 16" width="11" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="3" x2="13" y2="13"/><line x1="13" y1="3" x2="3" y2="13"/></svg>
                </button>
              </div>
              <p class="cl-detail-desc">{{ selectedOntologyItem.description }}</p>
              <div v-if="selectedOntologyItem.attributes?.length" class="cl-detail-sect">
                <span class="cl-detail-lbl">ATRIBUTOS</span>
                <div class="cl-attr-list">
                  <div v-for="a in selectedOntologyItem.attributes" :key="a.name" class="cl-attr-row">
                    <span class="cl-attr-name">{{ a.name }}</span>
                    <span class="cl-attr-type">{{ a.type }}</span>
                    <span class="cl-attr-desc">{{ a.description }}</span>
                  </div>
                </div>
              </div>
              <div v-if="selectedOntologyItem.examples?.length" class="cl-detail-sect">
                <span class="cl-detail-lbl">EXEMPLOS</span>
                <div class="cl-chips">
                  <span v-for="ex in selectedOntologyItem.examples" :key="ex" class="cl-chip">{{ ex }}</span>
                </div>
              </div>
              <div v-if="selectedOntologyItem.source_targets?.length" class="cl-detail-sect">
                <span class="cl-detail-lbl">CONEXÕES</span>
                <div class="cl-conn-list">
                  <div v-for="(c, i) in selectedOntologyItem.source_targets" :key="i" class="cl-conn-row">
                    <span class="cl-conn-node">{{ c.source }}</span>
                    <div class="cl-conn-arrow">
                      <div class="cl-conn-line-inner"></div>
                      <svg viewBox="0 0 8 8" width="6" fill="currentColor"><polygon points="0,0 8,4 0,8"/></svg>
                    </div>
                    <span class="cl-conn-node">{{ c.target }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Done: ontology tag cloud -->
            <div v-if="currentPhase > 0 && projectData?.ontology" class="cl-onto">
              <div class="cl-onto-group">
                <span class="cl-onto-lbl">Entidades</span>
                <div class="cl-tags">
                  <button v-for="e in projectData.ontology.entity_types" :key="e.name" class="cl-tag cl-tag--e" @click="selectOntologyItem(e, 'entity')">{{ e.name }}</button>
                </div>
              </div>
              <div class="cl-onto-group">
                <span class="cl-onto-lbl">Relações</span>
                <div class="cl-tags">
                  <button v-for="r in projectData.ontology.relation_types" :key="r.name" class="cl-tag cl-tag--r" @click="selectOntologyItem(r, 'relation')">{{ r.name }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Step 2: Mapeamento de rede ── -->
        <div class="cl-row" :class="{ 'cl-row--done': currentPhase > 1, 'cl-row--active': currentPhase === 1, 'cl-row--pending': currentPhase < 1 }">
          <div class="cl-track">
            <div class="cl-node">
              <svg v-if="currentPhase > 1" viewBox="0 0 14 14" width="8" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="2.5 7 5.5 10 11.5 3.5"/></svg>
              <span v-else-if="currentPhase === 1" class="cl-spin"></span>
            </div>
            <div class="cl-line"></div>
          </div>
          <div class="cl-col">
            <div class="cl-label-row">
              <span class="cl-label">Mapeamento de rede</span>
              <span v-if="currentPhase === 1" class="cl-pct">{{ buildProgress?.progress || 0 }}%</span>
            </div>

            <div v-if="graphStats.nodes > 0" class="cl-stats">
              <span class="cl-stat"><strong>{{ graphStats.nodes }}</strong> nós</span>
              <span class="cl-stat-dot">·</span>
              <span class="cl-stat"><strong>{{ graphStats.edges }}</strong> arestas</span>
              <span class="cl-stat-dot">·</span>
              <span class="cl-stat"><strong>{{ graphStats.types }}</strong> tipos</span>
            </div>

            <div v-if="currentPhase === 1 && buildProgress" class="cl-prog">
              <div class="cl-prog-bar">
                <div class="cl-prog-fill" :style="{ width: (buildProgress.progress || 0) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Step 3: Rede pronta ── -->
        <div class="cl-row cl-row--last" :class="{ 'cl-row--active': currentPhase >= 2, 'cl-row--pending': currentPhase < 2 }">
          <div class="cl-track">
            <div class="cl-node">
              <svg v-if="currentPhase >= 2" viewBox="0 0 14 14" width="8" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="2.5 7 5.5 10 11.5 3.5"/></svg>
            </div>
          </div>
          <div class="cl-col">
            <span class="cl-label">Rede pronta</span>
            <div v-if="currentPhase >= 2" class="cl-ready-info">
              {{ graphStats.nodes }} nós · {{ graphStats.edges }} arestas disponíveis para simulação
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer action button -->
    <div v-if="currentPhase >= 2" class="cl-foot">
      <button class="cl-action" :disabled="creatingSimulation" @click="handleEnterEnvSetup">
        <span v-if="creatingSimulation" class="cl-btn-spin"></span>
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
/* ── SHELL ── */
.cl {
  height: 100%;
  background: var(--bg);
  display: flex; flex-direction: column;
  font-family: var(--font);
  overflow: hidden;
}

/* ── HEADER ── */
.cl-head {
  flex-shrink: 0; height: 48px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center;
  padding: 0 20px;
}
.cl-head-title {
  font-size: 0.64rem; font-weight: 700; letter-spacing: 0.1em;
  color: var(--text3); text-transform: uppercase;
}

/* ── BODY ── */
.cl-body {
  flex: 1; overflow-y: auto; padding: 28px 20px;
}
.cl-body::-webkit-scrollbar { width: 2px; }
.cl-body::-webkit-scrollbar-thumb { background: var(--border2); }

/* ── TIMELINE ── */
.cl-timeline { display: flex; flex-direction: column; }

.cl-row { display: flex; gap: 16px; min-height: 56px; }

/* ── TRACK ── */
.cl-track {
  display: flex; flex-direction: column; align-items: center;
  flex-shrink: 0; width: 22px;
}
.cl-node {
  width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
  border: 1.5px solid var(--border2);
  background: var(--bg);
  display: flex; align-items: center; justify-content: center;
  position: relative; z-index: 1;
  transition: border-color 0.25s, background 0.25s, color 0.25s;
}
.cl-row--active .cl-node {
  border-color: var(--green-border);
  background: var(--green-dim);
  color: var(--green-text);
}
.cl-row--done .cl-node {
  border-color: var(--green-border);
  background: rgba(189,235,181,0.06);
  color: var(--green-text);
}
.cl-row--pending .cl-node {
  border-color: var(--border);
  opacity: 0.35;
}
.cl-line {
  flex: 1; width: 1px; background: var(--border); margin-top: 4px;
  transition: background 0.25s;
}
.cl-row--done .cl-line { background: var(--green-border); opacity: 0.35; }
.cl-row--last .cl-line { display: none; }

.cl-spin {
  width: 10px; height: 10px; border-radius: 50%; display: block;
  border: 1.5px solid transparent;
  border-top-color: var(--green-text);
  animation: cl-rotate 0.85s linear infinite;
}
@keyframes cl-rotate { to { transform: rotate(360deg); } }

/* ── COLUMN ── */
.cl-col { flex: 1; min-width: 0; padding-bottom: 26px; }
.cl-row--last .cl-col { padding-bottom: 0; }

.cl-label {
  font-size: 0.78rem; font-weight: 600; color: var(--text3);
  line-height: 22px; letter-spacing: -0.01em;
  transition: color 0.2s;
}
.cl-row--active .cl-label { color: var(--text); }
.cl-row--done .cl-label { color: var(--text2); }
.cl-row--pending .cl-label { opacity: 0.4; }

.cl-label-row {
  display: flex; align-items: center; gap: 10px;
  justify-content: space-between; line-height: 22px;
}
.cl-pct {
  font-size: 0.64rem; font-weight: 700; color: var(--green-text);
  font-family: var(--mono, monospace); flex-shrink: 0;
}

/* ── SCANNING PROGRESS ── */
.cl-scan { margin-top: 8px; display: flex; flex-direction: column; gap: 6px; }
.cl-scan-bar {
  height: 2px; background: var(--border); border-radius: 2px; overflow: hidden;
}
.cl-scan-fill {
  height: 100%; width: 35%;
  background: linear-gradient(to right, transparent, var(--green-border), transparent);
  animation: cl-sweep 1.6s ease-in-out infinite;
}
@keyframes cl-sweep { 0%{transform:translateX(-180%)} 100%{transform:translateX(450%)} }
.cl-scan-msg { font-size: 0.63rem; color: var(--text3); }

/* ── ONTOLOGY TAGS ── */
.cl-onto { margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }
.cl-onto-group { display: flex; flex-direction: column; gap: 5px; }
.cl-onto-lbl {
  font-size: 0.55rem; font-weight: 700; letter-spacing: 0.1em;
  color: var(--text3); text-transform: uppercase;
}
.cl-tags { display: flex; flex-wrap: wrap; gap: 4px; }
.cl-tag {
  font-size: 0.61rem; padding: 3px 9px; border-radius: 4px;
  cursor: pointer; border: 1px solid var(--border);
  background: var(--bg3); color: var(--text2);
  font-family: inherit; transition: all 0.14s; letter-spacing: 0.01em;
}
.cl-tag--r { color: var(--text3); background: transparent; }
.cl-tag:hover { border-color: var(--border2); color: var(--text); background: var(--bg3); }

/* ── DETAIL PANEL ── */
.cl-detail {
  margin-top: 10px; padding: 12px;
  background: var(--bg3); border: 1px solid var(--border2);
  border-left: 2px solid var(--green-border);
  border-radius: 6px;
  display: flex; flex-direction: column; gap: 10px;
  animation: cl-fadein 0.14s ease;
}
@keyframes cl-fadein { from { opacity:0; transform: translateY(-4px); } to { opacity:1; } }
.cl-detail-hd { display: flex; align-items: center; gap: 8px; }
.cl-detail-type {
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em;
  background: var(--green-dim); color: var(--green-text);
  border: 1px solid var(--green-border); padding: 2px 6px; border-radius: 3px;
}
.cl-detail-name { font-size: 0.76rem; font-weight: 600; color: var(--text); flex: 1; }
.cl-detail-x {
  background: none; border: none; color: var(--text3);
  cursor: pointer; padding: 2px; display: flex; align-items: center; transition: color 0.12s;
}
.cl-detail-x:hover { color: var(--text); }
.cl-detail-desc { font-size: 0.67rem; color: var(--text3); line-height: 1.65; }
.cl-detail-sect { display: flex; flex-direction: column; gap: 5px; }
.cl-detail-lbl { font-size: 0.5rem; color: var(--text3); letter-spacing: 0.1em; }
.cl-attr-list { display: flex; flex-direction: column; gap: 3px; }
.cl-attr-row { display: flex; align-items: baseline; gap: 8px; font-size: 0.64rem; }
.cl-attr-name { color: var(--text); font-weight: 600; min-width: 70px; }
.cl-attr-type { color: var(--green-text); opacity: 0.55; font-size: 0.58rem; min-width: 44px; }
.cl-attr-desc { color: var(--text3); flex: 1; }
.cl-chips { display: flex; flex-wrap: wrap; gap: 3px; }
.cl-chip {
  font-size: 0.59rem; padding: 2px 7px; border-radius: 3px;
  background: var(--bg); border: 1px solid var(--border); color: var(--text3);
}
.cl-conn-list { display: flex; flex-direction: column; gap: 4px; }
.cl-conn-row { display: flex; align-items: center; gap: 6px; }
.cl-conn-node {
  font-size: 0.62rem; color: var(--text2);
  background: var(--bg); border: 1px solid var(--border);
  padding: 2px 7px; border-radius: 3px;
}
.cl-conn-arrow { display: flex; align-items: center; gap: 2px; flex: 1; color: var(--green-text); opacity: 0.4; }
.cl-conn-line-inner { flex: 1; height: 1px; background: currentColor; }

/* ── STATS ── */
.cl-stats { margin-top: 5px; display: flex; align-items: center; gap: 5px; }
.cl-stat { font-size: 0.65rem; color: var(--text3); }
.cl-stat strong { color: var(--text2); font-weight: 700; }
.cl-stat-dot { color: var(--border2); font-size: 0.5rem; }

/* ── PROGRESS BAR ── */
.cl-prog { margin-top: 8px; }
.cl-prog-bar { height: 2px; background: var(--border); border-radius: 2px; overflow: hidden; }
.cl-prog-fill {
  height: 100%;
  background: linear-gradient(to right, var(--green-border), var(--green-text));
  border-radius: 2px; transition: width 0.5s ease;
}

/* ── READY ── */
.cl-ready-info { margin-top: 4px; font-size: 0.65rem; color: var(--text3); line-height: 1.5; }

/* ── FOOTER ── */
.cl-foot {
  flex-shrink: 0; padding: 12px 16px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}
.cl-action {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 10px 20px; border-radius: 6px; border: none;
  background: var(--green-text, #BDEBB5); color: #000;
  font-family: var(--font); font-size: 0.72rem; font-weight: 700;
  letter-spacing: 0.01em; cursor: pointer; transition: all 0.14s;
}
.cl-action:hover:not(:disabled) { opacity: 0.9; }
.cl-action:disabled { background: var(--bg3); color: var(--text3); cursor: not-allowed; }
.cl-btn-spin {
  width: 11px; height: 11px; flex-shrink: 0; display: block;
  border: 1.5px solid rgba(0,0,0,0.18); border-top-color: #000;
  border-radius: 50%; animation: cl-rotate 0.8s linear infinite;
}
</style>
