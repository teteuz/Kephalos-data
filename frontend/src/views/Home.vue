<template>
  <div class="k">

    <!-- NAV -->
    <nav class="k-nav">
      <div class="k-brand">
        <img src="/kephalos-logo.png" alt="KEPHALOS" class="k-logo-img" />
      </div>

      <div class="k-nav-center">
        <span class="k-nav-item">Platform</span>
        <span class="k-nav-item">Research</span>
        <span class="k-nav-item">Use Cases</span>
      </div>

      <div class="k-nav-right">
        <div class="k-status">
          <span class="k-status-dot"></span>
          <span>Systems online</span>
        </div>
        <button class="k-nav-btn" @click="scrollToConsole">Run Simulation</button>
      </div>
    </nav>

    <!-- HERO -->
    <section class="k-hero">
      <canvas ref="heroCanvas" class="k-canvas"></canvas>

      <div class="k-hero-body">
        <div class="k-eyebrow">
          <span class="k-eyebrow-line"></span>
          <span>MULTI-AGENT PREDICTION ENGINE</span>
        </div>

        <h1 class="k-title">
          What will people do<br>
          <span class="k-title-dim">when it happens?</span>
        </h1>

        <p class="k-subtitle">
          Upload any document. Kephalos builds a knowledge graph, generates up to 500 autonomous agents from real entities, and simulates how decisions, crises, and narratives unfold — before you commit to anything.
        </p>

        <div class="k-hero-cta">
          <button class="k-btn-run" @click="scrollToConsole">
            Run a simulation
            <svg viewBox="0 0 16 16" fill="currentColor" width="13" height="13"><path d="M3 8l10 0M9 4l4 4-4 4"/></svg>
          </button>
          <div class="k-hero-meta">
            <span>Up to 500 agents</span>
            <span class="k-dot">·</span>
            <span>Any document</span>
            <span class="k-dot">·</span>
            <span>Dual-platform</span>
          </div>
        </div>
      </div>

      <!-- Floating data readout -->
      <div class="k-readout">
        <div class="k-readout-row" v-for="(r, i) in readouts" :key="i">
          <span class="k-readout-key">{{ r.key }}</span>
          <span class="k-readout-val" :class="r.cls">{{ r.val }}</span>
        </div>
        <div class="k-readout-bar">
          <div class="k-readout-fill"></div>
        </div>
        <div class="k-readout-label">SYSTEM READY</div>
      </div>
    </section>

    <!-- WHAT IT DOES — horizontal scroll of use cases -->
    <section class="k-usecases">
      <div class="k-uc-header">
        <span class="k-label">WHERE IT WORKS</span>
      </div>
      <div class="k-uc-grid">
        <div class="k-uc" v-for="uc in usecases" :key="uc.id">
          <div class="k-uc-num">{{ uc.id }}</div>
          <div class="k-uc-icon">{{ uc.icon }}</div>
          <div class="k-uc-title">{{ uc.title }}</div>
          <div class="k-uc-desc">{{ uc.desc }}</div>
          <div class="k-uc-tag">{{ uc.tag }}</div>
        </div>
      </div>
    </section>

    <!-- CONSOLE -->
    <section class="k-console" id="console" ref="consoleRef">
      <div class="k-console-left">
        <div class="k-label">RUN A SIMULATION</div>
        <h2 class="k-console-title">Feed the engine.<br>See what happens.</h2>
        <p class="k-console-desc">Upload intelligence in any format. Set your objective. The engine extracts entities, builds a graph, and spawns a world of agents that play it out.</p>

        <div class="k-pipeline">
          <div class="k-pipe" v-for="(step, i) in pipelineSteps" :key="i">
            <div class="k-pipe-num">{{ String(i+1).padStart(2,'0') }}</div>
            <div class="k-pipe-name">{{ step.title }}</div>
          </div>
        </div>
      </div>

      <div class="k-console-right">
        <!-- Terminal header -->
        <div class="k-term-header">
          <div class="k-term-dots">
            <span></span><span></span><span></span>
          </div>
          <span class="k-term-title">kephalos — engine console</span>
          <span class="k-term-badge">v1.0</span>
        </div>

        <div class="k-term-body">
          <!-- File input -->
          <div class="k-term-section">
            <div class="k-term-label">
              <span class="k-term-num">01</span>
              <span>INTELLIGENCE FEED</span>
              <span class="k-term-hint">pdf · md · txt</span>
            </div>

            <div
              class="k-dropzone"
              :class="{ hover: isDragOver, filled: files.length > 0 }"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
            >
              <input ref="fileInput" type="file" multiple accept=".pdf,.md,.txt" @change="handleFileSelect" style="display:none" />
              <div v-if="!files.length" class="k-drop-empty">
                <div class="k-drop-icon">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
                  </svg>
                </div>
                <span>Drop document or click to browse</span>
              </div>
              <div v-else class="k-drop-files">
                <div class="k-drop-file" v-for="(f, i) in files" :key="i">
                  <span class="k-file-ext">{{ f.name.split('.').pop() }}</span>
                  <span class="k-file-name">{{ f.name }}</span>
                  <button class="k-file-rm" @click.stop="files.splice(i,1)">×</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Directive -->
          <div class="k-term-section">
            <div class="k-term-label">
              <span class="k-term-num">02</span>
              <span>SIMULATION DIRECTIVE</span>
              <div class="k-tpls">
                <button
                  v-for="tpl in directiveTemplates" :key="tpl.id"
                  :class="['k-tpl', { on: activeTpl === tpl.id }]"
                  @click.stop="applyTemplate(tpl)"
                >{{ tpl.short }}</button>
              </div>
            </div>

            <div class="k-textarea-wrap">
              <textarea
                v-model="formData.simulationRequirement"
                class="k-textarea"
                :placeholder="currentPlaceholder"
                rows="5"
                :disabled="loading"
              ></textarea>
              <span class="k-textarea-ver">KEPHALOS-V1.0</span>
            </div>
          </div>

          <!-- Launch -->
          <button class="k-launch" :disabled="!canSubmit || loading" @click="startSimulation">
            <span class="k-launch-pre">$</span>
            <span>{{ loading ? 'initializing...' : 'kephalos run --parallel --agents=max' }}</span>
            <svg v-if="!loading" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
          </button>
        </div>
      </div>
    </section>

    <HistoryDatabase />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'

