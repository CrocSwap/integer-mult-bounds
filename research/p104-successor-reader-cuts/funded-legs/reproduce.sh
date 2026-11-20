#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
out=$(mktemp -d)
trap 'rm -rf -- "$out"' EXIT HUP INT TERM
word=../inputs/DOUBLE-CANDIDATE.json.gz
app=../inputs/DOUBLE-APPLICATION.json
python3 -IB replay.py "$word" "$app" --support construction.py > "$out/roster.json"
python3 -IB - "$out/roster.json" <<'CHECK'
import hashlib, json, pathlib, sys
p = pathlib.Path(sys.argv[1])
summary = json.loads(pathlib.Path("SUMMARY.json").read_bytes())
assert hashlib.sha256(p.read_bytes()).hexdigest() == summary["all_donors_sha256"]
assert json.loads(p.read_bytes())["roster_summary"] == summary["roster_summary"]
CHECK
python3 -B receiver508.py "$word" --support construction.py --public-cone > "$out/cone.json"
cmp PUBLIC-CONE.json "$out/cone.json"
python3 -IB binary.py > "$out/binary.json"
cmp BINARY.json "$out/binary.json"
printf '%s\n' 'The full rational donor roster, public cone and binary early-ingress tests reproduced.'
