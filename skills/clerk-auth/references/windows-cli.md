# Windows CLI reality + PowerShell workarounds

Load this file only when a specific failure hits (see triggers below).
Facts here were verified against specific CLI versions and will rot —
always re-probe the current state first.

## Probe first (Windows install)

```powershell
clerk --version                         # already installed?
npm view @clerk/cli-win32-x64 versions  # does the platform package exist now?
npm i -g clerk                          # try plain install before any workaround
```

If plain `npm i -g clerk` succeeds, skip the rest of this section. If it
fails with "Unsupported or missing platform: win32-x64" (npm 404 for
`@clerk/cli-win32-x64`), apply a workaround. Same failure via `npx clerk`.

Provenance (last verified 2026-08-28, CLI 3.2.0): the npm publishing matrix
was broken for win32-x64 — 3.2.0 pinned `@clerk/cli-win32-x64: 3.2.0` in
optionalDependencies, but that platform package was never published (E404);
latest win32-x64 stable then was 2.2.0. Re-verify before trusting this.

## Workarounds (verified working at CLI 3.2.0)

1. Pin the older release: `npm i -g clerk@2.2.0` (its win32-x64 platform
   package exists). Older but functional.
2. Install the binary directly:
   https://github.com/clerk/cli/releases/download/v3.2.0/clerk-win32-x64.exe
   (the official install script at `clerk.com/install` has a proper win32
   branch with MINGW/MSYS/CYGWIN detection).

Recheck before pinning: `npm view @clerk/cli-win32-x64 versions` — once a
3.x platform package appears, plain `npm i -g clerk` works again.

## PowerShell quoting and payloads

- Trigger: a `--json` / `--input-json` flag fails with quotes stripped —
  confusingly, or silently under `2>$null`.
- `clerk config patch --json '{\"k\": \"v\"}'` works. Plain single-quoted
  `'{...}'` gets its quotes stripped by PowerShell native arg passing.
- POST bodies: write a temp file, then
  `clerk api /invitations -X POST --file body.json --yes`.
- `clerk env pull --app <id> --file tmp.env`, then parse locally. Bonus: the
  publishable key base64-decodes (strip the `pk_test_` prefix, base64url
  decode, strip a trailing `$`) to the instance's FAPI domain — a
  dashboard-free source for `CLERK_DOMAIN`.
