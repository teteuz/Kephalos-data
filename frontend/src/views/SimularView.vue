<template>
  <div class="sp">

    <NavBar />

    <!-- Main two-column layout -->
    <div class="sp-main">

      <!-- ── Left: Context panel ── -->
      <aside class="sp-left">
        <div class="sp-eyebrow">KEPHALOS DATA · MOTOR DE SIMULAÇÃO</div>

        <h1 class="sp-title">
          Configure seu<br>
          <span class="sp-title-dim">cenário de previsão.</span>
        </h1>

        <p class="sp-desc">
          Descreva o evento, contexto ou decisão que deseja simular. O motor extrai entidades, mapeia uma rede de atores e executa agentes autônomos por 72 horas simuladas em dois ambientes sociais paralelos.
        </p>

        <!-- Process Steps -->
        <div class="sp-steps">
          <div class="sp-step" v-for="(step, i) in processSteps" :key="i">
            <div class="sp-step-track">
              <div class="sp-step-circle">{{ String(i+1).padStart(2,'0') }}</div>
              <div v-if="i < processSteps.length - 1" class="sp-step-line"></div>
            </div>
            <div class="sp-step-body">
              <div class="sp-step-title">{{ step.title }}</div>
              <div class="sp-step-desc">{{ step.desc }}</div>
            </div>
          </div>
        </div>

        <!-- Real Stats -->
        <div class="sp-stats">
          <div class="sp-stat" v-for="s in simStats" :key="s.label">
            <div class="sp-stat-val">{{ s.value }}</div>
            <div class="sp-stat-lbl">{{ s.label }}</div>
          </div>
        </div>
      </aside>

      <!-- ── Right: Console ── -->
      <section class="sp-right">
        <div class="sp-terminal" :class="{ 'sp-terminal--focused': isFocused }">

          <!-- Terminal header bar -->
          <div class="sp-term-head">
            <div class="sp-dots">
              <span></span><span></span><span class="sp-dot-green"></span>
            </div>
            <span class="sp-term-title">KEPHALOS-DATA · MOTOR DE SIMULAÇÃO</span>
            <div class="sp-status-pill">
              <span class="sp-status-dot"></span>
              PRONTO
            </div>
          </div>

          <!-- Directive templates -->
          <div class="sp-templates">
            <span class="sp-tpl-label">Diretivas:</span>
            <button
              v-for="tpl in directiveTemplates"
              :key="tpl.id"
              class="sp-tpl"
              :class="{ 'sp-tpl--active': activeTpl === tpl.id }"
              @click="applyTemplate(tpl)"
            >{{ tpl.short }}</button>
          </div>

          <!-- Input area (drag-and-drop enabled) -->
          <div
            class="sp-input-area"
            @dragover.prevent="isDragOver = true"
            @dragleave.prevent="isDragOver = false"
            @drop.prevent="handleDrop"
            :class="{ 'sp-input-area--drag': isDragOver }"
          >
            <textarea
              v-model="query"
              class="sp-textarea"
              :placeholder="placeholder"
              rows="8"
              :disabled="loading"
              @focus="isFocused = true"
              @blur="isFocused = false"
              @keydown.enter.ctrl="canSubmit && !loading && startSimulation()"
            ></textarea>
          </div>

          <!-- Footer: attach + run -->
          <div class="sp-footer">
            <div class="sp-attach-zone">
              <input
                ref="fileInput"
                type="file"
                multiple
                accept=".pdf,.md,.txt"
                @change="handleFileSelect"
                style="display:none"
              />

              <div v-if="!files.length" class="sp-attach-row">
                <button class="sp-attach-btn" @click="$refs.fileInput.click()" :disabled="loading">
                  <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                  </svg>
                  Anexar documento
                </button>
                <span class="sp-attach-hint">PDF, MD, TXT — opcional</span>
              </div>

              <div v-else class="sp-files">
                <div v-for="(f, i) in files" :key="i" class="sp-file">
                  <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  <span>{{ f.name }}</span>
                  <button @click.stop="files.splice(i, 1)">×</button>
                </div>
                <button class="sp-add-more" @click="$refs.fileInput.click()">+ outro</button>
              </div>
            </div>

            <button class="sp-run" :disabled="!canSubmit || loading" @click="startSimulation">
              <span v-if="loading" class="sp-spinner"></span>
              <template v-else>
                <span>Iniciar Simulação</span>
                <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                  <line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/>
                </svg>
              </template>
            </button>
          </div>
        </div>

        <!-- Sub-hint -->
        <div class="sp-hint">Ctrl+Enter para iniciar · Documentos são opcionais · Cada execução simula 3 dias completos de interações sociais comprimidos em ~30 min</div>

        <!-- Recent simulations teaser (dashboard link) -->
        <div class="sp-history-cta">
          <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="8" cy="8" r="6"/><polyline points="8 5 8 8 10 9"/>
          </svg>
          <span>Ver simulações anteriores em</span>
          <router-link to="/dashboard" class="sp-history-link">Painel</router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const fileInput = ref(null)

