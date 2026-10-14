# Reproduce the exact recovery/byte source chain

This recipe describes a fresh-reader check of manifest SHA-256 `594860a0fff2d9575193a7bd5fd773579e93697bac0db9a9eeabf154f6b05f7e`. It was inspected, not executed during publication preparation. Existing accepted roots were not rebuilt. The original individual checks and independent reviews bind the unchanged source/probe/type results in the manifest.

## Prepared environment only

Use an already prepared Lean **4.21.0** and Mathlib checkout **308445d7985027f538e281e18df29ca16ede2ba3**, with coherent official dependency objects at that revision. Installation, download, dependency recovery and cache rebuilding are outside this recipe. Stop if these prerequisites are unavailable. The import path below uses the seven required package object directories; it does not include the unused Cli package.

Set absolute paths for the prepared runtime, Mathlib, this published package, and a public repository clone containing the three exact prerequisite commits. The package must contain the four sources at the manifest's `proposed_path` locations and this manifest at its root. Use the existing canonical compiler lock when sharing a research installation; a fresh isolated reader can choose a lock in its own workspace.

```sh
set -eu
export LEAN_HOME=/absolute/path/to/lean-4.21.0-linux
export MATHLIB=/absolute/path/to/mathlib4
export PACKAGE=/absolute/path/to/lean-recovered-byte-provider-chain
export PUBLIC_REPO=/absolute/path/to/integer-mult-bounds
export COMPILER_LOCK=/absolute/path/to/the/compiler.lock
export BUILD=$(mktemp -d)
mkdir "$BUILD/src" "$BUILD/objects" "$BUILD/logs"
"$LEAN_HOME/bin/lean" --version
test "$(git -C "$MATHLIB" rev-parse HEAD)" = 308445d7985027f538e281e18df29ca16ede2ba3
```

Do not substitute a moving branch, ambient research object directory or a different Lean version. Verify source identities before compiling. The following script copies only the four new package sources; it materializes the thirteen public prerequisites into the temporary reader build using exact `git show` references. It performs no network fetch and does not modify the public repository.

```sh
python3 - <<'PYCODE'
import hashlib, json, os, pathlib, re, subprocess
package = pathlib.Path(os.environ['PACKAGE'])
repo = pathlib.Path(os.environ['PUBLIC_REPO'])
build = pathlib.Path(os.environ['BUILD'])
raw = (package / 'PUBLIC_SOURCE_MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '594860a0fff2d9575193a7bd5fd773579e93697bac0db9a9eeabf154f6b05f7e'
m = json.loads(raw)
version = subprocess.check_output([os.environ['LEAN_HOME'] + '/bin/lean', '--version'], text=True)
assert re.search(r'version 4\.21\.0(?:,|\))', version), version
ml = pathlib.Path(os.environ['MATHLIB'])
packages = json.loads((ml / 'lake-manifest.json').read_text())['packages']
required = ['batteries', 'Qq', 'aesop', 'proofwidgets', 'importGraph', 'LeanSearchClient', 'plausible']
for name in required:
    entry = next(x for x in packages if x['name'] == name)
    path = ml / '.lake/packages' / name
    head = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    assert head == entry['rev'], (name, head, entry['rev'])
    assert (path / '.lake/build/lib/lean').is_dir(), name
for item in m['public_prerequisites'] + m['new_modules']:
    if 'revision' in item:
        data = subprocess.check_output(['git', '-C', str(repo), 'show', item['revision'] + ':' + item['path']])
    else:
        data = (package / item['proposed_path']).read_bytes()
    assert len(data) == item['bytes'], item['module']
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['module']
    (build / 'src' / (item['module'] + '.lean')).write_bytes(data)
assert len(m['research_topological_order']) == 17
(build / 'MODULES').write_text('\n'.join(m['research_topological_order']) + '\n')
PYCODE
```

The exact public heads are PR1831 `542f914ca0e5df4026341d08c84385cb1a71cfdf`, PR1879 `981afe759f7dd206188b1c1a62250c6425bcd76a`, and PR1927 `a5838afac3a2d69d802c2440cbfa7d160ca0b218`. Their file paths and hashes are in the manifest. If a Git object is absent, stop; obtaining it is a separate environment-preparation action.

## Isolated serial compilation

Use only the fresh research object directory and the exact prepared official roots. The order is syntax, index codec, binary checker, permutation checker, parsed certificate, canonical encoding, gather, JSON bridge/interpreter, four public adapters, restricted recovery, recovered dictionary entry, byte-call parser, and byte-recovery join.

```sh
export LEAN_NUM_THREADS=1
unset LEAN_OPTS
export LEAN_PATH="$BUILD/objects:$MATHLIB/.lake/packages/batteries/.lake/build/lib/lean:$MATHLIB/.lake/packages/Qq/.lake/build/lib/lean:$MATHLIB/.lake/packages/aesop/.lake/build/lib/lean:$MATHLIB/.lake/packages/proofwidgets/.lake/build/lib/lean:$MATHLIB/.lake/packages/importGraph/.lake/build/lib/lean:$MATHLIB/.lake/packages/LeanSearchClient/.lake/build/lib/lean:$MATHLIB/.lake/packages/plausible/.lake/build/lib/lean:$MATHLIB/.lake/build/lib/lean:$LEAN_HOME/lib/lean"
while IFS= read -r module; do
  test ! -e "$BUILD/objects/$module.olean"
  python3 -c 'import os, shutil; assert shutil.disk_usage(os.environ["BUILD"]).free >= 8 * 1024**3'
  flock -x "$COMPILER_LOCK" timeout --signal=KILL 60s bash -c '
    ulimit -v 4194304
    exec "$LEAN_HOME/bin/lean" -j1 -o "$BUILD/objects/$1.olean" "$BUILD/src/$1.lean"
  ' _ "$module" > "$BUILD/logs/$module.stdout" 2> "$BUILD/logs/$module.stderr"
  test -s "$BUILD/objects/$module.olean"
done < "$BUILD/MODULES"
```

Each root is a separate serial bounded phase with a 60-second hard wall, 4GiB address-space limit and 8GiB free-disk floor. These operational limits are not a cost theorem. A shared research installation should use its established bounded runner and lock rather than launch a competing copy of this illustrative fresh-reader loop. Do not retry by raising caps or replacing source bytes. Preserve failure output and stop on the first nonzero exit.

## Evidence inspection

Exit zero and an object file are necessary but insufficient. Compare all embedded axiom probes and complete printed theorem types. For the four new modules, the manifest contains the exact 15 observed probes and seven printed types; all observed axioms are among `propext`, `Classical.choice` and `Quot.sound`. Preserve the full output, classify every warning, and reject `sorryAx`, errors, unresolved goals or unexplained output. Compare prerequisite output with its own pinned public acceptance evidence. Object hashes can depend on invocation/path details and are not substitutes for source and kernel checking.

The sources retain their historical preparation comments and attributions. This recipe does not claim that a single combined 17-root shell loop was run in the original acceptance session. No selected artifact, dictionary key, digest or physical executor is validated by reproduction of the generic theorems.

Author-checked context: kappa = 836330098538459/500000000000000000 = 0.001672660197076918. The generic results do not use or change kappa. Restricted factorization, parser standards/lexical/duplicate-key policy, actual selected-file success, complex phases, physical direction/execution, precision and costs retain the limitations stated in the manifest and README.
