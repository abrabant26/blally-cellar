---
name: flowvino-cellar-update
description: Use this skill whenever the user shares photos of wine bottles/labels, a wine shop receipt or invoice, or otherwise says they bought or received new wine — and whenever they mention drinking, finishing, or opening a bottle (e.g. "we drank the Barolo last night," "finished off the Rioja"). This skill researches each wine (producer, vintage, grape blend, region, drink-by window) and produces updated wines.json / drink-log.json files matching the schema used by the FlowVino wine cellar site (cellar.flowvino.work, GitHub repo abrabant26/blally-cellar). Trigger this any time bottle labels, wine invoices, or wine-drinking updates come up, even if the user doesn't explicitly say "update the cellar."
---

# FlowVino Cellar Update

This skill keeps Ally and her partner's wine cellar (cellar.flowvino.work) current. The site is a static page that reads `data/wines.json` and `data/drink-log.json` from a public GitHub repo (`abrabant26/blally-cellar`) — there's no live database, so "updating the cellar" means producing new versions of those two files for the user to upload to GitHub (Add file → Upload files → replace the existing file → Commit).

Two kinds of updates land here:
1. **New wine** — photos of bottles/labels, or a receipt/invoice from a wine shop → add entries to `wines.json`.
2. **Drink log** — the user mentions drinking a wine → add an entry to `drink-log.json` and decrement that wine's bottle count in `wines.json`.

A single message might contain both, or several of one kind (e.g. four bottles in one rack photo).

## Step 0: Get the current data

Always start from the live published data, not memory — the user or their partner may have already published changes since you last touched this.

Fetch both files fresh:
- `https://cellar.flowvino.work/data/wines.json`
- `https://cellar.flowvino.work/data/drink-log.json`

If the site fetch fails for some reason, fall back to `https://raw.githubusercontent.com/abrabant26/blally-cellar/main/data/wines.json` (and `.../drink-log.json`). If the user has pasted or uploaded a copy of either file directly, use that instead of fetching.

## Step 1: New wine entries

For each wine in the photos/receipt/description:

**Extract what's directly visible or stated:**
- `name` — the wine's name as it would appear on a wine list (not necessarily the full label text)
- `producer`
- `vintage`
- `region`
- If from a receipt/invoice: `price` (use the actual amount paid, e.g. after-discount total, not list price), `purchaseSource` (the merchant name), `purchaseDate` (invoice date)
- `quantity` — default 1 per distinct wine unless the receipt states otherwise (e.g. "2 x")

**Research what isn't directly visible** (web search — don't guess at specifics you can look up):
- `varietal` — the actual grape composition. For blends, get real percentages if published (e.g. "80% Grenache, 10% Mourvèdre, 7% Syrah, 3% Cinsault") rather than a generic guess. For wines governed by an appellation that mandates the grape (e.g. red Burgundy = Pinot Noir, Chablis = Chardonnay, Barolo = 100% Nebbiolo), the appellation rule is a reliable source even without searching.
- `grape` — see the taxonomy in `references/schema.md`. Reuse an existing category from the current `wines.json` if the wine fits one (fetch the current file first, per Step 0, and check what grape values are already in use — reuse them verbatim so grouping in the app stays clean rather than fragmenting into near-duplicate categories).
- `drinkFrom` / `drinkTo` — estimate a sensible drink window. Search for the specific wine's aging potential/critic drinking window where possible; where not, use the style/region heuristics in `references/schema.md` as a starting point and adjust for known characteristics of that producer or appellation (e.g. a Grand Cru will typically age longer than a village-level wine from the same region).

**Fields to leave blank** (these are the humans' own data, never fabricate them): `rating`, `bin`, and — for wines not from a traceable receipt — `price`, `purchaseSource`, `purchaseDate`.

**Matching against existing entries:** if a wine with the same or clearly equivalent name already exists in the fetched `wines.json`, treat this as updating that entry (e.g. increasing quantity, filling in a blank field) rather than creating a duplicate. Flag it to the user either way ("this looks like the same Barolo Villero already in the cellar — increased quantity to 2" or "added as new, but check whether this is the same bottle as X").

## Step 2: Drink log entries

When the user says they drank/finished/opened a wine:
1. Match it to an entry in `wines.json` by name (fuzzy is fine — "the Barolo" can match "Barolo Villero" if that's the only Barolo with bottles remaining; ask if it's ambiguous).
2. Create a `drink-log.json` entry with `dateDrunk` (today unless the user gives a date — "last night," "on Saturday" etc. should resolve to an actual date), and `notes` capturing whatever they said about the occasion or the wine itself.
3. Decrease that wine's `quantity` by 1 in `wines.json`, unless the user's phrasing implies otherwise (e.g. "we opened it but didn't finish" — use judgment, ask if unsure).

## Step 3: Apply the changes and hand back files

Use `scripts/merge_wines.py` and `scripts/log_tasting.py` (see below) to apply your researched entries onto the fetched baseline — don't hand-edit the JSON yourself, the scripts handle id generation, timestamps, and merging so the output is always valid and consistent with what's already published.

Then:
1. Show the user a short plain-English summary of what changed (new wines added, quantities updated, tastings logged) — not a wall of JSON.
2. Write the two full updated files (`wines.json`, `drink-log.json` — only the one(s) that actually changed) to the workspace and hand them to the user.
3. Remind them how to publish: upload the file(s) into the `data/` folder of the `abrabant26/blally-cellar` GitHub repo (Add file → Upload files → it'll offer to replace the existing file → Commit changes). The live site updates within about a minute.

## Using the scripts

Both scripts take file paths, not stdin — write your researched entries to a small JSON file first, then run the script.

**`scripts/merge_wines.py`** — add or update wine entries:
```
python scripts/merge_wines.py <current-wines.json> <new-entries.json> <output-wines.json>
```
`new-entries.json` is a JSON array of wine objects. Include `name` at minimum. If an object includes an `"id"` matching an existing entry, or its `name` matches an existing entry (case-insensitive), that entry is updated in place (only the fields you provide are changed — omit fields you don't want to touch). Otherwise a new entry is created: a unique `id` is slugified from the name and an `addedAt` timestamp is set automatically, so don't include those yourself.

**`scripts/log_tasting.py`** — log a tasting and decrement inventory:
```
python scripts/log_tasting.py <current-wines.json> <current-drink-log.json> <tastings.json> <output-wines.json> <output-drink-log.json>
```
`tastings.json` is a JSON array of objects like:
```json
{"wineName": "Barolo Villero", "dateDrunk": "2026-08-02", "notes": "Shared with the Smiths, paired with steak.", "decrement": true}
```
`wineName` can also be `wineId` if you already know it. `decrement` defaults to `true` if omitted.

See `references/schema.md` for the exact field list, the grape taxonomy, and drink-window heuristics.
