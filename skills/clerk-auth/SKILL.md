---
name: clerk-auth
description: >
  Adds Clerk authentication to a web app via the Clerk CLI, composing with
  Clerk's official AI stack (skills repo, CLI agent mode, MCP server).
  Windows-capable wrapper carrying local conventions: app-ID resolution via
  ~/.agents/env/clerk.env, split credential storage (pk_ frontend, sk_
  secrets), Windows CLI install + PowerShell quoting workarounds, Next.js
  matcher check, docs fallback for other frameworks, visible auth controls,
  clerk doctor, shadcn/ui theming, split-stack field notes (Vite SPA +
  Python/other backend), CLI gatekeeping (sign-up modes, invitations, org
  trap), clean-strip path. Use when the user asks to add Clerk auth,
  sign-in/sign-up, or user management, says "add Clerk to my app", or hits
  Clerk CLI install/login issues on Windows.
---

# Add Clerk Authentication

Set up Clerk authentication with the Clerk CLI. Interactive by default:
present the checklist, pause while the user completes the browser-side login
flow, and continue from CLI output. Before driving the CLI from a script or
sandbox, read "Agent mode rules" below.

## Ecosystem: compose, don't duplicate

Clerk ships a first-class AI-native stack (skills, CLI agent mode, MCP
server, prompts). This pack is a Windows-capable, convention-carrying wrapper
over that stack — not a replacement.

