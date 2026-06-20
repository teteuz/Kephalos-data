-- ============================================================
-- Kephalos: Supabase migrations for auth + Stripe integration
-- Run these in the Supabase SQL Editor
-- ============================================================

-- 1. stripe_customers
--    Maps each Supabase user to their Stripe customer ID
-- ------------------------------------------------------------
create table if not exists public.stripe_customers (
  user_id        uuid primary key references auth.users(id) on delete cascade,
  stripe_customer_id text unique not null,
  created_at     timestamptz default now()
);

alter table public.stripe_customers enable row level security;

drop policy if exists "Users can view own customer record" on public.stripe_customers;
create policy "Users can view own customer record"
  on public.stripe_customers for select
  using (auth.uid() = user_id);


-- 2. subscriptions
--    Mirrors the Stripe subscription object, kept in sync via webhook
-- ------------------------------------------------------------
create table if not exists public.subscriptions (
  id                      uuid primary key default gen_random_uuid(),
  user_id                 uuid unique not null references auth.users(id) on delete cascade,
  stripe_subscription_id  text unique,
  stripe_customer_id      text,
  status                  text not null default 'inactive',
  -- status values: trialing | active | past_due | canceled | unpaid | incomplete
  plan_name               text default 'Pro',
  price_id                text,
  current_period_start    bigint,
  current_period_end      bigint,
  cancel_at_period_end    boolean default false,
  created_at              timestamptz default now(),
  updated_at              timestamptz default now()
);

alter table public.subscriptions enable row level security;

drop policy if exists "Users can view own subscription" on public.subscriptions;
create policy "Users can view own subscription"
  on public.subscriptions for select
  using (auth.uid() = user_id);

-- Service role (backend) has full access — no RLS policy needed for INSERT/UPDATE
-- because the Supabase service role key bypasses RLS by default.


-- 3. Helpful function: check if the calling user has an active subscription
-- ------------------------------------------------------------
create or replace function public.is_subscribed()
returns boolean
language sql
security definer
as $$
  select exists (
    select 1 from public.subscriptions
    where user_id = auth.uid()
    and status in ('active', 'trialing')
  );
$$;


-- 3. simulation_usage
--    Tracks how many simulations each user creates (for free-tier quota)
-- ------------------------------------------------------------
create table if not exists public.simulation_usage (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users(id) on delete cascade,
  simulation_id  text not null,
  created_at     timestamptz default now()
);

alter table public.simulation_usage enable row level security;

-- Users can view their own usage records (for frontend display)
drop policy if exists "Users can view own simulation usage" on public.simulation_usage;
create policy "Users can view own simulation usage"
  on public.simulation_usage for select
  using (auth.uid() = user_id);

-- Backend (service role key) bypasses RLS for INSERT — no policy needed.

-- Index for fast monthly count queries
create index if not exists simulation_usage_user_month_idx
  on public.simulation_usage (user_id, created_at);


-- 4. Example: protect a table so only subscribed users can insert
-- (Uncomment and adapt to your own tables as needed)
-- ------------------------------------------------------------
-- alter table public.projects enable row level security;
--
-- create policy "Only subscribers can create projects"
--   on public.projects for insert
--   with check (public.is_subscribed());
--
-- create policy "Users can view own projects"
--   on public.projects for select
--   using (auth.uid() = user_id);
