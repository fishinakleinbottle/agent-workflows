---
name: test-coverage
description: Run backend test suite with pytest-cov, analyze line/branch coverage against the previous baseline, discover untested endpoints, check test quality, and produce a structured pass/fail report.
---

# Test Coverage Analysis

A generic, automated coverage skill that uses `pytest-cov` for line/branch coverage, dynamically discovers endpoints and test gaps, and provides structured analysis across multiple coverage dimensions.

## Step 1 — Load previous baseline

Read `.ai/latest-coverage-report.md` if it exists. Extract per-file coverage percentages, overall coverage, test count, untested endpoints, and known critical gaps. This is the **baseline** for comparison.

If the file does not exist, treat this as the first run — there is no baseline to compare against.

## Step 2 — Prerequisites

**Required packages:** `pytest` and `pytest-cov` must both be installed in the project's Python environment. `pytest-cov` is a pytest plugin — it cannot function without `pytest`.

Verify both are available:

```bash
cd backend && source .venv/bin/activate && pip show pytest pytest-cov
```

If either package is missing, detect the project's dependency manager and use the correct command. Do **not** mix managers — e.g. running bare `pip install` in a `uv`-managed project installs the package but does not record it in `pyproject.toml` or the lockfile, so the next `uv sync` will remove it.

Detect the manager by checking for lockfiles/config in the project root:

- `uv.lock` exists → **uv project**
- `poetry.lock` exists → **poetry project**
- `requirements*.txt` exists → **pip project**

Then install accordingly:

```bash
# uv — adds to pyproject.toml [dev-dependencies] and installs:
cd backend && uv add --dev pytest pytest-cov

# poetry — adds to [tool.poetry.group.dev.dependencies] and installs:
cd backend && poetry add --group dev pytest pytest-cov

# pip — installs into the active venv (also add to requirements-dev.txt manually):
cd backend && source .venv/bin/activate && pip install pytest pytest-cov
```

If the packages are already declared in `pyproject.toml` dev dependencies but not installed, sync instead:

```bash
# uv:
cd backend && uv sync --group dev

# poetry:
cd backend && poetry install --with dev

# pip:
cd backend && source .venv/bin/activate && pip install -r requirements-dev.txt
```

If no virtual environment (`.venv`) exists and the project has no dependency manager, create one:

```bash
cd backend && python -m venv .venv && source .venv/bin/activate && pip install pytest pytest-cov
```

Coverage config (thresholds, source paths, omit patterns) is typically defined in `pyproject.toml` or `setup.cfg`. If neither exists, the defaults from the Step 3 command flags will be used.

## Step 3 — Run tests with coverage

```bash
cd backend && source .venv/bin/activate && python -m pytest \
  --cov=app --cov-report=term-missing --cov-report=json:coverage.json \
  --cov-branch -v --tb=short 2>&1
```

- If any tests **fail**, stop immediately. Report the failures. Do not proceed to coverage analysis.
- Record: total passed, failed, skipped, errors.

## Step 4 — Analyze coverage report

Read `backend/coverage.json` and classify every source file into tiers:

| Tier         | Coverage | Priority                          |
| ------------ | -------- | --------------------------------- |
| Untested     | 0%       | Critical — must fix before PR     |
| Low          | <50%     | High — likely missing major logic |
| Below target | <75%     | Medium — review gaps              |
| Adequate     | >=75%    | Low — spot-check only             |

For each file in the top 3 tiers (Untested, Low, Below target):

- If the file appeared in the baseline, compare coverage. If coverage **improved or held steady**, note the delta but skip deep analysis unless it's still below target.
- If the file **regressed** from baseline, or is **new to the codebase**, prioritize it for deep analysis.
- If no baseline exists, analyze all files in the top 3 tiers.

For files requiring deep analysis, read the source file and examine the **uncovered line numbers** from the JSON report. Categorize what's missing:

