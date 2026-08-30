# AGENTS.md

Public agent-skills library for Global Payments SDK integrations. Skills are
grounded in real SDK source — verify class names, method chains, and
configuration fields against the actual `globalpayments/*` repositories
before changing them.

## Layout

```
.claude-plugin/marketplace.json        Claude Code repo marketplace catalog
.agents/plugins/marketplace.json       Codex / ChatGPT repo marketplace catalog
plugins/gp-sdk-skills/plugin.json      Agent Plugins 1.0 manifest (Cursor, Copilot, VS Code, Kiro)
plugins/gp-sdk-skills/.claude-plugin/plugin.json    Claude Code plugin manifest
plugins/gp-sdk-skills/.codex-plugin/plugin.json     Codex plugin manifest
plugins/gp-sdk-skills/skills/gp-*-sdk/ the eight SDK skills
scripts/validate-packaging.py          packaging + manifest validator
scripts/validate-sdk-skill.py          skill structure/length validator
.github/workflows/ci.yml               runs both validators on push and PR
```

The three manifests serve three distribution contracts and must agree on
`name` and `version` — bump them together.

## Skill structure

- Each skill is `skills/<name>/SKILL.md` plus companion docs under
  `skills/<name>/references/`. No companion doc sits flat at a skill root.
- Every skill has `references/REFERENCE.md`. Only `gp-android-sdk` keeps
  `references/VERIFICATION.md`, because its SKILL.md references it; a
  VERIFICATION.md no skill mentions is an orphan and must be deleted.
- `SKILL.md` must mention companion docs with a `references/` prefix; files
  under `references/` must reference `SKILL.md` with a `../` prefix.
- Frontmatter `name` matches the parent directory and `description` stays
  within the 1024-character Agent Skills cap.

## Before opening a PR

```
python3 scripts/validate-packaging.py
python3 scripts/validate-sdk-skill.py --all
```

Both must pass; CI runs the same commands.
