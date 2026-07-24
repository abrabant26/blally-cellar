# Wine Cellar — setup instructions

This folder is a complete, ready-to-publish website. No coding required — everything below is clicking buttons on github.com and cloudflare.com.

## What's in here

- `index.html` — the cellar app (cards, ratings, drink windows, grouping, drink log)
- `data/wines.json` — your 20 wines (the actual data the site reads)
- `data/drink-log.json` — the tasting log (starts empty)
- `CNAME` — tells GitHub Pages to answer to `cellar.flowvino.work`

## Step 1: Create the GitHub repo

1. Go to [github.com/new](https://github.com/new) while signed in as **abrabant26**.
2. Repository name: `blally-cellar`
3. Set it to **Public** (required for free GitHub Pages).
4. Leave "Add a README" unchecked. Click **Create repository**.

## Step 2: Upload these files

1. On the new repo's page, click **"uploading an existing file"** (or Add file → Upload files).
2. Drag in all four items from this folder: `index.html`, `CNAME`, and the whole `data` folder (drag `data/wines.json` and `data/drink-log.json` — GitHub will recreate the `data/` folder automatically).
3. Scroll down, click **Commit changes**.

## Step 3: Turn on GitHub Pages

1. In the repo, go to **Settings → Pages** (left sidebar).
2. Under "Build and deployment" → Source, choose **Deploy from a branch**.
3. Branch: **main**, folder: **/ (root)**. Click **Save**.
4. Under "Custom domain," it should auto-detect `cellar.flowvino.work` from the CNAME file. If not, type it in and click **Save**.
5. GitHub will show a note that DNS isn't configured yet — that's Step 4.

## Step 4: Point the subdomain at GitHub (in Cloudflare)

1. Log into Cloudflare, select the **flowvino.work** zone.
2. Go to **DNS → Records → Add record**.
3. Type: **CNAME**
   Name: **cellar**
   Target: **abrabant26.github.io**
   Proxy status: click it so it shows **DNS only** (grey cloud, not orange) — GitHub Pages manages its own SSL certificate and the proxy can interfere with that at first.
4. Save. DNS usually propagates within a few minutes, sometimes up to an hour.
5. Back in GitHub → Settings → Pages, wait for the "DNS check successful" message, then check **Enforce HTTPS**.

Once that's done, **https://cellar.flowvino.work** is live and shows the cellar.

## How updates work (no GitHub skills needed after setup)

The site always shows whatever is in `data/wines.json` and `data/drink-log.json` in the repo — that's the "published" version everyone sees.

**When your partner sends new bottle photos to Claude:**
1. Claude reads the photos and gives you an updated `wines.json` file.
2. Go to the repo → open the `data` folder → click `wines.json` → click the pencil (Edit) icon → select all, paste in the new contents → **Commit changes**.
   (Or: Add file → Upload files → drag in the new `wines.json` → it'll ask to replace the existing one → Commit.)
3. The live site updates within about a minute.

**When you edit directly on the live site** (add a wine, change a rating, mark something as drunk): those changes only live in your browser until you publish them. Click **"⬇ Download wines.json (to publish)"** (or the drink-log equivalent) at the bottom of the page, then repeat the upload step above with the downloaded file.

## Notes

- Anyone can *view* the site without a GitHub account. Only whoever has access to the `abrabant26` GitHub account can *publish* changes.
- If you want to add a second person who can publish directly (not just relay through Claude), add them as a Collaborator under repo Settings → Collaborators.
