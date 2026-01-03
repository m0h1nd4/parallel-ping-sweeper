#!/usr/bin/env python3
"""
parallel_ping_sweeper.py

Async, cross-platform ICMP ping sweeper for IPv4/IPv6 networks.
- argparse CLI
- configurable timeout
- CSV/JSON output
- IPv4 & IPv6 support
- asyncio concurrency
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import ipaddress
import json
import platform
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PingResult:
    ip: str
    online: bool
    rtt_ms: Optional[float] = None  # optional, not always available via system ping
    error: Optional[str] = None


def _platform_system() -> str:
    return platform.system().lower()


def _have_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _build_ping_command(ip: str, *, count: int, timeout_s: float, prefer_ipv6: bool) -> List[str]:
    """
    Build a system ping command for the current OS.

    We intentionally keep parsing minimal and rely primarily on return codes.
    Timeout handling differs by OS:
      - Windows: -w timeout_ms (per reply)
      - Linux:   -W timeout_s (per reply, integer seconds) or -w deadline_s (overall)
      - macOS:   no -W; use -W timeout_ms (on newer versions) or -t for ttl.
               For macOS, we use -W timeout_ms if available; otherwise fall back
               to a reasonable approach and rely on process timeout.
    IPv6:
      - Windows: ping -6
      - Linux/macOS: ping -6 OR ping6 (depending on distro)
    """
    osname = _platform_system()
    timeout_ms = max(1, int(timeout_s * 1000))
    timeout_s_int = max(1, int(timeout_s))

    # Prefer a single "ping" binary when possible
    ping_cmd = "ping"
    if prefer_ipv6 and osname in ("linux", "darwin") and not _have_cmd("ping"):
        # Highly unusual, but keep safe.
        ping_cmd = "ping6" if _have_cmd("ping6") else "ping"

    if prefer_ipv6 and osname in ("linux", "darwin") and _have_cmd("ping6"):
        # Some systems still provide ping6; we'll use ping with -6 first,
        # but fallback to ping6 in execution if needed.
        pass

    cmd: List[str] = [ping_cmd]

    if prefer_ipv6:
        if osname == "windows":
            cmd += ["-6"]
        else:
            # On Linux/macOS: ping -6 works in most cases
            cmd += ["-6"]

    # Count flag
    if osname == "windows":
        cmd += ["-n", str(count), "-w", str(timeout_ms)]
    else:
        cmd += ["-c", str(count)]
        # Linux supports -W seconds. macOS behavior varies, so we rely on process timeout too.
        # We'll pass something reasonable when possible.
        if osname == "linux":
            cmd += ["-W", str(timeout_s_int)]
        elif osname == "darwin":
            # macOS: -W is timeout in ms on newer versions; older may not support it.
            # We'll include it; if ping exits with usage error, we handle fallback.
            cmd += ["-W", str(timeout_ms)]

    cmd.append(ip)
    return cmd


async def _run_ping_command(cmd: Sequence[str], *, process_timeout_s: float) -> Tuple[int, str]:
    """
    Run ping command asynchronously; return (returncode, stderr_summary).
    stdout is discarded; stderr is captured for diagnostics.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            _, stderr = await asyncio.wait_for(proc.communicate(), timeout=process_timeout_s)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return 124, "timeout"
        return proc.returncode, (stderr.decode(errors="ignore").strip() if stderr else "")
    except FileNotFoundError:
        return 127, f"command not found: {cmd[0]}"
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


async def ping_ip(ip: str, *, timeout_s: float, count: int = 1) -> PingResult:
    """
    Ping a single IP (IPv4 or IPv6). Returns PingResult.

    We primarily use the return code:
      0 => reachable
      else => not reachable or error
    """
    prefer_ipv6 = ":" in ip
    cmd = _build_ping_command(ip, count=count, timeout_s=timeout_s, prefer_ipv6=prefer_ipv6)

    # Add a small cushion for overall process timeout
    process_timeout_s = max(1.0, timeout_s + 0.5)

    rc, err = await _run_ping_command(cmd, process_timeout_s=process_timeout_s)

    # Fallback: if IPv6 on linux/darwin and ping -6 is rejected, try ping6
    osname = _platform_system()
    if prefer_ipv6 and osname in ("linux", "darwin") and rc != 0 and _have_cmd("ping6"):
        if "usage" in err.lower() or "unknown option" in err.lower() or "invalid option" in err.lower():
            cmd2 = ["ping6"] + list(cmd[1:])  # reuse flags where possible
            rc, err = await _run_ping_command(cmd2, process_timeout_s=process_timeout_s)

    online = (rc == 0)
    return PingResult(ip=ip, online=online, error=(None if online else (err or None)))


