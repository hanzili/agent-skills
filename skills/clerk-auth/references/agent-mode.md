# Agent mode rules (additive to official docs)

Full official reference:
https://github.com/clerk/skills/blob/main/skills/core/clerk-cli/references/agent-mode.md

This file carries only what this pack adds beyond it.

- Activation priority: `--mode agent` flag > `CLERK_MODE=agent` env >
  stdout not a TTY (piped / agent harness). Force explicitly when the
  harness might look interactive.
- Conventions: `--yes` for mutations, `--json` for structured output. Every
  command also accepts `--input-json '<json|@file|->'` instead of flags.
- In agent mode, mutation confirmations are silently skipped — `--dry-run`
  is the only safety net for `config patch` / `api -X POST` mutations.
- Errors arrive as structured JSON on stderr; exit codes: `0` success,
  `1` runtime error, `2` usage/validation error.
- `clerk auth login` has no headless branch — when unauthenticated it still
  opens a browser and binds a localhost callback, so it stalls in sandboxes.
  Set `CLERK_PLATFORM_API_KEY` for headless automation instead, or hand the
  login step back to the user and wait.
- Sandbox warn-once ("Host-only Clerk state or system capabilities may be
  unavailable in agent mode..."): treat any auth/link/env/config/API failure
  from that invocation as suspect until rerun on the host shell.
