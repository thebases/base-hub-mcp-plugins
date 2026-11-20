# Installed modules: what this Base HUB can do

A Base HUB instance is a set of installed modules. The MCP transport and the `base.*` tools are always there; every other tool group, and every business model, exists only when its module is installed for the caller's tenant database. Two instances can look very different, so never assume: read `tools/list` (your tool names) and `base.model.list` first, and trust them over this file.

Tool names may appear as wire names (`.` → `_`, e.g. `project_record_search_read`); see SKILL.md §1.

## How to tell what is installed

| You see | Module(s) installed | Notes |
|---|---|---|
| `base.*` tools | `base`, `base-mcp` | Always present when connected |
| `workflow.*` | `base-workflow` | Workflow CRUD, export/import, step and edge rewrites |
| `knowledge.doc.*` | `knowledge` | Markdown knowledge tree; also the in-app docs |
| `auth.*` | `base-auth` | OAuth clients (`sys.oauth_client`) |
| `automation.*` | `base-automation` | Actions and crons |
| `bus.*` | `base-bus` | Service bus |
| `calendar.*` | `base-calendar` | Recurrence rules and occurrences |
| `credential.*` | `base-credential` | Named credentials (`sys.credential`) |
| `website.*` | `website` | Sites, pages, SEO, publish |
| `website_blog.*` | `website-blog` | Blogs and posts |
| `project.*` | `project` | Projects and tasks |
| `tbl.helpdesk_*` models, no tools | `helpdesk` | Use `base.*` |
| `edc.*` models, no tools | `edc` | Payment terminals; use `base.*`, rules below |

A missing group means the module is not installed for this tenant (a disabled tool and a nonexistent one look the same). Tell the user to ask an admin to install it; don't imitate it with `base.record.*` on models that don't exist. The tool list refreshes within ~30 s of an install or uninstall.

Models without their own tool group (helpdesk, EDC, and any other business module) are reached through `base.*`: `base.model.describe` / `fields_get` first, then `base.record.*`, and `base.record.call_method` for their runtime methods (list them with `base.model.methods`; don't guess names).

## `project.*` (module `project`)

`project.record.*` (same shapes as `base.record.*`; create needs `idempotency_key`) restricted to: `tbl.project`, `tbl.project_stage`, `tbl.project_task_type`, `tbl.project_task_stage_personal`, `tbl.project_tag`, `tbl.project_milestone`, `tbl.project_update`, `tbl.project_collaborator`, `tbl.project_role`, `tbl.project_task`. No pinned verbs beyond CRUD. Resolve relations (`project_id`, stage, collaborators, tags) by searching the related model first, as usual.

## Helpdesk (module `helpdesk`)

Models include `tbl.helpdesk_ticket`, `_ticket_comment`, `_ticket_type`, `_ticket_category`, `_ticket_channel`, `_team`, `_stage`, `_tag`, `_sla`, `_sla_status`, `_rating`, `_digest_log`, `_ticket_activity_link`. No `helpdesk.*` tools: use `base.record.*`. Tickets have SLA/assignment services and hooks that run on write, so read the record back after changing stage/team/assignee and expect side effects (SLA status rows, activity links).

## EDC payment terminals (module `edc`)

No `edc.*` tools; all access is via `base.*` against these models: `edc.device`, `edc.device.activation`, `edc.device.available_command`, `edc.device.command`, `edc.device.config`, `edc.device.status`, `edc.routing.rule`, `edc.device.log`, `edc.device.error.log`, `edc.device.secret`, `edc.group`, `edc.config.bank.app`, `edc.tidmid.config`, `edc.mqtt.message`, `edc.mqtt.nonce`, `edc.audit.log`, `edc.transaction`, `edc.transaction.journal`, `edc.settlement.journal`, `edc.txn.log`.

Operating rules (money-adjacent, audit-sensitive):
- **Treat `edc.transaction`, `*.journal`, `edc.txn.log`, `edc.audit.log`, `edc.mqtt.*` as read-mostly.** Device callbacks write them with guarded, never-regressing status transitions. Don't `write`/`unlink` them to "fix" a status; investigate with `search_read` and report. Any balance/settlement correction is for the operations team, not an MCP edit.
- **Device secrets are never retrievable.** `edc.device` keeps a one-way hash; `edc.device.secret` holds an encrypted signing copy that is not meant to be read back. Issuing/rotating a secret is a runtime method (`activate` / `rotate_secret`) reached with `base.record.call_method`; confirm with the user first, return any new secret exactly once, and warn it can't be shown again. `provisioning_secret_not_configured` means the server has no encryption key configured: an admin task.
- **Commands go through `edc.device.command`'s dispatch method** (`call_method` → `dispatch`), which signs and sends it to the device; device responses move the command through ACKED / SUCCESS / FAILED / EXPIRED. Creating a command row directly does not send it. Confirm the target device and command before dispatching: it reaches a physical terminal.
- **Some EDC methods are also device-facing HTTP routes** (`/base/edc/...`, `/base/transaction/{init,result,settle}`, `/device/provision`). Those are for terminals, not for MCP use.
- Empty status/telemetry on a healthy device may mean MQTT ingestion is turned off on that instance.
- EDC message handling runs as workflows and cron jobs (`workflow.*` / `automation.*` can inspect them). Rewriting them with `workflow.replace_action_sequence` changes payment-terminal processing: export first and confirm.

## The same on every instance (don't re-ask)

`idempotency_key` rules, `base.batch.execute`, custom-model publish lifecycle (publish state not persisted across restart/replicas), 4 KB field trimming, `limit` clamp to 200, OAuth bearer tokens with the user's own permissions (`X-API-Key` never works on `/mcp`), closed per-group model allowlists, OAuth discovery and dynamic client registration (`references/connecting-clients.md`).
