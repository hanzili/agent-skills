---
name: ai-native-mihomo
description: >-
  Use when setting up, migrating, or troubleshooting a mihomo (Clash Meta) proxy
  stack in an AI-native way on Linux: headless core + REST API as the agent
  control surface, rootless systemd + TUN via setcap, agent self-heal of network
  failures, or deciding GUI-wrapper vs headless. Also covers the CN-network
  download doctrine (mirrors, human-phone relay) and API-driven proxy control
  (switch nodes, health checks, reload, subscriptions). Not for picking
  airports/subscriptions (human business) or WireGuard-lane VPNs.
version: 1.0.0
author: Liz (lizliz.xyz)
license: MIT
---

# AI-native mihomo proxy stack

## The pattern

Every GUI clash client (FlClash, Clash Verge Rev, ...) is a thin shell over the
**mihomo core**. The AI-native move is to drop the shell and keep the core,
because the core already exposes everything a GUI does as a **REST API**
(`external-controller`). The GUI is a disposable human convenience; the API is
the contract agents build on.

```
airport profile (yaml) ──security patch──▶ config.yaml ◀── mihomo binary (headless)
                                                │                │  (setcap: TUN without root)
                                    systemd --user service   REST API 127.0.0.1:9090
                                                │                │
                                     TUN gvisor + auto-route   agent: curl / jq / MCP
```

Properties that matter:
- **Rootless**: `systemd --user` + file capabilities. No root-owned configs, so
  agents can manage everything without sudo.
- **Declarative**: one yaml = whole state. Reproduce = copy 3 files.
- **Observable**: every dial, rule match, and delay is one GET away.

## Security doctrine

Assume every airport-exported config ships the same landmines until proven
otherwise. Patch on ingestion, before first start:

1. `external-controller: 0.0.0.0:9090` → `127.0.0.1:9090`. With the default
   empty secret this is a LAN-open control API — anyone on the Wi-Fi owns your
   proxy.
2. `secret: ''` → `openssl rand -hex 12`. The secret is not a secret from the
   local agent (it reads the same config file); it is a fence against the LAN.
3. Scan for `allow-lan: true` — keep only if LAN sharing is actually wanted.

## Download doctrine (CN networks)

A ladder; try in order, never grind a rung:

1. **Direct GitHub**: often <50 KB/s. Budget-check first
   (`curl -r 0-1M -o /dev/null -w '%{speed_download}'`), don't commit blind.
2. **Mirror prefix** (`https://ghfast.top/<github-url>`): ~250 KB/s but flaky —
   connections reset mid-stream. Always pair with `curl -C -` resume in a retry
   loop.
3. **Human-phone relay**: the phone downloads in seconds on cellular, then
   LocalSend/AirDrop to the desktop. For anything >20 MB or after two failed
   mirror attempts, hand the URL to the human and move on. The phone is the
   fastest network interface in the room.

## Privilege doctrine

The agent must never touch a password prompt — `sudo` interactively is
unreachable by design, and that is a feature. Ladder:

1. **Design root away**: `systemd --user` service +
   `setcap cap_net_admin,cap_net_bind_service=ep <binary>` gives TUN (and port
   53 bind) without root. Everything stays agent-editable.
2. **One-line human-in-the-loop**: when a privileged one-off is unavoidable,
   run `pkexec <cmd>` — a native auth dialog pops on the user's desktop; they
   type the password there, the agent orchestrates everything around it.
3. `setcap` is lost whenever the binary is replaced (update/reinstall). Re-check
   with `getcap` after every binary change.

## API cookbook

All requests: `curl -H "Authorization: Bearer $SECRET" http://127.0.0.1:9090/...`
(`$SECRET` lives in the config file). Machine-agnostic.

```bash
# self-heal loop: probe → test → switch → re-probe
curl -s -o /dev/null -w '%{http_code}' https://www.gstatic.com/generate_204   # 204 = alive
curl -s "$API/proxies" | jq '.proxies | to_entries[] | select(.value.now) | {k:.key, now:.value.now}'
curl -s "$API/group/$GROUP/delay?url=https%3A%2F%2Fwww.gstatic.com%2Fgenerate_204&timeout=5000" | jq
curl -s -X PUT "$API/proxies/$GROUP" -d '{"name":"<node>"}'
curl -s -X PATCH "$API/configs" -d '{"mode":"rule|global|direct"}'
curl -s -X PUT "$API/configs?force=true"          # reload config from disk
curl -s -X PUT "$API/providers/proxies/$NAME"     # refresh a subscription provider
curl -s "$API/connections" | jq '.connections | length'   # null = inbound dead
curl -s -X POST "$API/restart"
journalctl --user -u mihomo -f                    # logs
```

## TUN debugging playbook

