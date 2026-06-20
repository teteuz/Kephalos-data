"""
Stripe integration — checkout, portal, and webhook
Uses stripe-python v5+ StripeClient API.

Env vars required (in root .env):
  STRIPE_SECRET_KEY
  STRIPE_WEBHOOK_SECRET
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY
"""

import os
import stripe
from flask import Blueprint, request, jsonify, current_app

from ..utils.supabase_client import get_supabase_admin

stripe_bp = Blueprint('stripe', __name__)


# ─── Clients ──────────────────────────────────────────────────────────────────

def _stripe_client():
    return stripe.StripeClient(os.environ['STRIPE_SECRET_KEY'])


# ─── Auth middleware ───────────────────────────────────────────────────────────

def _require_auth():
    """Returns (user, error_response) tuple."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, (jsonify(error='Missing token'), 401)
    token = auth_header.split(' ', 1)[1]
    try:
        sb = get_supabase_admin()
        result = sb.auth.get_user(token)
        user = result.user
        if not user:
            raise ValueError('no user')
        return user, None
    except Exception:
        return None, (jsonify(error='Invalid token'), 401)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_stripe_customer_id(user_id: str):
    result = get_supabase_admin().table('stripe_customers') \
        .select('stripe_customer_id') \
        .eq('user_id', user_id) \
        .limit(1) \
        .execute()
    rows = result.data or []
    return rows[0]['stripe_customer_id'] if rows else None


def _save_stripe_customer_id(user_id: str, stripe_customer_id: str):
    get_supabase_admin().table('stripe_customers').upsert({
        'user_id': user_id,
        'stripe_customer_id': stripe_customer_id,
    }).execute()


def _get_user_id_from_customer(stripe_customer_id: str):
    result = get_supabase_admin().table('stripe_customers') \
        .select('user_id') \
        .eq('stripe_customer_id', stripe_customer_id) \
        .limit(1) \
        .execute()
    rows = result.data or []
    return rows[0]['user_id'] if rows else None


def _attr(obj, key, default=None):
    """Safe attribute access for both StripeObject and plain dicts."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _upsert_subscription(subscription):
    customer_id = _attr(subscription, 'customer')
    user_id = _get_user_id_from_customer(customer_id)
    if not user_id:
        current_app.logger.error('_upsert_subscription: no user for customer %s', customer_id)
        return

    items_obj = _attr(subscription, 'items')
    items_data = _attr(items_obj, 'data', []) if items_obj else []
    first = items_data[0] if items_data else None
    price = _attr(first, 'price') if first else None
    plan_name = (_attr(price, 'nickname') or 'Pro') if price else 'Pro'
    price_id = _attr(price, 'id') if price else None

    try:
        get_supabase_admin().table('subscriptions').upsert({
            'user_id': user_id,
            'stripe_subscription_id': _attr(subscription, 'id'),
            'stripe_customer_id': customer_id,
            'status': _attr(subscription, 'status'),
            'plan_name': plan_name,
            'price_id': price_id,
            'current_period_start': _attr(subscription, 'current_period_start'),
            'current_period_end': _attr(subscription, 'current_period_end'),
            'cancel_at_period_end': _attr(subscription, 'cancel_at_period_end', False),
        }, on_conflict='user_id').execute()
        current_app.logger.info('Subscription upserted for user %s: status=%s',
                                user_id, _attr(subscription, 'status'))
    except Exception as e:
        current_app.logger.error('Failed to upsert subscription: %s', e)


def _cancel_subscription(subscription):
    user_id = _get_user_id_from_customer(_attr(subscription, 'customer'))
    if not user_id:
        return
    get_supabase_admin().table('subscriptions') \
        .update({'status': 'canceled'}) \
        .eq('user_id', user_id).execute()


def _handle_checkout_completed(session):
    subscription_id = _attr(session, 'subscription')
    customer_id = _attr(session, 'customer')
    if not subscription_id or not customer_id:
        return

    user_id = _get_user_id_from_customer(customer_id)
    if not user_id:
        current_app.logger.error('checkout.completed: no user for customer %s', customer_id)
        return

    try:
        sub = _stripe_client().subscriptions.retrieve(subscription_id)
        _upsert_subscription(sub)
    except Exception as e:
        current_app.logger.error('checkout.completed handler error: %s', e)


# ─── Routes ───────────────────────────────────────────────────────────────────

@stripe_bp.post('/create-checkout-session')
def create_checkout_session():
    user, err = _require_auth()
    if err:
        return err

    body = request.get_json(force=True)
    price_id = body.get('priceId')
    success_url = body.get('successUrl')
    cancel_url = body.get('cancelUrl')

    if not price_id:
        return jsonify(error='priceId is required'), 400

    try:
        client = _stripe_client()

        customer_id = _get_stripe_customer_id(user.id)
        if not customer_id:
            customer = client.customers.create(params={
                'email': user.email,
                'metadata': {'supabase_user_id': user.id},
            })
            customer_id = customer.id
            _save_stripe_customer_id(user.id, customer_id)

        session = client.checkout.sessions.create(params={
            'mode': 'subscription',
            'customer': customer_id,
            'line_items': [{'price': price_id, 'quantity': 1}],
            'success_url': success_url,
            'cancel_url': cancel_url,
            'subscription_data': {'metadata': {'supabase_user_id': user.id}},
        })
        return jsonify(success=True, url=session.url)
    except Exception as e:
        current_app.logger.exception('Stripe checkout error')
        return jsonify(success=False, error=str(e)), 500


@stripe_bp.post('/create-portal-session')
def create_portal_session():
    user, err = _require_auth()
    if err:
        return err

    body = request.get_json(force=True)
    return_url = body.get('returnUrl')

    try:
        customer_id = _get_stripe_customer_id(user.id)
        if not customer_id:
            return jsonify(error='No Stripe customer found'), 400

        session = _stripe_client().billing_portal.sessions.create(params={
            'customer': customer_id,
            'return_url': return_url,
        })
        return jsonify(success=True, url=session.url)
    except Exception as e:
        current_app.logger.exception('Portal session error')
        return jsonify(success=False, error=str(e)), 500


@stripe_bp.post('/webhook')
def webhook():
    payload = request.get_data()
    sig = request.headers.get('Stripe-Signature', '')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig, webhook_secret)
    except stripe.error.SignatureVerificationError as e:
        current_app.logger.error('Webhook signature failed: %s', e)
        return jsonify(error='Invalid signature'), 400
    except Exception as e:
        current_app.logger.error('Webhook error: %s', e)
        return jsonify(error=str(e)), 400

    data = event['data']['object']
    event_type = event['type']
    current_app.logger.info('Webhook received: %s', event_type)

    if event_type == 'checkout.session.completed':
        _handle_checkout_completed(data)
    elif event_type in ('customer.subscription.created', 'customer.subscription.updated'):
        _upsert_subscription(data)
    elif event_type == 'customer.subscription.deleted':
        _cancel_subscription(data)
    elif event_type == 'invoice.payment_failed':
        current_app.logger.warning('Payment failed for customer: %s', data.get('customer'))

    return jsonify(received=True)
