<template>
  <div class="k">

    <!-- NAV -->
    <nav class="k-nav">
      <div class="k-brand">
        <img src="/kephalos-logo.png" alt="KEPHALOS" class="k-logo-img" />
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
        </div>
      </div>

      <!-- Brain image -->
      <video src="/ai orb 2.webm" alt="AI Orb Animation" class="k-brain-image" autoplay loop muted playsinline preload="auto" style="display: block;"></video>
    </section>

    <!-- WHAT IT DOES — horizontal scroll of use cases -->
    <section class="k-usecases">
      <div class="k-uc-header">
        <span class="k-label">WHERE IT WORKS</span>
      </div>
      <div class="k-uc-grid">
        <div class="k-uc" v-for="uc in usecases" :key="uc.id">
          <div class="k-uc-title">{{ uc.title }}</div>
          <div class="k-uc-desc">{{ uc.desc }}</div>
          <div class="k-uc-tag">{{ uc.tag }}</div>
        </div>
      </div>
    </section>

    <!-- CONSOLE -->
    <section class="k-console" id="console">
      <!-- Text Section Above Console -->
      <div class="k-console-intro">
        <div class="k-label">RUN A SIMULATION</div>
        <h2 class="k-console-title">Feed the engine.<br>See what happens.</h2>
        <p class="k-console-desc">Upload intelligence in any format. Set your objective. The engine extracts entities, builds a graph, and spawns a world of agents that play it out.</p>
      </div>

      <!-- Centered Console with Glass Effect -->
      <div class="k-console-center">
        <div class="k-console-right">
          <!-- Terminal header -->
          <div class="k-term-header">
            <span class="k-term-title">KEPHALOS-DATA</span>
          </div>

          <div class="k-term-body">
            <!-- File input -->
            <div class="k-term-section">
              <div class="k-term-label">
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

const pipelineSteps = []

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

// Minimal particle field + Intersection Observer
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
  background: #BDEBB5; box-shadow: 0 0 6px #BDEBB5;
  animation: pulse 2.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

.k-nav-btn {
  background: linear-gradient(135deg, #BDEBB5 0%, #A8E6A1 100%);
  color: #000;
  border: none; padding: 7px 16px;
  font-size: 0.82rem; font-weight: 600;
  border-radius: 6px; cursor: pointer;
  font-family: 'Roboto Mono', monospace;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(189, 235, 181, 0.3);
  position: relative;
  overflow: hidden;
}
.k-nav-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}
.k-nav-btn:hover::before {
  left: 100%;
}
.k-nav-btn:hover { 
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(189, 235, 181, 0.4);
}

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
  font-family: var(--mono);
}
.k-title-dim { color: #fff; font-weight: 300; }

.k-subtitle {
  font-size: 0.95rem; line-height: 1.75;
  color: rgba(255,255,255,0.4); font-weight: 400;
  margin-bottom: 36px; max-width: 500px;
}

.k-hero-cta { display: flex; flex-direction: column; gap: 16px; }

.k-btn-run {
  display: inline-flex; align-items: center; gap: 10px;
  background: linear-gradient(135deg, #BDEBB5 0%, #A8E6A1 100%);
  color: #000;
  border: none; padding: 13px 24px;
  font-size: 0.88rem; font-weight: 700;
  border-radius: 8px; cursor: pointer;
  font-family: 'Roboto Mono', monospace;
  width: fit-content;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(189, 235, 181, 0.3);
  position: relative;
  overflow: hidden;
}
.k-btn-run::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}
.k-btn-run:hover::before {
  left: 100%;
}
.k-btn-run:hover { 
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(189, 235, 181, 0.4);
}
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
.k-readout-val.green { color: #BDEBB5; }

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

.k-brain-image {
  width: 100%;
  height: auto;
  max-width: 650px;
  object-fit: contain;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-left: -150px;
  animation: brainPulse 5.5s ease-in-out infinite;
}

.k-brain-image:hover {
  filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6)) drop-shadow(0 0 40px rgba(59, 130, 246, 0.3));
}

@keyframes brainPulse {
  0%, 100% {
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.2)) drop-shadow(0 0 20px rgba(255, 255, 255, 0.1));
  }
  50% {
    filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.4)) drop-shadow(0 0 50px rgba(255, 255, 255, 0.2));
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
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
..k-uc:hover { background: rgba(255,255,255,0.03); }

.k-uc-title { font-size: 1.1rem; font-weight: 700; color: #ffffff; }
.k-uc-desc { font-size: 0.9rem; color: rgba(255,255,255,0.75); line-height: 1.55; }
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 60px;
}

.k-console-intro {
  text-align: center;
  max-width: 680px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.k-console-title {
  font-size: 2rem; font-weight: 800;
  letter-spacing: -0.03em; line-height: 1.15; color: #fff;
  margin: 14px 0 16px;
  background: linear-gradient(135deg, #fff 0%, #BDEBB5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.k-console-desc {
  font-size: 0.88rem; color: rgba(189, 235, 181, 0.6);
  line-height: 1.75; max-width: 580px;
}

.k-console-center {
  width: 100%;
  max-width: 720px;
  opacity: 1;
  transform: translateY(0);
  transition: all 0.4s ease;
}

.k-pipeline { display: none; }
.k-pipe { display: none; }

/* Terminal card with glass effect */
.k-console-right {
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px) saturate(1.1);
  -webkit-backdrop-filter: blur(20px) saturate(1.1);
  box-shadow: 
    0 8px 32px rgba(0,0,0,0.4),
    inset 0 1px 0 rgba(255,255,255,0.06);
}

.k-term-header {
  background: rgba(0,0,0,0.6);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  padding: 16px 24px;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  backdrop-filter: blur(10px);
}
.k-term-dots { display: none; }
.k-term-title {
  font-family: 'Inter', 'Roboto', sans-serif; font-size: 0.92rem; font-weight: 700;
  color: #BDEBB5; letter-spacing: 0.05em;
}
.k-term-badge { display: none; }

.k-term-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; }