const processSteps = [
  {
    title: 'Analisar documentos',
    desc: 'Extração de entidades, relações e contexto semântico'
  },
  {
    title: 'Mapear rede de entidades',
    desc: 'Ontologia de atores, relações e conexões semânticas'
  },
  {
    title: 'Gerar perfis de agentes',
    desc: 'Personas com memória, viés cognitivo e arquétipo social'
  },
  {
    title: 'Executar simulação dual-plataforma',
    desc: 'Info Plaza + Comunidade de Tópicos rodando em paralelo'
  },
  {
    title: 'Relatório de previsão',
    desc: 'Atribuição de influência, cascatas e narrativas emergentes'
  },
]

// Dados reais extraídos do código
const simStats = [
  { value: '2', label: 'plataformas\nem paralelo' },
  { value: '72h', label: '3 dias de vida\nsocial simulada' },
  { value: '~30min', label: 'para rodar os\n72h completos' },
]

const directiveTemplates = [
  {
    id: 'decision',
    short: 'DECISÃO',
    text: 'Dado este cenário, qual é a decisão ideal para maximizar resultados positivos e minimizar riscos? Simule como diferentes grupos de stakeholders reagem e identifique a estratégia com melhor relação risco-retorno.'
  },
  {
    id: 'narrative',
    short: 'NARRATIVA',
    text: 'Simule como narrativas e opinião pública evoluirão nas plataformas sociais nas próximas 72 horas. Qual informação se espalha mais rápido? Quais grupos amplificam ou amenizam a situação?'
  },
  {
    id: 'crisis',
    short: 'CRISE',
    text: 'Se esta crise escalar, simule as estratégias de resposta institucional e seus resultados. Qual abordagem melhor preserva a reputação e restaura a confiança dos stakeholders?'
  },
  {
    id: 'market',
    short: 'MERCADO',
    text: 'Simule como participantes do mercado — investidores, analistas, concorrentes, mídia — reagirão a este evento. Quais mudanças de narrativa emergem?'
  },
]

const activeTpl = ref(null)
const query = ref('')
const files = ref([])
const loading = ref(false)
const isDragOver = ref(false)
const isFocused = ref(false)

const placeholder =
  '// descreva o objetivo da simulação\n// ex: dado este cenário, qual é a decisão ideal para maximizar resultados e minimizar riscos?'

const canSubmit = computed(() => query.value.trim() !== '')

const applyTemplate = (tpl) => {
  activeTpl.value = tpl.id
  query.value = tpl.text
}

const handleFileSelect = (e) => { addFiles(Array.from(e.target.files)) }
const handleDrop = (e) => {
  isDragOver.value = false
  addFiles(Array.from(e.dataTransfer.files))
}
const addFiles = (f) => {
  files.value.push(...f.filter(x =>
    ['pdf', 'md', 'txt'].includes(x.name.split('.').pop().toLowerCase())
  ))
}

const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, query.value)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}
</script>

<style scoped>
/* ─── Base ─── */
.sp {
  min-height: 100vh;
  background:
    radial-gradient(ellipse 80% 60% at 10% 50%, var(--green-dim) 0%, transparent 55%),
    var(--bg);
  color: var(--text);
  font-family: var(--font);
  display: flex;
  flex-direction: column;
}


/* ─── Main layout ─── */
.sp-main {
  flex: 1;
  display: grid;
  grid-template-columns: 38% 62%;
  max-width: 1360px;
  margin: 0 auto;
  width: 100%;
}

