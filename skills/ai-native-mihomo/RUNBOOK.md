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

Any full Clash/mihomo yaml works: airport export page ("Clash subscription
download"), an existing `config.yaml`, or a subscription URL (then use
`proxy-providers` instead of inline `proxies`). The profile supplies nodes,
groups, rules, DNS — you supply the patches.

**Done when**: the file parses as YAML and contains `proxies` + `rules`
(or `proxy-providers`).

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

## Gotchas that bite regardless of machine

- **`pkill -f` self-match**: a `pkill -f <pattern>` whose pattern appears in
  your own command line kills your own shell. `pgrep -x` / exact names first.
- **Caps evaporate on binary replacement**: update = re-run setcap.
- **Mirror resets mid-stream**: pair every mirror fetch with `curl -C -` and a
  retry loop; two failures → human-phone relay.
- **Subscription refresh**: inline-profile workflows get updates by replacing
  the file + `PUT /configs?force=true`; `proxy-provider` workflows by
  `PUT /providers/proxies/<name>`.