.k-term-section { display: flex; flex-direction: column; gap: 10px; }

.k-term-label {
  display: flex; align-items: center; gap: 10px;
  font-family: 'Inter', 'Roboto', sans-serif; font-size: 0.75rem;
  color: rgba(189, 235, 181, 0.8); font-weight: 600; letter-spacing: 0.06em;
}
.k-term-hint {
  margin-left: auto;
  color: rgba(168, 230, 161, 0.6);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Drop zone */
.k-dropzone {
  border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
  min-height: 100px; display: flex; align-items: center; justify-content: center;
  cursor: pointer; background: rgba(255,255,255,0.02);
  transition: all 0.2s ease;
  overflow-y: auto;
}
.k-dropzone.hover, .k-dropzone:hover {
  border-color: rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.05);
  box-shadow: inset 0 0 20px rgba(255,255,255,0.05);
}
.k-dropzone.filled { align-items: flex-start; padding: 10px; }

.k-drop-empty {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  color: rgba(255,255,255,0.35); font-size: 0.78rem;
}
.k-drop-icon {
  width: 32px; height: 32px;
  border: 1px solid rgba(255,255,255,0.12); border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.35);
}
.k-drop-files { display: flex; flex-direction: column; gap: 5px; width: 100%; }
.k-drop-file {
  display: flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px; padding: 6px 8px;
  font-size: 0.75rem;
}
.k-file-ext {
  font-family: var(--mono); font-size: 0.55rem; font-weight: 600;
  color: rgba(255,255,255,0.4); text-transform: uppercase;
  border: 1px solid rgba(255,255,255,0.1); padding: 0px 4px; border-radius: 2px;
}
.k-file-name { flex: 1; font-size: 0.75rem; color: rgba(255,255,255,0.6); }
.k-file-rm { background: none; border: none; color: rgba(255,255,255,0.25); font-size: 0.95rem; cursor: pointer; transition: color 0.15s; }
.k-file-rm:hover { color: rgba(255,100,100,0.7); }

/* Template pills */
.k-tpls { display: flex; gap: 2px; margin-left: auto; }
.k-tpl {
  font-family: var(--mono); font-size: 0.53rem; font-weight: 600;
  letter-spacing: 0.07em; padding: 3px 6px;
  border: 1px solid rgba(189, 235, 181, 0.2);
  background: transparent; color: rgba(189, 235, 181, 0.6);
  border-radius: 3px; cursor: pointer; transition: all 0.15s;
}
.k-tpl:hover { border-color: rgba(189, 235, 181, 0.4); color: rgba(189, 235, 181, 0.8); background: rgba(189, 235, 181, 0.05); }
.k-tpl.on { background: rgba(189, 235, 181, 0.15); color: #BDEBB5; border-color: rgba(189, 235, 181, 0.5); }

/* Textarea */
.k-textarea-wrap { position: relative; }
.k-textarea {
  width: 100%; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px;
  background: rgba(255,255,255,0.03); padding: 12px;
  font-family: var(--mono); font-size: 0.74rem; line-height: 1.6;
  color: rgba(255,255,255,0.85); resize: vertical; outline: none;
  transition: all 0.15s ease;
  caret-color: rgba(255,255,255,0.7);
}
.k-textarea:focus { border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.06); }
.k-textarea::placeholder { color: rgba(255,255,255,0.2); }
.k-textarea-ver {
  position: absolute; bottom: 8px; right: 10px;
  font-family: var(--mono); font-size: 0.54rem;
  color: rgba(189, 235, 181, 0.4); letter-spacing: 0.06em;
}

/* Launch button */
.k-launch {
  width: 100%;
  background: linear-gradient(135deg, rgba(189, 235, 181, 0.1) 0%, rgba(168, 230, 161, 0.05) 100%);
  color: rgba(255,255,255,0.9);
  border: 1px solid rgba(189, 235, 181, 0.3); padding: 12px 16px; border-radius: 6px;
  font-family: var(--mono); font-size: 0.75rem; font-weight: 600;
  letter-spacing: 0.04em;
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}
.k-launch::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(189, 235, 181, 0.1), transparent);
  transition: left 0.5s;
}
.k-launch:hover:not(:disabled)::before {
  left: 100%;
}
.k-launch:hover:not(:disabled) { 
  background: linear-gradient(135deg, rgba(189, 235, 181, 0.2) 0%, rgba(168, 230, 161, 0.1) 100%);
  transform: translateY(-1px);
  border-color: rgba(189, 235, 181, 0.5);
  box-shadow: 0 8px 16px rgba(189, 235, 181, 0.2);
}
.k-launch:disabled { background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.15); cursor: not-allowed; }
.k-launch-pre { color: rgba(189, 235, 181, 0.6); font-size: 0.9rem; }
.k-launch span:nth-child(2) { flex: 1; text-align: left; }
.k-launch svg { margin-left: auto; flex-shrink: 0; stroke: #BDEBB5; }
.k-launch:disabled .k-launch-pre { color: rgba(255,255,255,0.08); }
.k-launch:disabled svg { display: none; }

@media (max-width: 1100px) {
  .k-hero { grid-template-columns: 1fr; padding: 60px 40px; }
  .k-readout { display: none; }
  .k-uc-grid { grid-template-columns: repeat(1, 1fr); }
  .k-console { padding: 60px 40px; gap: 40px; }
  .k-console-center { max-width: 100%; }
  .k-title { font-size: 2.8rem; }
  .k-nav-center { display: none; }
}
</style>