/* ─── Left panel ─── */
.sp-left {
  padding: 60px 52px 52px 52px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.sp-eyebrow {
  font-size: 0.56rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--green-text);
}

.sp-title {
  font-size: 2.7rem;
  font-weight: 300;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin: 0;
  color: var(--text);
}
.sp-title-dim { color: var(--text3); }

.sp-desc {
  font-size: 0.72rem;
  color: var(--text2);
  line-height: 1.8;
  max-width: 360px;
  margin: 0;
}

/* ─── Steps ─── */
.sp-steps {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.sp-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.sp-step-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.sp-step-circle {
  width: 26px; height: 26px;
  border-radius: 50%;
  border: 1px solid var(--border2);
  background: var(--surface-1);
  display: flex; align-items: center; justify-content: center;
  font-size: 8px; font-weight: 700;
  color: var(--text3);
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.sp-step-line {
  width: 1px;
  height: 24px;
  background: linear-gradient(to bottom, var(--green-border), var(--border));
  margin: 3px 0;
}

.sp-step-body {
  padding: 3px 0 22px;
}
.sp-step-title {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 2px;
}
.sp-step-desc {
  font-size: 0.6rem;
  color: var(--text2);
  line-height: 1.55;
}

/* ─── Stats ─── */
.sp-stats {
  display: flex;
  gap: 0;
  border-top: 1px solid var(--border);
  padding-top: 24px;
}
.sp-stat {
  flex: 1;
  padding: 0 16px;
  border-right: 1px solid var(--border);
}
.sp-stat:first-child { padding-left: 0; }
.sp-stat:last-child { border-right: none; }
.sp-stat-val {
  display: block;
  font-size: 1.45rem;
  font-weight: 300;
  letter-spacing: -0.02em;
  color: var(--text);
  margin-bottom: 5px;
}
.sp-stat-lbl {
  font-size: 0.56rem;
  color: var(--text3);
  letter-spacing: 0.06em;
  line-height: 1.6;
  white-space: pre-line;
}

/* ─── Right panel ─── */
.sp-right {
  padding: 60px 52px 48px 60px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  justify-content: center;
}

/* ─── Terminal ─── */
.sp-terminal {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 14px;
  overflow: hidden;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.sp-terminal--focused {
  border-color: var(--green-border);
  box-shadow: 0 0 0 1px var(--green-dim), 0 24px 64px rgba(0,0,0,0.12);
}

/* Terminal header bar */
.sp-term-head {
  padding: 11px 18px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
}
.sp-dots { display: flex; gap: 5px; }
.sp-dots span {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--surface-3);
}
.sp-dot-green {
  background: var(--green) !important;
  box-shadow: 0 0 6px var(--green);
}
.sp-term-title {
  flex: 1;
  font-size: 0.57rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--text3);
}
.sp-status-pill {
  display: flex; align-items: center; gap: 5px;
  font-size: 0.54rem; font-weight: 700; letter-spacing: 0.1em;
  color: var(--green-text);
  background: var(--green-dim);
  border: 1px solid var(--green-border);
  padding: 2px 9px; border-radius: 20px;
}
.sp-status-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 5px var(--green);
  animation: sp-pulse 2.4s ease-in-out infinite;
}
@keyframes sp-pulse { 0%,100%{opacity:.8} 50%{opacity:.3} }

