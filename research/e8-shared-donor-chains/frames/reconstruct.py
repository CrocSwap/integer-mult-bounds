"""Exact reconstruction of 119 disjoint helper entrance gauges; Python stdlib only."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import copy, json

SOURCE_SHA256 = "a4e42aa1663f5ad0da48cee6fe8514b205e43cf6e791b80674dbc7506a098a32"
SELECTION_SHA256 = "17b7959402af929e2b24d2d1b285f84d6cf51a90cd077eb0fca9b4f5f7bf1d76"
CANDIDATE_SHA256 = "3b78069c4ce032e95f757a2f79fa5557af923c947430b638b0eb6859be659866"
EXPECTED_DELTA = {1:169, 2:91, 3:-43, 4:15, 5:10, 6:-96, 7:-3}

def digest(p):
    return sha256(p.read_bytes()).hexdigest()

def inside(a, b):
    piv = {}
    for u in b:
        while u:
            k = u.bit_length()-1
            if k in piv: u ^= piv[k]
            else: piv[k] = u; break
    for u in a:
        while u:
            k = u.bit_length()-1
            if k not in piv: return False
            u ^= piv[k]
    return True

def gate_roles(g):
    return [g[2]] + ([r for r,_,_ in g[3]] + (g[4] if len(g)>4 else [])
                     if g[0]=='out' else [r for r,_,_ in g[3]])

def first_frames(c):
    result = {}
    for part in ('A', 'B'):
        for g in c[part]:
            for r in gate_roles(g):
                if r >= 2*c['v'] and g[1] and r not in result: result[r] = g[1]
    return result

def replay(c):
    """Complete rational affine-in-X operator, including the retained snapshot."""
    n, v = 2*c['v']+c['R'], c['v']
    rows = [{r:Q(1)} for r in range(n)]
    def add(t, values, coefficient):
        for k, a in list(values.items()):
            z = rows[t].get(k,Q(0)) + coefficient*a
            if z: rows[t][k] = z
            else: rows[t].pop(k,None)
    for part in ('A','B'):
        if part=='B':
            totals = {k:dict(rows[r]) for k,r,_ in c['ret']}
            for t, entry in enumerate(c['scat']['table']):
                for k,a,b in entry: add(v+t, totals[k], Q(a,b))
        for g in c[part]:
            assert g[0] in ('in','out')
            for r,a,b in g[3]:
                t,source = (g[2],r) if g[0]=='in' else (r,g[2])
                add(t, dict(rows[source]), Q(a,b))
    return rows

def rehist_and_audit(c):
    v, n = c['v'], 2*c['v']+c['R']
    current = c['start'][:]
    hist = {k:Counter() for k in ('x','y','s','c')}
    transitions = 0
    def visit(r,f):
        nonlocal transitions
        old = current[r]
        assert inside(c['frames'][old], c['frames'][f]), ('non-nested',r,old,f)
        if old != f:
            cls = 'x' if r<v else 'y' if r<2*v else 's'
            rank = len(c['frames'][f])-len(c['frames'][old])
            assert rank > 0
            hist[cls][rank] += 1; current[r] = f; transitions += 1
    for part in ('A','B'):
        if part=='B':
            for _,_,f in c['ret']: hist['c'][len(c['frames'][f])] += 1
        for g in c[part]:
            for r in gate_roles(g): visit(r,g[1])
    for r in range(n): visit(r,c['final'][r])
    c['blocks'] = {k:{str(r):count for r,count in sorted(h.items())} for k,h in hist.items()}
    c['N'] = sum(r*count for h in hist.values() for r,count in h.items())
    assert current == c['final']
    return transitions

def histogram(c):
    h = Counter()
    for block in c['blocks'].values(): h.update({int(r):n for r,n in block.items()})
    return h

def reconstruct(base, witness):
    assert witness['source_sha256'] == SOURCE_SHA256
    assert not base['ext']
    v, n = base['v'], 2*base['v']+base['R']
    old = replay(base); first = first_frames(base)
    result = copy.deepcopy(base)
    selection, used, frame_receipt = [], set(), []
    for plan in witness['plans']:
        basis = plan['basis']; dim = len(basis)
        assert dim == plan['ed'] and len(set(basis)) == dim
        assert len({u for u in range(1,1<<base['h']) if inside([u],basis)}) == (1<<dim)-1
        roles = set(plan['donors']) | {p['pivot'] for p in plan['pivots']}
        assert not roles & used
        used |= roles
        frame = next((i for i,f in enumerate(result['frames'])
                      if len(f)==dim and inside(basis,f)),len(result['frames']))
        assert frame == len(result['frames']), 'Expected genuinely new registered frame'
        result['frames'].append(basis)
        frame_receipt.append({'frame_id':frame,'basis':basis,'gauges':len(plan['pivots']),
                              'donors':len(plan['donors'])})
        actual_donors = set()
        for entry in plan['pivots']:
            p = entry['pivot']
            assert 2*v <= p < n and base['start'][p] == 0
            assert inside(basis, base['frames'][first[p]])
            coefficients = {int(r):Q(str(a)).limit_denominator(10000)
                            for r,a in entry['coefficients'].items()}
            assert p not in coefficients
            for r,a in coefficients.items():
                assert 2*v <= r < n and base['start'][r] == 0 and a
                assert a.denominator in (1,2)
                assert inside(basis, base['frames'][first[r]])
                actual_donors.add(r)
            for t in range(v,2*v):
                assert old[t].get(p,Q(0)) + sum(a*old[t].get(r,Q(0))
                          for r,a in coefficients.items()) == 0
            selection.append((frame,p,coefficients))
        assert actual_donors == set(plan['donors'])
    assert len(selection)==119 and len(frame_receipt)==26
    assert sum(len(result['frames'][f]) for f,_,_ in selection)==265
    assert len(used)==262
    pivots = {p for _,p,_ in selection}
    donors = {r for _,_,cm in selection for r in cm}
    assert not pivots & donors and len(donors)==143
    head = defaultdict(list)
    for frame,p,cm in selection:
        result['start'][p] = frame
        for donor,a in cm.items(): head[donor,frame].append([p,a.numerator,a.denominator])
    unit_gates = []
    for (donor,frame),terms in sorted(head.items()):
        for p,a,b in sorted(terms):
            unit_gates += [['in',frame,donor,[[p,1 if a>0 else -1,b]]] for _ in range(abs(a))]
    assert len(unit_gates)==240
    result['A'] = unit_gates + base['A']
    result['ext'] = sorted([p,frame] for frame,p,_ in selection)
    transitions = rehist_and_audit(result)
    new = replay(result)
    for t in range(n):
        wanted = dict(old[t])
        for _,p,cm in selection:
            z = wanted.get(p,Q(0)) + sum(a*old[t].get(r,Q(0)) for r,a in cm.items())
            if z: wanted[p] = z
            else: wanted.pop(p,None)
        assert wanted == new[t], ('M*S mismatch',t)
        assert all(new[t].get(x,Q(0)) == old[t].get(x,Q(0)) for x in range(2*v))
    assert all(p not in new[t] for p in pivots for t in range(v,2*v))
    bad = copy.deepcopy(result); bad['A'] = bad['A'][1:]; badrows = replay(bad)
    assert any(p in badrows[t] for p in pivots for t in range(v,2*v))
    before,after = histogram(base),histogram(result)
    delta = {r:after[r]-before[r] for r in before.keys()|after.keys() if after[r]!=before[r]}
    assert delta==EXPECTED_DELTA and sum(r*count for r,count in delta.items())==-265
    K = [[[r-2*v,a.numerator,a.denominator] for r,a in sorted(new[v+t].items()) if r>=2*v]
         for t in range(v)]
    return result,K,frame_receipt,transitions

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('base_candidate',type=Path)
    parser.add_argument('output_dir',type=Path)
    parser.add_argument('selection',type=Path,nargs='?',default=Path(__file__).with_name('selection.json'))
    args = parser.parse_args()
    assert digest(args.base_candidate)==SOURCE_SHA256, 'Source hash mismatch'
    assert digest(args.selection)==SELECTION_SHA256, 'Frozen selection hash mismatch'
    assert not args.output_dir.exists(), 'Output directory must be fresh'
    base = json.loads(args.base_candidate.read_text())
    result,K,frames,transitions = reconstruct(base,json.loads(args.selection.read_text()))
    blob = json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    assert sha256(blob).hexdigest()==CANDIDATE_SHA256, 'Frozen candidate hash mismatch'
    args.output_dir.mkdir(parents=True)
    (args.output_dir/'candidate.json').write_bytes(blob)
    (args.output_dir/'K.json').write_text(json.dumps({'columns':base['R'],'rows':K},separators=(',',':')))
    receipt = {'status':'PASS_EXACT_ENTRANCE_RESPONSE_ALGEBRA_AND_FRAME_PATHS',
               'source_sha256':SOURCE_SHA256,'selection_sha256':SELECTION_SHA256,
               'candidate_sha256':CANDIDATE_SHA256,'K_sha256':digest(args.output_dir/'K.json'),
               'columns':2*base['v']+base['R'],'gauges':119,'donors':143,'new_spaces':frames,
               'unit_entrance_gates':240,'coefficient_denominators':[1,2],
               'local_histogram_delta':EXPECTED_DELTA,'rank_mass_delta':-265,
               'transition_visits_including_final':transitions,
               'identity':'new raw operator = old raw operator * explicit entrance shear S',
               'negative_control':'omitting first entrance unit gate breaks a zero response',
               'scope':'Exact finite algebra, scalar coefficient bill and nested frame paths. '
                       'Separate scalar normalization, phases, banks, invoice and outer assembly required.',
               'kappa_claimed':False}
    (args.output_dir/'RECEIPT.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps(receipt))

if __name__=='__main__': main()
