<template>
  <div class="sp">
    <NavBar />

    <div class="sp-main">

      <!-- Cabeçalho -->
      <div class="sp-header">
        <div class="sp-eyebrow">KEPHALOS</div>
        <h1 class="sp-title">
          Configure seu<br>
          <span class="sp-title-dim">cenário de previsão.</span>
        </h1>
        <p class="sp-desc">
          Descreva o evento, contexto ou decisão que deseja simular. O motor extrai entidades, mapeia uma rede de atores e executa agentes autônomos por 72 horas simuladas.
        </p>
      </div>

      <!-- Terminal -->
      <div class="sp-terminal" :class="{ 'sp-terminal--focused': isFocused }">

        <!-- Barra do terminal -->
        <div class="sp-term-head">
          <span class="sp-term-title">Como posso ajudar você hoje?</span>
        </div>

        <!-- Área de input principal -->
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
            rows="7"
            :disabled="loading"
            @focus="isFocused = true"
            @blur="isFocused = false"
            @keydown.enter.ctrl="canSubmit && !loading && startSimulation()"
          ></textarea>
        </div>

        <!-- Painel de configuração avançada (colapsável) -->
        <Transition name="config-slide">
          <div v-if="showConfig" class="sp-config">
            <div class="sp-config-inner">

              <!-- Campo de nome do cenário -->
              <div class="sp-cfg-row">
                <label class="sp-cfg-label">NOME DO CENÁRIO</label>
                <input
                  v-model="scenarioTitle"
                  class="sp-cfg-input"
                  placeholder="Ex: Abrir uma academia em São Paulo em 2026"
                />
              </div>

              <!-- Templates de cenário -->
              <div class="sp-cfg-row">
                <label class="sp-cfg-label">CENÁRIOS PRONTOS</label>
                <div class="sp-chips">
                  <button
                    v-for="sc in scenarioTemplates"
                    :key="sc.id"
                    class="sp-chip"
                    :class="{ 'sp-chip--active': activeScenario === sc.id }"
                    @click="applyScenario(sc)"
                  >{{ sc.short }}</button>
                </div>
              </div>

              <!-- Templates de diretiva -->
              <div class="sp-cfg-row">
                <label class="sp-cfg-label">DIRETIVA DE ANÁLISE</label>
                <div class="sp-chips">
                  <button
                    v-for="tpl in directiveTemplates"
                    :key="tpl.id"
                    class="sp-chip"
                    :class="{ 'sp-chip--active': activeTpl === tpl.id }"
                    @click="applyDirective(tpl)"
                  >{{ tpl.short }}</button>
                </div>
              </div>

            </div>
          </div>
        </Transition>

        <!-- Rodapé do terminal -->
        <div class="sp-footer">
          <div class="sp-footer-left">
            <input
              ref="fileInput"
              type="file"
              multiple
              accept=".pdf,.md,.txt"
              @change="handleFileSelect"
              style="display:none"
            />

            <!-- Sem arquivos: botão de anexar -->
            <div v-if="!files.length" class="sp-attach-row">
              <button class="sp-attach-btn" @click="$refs.fileInput.click()" :disabled="loading">
                <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                </svg>
                Anexar documento
              </button>
              <span class="sp-attach-hint">PDF, MD, TXT — opcional</span>
            </div>

            <!-- Com arquivos: lista -->
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

            <!-- Botão de configurar cenário -->
            <button
              class="sp-cfg-toggle"
              :class="{ 'sp-cfg-toggle--active': showConfig }"
              @click="showConfig = !showConfig"
              :disabled="loading"
            >
              <svg viewBox="0 0 16 16" width="11" height="11" fill="none" stroke="currentColor" stroke-width="1.8">
                <circle cx="8" cy="8" r="2.5"/>
                <path d="M8 1v2M8 13v2M1 8h2M13 8h2M3.2 3.2l1.4 1.4M11.4 11.4l1.4 1.4M11.4 3.2l-1.4 1.4M4.6 11.4l-1.4 1.4"/>
              </svg>
              Configurar cenário
              <svg class="sp-cfg-chevron" :class="{ open: showConfig }" viewBox="0 0 10 10" width="9" height="9" fill="none" stroke="currentColor" stroke-width="1.8">
                <polyline points="2 3.5 5 6.5 8 3.5"/>
              </svg>
            </button>
          </div>

          <button
            class="sp-run"
            :disabled="!canSubmit || loading"
            title="Ctrl+Enter para iniciar"
            @click="startSimulation"
          >
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

      <!-- Saiba mais -->
      <div class="sp-info">
        <button class="sp-info-toggle" @click="showInfo = !showInfo">
          <svg viewBox="0 0 16 16" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="8" cy="8" r="6"/>
            <line x1="8" y1="5" x2="8" y2="8"/>
            <line x1="8" y1="11" x2="8" y2="11.5" stroke-width="2.5"/>
          </svg>
          Saiba mais
          <svg class="sp-info-chevron" :class="{ open: showInfo }" viewBox="0 0 12 12" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="2 4 6 8 10 4"/>
          </svg>
        </button>

        <div v-show="showInfo" class="sp-info-body">
          <div class="sp-info-block">
            <div class="sp-info-label">Quando o PDF faz diferença:</div>
            <ul class="sp-info-list">
              <li>Quando você quer agentes baseados em <strong>pessoas ou organizações reais</strong> (relatório de mercado com nomes de analistas, concorrentes, investidores)</li>
              <li>Quando o cenário tem <strong>dados específicos que o LLM não conhece</strong> (empresa privada, mercado de nicho, evento interno)</li>
            </ul>
          </div>
          <div class="sp-info-block">
            <div class="sp-info-label">Quando só o texto já basta:</div>
            <ul class="sp-info-list">
              <li>Cenários genéricos — <em>"simule o impacto de um aumento de juros no mercado de startups"</em></li>
              <li>Conteúdo de campanha — <em>"simulei abrir uma academia em 2026 usando IA"</em></li>
              <li>Testes rápidos de hipóteses</li>
            </ul>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '../components/NavBar.vue'

