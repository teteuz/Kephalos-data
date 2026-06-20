<template>
  <div class="simulation-panel">
    <!-- Top Control Bar -->
    <div class="control-bar">
      <div class="status-group">
        <!-- Twitter Platform Progress -->
        <div class="platform-status twitter" :class="{ active: runStatus.twitter_running, completed: runStatus.twitter_completed }">
          <div class="platform-header">
            <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
            </svg>
            <span class="platform-name">Info Plaza</span>
            <span v-if="runStatus.twitter_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">RODADA</span>
              <span class="stat-value mono">{{ runStatus.twitter_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">Tempo</span>
              <span class="stat-value mono">{{ twitterElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">AÇÕES</span>
              <span class="stat-value mono">{{ runStatus.twitter_actions_count || 0 }}</span>
            </span>
          </div>
          <!-- Available action hints -->
          <div class="actions-tooltip">
            <div class="tooltip-title">Ações Disponíveis</div>
            <div class="tooltip-actions">
              <span class="tooltip-action">POST</span>
              <span class="tooltip-action">LIKE</span>
              <span class="tooltip-action">REPOST</span>
              <span class="tooltip-action">QUOTE</span>
              <span class="tooltip-action">FOLLOW</span>
              <span class="tooltip-action">IDLE</span>
            </div>
          </div>
        </div>

        <!-- Reddit Platform Progress -->
        <div class="platform-status reddit" :class="{ active: runStatus.reddit_running, completed: runStatus.reddit_completed }">
          <div class="platform-header">
            <svg class="platform-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
            <span class="platform-name">Topic Community</span>
            <span v-if="runStatus.reddit_completed" class="status-badge">
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </span>
          </div>
          <div class="platform-stats">
            <span class="stat">
              <span class="stat-label">RODADA</span>
              <span class="stat-value mono">{{ runStatus.reddit_current_round || 0 }}<span class="stat-total">/{{ runStatus.total_rounds || maxRounds || '-' }}</span></span>
            </span>
            <span class="stat">
              <span class="stat-label">Tempo</span>
              <span class="stat-value mono">{{ redditElapsedTime }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">AÇÕES</span>
              <span class="stat-value mono">{{ runStatus.reddit_actions_count || 0 }}</span>
            </span>
          </div>
          <!-- Available action hints -->
          <div class="actions-tooltip">
            <div class="tooltip-title">Ações Disponíveis</div>
            <div class="tooltip-actions">
              <span class="tooltip-action">POST</span>
              <span class="tooltip-action">COMMENT</span>
              <span class="tooltip-action">LIKE</span>
              <span class="tooltip-action">DISLIKE</span>
              <span class="tooltip-action">SEARCH</span>
              <span class="tooltip-action">TREND</span>
              <span class="tooltip-action">FOLLOW</span>
              <span class="tooltip-action">MUTE</span>
              <span class="tooltip-action">REFRESH</span>
              <span class="tooltip-action">IDLE</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action distribution mini-chart -->
      <div class="action-dist" v-if="allActions.length > 0">
        <div class="dist-label">ATIVIDADE</div>
        <div class="dist-bars">
          <div
            v-for="seg in actionDistribution"
            :key="seg.type"
            class="dist-bar"
            :style="{ width: seg.pct + '%', background: seg.color }"
            :title="seg.type + ': ' + seg.count"
          ></div>
        </div>
        <div class="dist-counts">
          <span v-for="seg in actionDistribution" :key="seg.type" class="dist-count-item" :style="{ color: seg.color }">
            {{ seg.shortLabel }} {{ seg.count }}
          </span>
        </div>
      </div>

      <div class="action-controls">
        <button
          class="action-btn primary"
          :disabled="phase !== 2 || isGeneratingReport"
          @click="handleNextStep"
        >
          <span v-if="isGeneratingReport" class="loading-spinner-small"></span>
          {{ isGeneratingReport ? 'Gerando...' : 'Gerar relatório' }}
          <span v-if="!isGeneratingReport" class="arrow-icon">→</span>
        </button>
      </div>
    </div>

    <!-- Cascade Alert Toasts -->
    <div class="cascade-toasts">
      <TransitionGroup name="cascade-toast">
        <div
          v-for="toast in cascadeToasts"
          :key="toast.id"
          class="cascade-toast"
          @click="dismissToast(toast.id)"
        >
          <div class="toast-icon">⚡</div>
          <div class="toast-body">
            <div class="toast-title">CASCADE DETECTED</div>
            <div class="toast-msg">{{ toast.message }}</div>
          </div>
          <div class="toast-spread">{{ toast.spread }}</div>
        </div>
      </TransitionGroup>
    </div>

    <!-- Main Content: Dual Timeline -->
    <div class="main-content-area" ref="scrollContainer">
      <!-- Timeline Header -->
      <div class="timeline-header" v-if="allActions.length > 0">
        <div class="timeline-stats">
          <span class="total-count">TOTAL DE EVENTOS: <span class="mono">{{ allActions.length }}</span></span>
          <span class="platform-breakdown">
            <span class="breakdown-item twitter">
              <svg class="mini-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
              <span class="mono">{{ twitterActionsCount }}</span>
            </span>
            <span class="breakdown-divider">/</span>
            <span class="breakdown-item reddit">
              <svg class="mini-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
              <span class="mono">{{ redditActionsCount }}</span>
            </span>
          </span>
        </div>
        <div class="timeline-filters">
          <input
            v-model="agentSearch"
            class="agent-search"
            placeholder="Filtrar por agente..."
            @input="filterChanged"
          />
          <div class="round-filter" v-if="maxRoundInActions > 0">
            <span class="round-filter-label">R{{ roundFilter[0] }}–{{ roundFilter[1] }}</span>
            <input type="range" :min="1" :max="maxRoundInActions" v-model.number="roundFilter[1]" class="round-slider" />
          </div>
        </div>
      </div>

      <!-- Chat Feed -->
      <div class="chat-feed">
        <TransitionGroup name="chat-msg">
          <div
            v-for="action in chronologicalActions"
            :key="action._uniqueId || action.id || `${action.timestamp}-${action.agent_id}`"
            class="chat-msg"
            :class="action.platform"
          >
            <!-- Avatar -->
            <div class="chat-avatar" :class="action.platform">
              {{ (action.agent_name || 'A')[0].toUpperCase() }}
            </div>

            <div class="chat-bubble">
              <!-- Bubble header -->
              <div class="chat-bubble-header">
                <span class="chat-agent-name">{{ action.agent_name }}</span>
                <span class="chat-action-badge" :class="getActionTypeClass(action.action_type)">
                  {{ getActionTypeLabel(action.action_type) }}
                </span>
                <span class="chat-platform-icon">
                  <svg v-if="action.platform === 'twitter'" viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                  <svg v-else viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                </span>
                <span class="chat-time">R{{ action.round_num }} · {{ formatActionTime(action.timestamp) }}</span>
              </div>

            <div class="chat-bubble-body">
              
              <div class="card-body">
                <!-- CREATE_POST: Create post -->
                <div v-if="action.action_type === 'CREATE_POST' && action.action_args?.content" class="content-text main-text">
                  {{ action.action_args.content }}
                </div>

                <!-- QUOTE_POST: Quote post -->
                <template v-if="action.action_type === 'QUOTE_POST'">
                  <div v-if="action.action_args?.quote_content" class="content-text">
                    {{ action.action_args.quote_content }}
                  </div>
                  <div v-if="action.action_args?.original_content" class="quoted-block">
                    <div class="quote-header">
                      <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                      <span class="quote-label">@{{ action.action_args.original_author_name || 'User' }}</span>
                    </div>
                    <div class="quote-text">
                      {{ truncateContent(action.action_args.original_content, 150) }}
                    </div>
                  </div>
                </template>

                <!-- REPOST: Repost -->
                <template v-if="action.action_type === 'REPOST'">
                  <div class="repost-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
                    <span class="repost-label">Repostado de @{{ action.action_args?.original_author_name || 'User' }}</span>
                  </div>
                  <div v-if="action.action_args?.original_content" class="repost-content">
                    {{ truncateContent(action.action_args.original_content, 200) }}
                  </div>
                </template>

                <!-- LIKE_POST: Like post -->
                <template v-if="action.action_type === 'LIKE_POST'">
                  <div class="like-info">
                    <svg class="icon-small filled" viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                    <span class="like-label">Curtiu post de @{{ action.action_args?.post_author_name || 'User' }}</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="liked-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

                <!-- CREATE_COMMENT: Create comment -->
                <template v-if="action.action_type === 'CREATE_COMMENT'">
                  <div v-if="action.action_args?.content" class="content-text">
                    {{ action.action_args.content }}
                  </div>
                  <div v-if="action.action_args?.post_id" class="comment-context">
                    <svg class="icon-small" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>
                    <span>Resposta ao post #{{ action.action_args.post_id }}</span>
                  </div>
                </template>

                <!-- SEARCH_POSTS: Search posts -->
                <template v-if="action.action_type === 'SEARCH_POSTS'">
                  <div class="search-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span class="search-label">Busca:</span>
                    <span class="search-query">"{{ action.action_args?.query || '' }}"</span>
                  </div>
                </template>

                <!-- FOLLOW: Follow user -->
                <template v-if="action.action_type === 'FOLLOW'">
                  <div class="follow-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>
                    <span class="follow-label">Seguiu @{{ action.action_args?.target_user || action.action_args?.user_id || 'User' }}</span>
                  </div>
                </template>

                <!-- UPVOTE / DOWNVOTE -->
                <template v-if="action.action_type === 'UPVOTE_POST' || action.action_type === 'DOWNVOTE_POST'">
                  <div class="vote-info">
                    <svg v-if="action.action_type === 'UPVOTE_POST'" class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"></polyline></svg>
                    <svg v-else class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    <span class="vote-label">{{ action.action_type === 'UPVOTE_POST' ? 'Votou positivo em' : 'Votou negativo em' }} Post</span>
                  </div>
                  <div v-if="action.action_args?.post_content" class="voted-content">
                    "{{ truncateContent(action.action_args.post_content, 120) }}"
                  </div>
                </template>

 <!-- DO_NOTHING: None（） -->
                <template v-if="action.action_type === 'DO_NOTHING'">
                  <div class="idle-info">
                    <svg class="icon-small" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span class="idle-label">Ação Ignorada</span>
                  </div>
                </template>

 <!-- ： content -->
                <div v-if="!['CREATE_POST', 'QUOTE_POST', 'REPOST', 'LIKE_POST', 'CREATE_COMMENT', 'SEARCH_POSTS', 'FOLLOW', 'UPVOTE_POST', 'DOWNVOTE_POST', 'DO_NOTHING'].includes(action.action_type) && action.action_args?.content" class="content-text">
                  {{ action.action_args.content }}
                </div>
              </div>

            </div><!-- /chat-bubble-body -->
            </div><!-- /chat-bubble -->
          </div><!-- /chat-msg -->
        </TransitionGroup>

        <div v-if="startError && allActions.length === 0" class="chat-error">
          <svg viewBox="0 0 16 16" width="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="8" cy="8" r="7"/><line x1="8" y1="5" x2="8" y2="8"/><line x1="8" y1="11" x2="8" y2="11"/></svg>
          <span>{{ startError }}</span>
        </div>
        <div v-else-if="allActions.length === 0" class="chat-waiting">
          <div class="pulse-ring"></div>
          <span>Aguardando ações dos agentes...</span>
        </div>
      </div><!-- /chat-feed -->
    </div><!-- /main-content-area -->

    <!-- Chat input bar (inject event) -->
    <div class="chat-input-bar" v-if="phase === 1">
      <input
        v-model="injectText"
        class="chat-input"
        placeholder="Inserir evento na simulação..."
        @keyup.enter="doInject"
      />
      <button class="chat-send-btn" @click="doInject" :disabled="!injectText.trim()">
        <svg viewBox="0 0 16 16" width="14" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="8" x2="13" y2="8"/><polyline points="9 4 13 8 9 12"/></svg>
      </button>
    </div>

    <!-- Bottom Info / Logs -->
    <div class="system-logs">
      <div class="log-header">
        <span class="log-title">MONITOR DE SIMULAÇÃO</span>
        <span class="log-id">{{ simulationId || 'NO_SIMULATION' }}</span>
      </div>
      <div class="log-content" ref="logContent">
        <div class="log-line" v-for="(log, idx) in systemLogs" :key="idx">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  startSimulation,
  stopSimulation,
  getRunStatus,
  getRunStatusDetail,
  injectSimulationEvent
} from '../api/simulation'
import { generateReport } from '../api/report'

const props = defineProps({
  simulationId: String,
 maxRounds: Number, // Step2
  minutesPerRound: {
    type: Number,
 default: 30 // 30minutes
  },
  projectData: Object,
  graphData: Object,
  systemLogs: Array
})

const emit = defineEmits(['go-back', 'next-step', 'add-log', 'update-status'])

const router = useRouter()

// State
const isGeneratingReport = ref(false)
const phase = ref(0) // 0: Not started, 1: , 2: Completed
const isStarting = ref(false)
const isStopping = ref(false)
const startError = ref(null)
const runStatus = ref({})
const allActions = ref([]) // （）
const actionIds = ref(new Set()) // ID
const scrollContainer = ref(null)

// Cascade toasts
const cascadeToasts = ref([])
let toastCounter = 0
const prevCascadeCount = ref(0)

const dismissToast = (id) => {
  cascadeToasts.value = cascadeToasts.value.filter(t => t.id !== id)
}

const addCascadeToast = (msg, spread) => {
  const id = ++toastCounter
  cascadeToasts.value.push({ id, message: msg, spread: `×${spread}` })
  setTimeout(() => dismissToast(id), 6000)
}

// Agent search + round filter
const agentSearch = ref('')
const roundFilter = ref([1, 9999])
const maxRoundInActions = computed(() =>
  allActions.value.reduce((m, a) => Math.max(m, a.round_num || 0), 0)
)
const filterChanged = () => {}

// Variable injection
const showInjectInput = ref(false)
const injectText = ref('')
const injectInputRef = ref(null)
const openInjectInput = () => {
  showInjectInput.value = true
  nextTick(() => injectInputRef.value?.focus())
}
const doInject = async () => {
  if (!injectText.value.trim() || !props.simulationId) return
  const headline = injectText.value.trim()
  addLog(`[INJECT] ${headline}`)
  injectText.value = ''
  showInjectInput.value = false
  try {
    const res = await injectSimulationEvent(props.simulationId, headline, 'both')
    if (res.success) {
      addCascadeToast(`Event injected: "${headline.substring(0, 55)}${headline.length > 55 ? '...' : ''}"`, '!')
      addLog(`✓ Event injected into ${res.data?.platforms_written?.join('+') || 'platforms'}`)
    } else {
      addLog(`✗ Inject failed: ${res.error || 'unknown'}`)
    }
  } catch (err) {
    addLog(`✗ Inject error: ${err.message}`)
  }
}

// Computed
// （，）
const chronologicalActions = computed(() => {
  let result = allActions.value
  if (agentSearch.value.trim()) {
    const q = agentSearch.value.toLowerCase()
    result = result.filter(a => (a.agent_name || '').toLowerCase().includes(q))
  }
  const maxR = roundFilter.value[1]
  if (maxR < 9999) {
    result = result.filter(a => (a.round_num || 0) <= maxR)
  }
  return result
})

// 
const twitterActionsCount = computed(() => {
  return allActions.value.filter(a => a.platform === 'twitter').length
})

const redditActionsCount = computed(() => {
  return allActions.value.filter(a => a.platform === 'reddit').length
})

const ACTION_DIST_CONFIG = [
  { type: 'CREATE_POST', shortLabel: 'POST', color: '#BDEBB5' },
  { type: 'REPOST',      shortLabel: 'RPT',  color: 'rgba(255,255,255,0.5)' },
  { type: 'QUOTE_POST',  shortLabel: 'QT',   color: 'rgba(189,235,181,0.5)' },
  { type: 'LIKE_POST',   shortLabel: 'LIKE', color: 'rgba(255,255,255,0.25)' },
  { type: 'CREATE_COMMENT', shortLabel: 'CMT', color: 'rgba(189,235,181,0.35)' },
  { type: 'DO_NOTHING',  shortLabel: 'IDLE', color: 'rgba(255,255,255,0.1)' },
]

const actionDistribution = computed(() => {
  const total = allActions.value.length || 1
  const counts = {}
  allActions.value.forEach(a => { counts[a.action_type] = (counts[a.action_type] || 0) + 1 })
  return ACTION_DIST_CONFIG
    .map(cfg => ({ ...cfg, count: counts[cfg.type] || 0, pct: Math.max(1, ((counts[cfg.type] || 0) / total) * 100) }))
    .filter(s => s.count > 0)
})

// （minutes）
const formatElapsedTime = (currentRound) => {
  if (!currentRound || currentRound <= 0) return '0h 0m'
  const totalMinutes = currentRound * props.minutesPerRound
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60
  return `${hours}h ${minutes}m`
}

// Twitter
const twitterElapsedTime = computed(() => {
  return formatElapsedTime(runStatus.value.twitter_current_round || 0)
})

// Reddit
const redditElapsedTime = computed(() => {
  return formatElapsedTime(runStatus.value.reddit_current_round || 0)
})

// Methods
const addLog = (msg) => {
  emit('add-log', msg)
}

// （）
const resetAllState = () => {
  phase.value = 0
  runStatus.value = {}
  allActions.value = []
  actionIds.value = new Set()
  prevTwitterRound.value = 0
  prevRedditRound.value = 0
  startError.value = null
  isStarting.value = false
  isStopping.value = false
 stopPolling() // 
}

// 
const doStartSimulation = async () => {
  if (!props.simulationId) {
    addLog('Error: missing simulationId')
    return
  }
  
 // ，
  resetAllState()
  
  isStarting.value = true
  startError.value = null
  addLog('Starting dual-platform parallel simulation...')
  emit('update-status', 'processing')
  
  try {
    const params = {
      simulation_id: props.simulationId,
      platform: 'parallel',
 force: true, // 
 enable_graph_memory_update: true // 
    }
    
    if (props.maxRounds) {
      params.max_rounds = props.maxRounds
      addLog(`Set max simulation rounds: ${props.maxRounds}`)
    }
    
    addLog('Dynamic graph update mode enabled')
    
    const res = await startSimulation(params)
    
    if (res.success && res.data) {
      if (res.data.force_restarted) {
 addLog('✓ ，Start Simulation')
      }
      addLog('✓ Simulation engine started successfully')
      addLog(`  ├─ PID: ${res.data.process_pid || '-'}`)
      
      phase.value = 1
      runStatus.value = res.data
      
      startStatusPolling()
      startDetailPolling()
    } else {
      startError.value = res.error || 'Start failed'
 addLog(`✗ Start failed: ${res.error || ''}`)
      emit('update-status', 'error')
    }
  } catch (err) {
    startError.value = err.message
    addLog(`✗ Start exception: ${err.message}`)
    emit('update-status', 'error')
  } finally {
    isStarting.value = false
  }
}

// 
const handleStopSimulation = async () => {
  if (!props.simulationId) return
  
  isStopping.value = true
  addLog('Stopping simulation...')
  
  try {
    const res = await stopSimulation({ simulation_id: props.simulationId })
    
    if (res.success) {
      addLog('✓ Simulation stopped')
      phase.value = 2
      stopPolling()
      emit('update-status', 'completed')
    } else {
 addLog(`Stop failed: ${res.error || ''}`)
    }
  } catch (err) {
    addLog(`Stop exception: ${err.message}`)
  } finally {
    isStopping.value = false
  }
}

// 
let statusTimer = null
let detailTimer = null

const startStatusPolling = () => {
  statusTimer = setInterval(fetchRunStatus, 2000)
}

const startDetailPolling = () => {
  detailTimer = setInterval(fetchRunStatusDetail, 3000)
}

const stopPolling = () => {
  if (statusTimer) {
    clearInterval(statusTimer)
    statusTimer = null
  }
  if (detailTimer) {
    clearInterval(detailTimer)
    detailTimer = null
  }
}

// ，
const prevTwitterRound = ref(0)
const prevRedditRound = ref(0)

const fetchRunStatus = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getRunStatus(props.simulationId)
    
    if (res.success && res.data) {
      const data = res.data
      
      runStatus.value = data
      
 // 
      if (data.twitter_current_round > prevTwitterRound.value) {
        addLog(`[Plaza] R${data.twitter_current_round}/${data.total_rounds} | T:${data.twitter_simulated_hours || 0}h | A:${data.twitter_actions_count}`)
        prevTwitterRound.value = data.twitter_current_round
      }
      
      if (data.reddit_current_round > prevRedditRound.value) {
        addLog(`[Community] R${data.reddit_current_round}/${data.total_rounds} | T:${data.reddit_simulated_hours || 0}h | A:${data.reddit_actions_count}`)
        prevRedditRound.value = data.reddit_current_round
      }

      // Cascade detection from action spread
      const totalActions = data.twitter_actions_count + data.reddit_actions_count
      if (totalActions > prevCascadeCount.value + 50) {
        prevCascadeCount.value = totalActions
      }

 // Completed（ runner_status ）
      const isCompleted = data.runner_status === 'completed' || data.runner_status === 'stopped'
      const isFailed = data.runner_status === 'failed'

      if (isFailed) {
        const errMsg = data.error || 'Processo de simulação encerrou com erro'
        addLog(`✗ Simulation failed: ${errMsg}`)
        startError.value = errMsg
        stopPolling()
        emit('update-status', 'error')
        return
      }

      const platformsCompleted = checkPlatformsCompleted(data)

      if (isCompleted || platformsCompleted) {
        if (platformsCompleted && !isCompleted) {
          addLog('✓ Detected all platform simulations have ended')
        }
        addLog('✓ Simulation completed')
        phase.value = 2
        stopPolling()
        emit('update-status', 'completed')
      }
    }
  } catch (err) {
    console.warn('Failed to fetch run status:', err)
  }
}

// Completed
const checkPlatformsCompleted = (data) => {
 // ， false
  if (!data) return false
  
 // 
  const twitterCompleted = data.twitter_completed === true
  const redditCompleted = data.reddit_completed === true
  
 // items，
 // actions_count （ count > 0 running true）
  const twitterEnabled = (data.twitter_actions_count > 0) || data.twitter_running || twitterCompleted
  const redditEnabled = (data.reddit_actions_count > 0) || data.reddit_running || redditCompleted
  
 // ， false
  if (!twitterEnabled && !redditEnabled) return false
  
 // Completed
  if (twitterEnabled && !twitterCompleted) return false
  if (redditEnabled && !redditCompleted) return false
  
  return true
}

const fetchRunStatusDetail = async () => {
  if (!props.simulationId) return
  
  try {
    const res = await getRunStatusDetail(props.simulationId)
    
    if (res.success && res.data) {
 // all_actions 
      const serverActions = res.data.all_actions || []
      
 // （）
      let newActionsAdded = 0
      serverActions.forEach(action => {
 // ID
        const actionId = action.id || `${action.timestamp}-${action.platform}-${action.agent_id}-${action.action_type}`
        
        if (!actionIds.value.has(actionId)) {
          actionIds.value.add(actionId)
          allActions.value.push({
            ...action,
            _uniqueId: actionId
          })
          newActionsAdded++
        }
      })
      
 // ，
 // 
    }
  } catch (err) {
 console.warn(':', err)
  }
}

// Helpers
const getActionTypeLabel = (type) => {
  const labels = {
    'CREATE_POST': 'POST',
    'REPOST': 'REPOST',
    'LIKE_POST': 'LIKE',
    'CREATE_COMMENT': 'COMMENT',
    'LIKE_COMMENT': 'LIKE',
    'DO_NOTHING': 'IDLE',
    'FOLLOW': 'FOLLOW',
    'SEARCH_POSTS': 'SEARCH',
    'QUOTE_POST': 'QUOTE',
    'UPVOTE_POST': 'UPVOTE',
    'DOWNVOTE_POST': 'DOWNVOTE'
  }
  return labels[type] || type || 'UNKNOWN'
}

const getActionTypeClass = (type) => {
  const classes = {
    'CREATE_POST': 'badge-post',
    'REPOST': 'badge-action',
    'LIKE_POST': 'badge-action',
    'CREATE_COMMENT': 'badge-comment',
    'LIKE_COMMENT': 'badge-action',
    'QUOTE_POST': 'badge-post',
    'FOLLOW': 'badge-meta',
    'SEARCH_POSTS': 'badge-meta',
    'UPVOTE_POST': 'badge-action',
    'DOWNVOTE_POST': 'badge-action',
    'DO_NOTHING': 'badge-idle'
  }
  return classes[type] || 'badge-default'
}

const truncateContent = (content, maxLength = 100) => {
  if (!content) return ''
  if (content.length > maxLength) return content.substring(0, maxLength) + '...'
  return content
}

const formatActionTime = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const handleNextStep = async () => {
  if (!props.simulationId) {
    addLog('Error: missing simulationId')
    return
  }
  
  if (isGeneratingReport.value) {
    addLog('Report generation request sent. Please wait...')
    return
  }
  
  isGeneratingReport.value = true
  addLog('Starting report generation...')
  
  try {
    const res = await generateReport({
      simulation_id: props.simulationId,
      force_regenerate: true
    })
    
    if (res.success && res.data) {
      const reportId = res.data.report_id
      addLog(`✓ Report generation task started: ${reportId}`)
      
 // 
      router.push({ name: 'Report', params: { reportId } })
    } else {
 addLog(`✗ Failed to start report generation: ${res.error || ''}`)
      isGeneratingReport.value = false
    }
  } catch (err) {
    addLog(`✗ Report generation start exception: ${err.message}`)
    isGeneratingReport.value = false
  }
}

// Scroll log to bottom
const logContent = ref(null)
watch(() => props.systemLogs?.length, () => {
  nextTick(() => {
    if (logContent.value) {
      logContent.value.scrollTop = logContent.value.scrollHeight
    }
  })
})

onMounted(() => {
 addLog('Step3 Initializing')
  if (props.simulationId) {
    doStartSimulation()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.simulation-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
  font-family: 'Roboto Mono', 'JetBrains Mono', monospace;
  overflow: hidden;
}

/* --- Control Bar --- */
.control-bar {
  background: var(--bg2);
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
  gap: 12px;
}

.status-group {
  display: flex;
  gap: 10px;
}

/* Platform Status Cards */
.platform-status {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 14px;
  border-radius: 8px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  opacity: 0.6;
  transition: all 0.25s;
  min-width: 150px;
  position: relative;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.platform-status.active {
  opacity: 1;
  border-color: rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.04);
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.platform-status.completed {
  opacity: 1;
  border-color: rgba(189,235,181,0.25);
  background: rgba(189,235,181,0.04);
}

/* Actions Tooltip */
.actions-tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  padding: 10px 14px;
  background: rgba(20,20,20,0.97);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6);
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 100;
  min-width: 190px;
  pointer-events: none;
  backdrop-filter: blur(10px);
}
.actions-tooltip::before {
  content: '';
  position: absolute;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-bottom: 5px solid rgba(255,255,255,0.1);
}
.platform-status:hover .actions-tooltip {
  opacity: 1;
  visibility: visible;
}
.tooltip-title {
  font-size: 9px;
  font-weight: 700;
  color: rgba(255,255,255,0.25);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 8px;
}
.tooltip-actions { display: flex; flex-wrap: wrap; gap: 5px; }
.tooltip-action {
  font-size: 9px;
  font-weight: 600;
  padding: 2px 7px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 3px;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.04em;
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 3px;
}
.platform-name {
  font-size: 10px;
  font-weight: 700;
  color: rgba(255,255,255,0.7);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.platform-status.twitter .platform-icon { color: rgba(255,255,255,0.5); }
.platform-status.reddit .platform-icon { color: rgba(255,255,255,0.5); }
.platform-status.completed .platform-name { color: #BDEBB5; }

.platform-stats { display: flex; gap: 12px; }
.stat { display: flex; align-items: baseline; gap: 4px; }
.stat-label {
  font-size: 7px;
  color: rgba(255,255,255,0.2);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.stat-value {
  font-size: 11px;
  font-weight: 600;
  color: rgba(255,255,255,0.8);
}
.stat-total, .stat-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.25);
  font-weight: 400;
}
.status-badge {
  margin-left: auto;
  color: #BDEBB5;
  display: flex;
  align-items: center;
}

/* Action Button */
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 11px;
  font-weight: 700;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-family: 'Roboto Mono', monospace;
}
.action-btn.primary {
  background: #fff;
  color: #000;
}
.action-btn.primary:hover:not(:disabled) { opacity: 0.88; }
.action-btn:disabled { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.2); cursor: not-allowed; }

/* --- Main Content Area --- */
.main-content-area {
  flex: 1;
  overflow-y: auto;
  position: relative;
  background: var(--bg);
}
.main-content-area::-webkit-scrollbar { width: 3px; }
.main-content-area::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); }

