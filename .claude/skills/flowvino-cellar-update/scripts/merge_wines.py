#!/usr/bin/env python3
"""
Merge researched wine entries into the cellar's wines.json.

Usage:
    python merge_wines.py <current-wines.json> <new-entries.json> <output-wines.json>

new-entries.json is a JSON array of wine objects. Each needs at least "name".
- If an object has "id" matching an existing entry, or "name" matches an
  existing entry (case-insensitive), that entry is updated in place: only
  the fields present in the new object are changed, everything else on the
  existing entry is left untouched.
- Otherwise, a new entry is created. A unique id is slugified from the name
  and addedAt is set to the current time automatically.

Never pass "id" or "addedAt" for brand-new wines — this script sets them.
"""
import json
import re
import sys
import time


def slugify(name):
    normalized = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_]+", "-", normalized).strip("-")
    return "wine-" + slug[:60]


def unique_id(base, existing_ids):
    if base not in existing_ids:
        return base
    n = 2
    while f"{base}-{n}" in existing_ids:
        n += 1
    return f"{base}-{n}"


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    current_path, new_path, output_path = sys.argv[1:4]

    with open(current_path) as f:
        wines = json.load(f)
    with open(new_path) as f:
        new_entries = json.load(f)

    by_id = {w.get("id"): w for w in wines}
    by_name = {w.get("name", "").strip().lower(): w for w in wines}
    existing_ids = set(by_id.keys())

    added, updated = [], []

    for entry in new_entries:
        target = None
        if entry.get("id") and entry["id"] in by_id:
            target = by_id[entry["id"]]
        elif entry.get("name", "").strip().lower() in by_name:
            target = by_name[entry["name"].strip().lower()]

        if target is not None:
            for k, v in entry.items():
                if k in ("id", "addedAt"):
                    continue
                target[k] = v
            updated.append(target["name"])
        else:
            new_wine = dict(entry)
            base_id = slugify(new_wine.get("name", "wine"))
            new_id = unique_id(base_id, existing_ids)
            existing_ids.add(new_id)
            new_wine["id"] = new_id
            new_wine.setdefault("quantity", 1)
            new_wine["addedAt"] = int(time.time() * 1000)
            wines.append(new_wine)
            by_id[new_id] = new_wine
            by_name[new_wine.get("name", "").strip().lower()] = new_wine
            added.append(new_wine["name"])

    with open(output_path, "w") as f:
        json.dump(wines, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(wines)} total wines to {output_path}")
    if added:
        print(f"Added ({len(added)}): " + ", ".join(added))
    if updated:
        print(f"Updated ({len(updated)}): " + ", ".join(updated))


if __name__ == "__main__":
    main()
