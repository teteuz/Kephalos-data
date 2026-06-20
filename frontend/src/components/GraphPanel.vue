<template>
  <div class="graph-panel">
    <div class="panel-header">
      <!-- Top toolbar (Internal Top Right) -->
      <div class="header-tools">
        <button class="tool-btn" @click="$emit('refresh')" :disabled="loading" title="Refresh graph">
          <span class="icon-refresh" :class="{ 'spinning': loading }">↻</span>
          <span class="btn-text">Refresh</span>
        </button>
        
        <!-- Simulation Control Buttons -->
        <div v-if="isSimulating" class="simulation-controls">
          <button class="tool-btn control-btn" @click="$emit('pause-simulation')" title="Pause simulation">
            <span class="icon-pause">⏸</span>
            <span class="btn-text">Pause</span>
          </button>
          <button class="tool-btn control-btn resume-btn" @click="$emit('resume-simulation')" title="Resume simulation">
            <span class="icon-play">▶</span>
            <span class="btn-text">Resume</span>
          </button>
        </div>
      </div>
    </div>
    
    <div class="graph-container" ref="graphContainer">
      <!-- Tooltip -->
      <div v-if="tooltip.visible" class="graph-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <div class="tooltip-title">{{ tooltip.title }}</div>
        <div class="tooltip-content">{{ tooltip.content }}</div>
      </div>

      <!-- Mobile node list (replaces globe on small screens) -->
      <div v-if="graphData && isMobile" class="mobile-graph-list">
        <div class="mgl-header">
          <span class="mgl-title">Entidades do Grafo</span>
          <span class="mgl-count">{{ (graphData.nodes || []).length }} nós · {{ (graphData.edges || []).length }} arestas</span>
        </div>
        <input v-model="mobileSearch" class="mgl-search" placeholder="Buscar nó..." />
        <div class="mgl-nodes">
          <div
            v-for="node in filteredMobileNodes"
            :key="node.uuid"
            class="mgl-node"
            :class="{ selected: selectedItem && selectedItem.data && selectedItem.data.uuid === node.uuid }"
            @click="selectMobileNode(node)"
          >
            <span class="mgl-dot" :style="{ background: getNodeColor(node) }"></span>
            <span class="mgl-name">{{ node.name || 'Unnamed' }}</span>
            <span class="mgl-type">{{ getNodeType(node) }}</span>
          </div>
        </div>
        <!-- Detail panel reused -->
        <div v-if="selectedItem" class="detail-panel mgl-detail">
          <div class="detail-panel-header">
            <span class="detail-title">{{ selectedItem.type === 'node' ? 'Detalhes' : 'Relação' }}</span>
            <span v-if="selectedItem.type === 'node'" class="detail-type-badge" :style="{ background: selectedItem.color, color: '#fff' }">{{ selectedItem.entityType }}</span>
            <button class="detail-close" @click="closeDetailPanel">×</button>
          </div>
          <div class="detail-content" v-if="selectedItem.type === 'node'">
            <div class="detail-row">
              <span class="detail-label">Name:</span>
              <span class="detail-value">{{ selectedItem.data.name }}</span>
            </div>
            <div class="detail-section" v-if="selectedItem.data.summary">
              <div class="section-title">Summary:</div>
              <div class="summary-text">{{ selectedItem.data.summary }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Graph visualization (desktop only) -->
      <div v-if="graphData && !isMobile" class="graph-view">
        <svg ref="graphSvg" class="graph-svg"></svg>
        
 <!-- Building/ -->
        <div v-if="currentPhase === 1 || isSimulating" class="graph-building-hint">
          <div class="memory-icon-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="memory-icon">
              <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-4.04z" />
              <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-4.04z" />
            </svg>
          </div>
          {{ isSimulating ? 'GraphRAG short/long-term memory updating in real time' : 'Updating in real-time...' }}
        </div>
        
 <!-- -->
        <div v-if="showSimulationFinishedHint" class="graph-building-hint finished-hint">
          <div class="hint-icon-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="hint-icon">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <span class="hint-text">A small amount of content is still processing. Please refresh the graph shortly.</span>
          <button class="hint-close-btn" @click="dismissFinishedHint" title="Close hint">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <!-- Node/edge detail panel -->
        <div v-if="selectedItem" class="detail-panel">
          <div class="detail-panel-header">
            <span class="detail-title">{{ selectedItem.type === 'node' ? 'Node Details' : 'Relationship' }}</span>
            <span v-if="selectedItem.type === 'node'" class="detail-type-badge" :style="{ background: selectedItem.color, color: '#fff' }">
              {{ selectedItem.entityType }}
            </span>
            <button class="detail-close" @click="closeDetailPanel">×</button>
          </div>
          
          <!-- Node details -->
          <div v-if="selectedItem.type === 'node'" class="detail-content">
            <div class="detail-row">
              <span class="detail-label">Name:</span>
              <span class="detail-value">{{ selectedItem.data.name }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">UUID:</span>
              <span class="detail-value uuid-text">{{ selectedItem.data.uuid }}</span>
            </div>
            <div class="detail-row" v-if="selectedItem.data.created_at">
              <span class="detail-label">Created:</span>
              <span class="detail-value">{{ formatDateTime(selectedItem.data.created_at) }}</span>
            </div>
            
            <!-- Properties -->
            <div class="detail-section" v-if="selectedItem.data.attributes && Object.keys(selectedItem.data.attributes).length > 0">
              <div class="section-title">Properties:</div>
              <div class="properties-list">
                <div v-for="(value, key) in selectedItem.data.attributes" :key="key" class="property-item">
                  <span class="property-key">{{ key }}:</span>
                  <span class="property-value">{{ value || 'None' }}</span>
                </div>
              </div>
            </div>
            
            <!-- Summary -->
            <div class="detail-section" v-if="selectedItem.data.summary">
              <div class="section-title">Summary:</div>
              <div class="summary-text">{{ selectedItem.data.summary }}</div>
            </div>

            <!-- Agent Profile: Emotional Baseline -->
            <div class="detail-section" v-if="selectedItem.agentProfile">
              <div class="section-title">Agent Profile</div>
              <div class="agent-profile-card">
                <div class="ap-row">
                  <span class="ap-label">Persona</span>
                  <span class="ap-value ap-tier" :class="'tier-' + selectedItem.agentProfile.socioeconomic_tier">
                    {{ selectedItem.agentProfile.socioeconomic_tier }}
                  </span>
                </div>
                <div class="ap-row" v-if="selectedItem.agentProfile.profession">
                  <span class="ap-label">Role</span>
                  <span class="ap-value">{{ selectedItem.agentProfile.profession }}</span>
                </div>
                <div class="ap-row" v-if="selectedItem.agentProfile.country">
                  <span class="ap-label">Country</span>
                  <span class="ap-value">{{ selectedItem.agentProfile.country }}</span>
                </div>
                <div class="ap-row" v-if="selectedItem.agentProfile.mbti">
                  <span class="ap-label">MBTI</span>
                  <span class="ap-value">{{ selectedItem.agentProfile.mbti }}</span>
                </div>

                <!-- Emotional baseline bars -->
                <div class="ap-emotions" v-if="selectedItem.agentProfile.emotional_baseline">
                  <div class="ap-emo-label">Emotional Baseline</div>
                  <div
                    v-for="(val, key) in selectedItem.agentProfile.emotional_baseline"
                    :key="key"
                    class="ap-emo-row"
                  >
                    <span class="ap-emo-key">{{ key }}</span>
                    <div class="ap-emo-bar-track">
                      <div class="ap-emo-bar" :style="{ width: (val * 100) + '%', background: emoColor(key) }"></div>
                    </div>
                    <span class="ap-emo-val">{{ (val * 100).toFixed(0) }}</span>
                  </div>
                </div>

                <!-- Cognitive biases -->
                <div class="ap-biases" v-if="selectedItem.agentProfile.cognitive_biases?.length">
                  <div class="ap-emo-label">Cognitive Biases</div>
                  <div class="ap-bias-list">
                    <span
                      v-for="bias in selectedItem.agentProfile.cognitive_biases"
                      :key="bias"
                      class="ap-bias-tag"
                    >{{ bias.replace(/_/g, ' ') }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Labels -->
            <div class="detail-section" v-if="selectedItem.data.labels && selectedItem.data.labels.length > 0">
              <div class="section-title">Labels:</div>
              <div class="labels-list">
                <span v-for="label in selectedItem.data.labels" :key="label" class="label-tag">
                  {{ label }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Edge details -->
          <div v-else class="detail-content">
            <!-- Self-loop group details -->
            <template v-if="selectedItem.data.isSelfLoopGroup">
              <div class="edge-relation-header self-loop-header">
                {{ selectedItem.data.source_name }} - Self Relations
                <span class="self-loop-count">{{ selectedItem.data.selfLoopCount }} items</span>
              </div>
              
              <div class="self-loop-list">
                <div 
                  v-for="(loop, idx) in selectedItem.data.selfLoopEdges" 
                  :key="loop.uuid || idx" 
                  class="self-loop-item"
                  :class="{ expanded: expandedSelfLoops.has(loop.uuid || idx) }"
                >
                  <div 
                    class="self-loop-item-header"
                    @click="toggleSelfLoop(loop.uuid || idx)"
                  >
                    <span class="self-loop-index">#{{ idx + 1 }}</span>
                    <span class="self-loop-name">{{ loop.name || loop.fact_type || 'RELATED' }}</span>
                    <span class="self-loop-toggle">{{ expandedSelfLoops.has(loop.uuid || idx) ? '−' : '+' }}</span>
                  </div>
                  
                  <div class="self-loop-item-content" v-show="expandedSelfLoops.has(loop.uuid || idx)">
                    <div class="detail-row" v-if="loop.uuid">
                      <span class="detail-label">UUID:</span>
                      <span class="detail-value uuid-text">{{ loop.uuid }}</span>
                    </div>
                    <div class="detail-row" v-if="loop.fact">
                      <span class="detail-label">Fact:</span>
                      <span class="detail-value fact-text">{{ loop.fact }}</span>
                    </div>
                    <div class="detail-row" v-if="loop.fact_type">
                      <span class="detail-label">Type:</span>
                      <span class="detail-value">{{ loop.fact_type }}</span>
                    </div>
                    <div class="detail-row" v-if="loop.created_at">
                      <span class="detail-label">Created:</span>
                      <span class="detail-value">{{ formatDateTime(loop.created_at) }}</span>
                    </div>
                    <div v-if="loop.episodes && loop.episodes.length > 0" class="self-loop-episodes">
                      <span class="detail-label">Episodes:</span>
                      <div class="episodes-list compact">
                        <span v-for="ep in loop.episodes" :key="ep" class="episode-tag small">{{ ep }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
            
 <!-- Edge details -->
            <template v-else>
              <div class="edge-relation-header">
                {{ selectedItem.data.source_name }} → {{ selectedItem.data.name || 'RELATED_TO' }} → {{ selectedItem.data.target_name }}
              </div>
              
              <div class="detail-row">
                <span class="detail-label">UUID:</span>
                <span class="detail-value uuid-text">{{ selectedItem.data.uuid }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Label:</span>
                <span class="detail-value">{{ selectedItem.data.name || 'RELATED_TO' }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Type:</span>
                <span class="detail-value">{{ selectedItem.data.fact_type || 'Unknown' }}</span>
              </div>
              <div class="detail-row" v-if="selectedItem.data.fact">
                <span class="detail-label">Fact:</span>
                <span class="detail-value fact-text">{{ selectedItem.data.fact }}</span>
              </div>
              
              <!-- Episodes -->
              <div class="detail-section" v-if="selectedItem.data.episodes && selectedItem.data.episodes.length > 0">
                <div class="section-title">Episodes:</div>
                <div class="episodes-list">
                  <span v-for="ep in selectedItem.data.episodes" :key="ep" class="episode-tag">
                    {{ ep }}
                  </span>
                </div>
              </div>
              
              <div class="detail-row" v-if="selectedItem.data.created_at">
                <span class="detail-label">Created:</span>
                <span class="detail-value">{{ formatDateTime(selectedItem.data.created_at) }}</span>
              </div>
              <div class="detail-row" v-if="selectedItem.data.valid_at">
                <span class="detail-label">Valid From:</span>
                <span class="detail-value">{{ formatDateTime(selectedItem.data.valid_at) }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>
      
      <!-- Loading state -->
      <div v-else-if="loading" class="graph-state">
        <div class="loading-spinner"></div>
        <p>Loading graph data...</p>
      </div>
      
 <!-- Pending/ -->
      <div v-else class="graph-state">
        <div class="empty-icon">❖</div>
        <p class="empty-text">PendingOntology Generation...</p>
      </div>
    </div>

    <!-- Bottom legend (Bottom Left) -->
    <div v-if="graphData && entityTypes.length" class="graph-legend">
      <span class="legend-title">Entity Types</span>
      <div class="legend-items">
        <div class="legend-item" v-for="type in entityTypes" :key="type.name">
          <span class="legend-dot" :style="{ background: type.color }"></span>
          <span class="legend-label">{{ type.name }}</span>
        </div>
      </div>
    </div>
    

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  graphData: Object,
  loading: Boolean,
  currentPhase: Number,
  isSimulating: Boolean,
  agentProfiles: { type: Array, default: () => [] }
})

const emit = defineEmits(['refresh', 'toggle-maximize', 'pause-simulation', 'resume-simulation'])

const graphContainer = ref(null)
const graphSvg = ref(null)
const selectedItem = ref(null)
const expandedSelfLoops = ref(new Set())
const isMobile = ref(false)
const mobileSearch = ref('')

const filteredMobileNodes = computed(() => {
  const nodes = props.graphData?.nodes || []
  const q = mobileSearch.value.trim().toLowerCase()
  if (!q) return nodes
  return nodes.filter(n => (n.name || '').toLowerCase().includes(q))
})

const getNodeType = (node) => node.labels?.find(l => l !== 'Entity') || 'Entity'
const getNodeColor = (node) => {
  const colors = ['#3b82f6','#f59e0b','#10b981','#ef4444','#8b5cf6','#06b6d4','#f97316','#ec4899','#14b8a6','#a3e635']
  const type = getNodeType(node)
  const idx = entityTypes.value.findIndex(t => t.name === type)
  return colors[idx >= 0 ? idx % colors.length : 0]
}

const selectMobileNode = (node) => {
  const type = getNodeType(node)
  selectedItem.value = {
    type: 'node',
    data: node,
    color: getNodeColor(node),
    entityType: type,
    agentProfile: getAgentProfile(node.name)
  }
}

//
const showSimulationFinishedHint = ref(false) // 
const wasSimulating = ref(false) // 
const tooltip = ref({ visible: false, x: 0, y: 0, title: '', content: '' })

// 
const dismissFinishedHint = () => {
  showSimulationFinishedHint.value = false
}

// 
const showTooltip = (event, d, type) => {
  const rect = graphContainer.value.getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: event.clientX - rect.left + 10,
    y: event.clientY - rect.top + 10,
    title: d.name,
    content: type === 'node' ? `${d.type} • ${d.rawData.labels?.join(', ') || 'Entity'}` : d.name
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

// isSimulating ，
watch(() => props.isSimulating, (newValue, oldValue) => {
  if (wasSimulating.value && !newValue) {
 // ，
    showSimulationFinishedHint.value = true
  }
  wasSimulating.value = newValue
}, { immediate: true })

// /
const toggleSelfLoop = (id) => {
  const newSet = new Set(expandedSelfLoops.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  expandedSelfLoops.value = newSet
}

// 
const entityTypes = computed(() => {
  if (!props.graphData?.nodes) return []
  const typeMap = {}
 // 
  const colors = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#ec4899', '#14b8a6', '#a3e635']
  
  props.graphData.nodes.forEach(node => {
    const type = node.labels?.find(l => l !== 'Entity') || 'Entity'
    if (!typeMap[type]) {
      typeMap[type] = { name: type, count: 0, color: colors[Object.keys(typeMap).length % colors.length] }
    }
    typeMap[type].count++
  })
  return Object.values(typeMap)
})

// 
const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true 
    })
  } catch {
    return dateStr
  }
}

const closeDetailPanel = () => {
  selectedItem.value = null
 expandedSelfLoops.value = new Set() //
}

// Profile lookup by entity name
const getAgentProfile = (entityName) => {
  if (!props.agentProfiles?.length || !entityName) return null
  const lower = entityName.toLowerCase()
  return props.agentProfiles.find(p =>
    p.name?.toLowerCase() === lower ||
    p.user_name?.toLowerCase().includes(lower.split(' ')[0].toLowerCase())
  ) || null
}

// Emotion color coding
const emoColor = (key) => {
  const map = {
    valence: '#BDEBB5',
    anxiety: '#f59e0b',
    trust: '#3b82f6',
    excitability: '#ec4899'
  }
  return map[key] || (isDarkTheme() ? 'rgba(255,255,255,0.4)' : 'rgba(0,0,0,0.3)')
}

let animationRef = null
let linkLabelsRef = null
let linkLabelBgRef = null

const isDarkTheme = () => document.documentElement.getAttribute('data-theme') === 'dark'

const themeColors = () => {
  const dark = isDarkTheme()
  return {
    gridLat:   dark ? 'rgba(255,255,255,0.055)' : 'rgba(0,0,0,0.045)',
    gridLon:   dark ? 'rgba(255,255,255,0.04)'  : 'rgba(0,0,0,0.03)',
    link:      dark ? 'rgba(255,255,255,0.18)'   : 'rgba(0,0,0,0.15)',
    nodeBg:    dark ? '#060a0f' : '#f0f0f2',
    labelFill: dark ? 'rgba(255,255,255,0.82)'   : 'rgba(0,0,0,0.75)',
  }
}

const renderGraph = () => {
  if (!graphSvg.value || !props.graphData) return

  if (animationRef) { cancelAnimationFrame(animationRef); animationRef = null }

  const container = graphContainer.value
  const width = container.clientWidth
  const height = container.clientHeight

  const svg = d3.select(graphSvg.value)
    .attr('width', width).attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`)
  svg.selectAll('*').remove()

  const nodesData = props.graphData.nodes || []
  const edgesData = props.graphData.edges || []
  if (nodesData.length === 0) return

  const nodeMap = {}
  nodesData.forEach(n => nodeMap[n.uuid] = n)

  const nodes = nodesData.map(n => ({
    id: n.uuid,
    name: n.name || 'Unnamed',
    type: n.labels?.find(l => l !== 'Entity') || 'Entity',
    rawData: n,
    _sx: 0, _sy: 0, _sz: 0,
    _px: 0, _py: 0, _pz: 0, _scale: 1, _r: 8, _opacity: 1
  }))

  const nodeIds = new Set(nodes.map(n => n.id))
  const nodeById = {}
  nodes.forEach(n => nodeById[n.id] = n)

  // Fibonacci sphere distribution
  const goldenAngle = Math.PI * (3 - Math.sqrt(5))
  nodes.forEach((nd, i) => {
    const y = nodes.length === 1 ? 0 : 1 - (i / (nodes.length - 1)) * 2
    const r = Math.sqrt(Math.max(0, 1 - y * y))
    nd._sx = Math.cos(goldenAngle * i) * r
    nd._sy = y
    nd._sz = Math.sin(goldenAngle * i) * r
  })

  // Build edges (skip self-loops — no meaningful arc on globe)
  const seen = new Set()
  const edges = []
  edgesData
    .filter(e => nodeIds.has(e.source_node_uuid) && nodeIds.has(e.target_node_uuid) && e.source_node_uuid !== e.target_node_uuid)
    .forEach(e => {
      const key = [e.source_node_uuid, e.target_node_uuid].sort().join('_')
      if (seen.has(key)) return
      seen.add(key)
      edges.push({
        source: nodeById[e.source_node_uuid],
        target: nodeById[e.target_node_uuid],
        name: e.name || e.fact_type || 'RELATED',
        rawData: { ...e, source_name: nodeMap[e.source_node_uuid]?.name, target_name: nodeMap[e.target_node_uuid]?.name }
      })
    })

  // Colors
  const colorMap = {}
  entityTypes.value.forEach(t => colorMap[t.name] = t.color)
  const getColor = (type) => colorMap[type] || '#888'

  // Sphere geometry
  const cx = width / 2, cy = height / 2
  const sphereR = Math.min(width, height) * 0.36

  // SVG defs
  const defs = svg.append('defs')

  // Clip to sphere
  defs.append('clipPath').attr('id', 'sph-clip')
    .append('circle').attr('cx', cx).attr('cy', cy).attr('r', sphereR - 1)


  // ── Graph groups (clipped to sphere) ──
  const g = svg.append('g').attr('clip-path', 'url(#sph-clip)')
  const gridGroup = g.append('g')
  const linkGroup = g.append('g')
  const nodeGroup = g.append('g')

  // Zoom + pan
  svg.call(d3.zoom().extent([[0,0],[width,height]]).scaleExtent([0.3,4]).on('zoom', ev => g.attr('transform', ev.transform)))

  // Grid lines — latitude (5) and longitude (8)
  const latPts  = [-Math.PI/3, -Math.PI/6, 0, Math.PI/6, Math.PI/3].map(lat =>
    Array.from({length: 73}, (_, i) => {
      const lon = (i / 72) * Math.PI * 2
      return { sx: Math.cos(lat)*Math.cos(lon), sy: Math.sin(lat), sz: Math.cos(lat)*Math.sin(lon) }
    })
  )
  const lonPts = Array.from({length: 8}, (_, k) => k * Math.PI / 4).map(lon =>
    Array.from({length: 73}, (_, i) => {
      const lat = (i / 72) * Math.PI - Math.PI/2
      return { sx: Math.cos(lat)*Math.cos(lon), sy: Math.sin(lat), sz: Math.cos(lat)*Math.sin(lon) }
    })
  )

  const tc = themeColors()
  const latPaths = latPts.map(pts =>
    gridGroup.append('path').datum(pts).attr('fill','none')
      .attr('stroke', tc.gridLat).attr('stroke-width', 0.6).style('pointer-events','none')
  )
  const lonPaths = lonPts.map(pts =>
    gridGroup.append('path').datum(pts).attr('fill','none')
      .attr('stroke', tc.gridLon).attr('stroke-width', 0.5).style('pointer-events','none')
  )

  // Edges
  const link = linkGroup.selectAll('path').data(edges).enter().append('path')
    .attr('fill', 'none').attr('stroke', tc.link).attr('stroke-width', 1)
    .style('cursor', 'pointer')
    .on('click', (event, d) => {
      event.stopPropagation()
      linkGroup.selectAll('path').attr('stroke', themeColors().link).attr('stroke-width', 1)
      d3.select(event.target).attr('stroke','#BDEBB5').attr('stroke-width', 2)
      selectedItem.value = { type: 'edge', data: d.rawData }
    })

  // Hidden label placeholders (tick-compat)
  const linkLabelBg = linkGroup.selectAll('rect').data([]).enter().append('rect').style('display','none')
  const linkLabels  = linkGroup.selectAll('text').data([]).enter().append('text').style('display','none')
  linkLabelsRef = linkLabels; linkLabelBgRef = linkLabelBg

  // Nodes
  const node = nodeGroup.selectAll('circle').data(nodes, d => d.id).enter().append('circle')
    .attr('r', 8).attr('fill', d => getColor(d.type))
    .attr('stroke', tc.nodeBg).attr('stroke-width', 1.5)
    .style('cursor', 'pointer')
    .on('click', (event, d) => {
      event.stopPropagation()
      node.attr('stroke', themeColors().nodeBg).attr('stroke-width', 1.5)
      linkGroup.selectAll('path').attr('stroke', themeColors().link).attr('stroke-width', 1)
      d3.select(event.target).attr('stroke','#BDEBB5').attr('stroke-width', 2.5)
      link.filter(l => l.source?.id === d.id || l.target?.id === d.id)
        .attr('stroke','rgba(189,235,181,0.55)').attr('stroke-width', 1.8)
      selectedItem.value = {
          type: 'node',
          data: d.rawData,
          color: getColor(d.type),
          entityType: d.type,
          agentProfile: getAgentProfile(d.name)
        }
    })
    .on('mouseenter', (event, d) => {
      if (!selectedItem.value || selectedItem.value.data?.uuid !== d.rawData.uuid) {
        d3.select(event.target).attr('r', d._r * 1.45).attr('stroke','rgba(189,235,181,0.8)').attr('stroke-width', 2)
        showTooltip(event, d, 'node')
      }
    })
    .on('mouseleave', (event, d) => {
      if (!selectedItem.value || selectedItem.value.data?.uuid !== d.rawData.uuid) {
        d3.select(event.target).attr('r', d._r).attr('stroke', themeColors().nodeBg).attr('stroke-width', 1.5)
        hideTooltip()
      }
    })

  // Node labels
  const nodeLabels = nodeGroup.selectAll('text').data(nodes, d => d.id).enter().append('text')
    .text(d => d.name.length > 10 ? d.name.substring(0, 10) + '…' : d.name)
    .attr('font-size','11px').attr('fill', tc.labelFill).attr('font-weight','500')
    .attr('dx', 13).attr('dy', 4)
    .style('pointer-events','none').style('font-family','system-ui, sans-serif')

  // ── 3D projection (Y-rotation + slight X tilt) ──
  const TILT = 0.22
  let rotY = 0
  let rotSpeed = 0.004

  const project = (sx, sy, sz) => {
    const x1 = sx * Math.cos(rotY) - sz * Math.sin(rotY)
    const z1 = sx * Math.sin(rotY) + sz * Math.cos(rotY)
    const y2 = sy * Math.cos(TILT) - z1 * Math.sin(TILT)
    const z2 = sy * Math.sin(TILT) + z1 * Math.cos(TILT)
    const p  = 2.6 / (2.6 + z2)
    return { x: cx + x1 * sphereR * p, y: cy + y2 * sphereR * p, z: z2, scale: p }
  }

  const gridPath = (pts) => {
    let d = '', prev = false
    pts.forEach(pt => {
      const p = project(pt.sx, pt.sy, pt.sz)
      if (p.z > -0.6) { d += (prev ? 'L' : 'M') + p.x.toFixed(1) + ',' + p.y.toFixed(1); prev = true }
      else prev = false
    })
    return d
  }

  // Slow on hover
  svg.on('mouseenter', () => { rotSpeed = 0.001 })
     .on('mouseleave', () => { rotSpeed = 0.004 })

  // SVG background click → deselect
  svg.on('click', () => {
    selectedItem.value = null
    node.attr('stroke', themeColors().nodeBg).attr('stroke-width', 1.5)
    linkGroup.selectAll('path').attr('stroke', themeColors().link).attr('stroke-width', 1)
  })

  // ── Animation loop ──
  const animate = () => {
    rotY += rotSpeed

    // Grid
    latPaths.forEach(p => p.attr('d', gridPath(p.datum())))
    lonPaths.forEach(p => p.attr('d', gridPath(p.datum())))

    // Project nodes
    nodes.forEach(nd => {
      const p = project(nd._sx, nd._sy, nd._sz)
      nd._px = p.x; nd._py = p.y; nd._pz = p.z; nd._scale = p.scale
      nd._r = Math.max(5, 9 * p.scale)
      nd._opacity = p.z < -0.1 ? Math.max(0.12, 0.75 + p.z * 0.65) : 0.95
    })

    // Depth sort (painter's algorithm)
    node.sort((a, b) => a._pz - b._pz)
    nodeLabels.sort((a, b) => a._pz - b._pz)

    node.attr('cx', d => d._px).attr('cy', d => d._py).attr('r', d => d._r).attr('opacity', d => d._opacity)
    nodeLabels.attr('x', d => d._px).attr('y', d => d._py)
      .attr('opacity', d => d._pz < -0.05 ? 0 : Math.min(0.9, 0.35 + d._pz * 0.65))
      .attr('font-size', d => Math.max(9, 11 * d._scale) + 'px')

    // Great-circle edge arcs (midpoint on sphere surface)
    link.attr('d', d => {
      const s = d.source, t = d.target
      if (!s || !t) return ''
      const mx = (s._sx + t._sx) / 2, my = (s._sy + t._sy) / 2, mz = (s._sz + t._sz) / 2
      const ml = Math.sqrt(mx*mx + my*my + mz*mz) || 1
      const mp = project(mx/ml, my/ml, mz/ml)
      return `M${s._px.toFixed(1)},${s._py.toFixed(1)} Q${mp.x.toFixed(1)},${mp.y.toFixed(1)} ${t._px.toFixed(1)},${t._py.toFixed(1)}`
    })
    .attr('opacity', d => {
      if (!d.source || !d.target) return 0
      const z = (d.source._pz + d.target._pz) / 2
      return z < -0.3 ? 0.03 : z < 0 ? 0.07 + (z + 0.3) * 0.33 : 0.2 + z * 0.15
    })

    animationRef = requestAnimationFrame(animate)
  }

  animate()
}

// ── STUB so old watch/tick refs compile ──
const currentSimulation = null
// fake tick references for any surviving code
const _stubWatch = () => {
  if (linkLabelsRef) { /* noop */ }
  if (linkLabelBgRef) { /* noop */ }
}

watch(() => props.graphData, () => {
  nextTick(renderGraph)
}, { deep: true })


const handleResize = () => {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) nextTick(renderGraph)
}

onMounted(() => {
  isMobile.value = window.innerWidth < 768
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (animationRef) cancelAnimationFrame(animationRef)
})
</script>

<style scoped>
/* ── GRAPH PANEL — Dark Financial Theme ── */
.graph-panel {
  position: relative;
  width: 100%;
  height: 100%;
  background: var(--bg);
  background-image:
    linear-gradient(var(--green-dim) 1px, transparent 1px),
    linear-gradient(90deg, var(--green-dim) 1px, transparent 1px);
  background-size: 32px 32px;
  overflow: hidden;
}

.graph-container {
  position: relative;
  width: 100%;
  height: 100%;
}


.graph-view {
  position: relative;
  z-index: 2;
}


.panel-header {
  position: absolute;
  top: 0; left: 0; right: 0;
  padding: 14px 18px;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to bottom, rgba(8,12,20,0.96) 60%, transparent);
  pointer-events: none;
}

.panel-title {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-family: var(--mono);
  pointer-events: auto;
}

.header-tools {
  pointer-events: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

.tool-btn {
  height: 28px;
  padding: 0 10px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  cursor: pointer;
  color: rgba(255,255,255,0.45);
  transition: all 0.15s;
  font-size: 11px;
}
.tool-btn:hover {
  background: rgba(59,130,246,0.12);
  color: #60a5fa;
  border-color: rgba(59,130,246,0.3);
}
.tool-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.tool-btn .btn-text { font-size: 11px; font-family: var(--mono); letter-spacing: 0.05em; }

.icon-refresh.spinning { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.graph-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.graph-view {
  width: 100%;
  height: 100%;
  position: relative;
}

.graph-svg {
  width: 100%;
  height: 100%;
  display: block;
}

/* ── REAL-TIME BUILDING HINT ── */
.graph-building-hint {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(8,12,20,0.92);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 24px;
  padding: 8px 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  font-family: var(--mono);
  color: #60a5fa;
  letter-spacing: 0.06em;
  backdrop-filter: blur(12px);
  white-space: nowrap;
  z-index: 20;
  animation: fadeInUp 0.3s ease;
  box-shadow: 0 0 24px rgba(59,130,246,0.15);
}

.finished-hint {
  color: #34d399;
  border-color: rgba(52,211,153,0.3);
  box-shadow: 0 0 24px rgba(52,211,153,0.1);
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateX(-50%) translateY(8px); }
  to   { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.memory-icon, .hint-icon { width: 16px; height: 16px; flex-shrink: 0; animation: pulse-icon 2s infinite; }
@keyframes pulse-icon { 0%,100%{opacity:1} 50%{opacity:0.5} }
.hint-text { font-size: 11px; }

.dismiss-btn {
  background: none; border: none;
  color: rgba(52,211,153,0.6);
  cursor: pointer; padding: 0 0 0 4px; opacity: 0.7;
  transition: opacity 0.15s;
}
.dismiss-btn:hover { opacity: 1; }

/* ── NODE DETAIL PANEL ── */
.node-detail {
  position: absolute;
  top: 52px; right: 12px;
  width: 280px;
  max-height: calc(100% - 80px);
  overflow-y: auto;
  background: rgba(8,12,20,0.96);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  z-index: 20;
  backdrop-filter: blur(16px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(8px); }
  to   { opacity: 1; transform: translateX(0); }
}

.detail-header {
  padding: 12px 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(255,255,255,0.03);
}

.detail-title {
  font-size: 10px;
  font-family: var(--mono);
  font-weight: 600;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.detail-type-badge {
  font-size: 9px;
  font-family: var(--mono);
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 3px;
  letter-spacing: 0.06em;
}

.close-btn {
  background: none; border: none;
  color: rgba(255,255,255,0.3);
  cursor: pointer; font-size: 1rem; padding: 0;
  transition: color 0.15s; line-height: 1;
}
.close-btn:hover { color: #fff; }

.detail-content { padding: 12px 14px; }

.detail-row {
  display: flex; flex-direction: column;
  gap: 2px; margin-bottom: 10px;
}
.detail-label {
  font-size: 9px;
  font-family: var(--mono);
  color: rgba(255,255,255,0.3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.detail-value {
  font-size: 11px;
  color: rgba(255,255,255,0.8);
  word-break: break-all;
  line-height: 1.4;
}
.detail-value.mono {
  font-family: var(--mono);
  font-size: 10px;
  color: #60a5fa;
}

.detail-section { margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.07); }
.detail-section-title {
  font-size: 9px;
  font-family: var(--mono);
  color: rgba(255,255,255,0.3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.labels-list { display: flex; flex-wrap: wrap; gap: 4px; }
.label-tag {
  font-size: 9px;
  font-family: var(--mono);
  padding: 2px 7px;
  border-radius: 3px;
  background: rgba(59,130,246,0.15);
  color: #60a5fa;
  border: 1px solid rgba(59,130,246,0.2);
  letter-spacing: 0.04em;
}

/* Self-loop / edge detail */
.edge-relation-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  font-size: 11px; color: rgba(255,255,255,0.7);
}
.self-loop-header { flex-direction: column; align-items: flex-start; }
.edge-node-name {
  font-family: var(--mono); font-size: 10px;
  color: #60a5fa; font-weight: 600;
}
.edge-arrow { color: rgba(255,255,255,0.25); font-size: 10px; }
.edge-label {
  font-family: var(--mono); font-size: 9px;
  color: rgba(255,255,255,0.4); letter-spacing: 0.08em;
}
.edge-count-badge {
  font-size: 9px; font-family: var(--mono);
  background: rgba(59,130,246,0.15); color: #60a5fa;
  border: 1px solid rgba(59,130,246,0.2);
  padding: 2px 7px; border-radius: 3px;
  cursor: pointer; transition: all 0.15s;
}
.edge-count-badge:hover { background: rgba(59,130,246,0.25); }

.self-loop-edges { padding: 10px 14px; display: flex; flex-direction: column; gap: 8px; }
.self-loop-edge-item {
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 5px;
  padding: 8px 10px;
  background: rgba(255,255,255,0.02);
}
.self-loop-edge-label {
  font-family: var(--mono); font-size: 9px;
  color: rgba(255,255,255,0.3); letter-spacing: 0.08em; margin-bottom: 4px;
}
.self-loop-edge-fact {
  font-size: 10px; color: rgba(255,255,255,0.65); line-height: 1.4;
}

/* ── EMPTY / LOADING STATES ── */
.graph-state {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  height: 100%; gap: 12px;
  color: rgba(255,255,255,0.25);
  font-family: var(--mono);
}
.graph-state svg { opacity: 0.2; }
.graph-state p { font-size: 11px; letter-spacing: 0.08em; }

.loading-spinner {
  width: 24px; height: 24px;
  border: 2px solid rgba(255,255,255,0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* ── LEGEND ── */
.graph-legend {
  position: absolute;
  bottom: 16px; left: 16px;
  background: rgba(8, 8, 8, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  padding: 10px 14px;
  backdrop-filter: blur(10px) saturate(180%);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 10;
  transition: all 0.3s ease;
}
.graph-legend:hover {
  background: rgba(8, 8, 8, 0.5);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
.legend-title {
  font-size: 9px;
  font-family: Arial, sans-serif;
  color: #FFFFFF;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 8px;
  display: block;
}
.legend-item {
  display: flex; align-items: center; gap: 7px;
  margin-bottom: 5px;
}
.legend-item:last-child { margin-bottom: 0; }
.legend-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.legend-label {
  font-size: 10px;
  font-family: Arial, sans-serif;
  color: #FFFFFF;
  letter-spacing: 0.04em;
}


/* ── SIMULATION CONTROLS ── */
.simulation-controls {
  display: flex;
  gap: 8px;
  margin-left: 12px;
  padding-left: 12px;
  border-left: 1px solid rgba(255,255,255,0.1);
}

.control-btn {
  background: rgba(189,235,181,0.1);
  border: 1px solid rgba(189,235,181,0.3);
  color: #BDEBB5;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: rgba(189,235,181,0.2);
  border-color: rgba(189,235,181,0.5);
  transform: translateY(-1px);
}

.resume-btn {
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.3);
  color: #60a5fa;
}

.resume-btn:hover {
  background: rgba(59,130,246,0.2);
  border-color: rgba(59,130,246,0.5);
}

/* ── MOBILE NODE LIST ── */
.mobile-graph-list {
  width: 100%; height: 100%;
  display: flex; flex-direction: column;
  overflow: hidden;
  background: inherit;
}
.mgl-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px 8px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}
.mgl-title {
  font-size: 10px; font-weight: 700; letter-spacing: 0.12em;
  text-transform: uppercase; color: rgba(255,255,255,0.45);
  font-family: var(--mono);
}
.mgl-count { font-size: 9px; color: rgba(255,255,255,0.2); font-family: var(--mono); }
.mgl-search {
  margin: 8px 12px; padding: 7px 12px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 5px; color: rgba(255,255,255,0.8); font-size: 12px;
  font-family: var(--mono); outline: none; flex-shrink: 0;
}
.mgl-search:focus { border-color: rgba(59,130,246,0.4); }
.mgl-search::placeholder { color: rgba(255,255,255,0.2); }
.mgl-nodes {
  flex: 1; overflow-y: auto; padding: 4px 12px 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.mgl-node {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: 5px;
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
  cursor: pointer; transition: all 0.15s;
}
.mgl-node:hover { background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.12); }
.mgl-node.selected { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); }
.mgl-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.mgl-name { flex: 1; font-size: 12px; color: rgba(255,255,255,0.8); truncate: true; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mgl-type { font-size: 9px; color: rgba(255,255,255,0.3); letter-spacing: 0.06em; font-family: var(--mono); flex-shrink: 0; }
.mgl-detail {
  flex-shrink: 0; border-top: 1px solid rgba(255,255,255,0.07);
  max-height: 220px; overflow-y: auto;
  background: rgba(8,12,20,0.98);
  border-radius: 0;
}
.mgl-nodes::-webkit-scrollbar { width: 3px; }
.mgl-nodes::-webkit-scrollbar-track { background: transparent; }
.mgl-nodes::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }

/* Scrollbar in detail panel */
.node-detail::-webkit-scrollbar { width: 3px; }
.node-detail::-webkit-scrollbar-track { background: transparent; }
.node-detail::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

/* ── TOOLTIP ── */
.graph-tooltip {
  position: absolute;
  background: rgba(8,12,20,0.95);
  border: 1px solid rgba(189,235,181,0.3);
  border-radius: 6px;
  padding: 8px 12px;
  pointer-events: none;
  z-index: 100;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
  max-width: 200px;
  font-size: 11px;
  font-family: var(--mono);
}
.tooltip-title {
  color: #BDEBB5;
  font-weight: 600;
  margin-bottom: 4px;
  letter-spacing: 0.05em;
}
.tooltip-content {
  color: rgba(255,255,255,0.8);
  line-height: 1.3;
}

/* Agent Profile Card */
.agent-profile-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 6px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 8px;
}
.ap-row { display: flex; align-items: center; justify-content: space-between; }
.ap-label { font-size: 9px; color: rgba(255,255,255,0.25); text-transform: uppercase; letter-spacing: 0.1em; }
.ap-value { font-size: 10px; color: rgba(255,255,255,0.65); font-weight: 500; }
.ap-tier { font-weight: 700; font-size: 9px; padding: 1px 6px; border-radius: 3px; letter-spacing: 0.08em; text-transform: uppercase; }
.tier-low { background: rgba(239,68,68,0.12); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
.tier-medium { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.5); border: 1px solid rgba(255,255,255,0.1); }
.tier-high { background: rgba(189,235,181,0.1); color: #BDEBB5; border: 1px solid rgba(189,235,181,0.2); }
.tier-very_high { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
.ap-emotions { display: flex; flex-direction: column; gap: 5px; }
.ap-emo-label { font-size: 8px; color: rgba(255,255,255,0.2); text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 2px; }
.ap-emo-row { display: flex; align-items: center; gap: 6px; }
.ap-emo-key { font-size: 9px; color: rgba(255,255,255,0.3); min-width: 70px; text-transform: capitalize; }
.ap-emo-bar-track { flex: 1; height: 3px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; }
.ap-emo-bar { height: 100%; border-radius: 2px; transition: width 0.4s ease; }
.ap-emo-val { font-size: 9px; color: rgba(255,255,255,0.3); min-width: 22px; text-align: right; }
.ap-biases { display: flex; flex-direction: column; gap: 5px; }
.ap-bias-list { display: flex; flex-wrap: wrap; gap: 4px; }
.ap-bias-tag {
  font-size: 8px; padding: 2px 6px; border-radius: 3px;
  background: rgba(245,158,11,0.08); color: rgba(245,158,11,0.65);
  border: 1px solid rgba(245,158,11,0.15); text-transform: capitalize;
}
</style>
