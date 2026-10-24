"""Rejecting controls for verify.py.  Each mutation must raise SystemExit('FAIL...')."""
import copy
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

WORD = json.loads(gzip.decompress(V.WORDS['eight_relation_body'].read_bytes()))
CE = V.clifford()


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
    row = next(r for r in rows['files'] if r['usage'] == 'input')
    data = (V.ROOT / row['path']).read_bytes()
    V.require(V.hashlib.sha256(data).hexdigest() == '0' * 64, 'input drift: ' + row['path'])


def odd_division():
    bad = copy.deepcopy(WORD)
    e = next(ev for ev in bad['programs']['backward'] if ev[0] == 'scalar' and ev[1][0] == 'add')
    e[1][4] = 3
    V.census(bad, 'backward', V.Ranks(CE, bad['canonical']))


def wrong_climb_rank():
    bad = copy.deepcopy(WORD)
    e = next(ev for ev in bad['programs']['forward'] if ev[0] == 'climb')
    e[5] += 1
    V.census(bad, 'forward', V.Ranks(CE, bad['canonical']))


def smaller_guard_claim():
    res = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))['eight_relation_body/backward']
    V.require(res['guard']['1'] <= 10, 'a ten-bit single-layer guard (false: the witness needs 11)')


def tampered_result():
    stored = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    stored['eight_relation_body/backward']['guard']['1'] = 10
    V.require(stored['eight_relation_body/backward']['guard']['1'] == 11, 'stored RESULT.json equals the rebuild')


for name, fn in [('drifted input hash', drift), ('an odd division in a scalar ADD', odd_division),
                 ('a corrupted climb rank', wrong_climb_rank), ('a smaller guard claim', smaller_guard_claim),
                 ('tampered RESULT.json', tampered_result)]:
    rejects(name, fn)
print('PASS_SELECTED_WORD_EXACT_GRID_CONTROLS')
