#!/usr/bin/env python3
"""Validate a gp-*-sdk skill directory against the structure contract.

Usage:
    python3 scripts/validate-sdk-skill.py skills/gp-java-sdk
    python3 scripts/validate-sdk-skill.py --all

Exits 0 when every checked skill passes, 1 otherwise.
"""

import pathlib
import re
import sys

SKILL_SECTIONS = [
    r"Source Hierarchy",
    r"Developer Portal Pages",
    r"Sample Repos",
    r"Quick Reference",
    r"Code Reference",
    r"Test Cards",
    r"Execution Rules",
]

REFERENCE_SECTIONS = [
    r"Installation",
    r"Gateway Configuration",
    r"Payment Methods",
    r"Core Transactions",
    r"Address Verification",
    r"Hosted Fields|Card Collection",
    r"Tokenization",
    r"Recurring Billing",
    r"3D Secure 2",
    r"Reporting",
    r"Error Handling",
]

# Soft bounds. Go, iOS and Android may legitimately land shorter.
SKILL_LINES = (90, 160)
REFERENCE_LINES = (350, 950)

PAN = re.compile(r"(?<!\d)\d{13,19}(?!\d)")
HEADING = re.compile(r"^##\s+(.*?)\s*$")
FENCE = re.compile(r"^\s*```(.*)$")


def read(path):
    return path.read_text(encoding="utf-8").splitlines()


def check_frontmatter(lines, expected_name, errors):
    if not lines or lines[0].strip() != "---":
        errors.append("SKILL.md does not start with '---' frontmatter")
        return
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append("SKILL.md frontmatter is not closed with '---'")
        return

    block = lines[1:end]
    name = None
    has_description = False
    for i, line in enumerate(block):
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip()
            if len(name) >= 2 and name[0] == name[-1] and name[0] in ("'", '"'):
                name = name[1:-1]
        if line.startswith("description:"):
            value = line.split(":", 1)[1].strip()
            # Body is either inline on this line, or a block scalar below it.
            has_description = bool(value) and (
                value in ("|", ">") or len(value) > 1
            )
            if value not in ("|", ">") and value and not (
                value.startswith(('"', "'"))
            ) and ": " in value:
                errors.append(
                    "SKILL.md description is an unquoted plain scalar "
                    "containing ': ' — YAML will not parse it"
                )
            if value in ("|", ">"):
                body = [b for b in block[i + 1:] if b.strip()]
                has_description = bool(body)

    if name != expected_name:
        errors.append(
            f"SKILL.md frontmatter name is {name!r}, expected {expected_name!r}"
        )
    if not has_description:
        errors.append("SKILL.md frontmatter has no non-empty description")


def check_sections(lines, patterns, label, errors):
    headings = [m.group(1) for m in (HEADING.match(l) for l in lines) if m]
    cursor = 0
    for pattern in patterns:
        rx = re.compile(pattern, re.IGNORECASE)
        for i in range(cursor, len(headings)):
            if rx.search(headings[i]):
                cursor = i + 1
                break
        else:
            errors.append(
                f"{label} is missing section matching '{pattern}' "
                "(or it appears out of order)"
            )


def check_fences(lines, label, errors):
    in_fence = False
    for n, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if not m:
            continue
        if in_fence:
            in_fence = False
            continue
        in_fence = True
        if not m.group(1).strip():
            errors.append(f"{label}:{n} opening code fence has no language tag")
    if in_fence:
        errors.append(f"{label} has an unclosed code fence")


def check_pans(lines, label, warnings):
    # Sandbox test card numbers are published test data and are acceptable
    # in these reference docs. This is an advisory only — it does not fail
    # the build — kept so a human can eyeball where bare digit runs land.
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("|"):
            continue  # markdown table row — cited test-card tables live here
        if PAN.search(line):
            warnings.append(
                f"{label}:{n} contains a bare 13-19 digit number outside a "
                "table row — check it's a cited sandbox test card"
            )


def check_length(lines, bounds, label, warnings):
    low, high = bounds
    if not low <= len(lines) <= high:
        warnings.append(
            f"{label} is {len(lines)} lines, outside the {low}-{high} guide band"
        )


