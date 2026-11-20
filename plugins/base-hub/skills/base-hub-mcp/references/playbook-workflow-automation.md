# Playbook: workflows, automation actions, scheduled jobs

Use when the user wants something to happen automatically: "when a form is submitted, create a contact and email sales", "every night, close stale tickets", "accept orders from our partner's webhook". Argument shapes: `tool-catalog.md` → workflow.*, automation.*.

## 1. Pick the right tool

| Need | Use |
|---|---|
| React to an event: an incoming webhook, an MQTT/Kafka message, a record being created/changed/deleted | **Workflow** (`workflow.*`) |
| Run on a schedule (every N seconds/minutes/hours) | **Automation cron** + **automation action** (`automation.*`); workflows have no cron trigger |
| A small piece of logic (Lua) or a simple record change, run on demand or by a cron | **Automation action** |
| Scheduled job that needs multi-step processing | Cron → Lua action, or a workflow step `lua_script` calling an automation action |

**Permissions:** authoring workflows needs `base.group_system`; setting what an automation action does (code, model, operation, handler) needs superadmin. Check early and tell the user if an admin must do it.

Look for an existing workflow or automation first (`workflow.record.search_read` on `base.workflow`, `automation.record.search_read`). Copying a similar one (`workflow.export` → adjust → `workflow.import`) is often faster than building from scratch.

## 2. Workflows

### Concepts
- `base.workflow`: `name` (unique), `topic` (unique, required; the webhook URL is `/wh/{topic}`), `execution_mode` `linear` (default; steps run in `sequence`) or `dag` (steps follow edges), `is_active`, `state` `draft`/`published`.
- **A workflow only runs its published version.** New workflows are `draft`, and editing steps, edges or settings sets `state` back to `draft`. Triggers and `/wh` always run the last published snapshot.
- Steps = `base.workflow.action` rows built from the action catalog. Discover live: `workflow.record.search_read` model `base.workflow.action.catalog`, domain `[["is_active","=",true]]`, fields `code, version, description, default_params`.

| Catalog code | Does |
|---|---|
| `parse_payload` | Raw bytes → JSON (put first for webhooks/messages) |
| `condition` | `extra_params.expression`, e.g. `{"field":"amount","gte":100}` (exists, empty, equals, not_equals, in, not_in, gt/gte/lt/lte, contains, regex, all/any/not) |
| `crud_model` | `model_name` + `extra_params.operation` create/update/upsert/find_or_create |
| `transform_data` | Reshape with a `template` |
| `flatten_json` | Nested → flat keys |
| `notify` | Outbound delivery (`channel`, `target_ref`, `headers`) |
| `post_output_object` | Call an outside URL (`target_ref`) |
| `hmac_action` / `hmac_verify`, `aes_action` / `aes_decrypt_action` | Sign/verify, encrypt/decrypt |
| `lua_script` | Run a Lua automation action (`extra_params.automation_action_id`) |
| `call_workflow` | Call another workflow (`target_workflow_id`; max 5 deep) |
| `for_each` | Loop over `items_path` (max 100 items by default) |
| `wait_approval` | Pause until a person approves (linear only) |

Trigger kinds (`base.workflow.trigger`: `workflow_id`, `trigger_type`, `topic`, `is_active`, `config`): `webhook` (optional; a workflow with no other trigger is served at `/wh/{topic}`; `config.hmac_secret` as `@cred:` ref), `model` (`config{model, operation: after_create|after_write|after_unlink|before_*, domain?}`), `mqtt` (topic pattern), `kafka` (topic, consumer group), `tcp` (only if enabled on the server).