/* Timeline Header */
.timeline-header {
  position: sticky;
  top: 0;
  background: rgba(8,8,8,0.92);
  backdrop-filter: blur(10px);
  padding: 10px 24px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  z-index: 5;
  display: flex;
  justify-content: center;
}
.timeline-stats {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
  padding: 4px 14px;
  border-radius: 20px;
}
.total-count { font-weight: 700; color: rgba(255,255,255,0.6); }
.platform-breakdown { display: flex; align-items: center; gap: 8px; }
.breakdown-item { display: flex; align-items: center; gap: 4px; }
.breakdown-divider { color: rgba(255,255,255,0.12); }
.breakdown-item.twitter { color: rgba(255,255,255,0.5); }
.breakdown-item.reddit { color: rgba(189,235,181,0.6); }

/* ── CHAT FEED ── */
.chat-feed {
  padding: 16px 16px 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 100%;
}

.chat-msg {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  animation: chatIn 0.22s cubic-bezier(0.22,1,0.36,1);
}
@keyframes chatIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

.chat-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; flex-shrink: 0;
  margin-top: 2px;
}
.chat-avatar.twitter {
  background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.8);
  border: 1px solid rgba(255,255,255,0.12);
}
.chat-avatar.reddit {
  background: rgba(189,235,181,0.12); color: #BDEBB5;
  border: 1px solid rgba(189,235,181,0.2);
}