const router = useRouter()
const consoleRef = ref(null)
const heroCanvas = ref(null)
const fileInput = ref(null)

const readouts = [
  { key: 'ENGINE', val: 'ONLINE', cls: 'green' },
  { key: 'AGENTS', val: 'UP TO 500', cls: '' },
  { key: 'PLATFORMS', val: 'DUAL', cls: '' },
  { key: 'VERSION', val: 'v0.1-PREVIEW', cls: '' },
]

const usecases = [
  { id: '01', icon: '◈', title: 'Financial Markets', desc: 'Simulate how investors, media, and analysts react to announcements before you make them. Identify the narrative that dominates.', tag: 'MARKET INTELLIGENCE' },
  { id: '02', icon: '◆', title: 'Policy & Governance', desc: 'Stress-test legislation or institutional decisions against simulated stakeholder populations before public release.', tag: 'POLICY SIMULATION' },
  { id: '03', icon: '◇', title: 'Crisis Management', desc: 'Run counterfactual scenarios. What if you responded differently at decision point X? Find the optimal path through uncertainty.', tag: 'COUNTERFACTUAL ANALYSIS' },
]

const pipelineSteps = [
  { icon: '◈', title: 'Graph Construction', desc: 'Reality seeds extracted and injected into a GraphRAG knowledge graph with temporal memory.' },
  { icon: '◉', title: 'Environment Setup', desc: 'Entities become agents. Personas, relationships, and parameters auto-generated.' },
  { icon: '▶', title: 'Simulation Run', desc: 'Dual-platform parallel simulation across Twitter-like and Reddit-like environments.' },
  { icon: '◆', title: 'Report Generation', desc: 'ReportAgent performs deep post-simulation analysis with full tool access.' },
  { icon: '◇', title: 'Deep Interaction', desc: 'Converse with any agent or interrogate the ReportAgent directly.' },
]

