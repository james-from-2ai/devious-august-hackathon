#!/usr/bin/env python3
"""Check that this machine is ready for the hackathon. Run this before Friday.

    make prework-verify
    python scripts/prework_verify.py     (if make is not available)

Prints one PASS or FAIL line at the end. Screenshot it into Slack.

Everything here runs locally. There is no scorer to talk to yet; its URL
gets handed out at the start of the session. That is deliberate, so your
pre-work does not depend on anything of mine being up.

Budget about 20 minutes, most of which is installing things.
"""

import os
import shutil
import socket
import subprocess
import sys
import time

REQUIRED_PY = (3, 11)
PORT = 8000
GREEN, RED, YELLOW, DIM, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m")

# Checks that are not required to compete. Block 2 is audio, and the text
# answer stays mandatory there, so a missing ffmpeg costs bonus points at
# worst. It should still be flagged rather than hidden.
OPTIONAL = {"ffmpeg"}

results = []


def record(name, ok, detail="", optional=False):
    results.append((name, ok, detail, optional))
    if ok:
        mark = f"{GREEN}  ok  {RESET}"
    elif optional:
        mark = f"{YELLOW} warn {RESET}"
    else:
        mark = f"{RED} FAIL {RESET}"
    print(f"[{mark}] {name}")
    if detail:
        print(f"         {DIM}{detail}{RESET}")


def check_python():
    v = sys.version_info
    ok = (v.major, v.minor) >= REQUIRED_PY
    record("python 3.11+", ok,
           f"found {v.major}.{v.minor}.{v.micro}" if ok else
           f"found {v.major}.{v.minor}, need {REQUIRED_PY[0]}.{REQUIRED_PY[1]}+")


def check_tool(name, args=("--version",), optional=False, hint=""):
    path = shutil.which(name)
    if not path:
        record(name, False, hint or f"{name} not found on PATH",
               optional=optional)
        return
    try:
        out = subprocess.run([name, *args], capture_output=True, text=True,
                             timeout=30)
        first = (out.stdout or out.stderr or "").strip().splitlines()
        record(name, True, first[0][:80] if first else path, optional=optional)
    except Exception as exc:
        record(name, False, f"{type(exc).__name__}: {exc}", optional=optional)


def check_env_file():
    if not os.path.exists(".env"):
        record(".env exists", False,
               "run `make setup`, or copy .env.example to .env")
        return False
    record(".env exists", True)
    return True


def check_api_key():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        record("anthropic key", False, "python-dotenv missing, run `make setup`")
        return
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key or key.startswith("sk-ant-...") or key == "":
        record("anthropic key set", False, "ANTHROPIC_API_KEY is empty in .env")
        return
    record("anthropic key set", True, f"{key[:11]}...{key[-4:]}")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=os.environ.get("ADVISE_MODEL", "claude-sonnet-4-6"),
            max_tokens=16,
            messages=[{"role": "user", "content": "Reply with the word ready."}],
        )
        text = "".join(b.text for b in msg.content if b.type == "text").strip()
        record("anthropic key works", True, f"model replied: {text[:40]!r}")
    except Exception as exc:
        record("anthropic key works", False,
               f"{type(exc).__name__}: {str(exc)[:120]}")


def port_open(port, timeout=0.5):
    with socket.socket() as s:
        s.settimeout(timeout)
        return s.connect_ex(("127.0.0.1", port)) == 0


def check_service():
    """Start the service if it is not already running, then exercise it."""
    import json
    import urllib.error
    import urllib.request

    started = None
    if not port_open(PORT):
        print(f"{DIM}         starting the service on :{PORT}...{RESET}")
        started = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--port",
             str(PORT), "--log-level", "warning"],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        for _ in range(40):
            if port_open(PORT):
                break
            if started.poll() is not None:
                err = (started.stderr.read() or b"").decode("utf-8", "replace")
                record("service starts", False, err.strip().splitlines()[-1][:150]
                       if err.strip() else "uvicorn exited immediately")
                return
            time.sleep(0.5)

    try:
        if not port_open(PORT):
            record("service starts", False, f"nothing listening on :{PORT}")
            return
        record("service starts", True, f"listening on :{PORT}")

        with urllib.request.urlopen(
                f"http://127.0.0.1:{PORT}/health", timeout=10) as resp:
            body = json.load(resp)
        record("GET /health", body.get("status") == "ok", json.dumps(body))

        payload = json.dumps({
            "question": "When should I sow cotton?",
            "district": "Warangal",
            "language": "en",
        }).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/advise", data=payload,
            headers={"Content-Type": "application/json"})
        start = time.time()
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.load(resp)
        elapsed = time.time() - start

        missing = [k for k in ("answer", "confidence", "sources")
                   if k not in body]
        if missing:
            record("POST /advise schema", False,
                   f"response missing {', '.join(missing)}")
        else:
            record("POST /advise schema", True,
                   f"{elapsed:.1f}s, answer {len(body['answer'])} chars "
                   f"(10s per-question limit in block 1)")
    except urllib.error.HTTPError as exc:
        # main.py returns a shaped JSON body on failure. Reading it turns
        # "HTTP Error 500" into something you can act on, which is usually
        # a missing or rejected API key.
        raw = ""
        try:
            raw = exc.read().decode("utf-8", "replace")
            detail = json.loads(raw)
            msg = f"{detail.get('error', '')}: {detail.get('detail', '')}"
        except Exception:
            msg = raw.strip() or f"HTTP {exc.code}"
        msg = msg.replace("\n", " ")

        # The body does not always survive the subprocess path, so fall back
        # to the checks we already ran. A 500 here is almost always the key.
        key_ok = any(name.startswith("anthropic key") and ok
                     for name, ok, _, _ in results)
        if not key_ok:
            msg += ("  <- expected: the Anthropic key check above did not "
                    "pass. Fix .env first.")
        record("POST /advise", False, msg[:200])
    except Exception as exc:
        record("POST /advise", False, f"{type(exc).__name__}: {str(exc)[:120]}")
    finally:
        if started:
            started.terminate()


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    print("\nPre-work check. Everything runs locally, nothing is scored.\n")

    check_python()
    check_tool("git")
    check_tool("uv", hint="install from https://docs.astral.sh/uv/")
    check_tool("cloudflared", hint=(
        "needed to expose your service to the scorer. "
        "https://developers.cloudflare.com/cloudflare-one/connections/"
        "connect-networks/downloads/"))
    check_tool("ffmpeg", optional=True, hint=(
        "only needed for the block 2 audio bonus. Windows: "
        "winget install Gyan.FFmpeg, then reopen your terminal."))

    if check_env_file():
        check_api_key()

    check_service()

    required_failed = [r for r in results if not r[1] and not r[3]]
    warned = [r for r in results if not r[1] and r[3]]

    print()
    if required_failed:
        print(f"{RED}PREWORK FAIL{RESET}  "
              f"{len(required_failed)} of {len(results)} checks failed: "
              f"{', '.join(r[0] for r in required_failed)}")
        print("\nFix those and run again. Ask in the channel if stuck; that is "
              "what the channel is for.")
        return 1

    suffix = f" ({len(warned)} optional warning)" if warned else ""
    print(f"{GREEN}PREWORK PASS{RESET}  all {len(results)} checks green"
          f"{suffix}. Screenshot this line into Slack.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
