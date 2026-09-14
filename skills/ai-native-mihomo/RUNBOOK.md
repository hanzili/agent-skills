# RUNBOOK — reproduce an AI-native mihomo stack on any Linux box

Abstract steps; each ends in a checkable completion criterion. Gotchas are
placed where they bite, not in a separate pile. Machine-specific values from
the reference install are in `SKILL.md` § This machine's instantiation.

## 1. Acquire the core binary

- `mihomo` is absent from Arch's official repos (and many distros). Do **not**
  reuse a GUI client's bundled core: FlClash's `FlClashCore` is a modified
  build whose IPC runs over a unix socket — it panics standalone. Get the
  official release from `MetaCubeX/mihomo` (stable tag, `linux-amd64.gz`).
- Fetch via the download doctrine ladder (SKILL.md). `gunzip`, install to
  `~/.local/bin/mihomo`, `chmod +x`.

**Done when**: `<binary> -v` prints `Mihomo Meta vX.Y.Z` (real mihomo, not a
renamed GUI core).

## 2. Acquire a profile

An airport export ("Clash subscription download"), an existing `config.yaml`,
or a subscription URL (then use `proxy-providers` instead of inline
`proxies`). The profile supplies nodes, groups, rules, DNS — you supply the
patches.

"Any full yaml works" is too strong: what matters is that it actually carries
nodes. Identify the shape first (SKILL.md § Ingesting a new profile) — a
provider-only export, a JSON blob and an HTML login page all parse as
*something*, and none of them is a drop-in config.

**Done when**: the file parses and yields a non-empty node list through one of
the known shapes (`proxies` / `proxy-providers` / top-level proxy array) — and
you can say which shape it was.

## 3. Patch security + append TUN

- `external-controller: 127.0.0.1:9090`, `secret: <openssl rand -hex 12>`
  (see Security doctrine — assume the profile ships LAN-open defaults).
- Append (start disabled; enable in step 7 after caps exist):

```yaml
tun:
  enable: false
  stack: gvisor        # pure userspace; `mixed` has dead-TCP failure modes
  auto-route: true
  auto-detect-interface: true
  dns-hijack:
    - any:53
```

**Done when**: `grep -E 'external-controller|secret|stack' config.yaml` shows
localhost + non-empty secret + gvisor.

## 4. Geo data (skip the first-start download stall)

Core boot blocks on `GeoIP/GeoSite` fetch if missing. Reuse any existing clash
install's files (`~/.local/share/com.follow.clash/` for FlClash,
`~/.local/share/io.github.clash-verge-rev*` for Verge) — copy as
`GeoIP.dat` / `GeoSite.dat` beside the config (both case variants is cheap
insurance). Profiles set `geo-auto-update: false` usually; the jsdelivr
`geox-url` in the profile covers later manual updates.

**Done when**: `ls ~/.config/mihomo/*.dat` shows both files.

## 5. Validate config

`mihomo -t -f ~/.config/mihomo/config.yaml -d ~/.config/mihomo`

**Done when**: `configuration file ... test is successful`.

## 6. Rootless service

`~/.config/systemd/user/mihomo.service`:

```ini
[Unit]
Description=Mihomo (Clash Meta) user service
After=network-online.target

[Service]
ExecStart=%h/.local/bin/mihomo -d %h/.config/mihomo
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
```

`systemctl --user daemon-reload && systemctl --user enable --now mihomo`

**Done when**: `systemctl --user is-active mihomo` = active AND
`curl -H "Authorization: Bearer $SECRET" 127.0.0.1:9090/version` returns JSON.

## 7. Verify the proxy path (pre-TUN)

`curl -x http://127.0.0.1:7890 https://www.gstatic.com/generate_204` → 204,
then exit-IP check (`curl -x ... https://ipinfo.io/json`) to confirm a real
airport node answered. Verify **before** TUN so failures are attributable to
the profile, not the TUN layer.

**Done when**: 204 + plausible foreign exit IP.

## 8. TUN (system-wide)

1. One-time privilege grant (Privilege doctrine):
   `pkexec setcap cap_net_admin,cap_net_bind_service=ep ~/.local/bin/mihomo`
   — user types the password in the native dialog. `getcap` confirms.
