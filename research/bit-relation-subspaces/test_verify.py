"""Rejecting controls for verify.py.  Each mutation must raise SystemExit('FAIL...')."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402


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


def corrupted_record():
    word, records = V.load()
    i = next(k for k, r in enumerate(records) if r[0] == 0 and r[4] == 1)
    r = list(records[i]); r[4] = 2; records = records[:i] + [tuple(r)] + records[i + 1:]
    V.paid_jobs(word, records)


def dependent_part():
    word, records = V.load()
    _, legal = V.paid_jobs(word, records)
    rows, mass, per, elems = V.multiset(legal, {})
    ok, P = V.split(elems, 8)
    e, twin = next((a, b) for a in range(len(P.elems)) for b in range(a + 1, a + 8)
                   if b < len(P.elems) and P.elems[a] == P.elems[b])
    k, other = P.where[e], P.where[twin]
    P.members[other].remove(twin); P.members[k].append(twin)
    V.require(P.check(), 'every part independent and exact cover')


def tampered_result():
    stored = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    stored['quotient']['tight'] = 1
    V.require(stored['quotient']['tight'] == 0, 'stored RESULT.json equals the rebuild')


import complex as CX  # noqa: E402


def complex_missing_relation():
    rel = json.loads(CX.RELATIONS.read_text(encoding='utf-8'))
    word = json.loads(CX.gzip.decompress(CX.WORD.read_bytes()))
    A, B = CX.candidates(word)
    V0 = CX.Echelon()
    for row in rel['rows'][:-1]:
        V0.add({int(k): CX.Q(s) for k, s in row.items()})
    CX.require(len({t for t, _, v in B if not V0.reduce(v)}) == 8, 'V0 frees all eight centre jobs')


def complex_dependent_row():
    word = json.loads(CX.gzip.decompress(CX.WORD.read_bytes()))
    A, B = CX.candidates(word)
    rows = [v for _, _, v in A]
    rows.append({k: 2 * x for k, x in rows[0].items()})
    E = CX.Echelon()
    CX.require(all(E.add(v) for v in rows), 'remaining pure-cold climb rows are linearly independent modulo V0')


def complex_corrupted_rank():
    word = json.loads(CX.gzip.decompress(CX.WORD.read_bytes()))
    e = next(ev for ev in word['programs']['backward'] if ev[0] == 'climb')
    e[5] += 1
    CX.candidates(word)


for name, fn in [('drifted input hash', drift), ('corrupted MOVE rank in the source records', corrupted_record),
                 ('dependent part in the partition certificate', dependent_part), ('tampered RESULT.json', tampered_result),
                 ('complex: one #5383 relation dropped', complex_missing_relation),
                 ('complex: injected dependent row', complex_dependent_row),
                 ('complex: corrupted climb rank', complex_corrupted_rank)]:
    rejects(name, fn)
print('PASS_BIT_RELATION_SUBSPACES_CONTROLS')
