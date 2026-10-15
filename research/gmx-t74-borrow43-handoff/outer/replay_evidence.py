"""Replays PR1673's supplier-independent exact evidence checks (unmodified scripts) in a temporary copy and compares each regenerated
artifact with the vendored one, exactly as PR1673's verify.py fast mode does (same CHECKS list, same normalisation; the two
supplier-specific frontier_fusion checks are replaced by check_ledger.py / independent_check.py of this package).
"""
import concurrent.futures, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
SRC = HERE.parent / 'vendor/pr1673/capped-phase-fusion'
CHECKS = re.findall(r"\('([^']+\.py)','([^']+\.json)'\)", (SRC / 'verify.py').read_text(encoding='utf-8'))
CHECKS = [c for c in CHECKS if not c[0].startswith('frontier_fusion/')]
assert len(CHECKS) == 19, len(CHECKS)


def norm(x):
    if isinstance(x, dict):
        return {k: norm(v) for k, v in x.items() if k not in {'seconds', 'native_required_output'}}
    if isinstance(x, list):
        return [norm(v) for v in x]
    return x


def main():
    assert __debug__
    import sympy
    assert sympy.__version__ == '1.14.0', 'PR1673 evidence is registered against sympy==1.14.0, found ' + sympy.__version__
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0', PYTHONINTMAXSTRDIGITS='500000')
    env.pop('PYTHONOPTIMIZE', None)
    with tempfile.TemporaryDirectory(prefix='phase-fusion-replay-') as td:
        root = Path(td) / 'p'
        shutil.copytree(SRC, root, ignore=shutil.ignore_patterns('__pycache__'))
        for script, artifact in CHECKS:
            (root / artifact).unlink()

        def run(c):
            script, artifact = c
            cp = subprocess.run([sys.executable, '-B', str(root / script)], cwd=root, env=env, capture_output=True, text=True, timeout=300)
            if cp.returncode:
                raise SystemExit(script + ' failed\n' + cp.stdout[-2000:] + cp.stderr[-2000:])
            if norm(json.loads((root / artifact).read_text(encoding='utf-8'))) != norm(json.loads((SRC / artifact).read_text(encoding='utf-8'))):
                raise SystemExit('proof-relevant JSON changed: ' + artifact)
            return script
        with concurrent.futures.ThreadPoolExecutor(3) as ex:
            done = list(ex.map(run, CHECKS))
    print('PASS_EXACT_REPLAY', len(done))


main()
