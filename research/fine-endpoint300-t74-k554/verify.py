"""Replay of the 1e-300 endpoint refinement over PR1839 (assertions must be enabled).

1. checks this package's MANIFEST;
2. fetches (or takes --dependency) PR1839's immutable package research/capped-fusion-t74-k554 at
   836ef6a1a550f439e42be65423cffd624658af6a and checks every file against that package's own MANIFEST (pinned by SHA256);
3. copies it under --work, applies overlay/ (finer engine constants, recertified SPEC endpoints, 1e-310 slacks, regenerated
   ledger artifacts, updated release checker) and checks the patched tree against overlay/MANIFEST.json file by file;
4. runs the patched package's own verify_release.py: fresh native supplier admission (or --native-cache reuse), strict T74
   admission with both supplier endpoints recertified at 1e-300 by the finer engines, the regenerated exact outer ledger
   (59 strict inequalities, 17 rejecting controls), the independent balance derivation and the inherited evidence replays;
5. binds the release receipt to CLAIM.json and requires a strict improvement over PR1839's exact kappa.
No file of the dependency is edited in place; everything is written under --work.
"""
import argparse, concurrent.futures, hashlib, json, os, shutil, subprocess, sys, time, urllib.request
from fractions import Fraction as Q
from pathlib import Path
P = Path(__file__).resolve().parent
KAPPA_1839 = Q('0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263049999999997996640490086748910957328658012158594')

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())

