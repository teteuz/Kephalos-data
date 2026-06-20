<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <AppLogo style="height:28px" />
      </div>

      <h1 class="auth-title">Criar Conta</h1>
      <p class="auth-sub">Comece gratuitamente, sem cartão de crédito</p>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="form-field">
          <label>E-mail</label>
          <input v-model="email" type="email" placeholder="voce@empresa.com" required />
        </div>

        <div class="form-field">
          <label>Senha</label>
          <input v-model="password" type="password" placeholder="Mín. 8 caracteres" required minlength="8" />
        </div>

        <div class="form-field">
          <label>Confirmar Senha</label>
          <input v-model="confirm" type="password" placeholder="Repita a senha" required />
        </div>

        <div v-if="error" class="auth-error">{{ error }}</div>

        <button type="submit" class="auth-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Criar Conta</span>
        </button>
      </form>

      <div v-if="success" class="auth-success">
        Conta criada! Verifique seu e-mail para confirmar, depois <router-link to="/login" class="auth-link">entre</router-link>.
      </div>

      <div class="auth-footer">
        Já tem uma conta?
        <router-link to="/login" class="auth-link">Entrar</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '../composables/useAuth'
import AppLogo from '../components/AppLogo.vue'

const { signUp } = useAuth()

const email = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)
const success = ref(false)

async function handleRegister() {
  error.value = ''
  if (password.value !== confirm.value) {
    error.value = 'As senhas não coincidem'
    return
  }
  loading.value = true
  try {
    await signUp(email.value, password.value)
    success.value = true
  } catch (err) {
    error.value = err.message || 'Erro ao criar conta'
  } finally {
    loading.value = false
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
.spinner { width: 13px; height: 13px; border: 2px solid rgba(0,0,0,0.3); border-top-color: #000; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
