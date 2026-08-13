.PHONY: setup dev check tunnel register submit prework-verify

# Windows without make: every target below is a thin wrapper over
# scripts/scorer_cli.py, so you can run the python command directly.
# See README.md for the exact equivalents.

setup:
	uv sync
	@test -f .env || cp .env.example .env
	@echo "Edit .env and put your ANTHROPIC_API_KEY in it."

dev:
	uv run uvicorn app.main:app --reload --port 8000

# Free and unlimited. Never touches your attempt budget.
check:
	uv run python scripts/scorer_cli.py check

tunnel:
	cloudflared tunnel --url http://localhost:8000

register:
	uv run python scripts/scorer_cli.py register

# Pre-flights, shows attempts remaining, then asks before spending one.
submit:
	uv run python scripts/scorer_cli.py submit

prework-verify:
	uv run python scripts/prework_verify.py
