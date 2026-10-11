"""#493's R489 bit word with #495's retimed complex word on hybrid cross-copy hosting: fresh replay on #494's branch.
usage: python -B research/r489-retimed-cross-copy-complex/verify.py /absolute/new/output [--parent-output /absolute/completed/494/output] [--dry-run]
By default this first runs #494's verify.py unchanged (#493's verify.sh, #442's complete verify.py, #448's cross-copy
hosting of #433's complex template, its independent audit and the exact assembly) and checks it against #494's
EXPECTED.json. --parent-output reuses a completed #494 output instead: its receipt status, its manifest digest, every
step-log digest and RESULT.json against #494's EXPECTED.json are checked, and the receipt says the parent was reused.
Then the candidate steps below run, RESULT.json is compared with EXPECTED.json and kappa must exceed #494's.
(#493's script needs numpy, sympy, a C++17 compiler and Boost headers: BOOST_INCLUDE.)"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, time
from fractions import Fraction as Q
assert __debug__
ROOT = Path(__file__).resolve().parent; RESEARCH = ROOT.parent
P494 = RESEARCH / 'r489-cross-copy-complex'; P493 = RESEARCH / 'e8-bit-carrier-skeleton'; P442 = RESEARCH / 'idle-axis-hosting'
PARENT_STATUS = 'PASS_FULL_R489_BIT_CROSS_COPY_COMPLEX_COMPOSITION'
# ---- candidate steps: (name, script, args).  Script paths and args are formatted with:
#   {pkg} this package, {p494} {p493} {p442} the parent packages, {out} the new output, {parent} the #494 output,
#   {pr493} = {parent}/pr493 (bit supplier), {up442} = {parent}/upstream442, {changed442} = {up442}/parent/changed
# The last step must write {out}/RESULT.json with at least the keys listed in EXPECTED.json.
CANDIDATE = [
    ('complex-word', '{pkg}/code/build_word.py', ['{out}/word']),
    ('complex-hybrid-cross-copy-hosting', '{pkg}/code/complex_retimed9.py',
     ['{changed442}/split-centres', '{changed442}/work/complex-nine-native/DATA-PHASES.json', '{out}/word/split-centres', '{out}/complex']),
    ('complex-finite-invoice', '{pkg}/code/invoice_retimed9.py', ['{out}/complex', '{out}/word/split-centres', '{changed442}/split-centres', '{out}/invoice']),
    ('independent-complex-audit', '{pkg}/code/audit_retimed9.py',
     ['{changed442}/split-centres', '{changed442}/work/complex-nine-native/DATA-PHASES.json', '{out}/word/split-centres', '{out}/complex', '{out}/CAUDIT.json']),
    ('exact-assembly', '{pkg}/code/assemble_complex.py',
     ['{pr493}', '{p493}', '{up442}', '{out}/invoice', '{out}/complex', '{out}/CAUDIT.json', '{out}/RESULT.json',
      '--status', 'PASS_CONDITIONAL_R489_BIT_WITH_RETIMED_CROSS_COPY_COMPLEX_ASSEMBLY',
      '--interface', 'complex side: PR495 retimed kernel word (PR449 kernel, PR458 paid two-sided adapters) with PR442 idle-data hosting, '
                     'PR448 cross-copy slots for width-nine residuals and whole PR495 entrance routes for entering residuals; '
                     'bit side: whole-residual hosting only']),
]
ap = argparse.ArgumentParser(); ap.add_argument('output', type=Path); ap.add_argument('--parent-output', type=Path)
ap.add_argument('--dry-run', action='store_true', help='development only: skip this package\'s manifest and EXPECTED.json, write RESULT.json, no receipt, exit 3')
a = ap.parse_args()
out = a.output.resolve(); assert not out.exists() and not out.is_relative_to(RESEARCH)
read = lambda p: json.loads(Path(p).read_text()); sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(d): return {p.relative_to(d).as_posix(): sha(p) for p in d.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
def integrity():
    if not a.dry_run:
        files = inventory(ROOT); files.pop('MANIFEST.json'); assert files == read(ROOT / 'MANIFEST.json')['files'], 'manifest mismatch'
        src = read(ROOT / 'SOURCE.json'); assert sha(P494 / 'MANIFEST.json') == src['pr494_manifest_sha256'], '#494 changed'
    m = read(P494 / 'MANIFEST.json'); files = inventory(P494); files.pop('MANIFEST.json'); assert files == m['files'], '#494 files'
    assert sha(P493 / 'MANIFEST.sha256') == m['pr493_manifest_sha256'] and sha(P442 / 'MANIFEST.json') == m['pr442_manifest_sha256']
integrity(); out.mkdir(parents=True); steps = []; PY = sys.executable
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.setdefault('PYTHON', PY)
env.pop('PYTHONOPTIMIZE', None)
def run(name, cmd, cwd=None):
    t = time.monotonic(); log = out / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f: q = subprocess.run([str(c) for c in cmd], env=env, stdout=f, stderr=subprocess.STDOUT, cwd=cwd)
    if q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-3000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 1), log_sha256=sha(log))); print('PASS', name, flush=True)
try:
    if a.parent_output:
        parent = a.parent_output.resolve(); r = read(parent / 'RECEIPT.json')
        assert r['status'] == PARENT_STATUS and r['manifest_sha256'] == sha(P494 / 'MANIFEST.json'), 'not a #494 receipt for this tree'
        for c in r['checks']: assert sha(parent / (c['name'] + '.log')) == c['log_sha256'], ('step log changed', c['name'])
    else:
        parent = out / 'parent494'; run('parent-494-full', [PY, '-B', P494 / 'verify.py', parent])
    ref = read(parent / 'RESULT.json'); exp494 = read(P494 / 'EXPECTED.json')
    for k, v in exp494.items(): assert ref[k] == v, ('#494 result', k)
    ctx = dict(pkg=ROOT, p494=P494, p493=P493, p442=P442, out=out, parent=parent, pr493=parent / 'pr493',
               up442=parent / 'upstream442', changed442=parent / 'upstream442/parent/changed')
    assert CANDIDATE, 'no candidate steps defined'
    for name, script, args in CANDIDATE: run(name, [PY, '-B', script.format(**ctx), *[str(x).format(**ctx) for x in args]])
    actual = read(out / 'RESULT.json')
    if a.dry_run: print('DRY RUN (no receipt):', json.dumps(actual, indent=2)); sys.exit(3)
    expected = read(ROOT / 'EXPECTED.json')
    for k, v in expected.items(): assert actual[k] == v, (k, actual[k], v)
    assert Q(actual['kappa']) > Q(exp494['kappa']), 'kappa does not exceed #494'
    integrity()
    receipt = dict(status='PASS_COMPONENTS_WITH_VERIFIED_PR494_REUSE' if a.parent_output else 'PASS_FULL_R489_BIT_RETIMED_CROSS_COPY_COMPLEX_COMPOSITION',
                   mode='parent-reuse' if a.parent_output else 'full', kappa=actual['kappa'], kappa_decimal=actual['kappa_decimal'],
                   reference_pr494_kappa=exp494['kappa'], manifest_sha256=sha(ROOT / 'MANIFEST.json'),
                   parent_receipt_sha256=sha(parent / 'RECEIPT.json'), checks=steps, python=sys.version.split()[0])
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt, indent=2))
except SystemExit: raise
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
