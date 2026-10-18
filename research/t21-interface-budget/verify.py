# SPDX-License-Identifier: Apache-2.0
"""Cold replay of the T21 interface-budget note, with negative controls.

1. Extract only native/local/FULL-WORD.json.gz from the committed, hash-pinned
   selected T21 replay archive and check its content digest (PR869 U8 word).
2. Re-run the classification and the exact pricing; compare with RESULT-*.json.
3. Run six controls, each of which must be rejected for its stated reason.

Usage: python3 -B research/t21-interface-budget/verify.py --work NEW_EMPTY_DIR
Standard-library Python 3.10+, no network. Do not use -O.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT/'research/community-frontier890-audit/t21-replay.tar.gz'
ARCHIVE_SHA256 = '6dcd7040109174918fe25a631e349741e5d7fa1740e063e2bdd5ea77b054b6b4'
MEMBER = 'native/local/FULL-WORD.json.gz'


def require(ok, msg):
    if not ok:
        raise SystemExit('FAIL ' + msg)


def module(name):
    spec = importlib.util.spec_from_file_location('t21budget_' + name, HERE/(name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rejected(fn, needle):
    try:
        fn()
    except SystemExit as e:
        require(needle in str(e), f'control rejected for the wrong reason: {e} (wanted {needle!r})')
        return str(e)
    raise SystemExit(f'FAIL control accepted (wanted rejection: {needle})')


def canonical(x):
    return json.dumps(x, indent=1, sort_keys=True)


def main():
    require(__debug__, 'run without -O: the retained outer engine uses assertions')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    args = ap.parse_args()
    work = args.work.resolve()
    require(not work.exists() or not any(work.iterdir()), 'work directory must be new or empty')
    work.mkdir(parents=True, exist_ok=True)

    require(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == ARCHIVE_SHA256, 'selected T21 replay archive pin')
    with tarfile.open(ARCHIVE) as tar:
        data = tar.extractfile(tar.getmember(MEMBER)).read()
    word_path = work/'U8-FULL-WORD.json.gz'
    word_path.write_bytes(data)

    C = module('classify')
    word, digest = C.load_word(word_path)
    cls = json.loads(json.dumps(C.report(word, digest)))
    (work/'RESULT-CLASSIFICATION.json').write_text(canonical(cls))
    require(canonical(cls) == (HERE/'RESULT-CLASSIFICATION.json').read_text(), 'classification differs from committed result')
    print('classification', cls['status'], cls['mass_by_role'])

    sys.argv = ['budget.py', str(work/'RESULT-CLASSIFICATION.json'), str(work/'RESULT-BUDGET.json')]
    Bm = module('budget')
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        Bm.main()
    got = json.loads((work/'RESULT-BUDGET.json').read_text())
    require(canonical(got) == (HERE/'RESULT-BUDGET.json').read_text(), 'budget differs from committed result')
    print('budget', got['status'], 'kappa', got['base']['kappa_decimal'], 'cap', got['bit_cap']['kappa_decimal'])

    controls = {}
    # C1: a frame shrink inside B (non-monotone chain) must be rejected by the classifier.
    w = copy.deepcopy(word)
    i = next(i for i, g in enumerate(w['B']) if g[-1])
    w['B'][i] = w['B'][i][:-1] + [[]]
    controls['C1_shrunk_B_frame'] = rejected(lambda: C.report(w, digest), 'non-monotone frame')
    # C2: moving one low-end tail from early cleanup into the FULL cleanup must be rejected.
    w = copy.deepcopy(word)
    w['early_cleanup'] = w['early_cleanup'][1:]
    controls['C2_tail_moved_to_FULL_cleanup'] = rejected(lambda: C.report(w, digest), 'FULL cleanup touches a low end')
    # C3: moving a low-end helper's final frame to FULL changes widths/profile.
    w = copy.deepcopy(word)
    q = next(iter(w['helper_final']))
    del w['helper_final'][q]
    controls['C3_drop_low_end'] = rejected(lambda: C.report(w, digest), 'differs')
    # C4: the budget refuses a classification whose profile is not the claimed local profile.
    bad = json.loads(canonical(cls))
    bad['profile']['1'] -= 1
    (work/'BAD-CLASSIFICATION.json').write_text(canonical(bad))
    sys.argv = ['budget.py', str(work/'BAD-CLASSIFICATION.json'), str(work/'BAD-BUDGET.json')]
    controls['C4_wrong_profile_to_budget'] = rejected(lambda: Bm.main(), 'classified profile')
    # C5: the selected complex endpoint advanced by one grid tick is rejected by both engines.
    claim = json.loads((ROOT/'research/complex-t21-owners/data/CLAIM.json').read_text())
    H = Counter({int(r): 189*n for r, n in claim['local_profile'].items()})
    H.update({int(r): n for r, n in claim['idle'].items()})
    b1 = Q(claim['complex_lower']) + Bm.GRID
    require(Bm.above_root(H, 73, 18816, b1, False), 'C5 successor accepted')
    controls['C5_complex_successor'] = 'rejected: both engines prove moment(b+1e-24) > 1'
    # C6: one local unit per call does NOT reach the bit cap (headroom minimality).
    below = got['headroom']['delete_rank1_children_below'][0]
    require(below['units_per_call'] == 1, 'C6 data')
    L = Counter({int(r): n for r, n in claim['local_profile'].items()})
    L[1] -= 1
    H1 = Counter({r: 189*n for r, n in L.items()})
    H1.update({int(r): n for r, n in claim['idle'].items()})
    require(not Bm.below_root(H1, 73, 18816, Q(got['bit_cap']['complex_b_needed_above']), False), 'C6 one unit binds')
    controls['C6_one_unit_does_not_bind'] = 'rejected: with one rank-1 child fewer per call, b stays below c/(1-beta)'
    import subprocess
    run = subprocess.run([sys.executable, '-I', str(HERE/'independent.py'), str(word_path),
                          str(work/'RESULT-CLASSIFICATION.json'), str(work/'RESULT-BUDGET.json'),
                          str(ROOT/'research/complex-t21-owners/vendor/pr870/inputs/PR589-EXPECTED.json')],
                         capture_output=True, text=True)
    require(run.returncode == 0 and 'PASS_INDEPENDENT_FLOAT_CROSSCHECK' in run.stdout, 'independent cross-check: ' + run.stderr[-500:])
    print(run.stdout.strip().splitlines()[-1])
    (work/'CONTROLS.json').write_text(canonical(controls))
    for k, v in controls.items():
        print(k, '->', v)
    print('PASS_T21_INTERFACE_BUDGET_REPLAY')


if __name__ == '__main__':
    main()