TUN blackout = one broken layer. Isolate with decisive tests, top to bottom;
each test has a binary reading:

| Layer | Decisive test | Reading |
|---|---|---|
| DNS hijack | `getent hosts google.com` | fake-ip `198.18.x.x` = hijack working |
| Inbound to core | curl any site, then `GET /connections` | `null` = traffic never reaches core → stack problem |
| Hijack routes | `ip route show table 2022` | `default via <tun-ip> dev Meta` = routes installed |
| Outbound escape | `curl --interface <phys-iface> https://223.5.5.5` | works = bound sockets escape TUN rules; core must bind its outbounds (`auto-detect-interface: true` / top-level `interface-name`) |

Known fixes, in order of likelihood:
- `tun.stack: mixed` dead on some setups → `gvisor` (pure userspace, always
  works; restart after change).
- Core outbound dials time out while direct rules work → outbound looping into
  the TUN; ensure interface binding (see escape row above).
- Node flapping (some `000`s succeed on retry) → auto-select mid
  health-check culling; retry once before digging.

Known-harmless log noise: UDP QUIC dials `can't resolve ip: couldn't find ip`
(fake-ip + UDP relay limitation; apps fall back to TCP); DNS UDP bind conflict
on 5353 (mDNS owns it); provider health-check "use HTTPS" warning.

## Why the GUIs are disposable — and why full delegation wins

**A GUI client is a renderer over the same REST API.** Switch node, health
check, mode toggle, reload, subscription update — every GUI action maps 1:1 to
an endpoint. Nothing in the GUI is a capability the API lacks; the GUI is a
*rendering preference*, not an interface anyone needs.

Its costs, meanwhile, compound on exactly the machines agents run on:

- **Bundled-library rot**: AppImage/Electron shells carry legacy libstdc++ and
  friends that break against rolling-release mesa (the EGL-crash class).
- **Core lag**: GUIs ship stale cores; the headless path updates the core
  alone, in one file swap.
- **Opaque state**: profiles live in app-private SQLite/prefs stores no agent
  can safely mutate. Headless mihomo's entire state is one yaml.

**Delegation is the modern control loop.** The agent is simultaneously the
first to *feel* a proxy failure (its own fetches time out before a human
notices) and the fastest to act: probe → delay-test → switch → re-probe,
seconds, zero human context switch. A GUI inserts a human into a loop that no
longer needs one. The human exits the loop entirely, remaining only for
privilege one-offs (the `pkexec` dialog) and business decisions (which airport
to pay for). The dashboard's last real job — "is it working?" — is one 204
probe.

**And the product question dissolves.** Wrappers over the API already exist
(`mihomot` with its agent-facing `/skill.md`, `mcp-server-clash-verge`,
`mihomo-mcp`, `mihomo-rs`); the API is the real surface and they are conveni-
ences over it. Any new wrapper has a hard ceiling — a ~200-line disposable
shim. The scaffold's value *is* its disposability, so build-vs-buy is not a
real decision. The stack to beat is `mihomo + REST API`, and nothing on the
market beats it by existing.

**Expiry clause**: this doctrine holds while mihomo stays a stable, actively
maintained core — it ships monthly+, patches CVEs proactively, and has been
the de-facto standard since the original Clash core was archived (2023-11);
its risks are category-level (bus factor, GFW arms race), not fixable by
switching cores. Re-review the whole setup if releases stall for months, the
API surface breaks without deprecation (it has had breaking tweaks, e.g.
`/proxies` behavior changes), or the protocol landscape resets. Keeping one
GUI installed as a cold spare is fine; architect as if it does not exist.

## This machine's instantiation

Concrete instance of the pattern (paths/secret are machine-specific):

| Piece | Value |
|---|---|
| Binary | `~/.local/bin/mihomo` (official v1.19.30, caps via setcap) |
| Config | `~/.config/mihomo/config.yaml` (airport profile + patches, `tun.stack: gvisor`) |
| Geo data | `~/.config/mihomo/{GeoIP,GeoSite}.dat` (reused from FlClash data dir) |
| Service | `~/.config/systemd/user/mihomo.service` → `systemctl --user ...` |
| API | `http://127.0.0.1:9090`, secret: real value in `~/.config/mihomo/config.yaml` (never copy secrets into docs) |
| Proxy port | `127.0.0.1:7890` (mixed, `allow-lan: true` for LAN devices) |
| Legacy GUI | FlClash AppImage extracted at `~/Downloads/squashfs-root`; launch with `LD_LIBRARY_PATH=lib:syslibs` (bundled legacy libstdc++ breaks EGL on rolling mesa — bypass bundled libs, symlink only `libkeybinder-3.0.so.0`) |

Full reproduction steps with per-step completion criteria: [RUNBOOK.md](RUNBOOK.md).
