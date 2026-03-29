<template>
  <div class="wb">
    <div class="wb-scroll">

      <!-- Step 01 -->
      <div class="wb-step" :class="{ active: currentPhase === 0, done: currentPhase > 0 }">
        <div class="wb-step-head">
          <div class="wb-step-left">
            <span class="wb-step-n">01</span>
            <span class="wb-step-title">Ontology Generation</span>
          </div>
          <span v-if="currentPhase > 0" class="wb-badge wb-badge--ok">COMPLETED</span>
          <span v-else-if="currentPhase === 0" class="wb-badge wb-badge--run">GENERATING</span>
          <span v-else class="wb-badge wb-badge--idle">PENDING</span>
        </div>

        <div class="wb-step-body">
          <span class="wb-endpoint">POST /api/graph/ontology/generate</span>
          <p class="wb-desc">LLM analyzes documents and simulation requirements, extracts real-world seeds, and generates the proper ontology structure.</p>

          <div v-if="currentPhase === 0 && ontologyProgress" class="wb-progress">
            <span class="wb-spinner"></span>
            <span>{{ ontologyProgress.message || 'Analyzing documents...' }}</span>
          </div>

          <!-- Ontology detail overlay -->
          <div v-if="selectedOntologyItem" class="wb-overlay">
            <div class="wb-overlay-head">
              <span class="wb-overlay-badge">{{ selectedOntologyItem.itemType === 'entity' ? 'ENTITY' : 'RELATION' }}</span>
              <span class="wb-overlay-name">{{ selectedOntologyItem.name }}</span>
              <button class="wb-overlay-close" @click="selectedOntologyItem = null">×</button>
            </div>
            <p class="wb-overlay-desc">{{ selectedOntologyItem.description }}</p>

            <div v-if="selectedOntologyItem.attributes?.length" class="wb-overlay-section">
              <span class="wb-overlay-label">ATTRIBUTES</span>
              <div class="wb-attr-list">
                <div v-for="a in selectedOntologyItem.attributes" :key="a.name" class="wb-attr">
                  <span class="wb-attr-name">{{ a.name }}</span>
                  <span class="wb-attr-type">{{ a.type }}</span>
                  <span class="wb-attr-desc">{{ a.description }}</span>
                </div>
              </div>
            </div>
            <div v-if="selectedOntologyItem.examples?.length" class="wb-overlay-section">
              <span class="wb-overlay-label">EXAMPLES</span>
              <div class="wb-ex-list">
                <span v-for="ex in selectedOntologyItem.examples" :key="ex" class="wb-ex">{{ ex }}</span>
              </div>
            </div>
            <div v-if="selectedOntologyItem.source_targets?.length" class="wb-overlay-section">
              <span class="wb-overlay-label">CONNECTIONS</span>
              <div class="wb-conn-list">
                <div v-for="(c, i) in selectedOntologyItem.source_targets" :key="i" class="wb-conn">
                  <span>{{ c.source }}</span><span class="wb-conn-arrow">→</span><span>{{ c.target }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Entity tags -->
          <div v-if="projectData?.ontology?.entity_types" class="wb-tags" :class="{ dim: selectedOntologyItem }">
            <span class="wb-tag-label">ENTITY TYPES</span>
            <div class="wb-tag-list">
              <span
                v-for="e in projectData.ontology.entity_types" :key="e.name"
                class="wb-tag wb-tag--entity"
                @click="selectOntologyItem(e, 'entity')"
              >{{ e.name }}</span>
            </div>
          </div>

          <!-- Relation tags -->
          <div v-if="projectData?.ontology?.edge_types" class="wb-tags" :class="{ dim: selectedOntologyItem }">
            <span class="wb-tag-label">RELATION TYPES</span>
            <div class="wb-tag-list">
              <span
                v-for="r in projectData.ontology.edge_types" :key="r.name"
                class="wb-tag wb-tag--relation"
                @click="selectOntologyItem(r, 'relation')"
              >{{ r.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 02 -->
      <div class="wb-step" :class="{ active: currentPhase === 1, done: currentPhase > 1 }">
        <div class="wb-step-head">
          <div class="wb-step-left">
            <span class="wb-step-n">02</span>
            <span class="wb-step-title">GraphRAG Build</span>
          </div>
          <span v-if="currentPhase > 1" class="wb-badge wb-badge--ok">COMPLETED</span>
          <span v-else-if="currentPhase === 1" class="wb-badge wb-badge--run">{{ buildProgress?.progress || 0 }}%</span>
          <span v-else class="wb-badge wb-badge--idle">PENDING</span>
        </div>

        <div class="wb-step-body">
          <span class="wb-endpoint">POST /api/graph/build</span>
          <p class="wb-desc">Documents are chunked and processed by Zep to build a knowledge graph, extract entities/relations, and form temporal memory plus community summaries.</p>

          <div class="wb-stats">
            <div class="wb-stat">
              <span class="wb-stat-val">{{ graphStats.nodes }}</span>
              <span class="wb-stat-key">NODES</span>
            </div>
            <div class="wb-stat">
              <span class="wb-stat-val">{{ graphStats.edges }}</span>
              <span class="wb-stat-key">EDGES</span>
            </div>
            <div class="wb-stat">
              <span class="wb-stat-val">{{ graphStats.types }}</span>
              <span class="wb-stat-key">TYPES</span>
            </div>
          </div>

          <!-- Progress bar when building -->
          <div v-if="currentPhase === 1 && buildProgress" class="wb-bar-wrap">
            <div class="wb-bar">
              <div class="wb-bar-fill" :style="{ width: (buildProgress.progress || 0) + '%' }"></div>
            </div>
            <span class="wb-bar-pct">{{ buildProgress.progress || 0 }}%</span>
          </div>
        </div>
      </div>

      <!-- Step 03 -->
      <div class="wb-step" :class="{ active: currentPhase >= 2 }">
        <div class="wb-step-head">
          <div class="wb-step-left">
            <span class="wb-step-n">03</span>
            <span class="wb-step-title">Build Complete</span>
          </div>
          <span v-if="currentPhase >= 2" class="wb-badge wb-badge--run">IN PROGRESS</span>
        </div>

        <div class="wb-step-body">
          <span class="wb-endpoint">POST /api/simulation/create</span>
          <p class="wb-desc">Graph build is complete. Continue to the next step: Environment Setup.</p>
          <button
            class="wb-action"
            :disabled="currentPhase < 2 || creatingSimulation"
            @click="handleEnterEnvSetup"
          >
            <span v-if="creatingSimulation" class="wb-spinner"></span>
            {{ creatingSimulation ? 'Creating simulation...' : 'Go to Environment Setup →' }}
          </button>
        </div>
      </div>

    </div>

    <!-- System log -->
    <div class="wb-log">
      <div class="wb-log-header">
        <span class="wb-log-label">SYSTEM DASHBOARD</span>
        <span class="wb-log-id">{{ projectData?.project_id || 'NO_PROJECT' }}</span>
      </div>
      <div class="wb-log-body" ref="logContent">
        <div class="wb-log-line" v-for="(log, i) in systemLogs" :key="i">
          <span class="wb-log-time">{{ log.time }}</span>
          <span class="wb-log-msg">{{ log.msg }}</span>
        </div>
      </div>
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
      alert('Failed to create simulation: ' + (res.error || 'Unknown error'))
    }
  } catch (err) {
    alert('Exception: ' + err.message)
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
  background: #080808;
  display: flex; flex-direction: column;
  font-family: 'Roboto Mono', 'JetBrains Mono', monospace;
  overflow: hidden;
}

.wb-scroll {
  flex: 1; overflow-y: auto;
  padding: 20px; display: flex; flex-direction: column; gap: 1px;
}
.wb-scroll::-webkit-scrollbar { width: 3px; }
.wb-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); }

