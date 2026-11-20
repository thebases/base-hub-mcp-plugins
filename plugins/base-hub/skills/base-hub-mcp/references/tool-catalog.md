# Base HUB MCP tool catalog

Source of truth: the live `tools/list` of the instance you are connected to (each installed module contributes its group). Names here are the internal dotted names; `tools/list` advertises them with `.` → `_` (over 64 chars or colliding: hash suffix), and `tools/call` accepts both forms. This file mirrors the exact `InputSchema` each tool advertises over `tools/list` ; after a Base HUB upgrade, trust the live `tools/list` schema over this file.

**Cross-cutting:** `idempotency_key` (string, stable per logical operation) is **required** on `base.record.create`, `base.model.create_custom`, `website.record.create`, `website_blog.record.create`, `website.page.design_upsert` (create only), `workflow.record.create`, `workflow.import`, `knowledge.doc.create`, `auth.record.create`, `automation.record.create`, `calendar.record.create`, `credential.record.create`, `project.record.create`. The examples below omit it for brevity — add it.

## base.model.*

### `base.model.list`
No arguments. Lists registered runtime models available to the authenticated caller.

### `base.model.describe`
```json
{ "model": "tbl.partner" }
```
Returns fields, relations, runtime flags.

### `base.model.methods`
```json
{ "model": "tbl.partner" }
```
Registered runtime methods for a model.

### `base.model.fields_get`
```json
{ "model": "tbl.partner" }
```
Field metadata, UI-compatible shape.

### `base.model.create_custom`
```json
{
  "name": "tbl.partner.address",
  "label": "Partner Address",
  "description": "optional",
  "fields": [
    { "field_name": "street", "label": "Street", "data_type": "text", "is_required": true },
    { "field_name": "partner_id", "data_type": "many2one", "relation_model": "tbl.partner", "is_required": true }
  ]
}
```
- `name` and `idempotency_key` required; `fields` optional (you can add fields later with `add_field`).
- `name` is normalized: spaces → `.`, `tbl.` prefix added if missing, final name ≤ 24 chars; physical table = name with `.` → `_`.
- `bid` is always server-generated — never pass one.
- Metadata only. Nothing queryable until `base.model.publish`.
- To rename/delete the *model itself* (not a field), use `base.record.write`/`unlink` with `model: "sys.model"` — there's no `base.model.rename`/`delete_model` tool.
- `data_type` defaults to `"text"`. Relation kinds: `many2one`, `one2one` (publishable, need `relation_model`); `one2many`, `many2many` (metadata-only, `publish` rejects a model that has only these).
- `relation_model` aliases accepted: `relation`, `comodel`, `related_model`, `target_model`. `many2one: true` is shorthand for `relation_type: "many2one"`.

### `base.model.add_field`
```json
{ "model": "tbl.partner.address", "field_name": "city", "data_type": "text", "is_required": false }
```
- Required: `model`, `field_name`.
- Same relation rules as `create_custom`.
- **Rejected if the model is already published** — `base.model.unpublish` first.

### `base.model.delete_field`
```json
{ "model": "tbl.partner.address", "field_name": "notes" }
```
- Resolved by `field_name`, no id lookup needed.
- Only custom fields (added via `add_field`/`create_custom`) can be deleted — registry-synced fields on a Go-coded model are read-only (system models return 403 `system_model_protected`).
- Rejected while published — unpublish, delete, re-publish. Republish actually drops the column and its data.

### `base.model.rename_field`
```json
{ "model": "tbl.partner.address", "field_name": "notes", "new_field_name": "remarks", "new_label": "Remarks" }
```
- `new_field_name` and/or `new_label` — at least the rename target.
- Same published-model restriction as `delete_field`.

### `base.model.publish`
```json
{ "model": "tbl.account" }
```
- Superadmin identity required.
- Provisions the physical Postgres table from current `sys.model.field` catalog rows, registers the model for `base.record.*`/`create_ui`.
- Publishable `data_type`s only: `text`, `integer`, `float`, `boolean`, `date`, `datetime`, `json`, `many2one`, `one2one` (relations need `relation_model`). Anything else, including `one2many`/`many2many`, fails the whole publish.
- Not persisted across a server restart — re-publish if a model that used to work suddenly can't be read/written.
- Republishing after a field add/delete/rename reconciles the table with `ADD`/`RENAME`/`DROP COLUMN` as needed — a field delete really does drop the column and its data on republish.

