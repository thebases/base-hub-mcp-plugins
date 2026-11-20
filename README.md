# Base HUB plugin marketplace

A Claude plugin marketplace containing one plugin, **base-hub**:

- **Skill** `base-hub-mcp`: the Base HUB Operation Agent (websites, knowledge, records, custom models, workflows, automations).
- **MCP connector** `base-hub`: connects to *your* Base HUB tenant. Each user is asked for their own MCP URL and tenant database, so one plugin works for every tenant.

## Install

In Claude Code:

```text
/plugin marketplace add thebases/base-hub-mcp-plugins
/plugin install base-hub@base-hub-marketplace
```

In the Claude app, open **Add marketplace**, enter `thebases/base-hub-mcp-plugins` and click **Sync**, then install **Base HUB**.

When the plugin is enabled you are prompted for:

| Setting | Example | Notes |
|---|---|---|
| Base HUB MCP URL | `https://your-tenant.thebase.com/mcp` | Must be the full URL ending in `/mcp` |
| Tenant database name | `base-home` | Sent as the `X-Database-Name` header |

Then run `/mcp` and sign in to Base HUB (OAuth). Change the values later in `/config`.

### Upload as a zip

Do not zip the repo root, because it is a marketplace and has no `plugin.json`. Build the plugin zip instead:

```bash
python scripts/build_plugin_zip.py   # -> dist/base-hub.zip
```

Upload `dist/base-hub.zip`. It has `.claude-plugin/plugin.json` at the zip root.

## Troubleshooting

- Server missing in `/mcp`: a required setting is empty. Open `/config` and fill both values, or check the `/plugin` Errors tab.
- `401 oauth token is not valid for the requested database`: the database name does not match your sign-in. Fix the tenant database value and sign in again.
- Wrong tenant: change the two values in `/config`, then reconnect from `/mcp`.

## Layout

```text
.claude-plugin/marketplace.json
plugins/base-hub/
├── .claude-plugin/plugin.json     manifest + userConfig prompts
├── .mcp.json                      MCP server using ${user_config.*}
└── skills/base-hub-mcp/           the skill (SKILL.md, references/, evals/)
```

## Validate

```bash
claude plugin validate ./plugins/base-hub
claude plugin validate .
```
