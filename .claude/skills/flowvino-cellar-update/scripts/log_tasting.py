#!/usr/bin/env python3
"""
Log tastings into drink-log.json and (by default) decrement wines.json quantities.

Usage:
    python log_tasting.py <current-wines.json> <current-drink-log.json> \
        <tastings.json> <output-wines.json> <output-drink-log.json>

tastings.json is a JSON array of objects, e.g.:
[
  {
    "wineName": "Barolo Villero",
    "dateDrunk": "2026-08-02",
    "notes": "Shared with the Smiths, paired with steak.",
    "decrement": true
  }
]

"wineName" does a case-insensitive substring match against wines.json (use
"wineId" instead if you already resolved the exact id). "decrement" defaults
to true if omitted. "dateDrunk" defaults to today if omitted.
"""
import datetime
import json
import random
import string
import sys
import time


def gen_id():
    return "log_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def find_wine(wines, tasting):
    if tasting.get("wineId"):
        for w in wines:
            if w.get("id") == tasting["wineId"]:
                return w
        return None
    name = tasting.get("wineName", "").strip().lower()
    if not name:
        return None
    # exact match first, then substring match
    for w in wines:
        if w.get("name", "").strip().lower() == name:
            return w
    matches = [w for w in wines if name in w.get("name", "").strip().lower()]
    return matches[0] if len(matches) == 1 else None


def main():
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit(1)

    wines_path, log_path, tastings_path, out_wines_path, out_log_path = sys.argv[1:6]

    with open(wines_path) as f:
        wines = json.load(f)
    with open(log_path) as f:
        drink_log = json.load(f)
    with open(tastings_path) as f:
        tastings = json.load(f)

    today = datetime.date.today().isoformat()
    logged, not_found = [], []

    for t in tastings:
        wine = find_wine(wines, t)
        if wine is None:
            not_found.append(t.get("wineName") or t.get("wineId") or "(unknown)")
            continue

        entry = {
            "id": gen_id(),
            "wineId": wine["id"],
            "wineName": wine.get("name", ""),
            "producer": wine.get("producer", ""),
            "vintage": wine.get("vintage"),
            "grape": wine.get("grape", ""),
            "dateDrunk": t.get("dateDrunk") or today,
            "notes": t.get("notes", ""),
            "loggedAt": int(time.time() * 1000),
        }
        drink_log.append(entry)
        logged.append(wine.get("name", ""))

        if t.get("decrement", True):
            wine["quantity"] = max(0, int(wine.get("quantity") or 0) - 1)

    with open(out_wines_path, "w") as f:
        json.dump(wines, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(out_log_path, "w") as f:
        json.dump(drink_log, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Logged {len(logged)} tasting(s): " + ", ".join(logged) if logged else "Logged 0 tastings")
    if not_found:
        print(f"Could not confidently match ({len(not_found)}): " + ", ".join(not_found))
        print("Resolve these manually — ambiguous or no match in wines.json.")


if __name__ == "__main__":
    main()