/* ── STEP CARD ── */
.wb-step {
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
  margin-bottom: 8px;
}
.wb-step.active { border-color: rgba(255,255,255,0.14); }
.wb-step.done { border-color: rgba(34,197,94,0.15); }

.wb-step-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px;
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.wb-step.active .wb-step-head { background: rgba(255,255,255,0.04); }

.wb-step-left { display: flex; align-items: center; gap: 14px; }

.wb-step-n {
  font-size: 1.1rem; font-weight: 700;
  color: rgba(255,255,255,0.15);
}
.wb-step.active .wb-step-n,
.wb-step.done .wb-step-n { color: rgba(255,255,255,0.6); }

.wb-step-title {
  font-size: 0.82rem; font-weight: 600;
  color: rgba(255,255,255,0.5); letter-spacing: 0.02em;
}
.wb-step.active .wb-step-title { color: #fff; }

/* ── BADGES ── */
.wb-badge {
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
  padding: 3px 8px; border-radius: 3px;
}
.wb-badge--ok { background: rgba(34,197,94,0.1); color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
.wb-badge--run { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.55); border: 1px solid rgba(255,255,255,0.12); animation: blink 1.5s infinite; }
.wb-badge--idle { background: transparent; color: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.07); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* ── STEP BODY ── */
.wb-step-body { padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; }

.wb-endpoint {
  font-size: 0.65rem; color: rgba(255,255,255,0.2); letter-spacing: 0.06em;
}
.wb-desc { font-size: 0.75rem; color: rgba(255,255,255,0.35); line-height: 1.6; }

/* Progress spinner */
.wb-progress {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.72rem; color: rgba(255,255,255,0.4);
}
.wb-spinner {
  width: 12px; height: 12px; flex-shrink: 0;
  border: 1.5px solid rgba(255,255,255,0.1);
  border-top-color: rgba(255,255,255,0.5);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Tags */
.wb-tags { display: flex; flex-direction: column; gap: 8px; transition: opacity 0.2s; }
.wb-tags.dim { opacity: 0.2; pointer-events: none; }
.wb-tag-label {
  font-size: 0.58rem; color: rgba(255,255,255,0.2);
  letter-spacing: 0.12em;
}
.wb-tag-list { display: flex; flex-wrap: wrap; gap: 5px; }
.wb-tag {
  font-size: 0.68rem; padding: 3px 10px; border-radius: 3px;
  cursor: pointer; transition: all 0.12s; letter-spacing: 0.03em;
}
.wb-tag--entity {
  background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.08);
}
.wb-tag--entity:hover { background: rgba(255,255,255,0.1); color: #fff; border-color: rgba(255,255,255,0.2); }
.wb-tag--relation {
  background: rgba(255,255,255,0.03); color: rgba(255,255,255,0.35);
  border: 1px solid rgba(255,255,255,0.06);
}
.wb-tag--relation:hover { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7); }

/* Stats */
.wb-stats {
  display: flex; gap: 0;
  border: 1px solid rgba(255,255,255,0.07); border-radius: 6px; overflow: hidden;
}
.wb-stat {
  flex: 1; padding: 12px 16px; display: flex; flex-direction: column; gap: 4px;
  align-items: center; border-right: 1px solid rgba(255,255,255,0.07);
}
.wb-stat:last-child { border-right: none; }
.wb-stat-val {
  font-size: 1.3rem; font-weight: 700; color: #fff;
}
.wb-stat-key { font-size: 0.58rem; color: rgba(255,255,255,0.2); letter-spacing: 0.12em; }

/* Progress bar */
.wb-bar-wrap { display: flex; align-items: center; gap: 10px; }
.wb-bar {
  flex: 1; height: 2px; background: rgba(255,255,255,0.07); border-radius: 1px; overflow: hidden;
}
.wb-bar-fill { height: 100%; background: rgba(255,255,255,0.4); border-radius: 1px; transition: width 0.5s ease; }
.wb-bar-pct { font-size: 0.65rem; color: rgba(255,255,255,0.3); min-width: 30px; text-align: right; }

/* Action button */
.wb-action {
  display: flex; align-items: center; gap: 8px;
  background: #fff; color: #000;
  border: none; padding: 12px 20px; border-radius: 6px;
  font-family: 'Roboto Mono', monospace; font-size: 0.76rem; font-weight: 600;
  cursor: pointer; transition: opacity 0.12s; width: 100%; justify-content: center;
}
.wb-action:hover:not(:disabled) { opacity: 0.85; }
.wb-action:disabled { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.2); cursor: not-allowed; }