const router = useRouter()
const fileInput = ref(null)

const scenarioTemplates = [
  {
    id: 'academia',
    short: 'Academia',
    title: 'Abrir uma academia em São Paulo em 2026',
    directive: 'Dado este cenário, qual é a decisão ideal para maximizar resultados e minimizar riscos? Simule como clientes potenciais, concorrentes e fornecedores reagem ao lançamento.'
  },
  {
    id: 'startup',
    short: 'Startup',
    title: 'Lançar um app de finanças pessoais para a Geração Z',
    directive: 'Simule como o mercado reage ao lançamento. Qual narrativa se consolida e quais grupos amplificam ou rejeitam o produto?'
  },
  {
    id: 'marca',
    short: 'Rebranding',
    title: 'Relançamento de marca de moda sustentável no Brasil',
    directive: 'Simule como a opinião pública reage ao reposicionamento. Quais grupos abraçam a narrativa de sustentabilidade e quais a questionam?'
  },
  {
    id: 'crise',
    short: 'Crise',
    title: 'Gestão de crise após recall de produto alimentício',
    directive: 'Simule as estratégias de resposta institucional e seus resultados. Qual abordagem melhor preserva a reputação e restaura a confiança dos consumidores?'
  },
]

const directiveTemplates = [
  {
    id: 'decision',
    short: 'Decisão',
    text: 'Dado este cenário, qual é a decisão ideal para maximizar resultados positivos e minimizar riscos? Simule como diferentes grupos de stakeholders reagem e identifique a estratégia com melhor relação risco-retorno.'
  },
  {
    id: 'narrative',
    short: 'Narrativa',
    text: 'Simule como narrativas e opinião pública evoluirão nas plataformas sociais nas próximas 72 horas. Qual informação se espalha mais rápido? Quais grupos amplificam ou amenizam a situação?'
  },
  {
    id: 'crisis',
    short: 'Crise',
    text: 'Se esta crise escalar, simule as estratégias de resposta institucional e seus resultados. Qual abordagem melhor preserva a reputação e restaura a confiança dos stakeholders?'
  },
  {
    id: 'market',
    short: 'Mercado',
    text: 'Simule como participantes do mercado — investidores, analistas, concorrentes, mídia — reagirão a este evento. Quais mudanças de narrativa emergem?'
  },
]