### Build recipe
1. **Agree the flow in words** with the user: trigger → steps → what success looks like. Show it as a numbered list.
2. `workflow.record.create` on `base.workflow` `{name, topic, description, execution_mode}` + `idempotency_key`.
3. Secrets: `workflow.record.create` on `base.workflow.credential` `{name, credential_type, value}`; refer to it as `@cred:<name>`. Secret columns (`hmac_key`, `aes_key`, `authorization`) refuse literal values. Never echo secrets back.
4. `workflow.replace_action_sequence` `{workflow_id, steps}`. Step shape: `{"action_code":"crud_model","step_key":"save_contact","name":"Save contact","model_name":"tbl.partner","extra_params":{"operation":"find_or_create"},"timeout_seconds":30,"retry_policy":{"max_attempts":3}}`. Array order sets the sequence. Node parameters not in a typed column go in `extra_params`; `continue_on_error` / `extra_params.on_error_step_key` control failure handling.
5. DAG only: `workflow.replace_workflow_edges` `{workflow_id, edges:[{"from_step_key":"a","to_step_key":"b","edge_type":"success"}]}` (`success`, `failure`, `condition` + `condition_expr`, `always`); acyclic, keys must exist.
6. Trigger (if not a plain webhook): `workflow.record.create` on `base.workflow.trigger`.
7. **Validate and publish** (no `workflow.*` tool for this): `base.record.call_method` model `base.workflow`, method `validate`, ids `[id]`; fix the errors; then method `publish` (refused while validation fails); `set_active` with kwargs `{active: true}` if it isn't active. Confirm with the user before publishing: it starts processing real events.
8. **Test and inspect:** trigger it (a test record for a `model` trigger; the user POSTs to `/wh/{topic}` for webhooks), then `workflow.record.search_read` on `base.workflow.run` with `[["workflow_id","=",id]]`, order `id desc`, fields `status, last_error, current_step, step_runs, output_payload`. Statuses: pending, running, succeeded, waiting_retry, failed, dead_letter, cancelled, skipped. Re-run with method `replay_run` (kwargs `from_step_key?`); failed outbound calls on `base.workflow.outbound` retry with `manual_retry`.

### Changing a live workflow
- `workflow.export` first (it's the backup). `replace_action_sequence` deletes every step and its edges; `replace_workflow_edges` deletes all edges; pass `expected_revision` to avoid clobbering someone else's edit. Then validate + publish again.
- `workflow.import` always creates a new workflow (name/topic copy-suffixed); imported non-webhook triggers arrive inactive.
- Unlinking a workflow cascades to its steps, triggers and run history: prefer `set_active` false.
- Only one active workflow per topic. Workflows that drive EDC terminals change payment processing: export and get explicit confirmation.

## 3. Automation actions and scheduled jobs

- `automation.action`: `name`, `action_type`, `active`, plus by type:
  - `lua` → `lua_code` (must return a table to produce a result).
  - `sys_model` → `model`, `operation` (create, write, unlink, find_or_create), `domain` (a JSON **object** of field equalities, not a domain list; write/unlink require a non-empty one), `values`.
  - `go_handler` → `handler_key` (built-in jobs such as `workflow.resume_due_runs`).
- `automation.cron`: `name`, `action_id`, `interval_seconds` (≥30), `max_failures` (default 5; reaching it deactivates the cron, and setting `active` true again resets the count), `active`, `next_call` (create only). Read `last_run_status` and `fail_count` to check health.

Recipe: create the action → `automation.action.run` `{action_id, payload}` to test it (payload merges over `values`; it **really executes**, so confirm and use harmless data) → show the result → create the cron → after the first interval, read the cron's `last_run_status`.

Warn the user about these points:
- Scheduled runs and `sys_model` actions run **as sudo**: they bypass the user's access rules. Preview the affected records with a `search_read` on the same filter before enabling a write/unlink job.
- Lua sandbox: only base/table/string/math libraries, no files or network, 30 s timeout; `base.call(model, method, ids, kwargs)` *does* change data.
- An interval is not a calendar time: "every day at 8:00" means `interval_seconds: 86400` with `next_call` set to the next 8:00 (UTC Unix seconds); say the run time can drift.

## 4. Finish checklist

The workflow is published and active, or the cron is active · one test run succeeded, and you read back its status · secrets are stored as credentials · you told the user how to watch runs and how to switch it off (`set_active` false / cron `active` false).