2. Flip `tun.enable: true`, `systemctl --user restart mihomo`.
3. `ip link` shows the TUN device (`Meta`); plain `curl
   https://www.gstatic.com/generate_204` (no `-x`) → 204.

**Done when**: un-proxied curl hits 204. Everything on the machine now routes
through the core; agents need zero per-app proxy config.

## 9. If TUN blacks out

Work the TUN debugging playbook (SKILL.md) top to bottom — DNS, inbound,
routes, outbound escape — then apply the known fixes (gvisor, interface
binding). Retry once before digging: auto-select health-checks cause transient
`000`s on freshly started stacks.

**Done when**: the decisive test for each layer passes in order.

## 10. Ingest a new profile (staged, never in-place)

Ongoing operation, not a build step. The default is **extract nodes and merge
into the existing known-good shell** — never adopt the incoming file wholesale.

1. Identify the shape (SKILL.md table): full config / provider mapping / proxy
   list / subscription URL / reject.
2. Timestamp a backup of the working config *before* touching anything:
   `cp config.yaml config.yaml.bak-$(date +%Y%m%d-%H%M%S)`.
3. Extract nodes. **Keep local `dns:` / `tun:` / `rules:` /
   `external-controller` / `secret` exactly as they are** — a subscription
   must not get to rewrite security or policy.
4. Merge deterministically: same name + same definition dedupes; same name +
   different definition renames (`<name> (2)`) or is rejected with the conflict
   listed. Never silently overwrite.
5. Write a **candidate** file, not the live one.

**Done when**: you hold a candidate config plus a one-line statement of what
changed (node count, regions, renamed conflicts, anything excluded), and the
previous config still exists as a timestamped backup.

## 11. Verify policy routing (TUN) before believing it works

`auto-route` does **not** install a default route in the main table, so
checking `ip route` alone yields the false conclusion "TUN never took over":

```bash
ip rule show                  # expect a rule pointing at a dedicated table (this machine: 2022)
ip route show table 2022      # expect `default via <tun-ip> dev Meta`
ip link show Meta             # device up
curl -s -o /dev/null -w '%{http_code}' https://www.gstatic.com/generate_204   # NO -x → expect 204
```

When reading `ss`/logs for port `5353`, check *which* socket: mihomo's own DNS
listener versus the mDNS multicast address `224.0.0.251:5353`. Seeing both is
normal — a bare port grep is not evidence of a conflict. Same for
`configure tun interface: device or resource busy` on a **hot reload**: that is
usually the previous TUN not yet released, so re-check after a clean restart
before calling it a real failure.

**Done when**: the rule exists, the dedicated table holds the default via the
TUN device, and an un-proxied curl returns 204.

## 12. Failover acceptance test

This proves the automation, not your typing. Run it once per exit-selection
change.

1. Back up first, and write the blast radius down: "this machine loses internet
   until the selector acts; worst case is one timer interval".
2. Make the current exit fail (e.g. point the in-use node at a black-hole
   address in a *candidate* config) and apply it.
3. **Touch nothing.** Watch `/proxies` `now` plus an un-proxied `curl` on a
   loop until the exit moves on its own.
4. Restore the good config and confirm the exit comes back.

**Done when**: the exit moved with no human action and the logs show the
decision line (`SWITCH ... — <reason>`). For the recovery half, state whether
the cooldown expired naturally or you cleared the state file — a cleared
cooldown is a bypassed mechanism, not a natural recovery.

## Gotchas that bite regardless of machine

- **`pkill -f` self-match**: a `pkill -f <pattern>` whose pattern appears in
  your own command line kills your own shell. `pgrep -x` / exact names first.
- **Caps evaporate on binary replacement**: update = re-run setcap.
- **Mirror resets mid-stream**: pair every mirror fetch with `curl -C -` and a
  retry loop; two failures → human-phone relay.
- **Subscription refresh**: inline-profile workflows get updates by replacing
  the file + `PUT /configs?force=true` **with a JSON body naming the absolute
  path** (`-d '{"path":"/abs/path/config.yaml"}'` — an empty body returns
  `400 Body invalid`); `proxy-provider` workflows by
  `PUT /providers/proxies/<name>`.
- **A file that passes `mihomo -t` is not a loaded config.** Validate the
  candidate on disk, then reload, then confirm through the running core
  (`/proxies` group membership plus a real 204). "The file is correct" and "the
  core is serving it" are different claims.
