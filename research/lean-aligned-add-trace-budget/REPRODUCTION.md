# Reproduce the exact aligned-ADD/trace source closure

Use an already prepared official Lean 4.21.0 installation and Mathlib checkout/caches at the manifest commit, with its eight pinned package checkouts. Set LEAN_HOME, MATHLIB_HOME and a shared LEAN_REPLAY_LOCK. Git, Python3, timeout and flock are required. The recipe never invokes elan or installs/rebuilds dependencies. Run from this package directory.

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
export work
python3 - <<'PY_SOURCES'
import pathlib,hashlib,json,os,subprocess
w=pathlib.Path(os.environ['work']);m=json.load(open('PUBLIC_SOURCE_MANIFEST.json'))
for d in ['sources','objects','logs','upstream']:(w/d).mkdir()
def run(*a):return subprocess.check_output(list(a))
run('git','init','-q',str(w/'upstream'));fetched=set()
for x in m['public_prerequisites']:
    key=(x['repository'],x['commit'])
    if key not in fetched:
        run('git','-C',str(w/'upstream'),'fetch','--no-tags','--depth=1','https://github.com/'+x['repository']+'.git',x['commit']);fetched.add(key)
    b=run('git','-C',str(w/'upstream'),'show',x['commit']+':'+x['path'])
    if 'replacement' in x:
        assert len(b)==x['upstream_bytes'] and hashlib.sha256(b).hexdigest()==x['upstream_sha256']
        r=x['replacement'];a=r['before'].encode();c=r['after'].encode();assert b.count(a)==r['count']==1
        b=b.replace(a,c,1)
    size=x.get('derived_bytes',x.get('bytes'));sha=x.get('derived_sha256',x.get('sha256'))
    assert len(b)==size and hashlib.sha256(b).hexdigest()==sha
    (w/'sources'/(x['module']+'.lean')).write_bytes(b)
for x in m['shipped_modules']:
    b=pathlib.Path(x['path']).read_bytes()
    assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
    (w/'sources'/(x['module']+'.lean')).write_bytes(b)
(w/'order').write_text('\n'.join(m['compile_order'])+'\n')
PY_SOURCES
libpath="$work/objects:$MATHLIB_HOME/.lake/build/lib/lean"
for p in plausible LeanSearchClient importGraph proofwidgets aesop Qq batteries Cli; do
  libpath="$libpath:$MATHLIB_HOME/.lake/packages/$p/.lake/build/lib/lean"
done
while IFS= read -r module; do
  available_kib=$(df -Pk "$work" | awk 'NR==2 {print $4}')
  [ "$available_kib" -ge 8388608 ] || { echo 'Need at least 8 GiB free'; exit 1; }
  set +e
  (ulimit -v 4194304; LEAN_PATH="$libpath" timeout --signal=KILL 60s "$LEAN_HOME/bin/lean" -j1 -o "$work/objects/$module.olean" "$work/sources/$module.lean") >"$work/logs/$module.stdout" 2>"$work/logs/$module.stderr"
  result=$?
  set -e
  printf '%s\n' "$result" >"$work/logs/$module.exit-code"
  [ "$result" -eq 0 ] || { echo "Stopped; complete logs retained in $work/logs"; exit "$result"; }
done < "$work/order"
printf 'Sources, objects and logs retained in %s\n' "$work"
```

This is a reproduction recipe, not a claim of another publication-candidate replay. Stop if the prepared prerequisites are unavailable. The four shipped modules produced no warnings in their accepted runs; any warnings from exact reused prerequisites must be preserved in their logs.
