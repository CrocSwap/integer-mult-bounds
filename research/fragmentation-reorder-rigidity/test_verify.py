"""Rejecting controls for verify.py.  Each mutation must raise SystemExit('FAIL...')."""
import collections
import copy
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

word = json.loads(gzip.decompress((V.W3 / 'ACTUAL-WORD.json.gz').read_bytes()))
arith = json.loads((V.W3 / 'ARITHMETIC.json').read_text(encoding='utf-8'))


def rejects(name, fn):
    try:
        fn()
    except SystemExit as exc:
        if not str(exc).startswith('FAIL'):
            raise
        print('rejected:', name)
        return
    raise AssertionError('control accepted: ' + name)


def drift():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    rows['files'][0]['sha256'] = '0' * 64
    orig = V.pinned_inputs
    def patched():
        for row in rows['files']:
            if row['usage'] == 'input':
                data = (V.ROOT / row['path']).read_bytes()
                V.require(V.hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])
    patched()


def bad_rank():
    bad = copy.deepcopy(word)
    e = next(ev for ev in bad['programs']['forward'] if ev[0] == 'climb')
    e[5] += 1
    w = V.Word(bad, arith)
    prof = collections.Counter(w.climb_profile()); prof[8] += 8
    V.require(dict(prof) == w.N, 'climb profile + 8 centre jobs equals ARITHMETIC local_paid')


def frame_mismatch():
    bad = copy.deepcopy(word)
    e = next(ev for ev in bad['programs']['forward'] if ev[0] == 'scalar' and ev[1][0] == 'add' and ev[1][1][0] == 'L' and ev[1][2][0] == 'L' and ev[2] != 0)
    e[2] = 0
    V.Word(bad, arith)


def tampered_result():
    stored = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    stored['exact']['improving'] = 1
    V.require(stored['exact']['improving'] == 0, 'stored RESULT.json equals the rebuilt result')


def live_test():
    """ignoring the centre interface must produce feasible drops (otherwise the enumeration would be vacuous)."""
    w = V.Word(word, arith, pin_centre=False)
    LG = V.LevelGraph(w); LG.index_owners()
    res, feas, capped = V.drop_test(w, LG)
    V.require(res['improving'] >= 5, 'drop test finds improving drops without the centre interface')
    print('live: improving drops without the centre interface', res['improving'])


rejects('drifted input hash', drift)
rejects('corrupted climb rank', bad_rank)
rejects('contact frame mismatch', frame_mismatch)
rejects('tampered stored result', tampered_result)
live_test()
print('PASS_FRAGMENTATION_REORDER_RIGIDITY_CONTROLS')
