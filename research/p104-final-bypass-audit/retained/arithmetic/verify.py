"""Check one P104 repair with exact rational operators and a bank separator."""
from fractions import Fraction as F
from graphlib import TopologicalSorter
from hashlib import sha1, sha256
from math import gcd, lcm
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import time

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sources():
    pins = read(HERE / 'SOURCE-PINS.json')['sources']
    for pin in pins:
        raw = (HERE / pin['retained']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source Git blob')
    return len(pins)


def unpack(graph):
    return ({k: (a, b) for k, a, b in graph['moves']},
            {k: {j: F(q) for j, q in row} for k, row in graph['forms']})


def span(frame):
    values = {0}
    for x in frame:
        need(x not in values, 'independent chart basis')
        values |= {x ^ y for y in values}
    return values


def order(graph, moves, rows):
    first = graph['first_output']
    charts = {~i: c for i, c in enumerate(graph['initial'])}
    need(set(rows) == set(moves) | set(range(first, first+len(graph['initial']))), 'complete row inventory')
    sequence = list(TopologicalSorter({k: [j for j in row if j >= 0] for k, row in sorted(rows.items())}).static_order())
    spans = [span(f) for f in graph['frames']]
    for k in sequence:
        chart = moves[k][0] if k in moves else graph['final'][k-first]
        need(all(j in charts and charts[j] == chart for j in rows[k]), 'available same-chart donor')
        if k in moves:
            a, b = moves[k]
            need(spans[a] < spans[b] or spans[b] < spans[a], 'strictly nested paid charts')
            charts[k] = b
    return sequence


def edit(moves, rows, delta):
    moves, rows = moves.copy(), rows.copy()
    for k, before, after in delta['moves']:
        need(moves.get(k) == (None if before is None else tuple(before)), 'paid preimage')
        if after is None:
            del moves[k]
        else:
            moves[k] = tuple(after)
    for k, existed, kept, changes in delta['forms']:
        need((k in rows) == existed, 'row presence')
        row = rows.get(k, {}).copy()
        for j, old, new in changes:
            need(row.get(j) == (None if old is None else F(old)), 'coefficient preimage')
            if new is None:
                del row[j]
            else:
                row[j] = F(new)
        if kept:
            rows[k] = row
        else:
            need(not row, 'empty retired row')
            del rows[k]
    return moves, rows


def expand(graph, moves, rows):
    values = {~i: (1, {i: 1}) for i in range(len(graph['initial']))}
    products = 0
    for k in order(graph, moves, rows):
        parts = [(values[j], q) for j, q in rows[k].items()]
        den = lcm(*(d*q.denominator for (d, _), q in parts))
        total = {}
        for (d, vector), q in parts:
            factor = den//(d*q.denominator)*q.numerator
            for j, v in vector.items():
                total[j] = total.get(j, 0)+factor*v
                products += 1
        total = {j: v for j, v in total.items() if v}
        common = gcd(den, *total.values())
        values[k] = (den//common, {j: v//common for j, v in total.items()})
    return values, products


def vector(value):
    den, row = value
    return {j: F(v, den) for j, v in row.items()}


def add(row, other, factor):
    for j, v in other.items():
        new = row.get(j, 0)+factor*v
        if new:
            row[j] = new
        else:
            row.pop(j, None)
    return row


def reduced(row, basis):
    row = row.copy()
    while row:
        j = max(row)
        if j not in basis:
            break
        add(row, basis[j], -row[j])
    return row


def dot(a, b):
    return sum(v*b.get(j, 0) for j, v in a.items())


def terms(row):
    return [[j, str(v)] for j, v in sorted(row.items()) if v]


def scalar(graph, moves, rows, input_values, pulses=()):
    values = {~i: input_values.get(i, F(0)) for i in range(len(graph['initial']))}
    for k in order(graph, moves, rows):
        values[k] = sum(q*values[j] for j, q in rows[k].items())+dict(pulses).get(k, F(0))
    return values


def run():
    pin_count = sources()
    retained = HERE / 'retained'
    prior = load('prior7767', retained/'pr7767/verify.py')
    bridge = load('bridge7774', retained/'pr7774/rebase_pr7767.py')
    raw = read(retained/'donor/GRAPH.json.gz')
    need(sha256(encoded(raw)).hexdigest() == prior.PARENT_GRAPH, 'published parent graph')
    before = prior.apply_stack(prior.apply_delta(raw, read(retained/'pr7767/DELTA.json')), read(retained/'pr7767/STACK-DELTA.json'))
    before = json.loads(encoded(before))
    patch = read(retained/'pr7774/PR7767-TO-JOINT.json.gz')
    graph = bridge.apply(before, patch)
    need(bridge.apply(graph, patch, reverse=True) == before, 'literal reverse bridge')
    journal = read(retained/'pr7774/PAID-EDITS.json')
    need(sha256(encoded(graph)).hexdigest() == journal['inherited_graph'], 'exact edit input')
    moves0, rows0 = unpack(graph)
    first_edit = journal['ordered_edits'][0]
    need(first_edit['start'] == 99771, 'named first edit')
    moves, rows = edit(moves0, rows0, first_edit['delta'])
    old, old_products = expand(graph, moves0, rows0)
    new, new_products = expand(graph, moves, rows)
    first, count = graph['first_output'], len(graph['initial'])
    need(count == 1264 and all(old[first+i] == new[first+i] for i in range(count)), 'all input/output rational coefficients')
    x = vector(new[53])
    need(x == vector(old[99771]), 'repair is the removed source value')
    need(vector(new[96048]) == add(vector(old[96048]), x, -4), 'exact slope-four source substitution')
    quotient = add({j:-v for j,v in vector(new[103626]).items()}, vector(new[103736]), F(2))
    difference = add(vector(old[104247]), quotient, F(-1))
    need(difference == {j:2*v for j,v in x.items()}, 'terminal quotient leaves exactly twice the repair')
    need(all(53 not in rows[k] for k in moves), 'repair has terminal-only readers')
    a = scalar(graph, moves, rows, {}, [(96048, F(1))])
    b = scalar(graph, moves, rows, {}, [(53, F(1))])
    need((a[first+186], b[first+186], a[first+38], b[first+38]) == (F(-1,4), 0, 2, 16), 'nonzero residual minor')
    need(x[25] == F(-1,2), 'source witness input')
    # Every retained bank is allowed, even if it is too late for a specific terminal.
    bank = sorted([k for k, (_, c) in moves.items() if c == 127 and k != 53]
                  + [~i for i, c in enumerate(graph['initial']) if c == 127])
    basis = {}
    for k in bank:
        row = reduced(vector(new[k]), basis)
        if row:
            pivot = max(row)
            basis[pivot] = {j: v/row[pivot] for j, v in row.items()}
    residual = reduced(x, basis)
    need(residual and len(bank) == len(basis) == 907, 'missing repair direction')
    free = max(residual)
    witness = {free: F(1)}
    for pivot in sorted(basis):
        value = -dot(basis[pivot], witness)
        if value:
            witness[pivot] = value
    need(all(dot(vector(new[k]), witness) == 0 for k in bank), 'separator annihilates every receiving bank')
    separated = dot(x, witness)
    need(separated == residual[free] and separated, 'separator detects required value')
    # Direct runs check the symbolic law, including an attempted compensation at output 38.
    controls = []
    for slope, repair in [(3, 1), (4, 0), (0, F(1,2)), (F(7,3), F(-2,5)), (4, 1)]:
        changed = rows.copy()
        changed[96048] = add(rows[96048].copy(), rows[53], F(4)-slope)
        changed[53] = {j: repair*q for j, q in rows[53].items() if repair*q}
        got = scalar(graph, moves, changed, {25: F(1)})
        expected = scalar(graph, moves0, rows0, {25: F(1)})
        errors = {}
        for i in range(count):
            actual = got[first+i]-expected[first+i]
            need(actual == x[25]*((4-slope)*a[first+i]+(repair-1)*b[first+i]), 'two-parameter residual law')
            if actual:
                errors[i] = actual
        need(bool(errors) == ((slope, repair) != (4, 1)), 'mutation outcome')
        controls.append(dict(slope=str(slope), repair=str(repair), changed_outputs=len(errors), output186=str(errors.get(186,0)), output38=str(errors.get(38,0))))
    bad_moves = moves.copy();bad_moves[53] = (859,127)
    try:
        order(graph, bad_moves, rows)
    except ValueError:
        pass
    else:
        raise ValueError('wrong source chart accepted')
    # Follow the original identifiers through all later edits before checking the final witness.
    final_moves, final_rows = moves, rows
    for entry in journal['ordered_edits'][1:]:
        final_moves, final_rows = edit(final_moves, final_rows, entry['delta'])
    sequence = order(graph, final_moves, final_rows)
    final_graph = dict(graph, moves=[[k,*v] for k,v in sorted(final_moves.items())],
                       forms=[[k,terms(row)] for k,row in sorted(final_rows.items())], schedule=sequence)
    need(sha256(encoded(final_graph)).hexdigest() == journal['final_graph'], 'complete submitted graph')
    final_values = scalar(graph, final_moves, final_rows, {1:F(1)})
    lost = -final_rows[first+19][53]*final_values[53]
    need(lost == -8, 'independent final-word omission witness')
    omissions = read(retained/'pr7774/evidence/omissions.json')
    need(next(w for w in omissions['witnesses'] if w['paid_slot']==53) == dict(input_role=1,output_role=19,paid_slot=53,omitted_minus_qualified_coefficient='-8'), 'source omission agreement')
    rank = lambda pair: abs(len(graph['frames'][pair[0]])-len(graph['frames'][pair[1]]))
    need([rank(moves0[k]) for k in (99771,104247)] == [2,3] and rank(moves[53]) == 5, 'paid replacement ranks')
    return dict(source_files=pin_count,source_graph=journal['inherited_graph'],final_graph=journal['final_graph'],
                owners=count,before_paid=len(moves0),after_paid=len(moves),changed_forms=len(first_edit['delta']['forms']),
                exact_scalar_products=old_products+new_products,repair=terms(x),
                terminal_responses=[[i,str(a[first+i]),str(b[first+i])] for i in range(count) if a[first+i] or b[first+i]],
                separator=dict(bank_count=len(bank),rank=len(basis),bank_ids=bank,free_coordinate=free,input=terms(witness),repair_value=str(separated)),
                controls=controls,final_omission=dict(input_role=1,output_role=19,coefficient=str(lost)),wrong_chart_rejected=True,terminal_quotient_repair_coefficient='2')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    result = run()
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(result == read(HERE/'RESULT.json'), 'deposited certificate')
    print('PASS_P104_FIRST_RELAY_REPAIR', result['owners'], 'owners', len(result['terminal_responses']), 'affected outputs', result['separator']['bank_count'], 'separated banks', round(time.monotonic()-start,2), 'seconds')
