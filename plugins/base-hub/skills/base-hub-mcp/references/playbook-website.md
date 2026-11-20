# Playbook: websites, pages, menus, SEO, blog

Use when the user wants a website, landing page, About/Contact page, navigation, SEO, a contact form or a blog post. Needs the `website.*` tools (module `website`); blog needs `website_blog.*` (module `website-blog`). If they are missing, say the module isn't installed and stop. Argument shapes: `tool-catalog.md` → website.*.

## 1. Before you build

1. **Find the site.** `website.record.search_read` on `tbl.website_site`. Installing the module already seeds a site called "Website" with a homepage and a Bootstrap header/footer, so usually you extend that one instead of creating a second site. Only one site may have an empty `company_id`; a second site in the same company context fails unless you pass `company_id`.
2. **Which site does the public URL show?** An active `tbl.website_domain` row whose `host` matches wins; otherwise the lowest-id active site. Check before telling the user "it's live at ...".
3. **List existing pages** (`tbl.website_page`: `name`, `route_path`, `is_homepage`, `visibility`, `deploy_path`) so you update rather than duplicate.
4. **Agree a short plan** with the user: pages (name → URL), menu entries, what goes public, forms. Everything you publish is visible immediately.

## 2. Page URLs come from the page name

`route_path` is always derived from `name` as `/<slugify(name)>` (or `/` for the homepage), on create and whenever `name` or `is_homepage` changes. The `route_path` argument of `design_upsert` is effectively ignored. So choose the name for the URL you want ("About Us" → `/about-us`; name it "About" for `/about`). `route_path` must be unique per site.

Homepage: `/` is the page with `is_homepage=true`. Don't create a second homepage (route clash). To switch it: `base.record.call_method` model `tbl.website_page`, method `action_set_homepage`, ids `[page_id]`.

## 3. Writing page content

- Compose from builder blocks: `website.snippet.list` (filter `group`: intro, content, columns, text, images, people, catalog, social, contact, plus `dynamic` for live blog-post lists). Each snippet is a full `<section class="... py-5" data-snippet="..."><div class="container">...` block: concatenate the ones you need, replace the text, links and images, send the result as `html`.
- Published pages load Bootstrap 5.3 CSS, the theme CSS and BaseUI JS (bundles Bootstrap JS). Use plain Bootstrap 5 classes (`container`, `row`, `col-md-6`, `btn btn-primary`, `card`, ...).
- The sanitizer removes `script`, `style`, `iframe`, `object`, `embed`, `template`, `noscript`, `link`, `meta`, `base`, `svg`, `math` with their content, all `on*` handlers, and non-http(s)/mailto/tel URLs. Unknown tags are dropped but their children kept. Inline `style` and `class` survive; for page-wide CSS set `custom_css` (no `@import`, ≤100 KB) with `website.record.write`, then publish.
- **Images:** there is no website upload tool. Create a `sys.attachment` with `base.record.create` (`name`, `datas` base64, `is_public: true`) and reference `/web/content/<id>`; without `is_public` anonymous visitors can't load it. External https image URLs also work. A `tbl.website_asset` row (`site_id`, `attachment_id`, `alt_text`) is optional library metadata.
- Interactive behaviour is opt-in by marker attributes: `data-bh-animate`, `data-bh-countdown`, `data-bh-parallax`, `data-bh-lightbox`, `data-bh-popup`, `data-bh-form`, `data-bh-source`, `data-bh-lang-switch`, `data-bh-scrolltop`, `data-bh-search`.
- If a body contains `id="site-header"` / `id="site-footer"`, the site's own header/footer is skipped on that page.

## 4. Create or update with `design_upsert` (publishes!)

- **`design_upsert` publishes:** writes sanitized `body_html` (scripts, `<style>`, iframes, svg, event handlers stripped: style with classes/inline `style`) and deploys in one call, no draft-only step: confirm with the user before running on a live site. If publish fails after save, the draft stays saved (no rollback): fix the cause and call `website.publish`. Take a page down with `website.unpublish`.
- **No `page_id` creates a new page;** an existing `page_id` updates it. Confirm which the user means (common mistake: duplicate page). New page: `site_id`, `name`, `idempotency_key`.
- Response is `{page_id, page}`; fields over 4 KB are replaced by `<field>_bytes`, so read content back via `website.record.read`.
- **Long pages in chunks:** per call send `upload_id` + `html_chunk` + `chunk_index` (0-based) + `chunk_total`; nothing is touched until the last chunk (buffer expires ~2h). Never mix `html` with chunk args. Only the final chunk needs `idempotency_key` / `page_id` / `site_id` / `name`.
- Pages carry `visibility` (`public` | `logged_in`; logged-in pages are served only to signed-in users, `noindex`, out of the sitemap). `publish_at` (RFC3339) schedules a publish.
- `deploy_path` is a server folder, not a URL. The public URL is `http(s)://<host><route_path>`; a page is live while `deploy_path` is set.
- Every publish stores a version: `list_versions` / `action_restore_version` methods via `base.record.call_method` undo a bad publish.