/* Templates */
.sp-templates {
  padding: 11px 18px 9px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.sp-tpl-label {
  font-size: 0.57rem;
  color: var(--text3);
  letter-spacing: 0.08em;
  font-weight: 600;
}
.sp-tpl {
  font-family: var(--mono);
  font-size: 0.56rem; font-weight: 600; letter-spacing: 0.05em;
  padding: 3px 10px;
  border: 1px solid var(--border2);
  background: transparent; color: var(--text3);
  border-radius: 20px; cursor: pointer; transition: all 0.15s;
}
.sp-tpl:hover { border-color: var(--text2); color: var(--text2); }
.sp-tpl--active {
  background: var(--green-dim);
  color: var(--green-text);
  border-color: var(--green-border);
}

/* Input area */
.sp-input-area { transition: background 0.15s; }
.sp-input-area--drag { background: var(--green-dim); }

.sp-textarea {
  width: 100%; border: none; background: transparent;
  padding: 20px 20px 14px;
  font-family: var(--mono);
  font-size: 0.82rem; line-height: 1.7;
  color: var(--text);
  resize: none; outline: none; caret-color: var(--green);
  box-sizing: border-box;
}
.sp-textarea::placeholder { color: var(--text3); }

/* Footer */
.sp-footer {
  padding: 10px 14px 14px 16px;
  border-top: 1px solid var(--border);
  display: flex; align-items: flex-end;
  justify-content: space-between; gap: 12px;
}
.sp-attach-zone { flex: 1; min-width: 0; }
.sp-attach-row { display: flex; align-items: center; gap: 10px; }
.sp-attach-btn {
  display: inline-flex; align-items: center; gap: 6px;
  background: transparent;
  border: 1px dashed var(--border2);
  border-radius: 5px; padding: 6px 12px;
  font-family: var(--mono); font-size: 0.62rem;
  color: var(--text3); cursor: pointer; transition: all 0.15s;
}
.sp-attach-btn:hover:not(:disabled) {
  border-color: var(--text2); color: var(--text2);
}
.sp-attach-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.sp-attach-hint { font-size: 0.57rem; color: var(--text3); }
.sp-files { display: flex; flex-wrap: wrap; gap: 5px; align-items: center; }
.sp-file {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--green-dim);
  border: 1px solid var(--green-border);
  border-radius: 4px; padding: 4px 8px;
  font-size: 0.62rem; color: var(--green-text);
  font-family: var(--mono);
}
.sp-file span { max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sp-file button {
  background: none; border: none;
  color: var(--text3); cursor: pointer;
  font-size: 0.85rem; line-height: 1; padding: 0 1px;
}
.sp-file button:hover { color: var(--red); }
.sp-add-more {
  background: transparent; border: 1px dashed var(--border);
  border-radius: 4px; padding: 3px 8px;
  font-family: var(--mono); font-size: 0.58rem;
  color: var(--text3); cursor: pointer;
}
.sp-add-more:hover { color: var(--text2); }

/* Run button */
.sp-run {
  display: inline-flex; align-items: center; gap: 8px;
  background: var(--green-bright); color: #000; border: none;
  border-radius: 8px; padding: 12px 26px;
  font-family: var(--mono); font-size: 0.75rem;
  font-weight: 700; letter-spacing: 0.04em;
  cursor: pointer; transition: opacity 0.15s, transform 0.1s;
  white-space: nowrap; flex-shrink: 0;
}
.sp-run:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.sp-run:disabled {
  background: var(--surface-2);
  color: var(--text3);
  cursor: not-allowed; transform: none;
}
.sp-spinner {
  display: inline-block; width: 13px; height: 13px;
  border: 2px solid rgba(0,0,0,0.2); border-top-color: #000;
  border-radius: 50%; animation: sp-spin 0.7s linear infinite;
}
@keyframes sp-spin { to { transform: rotate(360deg); } }

/* Sub-elements */
.sp-hint {
  font-size: 0.56rem;
  color: var(--text3);
  letter-spacing: 0.05em;
  padding: 0 4px;
}
.sp-history-cta {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.6rem; color: var(--text3);
  margin-top: 4px; padding: 0 4px;
}
.sp-history-link {
  color: var(--green-text);
  text-decoration: none;
  transition: color 0.15s;
}
.sp-history-link:hover { opacity: 0.75; }

/* ─── Responsive ─── */
@media (max-width: 1000px) {
  .sp-main { grid-template-columns: 1fr; }
  .sp-left {
    padding: 44px 32px 32px;
    border-right: none;
    border-bottom: 1px solid var(--border);
    gap: 22px;
  }
  .sp-right { padding: 40px 32px 48px; }
  .sp-title { font-size: 2rem; }
  .sp-steps { display: none; }
}

@media (max-width: 600px) {
  .sp-left, .sp-right { padding: 28px 20px 36px; }
  .sp-stats { flex-direction: column; gap: 16px; }
  .sp-stat { border-right: none; border-bottom: 1px solid var(--border); padding: 0 0 16px; }
  .sp-stat:last-child { border-bottom: none; }
}
</style>
