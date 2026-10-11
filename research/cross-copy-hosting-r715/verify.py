"""Fresh replay: #472 in full (its #458 complex parent and the R715 whole-hosted bit composition), then cross-copy
idle-axis hosting of the R715 eleven-stage bit template and of #442's complex template, independent audit and exact
assembly.  usage: python -B research/cross-copy-hosting-r715/verify.py /absolute/new/output [--quick]
(--quick is passed through to #472 and skips only #443's inherited exhaustive negative controls; #472's parent needs
numpy, mpmath, sympy, a C++17 compiler and Boost headers, BOOST_INCLUDE if they are not on the include path.)"""
from pathlib import Path
import gzip, hashlib, json, os, subprocess, sys, time
assert __debug__
ROOT = Path(__file__).resolve().parent; PARENT = ROOT.parent / 'e8-r715-whole-hosted'
out = Path(sys.argv[1]).resolve(); quick = '--quick' in sys.argv[2:]; assert not out.exists() and not out.is_relative_to(ROOT.parent)
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
    run('parent-472-full', PARENT / 'verify.py', out / 'parent', *(['--quick'] if quick else []))
    rep = out / 'parent'; changed = rep / 'parent458/parent454/parent451/parent445/parent444/upstream442/parent/changed'
    run('bit-cross-copy-hosting-r715', ROOT / 'bit_split11.py', rep / 'bit', rep / 'local', out / 'bit')
    (out / 'bit/GEOMETRY.json').write_bytes((rep / 'bit/GEOMETRY.json').read_bytes())
    run('complex-cross-copy-hosting', ROOT / 'complex_split.py', changed / 'split-centres', out / 'complex')
    run('independent-audit', ROOT / 'audit_split11.py', rep / 'bit', rep / 'local', out / 'bit', changed, out / 'complex', out / 'AUDIT.json')
    run('exact-assembly', ROOT / 'assemble_split11.py', rep, out / 'bit', out / 'complex', out / 'AUDIT.json', out / 'RESULT.json')
    actual = read(out / 'RESULT.json'); expected = read(ROOT / 'EXPECTED.json')
    for k, v in expected.items(): assert actual[k] == v, (k, actual[k], v)
    h = hashlib.sha256(gzip.decompress((out / 'complex/GLOBAL-TEMPLATE.json.gz').read_bytes())).hexdigest(); assert h == expected['complex_template_sha256']
    integrity()
    receipt = dict(status='PASS_FULL_CROSS_COPY_R715_COMPOSITION', mode='quick' if quick else 'full', kappa=actual['kappa'], kappa_decimal=actual['kappa_decimal'],
                   gain_over_pr472_percent=actual['gain_over_pr472_percent'], manifest_sha256=sha(ROOT / 'MANIFEST.json'), checks=steps, python=sys.version.split()[0])
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt, indent=2))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), completed=steps), indent=2) + '\n'); raise
