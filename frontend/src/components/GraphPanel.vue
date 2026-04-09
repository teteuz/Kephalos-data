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
      <!-- Overlay animated background video -->
      <video class="graph-bg-video" src="/ai orb 2.webm" autoplay loop muted playsinline preload="auto"></video>

      <!-- Tooltip -->
      <div v-if="tooltip.visible" class="graph-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <div class="tooltip-title">{{ tooltip.title }}</div>
        <div class="tooltip-content">{{ tooltip.content }}</div>
      </div>

      <!-- Graph visualization -->
      <div v-if="graphData" class="graph-view">
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
    
    <div v-if="graphData" class="edge-labels-toggle">
      <label class="toggle-switch">
        <input type="checkbox" v-model="showEdgeLabels" />
        <span class="slider"></span>
      </label>
      <span class="toggle-label">{{ showEdgeLabels ? 'Hide Edge Labels' : 'Show Edge Labels' }}</span>
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
  isSimulating: Boolean
})

const emit = defineEmits(['refresh', 'toggle-maximize', 'pause-simulation', 'resume-simulation'])

const graphContainer = ref(null)
const graphSvg = ref(null)
const selectedItem = ref(null)
const showEdgeLabels = ref(true) // 
const expandedSelfLoops = ref(new Set()) // 
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

let currentSimulation = null
let linkLabelsRef = null
let linkLabelBgRef = null

