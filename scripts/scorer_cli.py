#!/usr/bin/env python3
"""Talk to the scorer. The CLI is the interface; there is no web UI.

    python scripts/scorer_cli.py check      free, unlimited schema check
    python scripts/scorer_cli.py register   tell the scorer your tunnel URL
    python scripts/scorer_cli.py submit     spends one attempt, asks first

`submit` will not spend an attempt until your local service answers, the
schema check passes, and you type y. A wasted attempt because cloudflared
dropped is the most demoralizing way to lose points and it is entirely
preventable.
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

SCORER = os.environ.get("SCORER_URL", "").rstrip("/")
TEAM = os.environ.get("TEAM_NAME", "")
# Your team name IS your credential. TEAM_TOKEN only exists as an override
# for events run in strict mode, and can stay empty.
TOKEN = os.environ.get("TEAM_TOKEN", "") or TEAM
ENDPOINT = os.environ.get("ENDPOINT_URL", "").rstrip("/")
# Where your machine listens locally. Hardcoding 8000 here sent "local
# service is not answering" to anyone running on another port while their
# tunnel was perfectly healthy. Set PORT (or LOCAL_URL) in .env if you moved.
LOCAL = (os.environ.get("LOCAL_URL", "").rstrip("/")
         or f"http://localhost:{os.environ.get('PORT', '8000')}")

# Names go on the leaderboard. Sent on register and again on every run, so a
# pair who fills this in late still gets credited rather than showing up as a
# bare team id for the rest of the day.
PARTICIPANTS = [p.strip() for p in
                os.environ.get("PARTICIPANTS", "").split(",") if p.strip()]

RED, GREEN, YELLOW, DIM, RESET = (
    "\033[31m", "\033[32m", "\033[33m", "\033[2m", "\033[0m")


def die(msg):
    print(f"{RED}{msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def require_env():
    missing = [k for k, v in
               [("SCORER_URL", SCORER), ("TEAM_NAME", TEAM)] if not v]
    if missing:
        die(f"Missing in .env: {', '.join(missing)}")


def auth():
    return {"Authorization": f"Bearer {TOKEN}"}


def payload():
    """The body every scorer call sends. One place, so names never get lost."""
    return {"team": TEAM, "endpoint_url": ENDPOINT, "participants": PARTICIPANTS}


def local_health():
    try:
        r = httpx.get(f"{LOCAL}/health", timeout=5)
        r.raise_for_status()
        return True, r.json()
    except Exception as exc:
        return False, str(exc)


def cmd_check():
    require_env()
    if not ENDPOINT:
        die("ENDPOINT_URL is empty. Run `make tunnel`, then put the URL in .env.")
    r = httpx.post(f"{SCORER}/check", headers=auth(),
                   json=payload(), timeout=60)
    body = r.json()
    if body.get("pass"):
        print(f"{GREEN}CHECK PASS{RESET}  schema conforms, "
              f"{body.get('latency_ms', '?')}ms")
        return 0
    print(f"{RED}CHECK FAIL{RESET}  {body.get('error', 'unknown')}")
    if body.get("detail"):
        print(f"{DIM}{body['detail']}{RESET}")
    return 1


def cmd_register():
    require_env()
    if not ENDPOINT:
        die("ENDPOINT_URL is empty. Run `make tunnel` first.")
    r = httpx.post(f"{SCORER}/register", headers=auth(),
                   json=payload(), timeout=30)
    r.raise_for_status()
    body = r.json()
    print(f"{GREEN}Registered{RESET} {TEAM} -> {ENDPOINT}")
    # Remaining, not budget: this line prints on every tunnel restart, and
    # "6" after you have spent three reads as three free attempts.
    b1 = body.get("block1_remaining", body.get("block1_budget", "?"))
    b2 = body.get("block2_remaining", body.get("block2_budget", "?"))
    print(f"Attempts remaining: block 1 {b1}, block 2 {b2}")
    return 0


def render_run(body):
    """Pretty-print a /run result. Categories only, never gold answers."""
    prev = body.get("previous_score")
    delta = "" if prev is None else f"  (prev {prev:g})  {body['total_score'] - prev:+g}"
    print(f"\nRUN #{body['run_id']}  {body['team']}  block {body['block']}  "
          f"score {body['total_score']:g}/{body['max_score']:g}{delta}")
    print(f"Attempts: {body['attempts_remaining']} of {body['attempts_budget']} "
          f"remaining\n")

    for q in body["results"]:
        verdict = "PASS" if q["category"] == "PASS" else "FAIL"
        color = GREEN if verdict == "PASS" else RED
        detail = q["reason"] if q["category"] == "PASS" else \
            f"{q['category']}: {q['reason']}"
        bonus = f"  {YELLOW}+{q['audio_bonus']:g} audio{RESET}" \
            if q.get("audio_bonus") else ""
        print(f"{q['question_id']}  {color}{verdict}{RESET}  "
              f"{q['score']:g}/10{bonus}   {detail}")
    if body.get("audio_max"):
        print(f"\n{YELLOW}Chatbot {body['total_score']:g}/100 · "
              f"Audio {body.get('audio_score', 0):g}/{body['audio_max']} · "
              f"TOTAL {body.get('combined_score', body['total_score']):g}"
              f"/{body.get('combined_max', 130)}{RESET}")

    fails = body.get("category_counts", {})
    if fails:
        print("\nCategories failed: " +
              ", ".join(f"{k} {v}" for k, v in fails.items()))
    print(f"p95 latency {body['p95_latency_ms'] / 1000:.1f}s"
          + (f" | cost/query ${body['cost_per_query']:.3f}"
             if body.get("cost_per_query") is not None else ""))
    if body.get("safety_fails"):
        print(f"{RED}SAFETY fails: {body['safety_fails']}{RESET}")
    return 0


def cmd_submit():
    require_env()
    if not ENDPOINT:
        die("ENDPOINT_URL is empty. Run `make tunnel` first.")
    if not PARTICIPANTS:
        die("PARTICIPANTS is empty in .env, and the leaderboard shows names, "
            "not team ids.\nAdd both of you, for example:\n"
            "    PARTICIPANTS=Ada Lovelace, Grace Hopper\n"
            "then run `make submit` again. Nothing was spent.")

    ok, info = local_health()
    if not ok:
        die(f"Local service is not answering on {LOCAL}: {info}\n"
            f"Start it with `make dev` before submitting.")
    print(f"{GREEN}local /health ok{RESET}  block {info.get('block')}")

    if cmd_check() != 0:
        die("Schema check failed. Fix that before spending an attempt.")

    status = httpx.get(f"{SCORER}/attempts", headers=auth(),
                       params={"team": TEAM}, timeout=30).json()
    used, budget = status["used"], status["budget"]
    if used >= budget:
        die(f"No attempts left ({used}/{budget} used).")

    print(f"\n{YELLOW}This will consume attempt {used + 1} of {budget}."
          f"{RESET} Continue? [y/N] ", end="")
    if input().strip().lower() != "y":
        print("Cancelled. No attempt spent.")
        return 0

    r = httpx.post(f"{SCORER}/run", headers=auth(),
                   json=payload(), timeout=600)
    if r.status_code == 429:
        die(f"Out of attempts: {r.json().get('detail', '')}")
    if r.status_code == 403:
        die(r.json().get("detail", "The challenge is over!"))
    if r.status_code == 400:
        # The judge refused before running anything; its message says why
        # and what to fix, so show it instead of a traceback.
        die(f"The judge declined to run: {r.json().get('detail', r.text)}")
    r.raise_for_status()
    return render_run(r.json())


COMMANDS = {"check": cmd_check, "register": cmd_register, "submit": cmd_submit}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"usage: {sys.argv[0]} {{{'|'.join(COMMANDS)}}}", file=sys.stderr)
        return 2
    return COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
