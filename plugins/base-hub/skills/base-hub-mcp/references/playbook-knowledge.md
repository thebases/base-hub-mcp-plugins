# Playbook: answering from the knowledge base, saving notes

Use when the user asks a question their company docs should answer ("what's our refund policy?", "how do I set up OAuth?"), wants a summary of documents, or wants to save/update a note. Needs `knowledge.doc.*` (module `knowledge`).

## 1. Namespaces

- `base`: product docs (SRS, user guides). Read-only; listed on the Home tenant only.
- `user_guide`: product user guides (MCP, automation, workflow, OAuth). Read-only; every tenant.
- `public`: the tenant's own notes. The only writable namespace.

Paths are namespace-prefixed (`public/hr/leave-policy.md`). A path without a prefix goes to `public`.

## 2. Answering a question

1. **Search with 2–4 keywords**, not the whole question: `knowledge.doc.search` matches only documents containing *every* word (no stemming), ranked, max 20 results. "refund policy" beats "what is our policy for refunding customers".
2. **Nothing found?** Try fewer or different words (synonyms, the other language: docs may be Vietnamese or English), then `knowledge.doc.find` (substring of the doc name/filename), then `knowledge.doc.list` to browse.
3. **Read the top 1–3 hits in full** with `knowledge.doc.read`. Search results carry only name/path/size, no excerpts, so you must read before you answer.
4. **Answer from what you read**, and cite: doc name, path and section heading. Quote short key passages when exact wording matters (policies, numbers).
5. **Say when the docs don't answer it.** Don't fill gaps from general knowledge as if it were company policy; label anything outside the docs as your own suggestion. If two docs conflict, show both and the dates (`updated_at`).

Business data questions ("how many open tickets?") are not knowledge questions: query the records with `base.record.search_read` instead, or combine both.

## 3. Saving or updating a note

- Writes need the user to be in `base.group_system` (or superadmin); a 403 means ask an admin.
- `knowledge.doc.create` `{path, content, name?, idempotency_key}`: `path` under `public/`, ends in `.md`, no `..`; subfolders allowed; `name` is the menu label. Fails if the path exists: then ask whether to update.
- `knowledge.doc.update` `{path, content}` **overwrites the whole document**: read it first, apply the change, show the user the diff in words, then write the full new content.
- `knowledge.doc.rename` `{from_path, to_path}`; `knowledge.doc.delete` `{path}` after confirmation.
- Write clear Markdown: a `#` title, short sections, the date and source of the information.
