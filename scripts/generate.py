#!/usr/bin/env python3
"""Generate tool-specific artifacts from canonical prompts."""

import argparse
import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT / "prompts"
ADAPTERS_DIR = ROOT / "adapters"
PROFILES_DIR = ROOT / "profiles"
DIST_DIR = ROOT / "dist"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from a markdown file."""
    match = re.match(r"^---\s*\n(.*?\n)---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).strip()
    return frontmatter, body


def load_fragment(name: str) -> str:
    """Load a fragment file by name."""
    path = PROMPTS_DIR / "fragments" / f"{name}.md"
    return path.read_text().strip()


def load_skill(name: str) -> tuple[dict, str]:
    """Load a canonical skill and return (frontmatter, body)."""
    path = PROMPTS_DIR / "skills" / name / "SKILL.md"
    return parse_frontmatter(path.read_text())


def load_agent(name: str) -> tuple[dict, str]:
    """Load a canonical agent and return (frontmatter, body)."""
    path = PROMPTS_DIR / "agents" / f"{name}.md"
    return parse_frontmatter(path.read_text())


def generate_skills(tool: str, skills: list[dict], env: Environment) -> list[str]:
    """Generate skill files for a specific tool. Returns list of output paths."""
    template = env.get_template(f"{tool}/skill.md.j2")
    generated = []

    for skill_cfg in skills:
        name = skill_cfg["name"]
        meta, body = load_skill(name)

        # Load fragments
        fragment_names = skill_cfg.get("fragments", [])
        fragments = [load_fragment(f) for f in fragment_names]

        rendered = template.render(
            name=meta.get("name", name),
            description=meta.get("description", ""),
            content=body,
            fragments=fragments,
            **{k: v for k, v in skill_cfg.items() if k not in ("name", "fragments")},
        )

        out_dir = DIST_DIR / tool / "skills" / name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "SKILL.md"
        out_path.write_text(rendered)
        generated.append(str(out_path.relative_to(ROOT)))

    return generated


def generate_agents(tool: str, agents: list[dict], env: Environment) -> list[str]:
    """Generate agent files for a specific tool. Returns list of output paths."""
    template = env.get_template(f"{tool}/agent.md.j2")
    generated = []

    for agent_cfg in agents:
        name = agent_cfg["name"]
        meta, body = load_agent(name)

        rendered = template.render(
            name=meta.get("name", name),
            description=meta.get("description", ""),
            content=body,
            tools=agent_cfg.get("tools", []),
            model=agent_cfg.get("model"),
        )

        out_dir = DIST_DIR / tool / "agents"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}.md"
        out_path.write_text(rendered)
        generated.append(str(out_path.relative_to(ROOT)))

    return generated


def generate_rules(tool: str, rules: list[dict], env: Environment) -> list[str]:
    """Generate rule files (cursor). Returns list of output paths."""
    template = env.get_template(f"{tool}/rule.mdc.j2")
    generated = []

    for rule_cfg in rules:
        name = rule_cfg["name"]
        rendered = template.render(**rule_cfg)

        out_dir = DIST_DIR / tool / "rules"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}.mdc"
        out_path.write_text(rendered)
        generated.append(str(out_path.relative_to(ROOT)))

    return generated


def generate_instructions(tool: str, instructions: list[dict], env: Environment) -> list[str]:
    """Generate instruction files (copilot). Returns list of output paths."""
    template = env.get_template(f"{tool}/instructions.md.j2")
    generated = []

    for inst_cfg in instructions:
        name = inst_cfg["name"]
        rendered = template.render(**inst_cfg)

        out_dir = DIST_DIR / tool / "instructions"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{name}.instructions.md"
        out_path.write_text(rendered)
        generated.append(str(out_path.relative_to(ROOT)))

    return generated


def main():
    parser = argparse.ArgumentParser(description="Generate tool-specific artifacts")
    parser.add_argument("--profile", default="default", help="Profile name (default: default)")
    args = parser.parse_args()

    # Load profile
    profile_path = PROFILES_DIR / f"{args.profile}.yaml"
    profile = yaml.safe_load(profile_path.read_text())

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(ADAPTERS_DIR)),
        keep_trailing_newline=True,
    )

    # Clean dist
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    all_generated = []

    for tool, config in profile.get("targets", {}).items():
        # Skills
        skills = config.get("skills", [])
        if skills:
            all_generated.extend(generate_skills(tool, skills, env))

        # Agents (claude)
        agents = config.get("agents", [])
        if agents:
            all_generated.extend(generate_agents(tool, agents, env))

        # Rules (cursor)
        rules = config.get("rules", [])
        if rules:
            all_generated.extend(generate_rules(tool, rules, env))

        # Instructions (copilot)
        instructions = config.get("instructions", [])
        if instructions:
            all_generated.extend(generate_instructions(tool, instructions, env))

    print(f"Generated {len(all_generated)} files:")
    for path in sorted(all_generated):
        print(f"  {path}")


if __name__ == "__main__":
    main()
