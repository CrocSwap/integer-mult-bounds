# Reproduction

This recipe assumes an existing Lean 4.21.0 / Mathlib checkout at 308445d7985027f538e281e18df29ca16ede2ba3 with its locked official dependencies and prepared objects. It does not install anything. Obtain permission separately before installation. Use the immutable public sources named in PUBLIC_SOURCE_MANIFEST.json; a checkout containing their Git objects is required. Stop if a revision or hash is absent.

Set SOURCE_REPO to that Git repository, PACKAGE to this package, and WORK to a new empty directory. The materializer below checks every raw source before any import-only recipe, then checks its exact derived hash. It does not fetch, build, run the diagnostic or extract the archive.

```sh
set -eu
: "${SOURCE_REPO:?set the repository containing the pinned public commits}"
: "${PACKAGE:?set this package directory}"
: "${WORK:?set a fresh directory}"
test ! -e "$WORK"
mkdir -p "$WORK/sources" "$WORK/objects"
export SOURCE_REPO PACKAGE WORK
python3 - <<'PYCODE'
import os,json,pathlib,subprocess,hashlib
p=pathlib.Path(os.environ['PACKAGE']);w=pathlib.Path(os.environ['WORK']);repo=os.environ['SOURCE_REPO']
m=json.loads((p/'PUBLIC_SOURCE_MANIFEST.json').read_text())
for r in m['public_prerequisites']:
 b=subprocess.check_output(['git','-C',repo,'show',r['revision']+':'+r['path']])
 recipe=r.get('derived_source_recipe')
 expected=recipe['raw_sha256'] if recipe else r['sha256']
 assert hashlib.sha256(b).hexdigest()==expected,r['module']
 if recipe:
  q=recipe['replace'];old=q['before'].encode();new=q['after'].encode()
  assert b.count(old)==q['count'];b=b.replace(old,new)
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['module']
 target=w/'sources'/(r['module'].replace('.','/')+'.lean');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
for r in m['new_modules']:
 b=(p/r['proposed_path']).read_bytes()
 assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],r['module']
 (w/'sources'/(r['module']+'.lean')).write_bytes(b)
b=(p/'L450_ENTRY.json').read_bytes()
assert len(b)==1627 and hashlib.sha256(b).hexdigest()=='49bd7af0e018196137adda44ee5d386d3eaa5b1f30a2b834cd865381d6e7a566'
print('Exact public reconstruction verified; no compiler or parser ran.')
PYCODE
```

## Runtime and shared admission

Use already prepared Lean 4.21.0 and Mathlib at the exact revision below. No installation, dependency recovery or cache download is part of this recipe. `MATHLIB` must point to the prepared checkout. `OFFICIAL_LEAN_PATH` must list only its required prepared official object directories. Relevant packages are Mathlib, batteries, Qq, aesop, proofwidgets, importGraph, LeanSearchClient and plausible. Cli is a locked source provenance entry but is not used as an object directory.

`COMPILER_LOCK` must be the existing canonical compiler lock used by all research jobs on the machine, for example `$NATIVE_ROOT/RESEARCH_COMPILER.lock`. Do not invent a separate lock to bypass another job. Every command below takes that same exclusive flock, checks at least 8 GiB free space after admission, then uses one compiler thread, a 4 GiB address-space cap and a 60-second wall cap. Each root is its own bounded phase.

The following verifies the exact accepted Linux Lean binary and Mathlib/official package revision pins before any compilation. A different-platform compiler is a separate reproduction context and must not be reported as this binary's exact replay.

```sh
set -eu
: "${LEAN:?set the exact already installed Lean binary}"
: "${MATHLIB:?set the prepared Mathlib checkout}"
: "${OFFICIAL_LEAN_PATH:?set the verified required official object directories}"
: "${COMPILER_LOCK:?set the existing shared canonical compiler lock}"
: "${WORK:?set the materialized source/object directory}"
: "${PACKAGE:?set this package directory}"
export LEAN MATHLIB OFFICIAL_LEAN_PATH COMPILER_LOCK WORK PACKAGE
unset LEAN_PATH LEAN_OPTS
printf '%s  %s\n' cbf5fd536e142ef1beaccf33f788fd8a7f3f29fb214e75c11319a8d8677b4b2b "$LEAN" | sha256sum -c -
python3 - <<'PYCODE'
import os,json,pathlib,subprocess,re
reported=subprocess.check_output([os.environ['LEAN'],'--version'],text=True).strip()
assert re.match(r"^Lean \(version 4\.21\.0(?:,|\))",reported),reported
print(reported)
m=pathlib.Path(os.environ['MATHLIB'])
def head(p):return subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
assert head(m)=='308445d7985027f538e281e18df29ca16ede2ba3'
assert (m/'lean-toolchain').read_text().strip()=='leanprover/lean4:v4.21.0'
lock=json.loads((m/'lake-manifest.json').read_text())
for p in lock['packages']:
 if p.get('type')=='git':
  assert head(m/'.lake/packages'/p['name'])==p['rev'],p['name']
for d in os.environ['OFFICIAL_LEAN_PATH'].split(':'):
 assert pathlib.Path(d).is_dir(),d
print('Exact runtime/source revisions and prepared directory presence verified.')
PYCODE
```

