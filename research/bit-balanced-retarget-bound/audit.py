"""Independent exact certificate audit for balanced fixed-clock BIT reassignments."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path

WORD = 'research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz'
INVOICE = 'research/paired-query-only-bit/EFREE-RESULT.json'
TARGET = '10018846261809/2500000000000000'
TRIAL = '1002040748181/250000000000000'
GRID = 10**40


def authenticated(root):
    data, pins = {}, {}
    for line in (Path(__file__).with_name('SOURCES.tsv')).read_text().splitlines():
        name, digest, _ = line.split('\t')
        path = Path(name)
        if path.is_absolute() or '..' in path.parts or name in pins:
            raise ValueError(f'ambiguous input path {name}')
        raw = (root/path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'changed input {name}')
        pins[name], data[name] = digest, raw
    return pins, data


def bits(support):
    assert len(support) == len(set(support))
    return sum(1 << i for i in support)


def add_binary(basis, v):
    while v:
        p = v.bit_length() - 1
        if p not in basis:
            basis[p] = v
            return
        v ^= basis[p]


def basis_binary(rows):
    basis = {}
    for row in rows:
        add_binary(basis, row)
    return basis


def same_binary_space(left, right):
    return len(left) == len(right) == len(basis_binary([*left.values(), *right.values()]))


def normal(frame):
    """An exact rank-seven null vector using forward elimination/back substitution."""
    a = [list(map(Q, row)) for row in frame]
    pivots = []
    for col in range(8):
        i = len(pivots)
        hit = next((j for j in range(i, 7) if a[j][col]), None)
        if hit is None:
            continue
        a[i], a[hit] = a[hit], a[i]
        for j in range(i + 1, 7):
            m = a[j][col] / a[i][col]
            if m:
                a[j] = [x - m*y for x, y in zip(a[j], a[i], strict=True)]
        pivots.append(col)
    assert len(pivots) == 7
    free, = set(range(8)) - set(pivots)
    v = [Q(0)]*8
    v[free] = Q(1)
    for i, col in reversed(list(enumerate(pivots))):
        v[col] = -sum(a[i][j]*v[j] for j in range(col+1, 8))/a[i][col]
    assert any(v)
    assert contains([list(map(Q, row)) for row in frame], v)
    return v


def contains(frame, v):
    return not any(sum(x*y for x,y in zip(row, v, strict=True)) for row in frame)


def closure(edges):
    """Reachability via reflexive transitive matrix elimination."""
    nodes = sorted({x for _, a, b in edges for x in (a,b)})
    reach = {(x,x) for x in nodes} | {(a,b) for _,a,b in edges}
    for k in nodes:
        reach.update((i,j) for i in nodes if (i,k) in reach for j in nodes if (k,j) in reach)
    return [e for e in edges if (e[2],e[1]) in reach]


def trace(word, selected=()):
    selected = set(selected)
    n = word['public']
    frames = word['start'] + [None]*word['owned_fields']
    lanes = [(frame, (1 << i) if i < n else 0, frozenset(), None) for i,frame in enumerate(frames)]
    moves, touched, sources = {}, defaultdict(list), {}
    for t,(op,i,*args) in enumerate(word['program']):
        f,r,markers,birth = lanes[i]
        touched[i].append(t)
        if op == 'MOVE':
            assert f == args[0] and f != 1
            g = args[1]
            moves[t] = (i,f,g,r)
            if t in selected:
                peers = [(v, origins) for j,(h,v,origins,_) in enumerate(lanes) if j != i and h == f]
                old = [r, *(v for v,_ in peers)]
                prior = {e for _,origins in peers for e in origins}
                extension = [v for e in prior for v in sources[e].values()]
                sources[t] = basis_binary(old + extension)
                markers = markers | {t}
            lanes[i] = (g,r,markers,t if g == 1 else birth)
        elif op == 'ADD':
            j,declared = args
            assert f == lanes[j][0] == declared
            lanes[i] = (f,r ^ lanes[j][1],markers ^ lanes[j][2],birth)
            touched[j].append(t)
        elif op == 'SWAP':
            j, = args
            lanes[i],lanes[j] = lanes[j],lanes[i]
            touched[j].append(t)
        else:
            assert op in ('INIT','CLEAR') and birth is None
            g, = args
            assert f == (None if op == 'INIT' else g)
            lanes[i] = (g if op == 'INIT' else None, 0, frozenset(), None)
    expected = [1 << i if i < n else 0 for i in range(len(lanes))]
    for i in range(111):
        expected[111+i] ^= 1 << i
    assert [x[0] for x in lanes] == word['final'] + [None]*word['owned_fields']
    assert [x[1] for x in lanes] == expected
    final_lineage = {birth: i for i,(f,_,_,birth) in enumerate(lanes) if f == 1}
    terminal = {t:r for t,(_,_,g,r) in moves.items() if g == 1}
    assert len(moves) == 2871 and len(terminal) == len(final_lineage) == 545
    assert set(terminal) == set(final_lineage)
    assert same_binary_space(basis_binary(terminal.values()), basis_binary(lanes[i][1] for i in final_lineage.values()))
    return moves,touched,sources,final_lineage


def enclose(x):
    return Q(x*GRID//1, GRID), Q(-(-x*GRID//1),GRID)


@cache
def atanh(x):
    terms = 45
    low = sum((2*x**(2*i+1)/(2*i+1) for i in range(terms)), Q(0))
    rest = 2*x**(2*terms+1)/((2*terms+1)*(1-x*x))
    return low,low+rest


@cache
def power(r,k):
    assert r >= 1 and 0 < k < 1
    shift = r.bit_length()-1
    binary = 1 << shift
    lo,hi = atanh(Q(r-binary,r+binary))
    l2,h2 = atanh(Q(1,3))
    left = enclose(k*(lo+shift*l2))[0]
    right = enclose(k*(hi+shift*h2))[1]
    assert 0 <= left <= right < 1

    def polynomial(x, n):
        value, term = Q(1), Q(1)
        for i in range(1,n+1):
            term *= -x/i
            value += term
        return value

    return enclose(r*polynomial(right,25))[0],enclose(r*polynomial(left,24))[1]


def price_shape(word,dims,invoice,moves,lineage):
    signed = Counter({int(r):v for r,v in invoice['targets'].items()})
    signed.subtract({int(r):v for r,v in invoice['paid'].items()})
    helpers = Counter(dims[word['final'][j]]-dims[word['start'][j]] for j in range(222,word['public']))
    assert helpers == {2:1,4:25,6:1,8:410} == {int(r):v for r,v in invoice['native_helpers'].items()}
    major = Counter(dims[moves[t][1]] for t,i in lineage.items() if i>=222 and word['start'][i]==0)
    assert major == {2:2,4:2,6:138,7:268}
    assert len(invoice['native_instances']) == 36

    def evaluate(k, h, stock):
        coeff = signed.copy()
        constant = 0
        for r,n in helpers.items():
            if r < 8:
                coeff[r] -= 36*n
                constant += 36*n*r
        for r,n in major.items():
            if r < 7:
                quantity = n + (stock if r==6 else 0)
                coeff[r+1] += 36*quantity
                coeff[8-r] += 36*quantity
                coeff[8] -= 36*quantity
                constant -= 36*quantity
        coeff[2] += 36*h
        constant -= 72*h
        lo = hi = Q(constant)
        for r,n in coeff.items():
            ends = [n*x for x in power(r,k)]
            lo += min(ends)
            hi += max(ends)
        return lo,hi

    return evaluate


def audit(root,receipt):
    pins,data = authenticated(root)
    assert receipt['status'] == 'PASS_COMPLETE_STOCK_UPPER'
    assert receipt['pins'] == pins and receipt['new_sites'] == 0
    assert 1 <= receipt['seconds_cap'] <= 480
    word = json.loads(gzip.decompress(data[WORD]))
    invoice = json.loads(data[INVOICE])
    old = json.loads(data['round25/RESULT.json'])
    incidence = json.loads(data['round24/RESULT.json'])
    original = json.loads(data['round22/RESULT.json'])
    marked = [p for p in incidence['incidence'] if p['marked']]
    assert [p['event'] for p in marked] == [p['event'] for p in json.loads(data['pr7209/RESULT.json'])['bank_maps']]
    singleton = [b['banks'][0] for b in original['scope'][1]['endpoint_consistency']['blocks'] if len(b['banks']) == 1]
    assert len(singleton) == 10 and len(marked) == 22
    dims = {int(f):raw['dim'] for f,raw in word['frames'].items()}
    frames = {int(f):[list(map(Q,row)) for row in raw['B']] for f,raw in word['frames'].items()}
    normals = {f:normal(frames[f]) for f,r in dims.items() if r == 7}
    moves,touched,_,lineage = trace(word)
    destinations, deadlines = {}, {}
    for j in singleton:
        row = marked[j]
        t = row['event']
        i,f,g,v = moves[t]
        assert g==1 and (i,f,bits(row['old_row'])) == (row['owner'],row['source_chart'],v)
        successor = next((e for e in touched[i] if e > t),len(word['program']))
        assert successor == row['quiet_window'][1]
        deadlines[j] = (t,successor)
        charts = {h for h,z in normals.items() if contains(frames[f],z)}
        assert charts == set(row['compatible_literal_charts'])
        assert not charts & destinations.keys()
        destinations.update({h:j for h in charts})
    assert len(destinations)==20
    carriers = [(e,i,f,g,v) for e,(i,f,g,v) in moves.items()
                if g in destinations and v and e<deadlines[destinations[g]][1]]
    old_carriers = {c['event']:c for c in old['carriers']}
    assert len(carriers)==60 and {c[0] for c in carriers}==old_carriers.keys()
    _,_,sources,_ = trace(word,old_carriers)
    old_sources = {d['event']:basis_binary(bits(row) for row in d['rows'])
                   for d in old['scopes'][-1]['carrier_source_bases']}
    assert sources.keys()==old_sources.keys()
    edges, nonnested = [], []
    for e,i,f,g,v in carriers:
        c = old_carriers[e]
        assert (i,f,g,v) == (c['owner'],c['source_chart'],c['target_chart'],bits(c['old_row']))
        assert same_binary_space(sources[e],old_sources[e])
        if dims[f]>=7 or not contains(frames[f],normals[g]):
            nonnested.append(e)
        else:
            edges.extend((e,g,h) for h in sorted(destinations)
                         if h != g and contains(frames[f],normals[h]))
    cycles = closure(edges)
    # Every feasible nonempty reassignment here exchanges a matched pair
    # within one bank. Each paid event and destination occurs only once.
    assert len(edges)==len(cycles)==20
    assert len({e for e,_,_ in edges})==20 and len({h for _,_,h in edges})==20
    arcs = {(g,h) for _,g,h in edges}
    assert all((h,g) in arcs and destinations[g]==destinations[h] for g,h in arcs)
    assert len({frozenset((g,h)) for g,h in arcs})==10
    marked_rows = [moves[row['event']][3] for row in marked]
    unmarked_rows = [moves[e][3] for e in lineage if e not in {p['event'] for p in marked}]
    w = basis_binary(unmarked_rows + marked_rows)
    assert len(unmarked_rows) == 523 and len(w) == 545
    shape = price_shape(word,dims,invoice,moves,lineage)
    result = {}
    for mode,(name,claim) in enumerate(zip(('literal','quiet'),receipt['clocks'],strict=True)):
        assert claim['clock']==name and claim['source_target_pairs']==60*20
        assert claim['nonnested_untested']==nonnested
        timely = [e for e in edges if e[0]+1<=deadlines[destinations[e[2]]][mode]]
        usable = [e for e in cycles if e[0]+1<=deadlines[destinations[e[2]]][mode]]
        for key,actual in [('all_balancing_incidences',edges),('cyclic_balancing_incidences',cycles),
                           ('timely_incidences',timely),('timely_cyclic_incidences',usable)]:
            assert claim[key]==[list(e) for e in actual], key
        expanded = 0
        for j,receiver in zip(singleton,claim['recipients'],strict=True):
            moves_in = [e for e,_,h in usable if destinations[h]==j]
            assert receiver['singleton']==j and receiver['timely_retarget_slots']==moves_in
            s = [bits(a['row']) for a in original['scope'][1]['banks'][j]['source_witnesses']]
            s += [v for e in moves_in for v in sources[e].values()]
            u = unmarked_rows + [marked_rows[j]]
            su = basis_binary(s+u)
            d = 21 - len(basis_binary(s+list(w.values()))) + len(su)
            q = receiver['new_quotient_basis']
            assert d == len(q) == len(basis_binary(map(bits,q)))
            for row in q:
                lift = 0
                for k in row:
                    assert 0<=k<len(marked) and k!=j
                    lift ^= marked_rows[k]
                assert len(basis_binary([*su.values(),lift]))==len(su)
            expanded += d>0
        assert expanded==claim['expanded_singleton_upper']
        bounds = {}
        for key in (TARGET,TRIAL):
            k = Q(key)
            assert shape(k,3,22)[1]<0
            claims = claim['price'][key]
            assert len(claims)==3
            for h,price in enumerate(claims):
                stock = min(22,12+expanded+2*(1+h))
                lo,hi = shape(k,h,stock)
                plo,phi = map(Q,price['net_upper'])
                assert (price['h'],price['stock_upper'])==(h,stock)
                assert lo<=plo<=phi<=hi
                first = next((n for n in range(23) if shape(k,h,n)[0]>0),None)
                assert all(shape(k,h,n)[1]<0 for n in range(23 if first is None else first))
                required = first-12-2*(1+h) if first is not None else None
                assert price['required_expansions']==required
                assert price['affordable_upper'] == (hi>=0 and first is not None)
                assert hi < 0 or lo > 0
                bounds.setdefault(key,[]).append({'h':h,'stock_upper':stock,'signed_upper':str(hi),
                                                  'needed_singleton_expansions':required})
        result[name] = {'geometry_arcs':len(edges),'cyclic_arcs':len(cycles),'timely_arcs':len(timely),
                        'timely_cyclic_arcs':len(usable),'excluded_nonnested_slots':len(nonnested),
                        'expanded_singleton_upper':expanded,'directed_price':bounds}
    return {'status':'PASS_INDEPENDENT_GEOMETRY_CHRONOLOGY_QUOTIENT_AND_PRICE',
            'input_pins':pins,'source_target_pairs':1200,'arrivals':len(lineage),
            'disjoint_exchange_blocks':10,'balanced_selections_including_identity':2**10,'modes':result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_root',type=Path)
    parser.add_argument('receipt',type=Path)
    args = parser.parse_args()
    late = [(1,1,2),(9,2,1),(3,2,3)]
    assert closure(late) == late[:2]
    assert [e for e in closure(late) if e[0]<5]==late[:1]
    print(json.dumps(audit(args.input_root,json.loads(args.receipt.read_bytes())),indent=2,sort_keys=True))


if __name__ == '__main__':
    assert __debug__
    main()