- **Happy path** — main success flow not exercised
- **Error handling** — `except` blocks, `HTTPException` raises
- **Auth/permissions** — `require_auth`, `require_admin`, `assert_line_access` checks
- **Input validation** — Pydantic validation, manual checks, 422 paths
- **State transitions** — status field changes (DRAFT->ACTIVE, PENDING->APPROVED, etc.)
- **External service failures** — try/except around OpenAI, Weaviate, Turn.io, SMTP
- **Edge cases** — empty collections, None values, boundary conditions

Don't just list line numbers — explain in human terms what logic is untested.

## Step 5 — Endpoint coverage analysis

Dynamically discover all route handlers:

```bash
cd backend && grep -rn "@router\.\(get\|post\|put\|delete\|patch\)" app/api/ --include="*.py"
```

Dynamically discover all test HTTP calls:

```bash
cd backend && grep -rn "client\.\(get\|post\|put\|delete\|patch\)" tests/ --include="*.py"
```

Cross-reference the two lists. For each route handler, check if at least one test exercises that method+path. Report untested endpoints.

If the baseline listed untested endpoints, check whether they are **still** untested or have been covered since. Flag newly untested endpoints (regressions) separately from carry-over gaps.

For tested endpoints, check if the test file covers multiple response scenarios:

- Success (2xx)
- Auth required (401)
- Forbidden (403)
- Not found (404)
- Validation error (422)

Not every endpoint needs all 5, but data-mutating endpoints (POST/PUT/DELETE) should have at least success + auth + validation tests.

## Step 6 — Test quality checks

Scan test files for:

1. **Assertion-less tests** — `def test_*` functions with no `assert` or `pytest.raises`. These pass but verify nothing.
2. **Overly broad exception catching** — `except Exception` in test code that swallows failures.
3. **Mock appropriateness** — External services (OpenAI, Weaviate, Turn.io, SMTP) should be mocked. Internal business logic (permissions, validation, DB queries) should NOT be mocked.
4. **Test isolation** — Tests should use the `clean_database` fixture or depend on fixtures that do.

## Step 7 — Report

Produce a structured report with the following sections:

### 7a. Summary

- Tests: X passed, Y failed, Z skipped
- Overall line coverage: X% (delta from baseline if available)
- Overall branch coverage: X%

### 7b. Coverage table (sorted by coverage ascending)

```
| Module | Line Cov % | Prev % | Delta | Grade |
```

Grades: A (>=85%), B (>=70%), C (>=55%), D (>=40%), F (<40%)

Include the **Prev %** and **Delta** columns only when a baseline exists. Flag regressions (negative delta) with a warning marker.

### 7c. Untested endpoints

List of method + path with no test coverage. If baseline exists, distinguish:

- **Carry-over** — still untested from previous run
- **New gap** — endpoint was previously tested but is now untested (regression)
- **Resolved** — endpoint was untested in baseline but is now covered

### 7d. Critical gaps (prioritized)

1. Security-sensitive code (auth, permissions) below 80%
2. Data mutation endpoints with no tests
3. External service error handling with no coverage
4. Any file at 0% coverage
5. Any file that **regressed** from baseline

### 7e. Test quality issues

Assertion-less tests, mock concerns, isolation issues.

### 7f. Recommendation

- **FAIL** if: tests fail, overall coverage <50%, any security file <70%, untested mutation endpoints exist
- **PASS WITH WARNINGS** if: passes thresholds but has notable gaps (files <50%, quality issues)
- **PASS** if: all tests pass, overall >=60%, no critical security gaps, all mutation endpoints tested

### 7g. Suggested fixes

For each critical gap, suggest a specific test: function name, what to test, which existing fixture to use.

## Step 8 — Update baseline

After producing the report, **overwrite** `.ai/latest-coverage-report.md` with the new results so the next run has an accurate baseline. Include a relative link to `backend/coverage.json` for the raw data. Use the same format as the existing file so future runs can parse it consistently.


## Testing Philosophy

- Tests should verify behavior, not implementation details.
- Prefer integration tests for critical paths; unit tests for complex logic.
- A failing test should clearly indicate what broke and where.
- Don't mock what you don't own — use fakes or test doubles for external services.
- Test names should describe the scenario and expected outcome.
- Avoid testing framework internals or language features.

