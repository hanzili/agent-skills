---
name: clerk-auth
description: >
  Adds Clerk authentication to a web app via the Clerk CLI, composing with
  Clerk's official AI stack (skills repo, CLI agent mode, MCP server).
  Windows-capable wrapper carrying local conventions: app-ID resolution via
  ~/.agents/env/clerk.env, split credential storage (pk_ frontend, sk_
  secrets), Windows CLI + PowerShell workarounds, Next.js matcher check,
  split-stack field notes (Vite SPA + Python/other backend), CLI
  gatekeeping. Use when the user asks to add Clerk auth, sign-in/sign-up,
  or user management, says "add Clerk to my app", or hits Clerk CLI
  install/login issues on Windows.
---

# Add Clerk Authentication

Set up Clerk authentication with the Clerk CLI. Interactive by default:
present the checklist, pause while the user completes the browser-side login
flow, and continue from CLI output. Before driving the CLI from a script or
sandbox, read references/agent-mode.md.

Reference files — load on demand when their trigger hits, not upfront:
`windows-cli.md` (Windows install/npm failure, PowerShell quoting) ·
`agent-mode.md` (headless/scripted CLI) · `local-conventions.md` (app-ID and
key resolution/persistence) · `split-stack.md` (Vite SPA + non-Node
backend) · `operations.md` (sign-up gatekeeping, invitations, org trap).

## Ecosystem: compose, don't duplicate

Clerk ships a first-class AI-native stack (skills, CLI agent mode, MCP
server, prompts). This pack is a Windows-capable, convention-carrying wrapper
over that stack — not a replacement.

- Framework setup depth, framework patterns, orgs, billing, webhooks,
  testing, mobile -> official skills: `npx skills add clerk/skills`
  (https://github.com/clerk/skills); `clerk init` also offers to install them
- Up-to-date SDK snippets inside AI clients -> `clerk mcp install`
  (also `clerk mcp list`, `clerk mcp uninstall`)
- Non-interactive CLI automation -> references/agent-mode.md; official
  reference: https://github.com/clerk/skills/blob/main/skills/core/clerk-cli/references/agent-mode.md
- Cross-project app-ID resolution, credential storage, Windows CLI reality,
  non-Next.js key routing -> this pack

Ecosystem overview: https://clerk.com/docs/guides/ai/overview

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

Probe first: `command -v clerk && clerk --version`.

- Already installed -> update with `clerk update --yes`.
- Missing -> try the standard install: `npm install -g clerk` (equivalents:
  pnpm / yarn / bun / `brew install clerk/stable/clerk`, or
  `curl -fsSL https://clerk.com/install | bash`). Without installing:
  `npx clerk@latest <command>` / `bunx clerk`.
- On Windows, if the install or `npx clerk` fails with "Unsupported or
  missing platform: win32-x64" or an npm 404 for a platform package, read
  references/windows-cli.md before pinning anything — it carries the
  verified workarounds and a recheck procedure.

## Step 2: Sign in to Clerk

Immediately after installing or updating the CLI, from the project root run
`clerk auth login`. This is the first command after install or update — do
not list apps, ask which Clerk app to use, or run `clerk init` before
authenticating. It opens a browser and binds a localhost callback; pause
while the user completes the flow, then continue from CLI output. If already
signed in, continue to initialization. Verify with `clerk whoami`.

**Sandbox/headless:** `clerk auth login` has no headless branch — it stalls.
Use `CLERK_PLATFORM_API_KEY` for headless automation, or hand the login step
back to the user and wait. Full agent-mode rules: references/agent-mode.md.

## Step 3: Initialize Clerk

Resolve the app ID first — never invent one or reuse another project's.
Short version: check `~/.agents/env/clerk.env` (project-name = app_id
lines), then a pasted personalized SKILL.md, then `clerk apps list --json`
+ ask the user to pick. Full resolution order and persistence rules:
references/local-conventions.md.

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
Non-interactive: `clerk init -y` skips confirmation prompts.

Package-manager signals on a non-empty directory: `pnpm-lock.yaml` -> pnpm;
`yarn.lock` -> yarn; `bun.lock`/`bun.lockb` -> bun; `package-lock.json` ->
npm; none detected -> npm.

**Keyless bootstrap:** an unauthenticated agent on keyless-capable
frameworks defaults to keyless — `clerk init` mints an unclaimed app with
temporary development keys; a later `clerk auth login` claims it
automatically. `--keyless` forces keyless over a stale link; `--login`
forces the authenticated flow.

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
partially supported, follow the official quickstart (it fully scaffolds
Next.js App/Pages Router, React, React Router, Nuxt, TanStack Start, Astro,
Vue, JS/Vite; Expo, Express, Fastify get the SDK plus docs steps).
Quickstart URL pattern:
`https://clerk.com/docs/<slug>/getting-started/quickstart` with slug:
`nextjs`, `react-router` (Remix), `astro`, `nuxt`, `tanstack-react-start`,
`react`, `vue`, `js-frontend` (Vite/vanilla JS), `expressjs`, `fastify`,
`expo` (iOS/Android/Chrome Extension have their own doc sections).
Everything else: https://clerk.com/docs/llms.txt

## Step 6: Ensure clear auth controls are visible

Make sure the app has clear sign-in, sign-up, and signed-in user controls so
the user can create and recognize their first account. Integrate them into
the existing layout; if clear auth controls already exist, reuse or adapt
them instead of duplicating them.

For Next.js App Router, use Clerk components from `@clerk/nextjs`:

```tsx
import { SignInButton, SignUpButton, Show, UserButton } from '@clerk/nextjs'

<Show when="signed-out"><SignInButton /><SignUpButton /></Show>
<Show when="signed-in"><UserButton /></Show>
```

Other frameworks use the same component names from their own Clerk package
(`@clerk/vue`, `@clerk/nuxt`, ...). Vite SPA: React SDK wrapped in
`ClerkProvider`, publishable key from `VITE_CLERK_PUBLISHABLE_KEY` (public
by design); a separate backend receives only the `sk_` key in its own env.
For the full SPA + non-Node backend wiring pattern, read
references/split-stack.md.

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

## Safety rules

- Next.js 15+: `auth()` is async. Always `await auth()`.
- `ClerkProvider` goes inside `<body>`, not wrapping `<html>`.
- Use `@clerk/nextjs` in Next.js; `@clerk/clerk-react` is for React SPAs.
- Secret keys (`sk_`) never enter client code, frontend env, or git.
- Gate integrations on key presence so key absence = exact legacy behavior.
- Server-side `sk_` calls hit `api.clerk.com`, never the Frontend API host
  (details in references/split-stack.md — this cost us a real bug once).
- Do not trawl env/secrets files hunting for Clerk values on your own
  initiative; read only files the user pointed you at, and ask for anything
  missing (references/local-conventions.md).

## After setup

Run the app and have the user create their first account through the UI. If
sign-up needs restricting, invitations are wanted, or the dashboard enabled
orgs by accident, read references/operations.md. For deeper framework
patterns (orgs, billing, webhooks, testing, mobile), install the official
skills: `npx skills add clerk/skills`.

Docs: https://clerk.com/docs/cli https://clerk.com/docs/llms.txt
Dashboard: https://dashboard.clerk.com/
