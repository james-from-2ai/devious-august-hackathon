# Quickstart, with Claude Code doing the typing

You never need to run a git or terminal command yourself. Claude Code is
your farmhand: paste each message below into it, in order, and it will run
the commands, watch the output, and fix what breaks.

If anything confuses you at any point, ask Claude Code to explain it. That
is not cheating; that is the workflow.

## 1. Before the event: get set up

Open Claude Code in an empty folder and paste:

```
Clone https://github.com/james-from-2ai/devious-august-hackathon and set it up.
Create the .env file from .env.example. I will paste my Anthropic API key next.
Set PARTICIPANTS to our two names: "NAME ONE, NAME TWO".
Then run the pre-work check (scripts/prework_verify.py) and help me fix
anything that fails until it prints PREWORK PASS.
```

When it prints `PREWORK PASS`, screenshot that line into Slack. Done: you
are ready for the day.

## 2. At the start of the hack: switch your machine on

The Slack channel gives you two values at 10:30, `SCORER_URL` and
`TEAM_TOKEN`. Then paste:

```
Add these two lines to .env (I am pasting the values from Slack):
SCORER_URL=... and TEAM_TOKEN=...
Then start my advice machine (make dev) and keep it running, start the
tunnel (make tunnel) and keep that running too, and confirm both worked:
/health answers, and the tunnel registered us with the judge.
```

The tunnel gives your machine a public address (that address is your
**endpoint**, the door the judge knocks on) and registers it for you
automatically.

## 3. The middle of the day: get your bearings

```
Read data/SOURCE.md, examples/calibration.jsonl, and app/handler.py.
Explain in plain words: what does our machine currently do when a question
arrives, what data does it have available to it, and how does the judge
score answers? Do not change any code yet.
```

Where you go from here is the hackathon. You get 6 scored attempts, the
judge never tells you the right answer, and how you spend the time between
attempts is the whole game. That part is yours to figure out.

## 4. When your local score looks good: face the judge

```
Run make check and show me the result. If it is green, talk me through
what make submit will do, then run it. Afterwards, read the per-question
feedback with me and tell us which failure category is costing us the most
points and why.
```

`make check` is free and unlimited. `make submit` spends one of your 6
attempts and puts your names and score on the leaderboard.

## The two rules that save the day

- **When anything errors, paste the whole error into Claude Code** and ask
  it to fix it. Stuck for more than 10 minutes: post in Slack.
- **Keep the two running windows open** (your machine and your tunnel).
  If the tunnel window dies, `make tunnel` again; it re-does everything.