const query = ref('')
const scenarioTitle = ref('')
const files = ref([])
const loading = ref(false)
const isFocused = ref(false)
const isDragOver = ref(false)
const showInfo = ref(false)
const showConfig = ref(false)
const activeScenario = ref(null)
const activeTpl = ref(null)

const placeholder =
  'Descreva o evento, decisão ou contexto que deseja simular.\nEx: "Dado este cenário, qual é a estratégia ideal para o lançamento?"'

const canSubmit = computed(() => query.value.trim() !== '')

const applyScenario = (sc) => {
  activeScenario.value = sc.id
  activeTpl.value = null
  scenarioTitle.value = sc.title
  query.value = sc.directive
}

const applyDirective = (tpl) => {
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
    setPendingUpload(files.value, query.value, scenarioTitle.value)
    router.push({ name: 'Process', params: { projectId: 'new' } })
  })
}
</script>

<style scoped>
.sp {
  min-height: 100vh;
  background:
    radial-gradient(ellipse 60% 50% at 80% 20%, var(--green-dim) 0%, transparent 60%),
    var(--bg);
  color: var(--text);
  font-family: var(--font);
  display: flex;
  flex-direction: column;
}

.sp-main {
  flex: 1;
  max-width: 760px;
  margin: 0 auto;
  width: 100%;
  padding: 52px 28px 72px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

/* ── Cabeçalho ── */
.sp-header { display: flex; flex-direction: column; gap: 14px; }

.sp-eyebrow {
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--green-text, #BDEBB5);
}

.sp-title {
  font-size: clamp(2rem, 5vw, 2.8rem);
  font-weight: 300;
  line-height: 1.15;
  margin: 0;
  color: var(--text);
}

.sp-title-dim { color: var(--text2); }

.sp-desc {
  font-size: 0.85rem;
  color: var(--text2);
  line-height: 1.6;
  max-width: 480px;
  margin: 0;
}

/* ── Terminal ── */
.sp-terminal {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: border-color 0.15s;
}

.sp-terminal--focused { border-color: var(--green); }

.sp-term-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--bg2);
}

.sp-dots { display: flex; gap: 5px; }
.sp-dots span { width: 10px; height: 10px; border-radius: 50%; background: var(--border2); }
.sp-dot-green { background: var(--green) !important; }

.sp-term-title { flex: 1; font-size: 0.6rem; letter-spacing: 0.12em; color: var(--text3); }

.sp-status-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--green);
}

.sp-status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

/* ── Input principal ── */
.sp-input-area {
  padding: 4px 16px 4px;
  transition: background 0.12s;
}

.sp-input-area--drag { background: rgba(189, 235, 181, 0.04); }

.sp-textarea {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text);
  font-family: var(--font);
  font-size: 0.875rem;
  line-height: 1.65;
  resize: none;
  outline: none;
  box-sizing: border-box;
  padding: 10px 0;
}

.sp-textarea::placeholder { color: var(--text3); }

/* ── Painel de configuração ── */
.sp-config {
  border-top: 1px solid var(--border);
  background: var(--bg2);
  overflow: hidden;
}

.sp-config-inner {
  padding: 16px 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sp-cfg-row { display: flex; flex-direction: column; gap: 7px; }

.sp-cfg-label {
  font-size: 0.55rem;
  letter-spacing: 0.14em;
  color: var(--text3);
}

.sp-cfg-input {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--text);
  font-family: var(--font);
  font-size: 0.82rem;
  padding: 7px 10px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.12s;
}

.sp-cfg-input:focus { border-color: var(--green); }
.sp-cfg-input::placeholder { color: var(--text3); }

.sp-chips { display: flex; flex-wrap: wrap; gap: 7px; }

