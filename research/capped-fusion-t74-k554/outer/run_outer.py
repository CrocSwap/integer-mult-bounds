"""Regenerates the two ledger artifacts in a temporary copy (the package stays immutable), compares them with the committed ones and
replays PR1673's supplier-independent evidence. Usage: run_outer.py TMPDIR"""
import json, shutil, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent
tmp = Path(sys.argv[1]); (tmp / 'new').mkdir(parents=True)
shutil.copytree(P / 'outer', tmp / 'outer', ignore=shutil.ignore_patterns('__pycache__'))
shutil.copy2(P / 'new/SPEC.json', tmp / 'new/SPEC.json'); shutil.copy2(P / 'CLAIM.json', tmp / 'CLAIM.json')
for art in ('LEDGER.json', 'INDEPENDENT.json'):
    (tmp / 'outer' / art).unlink()
for script in ('check_ledger.py', 'independent_check.py'):
    subprocess.run([sys.executable, '-B', str(tmp / 'outer' / script)], check=True, stdout=subprocess.DEVNULL)
for art in ('LEDGER.json', 'INDEPENDENT.json'):
    if (tmp / 'outer' / art).read_bytes() != (P / 'outer' / art).read_bytes():
        raise SystemExit('regenerated artifact differs from committed: ' + art)
subprocess.run([sys.executable, '-B', str(P / 'outer/sched_test.py')], check=True)
subprocess.run([sys.executable, '-B', str(P / 'outer/sched_review.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, '-B', str(P / 'outer/struct_check.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, '-B', str(P / 'outer/check_gaugefree.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, '-B', str(P / 'outer/check_fine_padding.py'), '--out', str(tmp / 'fine-padding.json')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, '-B', str(P / 'outer/replay_evidence.py')], check=True)
print('PASS_OUTER')
