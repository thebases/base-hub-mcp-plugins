# Core tools at a glance

Dotted names below; clients see wire names with `.` → `_` (`base.model.list` = `base_model_list`). See SKILL.md §1.

| Tool | Use |
|---|---|
| `base.model.list` / `describe` / `methods` / `fields_get` | List accessible models / fields+relations / custom methods / detailed field metadata |
| `base.record.search_read` / `read` | Search with domain / read by ID |
| `base.record.create` / `write` / `unlink` | CRUD |
| `base.record.call_method` | Run a model method, e.g. `attachments_for_record`, `render_report` |
| `base.model.create_custom` / `add_field` / `delete_field` / `rename_field` | Edit **catalog metadata only** for a custom model (no live table yet) |
| `base.model.publish` / `unpublish` | Provision/tear down the live Postgres table (superadmin only) |
| `base.model.create_ui` | Scaffold default list/form view + menu for a published model |
| `base.batch.execute` | `{steps:[{name,arguments}]}` in one DB transaction, all-or-nothing; cannot nest |
| `website.record.*` | CRUD on `tbl.website_{site,page,domain,asset,theme,snippet,menu,redirect,page_translation,form_submission}` |
| `website.seo.upsert` | Set SEO fields on a site or a page's nested `seo` object |
| `website.page.design_upsert` | Write a page's `html` **and publish it** in one call (chunked upload supported) |
| `website.snippet.list` | List native-builder blocks (`group`, `search` filters); read-only |
| `website.publish` / `unpublish` | Deploy / take offline a `tbl.website_site` or `tbl.website_page` |
| `website_blog.record.*`, `website_blog.post.publish` / `unpublish` / `archive` / `duplicate` | Blog/post/tag/category CRUD; post lifecycle (exactly one post id) |
| `workflow.record.*`, `workflow.export` / `import`, `workflow.replace_action_sequence` / `replace_workflow_edges` | Workflow CRUD; export/import a flow; rewrite steps or DAG edges |
| `knowledge.doc.list/find/search/read/create/update/rename/delete` | Markdown knowledge tree; only `public` namespace writable |
| `automation.record.*`, `automation.action.run` | `automation.action` / `automation.cron` CRUD; run an action now |
| `calendar.record.*`, `calendar.occurrences`, `calendar.reschedule_occurrence` | Recurrence rules; expanded occurrences; move one/following/all |
| `bus.publish/poll/recent/last_id/get_default_channels`, `bus.record.search_read/read` | Service bus; log model read-only |
| `auth.record.*` (`sys.oauth_client`), `credential.record.*` (`sys.credential`) | OAuth clients / named credentials; secrets never returned |
| `project.record.*` | Module `project`. Projects, stages, tasks, milestones, tags, roles |

Argument shapes: `references/tool-catalog.md`. Installed-module differences and project/helpdesk/EDC rules: `references/modules.md`.
