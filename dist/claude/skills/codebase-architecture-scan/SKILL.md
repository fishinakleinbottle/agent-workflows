---
name: codebase-architecture-scan
description: Full repository health audit — module structure, import coupling, layer discipline, dependency freshness, dead code, and test health — producing a scored report card.
---

# Codebase Architecture Scan

Full repo health audit. Not PR-scoped — scans the entire codebase and produces a scored report card across six dimensions.

## Step 1 — Module structure inventory

Discover all source files:

```bash
find app/ -name "*.py" -not -path "*__pycache__*"
```

For each directory under `app/`, count:
- Number of `.py` files
- Total lines per file: `wc -l <file>`

Produce a size distribution:

| Category | Threshold | Count |
|----------|-----------|-------|
| God files | >500 lines | ? |
| Large files | 301–500 lines | ? |
| Medium files | 101–300 lines | ? |
| Small files | ≤100 lines | ? |

Flag:
- **God files** (>500 lines) — list each with line count
- **God directories** (>20 `.py` files) — list each with file count

## Step 2 — Import graph and coupling

For every `.py` file under `app/`, extract imports:

```bash
grep -rn "^from app\.\|^import app\." app/ --include="*.py"
```

Build an adjacency list of module dependencies (only internal `app.*` imports).

Compute per-module metrics:

- **Fan-in** — how many other modules import this one. High fan-in = core utility, change carefully.
- **Fan-out** — how many other modules this one imports. High fan-out = possibly doing too much.

Produce a table (sorted by fan-out descending):

```
| Module | Fan-in | Fan-out | Flag |
```

Flag:
- Fan-out >10 — **HIGH COUPLING** (module depends on too many others)
- Fan-in >15 — **CORE MODULE** (many dependents — changes are high-risk)

Detect circular dependency chains: for each edge A→B, check if B→...→A exists. Report all cycles with the full chain.

## Step 3 — Layer boundary analysis

Classify all modules by layer using the same scheme as pre-pr-architecture-review:

| Layer | Path pattern |
|-------|-------------|
| API | `app/api/` |
| Service | `app/services/`, `app/core/` |
| Data | `app/models/`, `app/repositories/` |
| Utils | `app/utils/` |
| Config | `app/config/` |

Check every internal import crosses layers in the allowed direction:

| Importing Layer | May Import From | Must NOT Import From |
|----------------|----------------|---------------------|
| API | Service, Data, Utils, Config | Other API routes |
| Service | Data, Utils, Config | API |
| Data | Utils, Config | Service, API |
| Utils | Config, stdlib, third-party | API, Service, Data |

Count total violations and produce a table:

```
| File:Line | Import | Violation |
```

## Step 4 — Dependency freshness

Check for outdated packages:

```bash
pip list --outdated --format=json
```

Classify:

| Severity | Criteria |
|----------|----------|
| Critical | Major version behind (e.g., 1.x → 2.x) |
| Info | Minor version behind (e.g., 1.2 → 1.5) |
| Low | Patch version behind (e.g., 1.2.3 → 1.2.5) |

If `pip-audit` is available, check for known CVEs:

```bash
pip-audit --format=json 2>/dev/null
```

Produce a table:

```
| Package | Installed | Latest | Severity | CVEs |
```

## Step 5 — Dead code detection

For each function and class defined in `app/`:

```bash
grep -rn "def \|class " app/ --include="*.py"
```

For each definition, search for external usages:

```bash
grep -rn "function_name\|ClassName" app/ tests/ --include="*.py"
```

A definition is **potentially dead** if it is only referenced in its own file or never referenced at all.

Exclude from dead code detection:
- `__init__`, `__main__`, `__str__`, `__repr__` and other dunder methods
- Route handlers (invoked by the framework via decorators)
- Pydantic model classes (used by FastAPI for serialization)
- Functions decorated with `@app.on_event`, `@celery.task`, etc.
- Anything exported in `__all__`

Report potentially dead code:

```
| Definition | File:Line | References Found | Verdict |
```

## Step 6 — Test health

Count and compare:

```bash
find app/ -name "*.py" -not -path "*__pycache__*" | wc -l
find tests/ -name "*.py" -not -path "*__pycache__*" | wc -l
```

Check directory mirroring — for each directory under `app/`, does a corresponding directory exist under `tests/`?

```
| Source Directory | Test Directory | Exists? | Source Files | Test Files |
```

Flag source directories with no corresponding test directory.

Count total test cases:

```bash
python -m pytest --collect-only -q 2>&1 | tail -1
```

Compute test-to-source ratio: test files / source files.

## Step 7 — Scored report

Score each dimension on a 0–10 scale:

| Dimension | Weight | Scoring Criteria |
|-----------|--------|-----------------|
| Modularity | 20% | File sizes, directory sizes, function lengths. Deduct for god files (−2 each), god directories (−1 each). |
| Coupling | 20% | Fan-in/fan-out distribution, circular deps. Deduct for fan-out >10 (−1 each), cycles (−3 each). |
| Layer discipline | 15% | Layer boundary violations. Start at 10, deduct −1 per violation (min 0). |
| Dependency health | 15% | Outdated packages, known CVEs. Deduct for critical outdated (−2 each), CVEs (−3 each). |
| Dead code | 10% | Ratio of potentially dead definitions. 10 if <5%, 7 if <10%, 5 if <15%, 3 if <25%, 0 if >=25%. |
| Test health | 20% | Test/source ratio, directory mirroring. 10 if ratio >0.8 and full mirroring, scale down from there. |

**Overall score** = weighted average.

| Grade | Score |
|-------|-------|
| A | ≥85 |
| B | ≥70 |
| C | ≥55 |
| D | ≥40 |
| F | <40 |

Produce the final scorecard:

```
| Dimension | Score | Weight | Weighted | Key Issues |
```

**Overall: X/100 (Grade Y)**

## Step 8 — Update baseline

Write the full results to `.ai/architecture-baseline.md` so future scans and PR reviews can compare against this baseline.

Include:
- Scan date
- Overall score and grade
- Scored table
- Top 5 issues to address
- Module metrics (fan-in/fan-out for key modules)
- Layer violation count
- Dead code count
- Test health metrics

