"""Negative controls for xcheck.py: each single mutation of an honest word must be rejected.

Usage: controls.py FULL-WORD.json.gz CLAIM-JSON
"""
import copy, gzip, json, os, subprocess, sys, tempfile

word, claim = json.loads(gzip.open(sys.argv[1]).read()), sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
b_add = next(i for i, g in enumerate(word['B']) if g[0] == 'add' and len(g[-1]) > 1)


def negate(w):
    w['A'][0][3] *= -1


def drop_b(w):
    del w['B'][b_add]


def shrink_frame(w):
    w['B'][b_add][-1] = w['B'][b_add][-1][1:]


def late_tail(w):
    w['early_cleanup'].pop(0)


def entrance(w):  # a target reads an entering helper's start value
    w['B'].insert(0, ['add', w['report']['v'], int(next(iter(w['start_extra']))), 1, 1, list(range(1, 1 << w['report']['h']))])


def wrong_claim(w):
    return json.dumps(dict(json.loads(claim), profile={**json.loads(claim)['profile'], '1': json.loads(claim)['profile']['1'] + 1}))


results = {}
for mutate in (negate, drop_b, shrink_frame, late_tail, entrance, wrong_claim):
    w = copy.deepcopy(word)
    c = mutate(w) or claim
    with tempfile.NamedTemporaryFile(suffix='.json.gz', delete=False) as f:
        f.write(gzip.compress(json.dumps(w).encode()))
    r = subprocess.run([sys.executable, os.path.join(here, 'xcheck.py'), f.name, c], capture_output=True, text=True)
    os.unlink(f.name)
    last = (r.stdout + r.stderr).strip().splitlines()[-1]
    results[mutate.__name__] = last
    print(f'{mutate.__name__:13} {last}')
    assert last.startswith('FAIL'), mutate.__name__
print('PASS all', len(results), 'controls rejected')
