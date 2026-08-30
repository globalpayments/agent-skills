# Global Payments Agent Skills

Agent skills for integrating the Global Payments SDKs — .NET, Java, Node.js,
PHP, Python, Go, iOS and Android — packaged as one installable plugin.

[![skills.sh](https://skills.sh/b/globalpayments-samples/agent-skills)](https://skills.sh/globalpayments-samples/agent-skills)

Every skill is grounded in real SDK source: class names, method chains,
configuration fields, and error trees are verified against the actual
`globalpayments/*` repositories and their integration test suites, not
summarized from marketing docs. Where an SDK genuinely lacks a feature (for
example, GP Ecom has no connector in the Go SDK), the skill says so.

## Skills

| Skill | Language | Focus |
|---|---|---|
| `gp-android-sdk` | Kotlin/Java | Android client SDK — GP API, GP Ecom, Netcetera 3DS2, CardFormView |
| `gp-dotnet-sdk` | C# | `GlobalPayments.Api` — GP API, GP Ecom, Portico, terminal integration |
| `gp-go-sdk` | Go | Portico gateway and UPA terminal integration (no GP API connector) |
| `gp-ios-sdk` | Swift | iOS client SDK — GP API with full 3D Secure 2, async completions |
| `gp-java-sdk` | Java | `globalpayments-sdk` — GP API, GP Ecom, Portico, 3DS2 default flow |
| `gp-node-sdk` | TypeScript | `globalpayments-api` — GP API, GP Ecom, Portico, Promise-based |
| `gp-php-sdk` | PHP | GP API, GP Ecom, Portico plus PAX/UPA/HPA/Genius terminals |
| `gp-python-sdk` | Python | `GlobalPayments.Api` — GP API, Portico, GP Ecom via `PorticoConfig` |

## Install

### Claude Code

```
/plugin marketplace add globalpayments-samples/agent-skills
/plugin install gp-sdk-skills@globalpayments
```

### Codex / ChatGPT

```
codex plugin marketplace add globalpayments-samples/agent-skills
```

then run `/plugins` in the Codex CLI to install `gp-sdk-skills`.

### Fallback — `npx skills`

```
npx skills add globalpayments-samples/agent-skills --list
npx skills add globalpayments-samples/agent-skills --all
npx skills add globalpayments-samples/agent-skills --skill gp-php-sdk
```

### Cursor, GitHub Copilot, VS Code, Kiro

These editors consume the Agent Plugins 1.0 manifest at
`plugins/gp-sdk-skills/plugin.json` directly.

## Contributing

- Run both validators before opening a PR:
  `python3 scripts/validate-packaging.py && python3 scripts/validate-sdk-skill.py --all`
- Bump `version` in all three manifests together
  (`plugins/gp-sdk-skills/plugin.json`, `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json`).
- Companion docs live under each skill's `references/` directory; keep
  `SKILL.md` under 1024 characters of frontmatter description.

## License

[MIT](LICENSE)
