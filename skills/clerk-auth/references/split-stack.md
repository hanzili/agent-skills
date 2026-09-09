# Split-stack integration (Vite SPA + Python/other backend)

Field notes, verified in production (Vite SPA + FastAPI, Windows dev,
Cloudflare Pages + HK Ubuntu box), then stripped via the clean-strip path
below on pivot.

## Feature-flag discipline (makes shipping and stripping safe)

Gate the whole integration on env presence: frontend
`VITE_CLERK_PUBLISHABLE_KEY` (Clerk mode iff it starts with `pk_`), backend
`CLERK_DOMAIN` (Clerk verification iff non-empty). With keys absent the app
behaves 100% as before (legacy login path, legacy guard) — shipping is safe
and unwinding is a pure revert.

## Frontend wiring (SPA)

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

## Backend JWT verification (no official Python SDK)

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

## Backend API vs Frontend API (cost us a bug)

Secret-key (`sk_`) calls go to `https://api.clerk.com/v1/users/{sub}` with
`Authorization: Bearer sk_...`. Calling `{CLERK_DOMAIN}/v1/users/...` (the
Frontend API host) with an `sk_` silently 404s. Symptom: JIT provisioning
silently degrades to placeholder names. Server-side profile data (email,
`first_name`) lives on api.clerk.com, always.

## JIT provisioning recipe

- Add `clerk_user_id` (String(255), indexed) to the local users table;
  idempotent startup migration via PRAGMA-check + `ALTER TABLE ... ADD
  COLUMN` in the existing schema-ensure hook.
- On first sight of a verified `sub`: re-query by `clerk_user_id` (race
  guard) -> create row with `company_id` = min existing (single-tenant
  default), default role, `name` cascade: Clerk `first_name` -> email
  local-part -> placeholder. One extra Backend API call, only when
  provisioning.

## Clean-strip path

1. Tag HEAD first (`clerk-integration-snapshot-YYYYMMDD`) and push it.
2. `git revert --no-edit <feature-commit> <followup>` (keeps unrelated fix
   commits).
3. Env hygiene BOTH sides (frontend env key file, backend env lines, remote
   box env) BEFORE rebuilding.
4. Verify the live bundle no longer contains `pk_`.

Feature-flag discipline above makes this a clean revert, not surgery.
