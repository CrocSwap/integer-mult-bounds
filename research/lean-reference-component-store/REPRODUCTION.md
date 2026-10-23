# Reproduce the exact source closure

Use an already prepared official Lean 4.21.0 installation and Mathlib checkout at 308445d7985027f538e281e18df29ca16ede2ba3 with matching compiled caches and the package commits in PUBLIC_SOURCE_MANIFEST.json. Set LEAN_HOME, MATHLIB_HOME and the shared LEAN_REPLAY_LOCK. Git, Python3, sha256sum, timeout and flock are required. There is no automatic installer, cache download or elan invocation.

From this package directory:

```sh
set -eu
: "$LEAN_HOME" "$MATHLIB_HOME" "$LEAN_REPLAY_LOCK"
test -x "$LEAN_HOME/bin/lean"
unset LEAN_OPTS LEAN_PATH
"$LEAN_HOME/bin/lean" --version | grep -Eq '^Lean \(version 4\.21\.0([,)]| )'
[ "$(git -C "$MATHLIB_HOME" rev-parse HEAD)" = 308445d7985027f538e281e18df29ca16ede2ba3 ]
[ -z "$(git -C "$MATHLIB_HOME" status --porcelain --untracked-files=no)" ]
export MATHLIB_HOME
python3 - <<'PY_CHECK'
import json,os,pathlib,subprocess
m=json.load(open('PUBLIC_SOURCE_MANIFEST.json'));root=pathlib.Path(os.environ['MATHLIB_HOME'])
for x in m['runtime']['official_package_commits']:
    p=root/'.lake/packages'/x['name']
    assert subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()==x['commit']
    assert not subprocess.check_output(['git','-C',str(p),'status','--porcelain','--untracked-files=no'],text=True).strip()
PY_CHECK
exec 9>"$LEAN_REPLAY_LOCK"
flock 9
work=$(mktemp -d)
mkdir -p "$work/sources" "$work/objects" "$work/logs"
git init -q "$work/upstream"
git -C "$work/upstream" fetch --no-tags --depth=1 https://github.com/CrocSwap/integer-mult-bounds.git 299eb8effe080183313757ac36e76c1b98ed9fae
git -C "$work/upstream" show 299eb8effe080183313757ac36e76c1b98ed9fae:research/e8-lemma-g-lean/LemmaG/Stream.lean > "$work/sources/FreshScalarSupportStream.lean"
git -C "$work/upstream" fetch --no-tags --depth=1 https://github.com/bitplane/integer-mult-bounds.git 5bde684f9189b59d1388c089ec5475fb5cf59565
git -C "$work/upstream" show 5bde684f9189b59d1388c089ec5475fb5cf59565:research/lean-unitary-prefix-norm/PrefixNorm.lean > "$work/PrefixNorm.original.lean"
export work
python3 - <<'PY_DERIVE'
import pathlib,hashlib,os
w=pathlib.Path(os.environ['work']);b=(w/'PrefixNorm.original.lean').read_bytes()
assert hashlib.sha256(b).hexdigest()=='d1889e7402bc4ff4d2f78cd84034b51fd91d3020c17d65ddc3cb2c53b87621b1'
a=b'import LemmaG.Stream\n';c=b'import FreshScalarSupportStream\n';assert b.count(a)==1
(w/'sources/FreshScalarPrefixNorm.lean').write_bytes(b.replace(a,c,1))
PY_DERIVE
cp sources/IndependentEntryUpdates.lean sources/FreshComponentStoreFoldRefinement.lean sources/FreshReferenceMinusHalfStore.lean "$work/sources/"
python3 - <<'PY_HASH'
import pathlib,hashlib,json,os
w=pathlib.Path(os.environ['work']);m=json.load(open('PUBLIC_SOURCE_MANIFEST.json'))
expected={x['module']:(x['bytes'],x['sha256']) for x in m['shipped_modules']}
for x in m['public_prerequisites']:
    expected[x['module']]=(x.get('derived_bytes',x.get('bytes')),x.get('derived_sha256',x.get('sha256')))
for name,(size,digest) in expected.items():
    b=(w/'sources'/(name+'.lean')).read_bytes();assert len(b)==size and hashlib.sha256(b).hexdigest()==digest,name
PY_HASH
libpath="$work/objects:$MATHLIB_HOME/.lake/build/lib/lean"
for p in plausible LeanSearchClient importGraph proofwidgets aesop Qq batteries Cli; do
  libpath="$libpath:$MATHLIB_HOME/.lake/packages/$p/.lake/build/lib/lean"
done
for module in FreshScalarSupportStream IndependentEntryUpdates FreshScalarPrefixNorm FreshComponentStoreFoldRefinement FreshReferenceMinusHalfStore; do
  available_kib=$(df -Pk "$work" | awk 'NR==2 {print $4}')
  [ "$available_kib" -ge 8388608 ] || { echo 'Need at least 8 GiB free'; exit 1; }
  set +e
  (ulimit -v 4194304; LEAN_PATH="$libpath" timeout --signal=KILL 60s "$LEAN_HOME/bin/lean" -j1 -o "$work/objects/$module.olean" "$work/sources/$module.lean") >"$work/logs/$module.stdout" 2>"$work/logs/$module.stderr"
  result=$?
  set -e
  printf '%s\n' "$result" >"$work/logs/$module.exit-code"
  [ "$result" -eq 0 ] || { echo "Stopped; complete logs retained in $work/logs"; exit "$result"; }
done
printf 'Sources, objects and per-module logs retained in %s\n' "$work"
```

This is a deterministic reconstruction and reproduction recipe, not a report of another candidate replay. It preserves the one acknowledged warning. Existing accepted source/object evidence is retained separately. Prepared dependencies are required; stop rather than silently installing or rebuilding them.