## Choose one reproduction path

A. With independently verified accepted predecessor source/object pairs, set `RETAINED_LEAN_PATH` to their object directories and `ORDER_FILE` to `$PACKAGE/NEW_BUILD_ORDER.txt`. Only the four newly published roots compile. Verify the predecessor identities against their public manifests first; no private receipt or private object is required by the source statements.

B. An independent reader with only prepared official caches can set `RETAINED_LEAN_PATH` to the empty string and `ORDER_FILE` to `$PACKAGE/BUILD_ORDER.txt`. This compiles the complete 98-module public research closure in dependency order, using the materialized sources from the first section. It needs no private predecessor objects. The 94 public prerequisites are reused unchanged, apart from the one exact import-only recipe in the manifest. This optional fresh reproduction has not been run for this handoff and is not a new acceptance claim for a combined rebuild. Stop and retain evidence if any individual root exceeds its unchanged cap; do not automatically expand limits or install dependencies.

Both paths use the same command below. It saves each root's stdout, stderr, start/finish times and actual exit code before stopping on failure. None of the four new roots or the minimal closure contains the separate L450 #eval diagnostic. The logical parser and field-equation premises must be read from the printed types; compilation does not discharge them.

```sh
set -eu
: "${ORDER_FILE:?choose NEW_BUILD_ORDER.txt or BUILD_ORDER.txt as above}"
RETAINED_LEAN_PATH=${RETAINED_LEAN_PATH-}
export RETAINED_LEAN_PATH ORDER_FILE
mkdir -p "$WORK/logs"
python3 - <<'PYCODE'
import os,pathlib,subprocess,fcntl,resource,shutil,json,datetime,sys
w=pathlib.Path(os.environ['WORK']);lean=os.environ['LEAN']
manifest=json.loads((pathlib.Path(os.environ['PACKAGE'])/'PUBLIC_SOURCE_MANIFEST.json').read_text())
options={r['module']:r['accepted_compiler_options'] for r in manifest['new_modules']}
parts=[str(w/'objects')]
if os.environ['RETAINED_LEAN_PATH']:
 parts.extend(os.environ['RETAINED_LEAN_PATH'].split(':'))
parts.extend(os.environ['OFFICIAL_LEAN_PATH'].split(':'))
env={k:v for k,v in os.environ.items() if k not in ('LEAN_PATH','LEAN_OPTS')}
env['LEAN_PATH']=':'.join(parts)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def limits():resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
for name in pathlib.Path(os.environ['ORDER_FILE']).read_text().splitlines():
 if not name:continue
 stem=name.replace('.','/')
 source=w/'sources'/(stem+'.lean');obj=w/'objects'/(stem+'.olean')
 obj.parent.mkdir(parents=True,exist_ok=True)
 prefix=w/'logs'/name
 # Fresh logs prevent an accidental rerun from silently replacing evidence.
 receipt=prefix.with_suffix('.result.json')
 assert not receipt.exists(),f'Existing result for {name}; reconcile before any replay'
 with open(os.environ['COMPILER_LOCK'],'a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  assert shutil.disk_usage(w).free>=8*1024**3,'Less than 8 GiB free after admission'
  command=[lean,*options.get(name,['-j1']),'-o',str(obj),str(source)]
  record={'module':name,'command':command,'started_utc':utc()}
  with open(str(prefix)+'.stdout','xb') as out,open(str(prefix)+'.stderr','xb') as err:
   try:
    run=subprocess.run(command,env=env,stdout=out,stderr=err,timeout=60,preexec_fn=limits)
    record['exit_code']=run.returncode;record['timeout']=False
   except subprocess.TimeoutExpired:
    record['exit_code']=None;record['timeout']=True
  record.update(finished_utc=utc(),object_present=obj.exists())
  receipt.write_text(json.dumps(record,indent=2)+'\n')
  if record['exit_code']!=0 or not record['object_present']:
   sys.exit(f'Stopped at {name}; complete logs and result retained at {prefix}')
print('Requested serial source order completed; independently review all probes/types.')
PYCODE
```

Compare all four new roots' complete probes/types with ACCEPTANCE.json, and inspect every other root's output under the optional fresh path. Missing objects, unsupported axioms, warnings, errors or resource failures require review rather than silent continuation. These compilation paths were not executed during handoff preparation.

## Optional single-entry identity check

Given an independently obtained compressed witness file, check its compressed size, SHA256 and Git blob against `ARTIFACT_PROVENANCE.json`. A bounded decompression may then compare only the recorded interval with `L450_ENTRY.json`, while checking the full decompressed size/hash. This checks external byte identity; it does not authenticate the provider, prove a Lean parser equation, or establish all witness entries. The donor Python verifier is unnecessary for reproducing these Lean source results and is not part of this recipe.

The selected field equations are not hidden by reproduction: the final selected theorem prints five precise named-field equations as hypotheses. Read them in `ACCEPTANCE.json`; constructing a matching single-entry AST is a separate application and proving the original file's AST is a separate obligation.
