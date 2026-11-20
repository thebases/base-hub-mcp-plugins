# Troubleshooting

| Symptom | Cause → action |
|---|---|
| "Model not found" | Wrong name / not accessible → `base.model.list`, confirm exact name |
| Metadata created but CRUD fails | Not published → `base.model.publish` (superadmin) |
| `publish` rejects model | Only `one2many`/`many2many` fields, or relation field missing `relation_model` → check types in `references/tool-catalog.md` |
| Relation write fails | Guessed/stale ID → search related model, resolve real ID, retry |
| Non-`base.*` tool "unknown" / `tool_not_found` | Module not installed for tenant (or 30s cache) → check `tools/list`, ask admin; don't fall back to `base.record.*` |
| Create rejected, missing `idempotency_key` | Add a stable key; reuse on retry |
| `model_not_found` with `see also` hint | Hint points to a knowledge doc → verify name via `base.model.list`, read doc via `knowledge.doc.read` |
| Report won't render | No matching `sys.report` row → search first; if none, say a template/definition must be added |
| 401 `authorization is required` / `must use the Bearer scheme` / `invalid bearer token` | Missing/wrong/expired OAuth token; `X-API-Key` is not accepted on `/mcp` → mint a new token via `/oauth/token` |
| 401 `oauth token is not valid for the requested database` / 400 on database | Token minted for another tenant, or `?db=`/`X-Database-Name` missing/unknown → align them |
| `403 permission_denied` | The user's role lacks model/method access → fix RBAC or use a user with access; not a key-scope issue |
| `404 method_not_found` on `call_method` for a method that exists in code | Method is `Internal` (refused for clients) or name wrong → `base.model.methods`; not callable via MCP |
| Empty result but data should exist | Record rules/company scope filter rows (no error raised) → check the user's groups/company |
| Page/blog tool `tool_not_found` | `website`/`website-blog` module not installed for the tenant |
| Attachment invisible | Scope/permission mismatch → inspect `sys_model`, `model_id`, `company_id`, `user_id`, `group_id`, `is_public`; confirm bound record is readable |

| Client says the tool result is malformed (`structuredContent` expected record/object) | Server returned a list in `structuredContent` (Base HUB bug) → report to the development team; retrying won't help |
| Workflow created but nothing happens | Still `draft` or inactive → `base.record.call_method` `validate` → `publish` → `set_active`; check `base.workflow.run` for `last_error` |
| Cron stopped running | `fail_count` reached `max_failures` → read `last_run_status`, fix the action, set `active` true again |
| New page has the wrong URL | `route_path` is derived from the page `name` → rename the page |
| Menu change not visible on the site | Menu/header/theme are copied at publish → `website.publish` on the site |
| Images missing for visitors | Attachment not `is_public` → set it, or re-create the attachment with `is_public: true` |

Otherwise see the user guide's Troubleshooting and FAQ.
