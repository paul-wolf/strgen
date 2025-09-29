# Repository Guidelines

## Project Structure & Module Organization
- Core package is `strgen/`; `__init__.py` exports the generator plus `countries.py` data.
- Tests reside in `strgen/tests.py` so runtime and coverage logic evolve together; keep fixtures lightweight because Hypothesis already stresses edge cases.
- Docs live in `docs/` with a Sphinx `Makefile`; commit `_build/` output only on tagged releases.
- Repo root holds tooling (`cover.sh`, `setup.py`, `pyproject.toml`, `requirements.txt`); update when packaging assumptions change.

## Build, Test, and Development Commands
- Create a virtualenv (`python -m venv .venv && source .venv/bin/activate`) and install editable deps with `python -m pip install -e .`.
- Sync dev dependencies via `pip install -r requirements.txt` (pytest, Hypothesis, Ruff, docs, pre-commit).
- Run `pytest` to execute the suite (`strgen/tests.py`).
- Use `./cover.sh` for CI coverage (`coverage run -m pytest && coverage report -m`).
- Install hooks with `pre-commit install`; pre-commit runs Ruff and `pytest`.
- Build documentation locally with `make -C docs html`; inspect `_build/html/index.html` before publishing.

## Coding Style & Naming Conventions
- Follow the Ruff profile in `pyproject.toml`: Python 3.7+ syntax, 4-space indents, and 120-character lines; run `ruff format` and `ruff check` before committing.
- Keep constant-like strings upper snake case (`SPECIAL_CHARACTERS`), and prefer descriptive helper names over abbreviations.
- Type hints are welcome; stick to stdlib features available on 3.7–3.12 to match the test matrix.
- Represent template snippets and user-facing examples as raw strings to preserve escaping.

## Testing Guidelines
- Extend coverage in `strgen/tests.py` using `pytest` functions or Hypothesis strategies; name new tests `test_*` and isolate randomness with seeds when assertions depend on determinism.
- Run focused checks (`pytest -k <name>`) while iterating, then the full suite and `cover.sh` before pushing.
- Aim to maintain coverage (see `.coveragerc`) and add regression cases whenever fixing parser or rendering defects.
- Run `coverage html` for a browsable report when debugging gaps.

## Commit & Pull Request Guidelines
- Match the git history with short, imperative titles (`Fix OR bias`, `Use pre-3.8 permutation calc`); add detail in the body if behavior changes.
- Each PR should note linked issues, include testing evidence, and flag docs updates or release-note entries in `CHANGES.txt` when relevant.
- CI enforces `ruff` and `pytest` across Python 3.7–3.12; run both locally and attach any notable output to the PR description.
- Rebase against `main` before requesting review and keep release metadata separate from feature commits so maintainers can version cleanly.
