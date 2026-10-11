"""Rebuild PR #495's retimed kernel complex word from its frozen FULL-WORD with PR #495's own word-level scripts (vendored
byte for byte under vendor/complex, see SOURCE.json): exact arbitrary-input scalar and frame audit (scalar.py), both local
programs (programs.py), exact Clifford phase recipes for every used transition (phases.py), the paid two-sided residual
adapters of the entering helpers (adapters.py) and the independent local read-back (local_audit.py).
usage: build_word.py OUT        (writes OUT/split-centres/ and OUT/WORD.json)"""
from pathlib import Path
import gzip, hashlib, json, os, subprocess, sys
PKG = Path(__file__).resolve().parents[1]; VENDOR = PKG / 'vendor/complex'
out = Path(sys.argv[1]).resolve(); local = out / 'split-centres'; local.mkdir(parents=True)
src = PKG / 'data/complex/FULL-WORD.json.gz'; (local / 'FULL-WORD.json.gz').write_bytes(src.read_bytes())
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0'); env.pop('PYTHONOPTIMIZE', None); env.pop('CXOUT', None)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest(); done = []
for name, args in [('scalar', []), ('programs', []), ('phases', []), ('adapters', [local]), ('local_audit', [local])]:
    with (out / (name + '.log')).open('w') as f:
        subprocess.run([sys.executable, '-B', str(VENDOR / (name + '.py')), *map(str, args)], cwd=out, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)
    done.append(dict(step=name, log_sha256=sha(out / (name + '.log')))); print('PASS word', name, flush=True)
review = json.loads((local / 'LOCAL-REVIEW.json').read_text()); word = json.loads(gzip.decompress((local / 'CANONICAL-WORD.json.gz').read_bytes()))
assert review['status'] == 'PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION' and review['wrappers_per_call'] == 158
assert all(z['all_columns'] == 800 and z['helpers_restored_as_scalar_rows'] and z['private_centers_cleared'] for z in review['checks'].values())
widths = [word['h'] - len(word['frames'][word['start'][2 * word['v'] + h]]) for h in range(word['R'])]
res = dict(status='PASS_PR495_RETIMED_KERNEL_WORD_REBUILT', full_word_sha256=sha(src), canonical_word_sha256=review['canonical_word_sha256'],
           local_paid_profile={o: review['checks'][o]['paid_profile'] for o in ('forward', 'backward')},
           entering_helpers=sum(1 for w in widths if w < word['h']), widths=dict(sorted({str(w): widths.count(w) for w in set(widths)}.items())),
           mutations_rejected=review['mutations_rejected'], steps=done)
(out / 'WORD.json').write_text(json.dumps(res, indent=2) + '\n'); print(json.dumps({k: res[k] for k in ('status', 'entering_helpers', 'widths')}))