### `base.model.unpublish`
```json
{ "model": "tbl.account" }
```
- Superadmin identity required.
- Takes the model out of the live runtime registry (`base.record.*` stops seeing it) without touching the catalog row or the physical table/data.
- Required first step before either editing fields on a published model, or deleting the model entirely (`base.record.unlink` on `sys.model` refuses to run while still published).

### `base.model.create_ui`
```json
{ "model": "tbl.account", "label": "Accounts" }
```
- `model` required, `label` optional (defaults to the registered label).
- Creates one list `ui.view`, one form `ui.view` (auto-generated from field metadata), and one `ui.menu` entry opening `/web/<model>`, always nested under the root `menu.main` — no parent override.
- Stamps `sys.model.has_ui = true`.
- **Additive, not idempotent** — running it again creates a second set of views/menu entries. Don't re-run "just in case."

## base.record.*

### `base.record.search_read`
```json
{ "model": "tbl.partner", "domain": [["city", "=", "Ho Chi Minh City"]], "fields": ["id","name","mobile"], "limit": 20, "offset": 0, "order": "name asc" }
```
`model` required. `limit` defaults to 20, must be positive (else 422) and is clamped to 200; no cursor, page with `offset`.

### `base.record.read`
```json
{ "model": "tbl.partner", "ids": [125], "fields": ["id","name","email"] }
```
`model` and `ids` required.

### `base.record.create`
```json
{ "model": "tbl.partner", "values": { "name": "Nguyen Minh Anh", "mobile": "0901234567" }, "idempotency_key": "create-partner-nguyen-minh-anh-1" }
```
`model`, `values`, `idempotency_key` required.

### `base.record.write`
```json
{ "model": "tbl.partner", "ids": [125], "values": { "mobile": "0909998888" } }
```
`model`, `ids`, `values` all required. `values` may be one object applied to every id, or an array of objects matching `ids` (per-record batch; one transaction, all-or-nothing).