const directiveTemplates = [
  { id: 'decision', short: 'DECISION', label: 'Optimize decision', text: 'Given this scenario, what is the optimal decision to maximize positive outcomes and minimize risk? Simulate how different stakeholder groups react and identify the strategy with the best risk-reward profile.' },
  { id: 'narrative', short: 'NARRATIVE', label: 'Narrative spread', text: 'Simulate how narratives and public opinion will evolve across social platforms over the next 72 hours. Which information spreads fastest? Which groups amplify or defuse the situation?' },
  { id: 'crisis', short: 'CRISIS', label: 'Crisis response', text: 'If this crisis escalates, simulate the institutional response strategies and their outcomes. Which approach best preserves reputation and restores stakeholder trust?' },
  { id: 'market', short: 'MARKET', label: 'Market reaction', text: 'Simulate how market participants — investors, analysts, competitors, media — will react to this event. What narrative shifts emerge?' },
]

const activeTpl = ref(null)
const formData = ref({ simulationRequirement: '' })
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)

const currentPlaceholder = '// describe your simulation objective\n// e.g. given this scenario, what is the optimal decision to maximize results and minimize risk?'

const canSubmit = computed(() =>
  formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
)

const applyTemplate = (tpl) => {
  activeTpl.value = tpl.id
  formData.value.simulationRequirement = tpl.text
}

const handleFileSelect = (e) => { addFiles(Array.from(e.target.files)) }
const handleDrop = (e) => { isDragOver.value = false; addFiles(Array.from(e.dataTransfer.files)) }
const addFiles = (f) => {
  files.value.push(...f.filter(x => ['pdf','md','txt'].includes(x.name.split('.').pop().toLowerCase())))
}

const scrollToConsole = () => document.getElementById('console')?.scrollIntoView({ behavior: 'smooth' })

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}

// Minimal particle field
let raf = null
onMounted(() => {
  const c = heroCanvas.value
  if (!c) return
  const resize = () => { c.width = c.offsetWidth; c.height = c.offsetHeight }
  resize()
  window.addEventListener('resize', resize)

  const pts = Array.from({ length: 80 }, () => ({
    x: Math.random(), y: Math.random(),
    vx: (Math.random() - 0.5) * 0.0003,
    vy: (Math.random() - 0.5) * 0.0003,
    r: Math.random() * 0.8 + 0.2
  }))

  const draw = () => {
    if (!c) return
    const ctx = c.getContext('2d')
    const W = c.width, H = c.height
    ctx.clearRect(0, 0, W, H)

    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy
      if (p.x < 0) p.x = 1; if (p.x > 1) p.x = 0
      if (p.y < 0) p.y = 1; if (p.y > 1) p.y = 0
    })

    pts.forEach((a, i) => {
      pts.forEach((b, j) => {
        if (j <= i) return
        const dx = (a.x - b.x) * W, dy = (a.y - b.y) * H
        const d = Math.sqrt(dx * dx + dy * dy)
        if (d > 140) return
        ctx.beginPath()
        ctx.moveTo(a.x * W, a.y * H)
        ctx.lineTo(b.x * W, b.y * H)
        ctx.strokeStyle = `rgba(255,255,255,${(1 - d / 140) * 0.04})`
        ctx.lineWidth = 1
        ctx.stroke()
      })
      ctx.beginPath()
      ctx.arc(a.x * W, a.y * H, a.r, 0, Math.PI * 2)
      ctx.fillStyle = 'rgba(255,255,255,0.15)'
      ctx.fill()
    })

    raf = requestAnimationFrame(draw)
  }
  draw()
})
onUnmounted(() => { if (raf) cancelAnimationFrame(raf) })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;700&display=swap');

/* ─── BASE ─── */
.k {
  min-height: 100vh;
  background: #080808;
  color: #fff;
  font-family: 'Roboto Mono', monospace;
  --mono: 'Roboto Mono', 'JetBrains Mono', monospace;
}

/* ─── NAV ─── */
.k-nav {
  position: sticky; top: 0; z-index: 100;
  height: 56px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  background: rgba(8,8,8,0.9);
  backdrop-filter: blur(24px);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 40px;
}

.k-brand { display: flex; align-items: center; cursor: pointer; }
.k-logo-img { height: 64px; width: auto; display: block; }

