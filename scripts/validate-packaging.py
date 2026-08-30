#!/usr/bin/env python3
"""Validate the gp-sdk-skills plugin packaging and repo-level catalogs.

Checks, in order:

1. Skill frontmatter — every ``plugins/*/skills/*/SKILL.md`` must carry a
   ``name`` that matches its parent directory and satisfies the Agent Skills
   name constraints (≤64 chars, ``[a-z0-9-]`` only, no leading/trailing ``-``,
   no ``--``), and a non-empty ``description`` of at most 1024 characters.
2. Skill structure — companion docs live under ``references/``. A flat
   ``REFERENCE.md``/``VERIFICATION.md`` at a skill root is an error; every
   skill needs ``references/REFERENCE.md``; a ``references/VERIFICATION.md``
   must be referenced from the skill's SKILL.md (no orphans).
3. Path mentions — a SKILL.md may not contain a bare
   ``REFERENCE.md``/``VERIFICATION.md`` token (backticked or as a link
   target) without a ``references/`` prefix; a file under ``references/``
   may not contain a bare ``SKILL.md`` mention without a ``../`` prefix.
4. Plugin manifests — the three manifests (Agent Plugins 1.0 root
   ``plugin.json``, Claude ``.claude-plugin/plugin.json``, Codex
   ``.codex-plugin/plugin.json``) must exist, parse as JSON, and agree on
   ``name`` and ``version``. The AP1.0 manifest must carry the exact
   ``$schema`` URL, only permitted top-level keys, an ``author`` with only
   ``name``/``email``/``url``, and a conformant ``name``.
5. Marketplace catalogs — both catalogs must exist and parse; entries must
   resolve to an existing plugin directory; plugin names without a
   directory are errors; the Claude marketplace name must not be one of the
   names reserved for official Anthropic use.

Usage::

    python3 scripts/validate-packaging.py [--demo]

``--demo`` proves the rules fire on known-bad input (mirrors the
``validate-sdk-skill.py`` demo convention) and then exits.
"""

import json
import pathlib
import re
import sys

AP10_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AP10_PERMITTED_KEYS = {
    "$schema", "name", "version", "description", "author",
    "homepage", "repository", "license", "keywords", "extensions",
}
AP10_AUTHOR_KEYS = {"name", "email", "url"}
AP10_STRING_KEYS = {
    "name", "version", "description", "homepage", "repository", "license",
}

# Reserved Claude Code marketplace names (Claude Code docs, "Reserved names"
# note under marketplace schema — re-verified 2026-08-29).
RESERVED_MARKETPLACE_NAMES = {
    "claude-code-marketplace",
    "claude-code-plugins",
    "claude-plugins-official",
    "claude-plugins-community",
    "claude-community",
    "anthropic-marketplace",
    "anthropic-plugins",
    "agent-skills",
    "anthropic-agent-skills",
    "knowledge-work-plugins",
    "life-sciences",
    "claude-for-legal",
    "claude-for-financial-services",
    "financial-services-plugins",
    "first-party-plugins",
    "healthcare",
}

NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
DESCRIPTION_RE = re.compile(r"^description:\s*(.*?)(?=^\w+:|\Z)", re.M | re.S)
NAME_LINE_RE = re.compile(r"^name:\s*(.+?)\s*$", re.M)

# Bare companion-doc mentions. A token must carry the required relative
# prefix (`references/` or `./references/` inside a SKILL.md; `../` inside
# a moved reference doc). Valid markdown links whose *target* is prefixed
# are exempt as a whole, so the display label of
# ``[REFERENCE.md](./references/REFERENCE.md)`` passes while plain prose,
# a backticked bare token, or an unprefixed link target fails.
_PATH_BOUND = r"(?<![A-Za-z0-9._/-])"
_PATH_END = r"(?![A-Za-z0-9_/?-])(?!\.[A-Za-z0-9_.-])"
VALID_REF_LINK_IN_SKILL = re.compile(
    r"\[[^\]]*\]\((?:\./)?references/(?:REFERENCE|VERIFICATION)\.md\)"
)
VALID_REF_PATH_IN_SKILL = re.compile(
    _PATH_BOUND + r"(?:\./)?references/(?:REFERENCE|VERIFICATION)\.md" + _PATH_END
)
VALID_SKILL_LINK_IN_REFERENCES = re.compile(r"\[[^\]]*\]\(\.\./SKILL\.md\)")
VALID_SKILL_PATH_IN_REFERENCES = re.compile(
    _PATH_BOUND + r"\.\./SKILL\.md" + _PATH_END
)
REF_TOKEN = re.compile(r"(?:REFERENCE|VERIFICATION)\.md")
SKILL_TOKEN = re.compile(r"SKILL\.md")


