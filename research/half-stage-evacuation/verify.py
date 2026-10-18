#!/usr/bin/env python3
"""Direct literal owner and exact-moment check; full cold admission is separate.

Apache-2.0. PR2530 by zxv supplies immutable words and the original checker.
New work with substantial OpenAI Codex assistance; no independent human review.
"""
import argparse
import copy
import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE.parent/'source-partner-lifetimes'
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(HERE.parent/'source-partner-residual-exchanges'))
from build import need, prepare, read, write
from price import price


def verify(work):
    if not __debug__:
        raise RuntimeError('Assertions are required')
    for name, digest in read(HERE/'INPUTS.json').items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, 'input pin '+name)
    work.mkdir(parents=True, exist_ok=False)
    p = prepare(work/'source')
    for a, b in [('PROVIDERS.json', 'new/BORROW-PROVIDERS.json'),
                 ('base.json.gz', 'new/borrow/words/BORROW-WORD-43base.json.gz'),
                 ('extra.json.gz', 'new/borrow/words/BORROW-WORD-43extra.json.gz')]:
        shutil.copy2(HERE/'vendor/pr2588'/a, p/b)
    from generate import mod
    import contextlib, io
    al = mod('bounded_swapped_local', p/'new/borrow/audit_local.py')
    for tag in ['base','extra']:
        with contextlib.redirect_stdout(io.StringIO()):
            al.run(p/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz',work/f'LOCAL-{tag}.json')
    fillpath = p/'new/borrow-fill/FILL.json.gz'
    shutil.copy2(HERE/'evidence/SWAP-CANDIDATE-FILL.json.gz', fillpath)
    shutil.copy2(HERE/'evidence/CANDIDATE-ORDER.json', p/'new/borrow-fill/ORDER.json')
    def reconstruct(out):
        return subprocess.run([sys.executable, '-B', str(p/'reconstruct.py'), '--out', str(out)],
                              capture_output=True, text=True)
    r = reconstruct(work/'owners')
    need(r.returncode == 0, r.stderr)
    h = read(work/'owners/PROFILE.json')
    need(h == read(HERE/'evidence/SWAP-PROFILE.json'), 'literal paid profile')
    need(sum(int(rank)*n for rank, n in h.items()) == 4816512, 'rank mass')
    endpoint = price(h)
    need(endpoint == read(HERE/'evidence/SWAP-MOMENT.json')['endpoint'], 'exact moment enclosure')
    from packing_cap import calculate
    need(calculate() == read(HERE/'evidence/PACKING-CAP.json'), 'exact packing cap and realized fraction')
    claim = read(HERE/'CLAIM.json')
    ledger = read(HERE/'evidence/OUTER-LEDGER.json')
    full = read(HERE/'evidence/FULL-RESULT.json')
    row = ledger['rows']['struct_boundary_radix_union']
    k, previous = Q(claim['kappa']), Q(read(SOURCE/'CLAIM.json')['kappa'])
    need(previous < k < Q(endpoint['lower']), 'strict improved outer claim below certified endpoint')
    need(k == Q(row['kappa']['rational']) == Q(full['kappa']), 'claim, ledger and full receipt binding')
    need(Q(claim['gain_over_pr2530']) == k-previous, 'exact improvement over PR2530')
    leader = Q(read(HERE/'vendor/pr2588/OUTER-CLAIM.json')['kappa'])
    need(k > leader and Q(claim['gain_over_pr2588']) == k-leader, 'strict improvement over pinned PR2588')
    need(ledger['profile'] == full['global_profile'] == h and ledger['W'] == 66304, 'outer literal profile binding')
    need(len(row['strict_checks']) == 63 and all(Q(v['rational']) > 0 for v in row['strict_checks'].values()), '63 positive exact outer inequalities')
    need(full['status'] == 'PASS_HALF_STAGE_EVACUATION_COMPLETE_FINITE_ADMISSION_AND_OUTER' and all(s['exit_code'] == 0 for s in full['stages']), 'recorded complete replay status')
    need(full['candidate_fill_sha256'] == hashlib.sha256((HERE/'evidence/SWAP-CANDIDATE-FILL.json.gz').read_bytes()).hexdigest(), 'full receipt literal witness binding')
    fill = read(fillpath)
    sp = importlib.util.spec_from_file_location('literal_windows', p/'vendor/build_parent.py')
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    windows = mod.actual_windows(mod.read(p/'inputs/GLOBAL-TEMPLATE.json.gz'),
                                 read(p/'new/borrow-fill/ORDER.json'))[0]
    rejected = []
    for label in ['missing-role', 'outside-window', 'duplicate-family']:
        bad = copy.deepcopy(fill)
        if label == 'missing-role':
            bad['rows'].pop()
        elif label == 'outside-window':
            row = bad['rows'][0]
            allowed = windows[f'{row[2]},{row[3]}'][1]
            row[0] = next(t for t in range(666) if t not in allowed)
        else:
            first, second = next((a, b) for a, b in zip(bad['rows'], bad['rows'][1:]) if a[0] == b[0])
            second[2:] = first[2:]
        write(fillpath, bad)
        result = reconstruct(work/('bad-'+label))
        need(result.returncode != 0 and 'AssertionError' in result.stderr, 'mutation accepted '+label)
        rejected.append(dict(control=label, reason=result.stderr[-400:]))
    write(fillpath, fill)
    result = dict(status='PASS_LITERAL_OWNERS_AND_EXACT_MOMENT', roles=len(fill['rows']),
                  profile=h, endpoint=endpoint, rejected=rejected, recorded_outer_kappa=str(k),
                  scope='Strict owner windows, widths, capacities, distinct families, exact moment and arithmetic bindings to committed outer/full receipts. Repeating native, global and outer admission requires full_replay.py.')
    write(work/'RESULT.json', result)
    print(result['status'], flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path,
                    help='fresh directory for retained diagnostics; default: disposable temporary workspace')
    args = ap.parse_args(argv)
    if args.work is not None:
        if args.work.exists() or args.work.is_symlink():
            ap.error('--work must name a fresh path; existing data will not be overwritten')
        verify(args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='half-stage-evacuation-') as directory:
            verify(Path(directory) / 'check')


if __name__ == '__main__':
    main()
