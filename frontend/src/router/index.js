import { createRouter, createWebHistory } from 'vue-router'
import { supabase } from '../lib/supabase'

// Views
import Home from '../views/Home.vue'
import MainView from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'

// Auth Views (new)
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import PricingView from '../views/PricingView.vue'
import DashboardView from '../views/DashboardView.vue'
import SimularView from '../views/SimularView.vue'

const routes = [
  // Public routes
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: LoginView, meta: { guest: true } },
  { path: '/register', name: 'Register', component: RegisterView, meta: { guest: true } },
  { path: '/pricing', name: 'Pricing', component: PricingView },

  // Console de simulação
  {
    path: '/simular',
    name: 'Simular',
    component: SimularView,
    meta: { requiresAuth: true }
  },

  // Auth-required routes
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: MainView,
    props: true,
    meta: { requiresAuth: true, requiresSubscription: true }
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true,
    meta: { requiresAuth: true, requiresSubscription: true }
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true,
    meta: { requiresAuth: true, requiresSubscription: true }
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true,
    meta: { requiresAuth: true, requiresSubscription: true }
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true,
    meta: { requiresAuth: true, requiresSubscription: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const { data } = await supabase.auth.getSession()
  const session = data.session

  // Route requires auth and user is not logged in
  if (to.meta.requiresAuth && !session) {
    return next({ name: 'Login', query: { redirect: to.fullPath } })
  }

  // Route is guest-only (login/register) and user is already logged in
  if (to.meta.guest && session) {
    return next({ name: 'Dashboard' })
  }

  // Subscription gate — only checked for protected routes
  if (to.meta.requiresSubscription && session) {
    const { data: subData } = await supabase
      .from('subscriptions')
      .select('status')
      .eq('user_id', session.user.id)
      .single()

    const active = subData?.status === 'active' || subData?.status === 'trialing'
    if (!active) {
      return next({ name: 'Pricing', query: { upgrade: '1' } })
    }
  }

  next()
})

export default router
