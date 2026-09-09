# Local conventions: app-ID resolution + credential storage

These are workstation conventions carried by this pack, not Clerk
requirements. Follow them when working on this machine; treat them as
suggestions when adapting the skill elsewhere.

## App ID resolution order (never guess)

`clerk init` must link to the user's Clerk application. The app ID looks
like `app_XXXXXXXXXXXXXXXXXXXXXX`. Resolve it in this order:

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
missing).

## Credential storage split

Mirrors the `~/.agents` convention — `env\` for non-sensitive identifiers,
`secrets\` for anything that must not leak:

| Item | Example | Lives in |
|---|---|---|
| App ID | `app_...` | `~/.agents/env/clerk.env` (public identifier) |
| Publishable key | `pk_test_...` / `pk_live_...` | frontend env (designed to be public; safe in client code) |
| Secret key | `sk_test_...` / `sk_live_...` | `~/.agents/secrets/clerk.env` and/or backend `.env` — never client code, never git |

App IDs and publishable keys are public; secret keys are not.

## Env-file access rule

- Do not go trawling env/secrets files hunting for Clerk values on your own
  initiative.
- Reading a project file the user explicitly pointed you at is fine — e.g.
  updating a `.env.example` they asked for, or checking whether
  `VITE_CLERK_PUBLISHABLE_KEY` / `CLERK_DOMAIN` exist for the feature-flag
  gate.
- Resolve non-sensitive values from `~/.agents/env/clerk.env`; ask the user
  for anything else that is missing. Never print secret values back into
  the conversation.
