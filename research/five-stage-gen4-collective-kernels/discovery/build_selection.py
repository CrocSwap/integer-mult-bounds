"""Freeze kernel-selection.json: the K best twin pairs of discovery/twin-census.json (phi order),
bound to the fresh gen4 parity-fused transcript (input hashes). Usage: python3 -B build_selection.py K"""
import sys,json,importlib.util,hashlib,math,collections
from fractions import Fraction as Q
from math import lcm
from pathlib import Path
HERE=Path(__file__).resolve().parent;PKG=HERE.parent;K=int(sys.argv[1])
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ctx=load('g_prepare',PKG/'prepare.py').prepare()
producer=load('g_phys',PKG/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'])
producer=load('g_parity',PKG/'parity_transform.py').run(producer)
parity=producer['records']
producer=load('g_descent',PKG/'descent_transform.py').run(producer)
W,C=producer['W'],producer['C'];v=W.v;n=2*v+len(producer['context']['regs'])
pairs=json.loads((HERE/'twin-census.json').read_text())['pairs']
phi=lambda r:0 if r<=0 else r*math.log(120/r)
gain=lambda p:phi(p['dima']-1)-phi(p['dima'])+phi(1)+phi(p['dimb']-1)-phi(p['dimb'])
pairs.sort(key=lambda p:(gain(p),p['a']));pairs=pairs[:K]
sel=[];delta=collections.Counter()
for p in pairs:
    if p['line'][0]=='e_i-e_j':
        u=[0]*24;u[p['line'][1]]=1;u[p['line'][2]]=-1
    else:
        q=[Q(x)for x in p['line'][1]];d=lcm(*(x.denominator for x in q));u=[int(x*d)for x in q]
    f=W.register([u]);assert C.dimf[f]==1 and C.nondeg(f)and C.sub(f,p['first_a'])and C.sub(f,p['first_b'])
    rec=parity;cut=p['cut'];assert rec[6*cut]==1 and rec[6*cut+2]in(p['a'],p['b'])
    sel.append(dict(a=p['a'],b=p['b'],cut_read=[rec[6*cut+1],rec[6*cut+2],rec[6*cut+3]],rank=1,basis=[u],first_frame_dims=[p['dima'],p['dimb']],phi_gain=round(gain(p),6)))
    ra,rb=p['dima'],p['dimb'];delta[ra]-=1;delta[ra-1]+=1;delta[1]+=1;delta[rb]-=1;delta[rb-1]+=1
delta.pop(0,None);delta={str(k):c for k,c in sorted(delta.items())if c}
out=dict(status='GEN4_TWIN_PAIR_SELECTION_PER_PAIR_CUTS',provenance='discovery/census.py on the fresh gen4 parity-fused transcript, bound after #279 descent retiming; pairs ordered by phi-gain, K chosen by discovery/pick_k.py on the validated ledger model',
    n=n,v=v,input_raw_sha256=hashlib.sha256(producer['records'].tobytes()).hexdigest(),input_scalar_sha256=producer['physical']['scalar_projection_sha256'],
    selected_pairs=len(sel),expected_local_delta=delta,pairs=sel)
(PKG/'kernel-selection.json').write_text(json.dumps(out,indent=1)+'\n')
print('wrote',len(sel),'pairs; delta',delta)