.k-nav-center { display: flex; gap: 2px; }
.k-nav-item {
  font-size: 0.84rem; color: rgba(255,255,255,0.38);
  padding: 6px 14px; border-radius: 6px;
  cursor: pointer; transition: color 0.12s, background 0.12s;
}
.k-nav-item:hover { color: rgba(255,255,255,0.85); background: rgba(255,255,255,0.04); }

.k-nav-right { display: flex; align-items: center; gap: 20px; }

.k-status {
  display: flex; align-items: center; gap: 7px;
  font-family: var(--mono); font-size: 0.66rem;
  letter-spacing: 0.06em; color: rgba(255,255,255,0.3);
}
.k-status-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #22c55e; box-shadow: 0 0 6px #22c55e;
  animation: pulse 2.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

.k-nav-btn {
  background: #fff; color: #000;
  border: none; padding: 7px 16px;
  font-size: 0.82rem; font-weight: 600;
  border-radius: 6px; cursor: pointer;
  font-family: 'Roboto Mono', monospace;
  transition: opacity 0.12s;
}
.k-nav-btn:hover { opacity: 0.85; }

/* ─── HERO ─── */
.k-hero {
  position: relative;
  min-height: 88vh;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 0 40px 0 80px;
  gap: 60px;
  overflow: hidden;
}

.k-canvas {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  pointer-events: none;
}

.k-hero-body {
  position: relative; z-index: 2;
  max-width: 620px;
  display: flex; flex-direction: column; gap: 0;
}

.k-eyebrow {
  display: flex; align-items: center; gap: 14px;
  font-family: var(--mono); font-size: 0.66rem;
  letter-spacing: 0.14em; color: rgba(255,255,255,0.3);
  margin-bottom: 28px;
}
.k-eyebrow-line { width: 24px; height: 1px; background: rgba(255,255,255,0.2); }

.k-title {
  font-size: clamp(2.8rem, 5.5vw, 4.8rem);
  font-weight: 800; line-height: 1.06;
  letter-spacing: -0.04em; color: #fff;
  margin-bottom: 20px;
}
.k-title-dim { color: rgba(255,255,255,0.48); font-weight: 300; }

.k-subtitle {
  font-size: 0.95rem; line-height: 1.75;
  color: rgba(255,255,255,0.4); font-weight: 400;
  margin-bottom: 36px; max-width: 500px;
}

.k-hero-cta { display: flex; flex-direction: column; gap: 16px; }

.k-btn-run {
  display: inline-flex; align-items: center; gap: 10px;
  background: #fff; color: #000;
  border: none; padding: 13px 24px;
  font-size: 0.88rem; font-weight: 700;
  border-radius: 8px; cursor: pointer;
  font-family: 'Roboto Mono', monospace;
  width: fit-content;
  transition: all 0.12s;
}
.k-btn-run:hover { background: rgba(255,255,255,0.88); transform: translateY(-1px); }
.k-btn-run svg { stroke: #000; }

.k-hero-meta {
  display: flex; align-items: center; gap: 10px;
  font-family: var(--mono); font-size: 0.66rem;
  color: rgba(255,255,255,0.25); letter-spacing: 0.04em;
}
.k-dot { color: rgba(255,255,255,0.12); }

/* Floating readout panel */
.k-readout {
  position: relative; z-index: 2;
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(20px);
  border-radius: 10px;
  padding: 20px 24px;
  min-width: 220px;
  display: flex; flex-direction: column; gap: 10px;
}
.k-readout-row {
  display: flex; justify-content: space-between; align-items: center;
}
.k-readout-key {
  font-family: var(--mono); font-size: 0.62rem;
  color: rgba(255,255,255,0.28); letter-spacing: 0.1em;
}
.k-readout-val {
  font-family: var(--mono); font-size: 0.72rem;
  color: rgba(255,255,255,0.65); font-weight: 500;
}
.k-readout-val.green { color: #22c55e; }

.k-readout-bar {
  height: 2px; background: rgba(255,255,255,0.06);
  border-radius: 1px; margin-top: 4px; overflow: hidden;
}
.k-readout-fill {
  height: 100%; width: 100%;
  background: linear-gradient(90deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1));
  border-radius: 1px;
  animation: scan 3s ease-in-out infinite;
}
@keyframes scan { 0%,100%{transform:translateX(-100%)} 50%{transform:translateX(100%)} }

.k-readout-label {
  font-family: var(--mono); font-size: 0.6rem;
  color: rgba(255,255,255,0.2); letter-spacing: 0.14em; text-align: right;
}

/* ─── USE CASES ─── */
.k-usecases {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 64px 80px;
}
.k-uc-header {
  margin-bottom: 40px;
}
.k-label {
  font-family: var(--mono); font-size: 0.62rem;
  letter-spacing: 0.16em; color: rgba(255,255,255,0.25);
}

.k-uc-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 10px;
  overflow: hidden;
}
.k-uc {
  background: #080808;
  padding: 32px 28px;
  display: flex; flex-direction: column; gap: 12px;
  transition: background 0.15s;
}
.k-uc:hover { background: rgba(255,255,255,0.02); }

