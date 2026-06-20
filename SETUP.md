# Kephalos — Guia Completo de Setup e Deploy

## Visão Geral da Arquitetura

```
Frontend (Vue 3 + Vite)  ──── HTTPS ────►  Backend (Flask, Python)
        │                                         │
        │  Supabase JS SDK                        │  stripe-python
        ▼                                         ▼
  Supabase (auth + DB)              Stripe API + Supabase Admin
        ▲                                         │
        └─────── webhook ─────────────────────────┘
```

---

## PASSO 1 — Supabase

### 1.1 Rodar as migrations (uma vez)

Acesse **supabase.com → seu projeto → SQL Editor** e cole o conteúdo
do arquivo `supabase/migrations.sql`. Ele cria:

- `stripe_customers` — mapeia user_id → stripe_customer_id
- `subscriptions` — espelha o objeto de assinatura do Stripe
- RLS habilitado nas duas tabelas
- Função `is_subscribed()` para uso em políticas RLS

### 1.2 Ativar Email Auth

Supabase → Authentication → Providers → **Email → Enable**.

### 1.3 Variáveis necessárias

| Onde buscar | Variável |
|---|---|
| Supabase → Settings → API → URL | `VITE_SUPABASE_URL` (frontend) |
| Supabase → Settings → API → anon key | `VITE_SUPABASE_ANON_KEY` (frontend) |
| Supabase → Settings → API → service_role | `SUPABASE_SERVICE_ROLE_KEY` (backend — nunca expor) |

Estas já estão preenchidas nos arquivos `.env` e `.env.local`.

---

## PASSO 2 — Stripe (desenvolvimento local com Stripe CLI)

O Stripe precisa enviar eventos de pagamento (webhooks) para o seu backend.
Como o backend ainda está rodando localmente, usamos o **Stripe CLI** para
criar um túnel temporário — sem precisar de hospedagem.

### 2.1 Instalar o Stripe CLI

**Windows (recomendado via Scoop):**
```powershell
# Instalar Scoop (se não tiver)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Instalar Stripe CLI
scoop bucket add stripe https://github.com/stripe/scoop-stripe-cli.git
scoop install stripe
```

**Alternativa — baixar o .exe diretamente:**
Acesse https://github.com/stripe/stripe-cli/releases e baixe
`stripe_X.X.X_windows_x86_64.zip`, extraia e coloque `stripe.exe` no PATH.

### 2.2 Autenticar

```bash
stripe login
```
Abrirá o navegador para autorizar. Faça login com sua conta Stripe.

### 2.3 Escutar webhooks e repassar ao Flask

```bash
stripe listen --forward-to http://localhost:5001/api/stripe/webhook
```

A saída será algo como:
```
> Ready! Your webhook signing secret is whsec_abc123...
```

**Copie esse `whsec_...` e cole no `.env` raiz:**
```
STRIPE_WEBHOOK_SECRET=whsec_abc123...
```

Deixe este terminal rodando enquanto testa. Cada vez que rodar
`stripe listen` um novo segredo é gerado — atualize o `.env` e
reinicie o Flask.

### 2.4 Verificar o produto e preço no Stripe

Stripe Dashboard → Products → confirme que o produto Pro existe
e o Price ID bate com `STRIPE_PRICE_PRO_MONTHLY` no `.env`.

### 2.5 Ativar o Customer Portal

Stripe Dashboard → Settings → Billing → **Customer portal → Save**.
Necessário para o botão "Gerenciar / Cancelar".

---

## PASSO 3 — Rodar o projeto localmente

### Terminal 1 — Backend Flask

```bash
cd backend
pip install -r requirements.txt
python run.py
# ou: flask --app app run --port 5001
```

### Terminal 2 — Stripe CLI (webhook)

```bash
stripe listen --forward-to http://localhost:5001/api/stripe/webhook
```

### Terminal 3 — Frontend Vue

```bash
cd frontend
npm install
npm run dev
```

Acesse http://localhost:3000

### Testar o fluxo completo

1. Crie uma conta em `/register`
2. Acesse `/pricing` e clique em Assinar
3. No Stripe Checkout, use o cartão de teste: `4242 4242 4242 4242`
4. Após o pagamento, o Stripe CLI repassa o evento para o Flask
5. O Flask atualiza a tabela `subscriptions` no Supabase
6. Você é redirecionado para `/dashboard` com assinatura ativa

---

## PASSO 4 — Hospedagem com Railway (backend em produção)

Railway é gratuito para começar (500h/mês) e aceita Python/Flask diretamente.

### 4.1 Instalar Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### 4.2 Criar o projeto

```bash
# Na raiz do KephalosData
railway init
# Selecione "Empty project" e dê o nome "kephalos-backend"
```

