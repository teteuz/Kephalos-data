/**
 * Stripe integration routes for Kephalos
 * Mount this in your Express app: app.use('/api/stripe', stripeRouter)
 *
 * Requires env vars:
 *   STRIPE_SECRET_KEY
 *   STRIPE_WEBHOOK_SECRET
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_ROLE_KEY
 */

import express from 'express'
import Stripe from 'stripe'
import { createClient } from '@supabase/supabase-js'

const router = express.Router()

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY)

// Supabase admin client (service role — server-side only, never expose to frontend)
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
)

// ─── Auth middleware ───────────────────────────────────────────────────────────
// Validates the Supabase JWT from the Authorization header and attaches the user
async function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing token' })
  }
  const token = authHeader.split(' ')[1]
  const { data, error } = await supabase.auth.getUser(token)
  if (error || !data.user) {
    return res.status(401).json({ error: 'Invalid token' })
  }
  req.user = data.user
  next()
}

// ─── Create Checkout Session ───────────────────────────────────────────────────
// POST /api/stripe/create-checkout-session
router.post('/create-checkout-session', requireAuth, async (req, res) => {
  const { priceId, successUrl, cancelUrl } = req.body
  const userId = req.user.id
  const email = req.user.email

  try {
    // Retrieve or create Stripe customer
    let customerId = await getStripeCustomerId(userId)
    if (!customerId) {
      const customer = await stripe.customers.create({
        email,
        metadata: { supabase_user_id: userId }
      })
      customerId = customer.id
      await saveStripeCustomerId(userId, customerId)
    }

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      customer: customerId,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: successUrl,
      cancel_url: cancelUrl,
      subscription_data: {
        metadata: { supabase_user_id: userId }
      }
    })

    res.json({ success: true, url: session.url })
  } catch (err) {
    console.error('Stripe checkout error:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

// ─── Create Customer Portal Session ───────────────────────────────────────────
// POST /api/stripe/create-portal-session
router.post('/create-portal-session', requireAuth, async (req, res) => {
  const { returnUrl } = req.body
  const userId = req.user.id

  try {
    const customerId = await getStripeCustomerId(userId)
    if (!customerId) {
      return res.status(400).json({ error: 'No Stripe customer found' })
    }

    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: returnUrl
    })

    res.json({ success: true, url: session.url })
  } catch (err) {
    console.error('Portal session error:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

// ─── Stripe Webhook ───────────────────────────────────────────────────────────
// POST /api/stripe/webhook
// IMPORTANT: This route needs raw body — mount BEFORE express.json() middleware,
// or use express.raw({ type: 'application/json' }) on this specific route.
router.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature']
  let event

  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET)
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message)
    return res.status(400).send(`Webhook Error: ${err.message}`)
  }

  const data = event.data.object

  switch (event.type) {
    case 'customer.subscription.created':
    case 'customer.subscription.updated':
      await upsertSubscription(data)
      break

    case 'customer.subscription.deleted':
      await cancelSubscription(data)
      break

    case 'invoice.payment_failed':
      console.warn('Payment failed for customer:', data.customer)
      // Optionally notify user via email here
      break

    default:
      // Unhandled event type — safe to ignore
      break
  }

  res.json({ received: true })
})

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function getStripeCustomerId(userId) {
  const { data } = await supabase
    .from('stripe_customers')
    .select('stripe_customer_id')
    .eq('user_id', userId)
    .single()
  return data?.stripe_customer_id ?? null
}

async function saveStripeCustomerId(userId, stripeCustomerId) {
  await supabase
    .from('stripe_customers')
    .upsert({ user_id: userId, stripe_customer_id: stripeCustomerId })
}

async function getUserIdFromCustomer(stripeCustomerId) {
  const { data } = await supabase
    .from('stripe_customers')
    .select('user_id')
    .eq('stripe_customer_id', stripeCustomerId)
    .single()
  return data?.user_id ?? null
}

async function upsertSubscription(subscription) {
  const userId = await getUserIdFromCustomer(subscription.customer)
  if (!userId) {
    console.error('No user found for Stripe customer:', subscription.customer)
    return
  }

  const planName = subscription.items.data[0]?.price?.nickname || 'Pro'

  await supabase.from('subscriptions').upsert({
    user_id: userId,
    stripe_subscription_id: subscription.id,
    stripe_customer_id: subscription.customer,
    status: subscription.status,
    plan_name: planName,
    price_id: subscription.items.data[0]?.price?.id,
    current_period_start: subscription.current_period_start,
    current_period_end: subscription.current_period_end,
    cancel_at_period_end: subscription.cancel_at_period_end,
    updated_at: new Date().toISOString()
  }, { onConflict: 'user_id' })
}

async function cancelSubscription(subscription) {
  const userId = await getUserIdFromCustomer(subscription.customer)
  if (!userId) return

  await supabase
    .from('subscriptions')
    .update({ status: 'canceled', updated_at: new Date().toISOString() })
    .eq('user_id', userId)
}

export default router