## 5. Navigation menu, header, footer, theme

- **Menu** = `tbl.website_menu` rows: `site_id`, `name` (required), `page_id` (preferred; overrides `url`) or `url`, `parent_id` (same site, for dropdowns), `sequence` (default 10), `new_window`, `is_visible`. `page.is_in_menu` does **not** add a menu entry. Menus render into `ul#site-nav-menu` in the site header; if the header lacks that element the menu never shows.
- **Header/footer** = the site's `header_html` / `footer_html` (sanitized). The logo is markup inside the header (`#site-logo`, `#site-brand-name`); there is no logo field. Templates: methods `default_chrome` / `list_chrome_templates` (kwargs `kind=header|footer`).
- **Theme** = the site's `theme` JSON: `colors.main` = `[primary, secondary, tertiary]` (an array), `colors.light`, `colors.dark`, `website.mode` (light/dark), `website.pageLayout` (full/boxed), `headings.*`, `paragraph.*`, `button.*`, `link.style`. Values allow only `[#%.,\-\w\s()'"]` (no `url(`). Fonts are CSS font stacks only. `tbl.website_theme` rows are presets you copy into `site.theme`.
- **Menu, header, footer and theme are copied into each page at publish time:** after changing them run `website.publish` on the **site** (`model: tbl.website_site`, uses `ids[0]`, fails if the site has no pages).

## 6. SEO, redirects, languages

- **Page SEO is a nested `seo` JSON object** on `tbl.website_page`. Use `website.seo.upsert` (flat names in, merged into the object; `target` `site`|`page`), not raw `website.record.write`. Only the fields you pass change. Site defaults (`default_seo_name`, `robots_txt`, `sitemap_enabled`) via `target: site`.
- Redirects: `tbl.website_redirect` (`url_from` plain path, not `/`; `url_to` path or http(s) URL; `redirect_type` 301/302/404/410). Renaming a page can create one automatically.
- Translations: `tbl.website_page_translation` (`page_id`, `lang`, `body_html`, `seo`); `lang` must be in the site's `supported_languages` and not its `default_language`; served at `/<lang><route>`.

## 7. Contact and lead forms

`<form data-bh-form="key">` with `name`d inputs, an element with `data-bh-form-status`, optional `data-bh-form-success="Thanks!"` or `data-bh-form-redirect="/thanks"`, and the hidden honeypot input `website_url`. Key `^[a-z0-9][a-z0-9_-]{0,63}$`, ≤30 fields, input types text/email/tel/number/checkbox/radio/date/url. Every submission lands in `tbl.website_form_submission` (`form_key`, `data`, `state` new/done/spam, `site_id`); key `contact-us` also creates a `tbl.website_contact_request`. To route submissions somewhere (email, CRM record), add a workflow with a `model` trigger on `tbl.website_form_submission` after create (`playbook-workflow-automation.md`). Tell the user where to see submissions.

## 8. Blog

- **Blog (`website_blog.*`):** same record CRUD over blog/post/tag/category plus `website_blog.post.publish|unpublish|archive|duplicate` (exactly one id). Posts start `draft`; a future `published_at` schedules. Changing `slug`/`name`/`state`/`blog_id` needs exactly one id. Prefer `post.archive` over `unlink` (deleting a blog cascades to its posts).
- Post create: `name`, `blog_id` (search for the blog first), `content` (sanitized HTML), `idempotency_key`. Publish only after the user approves the draft.
- Public URLs: `/blog`, `/blog/<blog>`, `/blog/<blog>/<post>`, feed `feed.xml`.

## 9. Finish checklist

Page(s) published with the intended URL · menu entries exist and the site was republished · SEO title/description set · images load for anonymous visitors (`is_public`) · forms tested or explained · report the public URLs and what is still draft.
