"""fast_verify.py -- fast full verification of a derived #1218-style package.

Usage (Windows venv python or any py3.11+):
  PY -B scratch/ReplaySpeed/fast_verify.py PKG_DIR --work NEWWORK [--jobs 4] [--cache DIR]

PKG_DIR = <repo>/research/<slug> containing verify.py (the leader's recipe).
NEWWORK must not exist.  Result: NEWWORK/RESULT.json written by the package's
OWN unmodified verify.py (status PASS_..., kappa_decimal), plus NEWWORK/FAST.json timings.

What it does (nothing in the proof is weakened or replaced):
 1. Reads the package's verify.py to find the base/extra words.  Runs the two
    fresh native replays (replay_native.py: native, ledgers, local-replay,
    wrappers, phases) CONCURRENTLY, with the only slow step ('phases', exact
    per-edge Clifford lowering, 98 of ~105 s) executed by
    phases_parallel.py: the byte-identical computation split over --jobs
    processes by edge (CLIFFORD-RECIPES.json is asserted byte-identical in the
    self-test; CLIFFORD-REVIEW.json differs only in its 'seconds' field).
 2. Runs the package verify.py with --base-native-from/--extra-native-from on
    those directories.  That path re-checks FULL-WORD == word, STEPS.json
    step names/exit codes, and then runs every other stage unchanged
    (literal words, independent-local, fusion/x54 controls, leaver premise,
    literal-construct, strict-global).
--cache DIR (dev screening only): phase lowering results are memoised by frame content, so a derived
word that changes a few frames recomputes only edges touching them.
The autoshipper's own full proof (fresh native, sequential) is unchanged.
"""
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOWIN = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
ap = argparse.ArgumentParser()
ap.add_argument('pkg', type=Path)
ap.add_argument('--work', type=Path, required=True)
ap.add_argument('--jobs', type=int, default=4)
ap.add_argument('--native-only', action='store_true', help='stop after the two fresh native replays (screen a word: NEWWORK/native-*/local/*)')
ap.add_argument('--native-cache', type=Path, help='DIR/<sha256 of word file>/ holds a completed, hash-checked native replay of that exact word; reused when present (verify.py still re-checks FULL-WORD==word and STEPS), filled after a fresh native otherwise.')
ap.add_argument('--cache', type=Path, help='DEV SCREEN ONLY: memoise per-edge phase lowering keyed by frame content (unchanged edges of a modified word are reused). Not for release proofs.')
a = ap.parse_args()
pkg = a.pkg.resolve(); work = a.work.resolve()
assert not work.exists()
work.mkdir(parents=True)
t0 = time.monotonic()
timing = {}


def log(msg):
    print(f'[{time.monotonic()-t0:7.1f}s] {msg}', flush=True)


# --- stage 0: unpack layout exactly as verify.py does, to locate SRC -------
import tarfile
layout = work / 'layout0'
layout.mkdir()
with tarfile.open(pkg / 'upstream-layout.tar.gz') as t:
    for m in t.getmembers():
        assert m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
    t.extractall(layout, filter='data')
SRC = layout / 'joint1148-round45/source'
RN = SRC / 'research/k8-eight-ends/replay_native.py'
vsrc = (pkg / 'verify.py').read_text()
m = re.findall(r"\('(base|extra)',P/'([^']+)',a\.(?:base|extra)_native_from\)", vsrc)
words = {k: pkg / w for k, w in m}
assert set(words) == {'base', 'extra'}, words

# --- stage 1: concurrent native replays with parallel phases ---------------
env = dict(os.environ, PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
           FAST_PHASES_JOBS=str(max(1, a.jobs // 2 if a.jobs > 1 else 1)),
           FAST_PHASES_IMPL=str(HERE / 'phases_parallel.py'))
if a.cache:
    env['FAST_PHASES_CACHE'] = str(a.cache.resolve())
env.pop('PYTHONOPTIMIZE', None)
import hashlib, gzip


def fsha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tree_hashes(d):
    return {x.relative_to(d).as_posix(): fsha(x) for x in sorted(d.rglob('*')) if x.is_file() and x.name != 'CACHE.json'}


def cache_hit(word):
    if not a.native_cache:
        return None
    d = a.native_cache.resolve() / fsha(word)
    c = d / 'CACHE.json'
    if not c.is_file():
        return None
    meta = json.loads(c.read_text())
    if meta.get('word_sha256') != fsha(word) or meta.get('files') != tree_hashes(d):
        log('native cache entry %s failed its hash check; ignoring' % d.name)
        return None
    if gzip.decompress((d / 'local/FULL-WORD.json.gz').read_bytes()) != gzip.decompress(Path(word).read_bytes()):
        return None
    return d


def cache_store(word, out):
    if not a.native_cache:
        return
    root = a.native_cache.resolve(); root.mkdir(parents=True, exist_ok=True)
    d = root / fsha(word)
    if d.exists():
        return
    tmp = root / ('.tmp-%s-%d' % (d.name, os.getpid()))
    shutil.copytree(out, tmp)
    (tmp / 'CACHE.json').write_text(json.dumps(dict(word_sha256=fsha(word), files=tree_hashes(tmp)), indent=1))
    try:
        tmp.rename(d)
    except OSError:
        shutil.rmtree(tmp, ignore_errors=True)


natives = {}
procs = {}
for k, w in words.items():
    hit = cache_hit(w)
    if hit:
        natives[k] = hit
        log('native cache hit for %s word (%s)' % (k, hit.name[:12]))
        continue
    out = work / ('native-' + k)
    natives[k] = out
    f = open(work / f'fresh-native-{k}.log', 'w')
    procs[k] = (subprocess.Popen([sys.executable, '-B', str(HERE / 'native_fast.py'), str(RN), str(w), str(out)],
                                 stdout=f, stderr=subprocess.STDOUT, env=env, cwd=layout, creationflags=NOWIN), f)
for k, (p, f) in procs.items():
    rc = p.wait(); f.close()
    assert rc == 0, (k, (work / f'fresh-native-{k}.log').read_text()[-3000:])
timing['native_both'] = time.monotonic() - t0
log('native replays done (both)')

if a.native_only:
    shutil.rmtree(layout)
    (work / 'FAST.json').write_text(json.dumps(timing, indent=2))
    print(json.dumps(timing)); sys.exit(0)

# --- stage 2: the package's own verify.py, reusing those native dirs -------
shutil.rmtree(layout)
vwork = work / 'verify'
env2 = dict(os.environ, PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
t1 = time.monotonic()
r = subprocess.run([sys.executable, '-B', str(pkg / 'verify.py'), '--work', str(vwork),
                    '--base-native-from', str(natives['base']),
                    '--extra-native-from', str(natives['extra'])], env=env2,
                   stdout=(work / 'verify.log').open('w'), stderr=subprocess.STDOUT, creationflags=NOWIN)
timing['verify_reuse'] = time.monotonic() - t1
timing['total'] = time.monotonic() - t0
(work / 'FAST.json').write_text(json.dumps(timing, indent=2))
res = (vwork / 'RESULT.json')
if r.returncode or not res.exists():
    print((work / 'verify.log').read_text()[-4000:])
    sys.exit('FAIL: package verify.py exit %d' % r.returncode)
R = json.loads(res.read_text())
for k, w in words.items():
    if k in procs:
        cache_store(w, natives[k])
log(f"{R['status']} kappa_decimal={R['kappa_decimal']} total={timing['total']:.1f}s")
print(json.dumps(timing))
