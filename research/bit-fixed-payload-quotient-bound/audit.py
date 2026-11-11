"""Independent set-valued literal source and endpoint proof audit."""
from collections import defaultdict
from hashlib import sha256
from itertools import product
import gzip
import json
from pathlib import Path
import sys


root, receipt = map(Path, sys.argv[1:])
r = json.loads(receipt.read_bytes())
pins = {}
for line in Path(__file__).with_name('SOURCES.tsv').read_text().splitlines():
    name, digest, _ = line.split('\t')
    assert name not in pins
    pins[name] = digest
assert r['pins'] == pins


def read(path):
    raw = (root/path).read_bytes()
    assert sha256(raw).hexdigest() == pins[path]
    return raw


word = json.loads(gzip.decompress(read('research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz')))
banks = json.loads(read('pr7209/RESULT.json'))['bank_maps']
N = word['public']
fields = word['start'] + [None]*word['owned_fields']
rows = [frozenset([i]) for i in range(N)] + [frozenset()]*word['owned_fields']
observations = defaultdict(dict)
paid = {}
touched = defaultdict(list)


def mark(owner, cut, op):
    if rows[owner]:
        observations[fields[owner]].setdefault((owner, rows[owner]), (cut, op))


for i in range(len(fields)):
    mark(i, 0, 'initial')
for t, item in enumerate(word['program']):
    op, i = item[:2]
    touched[i].append(t)
    if op == 'ADD':
        j, f = item[2:]
        assert fields[j] == fields[i] == f
        touched[j].append(t)
        rows[i] = rows[i] ^ rows[j]
    elif op == 'SWAP':
        j = item[2]
        touched[j].append(t)
        fields[i], fields[j] = fields[j], fields[i]
        rows[i], rows[j] = rows[j], rows[i]
        mark(j, t+1, op)
    elif op == 'MOVE':
        f, g = item[2:]
        assert fields[i] == f and f != 1
        paid[t] = i, f, g, rows[i]
        fields[i] = g
    elif op == 'INIT':
        assert fields[i] is None and item[2] != 1
        fields[i], rows[i] = item[2], frozenset()
    else:
        assert op == 'CLEAR' and fields[i] == item[2] != 1
        fields[i], rows[i] = None, frozenset()
    mark(i, t+1, op)
assert fields == word['final'] + [None]*word['owned_fields']
assert rows == [frozenset((i, i-111)) if 111 <= i < 222 else frozenset([i]) for i in range(N)] + [frozenset()]*word['owned_fields']


def bounds(e):
    calls = touched[paid[e][0]]
    j = calls.index(e)
    return calls[j-1]+1 if j else 0, calls[j+1] if j+1 < len(calls) else len(word['program'])


def row_basis(seq):
    b = {}
    for v in seq:
        while v:
            i = min(v)
            if i in b:
                v ^= b[i]
            else:
                b[i] = v
                break
    return b


def modulo(seq, v):
    for i in sorted(seq):
        if i in v:
            v ^= seq[i]
    return v


selected = {v['event']: i for i, v in enumerate(banks)}
u = row_basis(v for t, (_, _, f, v) in paid.items() if f == 1 and t not in selected)
w = row_basis(row for f, row in zip(fields, rows) if f == 1)
assert len(u) == 523 and len(w) == 545
remainders = [modulo(u, paid[t][3]) for t in selected]
assert len(row_basis(remainders)) == 22
assert all(not modulo(w, v) for v in u.values())
augmented = row_basis(v ^ frozenset([N+i]) for i, v in enumerate(remainders))


def coefficient(v):
    assert not modulo(w, v)
    remainder = modulo(augmented, modulo(u, v))
    assert all(i >= N for i in remainder)
    return frozenset(i-N for i in remainder)