### 4.3 Criar Procfile no backend

```
# backend/Procfile
web: flask --app app run --host 0.0.0.0 --port $PORT
```

### 4.4 Configurar variáveis no Railway

No painel Railway → seu projeto → Variables, adicione todas as variáveis
do seu `.env` raiz (LLM_API_KEY, STRIPE_SECRET_KEY, SUPABASE_URL, etc.)

Adicione também:
```
FLASK_ENV=production
CORS_ORIGINS=https://seu-app.vercel.app,https://kephalosdata.com
```

### 4.5 Fazer deploy

```bash
cd backend
railway up
```

Railway te dará uma URL pública como `https://kephalos-backend-production.up.railway.app`.

### 4.6 Configurar webhook de produção no Stripe

Com o backend hospedado, substitua o Stripe CLI pelo webhook real:

Stripe Dashboard → Developers → Webhooks → **Add endpoint**:
- URL: `https://kephalos-backend-production.up.railway.app/api/stripe/webhook`
- Eventos:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_failed`

Copie o **Signing Secret** gerado e atualize `STRIPE_WEBHOOK_SECRET`
no Railway Variables.

### 4.7 Atualizar o frontend

Em `frontend/.env.local` (dev) ou variáveis de ambiente do Vercel (prod):
```
VITE_API_BASE_URL=https://kephalos-backend-production.up.railway.app
```

---

## PASSO 5 — Frontend no Vercel

```bash
cd frontend
npm install -g vercel
vercel
```

No painel Vercel → Settings → Environment Variables, adicione:
```
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
VITE_API_BASE_URL=https://kephalos-backend-production.up.railway.app
VITE_STRIPE_PRICE_PRO=price_1TLWdP7YRhynYDomtSr6vnXm
```

---

## PASSO 6 — App Mobile com Capacitor (iOS + Android)

O Capacitor empacota o Vue app como um app nativo. O código Vue
não muda — apenas é executado dentro de um WebView nativo.

### 6.1 Pré-requisitos

| Plataforma | Requisito |
|---|---|
| Android | Android Studio instalado |
| iOS | Mac com Xcode 14+ (obrigatório — não há como publicar no iOS sem Mac) |

### 6.2 Instalar dependências

```bash
cd frontend
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios
```

### 6.3 Inicializar o Capacitor

```bash
npx cap init "Kephalos Data" "com.kephalosdata.app" --web-dir dist
```

O arquivo `capacitor.config.ts` já está criado na pasta `frontend/`.

### 6.4 Adicionar plataformas

```bash
npx cap add android
npx cap add ios
```

Isso cria as pastas `frontend/android/` e `frontend/ios/`.

### 6.5 Build e sincronizar

```bash
# Compila o Vue e copia para as pastas nativas
npm run mobile:sync

# Ou separado:
npm run build
npx cap sync
```

### 6.6 Abrir no Android Studio

```bash
npm run mobile:android
# equivalente a: npx cap open android
```

No Android Studio → Run → selecione emulador ou celular conectado.

### 6.7 Abrir no Xcode (Mac)

```bash
npm run mobile:ios
# equivalente a: npx cap open ios
```

### 6.8 Publicar na Play Store

1. Android Studio → Build → Generate Signed Bundle (AAB)
2. Acesse play.google.com/console → Create app → Upload AAB
3. Preencha ficha, screenshots, política de privacidade → Submit

### 6.9 Publicar na App Store

1. Xcode → Product → Archive → Distribute App → App Store Connect
2. Acesse appstoreconnect.apple.com → My Apps → New App
3. Preencha ficha, screenshots → Submit for Review

### 6.10 Importante: URL do backend no app mobile

O app mobile não consegue acessar `localhost`. Em produção,
`VITE_API_BASE_URL` deve apontar para a URL pública do Railway.

Para testar em desenvolvimento com celular físico na mesma rede Wi-Fi,
edite `frontend/capacitor.config.ts` e descomente:
```ts
server: {
  url: 'http://192.168.1.157:3000',  // IP do seu computador
  cleartext: true,
}
```

---

## Checklist de produção

- [ ] Supabase migrations rodadas
- [ ] Supabase Email Auth ativado
- [ ] Stripe produto e preço criados
- [ ] Stripe Customer Portal ativado
- [ ] Backend no Railway com todas as variáveis de ambiente
- [ ] Webhook de produção configurado no Stripe (URL do Railway)
- [ ] Frontend no Vercel com VITE_API_BASE_URL apontando pro Railway
- [ ] Stripe em modo Live (trocar `sk_test_` por `sk_live_`)
- [ ] `.env` nunca commitado no git (verificar .gitignore)