.chat-bubble {
  flex: 1; min-width: 0;
  background: rgba(255,255,255,0.025);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px 12px 12px 3px;
  padding: 10px 14px;
  transition: border-color 0.15s;
}
.chat-msg.twitter .chat-bubble { border-color: rgba(255,255,255,0.08); }
.chat-msg.reddit  .chat-bubble { border-color: rgba(189,235,181,0.1); background: rgba(189,235,181,0.02); }
.chat-bubble:hover { border-color: rgba(255,255,255,0.14); }

.chat-bubble-header {
  display: flex; align-items: center; gap: 7px;
  margin-bottom: 7px; flex-wrap: wrap;
}
.chat-agent-name {
  font-size: 11.5px; font-weight: 600;
  color: rgba(255,255,255,0.75);
}
.chat-msg.reddit .chat-agent-name { color: #BDEBB5; }
.chat-action-badge {
  font-size: 8.5px; font-weight: 700; letter-spacing: 0.08em;
  padding: 2px 6px; border-radius: 3px; text-transform: uppercase;
}
.chat-platform-icon { color: rgba(255,255,255,0.2); display: flex; align-items: center; }
.chat-msg.reddit .chat-platform-icon { color: rgba(189,235,181,0.3); }
.chat-time {
  font-size: 9px; color: rgba(255,255,255,0.2);
  margin-left: auto; white-space: nowrap;
}

.chat-bubble-body { font-size: 12.5px; line-height: 1.55; color: rgba(255,255,255,0.72); }

.chat-waiting {
  display: flex; align-items: center; gap: 12px;
  color: rgba(255,255,255,0.2); font-size: 11px;
  padding: 32px 0; justify-content: center;
}

.chat-error {
  display: flex; align-items: flex-start; gap: 10px;
  color: rgba(255, 90, 90, 0.85); font-size: 11px;
  padding: 20px 16px;
  background: rgba(255, 60, 60, 0.07);
  border: 1px solid rgba(255, 60, 60, 0.18);
  border-radius: 8px; margin: 16px;
  line-height: 1.5;
}

/* Chat input bar */
.chat-input-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(8,8,12,0.95);
  flex-shrink: 0;
}
.chat-input {
  flex: 1; background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1); border-radius: 20px;
  padding: 8px 14px; font-size: 12px; color: rgba(255,255,255,0.8);
  outline: none; font-family: inherit;
  transition: border-color 0.15s;
}
.chat-input:focus { border-color: rgba(189,235,181,0.3); }
.chat-input::placeholder { color: rgba(255,255,255,0.2); }
.chat-send-btn {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--green, #BDEBB5); border: none;
  color: #000; display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0; transition: opacity 0.15s;
}
.chat-send-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.chat-send-btn:not(:disabled):hover { opacity: 0.85; }

