import { ref, computed } from 'vue'
import { supabase } from '../lib/supabase'
import { useAuth } from './useAuth'
import service from '../api/index'

const subscription = ref(null)
const loadingSubscription = ref(false)

export function useSubscription() {
  const { userId, isAuthenticated } = useAuth()

  const isSubscribed = computed(() => {
    return subscription.value?.status === 'active' || subscription.value?.status === 'trialing'
  })

  const planName = computed(() => subscription.value?.plan_name ?? 'Free')

  const subscriptionEnd = computed(() => {
    if (!subscription.value?.current_period_end) return null
    return new Date(subscription.value.current_period_end * 1000).toLocaleDateString('pt-BR')
  })

  async function fetchSubscription() {
    if (!isAuthenticated.value) return
    loadingSubscription.value = true
    try {
      const { data, error } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('user_id', userId.value)
        .single()

      if (error && error.code !== 'PGRST116') throw error
      subscription.value = data ?? null
    } catch (err) {
      console.error('Error fetching subscription:', err)
    } finally {
      loadingSubscription.value = false
    }
  }

  // Redirect to Stripe Checkout
  async function subscribe(priceId) {
    const result = await service.post('/api/stripe/create-checkout-session', {
      priceId,
      successUrl: `${window.location.origin}/dashboard?subscribed=true`,
      cancelUrl: `${window.location.origin}/pricing`
    })
    window.location.href = result.url
  }

  // Open Stripe Customer Portal for manage/cancel
  async function manageSubscription() {
    const result = await service.post('/api/stripe/create-portal-session', {
      returnUrl: `${window.location.origin}/dashboard`
    })
    window.location.href = result.url
  }

  return {
    subscription,
    loadingSubscription,
    isSubscribed,
    planName,
    subscriptionEnd,
    fetchSubscription,
    subscribe,
    manageSubscription
  }
}
