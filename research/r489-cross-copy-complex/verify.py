"""Fresh replay: #493's R489 bit supplier through its own verify.sh (eleven-stage whole-residual hosting, controls),
#442's complete verifier (which rebuilds #434 and the #433 complex word), then #448's cross-copy hosting of that
complex template, an independent audit of it, and the exact assembly of the two suppliers.
usage: python -B research/r489-cross-copy-complex/verify.py /absolute/new/output
(#493's script needs numpy, sympy, a C++17 compiler and Boost headers: BOOST_INCLUDE; the new steps are standard library.)"""
from pathlib import Path
import gzip, hashlib, json, os, subprocess, sys, time
assert __debug__
ROOT = Path(__file__).resolve().parent; P493 = ROOT.parent / 'e8-bit-carrier-skeleton'; P442 = ROOT.parent / 'idle-axis-hosting'
out = Path(sys.argv[1]).resolve(); assert not out.exists() and not out.is_relative_to(ROOT.parent)
read = lambda p: json.loads(Path(p).read_text()); sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def integrity():
    files = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts}
    m = read(ROOT / 'MANIFEST.json'); assert files == m['files'], 'manifest mismatch'
    assert sha(P493 / 'MANIFEST.sha256') == m['pr493_manifest_sha256'] and sha(P442 / 'MANIFEST.json') == m['pr442_manifest_sha256'], 'parent package changed'
integrity(); out.mkdir(parents=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None); steps = []
def run(name, cmd):
    t = time.monotonic(); log = out / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f: q = subprocess.run([str(c) for c in cmd], env=env, stdout=f, stderr=subprocess.STDOUT)
    if q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-3000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 1), log_sha256=sha(log))); print('PASS', name, flush=True)
py = lambda name, *a: run(name, [sys.executable, '-B', *a])
try:
    run('pr493-bit-supplier-full', ['bash', P493 / 'verify.sh', out / 'pr493'])
    r493 = read(out / 'pr493/RESULT.json'); assert r493['kappa']['pr448']['kappa'] == read(ROOT / 'EXPECTED.json')['kappa']
    py('pr442-full', P442 / 'verify.py', out / 'upstream442')
    changed = out / 'upstream442/parent/changed'
    py('complex-cross-copy-hosting', ROOT / 'complex_split.py', changed / 'split-centres', out / 'complex')
    py('independent-complex-audit', ROOT / 'audit_complex_only.py', changed, out / 'complex', out / 'CAUDIT.json')
    py('exact-assembly', ROOT / 'assemble_489.py', out / 'pr493', P493, out / 'upstream442', out / 'complex', out / 'CAUDIT.json', out / 'RESULT.json')
    actual = read(out / 'RESULT.json'); expected = read(ROOT / 'EXPECTED.json')
    for k, v in expected.items(): assert actual[k] == v, (k, actual[k], v)
    h = hashlib.sha256(gzip.decompress((out / 'complex/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(); assert h == expected['complex_template_sha256']
    integrity()
    receipt = dict(status='PASS_FULL_R489_BIT_CROSS_COPY_COMPLEX_COMPOSITION', kappa=actual['kappa'], kappa_decimal=actual['kappa_decimal'],
                   manifest_sha256=sha(ROOT / 'MANIFEST.json'), checks=steps, python=sys.version.split()[0])
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt, indent=2))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
