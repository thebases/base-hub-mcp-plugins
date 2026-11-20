# Playbook: a new kind of record with its own screen

Use when the user wants to track something Base HUB doesn't have yet ("equipment loans", "suppliers", "training sessions") and wants to manage it in the app. Argument shapes: `tool-catalog.md` → base.model.*.

## 1. First, make sure it's really new

`base.model.list`, then check the obvious candidates (SKILL.md §7): contacts are `tbl.partner`, tasks are `tbl.project_task`, tickets are `tbl.helpdesk_ticket`, files are `sys.attachment`. Propose a custom model only when nothing fits, and say why.

## 2. Design with the user

Turn the business description into a short field list and confirm it:

| User says | Field |
|---|---|
| name, title, note, code | `text` |
| quantity, count | `integer` |
| price, amount, weight | `float` (money: say there is no currency/precision handling) |
| yes/no, active, returned | `boolean` |
| due date / time | `date` / `datetime` |
| who/which customer, linked record | `many2one` + `relation_model` (e.g. `tbl.partner`) |
| free-form structured data | `json` |

- **Publishable field types:** `text`, `integer`, `float`, `boolean`, `date`, `datetime`, `json`, `many2one`, `one2one`. A model with only `one2many`/`many2many` is rejected; those stay metadata-only. There is no selection/dropdown type: use `text` and tell the user the allowed values aren't enforced.
- Model `name` is normalized: spaces → `.`, `tbl.` prefix added, ≤ 24 chars total. Pick a short name (`asset loan` → `tbl.asset.loan`). Max 1000 fields/model; duplicate names (case/whitespace-insensitive) rejected.

## 3. Build (4 steps, in order)

1. `base.model.create_custom` (`name`, `label`, `fields`, `idempotency_key`).
2. `base.model.add_field` for anything not in step 1.
3. `base.model.publish`: creates the real table. **`publish`/`unpublish` need superadmin.** On failure, explain that an admin must publish, or use an existing live model.
4. `base.model.create_ui` (`model`, `label`): one list view, one form view, one menu under the main menu. **Once only**: it's additive, a second call duplicates views/menus.

Steps 1–3 can run atomically in `base.batch.execute` (rollback on failure). Then verify: `base.record.create` a sample record only if the user agrees (or just `base.record.search_read` to prove the model is live), and tell the user where the menu is.

## 4. Invariants

- **Metadata != live.** `create_custom` / `add_field` only write `sys.model`/`sys.model.field` rows; nothing is queryable via `base.record.*` until `base.model.publish`. "Created the model but can't read/write" means publish, not re-create.
- **Field mutation needs unpublish first.** `add_field`/`delete_field`/`rename_field` fail on a published model: `unpublish`, change, `publish`. Delete/rename alters or drops the physical column on republish: a real schema change, confirm it (deleted field = deleted data).
- **Publish state doesn't survive server restart** (no boot rehydration of `PUBLISHED` rows; also affects multi-replica where one process ran the publish). If a custom model suddenly fails or works intermittently, re-run `base.model.publish` first.
- **`create_ui` is additive:** a second call duplicates views/menus; don't re-run "to make sure."
- **Go-registered models are protected:** `create_custom`/`add_field` on system models returns 403 `system_model_protected`; only MCP-created models can have fields edited. "Add a field to contacts" is a development-team request, not something you can do; offer a linked custom model instead (e.g. `tbl.partner.extra` with a `many2one` to `tbl.partner`).
- Rename/delete the model itself: `base.record.write`/`unlink` on `sys.model`; unlink requires it unpublished, and only `confirm_drop_table: true` drops the data (irreversible, explicit confirmation).

## 5. Make it useful

Ask whether the new model needs automation (reminder when a loan is overdue → automation cron or workflow), a report (needs the development team for a new template), or data import (create records in batches with stable idempotency keys).
