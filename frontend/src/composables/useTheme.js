import { ref, computed } from 'vue'

const theme = ref(
  (typeof localStorage !== 'undefined' && localStorage.getItem('kephalos_theme')) || 'light'
)

export function useTheme() {
  const isDark = computed(() => theme.value === 'dark')

  function setTheme(t) {
    theme.value = t
    document.documentElement.setAttribute('data-theme', t)
    localStorage.setItem('kephalos_theme', t)
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  return { theme, isDark, setTheme, toggleTheme }
}
