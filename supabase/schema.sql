-- Run once in the Supabase SQL Editor. All data access is through authenticated Next.js API routes.
create extension if not exists pgcrypto;
create table if not exists public.categories (
  id uuid primary key default gen_random_uuid(),
  group_id text not null default 'bubu' check (group_id in ('bubu', 'dreamharam')),
  name text not null,
  kind text not null check (kind in ('income', 'expense', 'both')),
  color text not null default '#4472c4',
  created_at timestamptz not null default now()
);
create table if not exists public.members (
  id uuid primary key default gen_random_uuid(),
  group_id text not null default 'bubu' check (group_id in ('bubu', 'dreamharam')),
  name text not null,
  note text not null default '',
  active boolean not null default true,
  created_at timestamptz not null default now()
);
create table if not exists public.transactions (
  id uuid primary key,
  group_id text not null default 'bubu' check (group_id in ('bubu', 'dreamharam')),
  sheet_row integer not null,
  recorded_at text not null,
  accounting_date date not null,
  kind text not null check (kind in ('income', 'expense')),
  amount bigint not null check (amount >= 0),
  description text not null default '',
  writer text not null,
  category_id uuid references public.categories(id) on delete set null,
  member_id uuid references public.members(id) on delete set null,
  updated_at timestamptz not null default now()
);
-- Also upgrade tables created before the two-department split. Existing rows belong to bubu.
alter table public.categories add column if not exists group_id text not null default 'bubu';
alter table public.members add column if not exists group_id text not null default 'bubu';
alter table public.transactions add column if not exists group_id text not null default 'bubu';
alter table public.categories drop constraint if exists categories_name_key;
create unique index if not exists categories_group_name_key on public.categories(group_id, name);
create index if not exists members_group_id_idx on public.members(group_id);
create index if not exists transactions_group_id_idx on public.transactions(group_id);
create index if not exists transactions_accounting_date_idx on public.transactions(accounting_date desc);
create index if not exists transactions_category_id_idx on public.transactions(category_id);
create index if not exists transactions_member_id_idx on public.transactions(member_id);
alter table public.categories enable row level security;
alter table public.members enable row level security;
alter table public.transactions enable row level security;