summary = []
for mode, s in enumerate(r['scope']):
    subspaces = []
    for i, (b, bank_result) in enumerate(zip(banks, s['banks'], strict=True)):
        t = b['event']
        owner, chart, _, old = paid[t]
        assert old == frozenset(b['prefix_input']) and list(bounds(t)) == b['pivot_quiet_window']
        cut = bounds(t)[1] if mode else t
        valid = set()
        charts = {chart} | {v['literal_chart'] for v in b['variants'] if v['literal_chart'] is not None}
        for f in charts:
            for (j, v), (clock, op) in observations[f].items():
                if clock <= cut and (f,j,v) != (chart,owner,old):
                    valid.add((v, ('physical', f, clock, j, op)))
        cohort = {e for variant in b['variants'] for e in variant['virtual_bank_events']} - {t}
        for e in cohort:
            j, f, g, v = paid[e]
            clock = bounds(e)[0] if mode else e+1
            if clock <= cut:
                assert g == 1
                valid.add((v, ('virtual', f, clock, j, e)))
        raw = {v for v, _ in valid}
        witnessed = {(frozenset(x['row']), tuple(x['path'])) for x in bank_result['source_witnesses']}
        assert witnessed <= valid and {v for v, _ in witnessed} == raw
        assert cut == bank_result['deadline_cut'] and len(raw) == bank_result['observed_coefficient_rows']
        # For this exact scope, every raw source row itself belongs to W.
        assert all(not modulo(w, v) for v in raw)
        assert len(row_basis(raw)) == bank_result['source_rank'] == bank_result['source_intersection_terminal_rank']
        projected = row_basis(coefficient(v) for v in raw)
        reported = row_basis(frozenset(v) for v in bank_result['quotient_basis'])
        assert len(projected) == len(reported) == bank_result['projected_rank']
        assert all(not modulo(reported, v) for v in projected.values())
        subspaces.append(projected)
    chosen = s['independent_assignment']
    assert len({x['bank'] for x in chosen}) == len(chosen)
    for x in chosen:
        i = x['bank']
        v = frozenset(x['terminal_row'])
        q = frozenset(x['quotient'])
        assert not modulo(subspaces[i], q) and q == coefficient(v)
        assert not modulo(row_basis(frozenset(y['row']) for y in s['banks'][i]['source_witnesses']), v)
    assert len(row_basis(frozenset(x['quotient']) for x in chosen)) == len(chosen)
    J = s['rado_restricted_banks']
    rank = len(row_basis(v for i in J for v in subspaces[i].values()))
    assert len(chosen) == 22-len(J)+rank == s['compatible_stock_upper'] == s['rado_exact_upper']
    endpoint = s['endpoint_consistency']
    all_banks = set()
    independent = nonzero = total = 0
    for block in endpoint['blocks']:
        ids = block['banks']
        assert not all_banks.intersection(ids)
        all_banks.update(ids)
        options = []
        for i in ids:
            a = [frozenset()]
            for v in subspaces[i].values():
                assert v <= set(ids)
                a += [v ^ x for x in a]
            options.append(a)
        tested = feasible = best = best_count = 0
        for tup in product(*options):
            tested += 1
            if len(row_basis(d ^ frozenset([i]) for i, d in zip(ids, tup))) != len(ids):
                continue
            feasible += 1
            best = max(best, len(row_basis(tup)))
            best_count = max(best_count, sum(bool(d) for d in tup))
        witness = [frozenset(x) for x in block['rank_attaining_deltas']]
        assert all(d in a for d, a in zip(witness, options, strict=True))
        assert len(row_basis(d ^ frozenset([i]) for i, d in zip(ids, witness))) == len(ids)
        assert len(row_basis(witness)) == best == block['maximum_independent_return_directions']
        assert tested == block['tested_choices'] and feasible == block['endpoint_preserving_choices']
        assert best_count == block['maximum_nonzero_changes']
        independent += best
        nonzero += best_count
        total += tested
    assert all_banks == set(range(22))
    assert independent == endpoint['endpoint_preserving_independent_upper']
    assert nonzero == endpoint['endpoint_preserving_nonzero_upper']
    summary.append({'clock': s['scope'], 'source_libraries': len(subspaces), 'rado_stock': len(chosen),
                    'endpoint_block_choices': total, 'endpoint_independent_stock': independent,
                    'endpoint_nonzero_stock': nonzero})
print(json.dumps({'status': 'PASS', 'independent_sets': summary}, sort_keys=True))
