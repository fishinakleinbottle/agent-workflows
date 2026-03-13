---
name: pre-pr-architecture-review
description: Detect architectural regressions in the PR before it merges — dependency direction violations, circular imports, breaking API changes, and complexity growth.
---

# Pre-PR Architecture Review

Detect architectural regressions in the current PR. Checks dependency direction, circular imports, API surface changes, complexity growth, and naming consistency against codebase conventions.

## Step 1 — Scope and classify changes

```bash
git diff --name-only main...HEAD
```

Classify every changed file by layer:

| Layer | Path pattern | Examples |
|-------|-------------|----------|
| API | `app/api/` | Route handlers, request/response schemas |
| Service | `app/services/`, `app/core/` | Business logic, orchestration |
| Data | `app/models/`, `app/repositories/` | ORM models, DB queries, migrations |
| Utils | `app/utils/` | Shared helpers, pure functions |
| Config | `app/config/`, `*.env*`, `settings.py` | Configuration, environment |
| Tests | `tests/` | Test files |

Produce a table:

```
| File | Layer | Change Type (new/modified/deleted) |
```

Flag **cross-layer changes** — PRs that touch both API and Data layers (or more than 2 layers) carry higher architectural risk.

## Step 2 — Dependency direction check

For each changed file, extract its imports:

```bash
grep -n "^from \|^import " <file>
```

Check dependency direction violations against the allowed import rules:

| Importing Layer | May Import From | Must NOT Import From |
|----------------|----------------|---------------------|
| API | Service, Data, Utils, Config | Other API routes |
| Service | Data, Utils, Config | API |
| Data | Utils, Config | Service, API |
| Utils | Config, stdlib, third-party | API, Service, Data |
| Config | stdlib, third-party | API, Service, Data, Utils |

For each violation found, report:
- File and line number
- The import statement
- Why it violates the rule (e.g., "Service layer importing from API layer")

If `.ai/architecture-baseline.md` exists, compare against baseline — distinguish **new violations** (introduced in this PR) from **pre-existing violations**.

## Step 3 — Circular import detection

Build a simplified import graph of changed files and their direct dependencies:

1. For each changed `.py` file, parse its imports
2. For each imported module (within `app/`), parse *its* imports
3. Check for direct cycles: A imports B, B imports A
4. Check for indirect cycles through changed files: A → B → C → A

```bash
python -c "
import ast, sys
with open(sys.argv[1]) as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        if isinstance(node, ast.ImportFrom) and node.module:
            print(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                print(alias.name)
" <file>
```

Report any cycles found with the full chain: `A → B → C → A`.

## Step 4 — API surface analysis

```bash
git diff main...HEAD -- "app/api/"
```

Detect changes to the API surface:

| Change Type | Detection | Risk |
|-------------|-----------|------|
| New endpoint | New `@router.get/post/put/delete/patch` decorator | Low (additive) |
| Changed signature | Modified function parameters or return type | Medium |
| Removed endpoint | Deleted route handler | High (breaking) |
| Changed URL path | Modified path in decorator | High (breaking) |

For **new endpoints**, check:
- Auth decorator is present (`@require_auth`, `@login_required`, or similar)
- Response model is specified
- Input validation via Pydantic models (not raw dicts)

For **changed endpoints**, assess backwards compatibility:
- Adding optional parameters = OK
- Adding required parameters = Breaking
- Changing return shape = Breaking
- Changing HTTP method = Breaking

## Step 5 — God file / complexity growth check

For each modified file, compare before/after:

```bash
git show main:<file> | wc -l
```

```bash
wc -l <file>
```

Produce a table:

```
| File | Lines Before | Lines After | Delta | Flag |
```

Flags:
- **GOD FILE** — file exceeds 500 total lines
- **RAPID GROWTH** — file grew by >50 lines in this PR
- **LONG FUNCTION** — any function exceeds 50 lines (use `grep -n "def "` to find function boundaries and measure)

## Step 6 — Naming and pattern consistency

Check that new files and symbols follow existing codebase conventions:

1. **File naming** — new files should match the naming pattern of their directory (e.g., `app/api/v1/endpoints/` uses `{resource}.py`, models use `{entity}.py`)
2. **Class naming** — `grep -rn "class.*:" <changed_files>` and compare against existing patterns in the same directory
3. **Function naming** — new public functions should follow the module's naming style (e.g., `get_`, `create_`, `update_`, `delete_` for CRUD)
4. **Constant naming** — should be UPPER_SNAKE_CASE

Flag inconsistencies with specific examples of the expected pattern.

## Step 7 — Report

### 7a. Layer classification

```
| File | Layer | Change Type |
```

Cross-layer change: Yes/No (list layers touched).

### 7b. Dependency direction violations

| File:Line | Import | Violation | New/Pre-existing |
|-----------|--------|-----------|-----------------|

### 7c. Circular import risks

Any cycles detected, with full chain.

### 7d. API surface changes

| Endpoint | Change Type | Breaking? | Auth Present? |
|----------|-------------|-----------|---------------|

### 7e. Complexity growth

| File | Before | After | Delta | Flags |
|------|--------|-------|-------|-------|

### 7f. Naming consistency

Issues found with expected vs actual patterns.

### 7g. Verdict

- **BLOCK** if: dependency direction violations introduced in this PR, circular imports detected, breaking API changes without version bump
- **WARN** if: cross-layer changes, files growing large, naming inconsistencies, pre-existing violations
- **PASS** if: clean architecture, no violations, consistent patterns

