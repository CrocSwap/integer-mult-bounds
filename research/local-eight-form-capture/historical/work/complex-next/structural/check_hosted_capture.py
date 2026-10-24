"""Check a local dirty capture and list its current physical owners."""
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
BASE = Path('/Users/aliromman/Documents/Codex/2026-10-10/hello-i-want-to-get-some/work/next-track/complex/pipeline')
WP = BASE/'retimed-4/split-centres/CANONICAL-WORD.json.gz'
TP = BASE/'retimed-4/complex/GLOBAL-TEMPLATE.json.gz'
w = json.loads(gzip.decompress(WP.read_bytes()))
t = json.loads(gzip.decompress(TP.read_bytes()))
n = 240 + w['R']

def add(rows, dst, src, q):
    for j, x in list(rows[src].items()):
        z = rows[dst].get(j, Q(0)) + q*x
        if z:
            rows[dst][j] = z
        else:
            rows[dst].pop(j, None)


def run(rows, operations):
    for e in operations:
        if e[0] == 'add':
            add(rows, e[1], e[2], Q(e[3], e[4]))
        else:
            rows[e[1]] = {j: x*Q(e[2], e[3]) for j, x in rows[e[1]].items()}


def identity():
    return [{i: Q(1)} for i in range(n)]


ops = w['precondition'] + w['compensation'] + w['A'] + w['B'] + w['cleanup']
rows = identity()
run(rows, ops)
assert all(rows[i] == {i: 1} for i in list(range(120)) + list(range(240, n)))
assert all({j: x for j, x in rows[i].items() if 120 <= j < 240} == {i: 1}
           for i in range(120, 240))
S = [{j: x for j, x in rows[120+i].items() if j < 120} for i in range(120)]
D = [{j: x for j, x in rows[120+i].items() if j >= 240} for i in range(120)]
assert all(w['start'][j] == 0 for row in D for j in row)
assert all(x.denominator & (x.denominator-1) == 0 for row in D for x in row.values())

# Each selected centre row is a dyadic form of the input X bank.
clean = [{i: Q(1)} if i < 240 else {} for i in range(n)]
run(clean, w['precondition'] + w['A'])
C = [clean[r] for r in w['centers'][:8]]
assert all(row and all(j < 120 for j in row) for row in C)
assert [[sum(C[i].get(j, 0)*C[k].get(j, 0) for j in range(120))
         for k in range(8)] for i in range(8)] == [[56*int(i == k) for k in range(8)] for i in range(8)]
code = [i for i, row in enumerate(S) if row]
for i in code:
    for j in range(120):
        gram = sum(row.get(i, 0)*row.get(j, 0) for row in C)/4
        assert Q(int(i == j)) - S[i].get(j, 0) == gram
helpers = list(range(758, 750, -1))
assert all(w['start'][r] == 0 and w['final'][r] == 1 for r in helpers)
assert all(w['start'][120+j] == 0 and w['final'][j] == 1 for row in C for j in row)

# Correct the omitted-centre word on all helper dirt, then retain eight forms.
state = identity()
for r, form in zip(helpers, C):
    for j, q in form.items():
        add(state, r, 120+j, q)
for i, row in enumerate(D):
    for j, q in row.items():
        add(state, 120+i, j, -q)
run(state, ops)
for r, form in zip(helpers, C):
    for j, q in form.items():
        add(state, r, j, Q(59, 4)*q)
expected = identity()
for i, row in enumerate(S):
    for j, q in row.items():
        add(expected, 120+i, j, q)
for r, form in zip(helpers, C):
    for j, q in form.items():
        expected[r][j] = Q(59, 4)*q
        expected[r][120+j] = q
assert state == expected

owners = []
for r in helpers:
    family, route = t['calls'][0]['owners'][r]
    assert 600 <= family <= 607 and route[:6] == [4, 2, 0, 9, 0, [1,2,3,4,5,6,7,8,9]]
    roles = []
    for call in t['calls']:
        if call['replica']:
            continue
        same = [(i, rr) for i, (f, rr) in enumerate(call['owners']) if f == family]
        assert len(same) <= 1
        roles += [dict(stage=call['stage'], register=i, route=rr) for i, rr in same]
    assert [z['stage'] for z in roles if z['stage'] <= 3] == [0, 2, 3]
    assert [z['route'][2] for z in roles if z['stage'] <= 3] == [0, 9, 18]
    owners.append(dict(family=family, capture_register=r, roles=roles))
result = dict(status='PASS_LOCAL_DIRTY_CAPTURE_AND_CURRENT_OWNER_INVENTORY',
              word_sha256=hashlib.sha256(WP.read_bytes()).hexdigest(),
              template_sha256=hashlib.sha256(TP.read_bytes()).hexdigest(),
              all_columns=n, retained_forms=8, centre_gram_multiplier=56, decoder_factor='C^t C / 4',
              dirty_correction_terms=sum(map(len,D)),
              local_source_and_target_map='X unchanged; Y += S X',
              local_helper_map='Selected h_i += C_i(59 X/4 + Y); all other helpers unchanged',
              owners=owners,
              scope='The local scalar map and current owner inventory are exact. The paid monomial adapters, endpoint decoder, scalar controller, owner restoration, and global cost are not verified.')
Path(__file__).with_name('hosted-capture-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'owners'}, indent=2))
