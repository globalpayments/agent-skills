# AGENTS.md

This repository publishes eight Global Payments SDK integration skills.
Use the relevant SDK source, sample code, and integration tests as authority.
Before changing a skill, verify its class names, method chains, configuration
fields, and error trees against the relevant `globalpayments/*` repository.
State when a feature is not supported or was not verified.

## Layout

```
.claude-plugin/marketplace.json        Claude Code marketplace catalog
.agents/plugins/marketplace.json       Codex / ChatGPT marketplace catalog
plugins/gp-sdk-skills/plugin.json      Agent Plugins 1.0 manifest
plugins/gp-sdk-skills/.claude-plugin/plugin.json
                                        Claude Code plugin manifest
plugins/gp-sdk-skills/.codex-plugin/plugin.json
                                        Codex plugin manifest
plugins/gp-sdk-skills/skills/gp-*-sdk/ the eight SDK skills
scripts/validate-packaging.py          packaging and manifest validator
scripts/validate-sdk-skill.py          skill structure, length, and frontmatter validator
.github/workflows/ci.yml               runs both validators on push and PR
```

## Distribution contracts

The three plugin manifests must use the same `name` and `version`. Update
them together.

## Skill structure

- Each skill contains `SKILL.md` and companion docs under `references/`.
- Every skill has `references/REFERENCE.md`.
- Only `gp-android-sdk` has `references/VERIFICATION.md`; it references that
  file from its `SKILL.md`. Delete an unused verification document.
- In `SKILL.md`, use `references/` or `./references/` for companion docs.
- In files under `references/`, use `../SKILL.md` for links back to `SKILL.md`.
- Frontmatter `name` must match the skill directory. Keep `description`
  within the 1024-character Agent Skills limit.

## Before opening a PR

```
python3 scripts/validate-packaging.py
python3 scripts/validate-sdk-skill.py --all
```

Both commands must pass. CI runs the same checks.