def _bare_mentions(text, token, strip):
    """Token occurrences left after removing every valid prefixed form."""
    for pattern in strip:
        text = pattern.sub("", text)
    return list(token.finditer(text))


def _quoted(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def check_frontmatter(skill_md, expected_name, errors):
    text = skill_md.read_text(encoding="utf-8")
    fm_match = FRONTMATTER.match(text)
    label = f"{expected_name}/SKILL.md"
    if not fm_match:
        errors.append(f"{label} has no frontmatter block")
        return
    fm = fm_match.group(1)

    name_match = NAME_LINE_RE.search(fm)
    if not name_match:
        errors.append(f"{label} frontmatter has no name")
    else:
        name = _quoted(name_match.group(1))
        if name != expected_name:
            errors.append(
                f"{label} frontmatter name {name!r} does not match "
                f"directory {expected_name!r}"
            )
        if len(name) > 64:
            errors.append(f"{label} frontmatter name exceeds 64 characters")
        if not re.fullmatch(r"[a-z0-9-]*", name):
            errors.append(
                f"{label} frontmatter name contains characters outside [a-z0-9-]"
            )
        if name.startswith("-") or name.endswith("-"):
            errors.append(f"{label} frontmatter name starts or ends with '-'")
        if "--" in name:
            errors.append(f"{label} frontmatter name contains '--'")

    desc_match = DESCRIPTION_RE.search(fm)
    if not desc_match:
        errors.append(f"{label} frontmatter has no description")
        return
    description = re.sub(r"^\|\s*\n", "", desc_match.group(1)).strip()
    if not description:
        errors.append(f"{label} frontmatter has an empty description")
    elif len(description) > 1024:
        errors.append(
            f"{label} frontmatter description is {len(description)} characters "
            "(Agent Skills cap is 1024)"
        )


def check_structure(skill_dir, errors):
    name = skill_dir.name
    if (skill_dir / "REFERENCE.md").exists():
        errors.append(
            f"{name}: flat REFERENCE.md at skill root; companion docs belong "
            "under references/"
        )
    if (skill_dir / "VERIFICATION.md").exists():
        errors.append(
            f"{name}: flat VERIFICATION.md at skill root; companion docs "
            "belong under references/"
        )
    if not (skill_dir / "references" / "REFERENCE.md").exists():
        errors.append(f"{name}: references/REFERENCE.md is missing")
    verification = skill_dir / "references" / "VERIFICATION.md"
    if verification.exists():
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists() or "VERIFICATION.md" not in skill_md.read_text(
            encoding="utf-8"
        ):
            errors.append(
                f"{name}: references/VERIFICATION.md is an orphan — "
                "SKILL.md never mentions it"
            )


def check_mentions(skill_dir, errors):
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        for match in _bare_mentions(
            text,
            REF_TOKEN,
            (VALID_REF_LINK_IN_SKILL, VALID_REF_PATH_IN_SKILL),
        ):
            errors.append(
                f"{name}/SKILL.md has a bare companion-doc mention without a "
                f"references/ prefix: {match.group(0)!r}"
            )
    references_dir = skill_dir / "references"
    if references_dir.is_dir():
        for doc in sorted(references_dir.iterdir()):
            if not doc.is_file():
                continue
            text = doc.read_text(encoding="utf-8")
            for match in _bare_mentions(
                text,
                SKILL_TOKEN,
                (VALID_SKILL_LINK_IN_REFERENCES, VALID_SKILL_PATH_IN_REFERENCES),
            ):
                errors.append(
                    f"{name}/references/{doc.name} has a bare SKILL.md "
                    f"mention without a ../ prefix: {match.group(0)!r}"
                )


def check_skill(skill_dir, errors):
    if not (skill_dir / "SKILL.md").exists():
        errors.append(f"{skill_dir.name}/SKILL.md is missing")
        return
    check_frontmatter(skill_dir / "SKILL.md", skill_dir.name, errors)
    check_structure(skill_dir, errors)
    check_mentions(skill_dir, errors)


def check_ap10_manifest(path, errors):
    label = "plugins/.../plugin.json"
    if not path.exists():
        errors.append(f"{label} (Agent Plugins 1.0) is missing")
        return None, None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is not valid JSON: {exc}")
        return None, None
    if not isinstance(data, dict):
        errors.append(f"{label} is not a JSON object")
        return None, None

    if not data.get("$schema"):
        errors.append(f"{label} is missing $schema")
    elif data["$schema"] != AP10_SCHEMA:
        errors.append(
            f"{label} $schema must be {AP10_SCHEMA!r}, "
            f"got {data['$schema']!r}"
        )
    if not data.get("name"):
        errors.append(f"{label} is missing name")

    name, version = data.get("name"), data.get("version")
    if isinstance(name, str):
        if len(name) < 1 or len(name) > 64:
            errors.append(f"{label} name must be 1-64 characters")
        if not NAME_RE.fullmatch(name):
            errors.append(
                f"{label} name {name!r} violates Agent Plugins 1.0 naming: "
                "alphanumeric first/last, [a-z0-9-.], no '--' or '..'"
            )
        if "--" in name or ".." in name:
            errors.append(f"{label} name contains '--' or '..'")

    extra = set(data) - AP10_PERMITTED_KEYS
    if extra:
        errors.append(
            f"{label} has top-level keys outside the Agent Plugins 1.0 "
            f"schema: {sorted(extra)}"
        )
    # The AP1.0 schema is closed AND typed: a permitted key present with
    # the wrong type is fatal. A missing optional key stays allowed; an
    # explicit null does not count as missing and fails.
    for key in sorted(AP10_STRING_KEYS):
        if key in data and not isinstance(data[key], str):
            errors.append(
                f"{label} {key} must be a string, "
                f"got {type(data[key]).__name__}"
            )
    if "author" in data:
        author = data["author"]
        if not isinstance(author, dict):
            errors.append(f"{label} author must be an object")
        else:
            bad = set(author) - AP10_AUTHOR_KEYS
            if bad:
                errors.append(
                    f"{label} author has keys outside name/email/url: "
                    f"{sorted(bad)}"
                )
            for key in sorted(set(author) & AP10_AUTHOR_KEYS):
                if not isinstance(author[key], str):
                    errors.append(
                        f"{label} author.{key} must be a string, "
                        f"got {type(author[key]).__name__}"
                    )
    if "keywords" in data:
        keywords = data["keywords"]
        if not (
            isinstance(keywords, list)
            and all(isinstance(k, str) for k in keywords)
        ):
            errors.append(f"{label} keywords must be an array of strings")
    if "extensions" in data:
        extensions = data["extensions"]
        if not isinstance(extensions, dict):
            errors.append(f"{label} extensions must be an object")
        else:
            for ext_key, ext_value in extensions.items():
                if not isinstance(ext_value, dict):
                    errors.append(
                        f"{label} extensions.{ext_key} must be an object, "
                        f"got {type(ext_value).__name__}"
                    )
    return name, version


def _load_json(path, label, errors):
    if not path.exists():
        errors.append(f"{label} is missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{label} is not valid JSON: {exc}")
        return None


def check_manifests(root, errors):
    plugin_dir = root / "plugins" / "gp-sdk-skills"
    name_ver = []

    ap_name, ap_version = check_ap10_manifest(
        plugin_dir / "plugin.json", errors
    )
    name_ver.append(("agent-plugins-1.0", ap_name, ap_version))

    claude = _load_json(
        plugin_dir / ".claude-plugin" / "plugin.json",
        "plugins/gp-sdk-skills/.claude-plugin/plugin.json",
        errors,
    )
    if isinstance(claude, dict):
        name_ver.append(
            ("claude", claude.get("name"), claude.get("version"))
        )
    else:
        name_ver.append(("claude", None, None))

    codex = _load_json(
        plugin_dir / ".codex-plugin" / "plugin.json",
        "plugins/gp-sdk-skills/.codex-plugin/plugin.json",
        errors,
    )
    if isinstance(codex, dict):
        name_ver.append(
            ("codex", codex.get("name"), codex.get("version"))
        )
    else:
        name_ver.append(("codex", None, None))

    distinct = {(n, v) for _, n, v in name_ver}
    if len(distinct) > 1:
        errors.append(
            "plugin manifests disagree on name/version: "
            + ", ".join(
                f"{source}={name!r}/{version!r}"
                for source, name, version in name_ver
            )
        )
    if not any(n == "gp-sdk-skills" for _, n, _ in name_ver):
        errors.append("plugin manifests do not carry name gp-sdk-skills")


def check_marketplaces(root, errors):
    claude_path = root / ".claude-plugin" / "marketplace.json"
    claude = _load_json(claude_path, ".claude-plugin/marketplace.json", errors)
    if isinstance(claude, dict):
        mname = claude.get("name")
        if mname in RESERVED_MARKETPLACE_NAMES:
            errors.append(
                f".claude-plugin/marketplace.json uses reserved "
                f"marketplace name {mname!r}"
            )
        _check_marketplace_entries(claude, root, ".claude-plugin", errors)

    codex_path = root / ".agents" / "plugins" / "marketplace.json"
    codex = _load_json(
        codex_path, ".agents/plugins/marketplace.json", errors
    )
    if isinstance(codex, dict):
        _check_marketplace_entries(codex, root, ".agents/plugins", errors)


def _check_marketplace_entries(data, root, label, errors):
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(f"{label}/marketplace.json has no plugins array")
        return
    for entry in plugins:
        if not isinstance(entry, dict):
            errors.append(f"{label}/marketplace.json entry is not an object")
            continue
        name = entry.get("name")
        if not name:
            errors.append(f"{label}/marketplace.json entry has no name")
            continue
        plugin_dir = root / "plugins" / str(name)
        if not plugin_dir.is_dir():
            errors.append(
                f"{label}/marketplace.json entry {name!r} has no "
                "corresponding plugin directory"
            )
        source = entry.get("source")
        if isinstance(source, str):
            path = root / source.lstrip("./") if source.startswith("./") else None
            if path is None or not path.is_dir():
                errors.append(
                    f"{label}/marketplace.json entry {name!r} source "
                    f"{source!r} does not resolve to an existing directory"
                )
        elif isinstance(source, dict):
            spath = source.get("path")
            if not spath:
                errors.append(
                    f"{label}/marketplace.json entry {name!r} object source "
                    "has no path"
                )
            else:
                resolved = root / str(spath).lstrip("./")
                if not resolved.is_dir():
                    errors.append(
                        f"{label}/marketplace.json entry {name!r} source "
                        f"path {spath!r} does not resolve to an existing "
                        "directory"
                    )
        else:
            errors.append(
                f"{label}/marketplace.json entry {name!r} has no resolvable "
                "source"
            )


def validate(root):
    errors = []
    skill_dirs = sorted((root / "plugins").glob("*/skills/*"))
    if not skill_dirs:
        errors.append("no plugin skills found under plugins/*/skills/")
    for skill_dir in skill_dirs:
        if not skill_dir.is_dir():
            continue
        check_skill(skill_dir, errors)
    check_manifests(root, errors)
    check_marketplaces(root, errors)
    return errors


def demo():
    """Self-check: the rules fire on known-bad input."""
    import tempfile

    def make_skill(tmp, name, frontmatter=None, files=None):
        skill = pathlib.Path(tmp) / name
        (skill / "references").mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(
            frontmatter
            if frontmatter is not None
            else "---\nname: %s\ndescription: real description\n---\nbody\n" % name
        )
        (skill / "references" / "REFERENCE.md").write_text("reference\n")
        for rel, content in (files or {}).items():
            target = skill / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        return skill

    # Frontmatter: name mismatch, caps, leading dash, --, overlong description.
    with tempfile.TemporaryDirectory() as tmp:
        errors = []
        check_frontmatter(
            make_skill(
                tmp,
                "gp-x-sdk",
                "---\nname: gp-other-sdk\ndescription: d\n---\n",
            ) / "SKILL.md",
            "gp-x-sdk",
            errors,
        )
        assert any("does not match" in e for e in errors), "name mismatch should fail"

        errors = []
        check_frontmatter(
            make_skill(
                tmp,
                "Gp-sdk",
                "---\nname: Gp-sdk\ndescription: d\n---\n",
            ) / "SKILL.md",
            "Gp-sdk",
            errors,
        )
        assert any("[a-z0-9-]" in e for e in errors), "uppercase name should fail"

        errors = []
        check_frontmatter(
            make_skill(
                tmp,
                "-gp-sdk",
                "---\nname: -gp-sdk\ndescription: d\n---\n",
            ) / "SKILL.md",
            "-gp-sdk",
            errors,
        )
        assert any("starts or ends" in e for e in errors), "leading dash should fail"

        errors = []
        check_frontmatter(
            make_skill(
                tmp,
                "gp--sdk",
                "---\nname: gp--sdk\ndescription: d\n---\n",
            ) / "SKILL.md",
            "gp--sdk",
            errors,
        )
        assert any("'--'" in e for e in errors), "double dash should fail"

        errors = []
        check_frontmatter(
            make_skill(
                tmp,
                "gp-x-sdk",
                "---\nname: gp-x-sdk\ndescription: %s\n---\n" % ("x" * 1025),
            ) / "SKILL.md",
            "gp-x-sdk",
            errors,
        )
        assert any("1024" in e for e in errors), "overlong description should fail"

        errors = []
        check_frontmatter(
            make_skill(tmp, "gp-x-sdk", "---\nname: gp-x-sdk\n---\n") / "SKILL.md",
            "gp-x-sdk",
            errors,
        )
        assert any("no description" in e for e in errors), (
            "missing description should fail"
        )

        # Structure: flat companion doc, missing reference, orphan verification.
        errors = []
        flat = make_skill(
            tmp, "gp-flat-sdk", files={"REFERENCE.md": "x"}
        )
        (flat / "references" / "REFERENCE.md").unlink()
        (flat / "references" / "VERIFICATION.md").write_text("x\n")
        check_structure(flat, errors)
        assert any("flat REFERENCE.md" in e for e in errors), (
            "flat REFERENCE.md should fail"
        )
        assert any("missing" in e for e in errors), (
            "missing references/REFERENCE.md should fail"
        )
        assert any("orphan" in e for e in errors), (
            "unreferenced VERIFICATION.md should fail"
        )

        # Bare mentions: both directions, including plain prose without
        # backticks and invalid link targets (valid display labels of
        # valid targets stay exempt).
        errors = []
        bare = make_skill(
            tmp,
            "gp-bare-sdk",
            files={
                "SKILL.md": (
                    "---\nname: gp-bare-sdk\ndescription: d\n---\n"
                    "see `REFERENCE.md`, bare REFERENCE.md prose, "
                    "[X](./VERIFICATION.md), [Y](VERIFICATION.md), "
                    "[x](../references/REFERENCE.md), "
                    "`../references/REFERENCE.md`, "
                    "https://host/references/REFERENCE.md, "
                    "`references/REFERENCE.mdx`, "
                    "./references/REFERENCE.md?x, and "
                    "backticked `references/REFERENCE.md.txt` plus "
                    "trailing references/REFERENCE.md..\n"
                ),
                "references/EXTRA.md": (
                    "see `SKILL.md`, bare SKILL.md prose, foo/../SKILL.md, "
                    "../SKILL.mdx, and ../SKILL.md.foo here\n"
                ),
            },
        )
        check_mentions(bare, errors)
        assert sum("bare companion-doc mention" in e for e in errors) == 11, (
            "backticked, plain-prose, bad-target, unprefixed-path, "
            "malformed-suffix, and dot-extension mentions in SKILL.md "
            "should fail"
        )
        assert sum("bare SKILL.md mention" in e for e in errors) == 5, (
            "backticked, plain-prose, non-../, malformed-suffix, and "
            "dot-extension SKILL.md mentions in references/ should fail"
        )
        clean = make_skill(
            tmp,
            "gp-clean-sdk",
            files={
                "SKILL.md": (
                    "---\nname: gp-clean-sdk\ndescription: d\n---\n"
                    "see [REFERENCE.md](./references/REFERENCE.md), "
                    "[alt label](references/VERIFICATION.md), "
                    "`references/REFERENCE.md`, and plain "
                    "references/REFERENCE.md prose\n"
                ),
                "references/EXTRA.md": (
                    "see `../SKILL.md`, plain ../SKILL.md prose, and "
                    "[SKILL.md](../SKILL.md) here\n"
                ),
            },
        )
        errors = []
        check_mentions(clean, errors)
        assert not errors, "prefixed mentions should pass"

    # AP1.0 manifest: wrong schema, extra key, bad name.
    with tempfile.TemporaryDirectory() as tmp:
        errors = []
        ap = pathlib.Path(tmp) / "plugin.json"
        ap.write_text(
            json.dumps(
                {
                    "$schema": "https://example.com/wrong.json",
                    "name": "Bad_Name",
                    "surprise": True,
                }
            )
        )
        check_ap10_manifest(ap, errors)
        assert any("$schema must be" in e for e in errors), (
            "wrong $schema should fail"
        )
        assert any("naming" in e for e in errors), "bad AP1.0 name should fail"
        assert any("surprise" in e for e in errors), "extra key should fail"

        errors = []
        ap.write_text(
            json.dumps({"$schema": AP10_SCHEMA, "name": "ok-name"})
        )
        name, version = check_ap10_manifest(ap, errors)
        assert not errors, "minimal valid AP1.0 manifest should pass"
        assert name == "ok-name" and version is None

        # Wrong-typed permitted keys fail (closed, typed schema); a fully
        # typed valid manifest passes.
        errors = []
        ap.write_text(
            json.dumps(
                {
                    "$schema": AP10_SCHEMA,
                    "name": "ok-name",
                    "version": 3,
                    "keywords": "not-an-array",
                    "extensions": {"web": "not-an-object"},
                    "author": {"name": "GP", "email": 42},
                }
            )
        )
        check_ap10_manifest(ap, errors)
        assert any("version must be a string" in e for e in errors), (
            "numeric version should fail"
        )
        assert any("keywords must be an array" in e for e in errors), (
            "string keywords should fail"
        )
        assert any("extensions.web must be an object" in e for e in errors), (
            "string extensions value should fail"
        )
        assert any("author.email must be a string" in e for e in errors), (
            "wrong-typed author value should fail"
        )

        errors = []
        ap.write_text(
            json.dumps(
                {"$schema": AP10_SCHEMA, "name": "ok-name", "keywords": None}
            )
        )
        check_ap10_manifest(ap, errors)
        assert any("keywords must be an array" in e for e in errors), (
            "explicit-null keywords should fail, not count as missing"
        )

        errors = []
        ap.write_text(
            json.dumps(
                {
                    "$schema": AP10_SCHEMA,
                    "name": "ok-name",
                    "version": "1.0.0",
                    "description": "d",
                    "author": {"name": "GP", "url": "https://example.com"},
                    "keywords": ["payments"],
                }
            )
        )
        check_ap10_manifest(ap, errors)
        assert not errors, "fully typed valid AP1.0 manifest should pass"

    # Manifest agreement + reserved marketplace names.
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        plugin = root / "plugins" / "gp-sdk-skills"
        (plugin / ".claude-plugin").mkdir(parents=True)
        (plugin / ".codex-plugin").mkdir(parents=True)
        for rel, name, version in (
            ("plugin.json", "gp-sdk-skills", "1.0.0"),
            (".claude-plugin/plugin.json", "gp-sdk-skills", "2.0.0"),
            (".codex-plugin/plugin.json", "gp-sdk-skills", "1.0.0"),
        ):
            (plugin / rel).write_text(
                json.dumps({"name": name, "version": version})
            )
        errors = []
        check_manifests(root, errors)
        assert any("disagree" in e for e in errors), (
            "version mismatch should fail"
        )

        errors = []
        claude_market = root / ".claude-plugin"
        claude_market.mkdir(exist_ok=True)
        (claude_market / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "agent-skills",
                    "plugins": [
                        {
                            "name": "gp-sdk-skills",
                            "source": "./plugins/gp-sdk-skills",
                        }
                    ],
                }
            )
        )
        codex_market = root / ".agents" / "plugins"
        codex_market.mkdir(parents=True, exist_ok=True)
        (codex_market / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "globalpayments",
                    "plugins": [
                        {
                            "name": "gp-sdk-skills",
                            "source": "./plugins/gp-sdk-skills",
                        }
                    ],
                }
            )
        )
        check_marketplaces(root, errors)
        assert any("reserved" in e for e in errors), (
            "reserved marketplace name should fail"
        )

        # Broken source resolution.
        (claude_market / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "globalpayments",
                    "plugins": [
                        {
                            "name": "gp-sdk-skills",
                            "source": "./plugins/does-not-exist",
                        },
                        {"name": "ghost-plugin",
                         "source": "./plugins/gp-sdk-skills"},
                    ],
                }
            )
        )
        errors = []
        check_marketplaces(root, errors)
        assert sum("does not resolve" in e for e in errors) == 1, (
            "unresolvable source should fail"
        )
        assert sum("no corresponding plugin directory" in e for e in errors) == 1, (
            "ghost plugin entry should fail"
        )

    print("demo: ok")


def main(argv):
    if argv and argv[0] == "--demo":
        demo()
        return 0
    if argv:
        print("usage: validate-packaging.py [--demo]")
        return 1
    root = pathlib.Path(__file__).resolve().parent.parent
    errors = validate(root)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s)")
        return 1
    print("packaging: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
