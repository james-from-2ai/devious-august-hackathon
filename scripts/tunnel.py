#!/usr/bin/env python3
"""Start the tunnel, update .env, and register with the judge. One command.

    make tunnel        (or: python scripts/tunnel.py)

Why this exists: cloudflared prints a new random URL every time it starts,
buried in a wall of log output. The manual flow was copy the URL, paste it
into .env, remember to re-run register. Forgetting any step leaves the judge
knocking on a dead address, and that is the single most predictable way for
a team to lose an attempt. This script does all three steps and stays
running; keep the window open.

If cloudflared is not installed, it says exactly how to install it and
exits, rather than stack-tracing.
"""

import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")
LOCAL = "http://localhost:8000"

URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")

GREEN, YELLOW, RED, DIM, RESET = (
    "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m")


def update_env(url):
    """Set ENDPOINT_URL in .env, touching nothing else in the file."""
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    replaced = False
    for i, line in enumerate(lines):
        if line.strip().startswith("ENDPOINT_URL="):
            lines[i] = f"ENDPOINT_URL={url}"
            replaced = True
    if not replaced:
        lines.append(f"ENDPOINT_URL={url}")
    with open(ENV_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def register():
    """Re-register with the scorer so the judge has the fresh address."""
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "scorer_cli.py"),
         "register"], cwd=ROOT)
    return result.returncode == 0


def main():
    if not shutil.which("cloudflared"):
        print(f"{RED}cloudflared is not installed.{RESET}\n"
              "  Windows:  winget install Cloudflare.cloudflared\n"
              "  Mac:      brew install cloudflared\n"
              "Then CLOSE this terminal, open a new one, and run "
              "`make tunnel` again.\n(PATH changes do not reach terminals "
              "that are already open.)", file=sys.stderr)
        return 1

    print(f"Starting the tunnel to {LOCAL} ...")
    print(f"{DIM}Keep this window open. Closing it disconnects your machine "
          f"from the judge.{RESET}\n")

    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", LOCAL],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1)

    url = None
    try:
        for line in proc.stdout:
            match = URL_RE.search(line)
            if match and not url:
                url = match.group(0)
                update_env(url)
                print(f"\n{GREEN}Your public address:{RESET}  {url}")
                print("Saved to .env as ENDPOINT_URL.")
                print("Telling the judge...\n")
                if register():
                    print(f"\n{GREEN}All set.{RESET} The judge can reach "
                          f"your machine. Leave this running.\n"
                          f"{DIM}(If this window closes, run `make tunnel` "
                          f"again; it re-does everything.){RESET}\n")
                else:
                    print(f"\n{YELLOW}Tunnel is up but registration "
                          f"failed.{RESET} Check SCORER_URL and TEAM_TOKEN "
                          f"in .env, then run `make register` yourself.\n")
            elif not url:
                # Show cloudflared's own output until the URL appears, so a
                # failure to connect is visible rather than a silent hang.
                sys.stdout.write(f"{DIM}{line}{RESET}")
        return proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print(f"\nTunnel stopped. Your old address is now dead: run "
              f"`make tunnel` again before the next submit.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