.k-uc-num {
  font-family: var(--mono); font-size: 0.6rem;
  color: rgba(255,255,255,0.18); letter-spacing: 0.1em;
}
.k-uc-icon { font-size: 1.2rem; color: rgba(255,255,255,0.5); }
.k-uc-title { font-size: 1rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; }
.k-uc-desc { font-size: 0.8rem; color: rgba(255,255,255,0.38); line-height: 1.65; flex: 1; }
.k-uc-tag {
  font-family: var(--mono); font-size: 0.58rem;
  letter-spacing: 0.1em; color: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.08);
  padding: 3px 8px; border-radius: 4px; width: fit-content;
}

/* ─── CONSOLE ─── */
.k-console {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 80px;
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 80px;
  align-items: start;
}

.k-console-left { padding-top: 4px; }

.k-console-title {
  font-size: 2rem; font-weight: 800;
  letter-spacing: -0.03em; line-height: 1.15; color: #fff;
  margin: 14px 0 16px;
}
.k-console-desc {
  font-size: 0.88rem; color: rgba(255,255,255,0.38);
  line-height: 1.75; margin-bottom: 36px; max-width: 380px;
}

.k-pipeline { display: flex; flex-direction: column; gap: 0; }
.k-pipe {
  display: flex; align-items: center; gap: 16px;
  padding: 10px 0;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.k-pipe:last-child { border-bottom: 1px solid rgba(255,255,255,0.06); }
.k-pipe-num {
  font-family: var(--mono); font-size: 0.6rem;
  color: rgba(255,255,255,0.2); letter-spacing: 0.1em; min-width: 24px;
}
.k-pipe-name { font-size: 0.82rem; color: rgba(255,255,255,0.45); }

/* Terminal card */
.k-console-right {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; overflow: hidden;
  background: rgba(255,255,255,0.02);
}

.k-term-header {
  background: rgba(255,255,255,0.03);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding: 11px 16px;
  display: flex; align-items: center; gap: 8px;
}
.k-term-dots { display: flex; gap: 5px; }
.k-term-dots span {
  width: 9px; height: 9px; border-radius: 50%;
  background: rgba(255,255,255,0.08);
}
.k-term-dots span:first-child { background: rgba(255,255,255,0.25); }
.k-term-title {
  font-family: var(--mono); font-size: 0.62rem;
  color: rgba(255,255,255,0.22); letter-spacing: 0.06em; flex: 1; margin-left: 4px;
}
.k-term-badge {
  font-family: var(--mono); font-size: 0.58rem;
  color: rgba(255,255,255,0.3);
}

.k-term-body { padding: 20px; display: flex; flex-direction: column; gap: 20px; }

.k-term-section { display: flex; flex-direction: column; gap: 10px; }

.k-term-label {
  display: flex; align-items: center; gap: 10px;
  font-family: var(--mono); font-size: 0.6rem;
  letter-spacing: 0.1em; color: rgba(255,255,255,0.28);
}
.k-term-num {
  background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6);
  font-size: 0.56rem; font-weight: 600; padding: 2px 6px;
}
.k-term-hint { margin-left: auto; color: rgba(255,255,255,0.15); }

