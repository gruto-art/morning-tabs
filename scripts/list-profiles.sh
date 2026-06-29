#!/bin/bash
# Discover Chrome profile directory names and the Google account each is signed into.
# Run this to figure out what to put in the "# PROFILE=" line of each profiles/*.txt file.

CHROME_DIR="$HOME/Library/Application Support/Google/Chrome"

if [ ! -d "$CHROME_DIR" ]; then
  echo "Chrome data directory not found at: $CHROME_DIR"
  exit 1
fi

python3 - <<'PY'
import json, os
chrome = os.path.expanduser("~/Library/Application Support/Google/Chrome")
local_state = json.load(open(os.path.join(chrome, "Local State")))
info = local_state.get("profile", {}).get("info_cache", {})

rows = []
for pdir, meta in info.items():
    name = meta.get("name", "?")
    email = meta.get("user_name", "") or "(not signed in)"
    rows.append((pdir, name, email))

def k(r):
    p = r[0]
    return (0, 0) if p == "Default" else (1, int(p.replace("Profile ", "")))
rows.sort(key=k)

print(f"\n{'Directory':<14} {'Display name':<26} {'Email / account'}")
print("-" * 80)
for pdir, name, email in rows:
    print(f"{pdir:<14} {name:<26} {email}")

print("\nTo use a profile, copy its directory name (e.g. 'Profile 1') into the")
print("first line of a profiles/*.txt file:  # PROFILE=Profile 1\n")
PY