### `base.record.unlink`
```json
{ "model": "tbl.partner", "ids": [125] }
```
`model` and `ids` required. **Special case for `model: "sys.model"`** (deleting a custom model's catalog row):
- The model must already be unpublished, or this call fails — `unlink` never implicitly takes a live model offline.
- The physical table/data is left untouched by default.
- Pass `"confirm_drop_table": true` to also permanently `DROP` the table after deleting the catalog row — irreversible, always confirm with the user before setting this.

### `base.record.call_method`
```json
{ "model": "sys.attachment", "method": "attachments_for_record", "ids": [], "args": [], "kwargs": { "sys_model": "tbl.partner", "model_id": 125 } }
```
`model` and `method` required. High-value methods:
| Model | Method | Use |
|---|---|---|
| `sys.attachment` | `attachments_for_record` | List attachments bound to one record |
| `sys.report` | `render_report` | Render HTML/PDF report output |
| `tbl.website_site` / `tbl.website_page` | `action_publish` / `action_unpublish` | Same effect as the dedicated `website.publish`/`unpublish` tools — prefer the dedicated tools for simpler arguments |

### `base.batch.execute`
```json
{ "steps": [
  { "name": "base.model.create_custom", "arguments": { "name": "invoice items", "idempotency_key": "k1" } },
  { "name": "base.model.add_field", "arguments": { "model": "tbl.invoice.items", "field_name": "qty", "data_type": "integer" } },
  { "name": "base.model.publish", "arguments": { "model": "tbl.invoice.items" } }
] }
```
All steps run in one DB transaction; any failure rolls back earlier steps. Cannot nest `base.batch.execute`. ACL applies per step.

## Optional groups (appear in `tools/list` only when the owning module is installed for the tenant)

All `<group>.record.*` tools mirror `base.record.*` (same argument shapes, `write` accepts the per-id values array) but restrict `model` to an allowlist enum. Create requires `idempotency_key`.

## website.*

Models (enum on `model`): `tbl.website_site`, `_page`, `_domain`, `_asset`, `_theme`, `_snippet`, `_menu`, `_redirect`, `_page_translation`, `_form_submission` (`publish`/`unpublish`: site and page only). Tool names keep the `website.` prefix. There is no `website.page.version` model. Pages have `visibility` (`public`|`logged_in`), `body_html` (sanitized), nested `seo`.

### `website.record.search_read` / `read` / `create` / `write` / `unlink`
For SEO prefer `website.seo.upsert` — page SEO is a nested `seo` JSON on `tbl.website_page`.

### `website.seo.upsert`
```json
{ "target": "page", "page_id": 42, "seo_title": "About Our Company", "include_in_sitemap": true }
```
- `target` required: `"site"` or `"page"`.
- `site` → `site_id` required; writes `default_seo_name`, `default_seo_desc`, `default_canonical_base`, `default_robots`, `robots_txt`, `sitemap_enabled` onto `tbl.website_site`.
- `page` → `page_id` required; merges `seo_title`, `seo_description`, `canonical_path`, `robots_directives`, `og_title`, `og_description`, `og_image_url`, `structured_data_json`, `include_in_sitemap` into the page's `seo` object.
- Only the fields you pass change.

### `website.page.design_upsert`
```json
{ "site_id": 1, "name": "About Us", "route_path": "/about", "html": "<main>...</main>", "idempotency_key": "about-page-1" }
```
- Writes `html` (sanitized into `body_html`: scripts, `<style>`, iframes, svg, event handlers and unsafe URLs removed; forms keep no action/method, use `data-bh-form`) **and publishes** the page in one call.
- Omit `page_id` → new page: `site_id`, `name`, `idempotency_key` required; `is_homepage` optional. `route_path` is accepted but the server always derives it from `name` (`/<slug-of-name>`, `/` for the homepage), so pick the name for the URL you want. Pass `page_id` → update that page (no key needed).
- Response `{page_id, page}`; `deploy_path` is set on success; fields over 4 KB are replaced by `<field>_bytes` (read content back with `website.record.read`).
- If publish fails after the save, the draft is kept (no rollback) — fix and call `website.publish`.
- **Chunked mode** for long pages: `upload_id` (stable id), `html_chunk`, `chunk_index` (0-based), `chunk_total` (same on every call). Non-final calls only buffer and return `{upload_id, chunk_index, chunk_total, chunks_received, complete:false}`; the final chunk assembles, writes and publishes, and is the only call that needs `idempotency_key`/`page_id`/`site_id`/`name`. Chunks can arrive out of order or be retried; buffered uploads expire after ~2h. Don't mix `html` with chunk args.

### `website.snippet.list`
`{ "group": "intro", "search": "hero" }` (both optional). Read-only; returns builder blocks (key, name, group, keywords, class, sanitized html). Groups: intro, content, columns, text, images, people, catalog, social, contact.

### `website.publish` / `website.unpublish`
```json
{ "model": "tbl.website_page", "ids": [42] }
```
`model` (`tbl.website_site` or `tbl.website_page`) and `ids` required. Site-level covers every page.

## website_blog.*

Needs the `website-blog` module. Models: `tbl.website_blog_blog`, `_post`, `_tag`, `_category`.
- `website_blog.record.search_read` / `read` / `create` / `write` / `unlink` mirror `base.record.*` (create needs `idempotency_key`; `write` `values` is a single object here). Post filters: `state` (`draft`|`published`|`archived`), `blog_id`, `published_at`.
- Post create needs `name` + `blog_id`; `content` is HTML (sanitized); `slug` generated if omitted; `state` defaults `draft`. Changing `slug`/`name`/`state`/`blog_id` needs exactly one id. Deleting a blog cascades to its posts.
- `website_blog.post.publish` / `unpublish` / `archive` / `duplicate` `{ "ids": [postId] }` (exactly one id). Publish with a future publish date stays hidden until then; `duplicate` returns a new draft.

## workflow.*

Models: `base.workflow`, `base.workflow.action`, `.edge`, `.trigger`, `.credential`, `.run`, `.outbound`, `.action.catalog`.
- `workflow.export` `{ "workflow_id": N }` → `{flow, actions, triggers, layout}`.
- `workflow.import` `{ "flow": {...}, "actions": [...], "triggers": [...], "layout": {...}, "idempotency_key": "..." }` — creates a new workflow; name/topic are copy-suffixed on collision.
- `workflow.replace_action_sequence` `{ "workflow_id": N, "steps": [...] }` — deletes all existing actions, then recreates in order. Destructive: export first if unsure.
- `workflow.replace_workflow_edges` `{ "workflow_id": N, "edges": [...] }` — same for DAG edges; only meaningful when `execution_mode` is `"dag"`.
- **Publishing has no `workflow.*` tool:** a workflow runs only its published snapshot, new or edited workflows are `draft`. Use `base.record.call_method` on `base.workflow` with `validate`, then `publish`, then `set_active` (kwargs `{active: true}`). Runs: `base.workflow.run` (`status`, `last_error`, `step_runs`); methods `replay_run`, `cancel_run`. Full recipe: `references/playbook-workflow-automation.md`.

## knowledge.*

Namespaces: `base`, `user_guide` (read-only), `public` (read-write). Paths are namespace-prefixed (`public/notes/todo.md`).
- `knowledge.doc.list` (no args); `knowledge.doc.find` `{query}` (name/filename substring); `knowledge.doc.search` `{query}` (content-ranked); `knowledge.doc.read` `{path}`.
- `knowledge.doc.create` `{path, content, idempotency_key}` (fails if exists); `knowledge.doc.update` `{path, content}` (overwrite); `knowledge.doc.rename` `{from_path, to_path}`; `knowledge.doc.delete` `{path}`.

## automation.*
Models `automation.action`, `automation.cron`. `automation.action.run` `{ "action_id": N }` runs one action now through the same path a due cron uses — it really executes the configured lua/sys_model/go_handler behavior, so confirm first.

## calendar.*
Models `base.calendar.recurrence`, `base.calendar.recurrence.exception`.
- `calendar.occurrences` `{sys_model, date_from, date_to, domain?}` — plain records plus expanded recurring occurrences for `[date_from, date_to)`; recurring rows carry `is_recurring`, `recurrence_id`, `master_record_id`, `occurrence_date`.
- `calendar.reschedule_occurrence` `{recurrence_id, original_occurrence_date, new_datetime, scope}` with `scope` ∈ `this` (writes an exception) / `following` (ends the rule the day before and starts a new one) / `all` (shifts the whole rule).

## bus.*
`bus.record.search_read` / `read` on `base.service.bus` only (append-only log). Writes only via `bus.publish` `{channels, event_type, payload}`; `bus.poll` (events newer than `last_id`), `bus.recent` (newest first, default 50), `bus.last_id`, `bus.get_default_channels`.

## project.*

Module `project` (depends `base`, `base-calendar`, `discuss`). Models (enum on `model`): `tbl.project`, `tbl.project_stage`, `tbl.project_task_type`, `tbl.project_task_stage_personal`, `tbl.project_tag`, `tbl.project_milestone`, `tbl.project_update`, `tbl.project_collaborator`, `tbl.project_role`, `tbl.project_task`.
- `project.record.search_read` / `read` / `create` / `write` / `unlink` mirror `base.record.*`. `create` requires `model`, `values` (object), `idempotency_key`. `write` requires `model`, `ids`, `values` (one object for every id, or an array of objects, one per id in order).
- No verbs beyond CRUD. Resolve `project_id`, stage, tag and collaborator ids by searching the related model first.

## auth.* / credential.*
- `auth.record.*` → `sys.oauth_client`. On create, a missing `client_secret` is generated and the plaintext is returned **only in that response**. `client_secret` is never returned by reads. Rotate via `base.record.call_method` `generate_client_secret` (confirm with the user first).
- `credential.record.*` → `sys.credential` (`name`, `credential_type`, `auth_url`, `user_name`/`password` or `client_id`/`client_secret`). Secrets are encrypted at rest and never returned. Force re-auth via `base.record.call_method` `login`.

---

## JSON-RPC envelope (for raw `/mcp` calls, not needed when using an MCP-native client)

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "base.record.search_read",
    "arguments": { "model": "tbl.partner", "fields": ["id","name","email"], "limit": 10 }
  }
}
```
`initialize` (`params.protocolVersion`) and `tools/list` (no params) work the same way. See the user guide's "GPT-Action-friendly schema" section for a full OpenAPI mirror of `/mcp/health`, `/mcp/tools`, and `/mcp` if building a non-MCP-native wrapper.
