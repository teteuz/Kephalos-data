<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <AppLogo style="height:28px" />
      </div>

      <h1 class="auth-title">Entrar</h1>
      <p class="auth-sub">Acesse seu ambiente de simulação</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="form-field">
          <label>E-mail</label>
          <input v-model="email" type="email" placeholder="voce@empresa.com" autocomplete="email" required />
        </div>

        <div class="form-field">
          <label>Senha</label>
          <input v-model="password" type="password" placeholder="••••••••" autocomplete="current-password" required />
        </div>

        <div v-if="error" class="auth-error">{{ error }}</div>

        <button type="submit" class="auth-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Entrar</span>
        </button>
      </form>

      <div class="auth-footer">
        <router-link to="/login" @click.prevent="handleForgot" class="auth-link">
          Esqueci a senha
        </router-link>
        <span class="auth-sep">·</span>
        <router-link to="/register" class="auth-link">Criar conta</router-link>
      </div>

      <div v-if="forgotSent" class="auth-success">
        Verifique seu e-mail. Link de redefinição enviado.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import AppLogo from '../components/AppLogo.vue'

const { signIn, resetPassword } = useAuth()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const forgotSent = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await signIn(email.value, password.value)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (err) {
    error.value = err.message || 'Credenciais inválidas'
  } finally {
    loading.value = false
  }
}

async function handleForgot() {
  if (!email.value) {
    error.value = 'Digite seu e-mail acima primeiro'
    return
  }
  try {
    await resetPassword(email.value)
    forgotSent.value = true
  } catch (err) {
    error.value = err.message
  }
}
</script>

<style scoped>
.auth-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg); padding: 24px; }
.auth-card { width: 100%; max-width: 400px; background: var(--bg3); border: 1px solid var(--border2); border-radius: 8px; padding: 40px 36px; }
.auth-logo { text-align: center; margin-bottom: 28px; }
.auth-title { font-size: 20px; font-weight: 500; color: var(--text); text-align: center; margin-bottom: 6px; }
.auth-sub { font-size: 12px; color: var(--text2); text-align: center; margin-bottom: 32px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.form-field { display: flex; flex-direction: column; gap: 6px; }
.form-field label { font-size: 11px; color: var(--text2); text-transform: uppercase; letter-spacing: 0.8px; }
.form-field input { background: var(--bg2); border: 1px solid var(--border); border-radius: 4px; padding: 10px 12px; color: var(--text); font-family: var(--font); font-size: 13px; outline: none; }
.form-field input:focus { border-color: var(--border2); }
.auth-btn { background: var(--green); color: #000; border: none; border-radius: 4px; padding: 11px; font-size: 13px; font-weight: 600; font-family: var(--font); cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; }
.auth-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.auth-error { font-size: 12px; color: var(--red); background: rgba(239,68,68,0.06); border: 1px solid rgba(239,68,68,0.15); border-radius: 4px; padding: 8px 12px; }
.auth-success { font-size: 12px; color: var(--green); background: rgba(189,235,181,0.06); border: 1px solid rgba(189,235,181,0.15); border-radius: 4px; padding: 8px 12px; margin-top: 16px; }
.auth-footer { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 20px; font-size: 12px; color: var(--text3); }
.auth-link { color: var(--text2); text-decoration: none; }
.auth-link:hover { color: var(--text); }
.auth-sep { color: var(--text3); }
.spinner { width: 13px; height: 13px; border: 2px solid rgba(0,0,0,0.3); border-top-color: #000; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
