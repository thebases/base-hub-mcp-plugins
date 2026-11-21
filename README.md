# Base HUB plugin marketplace

A Claude plugin marketplace containing one plugin, **base-hub**:

- **Skill** `base-hub-mcp`: the Base HUB Operation Agent (websites, knowledge, records, custom models, workflows, automations).
- **MCP connector** `base-hub`: connects to `https://edc.thebase.vn/mcp`.

## Install

In Claude Code:

```text
/plugin marketplace add thebases/base-hub-mcp-plugins
/plugin install base-hub@base-hub-marketplace
```

In the Claude app, open **Add marketplace**, enter `thebases/base-hub-mcp-plugins` and click **Sync**, then install **Base HUB**.

Then run `/mcp` and sign in to Base HUB (OAuth).

### Upload as a zip

Do not zip the repo root, because it is a marketplace and has no `plugin.json`. Build the plugin zip instead:

```bash
python scripts/build_plugin_zip.py   # -> dist/base-hub.zip
```

Upload `dist/base-hub.zip`. It has `.claude-plugin/plugin.json` at the zip root.

## Troubleshooting

- Server missing in `/mcp`: check the `/plugin` Errors tab.
- Signed in to the wrong account: reconnect from `/mcp` and sign in again.

## Layout

```text
.claude-plugin/marketplace.json
plugins/base-hub/
├── .claude-plugin/plugin.json     manifest
├── .mcp.json                      MCP server (https://edc.thebase.vn/mcp)
└── skills/base-hub-mcp/           the skill (SKILL.md, references/, evals/)
```

## Validate

```bash
claude plugin validate ./plugins/base-hub
claude plugin validate .
```