def main():
    if not __debug__: raise RuntimeError('Assertions required')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--dependency', type=Path, help='local copy of PR1839 research/capped-fusion-t74-k554 (checked file by file)')
    ap.add_argument('--native-cache', type=Path)
    ap.add_argument('--jobs', type=int, default=2)
    ap.add_argument('--arithmetic-only', action='store_true')
    a = ap.parse_args()
    work = a.work.resolve(); assert not work.exists() and not work.is_relative_to(P); work.mkdir(parents=True)
    pins = read(P / 'MANIFEST.json')
    have = {p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p != P / 'MANIFEST.json'}
    assert have == set(pins), sorted(have ^ set(pins))
    for n, h in pins.items(): assert sha(P / n) == h, n
    dep_info = read(P / 'DEPENDENCY.json'); claim = read(P / 'CLAIM.json'); stages = []
    t0 = time.monotonic()
    pkg = work / 'package'
    if a.dependency:
        src = a.dependency.resolve(); assert sha(src / 'MANIFEST.json') == dep_info['manifest_sha256']
        dpins = read(src / 'MANIFEST.json')
        for n, h in dpins.items(): assert sha(src / n) == h, n
        shutil.copytree(src, pkg, ignore=shutil.ignore_patterns('__pycache__'))
    else:
        pkg.mkdir()
        base = 'https://raw.githubusercontent.com/%s/%s/%s/' % (dep_info['repository'], dep_info['head'], dep_info['package'])
        raw = urllib.request.urlopen(base + 'MANIFEST.json', timeout=120).read()
        assert hashlib.sha256(raw).hexdigest() == dep_info['manifest_sha256']; (pkg / 'MANIFEST.json').write_bytes(raw)
        dpins = json.loads(raw)
        def fetch(n):
            f = pkg / n; assert f.resolve().is_relative_to(pkg.resolve())
            data = urllib.request.urlopen(base + n, timeout=300).read(); assert hashlib.sha256(data).hexdigest() == dpins[n], n
            f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(data)
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex: list(ex.map(fetch, dpins))
    have = {p.relative_to(pkg).as_posix() for p in pkg.rglob('*') if p.is_file() and p != pkg / 'MANIFEST.json'}
    assert have == set(dpins), sorted(have ^ set(dpins))
    stages.append(dict(name='dependency', files=len(dpins), manifest_sha256=dep_info['manifest_sha256'], seconds=round(time.monotonic() - t0, 2)))
    # overlay: every overlay file replaces a dependency file of the same path (no new files), then the patched tree must match overlay/MANIFEST.json
    ov = P / 'overlay'
    for f in sorted(ov.rglob('*')):
        if f.is_file():
            rel = f.relative_to(ov).as_posix(); assert rel in dpins or rel == 'MANIFEST.json', rel
            shutil.copy2(f, pkg / rel)
    patched = read(pkg / 'MANIFEST.json')
    assert set(patched) == set(dpins)
    for n, h in patched.items(): assert sha(pkg / n) == h, n
    changed = sorted(n for n in dpins if dpins[n] != patched[n])
    assert changed == sorted(f.relative_to(ov).as_posix() for f in ov.rglob('*') if f.is_file() and f.relative_to(ov).as_posix() != 'MANIFEST.json'), changed
    stages.append(dict(name='overlay', changed=changed))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    env.pop('PYTHONOPTIMIZE', None)
    def run(name, args, cwd):
        t = time.monotonic(); log = work / (name + '.log')
        with log.open('w') as out: r = subprocess.run([sys.executable, '-B', *map(str, args)], cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=r.returncode, seconds=round(time.monotonic() - t, 2), log_sha256=sha(log)))
        (work / 'STAGES.json').write_text(json.dumps(stages, indent=2))
        assert r.returncode == 0, (name, log.read_text()[-3000:]); print('PASS', name, flush=True)
    ledger = read(pkg / 'outer/LEDGER.json'); row = ledger['rows']['struct_boundary_radix_union']
    k = Q(row['kappa']['rational']); assert k == Q(claim['kappa']) and k == Q(read(pkg / 'outer/OUTER-CLAIM.json')['kappa'])
    assert k > KAPPA_1839 and len(row['strict_checks']) == 59 and all(Q(x['rational']) > 0 for x in row['strict_checks'].values())
    assert len(ledger['rejecting_controls']['struct_boundary_radix_union']) == 17
    if a.arithmetic_only:
        tmp = work / 'arithmetic'
        run('outer-regeneration', [pkg / 'outer/run_outer.py', tmp], work)
        out = dict(status='PASS_ARITHMETIC_ONLY', kappa=str(k), kappa_decimal=claim['kappa_decimal'], full_admission=False, stages=stages)
        (work / 'RESULT.json').write_text(json.dumps(out, indent=2) + '\n'); print(out['status'], flush=True); return
    opts = ['--main', work, '--work', work / 'release', '--jobs', str(max(1, a.jobs))]
    if a.native_cache: opts += ['--native-cache', a.native_cache.resolve()]
    run('release', [pkg / 'verify_release.py', *opts], work)
    rec = read(work / 'release/RELEASE-RECEIPT.json')
    assert rec['status'] == 'PASS_RELEASE' and Q(rec['kappa_decimal']) == k == Q(claim['kappa_decimal'])
    asm = read(work / 'release/verify/strict/ASSEMBLY.json'); spec = read(pkg / 'new/SPEC.json'); bj = read(pkg / 'outer/B.json')
    assert Q(asm['complex_lower']) == Q(spec['expected']['complex_lower']) == Q(claim['certified_native_endpoint'])
    assert Q(asm['conservative_complex_lower']) == Q(spec['expected']['conservative_complex_lower']) == Q(claim['certified_conservative_endpoint'])
    assert Q(bj['b']) < Q(asm['complex_lower']) < Q(bj['b_above_endpoint'])
    fine = [m for m in asm['moments'] + asm['conservative_moments'] if Q(m['endpoint']) in (Q(asm['complex_lower']), Q(asm['complex_lower']) + Q(1, 10**300), Q(asm['conservative_complex_lower']), Q(asm['conservative_complex_lower']) + Q(1, 10**300))]
    assert len(fine) >= 4 and all(m['accept'] == (Q(m['endpoint']) in (Q(asm['complex_lower']), Q(asm['conservative_complex_lower']))) for m in fine)
    out = dict(status='PASS_ENDPOINT300_REFINEMENT_FINITE_ADMISSION', kappa=str(k), kappa_decimal=claim['kappa_decimal'],
               gain_over_pr1839=str(k - KAPPA_1839), dependency_head=dep_info['head'], dependency_manifest=dep_info['manifest_sha256'],
               patched_manifest=sha(pkg / 'MANIFEST.json'), package_manifest=sha(P / 'MANIFEST.json'),
               assembly_sha256=sha(work / 'release/verify/strict/ASSEMBLY.json'), release_receipt=rec, stages=stages, scope=claim['scope'])
    (work / 'RESULT.json').write_text(json.dumps(out, indent=2) + '\n'); print(out['status'], flush=True)

if __name__ == '__main__': main()