/* Drop zone */
.k-dropzone {
  border: 1px solid rgba(255,255,255,0.08); border-radius: 7px;
  min-height: 110px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; background: rgba(255,255,255,0.02); transition: all 0.15s;
  overflow-y: auto;
}
.k-dropzone.hover, .k-dropzone:hover {
  border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.04);
}
.k-dropzone.filled { align-items: flex-start; padding: 12px; }

.k-drop-empty {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  color: rgba(255,255,255,0.2); font-size: 0.8rem;
}
.k-drop-icon {
  width: 36px; height: 36px;
  border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
.k-drop-files { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.k-drop-file {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 5px; padding: 7px 10px;
}
.k-file-ext {
  font-family: var(--mono); font-size: 0.58rem; font-weight: 600;
  color: rgba(255,255,255,0.4); text-transform: uppercase;
  border: 1px solid rgba(255,255,255,0.12); padding: 1px 5px; border-radius: 3px;
}
.k-file-name { flex: 1; font-size: 0.78rem; color: rgba(255,255,255,0.5); }
.k-file-rm { background: none; border: none; color: rgba(255,255,255,0.2); font-size: 1rem; cursor: pointer; transition: color 0.1s; }
.k-file-rm:hover { color: rgba(255,80,80,0.8); }

/* Template pills */
.k-tpls { display: flex; gap: 3px; margin-left: auto; }
.k-tpl {
  font-family: var(--mono); font-size: 0.55rem; font-weight: 600;
  letter-spacing: 0.08em; padding: 2px 7px;
  border: 1px solid rgba(255,255,255,0.08);
  background: transparent; color: rgba(255,255,255,0.28);
  border-radius: 3px; cursor: pointer; transition: all 0.1s;
}
.k-tpl:hover { border-color: rgba(255,255,255,0.2); color: rgba(255,255,255,0.6); }
.k-tpl.on { background: rgba(255,255,255,0.1); color: #fff; border-color: rgba(255,255,255,0.25); }

/* Textarea */
.k-textarea-wrap { position: relative; }
.k-textarea {
  width: 100%; border: 1px solid rgba(255,255,255,0.08); border-radius: 7px;
  background: rgba(255,255,255,0.02); padding: 13px;
  font-family: var(--mono); font-size: 0.76rem; line-height: 1.7;
  color: rgba(255,255,255,0.8); resize: vertical; outline: none;
  transition: border-color 0.15s;
}
.k-textarea:focus { border-color: rgba(255,255,255,0.2); }
.k-textarea::placeholder { color: rgba(255,255,255,0.18); }
.k-textarea-ver {
  position: absolute; bottom: 9px; right: 12px;
  font-family: var(--mono); font-size: 0.56rem;
  color: rgba(255,255,255,0.15); letter-spacing: 0.08em;
}

/* Launch button */
.k-launch {
  width: 100%;
  background: #fff; color: #000;
  border: none; padding: 13px 18px; border-radius: 7px;
  font-family: var(--mono); font-size: 0.76rem; font-weight: 600;
  letter-spacing: 0.04em;
  display: flex; align-items: center; gap: 10px;
  cursor: pointer; transition: all 0.12s;
}
.k-launch:hover:not(:disabled) { background: rgba(255,255,255,0.88); transform: translateY(-1px); }
.k-launch:disabled { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.2); cursor: not-allowed; }
.k-launch-pre { color: rgba(0,0,0,0.3); font-size: 1rem; }
.k-launch span:nth-child(2) { flex: 1; text-align: left; }
.k-launch svg { margin-left: auto; flex-shrink: 0; }
.k-launch:disabled .k-launch-pre { color: rgba(255,255,255,0.15); }
.k-launch:disabled svg { display: none; }

@media (max-width: 1100px) {
  .k-hero { grid-template-columns: 1fr; padding: 60px 40px; }
  .k-readout { display: none; }
  .k-uc-grid { grid-template-columns: repeat(1, 1fr); }
  .k-console { grid-template-columns: 1fr; padding: 60px 40px; }
  .k-title { font-size: 2.8rem; }
  .k-nav-center { display: none; }
}
</style>
