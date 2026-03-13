---
name: pr-review
description: Review the PR diff for quality, security risks, test coverage of changes, dependency impact, and completeness with a structured pass/fail verdict.
---

# PR Review

Review the PR diff for quality, risks, and completeness. Produces deterministic findings by scanning the diff for security patterns, mapping test coverage of changed files, analyzing dependency impact, and checking code quality signals.

## Step 1 — Scope the change

```bash
git diff --stat main...HEAD
```

```bash
git diff --name-only main...HEAD
```

Classify every changed file:
- **New** — file did not exist on main
- **Modified** — existing file changed
- **Deleted** — file removed
- **Renamed** — file moved/renamed
- **Test file** — path matches `tests/` or filename starts with `test_`
- **Source file** — everything else under `app/`

Count: X files changed, Y insertions, Z deletions.

Flag large diffs (>500 lines total) as requiring extra scrutiny.

## Step 2 — Security scan on diff

```bash
git diff main...HEAD
```

Grep the full diff for security-sensitive patterns:

| Pattern | Category | Severity |
|---------|----------|----------|
| `password\s*=`, `secret\s*=`, `api_key\s*=`, `token\s*=` (outside test files) | Hardcoded secrets | Critical |
| `f"SELECT`, `f"INSERT`, `f"UPDATE`, `f"DELETE`, `.format(` near SQL keywords | SQL injection | Critical |
| `eval(`, `exec(`, `subprocess.call(.*shell=True`, `pickle.loads` | Dangerous calls | Critical |
| `allow_origins=["*"]` | Permissive CORS | Warning |
| Commented-out auth decorators (`# @require_auth`, `# @login_required`) | Auth bypass | Critical |
| `print(`, `console.log(`, `import pdb`, `breakpoint()` | Debug statements | Warning |

For each match, read the surrounding context (10 lines before and after) to determine if it is a **true positive** or **false positive** (e.g., test fixtures, documentation strings, variable names that happen to contain "password").

## Step 3 — Test coverage of changed code

For each changed source file `app/foo/bar.py`:

1. Check if a corresponding test file exists: `tests/test_bar.py`, `tests/foo/test_bar.py`, or `tests/test_foo_bar.py`
2. If the test file exists, check if it was **also modified** in this PR

Produce a table:

```
| Source File | Test File | Test Exists? | Test Updated? |
```

Summary counts: X source files changed, Y have corresponding test files, Z test files were also updated in this PR.

Flag: changed source files with no corresponding test file. Flag: changed source files whose test file exists but was **not** updated (suspicious — the logic changed but tests didn't).

## Step 4 — Dependency impact analysis

For each changed source file, find its importers:

```bash
grep -rn "from app.foo.bar import\|import app.foo.bar" app/ --include="*.py"
```

For each consumer file found:
- Check if that consumer has a test file
- Check if that test file was updated in this PR

Flag downstream impact: "You changed `app/utils/auth.py` which is imported by 12 modules — only 2 of those modules' tests were updated."

Focus on high fan-in files (imported by >5 modules) — changes to these have outsized blast radius.

## Step 5 — TODO/FIXME audit

```bash
git diff main...HEAD | grep "^+" | grep -i "TODO\|FIXME\|HACK\|XXX"
```

For each match:
- **Acceptable**: TODO with a ticket reference — `# TODO(PROJ-123): migrate to async`
- **Flag**: TODO without a ticket — `# TODO: fix later`, `# FIXME`, `# HACK`
- **Flag**: XXX — typically indicates known broken code

Count: X new TODOs added, Y have ticket references, Z do not.

## Step 6 — Change quality checks

Scan changed files for quality signals:

1. **Long functions** — functions added or modified that exceed 50 lines. Use `grep -n "def "` to find function boundaries in changed files and measure line counts.
2. **Missing docstrings** — new files or new public classes/functions without docstrings.
3. **Debug statements left in** — `print(`, `console.log(`, `import pdb`, `breakpoint()`, `logging.debug(` in non-test source files.
4. **Commented-out code** — 3 or more consecutive lines that are commented out (not docstrings, not license headers).
5. **Bare exceptions** — `except:` or `except Exception:` without re-raising or logging.

## Step 7 — Report

### 7a. Summary

- Files changed: X (Y source, Z tests)
- Insertions: X, Deletions: Y
- Large diff warning: Yes/No

### 7b. Security findings

| Finding | File:Line | Severity | True/False Positive | Details |
|---------|-----------|----------|---------------------|---------|

### 7c. Test coverage of changes

```
| Source File | Test File | Exists? | Updated? |
```

Summary: X/Y source files have tests, Z/Y test files were updated.

### 7d. Dependency impact

Files changed with high fan-in, and how many of their consumers' tests were updated.

### 7e. TODO/FIXME audit

New TODOs without ticket references.

### 7f. Quality issues

Long functions, debug statements, commented-out code, bare exceptions.

### 7g. Verdict

- **FAIL** if: critical security findings (true positives), >50% of changed source files have no tests
- **PASS WITH WARNINGS** if: warning-level security findings, TODOs without tickets, untested dependency consumers, quality issues
- **PASS** if: all checks clean


## Testing Philosophy

- Tests should verify behavior, not implementation details.
- Prefer integration tests for critical paths; unit tests for complex logic.
- A failing test should clearly indicate what broke and where.
- Don't mock what you don't own — use fakes or test doubles for external services.
- Test names should describe the scenario and expected outcome.
- Avoid testing framework internals or language features.

