"""Verify both suppliers from scratch, then compose their exact endpoints:
  complex: PR #458's paid-adapter kernel (research/e8-complex-adapted-kernel), unchanged, its own full wrapper;
  bit:     the R715 eleven-stage whole-residual supplier (research/e8-r715-eleven-stage-whole), its own full wrapper.
usage: python -B research/e8-r715-paid-complex/verify.py /absolute/new/output
Structure follows PR #460's verify.py (Rohan Arun with OpenAI Codex assistance, Apache-2.0).
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, time
assert __debug__
ROOT = Path(__file__).resolve().parent
ap = argparse.ArgumentParser(); ap.add_argument('output', type=Path); ap.add_argument('--research-root', type=Path, default=ROOT.parent); a = ap.parse_args()
out = a.output.resolve(); research = a.research_root.resolve(); assert not out.exists() and not out.is_relative_to(research)
read = lambda p: json.loads(p.read_text()); sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def inv(p): return {f.relative_to(p).as_posix(): sha(f) for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts}
def integrity():
    actual = inv(ROOT); actual.pop('MANIFEST.json'); assert actual == read(ROOT / 'MANIFEST.json')
    for pin in read(ROOT / 'SOURCE.json').values():
        pkg = research / pin['package']; assert sha(pkg / 'MANIFEST.json') == pin['manifest_sha256'] and sha(pkg / 'SOURCE.json') == pin['source_sha256']
        actual = inv(pkg); actual.pop('MANIFEST.json'); assert actual == read(pkg / 'MANIFEST.json')
        for name, expected in read(pkg / 'SOURCE.json')['packages'].items(): assert inv(research / name) == expected['files'], name
integrity(); out.mkdir(parents=True); steps = []
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', E8_REPLAY_PHASES='1', PYTHON=sys.executable); env.pop('PYTHONOPTIMIZE', None)
if ' ' in str(research) or ' ' in str(out): env['BASH_ENV'] = str(ROOT / 'code/bash-env.sh')
if 'BOOST_INCLUDE' not in env and Path('/opt/homebrew/include/boost').exists(): env['BOOST_INCLUDE'] = '/opt/homebrew/include'
def run(name, path, *args):
    log = out / (name + '.log'); start = time.monotonic(); print('RUN', name, flush=True)
    with log.open('w') as f: q = subprocess.run([sys.executable, '-B', str(path), *map(str, args)], env=env, stdout=f, stderr=subprocess.STDOUT)
    if q.returncode: raise RuntimeError((name, q.returncode, log.read_text()[-5000:]))
    steps.append(dict(name=name, seconds=round(time.monotonic() - start, 2), log_sha256=sha(log))); print('PASS', name, flush=True)
try:
    run('full-complex458', research / 'e8-complex-adapted-kernel/verify.py', out / 'complex458')
    run('full-bit-r715', research / 'e8-r715-eleven-stage-whole/verify.py', out / 'bitr715')
    run('exact-composition', ROOT / 'compose.py', out / 'RESULT.json', '--research-root', research, '--complex-output', out / 'complex458', '--bit-output', out / 'bitr715')
    result = read(out / 'RESULT.json')
    for k, v in read(ROOT / 'EXPECTED.json').items(): assert result[k] == v, (k, result[k], v)
    assert result['mode'] == 'FRESH_FULL_SUPPLIERS'; integrity()
    receipt = dict(status='PASS_FULL_R715_PAID_COMPLEX_COMPOSITION', python=sys.version.split()[0], kappa=result['kappa'], kappa_decimal=result['kappa_decimal'],
                   gain_over_pr460_percent=result['gain_over_pr460_percent'], manifest_sha256=sha(ROOT / 'MANIFEST.json'), source_sha256=sha(ROOT / 'SOURCE.json'), steps=steps,
                   complex_receipt_sha256=sha(out / 'complex458/RECEIPT.json'), bit_receipt_sha256=sha(out / 'bitr715/RECEIPT.json'))
    (out / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n'); print(json.dumps(receipt, indent=2))
except BaseException as e:
    (out / 'FAILURE.json').write_text(json.dumps(dict(error=repr(e), steps=steps), indent=2) + '\n'); raise