| Concern | Source |
|---|---|
| Framework setup depth, framework patterns, orgs, billing, webhooks, testing, mobile | Official skills: `npx skills add clerk/skills` (https://github.com/clerk/skills); single skill: `npx skills add clerk/skills --skill <name>`. `clerk init` also offers to install them |
| Up-to-date SDK snippets inside AI clients | Clerk MCP server: `clerk mcp install` (also `clerk mcp list`, `clerk mcp uninstall`) |
| Non-interactive CLI automation | Agent mode — rules below; full reference: https://github.com/clerk/skills/blob/main/skills/core/clerk-cli/references/agent-mode.md |
| Cross-project app-ID resolution, credential storage conventions, Windows CLI install reality, non-Next.js key routing | This pack |

Ecosystem overview: https://clerk.com/docs/guides/ai/overview

## Clerk credentials: where they live (never guess)

`clerk init` must link to the user's Clerk application. The app ID looks like
`app_XXXXXXXXXXXXXXXXXXXXXX`. Resolve it in this order:

1. **Per-project env store**: read `~/.agents/env/clerk.env`
   (`%USERPROFILE%\.agents\env\clerk.env`). Lines are
   `<project-folder-name> = <app_id>` (e.g. `chuhai-cloud = app_...`) with a
   `default = <app_id>` fallback. Secret keys never live here.
2. A personalized `clerk.com/SKILL.md` the user pasted contains "linked to
   the Clerk application `app_...`" — use that ID verbatim **and persist it
   into `env/clerk.env`** (project name + app id).
3. If the CLI is authenticated, run `clerk apps list --json`, show the user
   the names and IDs, and ask them to pick. Never choose for them.
4. Otherwise ask the user (the ID is visible in the dashboard.clerk.com URL).

When an ID is confirmed from any source, persist
`<project-folder-name> = <app_id>` into `~/.agents/env/clerk.env` (create if
missing). `<app-id>` below means the resolved ID; never invent one or reuse
another project's.

Key storage split (mirrors the `~/.agents` convention — `env\` for
non-sensitive identifiers, `secrets\` for anything that must not leak):

| Item | Example | Lives in |
|---|---|---|
| App ID | `app_...` | `~/.agents/env/clerk.env` (public identifier) |
| Publishable key | `pk_test_...` / `pk_live_...` | frontend env (designed to be public; safe in client code) |
| Secret key | `sk_test_...` / `sk_live_...` | `~/.agents/secrets/clerk.env` and/or backend `.env` — never client code, never git |

App IDs and publishable keys are public; secret keys are not. Do not read
unrelated secret files to "double-check" — resolve non-sensitive values from
`env/` and ask the user for anything missing.

## Windows CLI reality (verified 2026-08-28)

Windows is supported as a product, but the npm publishing matrix broke at CLI
3.2.0 for win32-x64:

- `npm i -g clerk` at 3.2.0 fails: it pins `@clerk/cli-win32-x64: 3.2.0` in
  optionalDependencies, but that platform package was never published
  (registry E404; latest win32-x64 stable is 2.2.0). Error: "Unsupported or
  missing platform: win32-x64". Same failure via `npx clerk`.
- Workarounds (both verified working):
  1. Pin the older release: `npm i -g clerk@2.2.0` (its win32-x64 platform
     package exists). Older but functional.
  2. Install the binary directly:
     https://github.com/clerk/cli/releases/download/v3.2.0/clerk-win32-x64.exe
     (the official install script at `clerk.com/install` has a proper win32
     branch with MINGW/MSYS/CYGWIN detection).
- Recheck before pinning: `npm view @clerk/cli-win32-x64 versions` — once a
  3.x platform package appears, plain `npm i -g clerk` works again.

### PowerShell quoting and payloads (verified 2026-08-28)

- `clerk config patch --json '{\"k\": \"v\"}'` works. Plain single-quoted
  `'{...}'` gets its quotes stripped by PowerShell native arg passing and
  fails confusingly (or silently with `2>$null`).
- POST bodies: write a temp file, then
  `clerk api /invitations -X POST --file body.json --yes`.
- `clerk env pull --app <id> --file tmp.env`, then parse locally. Bonus: the
  publishable key base64-decodes (strip the `pk_test_` prefix, base64url
  decode, strip a trailing `$`) to the instance's FAPI domain — a
  dashboard-free source for `CLERK_DOMAIN`.

## Preliminary setup checklist

Before running any commands, present the user with this checklist:

```
Here's what I'll do to get you set up with Clerk.

1. Install or update the Clerk CLI
2. Set up Clerk in this project, or scaffold a new app if it's empty
3. Verify the Next.js proxy matcher when applicable
4. Start your app with Clerk installed.

Shall I proceed?
```

## Step 1: Install or update the Clerk CLI

From the project root: `command -v clerk && clerk --version`. If available,
update with `clerk update --yes`. If not: on Windows, read "Windows CLI
reality" above first — plain npm at 3.2.0 fails for win32-x64. Elsewhere use
`npm install -g clerk`. Equivalents: `pnpm install -g clerk`,
`yarn global add clerk`, `bun add -g clerk`,
`brew install clerk/stable/clerk`, or
`curl -fsSL https://clerk.com/install | bash`. Without installing:
`npx clerk@latest <command>` / `bunx clerk`. Shell completion
(`clerk completion`): bash, zsh, fish, PowerShell.

## Step 2: Sign in to Clerk

Immediately after installing or updating the CLI, from the project root run
`clerk auth login`. This is the first command after install or update — do
not list apps, ask which Clerk app to use, or run `clerk init` before
authenticating. It opens a browser and binds a localhost callback; pause
while the user completes the flow, then continue from CLI output. If already
signed in, continue to initialization. Verify with `clerk whoami`.

**Agent/sandbox caveat:** when unauthenticated, `clerk auth login` still
opens a browser and binds a localhost callback — no headless branch, so it
stalls in sandboxes. For headless automation set `CLERK_PLATFORM_API_KEY`
instead (see the official agent-mode reference). If unavailable, hand the
login step back to the user and wait.

### Agent mode rules

- Activation priority: `--mode agent` flag > `CLERK_MODE=agent` env >
  stdout not a TTY (piped / agent harness). Force explicitly when the
  harness might look interactive.
- Conventions: `--yes` for mutations, `--json` for structured output. Every
  command also accepts `--input-json '<json|@file|->'` instead of flags.
- In agent mode, mutation confirmations are silently skipped — `--dry-run`
  is the only safety net for `config patch` / `api -X POST` mutations.
- Errors arrive as structured JSON on stderr; exit codes: `0` success,
  `1` runtime error, `2` usage/validation error.
- Sandbox warn-once ("Host-only Clerk state or system capabilities may be
  unavailable in agent mode..."): treat any auth/link/env/config/API failure
  from that invocation as suspect until rerun on the host shell.

## Step 3: Initialize Clerk

Inspect the current directory to determine whether this is an existing
project or an empty directory.

**Existing project:** `clerk init --app <app-id>`. It detects the framework
and package manager, installs the correct SDK, and applies framework-specific
setup (providers, middleware, auth routes, env config). Do not pass
`--framework` or `--pm` for existing projects unless the user explicitly
wants to override detection or the CLI asks for those values.

**Empty directory:** ask which framework and package manager the user wants;
no preference -> Next.js and npm. Scaffold explicitly:
`clerk init --framework <framework> --pm <package-manager> --app <app-id>`.
Non-interactive: `clerk init -y` skips confirmation prompts;
`--input-json '{"framework":"next","yes":true}'` works too.

**Keyless bootstrap:** an unauthenticated agent on keyless-capable
frameworks defaults to keyless — `clerk init` mints an unclaimed app with
temporary development keys written to the project env; no login, no browser.
A later `clerk auth login` claims it automatically. `--keyless` forces
keyless over a stale link; `--login` forces the authenticated flow.

Package-manager signals on a non-empty directory: `pnpm-lock.yaml` -> pnpm;
`yarn.lock` -> yarn; `bun.lock`/`bun.lockb` -> bun; `package-lock.json` ->
npm. None detected and no user preference -> `npm`.

## Step 4: Verify the Next.js matcher

After `clerk init`, if the project uses Next.js, check `proxy.ts` (or
`middleware.ts` on Next.js 15 and earlier). `config.matcher` must include
Clerk's auto-proxy path once, after the API/TRPC matcher:

```ts
'/(api|trpc)(.*)',
'/__clerk/:path*',
```

Add `'/__clerk/:path*'` if it is missing.

## Step 5: Fall back to docs when init is incomplete

If `clerk init` reports the framework as unsupported, undetectable, or only
partially supported, follow the official quickstart. `clerk init` fully
scaffolds Next.js (App and Pages Router), React, React Router, Nuxt, TanStack
Start, Astro, Vue, JavaScript/Vite; Expo, Express, and Fastify get SDK
installation with the remaining steps coming from docs.

| Dependency | Quickstart |
|------------|-----------|
| `next` | https://clerk.com/docs/nextjs/getting-started/quickstart |
| `@remix-run/react` (Remix) | https://clerk.com/docs/react-router/getting-started/quickstart |
| `astro` | https://clerk.com/docs/astro/getting-started/quickstart |
| `nuxt` | https://clerk.com/docs/nuxt/getting-started/quickstart |
| `react-router` | https://clerk.com/docs/react-router/getting-started/quickstart |
| `@tanstack/react-start` | https://clerk.com/docs/tanstack-react-start/getting-started/quickstart |
| `react` | https://clerk.com/docs/react/getting-started/quickstart |
| `vue` | https://clerk.com/docs/vue/getting-started/quickstart |
| `vite` or vanilla JS | https://clerk.com/docs/js-frontend/getting-started/quickstart |
| `express` | https://clerk.com/docs/expressjs/getting-started/quickstart |
| `fastify` | https://clerk.com/docs/fastify/getting-started/quickstart |
| `expo` | https://clerk.com/docs/expo/getting-started/quickstart |
| iOS (Swift) | https://clerk.com/docs/ios/getting-started/quickstart |
| Android (Kotlin) | https://clerk.com/docs/android/getting-started/quickstart |
| Chrome Extension | https://clerk.com/docs/chrome-extension/getting-started/quickstart |

Everything else: https://clerk.com/docs/llms.txt

## Step 6: Ensure clear auth controls are visible

Make sure the app has clear sign-in, sign-up, and signed-in user controls so
the user can create and recognize their first account. Integrate them into
the existing layout, navigation, or landing screen so they feel natural and
polished. If clear auth controls already exist, reuse or adapt them instead
of duplicating them.

For Next.js App Router, use Clerk components from `@clerk/nextjs`:

```tsx
import { SignInButton, SignUpButton, Show, UserButton } from '@clerk/nextjs'

<Show when="signed-out"><SignInButton /><SignUpButton /></Show>
<Show when="signed-in"><UserButton /></Show>
```

Other frameworks use the same component names from their own Clerk package
(`@clerk/vue`, `@clerk/nuxt`, ...).

**Non-Next.js / split-stack.** Vite + React SPA: React SDK wrapped in
`ClerkProvider`, publishable key from `VITE_CLERK_PUBLISHABLE_KEY` (public
by design); vanilla Vite/JS: `@clerk/clerk-js`. A separate backend (Express,
Fastify, or a non-JS API) receives only the `sk_` key in its own env — same
split as the storage table above. For the full SPA + non-Node backend wiring
pattern, see "Field notes" below.

## Step 7: Verify the setup

After `clerk init` completes, run `clerk doctor`. In agent mode,
`doctor --fix` is ignored — read each check's `remedy` field
(`clerk doctor --json`) and apply fixes yourself. Then start the app, confirm
the auth controls are visible, and test the sign-in and sign-up flow.

## Step 8: If using shadcn/ui

If `components.json` exists in the project root and Clerk components are
used: `npm install @clerk/ui`, apply the theme in your provider
(`import { shadcn } from '@clerk/ui/themes'`, then
`<ClerkProvider appearance={{ theme: shadcn }}>`, and add
`@import '@clerk/ui/themes/shadcn.css';` to global CSS.

## Gatekeeping: control who can sign up (CLI, verified)

All via CLI; on PowerShell follow the quoting rules above. Config changes
are live immediately; verify with `clerk config pull` and re-read the field
(dry-run output can be swallowed by redirects).

- Restrict sign-up entirely — patch
  `{"auth_access_control": {"sign_up_mode": "restricted"}}` (enum:
  `public | restricted | waitlist`). `restricted` = strangers cannot sign up
  at all. Combine with invitations:
  `clerk api /invitations -X POST --file body.json --yes` -> invitation
  email sent, status `pending`. "email address is taken" = that person
  already has a Clerk account — no invitation needed.
- Email allowlist alternative:
  `{"auth_access_control": {"allowlist_enabled": true}}`.

### Org auto-enable trap

Dashboard onboarding (especially when enabling social connections/SSO)
silently flips `organization_settings.enabled: true` +
`force_organization_selection: true`, forcing every new signup through an
org-creation wall. Not using orgs? Patch
`{"organization_settings": {"enabled": false}}`.

Single-tenant products often don't need Clerk Organizations at all: if the
app already has its own tenant key + role model, Clerk orgs duplicate
membership plumbing you would still have to map (`org_id` -> your tenant
id). Keep your tenant key as source of truth; revisit orgs only for
self-serve tenant creation or enterprise SAML/SCIM.

## Field notes: split-stack integration (Vite SPA + Python/other backend)

Verified in production (Vite SPA + FastAPI, Windows dev, Cloudflare Pages +
HK Ubuntu box), then stripped via the clean-strip path below on pivot.

### Feature-flag discipline (makes shipping and stripping safe)

Gate the whole integration on env presence: frontend
`VITE_CLERK_PUBLISHABLE_KEY` (Clerk mode iff it starts with `pk_`), backend
`CLERK_DOMAIN` (Clerk verification iff non-empty). With keys absent the app
behaves 100% as before (legacy login path, legacy guard) — shipping is safe
and unwinding is a pure revert.

### Frontend wiring (SPA)

- Conditional `<ClerkProvider publishableKey signInUrl signUpUrl>` wraps the
  existing provider stack.
- A bridge component registers `useAuth().getToken()` into the fetch gateway
  via `setTokenResolver(fn)`; the header builder prefers the resolver token,
  falls back to the legacy localStorage token on empty/error.
- Router guard: Clerk mode -> `<SignedIn>` / `<SignedOut><RedirectToSignIn/>`;
  legacy mode -> existing token guard.
- Embed `<SignIn />` INSIDE the existing branded login page (adapt, don't
  duplicate); dedicated `/sign-up` route with `<SignUp />`;
  `<UserButton afterSignOutUrl="/login">` replaces the sidebar logout button.
- Watch `isSignedIn` -> navigate to the `?redirect_url` param or `/`.

### Backend JWT verification (no official Python SDK)

- Lazy-import `jwt` (PyJWT) + `httpx` so the module imports even if deps are
  missing. Module-level singleton:
  `jwt.PyJWKClient(f"{CLERK_DOMAIN}/.well-known/jwks.json")` (JWKS caching
  built in). Decode with
  `jwt.decode(token, key.key, algorithms=["RS256"], options={"verify_aud":
  False})` — Clerk session tokens have no fixed `aud`.
- Broad except -> return `None` -> the normal 401 path.
- Detect Clerk tokens by shape: starts with `eyJ` and `count(".") == 2`;
  route the check after the demo-token check, before the legacy token-table
  lookup.
- Return the SAME tuple shape as legacy auth so the API layer stays
  untouched.

### Backend API vs Frontend API (cost us a bug)

Secret-key (`sk_`) calls go to `https://api.clerk.com/v1/users/{sub}` with
`Authorization: Bearer sk_...`. Calling `{CLERK_DOMAIN}/v1/users/...` (the
Frontend API host) with an `sk_` silently 404s. Symptom: JIT provisioning
silently degrades to placeholder names. Server-side profile data (email,
`first_name`) lives on api.clerk.com, always.

### JIT provisioning recipe

- Add `clerk_user_id` (String(255), indexed) to the local users table;
  idempotent startup migration via PRAGMA-check + `ALTER TABLE ... ADD
  COLUMN` in the existing schema-ensure hook.
- On first sight of a verified `sub`: re-query by `clerk_user_id` (race
  guard) -> create row with `company_id` = min existing (single-tenant
  default), default role, `name` cascade: Clerk `first_name` -> email
  local-part -> placeholder. One extra Backend API call, only when
  provisioning.

### Clean-strip path

1. Tag HEAD first (`clerk-integration-snapshot-YYYYMMDD`) and push it.
2. `git revert --no-edit <feature-commit> <followup>` (keeps unrelated fix
   commits).
3. Env hygiene BOTH sides (frontend env key file, backend env lines, remote
   box env) BEFORE rebuilding.
4. Verify the live bundle no longer contains `pk_`.

Feature-flag discipline above makes this a clean revert, not surgery.

## Critical rules

- Next.js 15+: `auth()` is async. Always `await auth()`
- `ClerkProvider` goes inside `<body>`, not wrapping `<html>`
- Next.js proxy matchers: `'/__clerk/:path*'` after `'/(api|trpc)(.*)'`
- Never expose `CLERK_SECRET_KEY` in client code
- Use `@clerk/nextjs` in Next.js; `@clerk/clerk-react` is for React SPAs
- Server-side `sk_` calls hit `api.clerk.com`, never the Frontend API host
- Gate integrations on key presence so key absence = exact legacy behavior
- Never guess the app ID (`app_...`); resolve via the env store, or show
  `clerk apps list --json` and ask
- Headless/agent contexts: `CLERK_PLATFORM_API_KEY` instead of browser login;
  `--yes` for mutations, `--json` for output
- Do not read or print existing environment variable files; ask the user for
  any missing non-sensitive configuration

Docs: https://clerk.com/docs/cli https://clerk.com/docs/llms.txt

## After Setup

Have the user sign up as their first test user in the nav. After signup
succeeds and a profile icon appears, congratulate them. If a "Configure your
application" callout appears, tell them to click it. Recommend Organizations
(https://clerk.com/docs/guides/organizations/overview) only for genuinely
multi-tenant products — see the org note under "Gatekeeping" otherwise. Also
point to Components (https://clerk.com/docs/reference/components/overview),
the Dashboard (https://dashboard.clerk.com/), and official skills for deeper
framework patterns (`npx skills add clerk/skills`).