const renderGraph = () => {
  if (!graphSvg.value || !props.graphData) return
  
 // 
  if (currentSimulation) {
    currentSimulation.stop()
  }
  
  const container = graphContainer.value
  const width = container.clientWidth
  const height = container.clientHeight
  
  const svg = d3.select(graphSvg.value)
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`)
    
  svg.selectAll('*').remove()
  
  const nodesData = props.graphData.nodes || []
  const edgesData = props.graphData.edges || []
  
  if (nodesData.length === 0) return

  // Prep data
  const nodeMap = {}
  nodesData.forEach(n => nodeMap[n.uuid] = n)
  
  const nodes = nodesData.map(n => ({
    id: n.uuid,
    name: n.name || 'Unnamed',
    type: n.labels?.find(l => l !== 'Entity') || 'Entity',
    rawData: n
  }))
  
  const nodeIds = new Set(nodes.map(n => n.id))
  
 // ，
  const edgePairCount = {}
 const selfLoopEdges = {} // 
  const tempEdges = edgesData
    .filter(e => nodeIds.has(e.source_node_uuid) && nodeIds.has(e.target_node_uuid))
  
 // ，
  tempEdges.forEach(e => {
    if (e.source_node_uuid === e.target_node_uuid) {
 // - 
      if (!selfLoopEdges[e.source_node_uuid]) {
        selfLoopEdges[e.source_node_uuid] = []
      }
      selfLoopEdges[e.source_node_uuid].push({
        ...e,
        source_name: nodeMap[e.source_node_uuid]?.name,
        target_name: nodeMap[e.target_node_uuid]?.name
      })
    } else {
      const pairKey = [e.source_node_uuid, e.target_node_uuid].sort().join('_')
      edgePairCount[pairKey] = (edgePairCount[pairKey] || 0) + 1
    }
  })
  
 // 
  const edgePairIndex = {}
 const processedSelfLoopNodes = new Set() // 
  
  const edges = []
  
  tempEdges.forEach(e => {
    const isSelfLoop = e.source_node_uuid === e.target_node_uuid
    
    if (isSelfLoop) {
 // - items
      if (processedSelfLoopNodes.has(e.source_node_uuid)) {
 return // ，
      }
      processedSelfLoopNodes.add(e.source_node_uuid)
      
      const allSelfLoops = selfLoopEdges[e.source_node_uuid]
      const nodeName = nodeMap[e.source_node_uuid]?.name || 'Unknown'
      
      edges.push({
        source: e.source_node_uuid,
        target: e.target_node_uuid,
        type: 'SELF_LOOP',
        name: `Self Relations (${allSelfLoops.length})`,
        curvature: 0,
        isSelfLoop: true,
        rawData: {
          isSelfLoopGroup: true,
          source_name: nodeName,
          target_name: nodeName,
          selfLoopCount: allSelfLoops.length,
 selfLoopEdges: allSelfLoops // 
        }
      })
      return
    }
    
    const pairKey = [e.source_node_uuid, e.target_node_uuid].sort().join('_')
    const totalCount = edgePairCount[pairKey]
    const currentIndex = edgePairIndex[pairKey] || 0
    edgePairIndex[pairKey] = currentIndex + 1
    
 // （UUID < UUID）
    const isReversed = e.source_node_uuid > e.target_node_uuid
    
 // ：，
    let curvature = 0
    if (totalCount > 1) {
 // ，
 // ，
      const curvatureRange = Math.min(1.2, 0.6 + totalCount * 0.15)
      curvature = ((currentIndex / (totalCount - 1)) - 0.5) * curvatureRange * 2
      
 // ，
 // ，
      if (isReversed) {
        curvature = -curvature
      }
    }
    
    edges.push({
      source: e.source_node_uuid,
      target: e.target_node_uuid,
      type: e.fact_type || e.name || 'RELATED',
      name: e.name || e.fact_type || 'RELATED',
      curvature,
      isSelfLoop: false,
      pairIndex: currentIndex,
      pairTotal: totalCount,
      rawData: {
        ...e,
        source_name: nodeMap[e.source_node_uuid]?.name,
        target_name: nodeMap[e.target_node_uuid]?.name
      }
    })
  })
    
  // Color scale
  const colorMap = {}
  entityTypes.value.forEach(t => colorMap[t.name] = t.color)
  const getColor = (type) => colorMap[type] || '#999'

 // Simulation - 
  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(d => {
 // 
 // 150， 40
      const baseDistance = 150
      const edgeCount = d.pairTotal || 1
      return baseDistance + (edgeCount - 1) * 50
    }))
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collide', d3.forceCollide(50))
 // ，
    .force('x', d3.forceX(width / 2).strength(0.04))
    .force('y', d3.forceY(height / 2).strength(0.04))
  
  currentSimulation = simulation

  const g = svg.append('g')
  
  // Zoom
  svg.call(d3.zoom().extent([[0, 0], [width, height]]).scaleExtent([0.1, 4]).on('zoom', (event) => {
    g.attr('transform', event.transform)
  }))

 // Links - path 
  const linkGroup = g.append('g').attr('class', 'links')
  
 // 
  const getLinkPath = (d) => {
    const sx = d.source.x, sy = d.source.y
    const tx = d.target.x, ty = d.target.y
    
 // 
    if (d.isSelfLoop) {
 // ：items
      const loopRadius = 30
 // ，
 const x1 = sx + 8 // 
      const y1 = sy - 4
 const x2 = sx + 8 // 
      const y2 = sy + 4
 // （sweep-flag=1 ）
      return `M${x1},${y1} A${loopRadius},${loopRadius} 0 1,1 ${x2},${y2}`
    }
    
    if (d.curvature === 0) {
 // 
      return `M${sx},${sy} L${tx},${ty}`
    }
    
 // - 
    const dx = tx - sx, dy = ty - sy
    const dist = Math.sqrt(dx * dx + dy * dy)
 // ，，
 // ，
    const pairTotal = d.pairTotal || 1
 const offsetRatio = 0.25 + pairTotal * 0.05 // 25%，5%
    const baseOffset = Math.max(35, dist * offsetRatio)
    const offsetX = -dy / dist * d.curvature * baseOffset
    const offsetY = dx / dist * d.curvature * baseOffset
    const cx = (sx + tx) / 2 + offsetX
    const cy = (sy + ty) / 2 + offsetY
    
    return `M${sx},${sy} Q${cx},${cy} ${tx},${ty}`
  }
  
 // （）
  const getLinkMidpoint = (d) => {
    const sx = d.source.x, sy = d.source.y
    const tx = d.target.x, ty = d.target.y
    
 // 
    if (d.isSelfLoop) {
 // ：
      return { x: sx + 70, y: sy }
    }
    
    if (d.curvature === 0) {
      return { x: (sx + tx) / 2, y: (sy + ty) / 2 }
    }
    
 // t=0.5
    const dx = tx - sx, dy = ty - sy
    const dist = Math.sqrt(dx * dx + dy * dy)
    const pairTotal = d.pairTotal || 1
    const offsetRatio = 0.25 + pairTotal * 0.05
    const baseOffset = Math.max(35, dist * offsetRatio)
    const offsetX = -dy / dist * d.curvature * baseOffset
    const offsetY = dx / dist * d.curvature * baseOffset
    const cx = (sx + tx) / 2 + offsetX
    const cy = (sy + ty) / 2 + offsetY
    
 // B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2, t=0.5
    const midX = 0.25 * sx + 0.5 * cx + 0.25 * tx
    const midY = 0.25 * sy + 0.5 * cy + 0.25 * ty
    
    return { x: midX, y: midY }
  }
  
  const link = linkGroup.selectAll('path')
    .data(edges)
    .enter().append('path')
    .attr('stroke', 'rgba(255,255,255,0.12)')
    .attr('stroke-width', 1.2)
    .attr('fill', 'none')
    .style('cursor', 'pointer')
    .on('click', (event, d) => {
      event.stopPropagation()
 // 
      linkGroup.selectAll('path').attr('stroke', '#C0C0C0').attr('stroke-width', 1.5)
      linkLabelBg.attr('fill', 'rgba(20,25,40,0.92)')
      linkLabels.attr('fill', 'rgba(255,255,255,0.45)')
 // 
      d3.select(event.target).attr('stroke', '#3b82f6').attr('stroke-width', 2.5)
      
      selectedItem.value = {
        type: 'edge',
        data: d.rawData
      }
      d3.select(event.target).attr('stroke', '#BDEBB5').attr('stroke-width', 2.5)
    })

 // Link labels background ()
  const linkLabelBg = linkGroup.selectAll('rect')
    .data(edges)
    .enter().append('rect')
    .attr('fill', 'rgba(20,25,40,0.92)')
    .attr('rx', 3)
    .attr('ry', 3)
    .style('cursor', 'pointer')
    .style('pointer-events', 'all')
    .style('display', showEdgeLabels.value ? 'block' : 'none')
    .on('click', (event, d) => {
      event.stopPropagation()
      linkGroup.selectAll('path').attr('stroke', '#C0C0C0').attr('stroke-width', 1.5)
      linkLabelBg.attr('fill', 'rgba(20,25,40,0.92)')
      linkLabels.attr('fill', 'rgba(255,255,255,0.45)')
 // 
      link.filter(l => l === d).attr('stroke', '#BDEBB5').attr('stroke-width', 2.5)
      d3.select(event.target).attr('fill', 'rgba(189,235,181,0.2)')
      
      selectedItem.value = {
        type: 'edge',
        data: d.rawData
      }
    })

  // Link labels
  const linkLabels = linkGroup.selectAll('text')
    .data(edges)
    .enter().append('text')
    .text(d => d.name)
    .attr('font-size', '9px')
    .attr('fill', 'rgba(255,255,255,0.45)')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .style('cursor', 'pointer')
    .style('pointer-events', 'all')
    .style('font-family', 'system-ui, sans-serif')
    .style('display', showEdgeLabels.value ? 'block' : 'none')
    .on('click', (event, d) => {
      event.stopPropagation()
      linkGroup.selectAll('path').attr('stroke', '#C0C0C0').attr('stroke-width', 1.5)
      linkLabelBg.attr('fill', 'rgba(20,25,40,0.92)')
      linkLabels.attr('fill', 'rgba(255,255,255,0.45)')
 // 
      link.filter(l => l === d).attr('stroke', '#BDEBB5').attr('stroke-width', 2.5)
      d3.select(event.target).attr('fill', '#BDEBB5')
      
      selectedItem.value = {
        type: 'edge',
        data: d.rawData
      }
    })
    .on('mouseenter', (event, d) => {
      showTooltip(event, d, 'edge')
    })
    .on('mouseleave', () => {
      hideTooltip()
    })
  
 // 
  linkLabelsRef = linkLabels
  linkLabelBgRef = linkLabelBg

  // Nodes group
  const nodeGroup = g.append('g').attr('class', 'nodes')
  
  // Node circles
  const node = nodeGroup.selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('r', 10)
    .attr('fill', d => getColor(d.type))
    .attr('stroke', '#0a0a0a')
    .attr('stroke-width', 1.5)
    .style('cursor', 'pointer')
    .style('transition', 'r 0.3s ease, stroke 0.3s ease, stroke-width 0.3s ease')
    .call(d3.drag()
      .on('start', (event, d) => {
 // ，（）
        d.fx = d.x
        d.fy = d.y
        d._dragStartX = event.x
        d._dragStartY = event.y
        d._isDragging = false
      })
      .on('drag', (event, d) => {
 // （）
        const dx = event.x - d._dragStartX
        const dy = event.y - d._dragStartY
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (!d._isDragging && distance > 3) {
 // ，
          d._isDragging = true
          simulation.alphaTarget(0.3).restart()
        }
        
        if (d._isDragging) {
          d.fx = event.x
          d.fy = event.y
        }
      })
      .on('end', (event, d) => {
 // 结束拖拽后流畅过渡
        if (d._isDragging) {
          simulation.alphaTarget(0.15).restart()
          setTimeout(() => {
            simulation.alphaTarget(0)
          }, 500)
        }

        // 持续保持节点位置一小段时间，以免立即回弹断开
        d.fx = event.x
        d.fy = event.y
        setTimeout(() => {
          d.fx = null
          d.fy = null
        }, 300)

        d._isDragging = false
      })
    )
    .on('click', (event, d) => {
      event.stopPropagation()
 // 
      node.transition().duration(300).attr('r', 10).attr('stroke', '#0a0a0a').attr('stroke-width', 1.5)
      linkGroup.selectAll('path').transition().duration(300).attr('stroke', '#C0C0C0').attr('stroke-width', 1.5)
 // 
      d3.select(event.target).transition().duration(300).attr('r', 14).attr('stroke', '#BDEBB5').attr('stroke-width', 3)
 // 
      link.filter(l => l.source.id === d.id || l.target.id === d.id)
        .transition().duration(300)
        .attr('stroke', '#BDEBB5')
        .attr('stroke-width', 2)
      
      selectedItem.value = {
        type: 'node',
        data: d.rawData,
        entityType: d.type,
        color: getColor(d.type)
      }
    })
    .on('mouseenter', (event, d) => {
      if (!selectedItem.value || selectedItem.value.data?.uuid !== d.rawData.uuid) {
        d3.select(event.target).transition().duration(200).attr('r', 12).attr('stroke', 'rgba(189,235,181,0.8)').attr('stroke-width', 2)
        showTooltip(event, d, 'node')
      }
    })
    .on('mouseleave', (event, d) => {
      if (!selectedItem.value || selectedItem.value.data?.uuid !== d.rawData.uuid) {
        d3.select(event.target).transition().duration(200).attr('r', 10).attr('stroke', '#0a0a0a').attr('stroke-width', 1.5)
        hideTooltip()
      }
    })

  // Node Labels
  const nodeLabels = nodeGroup.selectAll('text')
    .data(nodes)
    .enter().append('text')
    .text(d => d.name.length > 8 ? d.name.substring(0, 8) + '…' : d.name)
    .attr('font-size', '11px')
    .attr('fill', 'rgba(255,255,255,0.75)')
    .attr('font-weight', '500')
    .attr('dx', 14)
    .attr('dy', 4)
    .style('pointer-events', 'none')
    .style('font-family', 'system-ui, sans-serif')

  simulation.on('tick', () => {
 // 
    link.attr('d', d => getLinkPath(d))
    
 // （None，）
    linkLabels.each(function(d) {
      const mid = getLinkMidpoint(d)
      d3.select(this)
        .attr('x', mid.x)
        .attr('y', mid.y)
 .attr('transform', '') // ，
    })
    
 // 
    linkLabelBg.each(function(d, i) {
      const mid = getLinkMidpoint(d)
      const textEl = linkLabels.nodes()[i]
      const bbox = textEl.getBBox()
      d3.select(this)
        .attr('x', mid.x - bbox.width / 2 - 4)
        .attr('y', mid.y - bbox.height / 2 - 2)
        .attr('width', bbox.width + 8)
        .attr('height', bbox.height + 4)
 .attr('transform', '') // 
    })

    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)

    nodeLabels
      .attr('x', d => d.x)
      .attr('y', d => d.y)
  })
  
 // 
  svg.on('click', () => {
    selectedItem.value = null
    node.attr('stroke', '#0a0a0a').attr('stroke-width', 1.5)
    linkGroup.selectAll('path').attr('stroke', '#C0C0C0').attr('stroke-width', 1.5)
    linkLabelBg.attr('fill', 'rgba(20,25,40,0.92)')
    linkLabels.attr('fill', 'rgba(255,255,255,0.45)')
  })
}

watch(() => props.graphData, () => {
  nextTick(renderGraph)
}, { deep: true })

// 
watch(showEdgeLabels, (newVal) => {
  if (linkLabelsRef) {
    linkLabelsRef.style('display', newVal ? 'block' : 'none')
  }
  if (linkLabelBgRef) {
    linkLabelBgRef.style('display', newVal ? 'block' : 'none')
  }
})

const handleResize = () => {
  nextTick(renderGraph)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (currentSimulation) {
    currentSimulation.stop()
  }
})
</script>

<style scoped>
/* ── GRAPH PANEL — Dark Financial Theme ── */
.graph-panel {
  position: relative;
  width: 100%;
  height: 100%;
  background: #030506;
  background-image:
    linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
  background-size: 32px 32px;
  overflow: hidden;
}

.graph-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.graph-bg-video {
  position: absolute;
  inset: 0;
  width: 140%;
  height: 140%;
  left: -20%;
  top: -20%;
  object-fit: cover;
  opacity: 0.22;
  transform: scale(1.03);
  pointer-events: none;
  transition: opacity 0.25s ease;
  z-index: 1;
}

.graph-bg-video:hover {
  opacity: 0.38;
  transform: scale(1.05);
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
  font-family: 'IBM Plex Mono', monospace;
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
.tool-btn .btn-text { font-size: 11px; font-family: 'IBM Plex Mono', monospace; letter-spacing: 0.05em; }

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
  font-family: 'IBM Plex Mono', monospace;
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
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 600;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.detail-type-badge {
  font-size: 9px;
  font-family: 'IBM Plex Mono', monospace;
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
  font-family: 'IBM Plex Mono', monospace;
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
  font-family: 'IBM Plex Mono', monospace;
  font-size: 10px;
  color: #60a5fa;
}

.detail-section { margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.07); }
.detail-section-title {
  font-size: 9px;
  font-family: 'IBM Plex Mono', monospace;
  color: rgba(255,255,255,0.3);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.labels-list { display: flex; flex-wrap: wrap; gap: 4px; }
.label-tag {
  font-size: 9px;
  font-family: 'IBM Plex Mono', monospace;
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
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: #60a5fa; font-weight: 600;
}
.edge-arrow { color: rgba(255,255,255,0.25); font-size: 10px; }
.edge-label {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  color: rgba(255,255,255,0.4); letter-spacing: 0.08em;
}
.edge-count-badge {
  font-size: 9px; font-family: 'IBM Plex Mono', monospace;
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
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
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
  font-family: 'IBM Plex Mono', monospace;
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

/* ── EDGE LABEL TOGGLE ── */
/* ── EDGE LABEL TOGGLE ── */
.edge-labels-toggle {
  position: absolute;
  top: 14px; left: 50%; transform: translateX(-50%);
  display: flex; align-items: center; gap: 8px;
  background: #000000;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 6px 14px;
  backdrop-filter: blur(12px);
  z-index: 15;
}
.toggle-label {
  font-size: 10px;
  font-family: Arial, sans-serif;
  color: #BDEBB5;
  letter-spacing: 0.08em;
  white-space: nowrap;
}
.toggle-switch { position: relative; width: 32px; height: 18px; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; cursor: pointer;
  inset: 0; background: rgba(189,235,181,0.2);
  border-radius: 18px; transition: 0.2s;
}
.slider:before {
  content: '';
  position: absolute;
  height: 12px; width: 12px;
  left: 3px; bottom: 3px;
  background: rgba(255,255,255,0.85);
  border-radius: 50%; transition: 0.2s;
}
input:checked + .slider { background: rgba(189,235,181,0.5); }
input:checked + .slider:before { background: #BDEBB5; transform: translateX(14px); }

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
  font-family: 'IBM Plex Mono', monospace;
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
</style>
