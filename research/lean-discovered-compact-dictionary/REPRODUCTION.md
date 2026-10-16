# Reproduce the exact discovered-key chain

This prospective recipe was inspected, not executed during publication preparation. The exact source manifest SHA-256 is 254e59f4d523485b1c677476abb71dbfa50f492c61f5907d0bc28d79b1088255. Individual source checks and independent reviews bind the results in ACCEPTANCE.json; a combined 29-root rebuild is not claimed.

Use an already prepared Lean 4.21.0 and Mathlib 308445d7985027f538e281e18df29ca16ede2ba3 with coherent official dependency objects. Installation, downloads/cache recovery and rebuilding dependencies are outside this recipe. Stop if these prerequisites or any exact public Git object are unavailable.

Set paths to that prepared installation, this published package and a public repository clone containing the manifest's exact commits. Use the established shared compiler lock, or a private lock for a genuinely isolated reader. Clear ambient Lean options before inspecting or entering any build environment.

```sh
set -eu
unset LEAN_PATH LEAN_OPTS
export LEAN_HOME=/absolute/path/to/lean-4.21.0-linux
export MATHLIB=/absolute/path/to/mathlib4
export PACKAGE=/absolute/path/to/lean-discovered-compact-dictionary
export PUBLIC_REPO=/absolute/path/to/integer-mult-bounds
export COMPILER_LOCK=/absolute/path/to/the/compiler.lock
export BUILD=$(mktemp -d)
mkdir "$BUILD/src" "$BUILD/objects" "$BUILD/logs"
"$LEAN_HOME/bin/lean" --version
test "$(cat "$MATHLIB/lean-toolchain")" = leanprover/lean4:v4.21.0
test "$(git -C "$MATHLIB" rev-parse HEAD)" = 308445d7985027f538e281e18df29ca16ede2ba3
```

Materialize the 24 unchanged public prerequisite sources from their immutable Git references into the new scratch directory. Copy only the five new package sources. This step reads the existing public clone and performs no network or repository write.

```sh
python3 - <<'PYCODE'
import hashlib, json, os, pathlib, re, subprocess
package=pathlib.Path(os.environ['PACKAGE']); repo=pathlib.Path(os.environ['PUBLIC_REPO']); build=pathlib.Path(os.environ['BUILD'])
raw=(package/'PUBLIC_SOURCE_MANIFEST.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='254e59f4d523485b1c677476abb71dbfa50f492c61f5907d0bc28d79b1088255'
m=json.loads(raw)
version=subprocess.check_output([os.environ['LEAN_HOME']+'/bin/lean','--version'],text=True)
assert re.search(r'version 4\.21\.0(?:,|\))',version),version
ml=pathlib.Path(os.environ['MATHLIB']); packages=json.loads((ml/'lake-manifest.json').read_text())['packages']
required=['batteries','Qq','aesop','proofwidgets','importGraph','LeanSearchClient','plausible']
for name in required:
    entry=next(x for x in packages if x['name']==name); path=ml/'.lake/packages'/name
    assert subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()==entry['rev']
    assert (path/'.lake/build/lib/lean').is_dir()
records={x['module']:x for x in m['public_prerequisites']+m['new_modules']}
assert len(records)==29 and len(m['research_topological_order'])==29
seen=set()
for name in m['research_topological_order']:
    item=records[name]
    assert all(dep in seen for dep in item['imports'] if dep in records)
    data=(subprocess.check_output(['git','-C',str(repo),'show',item['revision']+':'+item['path']])
          if 'revision' in item else (package/item['proposed_path']).read_bytes())
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],name
    (build/'src'/(name+'.lean')).write_bytes(data); seen.add(name)
(build/'MODULES').write_text('\n'.join(m['research_topological_order'])+'\n')
PYCODE
```

Compile serially using only the new research object directory and the prepared official roots. A shared installation should use its existing bounded runner/lock instead of launching a competing loop. Each root is a separate bounded phase. Stop at the first failure; do not raise caps or substitute source bytes.

```sh
export LEAN_NUM_THREADS=1
unset LEAN_OPTS
export LEAN_PATH="$BUILD/objects:$MATHLIB/.lake/packages/batteries/.lake/build/lib/lean:$MATHLIB/.lake/packages/Qq/.lake/build/lib/lean:$MATHLIB/.lake/packages/aesop/.lake/build/lib/lean:$MATHLIB/.lake/packages/proofwidgets/.lake/build/lib/lean:$MATHLIB/.lake/packages/importGraph/.lake/build/lib/lean:$MATHLIB/.lake/packages/LeanSearchClient/.lake/build/lib/lean:$MATHLIB/.lake/packages/plausible/.lake/build/lib/lean:$MATHLIB/.lake/build/lib/lean:$LEAN_HOME/lib/lean"
while IFS= read -r module; do
  test ! -e "$BUILD/objects/$module.olean"
  python3 -c 'import os,shutil; assert shutil.disk_usage(os.environ["BUILD"]).free >= 8*1024**3'
  flock -x "$COMPILER_LOCK" timeout --signal=KILL 60s bash -c '
    ulimit -v 4194304
    exec "$LEAN_HOME/bin/lean" -j1 -o "$BUILD/objects/$1.olean" "$BUILD/src/$1.lean"
  ' _ "$module" > "$BUILD/logs/$module.stdout" 2> "$BUILD/logs/$module.stderr"
  test -s "$BUILD/objects/$module.olean"
done < "$BUILD/MODULES"
```

Exit zero and an object are necessary, not sufficient. Compare every embedded probe and full type, consuming all output. The five new modules have 22 probes and 9 full printed types in ACCEPTANCE.json; observed axioms are among propext, Classical.choice and Quot.sound. Reject sorryAx, errors, unresolved goals and unexplained diagnostics. Compare prerequisites with their own public acceptance records. Object hashes depend on invocation/path and do not replace exact source/kernel checking. These operational caps are not an execution-cost theorem.

The final completeness theorem retains both actual JSON parser equations and restricted chart/layout conditions. No selected artifact, cryptographic digest, parser span or physical implementation is validated by reproducing these generic facts. Author-checked context kappa is 836330098538459/500000000000000000=0.001672660197076918; unchanged and unused by the generic statements.
