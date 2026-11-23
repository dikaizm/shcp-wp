# SHCP WordPress site

Local site: `schp-wp` in Local.app (`~/Local Sites/schp-wp`, http://localhost:10014, admin user `admin`).
Stack: Hello Elementor + `shcp-child`, Elementor 4.3.5, PRO Elements 4.3.2, Secure Custom Fields 6.9.10 (free ACF fork by WordPress.org: Repeater, Flexible Content, Gallery, Clone, Options Pages, no license), TablePress 3.5 (spec tables, CSV import), Polylang (EN/ID), Contact Form 7. PHP 8.5 (CF7 needs PHP 8.3 or newer).

## Layout

- `design/` – original design zips (superseded by Figma file `7ciRpkV2FuIJ2eCQIBu0Th`)
- `shcp-child/` – child theme: `application` post type, SCF fields (repeaters: benefits, spec sections → tabs → TablePress table), shortcodes (`[shcp_menu]`, `[shcp_lang]`, `[shcp_benefits]`, `[shcp_spec]`, `[shcp_t]`, `[shcp_btn]`, `[shcp_detail_buttons]`), `assets/site.js` (tabs, mobile menu, form states), `assets/icons/` (Figma SVGs), CSS. Symlinked into the site.
- `elementor/content.py` – all page copy, EN + ID (from the Figma EN and "- IND" frames)
- `elementor/applications.json` – applications (EN + `id` translations) and spec tables as row arrays
- `elementor/build.py` – generates Elementor JSON for header, footer, loop card, application template and 5 pages × 2 languages (+ `build/site.json`: CF7 forms, menus)
- `assets/` – web-ready images (`scripts/prep-figma-assets.py` from `assets/figma/`, the raw Figma exports, gitignored)
- `scripts/wp` – WP-CLI via `localwp cli schp-wp`; `scripts/shot.sh` – headless screenshots

## Rebuild from scratch (order matters)

```sh
python3 -I scripts/prep-figma-assets.py assets/figma assets
scripts/wp eval-file "$PWD/scripts/seed-applications.php" --user=admin   # EN+ID applications, terms, TablePress tables
scripts/wp eval-file "$PWD/scripts/import-assets.php"                    # media library + featured images -> elementor/media.json
python3 -I elementor/build.py
scripts/wp eval-file "$PWD/scripts/push-elementor.php" --user=admin   # --user required, else Elementor saves nothing
```

`push-elementor.php` overwrites every generated layout (both languages). Once someone edits in the Elementor editor, stop pushing and edit there.

## Gotchas

- Polylang 3.9 rewrites its option on shutdown: change settings via `PLL()->options[...]` + `->save()`, not `update_option('polylang')`.
- Headless Chrome clamps windows to ~500px; `scripts/shot.sh <path> out.png 390` uses an iframe for mobile.
- The shell's `curl` is wrapped by rtk and summarises output; use `rtk proxy curl` for raw HTML.

## Deploy to the client's server

1. Back up the live site.
2. Replace the theme symlink with a real copy (migration plugins skip symlinks):
   `rm "$HOME/Local Sites/schp-wp/app/public/wp-content/themes/shcp-child" && cp -R shcp-child "$HOME/Local Sites/schp-wp/app/public/wp-content/themes/"`
3. Export with All-in-One WP Migration or Duplicator, import on live (replaces DB, files and users).
4. On live: create the client's admin users, re-save permalinks, set SMTP (e.g. WP Mail SMTP), set CF7 recipient, check PHP ≥ 8.3.
5. Elementor + PRO Elements have no dashboard updates from these sources: update them together by hand. SCF, TablePress, Polylang, CF7 update normally from wordpress.org.

## Editing spec tables

TablePress → Import (CSV/Excel) or Edit (add rows/columns). `#colspan#` / `#rowspan#` merge cells; set table head rows to 2 for two-row headers. Then Applications → edit → Specification sections → tab → pick the table. Empty tab table = greyed-out tab.

## Staging (stelar-server-02)

Client preview: https://shcp-staging.stelarlab.co (Caddy basic-auth + noindex).
Docker stack in `deploy/staging/`: MariaDB + WordPress (PHP-FPM) + Mailpit, hard RAM cap ~512 MB.
The theme (`shcp-child/`) and the mail catcher are bind-mounted from the git checkout in
`/opt/shcp-staging/repo`; update with `/opt/shcp-staging/repo/deploy/staging/update.sh`.
Database, uploads and plugins were seeded once from the local site (not in git).
`design/` and `assets/` (client material) are intentionally not in this repo.