/* Transition */
.chat-msg-enter-active { transition: all 0.22s cubic-bezier(0.22,1,0.36,1); }
.chat-msg-leave-active { transition: all 0.18s ease; }
.chat-msg-enter-from  { opacity: 0; transform: translateY(10px); }
.chat-msg-leave-to    { opacity: 0; }

/* Legacy: keep avatar-placeholder for light-mode overrides in theme.css */
.avatar-placeholder {
  width: 28px; height: 28px;
  background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7);
  border-radius: 50%; display: none;
}
.timeline-item.reddit .avatar-placeholder {
  background: rgba(189,235,181,0.08);
  color: #BDEBB5;
  border-color: rgba(189,235,181,0.2);
}
.agent-name { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.75); }
.header-meta { display: flex; align-items: center; gap: 7px; }
.platform-indicator { color: rgba(255,255,255,0.2); display: flex; align-items: center; }
.timeline-item.reddit .platform-indicator { color: rgba(189,235,181,0.4); }

.action-badge {
  font-size: 8px;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border: 1px solid transparent;
}
.badge-post { background: rgba(189,235,181,0.1); color: #BDEBB5; border-color: rgba(189,235,181,0.2); }
.badge-comment { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.45); border-color: rgba(255,255,255,0.08); }
.badge-action { background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.35); border-color: rgba(255,255,255,0.06); }
.badge-meta { background: transparent; color: rgba(255,255,255,0.2); border: 1px dashed rgba(255,255,255,0.07); }
.badge-idle { opacity: 0.35; }
.badge-default { background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.3); border-color: rgba(255,255,255,0.06); }

