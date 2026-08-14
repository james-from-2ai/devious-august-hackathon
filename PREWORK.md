# Pre-work

**Do this before the session. Budget 20 minutes.** Most of it is installing
things and waiting for downloads.

Doing this on the day costs you build time, and build time is the whole
event. Four hours goes faster than you think.

At the end you run one command and screenshot one line into the channel.

---

## What you need installed

| Thing | Why | How |
|---|---|---|
| **Python 3.11+** | Runs the service | [python.org](https://www.python.org/downloads/). On Windows, tick **"Add Python to PATH"** in the installer. |
| **git** | Clone the repo | [git-scm.com](https://git-scm.com/downloads) |
| **uv** | Installs dependencies | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| **cloudflared** | Exposes your laptop to the grader | [Cloudflare docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) |
| **ffmpeg** | Block 2 audio bonus only, optional | Windows: `winget install Gyan.FFmpeg` then **reopen your terminal**. Mac: `brew install ffmpeg` |
| **An Anthropic API key** | The service calls Claude | Handed out separately. Do not commit it. |

## Steps

### 1. Clone and install

```bash
git clone https://github.com/james-from-2ai/devious-august-hackathon.git
cd devious-august-hackathon
make setup
```

No `make` on Windows? Run these instead:

```bash
uv sync
copy .env.example .env
```

### 2. Put your key in .env

Open `.env` and set `ANTHROPIC_API_KEY` to the key you were given.

`.env` is gitignored and must stay that way. If you ever paste a key into a
file that is not `.env`, say so in the channel and we will rotate it. This is
not a telling-off, it is just much cheaper than the alternative.

### 3. Check the service runs

```bash
make dev
```

Then in a second terminal:

```bash
curl http://localhost:8000/health
```

You want `{"status":"ok","block":1,"team":"..."}`.

### 4. Check the tunnel works

```bash
make tunnel
```

This starts cloudflared, waits for your public
`https://something.trycloudflare.com` address, **saves it into `.env` for
you, and registers it with the judge automatically**. On the day, that is
the whole flow; today (with no judge running yet) it will say registration
failed, which is expected and fine. The tunnel part working is what you are
checking.

To confirm it reaches your machine, open the printed URL in a browser and
add `/health`.

**The address changes every time cloudflared restarts**, so keep the tunnel
window open, and if it ever closes just run `make tunnel` again; it re-does
everything.

### 5. Run the verifier

```bash
make prework-verify
```

or

```bash
python scripts/prework_verify.py
```

It checks everything above, including making one real call to the Anthropic
API to prove your key works. It prints a single line at the end:

```
PREWORK PASS  all 9 checks green. Screenshot this line into Slack.
```

**Post that screenshot in the channel.** If it says FAIL, it names exactly
which checks failed and what to do. If you are stuck for more than 10
minutes, post the output instead. Someone will have hit the same thing.

---

## Optional, but you will be glad

- Skim `README.md`, especially section 6 on how you lose points and section 7
  on why attempts are limited.
- Open `data/SOURCE.md` and have a look at what is in `data/`. Five minutes
  of familiarity here is worth a lot on the day.
- Read the docstring at the top of `app/handler.py`. It is a list of every
  weakness in the baseline, which is to say a list of where the points are.

## Things that commonly go wrong

**`python` not found on Windows.** You missed the "Add Python to PATH"
checkbox. Re-run the installer and choose Modify.

**`ffmpeg` not found after installing.** Reopen your terminal. PATH changes
do not apply to already-open windows.

**`uv sync` fails on a corporate network.** Usually a proxy or certificate
issue. Post the error, do not spend 30 minutes on it.

**The tunnel URL 404s.** Make sure `make dev` is still running in the other
terminal. The tunnel forwards to your local service; if that is not up, there
is nothing to forward to.

**`make` not recognized on Windows.** Expected. Use the Python commands shown
above, or install make via `winget install GnuWin32.Make`.
