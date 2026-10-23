# Reproduce the exact source closure

These are prospective instructions, not a claim that publication preparation reran this build. Use an existing official Lean/Mathlib checkout, or arrange its setup separately. The required Mathlib commit is `308445d7985027f538e281e18df29ca16ede2ba3`, including the official dependencies in its `lake-manifest.json`; Lean must actually report version 4.21.0. Do not reuse unrelated research objects.

Set `PACKAGE` to this published package directory and `MATHLIB` to that exact official checkout. The package contains its two `sources/*.lean` files and this manifest. All other research source files are fetched at the immutable public revisions listed in the manifest, verified by byte count and SHA-256, and written only to a fresh scratch directory.

```bash
set -euo pipefail
unset LEAN_PATH LEAN_OPTS
export PACKAGE="/path/to/repository/research/lean-artifact-slice-binding"
export MATHLIB="/path/to/mathlib4"
test "$(git -C "$MATHLIB" rev-parse HEAD)" = 308445d7985027f538e281e18df29ca16ede2ba3
test "$(cat "$MATHLIB/lean-toolchain")" = leanprover/lean4:v4.21.0
export STAGE="$(mktemp -d)"
mkdir "$STAGE/sources" "$STAGE/objects" "$STAGE/logs"
python3 - <<'PYCODE'
import hashlib, json, os, pathlib, urllib.request
pkg = pathlib.Path(os.environ['PACKAGE'])
stage = pathlib.Path(os.environ['STAGE'])
m = json.loads((pkg / 'PUBLIC_SOURCE_MANIFEST.json').read_text())
new = {x['module']: x for x in m['new_modules']}
public = {x['module']: x for x in m['public_prerequisites']}
for module in m['research_topological_order']:
    entry = new.get(module) or public[module]
    if module in new:
        data = (pkg / entry['proposed_path']).read_bytes()
    else:
        url = ('https://raw.githubusercontent.com/' + entry['repository'] + '/'
               + entry['revision'] + '/' + entry['path'])
        with urllib.request.urlopen(url) as response:
            data = response.read()
    assert len(data) == entry['bytes'], module
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], module
    (stage / 'sources' / (module + '.lean')).write_bytes(data)
(stage / 'order.txt').write_text(''.join(x + '\n' for x in m['research_topological_order']))
PYCODE
cd "$MATHLIB"
unset LEAN_PATH LEAN_OPTS
lake env bash -c '
  set -euo pipefail
  version="$(lean --version)"
  printf "%s\n" "$version"
  case "$version" in *"version 4.21.0,"*|*"version 4.21.0)"*) ;; *) exit 1 ;; esac
  export LEAN_PATH="$STAGE/objects:$STAGE/sources${LEAN_PATH:+:$LEAN_PATH}"
  ulimit -v 4194304
  while IFS= read -r module; do
    timeout 60s lean -s65536 -j1 -o "$STAGE/objects/$module.olean" \
      "$STAGE/sources/$module.lean" >"$STAGE/logs/$module.stdout" \
      2>"$STAGE/logs/$module.stderr"
  done < "$STAGE/order.txt"
'
```

The shell stops at the first failed source. Inspect both new-module logs: all seven `CheckedArraySlice` and four `LocatedCompactEntry` axiom probes and their two complete types each must match `ACCEPTANCE.json`. No `sorryAx`, extra axiom, compiler error or warning is accepted for these sources. An object alone is insufficient. Compare the conditional premises as well as conclusions. The source closure is generic; this command does not execute a selected artifact census or authenticate an input digest.