def validate(skill_dir):
    errors, warnings = [], []
    name = skill_dir.name
    skill = skill_dir / "SKILL.md"
    reference = skill_dir / "references" / "REFERENCE.md"

    if not skill.exists():
        errors.append(f"{name}/SKILL.md is missing")
    if not reference.exists():
        errors.append(f"{name}/references/REFERENCE.md is missing")
    if errors:
        return errors, warnings

    skill_lines = read(skill)
    reference_lines = read(reference)

    check_frontmatter(skill_lines, name, errors)
    check_sections(skill_lines, SKILL_SECTIONS, f"{name}/SKILL.md", errors)
    check_sections(
        reference_lines, REFERENCE_SECTIONS, f"{name}/REFERENCE.md", errors
    )
    for lines, label in (
        (skill_lines, f"{name}/SKILL.md"),
        (reference_lines, f"{name}/REFERENCE.md"),
    ):
        check_fences(lines, label, errors)
        check_pans(lines, label, warnings)

    check_length(skill_lines, SKILL_LINES, f"{name}/SKILL.md", warnings)
    check_length(
        reference_lines, REFERENCE_LINES, f"{name}/REFERENCE.md", warnings
    )
    return errors, warnings


def main(argv):
    root = pathlib.Path(__file__).resolve().parent.parent
    if argv and argv[0] == "--all":
        targets = sorted(root.glob("plugins/*/skills/gp-*-sdk"))
    elif argv:
        targets = [pathlib.Path(a).resolve() for a in argv]
    else:
        print("usage: validate-sdk-skill.py <skill-dir>... | --all")
        return 1

    if not targets:
        print("ERROR: no skill directories matched")
        return 1

    failed = False
    for target in targets:
        errors, warnings = validate(target)
        for w in warnings:
            print(f"WARN:  {w}")
        for e in errors:
            print(f"ERROR: {e}")
            failed = True
        if not errors:
            print(f"PASS:  {target.name}")
    return 1 if failed else 0


def demo():
    """Self-check: the rules fire on known-bad input."""
    errs = []
    check_fences(["```", "x", "```"], "t", errs)
    assert errs, "untagged fence should fail"
    errs = []
    check_fences(["```php", "x", "```"], "t", errs)
    assert not errs, "tagged fence should pass"
    warns = []
    check_pans(["$card->number = '4263970000005262';"], "t", warns)
    assert warns, "bare PAN should warn"
    warns = []
    check_pans(["| `4263970000005262` | Frictionless | `05` |"], "t", warns)
    assert not warns, "PAN in a table row should pass"
    errs = []
    check_sections(["## Installation", "## Reporting"], [r"Reporting", r"Installation"], "t", errs)
    assert errs, "out-of-order sections should fail"
    errs = []
    check_sections(
        ["## Foo", "### notes on Recurring Billing here", "## Bar"],
        [r"Recurring Billing"], "t", errs,
    )
    assert errs, "a ### subheading must not satisfy a required ## section"

    # check_frontmatter: name-matches-directory is a binding constraint.
    errs = []
    check_frontmatter(
        ["---", "name: gp-php-sdk", "description: a real description", "---"],
        "gp-php-sdk", errs,
    )
    assert not errs, "matching name should pass"
    errs = []
    check_frontmatter(
        ["---", "name: gp-other-sdk", "description: a real description", "---"],
        "gp-php-sdk", errs,
    )
    assert errs, "mismatched name should fail"
    errs = []
    check_frontmatter(
        ["---", 'name: "gp-php-sdk"', "description: a real description", "---"],
        "gp-php-sdk", errs,
    )
    assert not errs, "quoted name matching should pass"
    errs = []
    check_frontmatter(
        ["---", "name: gp-php-sdk", "description:", "---"],
        "gp-php-sdk", errs,
    )
    assert errs, "missing/empty description should fail"
    errs = []
    check_frontmatter(
        ["---", "name: gp-php-sdk", "description: foo: bar baz", "---"],
        "gp-php-sdk", errs,
    )
    assert errs, "unquoted plain scalar containing ': ' should fail"

    print("demo: ok")


if __name__ == "__main__":
    if sys.argv[1:2] == ["--demo"]:
        demo()
    else:
        sys.exit(main(sys.argv[1:]))