.content-text { font-size: 12px; line-height: 1.65; color: rgba(255,255,255,0.55); margin-bottom: 8px; }
.content-text.main-text { font-size: 13px; color: rgba(255,255,255,0.8); }

.quoted-block, .repost-content {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-left: 2px solid rgba(255,255,255,0.1);
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 8px;
  font-size: 11px;
  color: rgba(255,255,255,0.4);
}
.quote-header, .repost-info, .like-info, .search-info, .follow-info, .vote-info, .idle-info, .comment-context {
  display: flex; align-items: center; gap: 6px;
  margin-bottom: 5px;
  font-size: 10px;
  color: rgba(255,255,255,0.3);
}
.icon-small { color: rgba(255,255,255,0.2); }
.icon-small.filled { color: rgba(255,255,255,0.25); }
.search-query {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(255,255,255,0.05);
  padding: 0 4px;
  border-radius: 2px;
  color: rgba(255,255,255,0.5);
}
.card-footer {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  font-size: 9px;
  color: rgba(255,255,255,0.18);
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.04em;
}

/* Waiting State */
.waiting-state {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column;
  align-items: center; gap: 18px;
  color: rgba(255,255,255,0.15);
  font-size: 10px; text-transform: uppercase; letter-spacing: 0.14em;
}
.pulse-ring {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 1px solid rgba(189,235,181,0.2);
  animation: ripple 2.4s infinite;
}
@keyframes ripple {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(2.8); opacity: 0; }
}

