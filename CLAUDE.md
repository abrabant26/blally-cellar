# blally-cellar

This repo is the FlowVino wine cellar site, deployed via GitHub Pages to
**cellar.flowvino.work**. It's a static site with no backend: `index.html`
reads `data/wines.json` and `data/drink-log.json` at load time, so those two
files are the live database. Whatever is committed to `main` is what the site
shows, usually within about a minute of pushing.

## When the user sends wine photos, receipts, or mentions drinking a bottle

Use the `flowvino-cellar-update` skill to research and produce the updated
`data/wines.json` / `data/drink-log.json`. That skill's job ends at "here are
the updated files" — finish the job in this repo by:

1. Writing the updated file(s) into `data/` in this working tree.
2. Showing the user a one- or two-line plain-English summary of what changed
   (e.g. "Added 2026 Testarossa Pinot Noir; logged the Barolo Villero as
   drunk on 8/2, quantity now 0").
3. Running:
   ```
   git add data/
   git commit -m "<short summary of the update>"
   git push origin main
   ```
4. Confirming the push succeeded and reminding the user the site updates in
   about a minute.

Don't ask for confirmation before pushing — that's the point of this setup.
Do still show the summary so there's a record of what happened. If a wine
can't be confidently matched (e.g. logging a drink for something ambiguous),
say so and skip that one rather than guessing.

## Schema and research guidance

Full field definitions, the grape-type taxonomy already in use, and
drink-window heuristics live in the `flowvino-cellar-update` skill's
`references/schema.md` — read that before inventing a new grape category or
estimating a drink window from scratch.

## Local dev

`index.html` fetches `data/*.json` with `fetch(..., { cache: 'no-store' })`,
so opening it directly (`file://`) will fail the fetch and fall back to
built-in defaults — serve the folder locally to test against real data:
```
python3 -m http.server 8080
```
then visit `http://localhost:8080`.
