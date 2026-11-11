"""Independent set-valued audit of 523 exact terminal source libraries."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
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
assert pins == r['pins']


def read(path):
    data = (root/path).read_bytes()
    assert sha256(data).hexdigest() == pins[path]
    return data


def value(ids):
    return frozenset(ids)


w = json.loads(gzip.decompress(read('research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz')))
marks = [x['event'] for x in json.loads(read('pr7209/RESULT.json'))['bank_maps']]
prior = json.loads(read('round22/RESULT.json'))['scope'][1]['endpoint_consistency']
singletons = value(b['banks'][0] for b in prior['blocks'] if len(b['banks']) == 1)
assert singletons == value(r['quiet_singleton_mark_positions'])
n = w['public']
roles = w['start']+[None]*w['owned_fields']
current = [value([i]) for i in range(n)] + [value([])]*w['owned_fields']
history = defaultdict(dict)
terminal = {}
contact = defaultdict(list)


def seen(i, cut, op):
    if current[i]:
        history[roles[i]].setdefault((i,current[i]), (cut,op))


for i in range(n):
    seen(i,0,'initial')
for t, row in enumerate(w['program']):
    op, i = row[:2]
    contact[i].append(t)
    if op == 'ADD':
        j, f = row[2:]
        assert roles[i] == roles[j] == f
        contact[j].append(t)
        current[i] ^= current[j]
    elif op == 'SWAP':
        j = row[2]
        contact[j].append(t)
        roles[i], roles[j] = roles[j], roles[i]
        current[i], current[j] = current[j], current[i]
        seen(j,t+1,op)
    elif op == 'MOVE':
        f, g = row[2:]
        assert roles[i] == f and f != 1
        if g == 1:
            peers = {(current[j], ('live',f,t,j)) for j, fj in enumerate(roles)
                     if j != i and fj == f and current[j]}
            terminal[t] = (i,f,current[i],peers)
        roles[i] = g
    elif op == 'INIT':
        assert roles[i] is None and row[2] != 1
        roles[i] = row[2]
        current[i] = value([])
    else:
        assert op == 'CLEAR' and roles[i] == row[2] != 1
        roles[i] = None
        current[i] = value([])
    seen(i,t+1,op)
assert roles == w['final']+[None]*w['owned_fields']
assert current == [value([i,i-111]) if 111 <= i < 222 else value([i]) for i in range(n)] + [value([])]*w['owned_fields']


def eliminate(vectors):
    basis = {}
    for v in vectors:
        while v:
            low = min(v)
            if low not in basis:
                basis[low] = v
                break
            v ^= basis[low]
    return basis


def mod(basis, vector):
    for low, v in sorted(basis.items()):
        if low in vector:
            vector ^= v
    return vector


orders = sorted(set(terminal)-set(marks)) + marks
assert len(orders) == 545 and r['completed_donor_slots'] == 523
span_w = eliminate(v for f, v in zip(roles,current) if f == 1)
assert len(span_w) == 545
basis = {}
for i, event in enumerate(orders):
    vec, label = terminal[event][2], value([i])
    assert not mod(span_w, vec)
    while vec:
        pivot = min(vec)
        if pivot in basis:
            row, idx = basis[pivot]
            vec ^= row
            label ^= idx
        else:
            basis[pivot] = (vec,label)
            break
    assert vec
assert len(basis) == 545
ordered = sorted(basis.items())


def coordinates(vector):
    support = value([])
    for pivot, (vec, label) in ordered:
        if pivot in vector:
            vector ^= vec
            support ^= label
    return vector, support


def intersect(raw):
    exterior, inside = {}, []
    for v in eliminate(raw).values():
        k, _ = coordinates(v)
        while k:
            p = min(k)
            if p not in exterior:
                exterior[p] = (k,v)
                break
            a,b = exterior[p]
            k ^= a
            v ^= b
        if not k:
            out, x = coordinates(v)
            assert not out
            inside.append(x)
    return eliminate(inside)


def agree(actual, reported):
    given = eliminate(value(v) for v in reported)
    assert len(actual) == len(given) and all(not mod(given,v) for v in actual.values())


summary = []
for mode, s in enumerate(r['scopes']):
    all_proj = []
    all_sing = []
    actual_nonzero = []
    for i, d in enumerate(s['donors']):
        t = orders[i]
        owner,f,old,live = terminal[t]
        assert (d['event'],d['owner'],d['source_chart'],value(d['old_row'])) == (t,owner,f,old)
        valid = set(live)
        k = contact[owner].index(t)
        end = contact[owner][k+1] if k+1 < len(contact[owner]) else len(w['program'])
        if mode:
            for (j,v),(cut,op) in history[f].items():
                if cut <= end and (j,v) != (owner,old):
                    valid.add((v,('cached',f,cut,j,op)))
        assert d['horizon'] == (end if mode else t)
        witnessed = {(value(x['row']), tuple(x['witness'])) for x in d['source_rows']}
        raw = {v for v,_ in valid}
        assert witnessed <= valid and {v for v,_ in witnessed} == raw
        space = intersect(raw)
        assert len(space) == d['V_intersection_W_rank']
        agree(space,d['full_terminal_basis'])
        projected = eliminate(value(j-523 for j in v if j >= 523) for v in space.values())
        singleton = eliminate(v & singletons for v in projected.values())
        agree(projected,d['projection_marked_basis'])
        agree(singleton,d['projection_singleton_basis'])
        if projected:
            actual_nonzero.append(t)
        all_proj.append(projected)
        all_sing.append(singleton)
    assert len(s['donors']) == 523
    assert actual_nonzero == ([21445] if mode else [])
    upper = []
    for key, spaces in (('marked_quotient_rank',all_proj),('isolated_singleton_projection_rank',all_sing)):
        cert = s[key]
        count = len(cert['assignments'])
        assert len({a['donor_index'] for a in cert['assignments']}) == count
        assert len(eliminate(value(a['projection']) for a in cert['assignments'])) == count
        for a in cert['assignments']:
            assert a['event'] == orders[a['donor_index']]
            assert not mod(spaces[a['donor_index']],value(a['projection']))
        j = cert['rado_restricted']
        rank = len(eliminate(v for i in j for v in spaces[i].values()))
        assert 523-len(j)+rank == count == cert['rank']
        assert rank == cert['rado_restricted_rank']
        assert count == sum(bool(v) for v in spaces)
        upper.append(count)
    assert s['raw_stock_upper'] == min(22,12+sum(upper))
    summary.append({'scope':s['scope'],'slots':523,'nonzero_mark_donors':actual_nonzero,
                    'quotient_and_singleton_ranks':upper,'endpoint_and_release_stock_upper':s['raw_stock_upper']})
charges = r['one_separately_charged_split_per_additional_donor']
assert len(charges) == 5
for h, entry in enumerate(charges):
    assert entry['new_charged_donors'] == h
    assert entry['stock_upper'] == min(22,14+2*h)
    assert entry['also_bounds_all_larger_h'] == (h == 4)
    for v in entry['directed'].values():
        c0,c1 = map(Fraction,v['minimum_split_tariff_interval'])
        a0,a1 = map(Fraction,v['unbilled_net_upper_interval'])
        q0,q1 = map(Fraction,v['net_upper_after_split_lower_tariff'])
        assert 0 < c0 <= c1 and (q0,q1) == (a0-h*c1,a1-h*c0)
        assert q1 < 0
print(json.dumps({'status':'PASS','independent_source_and_rank_audit':summary,
                  'charged_tariff_fraction_reconstructions':10},sort_keys=True))