/* Animation */
.timeline-item-enter-active,
.timeline-item-leave-active {
  transition: all 0.35s cubic-bezier(0.165, 0.84, 0.44, 1);
}
.timeline-item-enter-from { opacity: 0; transform: translateY(16px); }
.timeline-item-leave-to { opacity: 0; }

/* Logs */
.system-logs {
  background: rgba(0,0,0,0.6);
  border-top: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
  padding: 10px 16px;
  font-family: 'JetBrains Mono', monospace;
}
.log-header {
  display: flex; justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding-bottom: 6px; margin-bottom: 6px;
  font-size: 9px; letter-spacing: 0.1em;
}
.log-title { color: rgba(255,255,255,0.2); }
.log-id { color: rgba(255,255,255,0.12); }
.log-content {
  display: flex; flex-direction: column; gap: 2px;
  height: 80px; overflow-y: auto; padding-right: 4px;
}
.log-content::-webkit-scrollbar { width: 3px; }
.log-content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 2px; }
.log-line { font-size: 10px; display: flex; gap: 12px; line-height: 1.5; }
.log-time { color: rgba(255,255,255,0.2); min-width: 75px; }
.log-msg { color: rgba(255,255,255,0.5); word-break: break-all; }
.mono { font-family: 'JetBrains Mono', monospace; }

