import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './lib/supabase'
import './assets/theme.css'

// Apply saved theme before mount to avoid flash
const saved = localStorage.getItem('kephalos_theme') || 'light'
document.documentElement.setAttribute('data-theme', saved)

const app = createApp(App)
app.use(router)
app.mount('#app')