def iter_hosts(network: str) -> Iterable[str]:
    """
    Yield all host IPs in a given IPv4/IPv6 network in CIDR notation.
    Uses strict=False so users can provide a host address with /mask.
    """
    net = ipaddress.ip_network(network, strict=False)
    # ipaddress hosts() works for both v4/v6
    for ip in net.hosts():
        yield str(ip)


async def scan_network_async(
    network: str,
    *,
    concurrency: int,
    timeout_s: float,
    count: int,
    only_online: bool,
) -> List[PingResult]:
    """
    Async ping sweep with concurrency control.
    """
    sem = asyncio.Semaphore(concurrency)
    results: List[PingResult] = []

    async def _task(ip: str) -> None:
        async with sem:
            res = await ping_ip(ip, timeout_s=timeout_s, count=count)
            if (not only_online) or res.online:
                results.append(res)

    tasks = [_task(ip) for ip in iter_hosts(network)]
    await asyncio.gather(*tasks)
    # Stable ordering by IP address
    def _ip_sort_key(r: PingResult):
        try:
            return ipaddress.ip_address(r.ip)
        except Exception:
            return r.ip
    return sorted(results, key=_ip_sort_key)


def write_json(results: List[PingResult], out_path: Path, *, meta: dict) -> None:
    payload = {
        "meta": meta,
        "results": [
            {"ip": r.ip, "online": r.online, "rtt_ms": r.rtt_ms, "error": r.error}
            for r in results
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(results: List[PingResult], out_path: Path, *, meta: dict) -> None:
    # Store meta as comments at top (common approach)
    lines: List[List[str]] = []
    header = ["ip", "online", "rtt_ms", "error"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        f.write(f"# generated_at={meta.get('generated_at')}\n")
        f.write(f"# network={meta.get('network')}\n")
        f.write(f"# timeout_s={meta.get('timeout_s')}\n")
        f.write(f"# concurrency={meta.get('concurrency')}\n")
        w = csv.writer(f)
        w.writerow(header)
        for r in results:
            w.writerow([r.ip, str(r.online), "" if r.rtt_ms is None else r.rtt_ms, r.error or ""])


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="parallel-ping-sweeper",
        description="Async ICMP ping sweep for IPv4/IPv6 networks with CSV/JSON output.",
    )
    p.add_argument(
        "network",
        help="Target network in CIDR notation, e.g. 192.168.1.0/24 or 2001:db8::/64",
    )
    p.add_argument(
        "-c", "--concurrency",
        type=int,
        default=200,
        help="Number of concurrent ping tasks (default: 200).",
    )
    p.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="Per-host timeout in seconds (default: 1.0).",
    )
    p.add_argument(
        "--count",
        type=int,
        default=1,
        help="Ping echo request count per host (default: 1).",
    )
    p.add_argument(
        "--only-online",
        action="store_true",
        help="Print/export only online hosts (default: false).",
    )
    p.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        default=None,
        help="Write results as JSON to this file path.",
    )
    p.add_argument(
        "--csv",
        dest="csv_path",
        type=Path,
        default=None,
        help="Write results as CSV to this file path.",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output (useful when only exporting).",
    )
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    # Basic validation
    if args.concurrency < 1:
        print("Error: concurrency must be >= 1", file=sys.stderr)
        return 2
    if args.timeout <= 0:
        print("Error: timeout must be > 0", file=sys.stderr)
        return 2
    if args.count < 1:
        print("Error: count must be >= 1", file=sys.stderr)
        return 2

    # Validate network
    try:
        ipaddress.ip_network(args.network, strict=False)
    except ValueError as e:
        print(f"Error: invalid network '{args.network}': {e}", file=sys.stderr)
        return 2

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "network": args.network,
        "timeout_s": args.timeout,
        "concurrency": args.concurrency,
        "count": args.count,
        "platform": platform.platform(),
    }

    results = asyncio.run(
        scan_network_async(
            args.network,
            concurrency=args.concurrency,
            timeout_s=args.timeout,
            count=args.count,
            only_online=args.only_online,
        )
    )

    # Export
    if args.json_path:
        write_json(results, args.json_path, meta=meta)
    if args.csv_path:
        write_csv(results, args.csv_path, meta=meta)

    # Console output
    if not args.quiet:
        online = [r.ip for r in results if r.online]
        print(f"Network: {args.network}")
        print(f"Online hosts: {len(online)}")
        for ip in online:
            print(ip)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
