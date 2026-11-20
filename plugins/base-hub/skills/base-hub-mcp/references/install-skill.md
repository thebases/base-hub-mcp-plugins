# Installing this skill in Claude, Codex and Gemini

This folder follows the open Agent Skills format: a `SKILL.md` with only `name`, `description`, `compatibility` and `metadata` in its frontmatter (description under 1,024 characters), plus `references/` and `evals/`. Claude, OpenAI Codex and Gemini CLI load the same folder unchanged. The skill only teaches the agent how to use the tools; each client still needs the Base HUB MCP server attached (`references/connecting-clients.md`).

## Per project

Put (or link) the `base-hub-mcp` folder in the project's skills folder:

| Agent | Project folder | Check it loaded |
|---|---|---|
| Claude Code | `.claude/skills/base-hub-mcp/` | ask "what skills do you have?" or type `/base-hub-mcp` |
| OpenAI Codex (CLI, IDE) | `.agents/skills/base-hub-mcp/` | `/skills`, or mention `$base-hub-mcp` |
| Gemini CLI | `.agents/skills/base-hub-mcp/` or `.gemini/skills/base-hub-mcp/` | `/skills list` |

## For one user, in every project

Link or copy the folder into each agent's personal skills folder:

```bash
SKILL=/path/to/base-hub-mcp
ln -s "$SKILL" ~/.claude/skills/base-hub-mcp   # Claude Code
ln -s "$SKILL" ~/.agents/skills/base-hub-mcp   # Codex and Gemini CLI both read ~/.agents/skills
```

`~/.codex/skills/` (older Codex) and `~/.gemini/skills/` (Gemini CLI) also work if you prefer per-tool folders. Restart the agent afterwards.

## Chat apps

- **Claude apps (claude.ai, Desktop):** zip the folder (`base-hub-mcp/` at the zip root) and upload it under Settings → Capabilities → Skills, if your plan has skills. Otherwise paste `references/chat-instructions.md` into a Project.
- **ChatGPT (GPTs, Projects):** cannot load skill folders; paste `references/chat-instructions.md` into the instructions and attach the Base HUB app.
- **Gemini app (Gems):** paste `references/chat-instructions.md` into the Gem; it cannot call Base HUB tools until the Gemini app supports custom MCP servers, so use Gemini CLI for real work.

## Keeping it portable

When you edit `SKILL.md`, keep it vendor-neutral: no client-specific tool prefixes as the only form, no frontmatter fields outside `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`, and keep `description` under 1,024 characters. Codex and Gemini CLI skip a skill whose frontmatter fails those rules.
