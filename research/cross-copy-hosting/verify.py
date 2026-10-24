"""Fresh replay: #434 in full, then cross-copy idle-axis hosting of both suppliers, independent audit and exact assembly.
usage: python -B research/cross-copy-hosting/verify.py /absolute/new/output   (Python 3.11+, standard library only)"""
from pathlib import Path
import gzip, hashlib, json, os, subprocess, sys, time
assert __debug__
ROOT = Path(__file__).resolve().parent; PARENT = ROOT.parent / 'e8-early-reset-kernel'
out = Path(sys.argv[1]).resolve(); assert not out.exists() and not out.is_relative_to(ROOT.parent)
read = lambda p: json.loads(Path(p).read_text()); sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def integrity():
    files = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name != 'MANIFEST.json' and '__pycache__' not in p.parts}
    assert files == read(ROOT / 'MANIFEST.json')['files'], 'manifest mismatch'
    assert sha(PARENT / 'MANIFEST.json') == read(ROOT / 'MANIFEST.json')['parent_manifest_sha256'], 'parent package changed'
integrity(); out.mkdir(parents=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None); steps = []
def run(name, file, *args, cwd=None):
    t = time.monotonic(); log = out / (name + '.log'); print('RUN', name, flush=True)
    with log.open('w') as f: q = subprocess.run([sys.executable, '-B', str(file), *map(str, args)], cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT)
    if q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-3000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - t, 1), log_sha256=sha(log))); print('PASS', name, flush=True)
try:
    run('parent-434-full', PARENT / 'verify.py', out / 'parent')
    changed = out / 'parent/changed'
    run('bit-cross-copy-hosting', ROOT / 'bit_split.py', 'bit426-source-centres/global', 'bit426-source-centres', out / 'bit', cwd=changed)
    run('complex-cross-copy-hosting', ROOT / 'complex_split.py', 'split-centres', out / 'complex', cwd=changed)
    run('independent-audit', ROOT / 'audit_split.py', changed, out / 'bit', out / 'complex', out / 'AUDIT.json')
    run('exact-assembly', ROOT / 'assemble_split.py', changed, out / 'bit', out / 'complex', out / 'AUDIT.json', out / 'RESULT.json')
    run('toy-two-family-program-identity', ROOT / 'toy_two_family_check.py')
    assert json.loads((out / 'toy-two-family-program-identity.log').read_text()) == read(ROOT / 'TOY-EXPECTED.json'), 'toy check output differs'
    actual = read(out / 'RESULT.json'); expected = read(ROOT / 'EXPECTED.json')
    for k, v in expected.items(): assert actual[k] == v, (k, actual[k], v)
    for side, d in (('bit', 'bit'), ('complex', 'complex')):
        h = hashlib.sha256(gzip.decompress((out / d / 'GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest()
        assert h == expected[side + '_template_sha256'], (side, h)
    integrity()
    receipt = dict(status='PASS_FULL_CROSS_COPY_HOSTING_COMPOSITION', kappa=actual['kappa'], kappa_decimal=actual['kappa_decimal'],
                   gain_over_pr434_percent=actual['gain_over_pr434_percent'], manifest_sha256=sha(ROOT / 'MANIFEST.json'), checks=steps,
                   python=sys.version.split()[0])
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt, indent=2))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