/* Overlay */
.wb-overlay {
  background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px; padding: 14px; display: flex; flex-direction: column; gap: 10px;
  animation: fadein 0.15s ease;
}
@keyframes fadein { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

.wb-overlay-head { display: flex; align-items: center; gap: 10px; }
.wb-overlay-badge {
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.1em;
  background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.5);
  border: 1px solid rgba(255,255,255,0.1); padding: 2px 7px; border-radius: 3px;
}
.wb-overlay-name { font-size: 0.82rem; font-weight: 600; color: #fff; flex: 1; }
.wb-overlay-close {
  background: none; border: none; color: rgba(255,255,255,0.3);
  font-size: 1.1rem; cursor: pointer; transition: color 0.1s;
}
.wb-overlay-close:hover { color: #fff; }
.wb-overlay-desc { font-size: 0.75rem; color: rgba(255,255,255,0.4); line-height: 1.6; }
.wb-overlay-section { display: flex; flex-direction: column; gap: 6px; }
.wb-overlay-label { font-size: 0.58rem; color: rgba(255,255,255,0.2); letter-spacing: 0.12em; }

.wb-attr-list { display: flex; flex-direction: column; gap: 4px; }
.wb-attr { display: flex; align-items: baseline; gap: 8px; font-size: 0.72rem; }
.wb-attr-name { color: rgba(255,255,255,0.6); font-weight: 600; }
.wb-attr-type { color: rgba(255,255,255,0.2); font-size: 0.65rem; }
.wb-attr-desc { color: rgba(255,255,255,0.3); flex: 1; }

.wb-ex-list { display: flex; flex-wrap: wrap; gap: 4px; }
.wb-ex {
  font-size: 0.65rem; padding: 2px 8px;
  background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.4);
  border: 1px solid rgba(255,255,255,0.08); border-radius: 3px;
}

.wb-conn-list { display: flex; flex-direction: column; gap: 4px; }
.wb-conn {
  display: flex; align-items: center; gap: 8px; font-size: 0.7rem;
  color: rgba(255,255,255,0.5);
}
.wb-conn-arrow { color: rgba(255,255,255,0.2); }

/* ── SYSTEM LOG ── */
.wb-log {
  flex-shrink: 0;
  background: #000; border-top: 1px solid rgba(255,255,255,0.07);
}
.wb-log-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 16px; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.wb-log-label {
  font-size: 0.58rem; color: rgba(255,255,255,0.2); letter-spacing: 0.12em;
}
.wb-log-id { font-size: 0.58rem; color: rgba(255,255,255,0.15); }

.wb-log-body {
  height: 72px; overflow-y: auto; padding: 6px 16px;
  display: flex; flex-direction: column; gap: 2px;
}
.wb-log-body::-webkit-scrollbar { width: 3px; }
.wb-log-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.06); }

.wb-log-line { display: flex; gap: 14px; font-size: 0.65rem; line-height: 1.5; }
.wb-log-time { color: rgba(255,255,255,0.2); min-width: 80px; flex-shrink: 0; }
.wb-log-msg { color: rgba(255,255,255,0.4); word-break: break-all; }
</style>
