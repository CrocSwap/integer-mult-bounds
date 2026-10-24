"""Check an exact three-carrier decoder with repeated monotone read caps."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib, json, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]/'source/research/nodal-pair-async/inputs/work/odd-stages'))
import clifford_exact as c
h = 6
ports = [sum(1 << (2*i+((t >> i) & 1)) for i in range(3)) for t in range(8)]
sources = [1 << (2*i) for i in range(3)]
FULL = tuple(1 << i for i in range(h-1, -1, -1))

def basis(rows):
    rows = list(rows)
    out = {}
    for x in rows:
        for j in sorted(out, reverse=True):
            if x >> j & 1:
                x ^= out[j]
        if x:
            j = x.bit_length()-1
            for k in out:
                if out[k] >> j & 1:
                    out[k] ^= x
            out[j] = x
    return tuple(out[j] for j in sorted(out, reverse=True))

def inside(a, b):
    return basis(a+b) == b

cur = [(u,) for u in sources]+[()] * 8
rows = [{i: Q(1)} for i in range(11)]
events, transitions = [], set()
paid = Counter()
schedule = [(0, 1), (0, 3), (1, 2), (1, 6), (2, 4), (2, 5),
            (0, 5), (0, 7), (1, 3), (1, 7), (2, 6), (2, 7)]
pending = [{t for t in range(8) if t >> i & 1} for i in range(3)]

def climb(stream, out):
    old = cur[stream]
    assert inside(old, out)
    r = len(out)-len(old)
    if r:
        events.append(['child', stream, list(old), list(out), r])
        transitions.add((old, out))
        paid[r] += 1
    cur[stream] = out

for i, t in schedule:
    assert t in pending[i]
    out = basis(cur[i]+cur[3+t])
    assert all((u&ports[q]).bit_count() % 2 == 0 for u in out for q in pending[i])
    climb(i, out)
    climb(3+t, out)
    assert cur[i] == cur[3+t]
    events.append(['add', 3+t, i, 1, 1, list(out)])
    for col, q in rows[i].items():
        rows[3+t][col] = rows[3+t].get(col, Q(0))+q
    pending[i].remove(t)
assert not any(pending)
for t in range(8):
    expected = {3+t: Q(1)}
    expected.update({i: Q(1) for i in range(3) if t >> i & 1})
    assert rows[3+t] == expected
for i in range(3):
    assert rows[i] == {i: Q(1)}

for i in range(3):
    climb(i, FULL)
for t in range(8):
    cap = basis(c.nullspace((ports[t],), h))
    climb(3+t, cap)

recipes = []
for old, new in sorted(transitions):
    op = c.canonical_frame(h, old).adjoint().then(c.canonical_frame(h, new))
    record, emitted = c.lower_child(op)
    assert record['rank'] == len(new)-len(old)
    assert emitted.tab == op.tab and emitted.zero_state() == op.zero_state()
    recipes.append(dict(old=list(old), new=list(new), recipe=record))
word = dict(h=h, source_ports=sources, target_ports=ports, schedule=schedule,
            events=events, final_frames=[list(F) for F in cur], recipes=recipes)
raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
HERE.joinpath('GROWING-CYCLE-WORD.json').write_bytes(raw)
receipt = dict(status='PASS_EXACT_GROWING_CAP_DECODER', sources=3, targets=8,
    scalar_columns=11, reads=12, scalar_carriers=3,
    initial_frames='Three source lines and eight zero target frames.',
    source_values_unchanged=True, all_target_rows_exact=True,
    monotone_source_and_target_frames=True,
    future_target_compatibility_checked_at_every_read=True,
    paid_profile=dict(sorted(paid.items())), paid_rank_mass=sum(r*n for r, n in paid.items()),
    full_phase_lowerings=len(recipes), global_phase_and_pauli_columns=True,
    word_sha256=hashlib.sha256(raw).hexdigest(),
    scope='A finite decoder mechanism. It is not an identity controller, parent supplier or kappa bound.')
HERE.joinpath('GROWING-CYCLE-RESULT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
