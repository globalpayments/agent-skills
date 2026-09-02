# Global Payments Agent Skills

Integration guidance and copy-ready examples for the Global Payments SDKs in
.NET, Java, Node.js, PHP, Python, Go, iOS, and Android. The eight skills ship
as one installable plugin.

[![skills.sh](https://skills.sh/b/globalpayments/agent-skills)](https://skills.sh/globalpayments/agent-skills)

Each skill records verified class names, method chains, configuration fields,
and error trees. The material comes from SDK source, sample code, and
integration tests where they are available. Unsupported paths are called out
instead of guessed. The Go SDK skill, for example, notes that Go supports
Portico and UPA, not GP API or GP Ecom.

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
/plugin marketplace add globalpayments/agent-skills
/plugin install gp-sdk-skills@globalpayments
```

### Codex / ChatGPT

```
codex plugin marketplace add globalpayments/agent-skills
```

Then run `/plugins` in the Codex CLI to install `gp-sdk-skills`.

### Cursor, GitHub Copilot, VS Code, Kiro

These editors read the Agent Plugins 1.0 manifest at
`plugins/gp-sdk-skills/plugin.json`.

### Others — `npx skills`

```
npx skills add globalpayments/agent-skills --list
npx skills add globalpayments/agent-skills --all
npx skills add globalpayments/agent-skills --skill gp-php-sdk
```

## Contributing

- Run both validators before opening a PR:
  `python3 scripts/validate-packaging.py && python3 scripts/validate-sdk-skill.py --all`
- Bump `version` in all three manifests together:
  `plugins/gp-sdk-skills/plugin.json`, `.claude-plugin/plugin.json`, and
  `.codex-plugin/plugin.json`.
- Keep companion docs under each skill's `references/` directory.
- Keep each `SKILL.md` frontmatter description within the 1024-character cap.

## License

[MIT](LICENSE)