.loading-spinner-small {
  display: inline-block;
  width: 12px; height: 12px;
  border: 2px solid rgba(0,0,0,0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.arrow-icon { font-size: 14px; }

/* Cascade toasts */
.cascade-toasts {
  position: absolute;
  top: 70px; right: 16px;
  z-index: 200;
  display: flex; flex-direction: column; gap: 8px;
  pointer-events: none;
  width: 280px;
}
.cascade-toast {
  display: flex; align-items: center; gap: 10px;
  background: rgba(10,10,10,0.92);
  border: 1px solid rgba(189,235,181,0.3);
  border-radius: 8px; padding: 10px 14px;
  pointer-events: all; cursor: pointer;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
.cascade-toast-enter-active { transition: all 0.3s cubic-bezier(0.165,0.84,0.44,1); }
.cascade-toast-leave-active { transition: all 0.25s ease; }
.cascade-toast-enter-from { opacity: 0; transform: translateX(30px); }
.cascade-toast-leave-to { opacity: 0; transform: translateY(-10px); }
.toast-icon { font-size: 14px; flex-shrink: 0; }
.toast-body { flex: 1; min-width: 0; }
.toast-title { font-size: 8px; font-weight: 700; letter-spacing: 0.14em; color: #BDEBB5; margin-bottom: 2px; }
.toast-msg { font-size: 10px; color: rgba(255,255,255,0.6); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.toast-spread { font-size: 13px; font-weight: 700; color: #BDEBB5; flex-shrink: 0; }

/* Action distribution */
.action-dist { display: flex; flex-direction: column; gap: 4px; min-width: 120px; }
.dist-label { font-size: 7px; color: rgba(255,255,255,0.2); letter-spacing: 0.14em; font-weight: 700; }
.dist-bars { height: 4px; border-radius: 2px; overflow: hidden; display: flex; background: rgba(255,255,255,0.05); }
.dist-bar { height: 100%; transition: width 0.5s ease; }
.dist-counts { display: flex; flex-wrap: wrap; gap: 6px; }
.dist-count-item { font-size: 9px; font-weight: 600; opacity: 0.85; }

/* Agent search + round filter */
.timeline-filters {
  display: flex; align-items: center; gap: 10px;
  margin-top: 8px;
}
.agent-search {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 4px; padding: 4px 10px;
  font-family: 'Roboto Mono', monospace; font-size: 10px;
  color: rgba(255,255,255,0.7); outline: none;
  width: 150px; transition: border-color 0.15s;
}
.agent-search:focus { border-color: rgba(189,235,181,0.35); }
.agent-search::placeholder { color: rgba(255,255,255,0.2); }
.round-filter { display: flex; align-items: center; gap: 6px; }
.round-filter-label { font-size: 9px; color: rgba(255,255,255,0.3); min-width: 55px; font-family: 'Roboto Mono', monospace; }
.round-slider {
  -webkit-appearance: none; appearance: none;
  width: 80px; height: 3px;
  background: rgba(255,255,255,0.1); border-radius: 2px; outline: none;
}
.round-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 12px; height: 12px;
  background: #BDEBB5; border-radius: 50%; cursor: pointer;
}

/* Variable injection */
.inject-wrap { display: flex; align-items: center; gap: 6px; }
.inject-input-row { display: flex; align-items: center; gap: 5px; }
.inject-input {
  background: rgba(255,255,255,0.06); border: 1px solid rgba(189,235,181,0.3);
  border-radius: 5px; padding: 7px 12px;
  font-family: 'Roboto Mono', monospace; font-size: 10px;
  color: rgba(255,255,255,0.85); outline: none; width: 220px;
}
.inject-input:focus { border-color: rgba(189,235,181,0.6); }
.inject-input::placeholder { color: rgba(255,255,255,0.2); }
.inject-send {
  background: #BDEBB5; color: #000; border: none;
  border-radius: 4px; padding: 6px 10px;
  font-size: 13px; cursor: pointer; transition: opacity 0.12s;
}
.inject-send:hover:not(:disabled) { opacity: 0.85; }
.inject-send:disabled { background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.2); cursor: not-allowed; }
.inject-cancel {
  background: transparent; border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.4); border-radius: 4px; padding: 6px 8px;
  font-size: 14px; cursor: pointer; transition: all 0.12s;
}
.inject-cancel:hover { border-color: rgba(255,255,255,0.25); color: rgba(255,255,255,0.7); }
.inject-btn {
  background: rgba(189,235,181,0.1) !important;
  color: #BDEBB5 !important;
  border: 1px solid rgba(189,235,181,0.25) !important;
  font-size: 10px !important; padding: 7px 14px !important;
}
.inject-btn:hover { background: rgba(189,235,181,0.18) !important; }
</style>