.sp-chip {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--font);
  font-size: 0.72rem;
  border-radius: 4px;
  padding: 4px 11px;
  cursor: pointer;
  transition: all 0.12s;
}

.sp-chip:hover { border-color: var(--green); color: var(--green); }
.sp-chip--active { border-color: var(--green); color: var(--green); background: rgba(189, 235, 181, 0.07); }

/* ── Transição do painel ── */
.config-slide-enter-active,
.config-slide-leave-active {
  transition: max-height 0.22s ease, opacity 0.18s ease;
  max-height: 300px;
}

.config-slide-enter-from,
.config-slide-leave-to {
  max-height: 0;
  opacity: 0;
}

/* ── Rodapé ── */
.sp-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-top: 1px solid var(--border);
  gap: 10px;
  flex-wrap: wrap;
}

.sp-footer-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.sp-attach-row { display: flex; align-items: center; gap: 8px; }

.sp-attach-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid var(--border2);
  color: var(--text2);
  font-family: var(--font);
  font-size: 0.72rem;
  border-radius: 4px;
  padding: 5px 11px;
  cursor: pointer;
  transition: all 0.12s;
}

.sp-attach-btn:hover { border-color: var(--green); color: var(--green); }

.sp-attach-hint { font-size: 0.68rem; color: var(--text3); }

.sp-files { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }

.sp-file {
  display: flex; align-items: center; gap: 5px;
  font-size: 0.72rem; color: var(--text2);
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 4px; padding: 3px 8px;
}

.sp-file button {
  background: none; border: none; color: var(--text3);
  cursor: pointer; font-size: 0.9rem; line-height: 1; padding: 0 0 0 2px;
}

.sp-add-more {
  background: none; border: 1px dashed var(--border2);
  color: var(--text3); font-family: var(--font);
  font-size: 0.72rem; border-radius: 4px; padding: 3px 8px; cursor: pointer;
}

/* ── Botão Configurar Cenário ── */
.sp-cfg-toggle {
  display: flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  border: 1px solid var(--border2);
  color: var(--text3);
  font-family: var(--font);
  font-size: 0.7rem;
  border-radius: 4px;
  padding: 5px 11px;
  cursor: pointer;
  transition: all 0.12s;
  white-space: nowrap;
}

.sp-cfg-toggle:hover { border-color: var(--border); color: var(--text2); }
.sp-cfg-toggle--active { border-color: var(--green); color: var(--green); }

.sp-cfg-chevron {
  transition: transform 0.18s ease;
}

.sp-cfg-chevron.open { transform: rotate(180deg); }

/* ── Botão principal ── */
.sp-run {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--green);
  color: #000;
  border: none;
  border-radius: 6px;
  padding: 9px 20px;
  font-family: var(--font);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
  transition: opacity 0.12s, transform 0.12s;
}

.sp-run:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.sp-run:disabled { opacity: 0.35; cursor: not-allowed; }

.sp-spinner {
  width: 13px; height: 13px;
  border: 2px solid rgba(0,0,0,0.25);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ── Saiba mais ── */
.sp-info { display: flex; flex-direction: column; }

.sp-info-toggle {
  display: flex;
  align-items: center;
  gap: 7px;
  background: none;
  border: none;
  color: var(--text3);
  font-family: var(--font);
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.12s;
}

.sp-info-toggle:hover { color: var(--text2); }

.sp-info-chevron { transition: transform 0.18s ease; }
.sp-info-chevron.open { transform: rotate(180deg); }

.sp-info-body {
  margin-top: 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 18px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sp-info-block { display: flex; flex-direction: column; gap: 8px; }

.sp-info-label {
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  color: var(--text3);
}

.sp-info-list {
  padding-left: 16px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sp-info-list li { font-size: 0.8rem; color: var(--text2); line-height: 1.5; }
.sp-info-list li strong { color: var(--text); font-weight: 500; }
.sp-info-list li em { color: var(--text2); font-style: italic; }

@media (max-width: 560px) {
  .sp-footer { flex-direction: column; align-items: stretch; }
  .sp-run { justify-content: center; }
}
</style>
