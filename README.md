# Agent Workflows

Central repository for portable AI agent skills, agents, and rules. Single source of truth that generates tool-specific artifacts for Claude Code, Cursor, and GitHub Copilot.

## Quick Start

```bash
# Install dependencies
pip install -e .

# Generate all artifacts
make generate

# Deploy to a project
make sync TARGET=/path/to/project
```

## Structure

- `prompts/` — Canonical, tool-agnostic skills, agents, personas, and fragments
- `adapters/` — Jinja2 templates that produce tool-specific output
- `profiles/` — YAML configs defining what to generate per tool
- `dist/` — Generated output (committed)
- `scripts/` — Build tooling

## Workflow

1. Edit canonical prompts in `prompts/`
2. Run `make generate` to rebuild `dist/`
3. Run `make sync TARGET=/path/to/project` to deploy
4. Run `make diff TARGET=/path/to/project` to check for drift
