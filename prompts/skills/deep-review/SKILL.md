---
name: deep-review
description: Deep file/module-level code review — complexity analysis, type safety audit, error handling review, performance pattern detection, and business logic assessment with per-file grades.
---

# Deep Review

Deep-dive review of specific files or modules. Not PR-scoped — called when you want thorough analysis of particular code. Produces per-file grades across complexity, type safety, error handling, and performance.

## Step 1 — Target identification

Determine what to review:

- If the user specifies files or modules, use those as targets.
- If no target specified, review files changed in the current working tree:

```bash
git diff --name-only
```

- If the working tree is clean, review files changed in the last commit:

```bash
git diff --name-only HEAD~1
```

List all target files and confirm scope before proceeding.

## Step 2 — Complexity analysis

For each target file, extract functions and classes:

```bash
grep -n "def \|class " <file>
```

Measure per-function metrics:
- **Line count** — from the `def` line to the next `def`/`class`/end-of-file (adjust for nesting)
- **Nesting depth** — count the maximum indentation level within the function body relative to the function's base indentation

Produce a table:

```
| Function | Lines | Max Nesting | Flag |
```

Flags:
- **LONG** — function exceeds 40 lines
- **COMPLEX** — nesting depth >4 levels
- **GOD CLASS** — class exceeds 200 lines
- **GOD FILE** — file exceeds 400 lines

## Step 3 — Type safety audit

For each target file, check function signatures:

```bash
grep -n "def .*(.*):" <file>
```

For each function:
- Does it have **parameter type annotations**?
- Does it have a **return type annotation**?
- Does it use `Any` type? (`grep -n ": Any\|-> Any" <file>`)
- Does it use `# type: ignore`? (`grep -n "type: ignore" <file>`)

Produce a summary:
- X/Y functions have full type annotations (parameters + return)
- Z functions use `Any`
- W `# type: ignore` comments

Flag functions missing return type annotations — these hide bugs in callers.

## Step 4 — Error handling review

Find all try/except blocks in target files:

```bash
grep -n "try:\|except " <file>
```

For each try/except block, read the code and classify:

| Pattern | Verdict |
|---------|---------|
| `except SpecificError:` with logging/re-raise | Good |
| `except SpecificError:` with recovery logic | Good |
| `except Exception as e:` with logging | Acceptable |
| `except Exception:` with `pass` | **Critical** — swallows all errors |
| `except:` (bare) | **Critical** — catches SystemExit, KeyboardInterrupt |
| `except` with no logging | **Warning** — silent failure |

Also check:
- Resource cleanup in `finally` blocks (file handles, DB connections, locks)
- HTTP error codes in API handlers — are they specific (400, 404, 409) or generic (500)?
- Are exceptions from external services (DB, HTTP clients, file I/O) caught at the right level?

## Step 5 — Performance patterns

Scan target files for common performance anti-patterns:

**N+1 queries** — loops containing DB queries:
```bash
# Look for patterns like: for ... in ...: followed by db/session/query calls
grep -n "for .* in .*:" <file>
```
Then check if the loop body contains `db.query`, `session.execute`, `.filter(`, `.get(`.

**Unbounded queries**:
```bash
grep -n "\.all()\|\.filter(" <file>
```
Check if `.all()` or `.filter()` calls are missing `.limit()`. Flag queries that could return unbounded result sets.

**Synchronous I/O in async context**:
```bash
grep -n "async def" <file>
```
If the file uses `async def`, check for synchronous blocking calls inside async functions: `open(`, `requests.get(`, `time.sleep(`, `subprocess.run(`.

**Missing caching**:
- Repeated identical computations or DB queries within the same request path
- Pure functions called with the same arguments in a loop

## Step 6 — Business logic review

Read the target code and assess:

1. **Business rule placement** — are business rules in the service layer (good) or scattered across API handlers and models (bad)?
2. **Magic numbers/strings** — hardcoded values that should be named constants (e.g., `if status == 3`, `timeout=30`, `max_retries=5`)
3. **Validation boundaries** — is input validation happening at the API boundary (good) or deep inside business logic (bad)?
4. **Single responsibility** — does each function do one thing, or are there functions that validate + transform + persist + notify?
5. **Defensive coding** — are there unnecessary `if x is not None` checks where `x` can never be None based on the type/flow?

## Step 7 — Report

### 7a. File summaries

For each target file:

```
| File | Lines | Functions | Classes | Complexity Flags |
```

### 7b. Complexity table

```
| Function | File:Line | Lines | Nesting | Grade |
```

Grades: A (≤20 lines, ≤2 nesting), B (≤30 lines, ≤3 nesting), C (≤40 lines, ≤4 nesting), D (≤60 lines, ≤5 nesting), F (>60 lines or >5 nesting)

### 7c. Type safety score

X/Y functions fully annotated. List unannotated functions.

### 7d. Error handling issues

| Location | Pattern | Severity | Recommendation |
|----------|---------|----------|----------------|

### 7e. Performance concerns

| Location | Pattern | Severity | Recommendation |
|----------|---------|----------|----------------|

### 7f. Business logic observations

Bullet points on rule placement, magic values, validation boundaries.

### 7g. Per-file verdict

Score each file on a weighted scale:

| Dimension | Weight |
|-----------|--------|
| Complexity | 30% |
| Type safety | 20% |
| Error handling | 25% |
| Performance | 15% |
| Business logic | 10% |

Grade: A (≥85), B (≥70), C (≥55), D (≥40), F (<40)

```
| File | Complexity | Types | Errors | Perf | Logic | Overall | Grade |
```
