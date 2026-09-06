# Contributing to Bug Ledger MCP

Thanks for helping. This guide covers setup, how testing works here, the day-to-day workflow, and how to add the three things people add most: a tool, a migration, a Semgrep rule.

## Layout in one minute

```
shared/      language-neutral truth: schema SQL, Semgrep rules + fixtures, the /logbug prompt
python/      the server (canonical implementation) → PyPI
scripts/     sync.py copies shared/ into the Python package before a build
artifacts/   brand assets in artifacts/logo (mark, wordmark light/dark, app icon, PNG exports) and diagrams
```

`python/` is the reference implementation. A future TypeScript port mirrors its code and tests, so keep behaviour in Python explicit and tested.

## Setup

You need [uv](https://docs.astral.sh/uv/) and git. uv installs the right Python for you.

```sh
git clone git@github.com:xajeel/bugledger-mcp.git
cd bugledger-mcp/python
uv sync                 # installs the package, pytest, and ruff into .venv
cd ..
uvx pre-commit install  # lint + format on commit, tests on push
```

Run the server from the checkout with `uv run --directory python bugledger-mcp`. It waits silently on stdin; that is a stdio MCP server working. Point Claude Code at it with:

```sh
claude mcp add bugledger -- uv run --directory /abs/path/to/bugledger-mcp/python bugledger-mcp
```

## Testing: who runs what

The model is the same one large open-source projects use (PyTorch, FastAPI, pydantic): **fast checks on your machine for feedback, CI as the gate that decides what merges.**

| Where | What runs | When | Why |
|---|---|---|---|
| Your machine | `ruff check` + `ruff format` | every commit (hook) | style problems never reach review |
| Your machine | `pytest` (~3 s, 93 tests) | every push (hook), and whenever you want | you find out in seconds, not after a CI round-trip |
| CI (GitHub Actions) | lint · pytest on Python 3.10, 3.11, 3.12, 3.13, 3.14 · Semgrep rule self-test · package build · installed-wheel smoke run | every pull request and every push to `main` | covers versions and environments you do not have; `main` requires all of it green |

Your local run is a convenience. CI is the source of truth. A PR with red CI is not reviewed until it is green.

```sh
cd python
uv run pytest                 # whole suite
uv run pytest tests/test_e2e.py -q   # one file
uv run pytest -k search       # by name
uv run ruff check . && uv run ruff format .
uv run --group rules semgrep --test ../shared/rules --metrics=off   # rule pack self-test
```

### How the tests are layered

| Layer | Files | What they cover |
|---|---|---|
| Schema | `tests/test_*_bug.py`, `test_get_patterns.py` | pydantic validators: what the agent may and may not send |
| Repository | same files, `memory_db()` | SQL against an in-memory SQLite with **every** migration applied (`tests/helpers.py`) |
| Tool | `test_record_bug.py`, `test_get_guardrails.py`, … | the tool functions, with `git` and the filesystem faked |
| End-to-end | `tests/test_e2e.py` | the real server object driven by an in-memory MCP client: handshake, tool list, annotations, parameter descriptions, a full record → retrieve → search → resolve → update → delete lifecycle |

Rules every test follows:

- **Hermetic.** `tests/conftest.py` points `BUGLEDGER_HOME` at a temp dir, so no test can touch a real `~/.bugledger`. Use `tmp_path` when you need a file.
- **No network, no real git.** Monkeypatch `subprocess.run` (see `test_record_bug.py`).
- **Deterministic.** No sleeps, no clocks, no ordering assumptions beyond what the SQL guarantees.
- **A new feature ships with tests at the layer it touches**, plus one end-to-end assertion if it changes what the agent sees (a tool, a parameter, a return field).

## Workflow

1. Branch from `main`: `<your-name>/<topic>`, for example `xajeel/search-stemming`.
2. Keep commits small and use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `test:`, `docs:`, `ci:`, `chore:`, `style:`. Add a scope when it helps: `feat(search): …`.
3. Push. The pre-push hook runs the suite; CI runs the rest.
4. Open a PR against `main`. Describe the user-visible change and how you verified it.
5. One approval and green CI to merge. Squash or rebase, no merge commits into feature branches.

PR checklist:

- [ ] Tests added or updated at the right layer
- [ ] `uv run pytest` passes locally
- [ ] If `shared/` changed: `python scripts/sync.py` was run and the change is covered by a test
- [ ] If the agent-facing surface changed (tool, parameter, error text, prompt): README tool table and `test_e2e.py` updated
- [ ] No new dependency without a sentence in the PR on why

## How to add things

### A tool

1. `python/src/bugledger_mcp/schema/<name>.py`: a pydantic model with the validation rules. Error texts live in `utils/constant.py`; they are agent-facing UX, so write them as instructions the agent can act on.
2. `python/src/bugledger_mcp/tools/<name>.py`: the function. Every parameter gets a description. Required parameters use `Annotated[type, Field(description=...)]`; optional ones use `type | None = Field(default=None, description=...)` (the second form keeps descriptions visible on Python 3.10).
3. Register it in `tool_registry.py` with the right `ToolAnnotations` (read-only, idempotent, destructive).
4. Tests: schema, repository if it touches SQL, and an end-to-end call in `test_e2e.py`.
5. Add a row to the tool table in both READMEs.

### A migration

Add `shared/schema/00N_<name>.sql` with the next number. Never edit an existing migration; ledgers in the wild have already applied it. `run_migrations` applies files in name order and records progress in `PRAGMA user_version`. `tests/helpers.py` applies every file, so repository tests cover the new one automatically. Run `python scripts/sync.py` before starting the server locally.

### A Semgrep rule

Rules are the product's free "wow" and also how it gets uninstalled if they are noisy. Each rule must earn its place.

1. `shared/rules/<name>.yaml` with `bugledger-stacks: [python]` (or `[all]`) in `metadata`. `get_guardrails` filters on that field.
2. A fixture next to it, `shared/rules/<name>.py` / `.js`, with `# ruleid: <id>` above every line that must match and `# ok: <id>` above lines that must not.
3. Severity policy: `ERROR` blocks pull requests, so use it only for high-confidence security findings (injection, secrets, unsafe deserialization). Everything else is `WARNING` (advisory, printed, never fails CI).
4. Verify: `uv run --group rules semgrep --validate --config ../shared/rules --metrics=off` and `… --test ../shared/rules`.
5. Run the pack on a healthy real project (a few installed site-packages libraries work well) and put the hit count in the PR. A rule that fires on healthy code gets fixed or cut.

## Releasing (maintainers)

The version is hand-edited in exactly one place: `version` in `python/pyproject.toml`. `python/uv.lock` mirrors it and everything else derives from it at runtime (`bugledger_mcp.__version__` reads the installed package metadata, which feeds the MCP `serverInfo.version` and the stderr startup line). PyPI never accepts the same version twice, so every release needs a bump.

1. On a branch: `cd python && uv version --bump patch` (or `minor` / `major`). This updates `pyproject.toml` and `uv.lock` together. Commit as `chore(release): X.Y.Z`, open a PR, let CI pass, merge to `main`.
2. Publish a GitHub release with tag `vX.Y.Z` targeting `main` (GitHub UI, or `gh release create vX.Y.Z --target main --generate-notes`). Publishing the release is the only trigger for the `Publish` workflow; pushes, tags alone, and manual runs never upload.
3. The workflow refuses to continue if the tagged commit is not on `main` or the tag is not `v` + the pyproject version. Then it runs the tests, builds, checks the wheel, smoke-runs it, uploads with the `PYPI_API_TOKEN` repository secret, and finally installs `bugledger-mcp==X.Y.Z` from PyPI with `uvx` to prove the release is live.

If step 3 fails before the upload, fix the cause, delete the release and tag, and publish again. If it fails after the upload (the PyPI verify step), the version is already taken: bump again.

## Reporting bugs

Open an issue with the symptom, what you expected, your OS and Python version, and the last lines the server printed to stderr. If you fixed it yourself and you use Bug Ledger, you know what to do: `/logbug`.
