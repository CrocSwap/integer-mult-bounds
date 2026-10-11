"""Exact shared-donor entrance-gauge constructor; frozen source, explicit selection.
This extends the prior119 sufficient response construction. No global kappa claim.
Preserve the prior constructor/local notices and upstream attribution.
"""
from pathlib import Path
import argparse,json,copy,hashlib,math,sys
from hashlib import sha256
from collections import Counter,defaultdict
from fractions import Fraction as Q
sys.dont_write_bytecode=True
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('base_candidate',type=Path)
parser.add_argument('output',type=Path)
parser.add_argument('selection',type=Path)
parser.add_argument('--reference119',type=Path,required=True)
args=parser.parse_args()
basepath=args.base_candidate
out=args.output;assert not out.exists(),'Output directory must be fresh'
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

pins={str(p):digest(p) for p in [args.base_candidate,args.selection,args.reference119,Path(__file__)]}
w=json.loads(args.selection.read_text());b=json.loads(basepath.read_text());assert digest(basepath)=='a4e42aa1663f5ad0da48cee6fe8514b205e43cf6e791b80674dbc7506a098a32'
first=first_frames(b);old=replay(b);c=copy.deepcopy(b)
pivs=set();dons=set();sel=[];bydim=Counter();donorcharts=defaultdict(list)
for plan in w['plans']:
 e=plan['basis'];dim=len(e);assert dim==plan['ed']; assert len({u for u in range(1,512) if inside([u],e)})==(1<<dim)-1
 f=next((i for i,a in enumerate(c['frames']) if len(a)==dim and inside(e,a)),len(c['frames']))
 if f==len(c['frames']):c['frames'].append(e)
 actual=set()
 for entry in plan['pivots']:
  p=entry['pivot'];assert p not in pivs and b['start'][p]==0;pivs.add(p);bydim[dim]+=1
  assert inside(e,b['frames'][first[p]])
  cm={int(r):Q(str(x)).limit_denominator(10000) for r,x in entry['coefficients'].items()}
  for d,a in cm.items():
   assert a and a.denominator in (1,2) and b['start'][d]==0 and inside(e,b['frames'][first[d]])
   actual.add(d);dons.add(d);donorcharts[d].append(e)
  for t in range(b['v'],2*b['v']): assert old[t].get(p,Q(0))+sum(a*old[t].get(d,Q(0)) for d,a in cm.items())==0,(p,t)
  sel.append((f,p,cm));c['start'][p]=f
 assert actual==set(plan['donors'])
assert not pivs&dons
for d,es in donorcharts.items():
 for a in es:
  for b2 in es:assert inside(a,b2) or inside(b2,a)
unit=[]
for f,p,cm in sel:
 for d,a in cm.items():unit += [['in',f,d,[[p,1 if a>0 else -1,a.denominator]]] for _ in range(abs(a.numerator))]
unit.sort(key=lambda g:(len(c['frames'][g[1]]),g[1],g[2],g[3]))
c['A']=unit+b['A'];c['ext']=sorted([p,f] for f,p,_ in sel);trans=rehist_and_audit(c)
new=replay(c);assert all(p not in new[t] for p in pivs for t in range(c['v'],2*c['v']))
for t in range(len(new)):
 wanted=dict(old[t])
 for _,p,cm in sel:
  z=wanted.get(p,Q(0))+sum(a*old[t].get(d,Q(0)) for d,a in cm.items())
  if z:wanted[p]=z
  else:wanted.pop(p,None)
 assert wanted==new[t],t
old119=json.loads(args.reference119.read_text())
assert digest(args.reference119)=='3b78069c4ce032e95f757a2f79fa5557af923c947430b638b0eb6859be659866'
h0=histogram(old119);h1=histogram(c);delta={r:h1[r]-h0[r] for r in sorted(h1.keys()|h0.keys()) if h1[r]!=h0[r]}
a=.001013310887459710
chi=lambda r:r*math.expm1(a*math.log(73/r)) if r else 0
for g in unit:
 d=g[2];assert any(old[t].get(d,Q(0)) for t in range(c['v'],2*c['v'])), 'omission control needs nonzero donor response'
assert pins=={p:digest(Path(p)) for p in pins}, 'Input source changed during reconstruction'
receipt={'status':'EXACT_RESPONSE_AND_NESTED_FRAME_PASS','source_sha256':digest(basepath),'selection_sha256':digest(args.selection),'reference119_sha256':digest(args.reference119),'constructor_sha256':digest(Path(__file__)),'pivots':len(pivs),'donors':len(dons),'unit_gates':len(unit),'entrance_dimensions':dict(bydim),'dimension_sum':sum(d*n for d,n in bydim.items()),'local_delta_vs119':delta,'local_chi_gain_float_vs119':-sum(n*chi(r) for r,n in delta.items()),'source_columns_checked':len(new),'transitions':trans,'all_unit_omission_controls':len(unit),'input_source_hashes':pins,'residual_inventory_per_T8':{9-dim:8*count for dim,count in bydim.items()}|{9:8*(c['R']-len(pivs))},'scope':'Exact finite algebra and charged local histogram only; full scalar,phase,banks,invoice,outer admission remains required','kappa_claimed':False}
out.mkdir();blob=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(out/'candidate.json').write_bytes(blob);receipt['candidate_sha256']=hashlib.sha256(blob).hexdigest();(out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2));(out/'selection.json').write_text(json.dumps(w,indent=2));(out/'K.json').write_text(json.dumps({'columns':c['R'],'rows':[[[r-2*c['v'],a.numerator,a.denominator] for r,a in sorted(new[c['v']+t].items()) if r>=2*c['v']] for t in range(c['v'])]},separators=(',',':')));print(json.dumps(receipt))



