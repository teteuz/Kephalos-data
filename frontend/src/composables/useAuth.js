import { ref, computed } from 'vue'
import { supabase } from '../lib/supabase'
import { useRouter } from 'vue-router'

const user = ref(null)
const session = ref(null)
const loading = ref(true)

// Initialize auth state from Supabase session
supabase.auth.getSession().then(({ data }) => {
  session.value = data.session
  user.value = data.session?.user ?? null
  loading.value = false
})

supabase.auth.onAuthStateChange((_event, _session) => {
  session.value = _session
  user.value = _session?.user ?? null
})

export function useAuth() {
  const router = useRouter()

  const isAuthenticated = computed(() => !!user.value)
  const userEmail = computed(() => user.value?.email)
  const userId = computed(() => user.value?.id)

  async function signUp(email, password) {
    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) throw error
    return data
  }

  async function signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    return data
  }

  async function signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    router.push('/login')
  }

  async function resetPassword(email) {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`
    })
    if (error) throw error
  }

  async function updatePassword(newPassword) {
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    if (error) throw error
  }

  function getAccessToken() {
    return session.value?.access_token ?? null
  }

  return {
    user,
    session,
    loading,
    isAuthenticated,
    userEmail,
    userId,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updatePassword,
    getAccessToken
  }
}
