# linux-diag — Network diagnostics dispatcher

This directory hosts `lzt-netdiag`, a thin bash dispatcher over four network
diagnostic tools that are not packaged for Debian Forky upstream
(`speedtest-cli`, `iperf3`, `mtr`, `traceroute`) — instead, they run inside an
Arch Linux **distrobox** called `arch-loust` and are exported back to the host
PATH via `distrobox-export --bin`.

## Why a dispatcher instead of calling the wrappers directly?

| Concern | Without dispatcher | With dispatcher |
|---|---|---|
| Memory | `distrobox enter arch-loust -- speedtest-cli --simple` | `lzt-netdiag st --simple` |
| Tab-completion | 4 distinct command names | 1 canonical name with 6 subcommands |
| Auto-detection of local NICs | Manual `iw dev`, `ip route` | `lzt-netdiag host` |
| Tool availability | Each wrapper is independent | Pre-flight check fails fast with actionable error |

## Subcommands

| Subcommand | Pass-through to | Notes |
|---|---|---|
| `st`  | `speedtest-cli` | Accepts all native flags (`--simple`, `--json`, `--list`, `--server N`, etc.) |
| `i3`  | `iperf3`         | Accepts all native flags (`-c`, `-u`, `-t`, `-j`, `-b`, etc.) |
| `mtr` | `mtr`            | Accepts all native flags (`-c`, `-w`, `-J`, etc.) |
| `trace` | `traceroute`   | Accepts all native flags |
| `host` | host sysfs + iproute2 | Local-only nic auto-detect (interfaces, default route, wireless quality, DNS resolvers, gateway ping) |
| `version` | all four binaries | One-liner with versions + container name |
| `-h`, `--help`, `help`, no args | — | Extracted from script doc block via sed |

## Setup (one-time)

```sh
# 1. Create the distrobox (Arch Linux base; speedtest-cli, iperf3, mtr are in
#    upstream Arch; traceroute is bundled with `iputils` or installed as a
#    separate package depending on image age).
distrobox create -i archlinux:latest -n arch-loust
distrobox enter arch-loust -- sudo pacman -S speedtest-cli iperf3 mtr

# 2. Export each binary to the host PATH
distrobox enter arch-loust -- distrobox-export \
    --bin /usr/bin/speedtest-cli \
    --bin /usr/bin/iperf3 \
    --bin /usr/bin/mtr \
    --bin /usr/bin/traceroute \
    --export-path ~/.local/bin/

# 3. Drop this directory on the host
install -m 0755 lzt-netdiag ~/.local/bin/lzt-netdiag
```

## Usage examples

```sh
# Bandwidth + latency in compact form
lzt-netdiag st --simple

# Raw JSON for scripting
lzt-netdiag st --json | jq '.download.bandwidth, .ping'

# Bandwidth to a specific server for N seconds
lzt-netdiag i3 -c 192.168.1.64 -t 30

# UDP stream at 1 Mb/s for 5 seconds
lzt-netdiag i3 -c 192.168.1.64 -t 5 -u -b 1M

# Path MTU / packet-loss diagnostic
lzt-netdiag mtr 192.168.1.64 -c 30 -w

# JSON mtr for log ingest
lzt-netdiag mtr -J 192.168.1.64

# What hop is the bottleneck?
lzt-netdiag trace 1.1.1.1

# Local NIC inventory + gateway reachability
lzt-netdiag host

# Confirm all 4 binaries are exported and which container they're in
lzt-netdiag version
```

## Exit codes

| Code | Meaning |
|---|---|
| `0`  | OK |
| `1`  | Argument / tool / container error (with stderr message) |
| `127` | Tool missing from host PATH (re-run `distrobox-export`) |
| Other | Pass-through from underlying tool (e.g. `mtr` returns its own codes) |

## Why is this in NetBoozt?

The NetBoozt platform targets Windows users (see `runner-strategy.md`), but the
**build & maintain** workflow runs on Debian. When validating a release that
claims e.g. "improved connection-resilience on lossy networks", we need to
reproduce typical home-network pathologies — packet loss, MTU black holes,
slow DNS, asymmetric bandwidth — without polluting the host distro with
Arch-only packages. The dispatcher pattern lets the maintainer reproduce
field issues deterministically while keeping the host clean.

## Why a single-file script?

- Zero dependencies beyond `bash`, `distrobox`, `iproute2`, `procps`.
- Trivial to audit (160 lines).
- Single source of truth — `lzt-netdiag --help` reads the same doc-block that
  this README documents, so they cannot drift.

## Customization

The container name is configurable via `LZT_ARCH_LOUST` env var if you need
multiple coexisting arch distroboxes (e.g. `LZT_ARCH_LOUST=arch-test`).

## See also

- `runner-strategy.md` — Why builds use `windows-latest` (VPS runner is Linux-only)
- `tools/` — Other helper scripts committed to NetBoozt
