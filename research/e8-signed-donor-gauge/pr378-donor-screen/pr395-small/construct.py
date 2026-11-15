"""Signed prefix extension of Dugongue's PR390 construction.
Rohan Arun with OpenAI Codex assistance; Apache-2.0. Original notices retained.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import gzip,json,copy,hashlib,sys,importlib.util
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'e8-prefix-restoration'
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('upstream_pack',SOURCE/'code/bit-complex-output-shear-pack.py')
up=importlib.util.module_from_spec(spec);spec.loader.exec_module(up)
def transform(c,selection):
 v,R=c['v'],c['R'];n=2*v+R;nA=len(c['A']);d=copy.deepcopy(c);flat=[];version=[0]*n
 for gi,g in enumerate(c['A']+c['B']):
  for rr,a,b in g[3]:
   t,s=(rr,g[2]) if g[0]=='out' else (g[2],rr)
   assert not(v<=s<2*v)
   flat.append((gi,t,s,g[1],version[s],Q(a,b)));version[t]+=1
 used=set();destcuts={};addat=defaultdict(list);setups=[]
 for e in selection:
  i,j,cut,E=(e[k] for k in ('destination','donor_target','cut_group','recovery_frame'));lam=Q(e['coefficient'])
  assert lam in (Q(-1),Q(1));assert not({i,j}&used) and i!=j and v<=i,j<2*v;used|={i,j};assert c['start'][i]==c['start'][j]==0
  destcuts[i]=cut;setups.append(['in',0,i,[[j,-lam.numerator,lam.denominator]]]);rows={}
  for target,scale in [(i,Q(1)),(j,-lam)]:
   for gi,t,s,f,ve,q in flat:
    if gi<nA or gi>cut or t!=target:continue
    key=s,ve,f
    if key not in rows:rows[key]=[Q(0),gi]
    rows[key][0]+=scale*q
  jp=[x for x in flat if nA<=x[0]<=cut and x[1]==j];assert len(jp)>=e['prefix_target_deliveries'] and jp[-1][0]==cut and jp[-1][3]==E
  for (s,ve,f),(q,gi) in rows.items():
   if not q:continue
   assert q.denominator in (1,2,3,6)
   for _ in range(abs(q.numerator)):addat[gi].append(['in',f,i,[[s,1 if q>0 else -1,q.denominator]]])
  addat[cut].append(['in',E,i,[[j,lam.numerator,lam.denominator]]])
 B=list(setups)
 for bi,g in enumerate(c['B']):
  gi=nA+bi;g=copy.deepcopy(g)
  if g[0]=='out':g[3]=[z for z in g[3] if z[0] not in destcuts or gi>destcuts[z[0]]];B.append(g)
  elif g[2] in destcuts and gi<=destcuts[g[2]]:B.extend(['out',g[1],s,[],[]] for s,_,_ in g[3])
  else:B.append(g)
  B.extend(addat.get(gi,[]))
 d['B']=B;d['derived_from']=c['derived_from']+' | '+str(len(selection))+' exact signed disjoint target-prefix shears'
 return up.rehist(d)
def emit(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    c=json.loads(gzip.decompress((up.BASE/'data/gcert1-e8-r783-far.json.gz').read_bytes()))
    selection=json.loads((ROOT/'SELECTION.json').read_text());d=transform(c,selection)
    original=up.signed_rows(c);assert original==up.signed_rows(d)
    ablated=transform(c,[]);assert all(ablated[k]==c[k] for k in ['A','B','blocks'])
    controls=[];at=next(i for i,e in enumerate(selection) if Q(e['coefficient'])<0);entry=selection[at]
    bad=copy.deepcopy(d);bad['B'].pop(at);assert up.signed_rows(bad)!=original;controls.append('signed setup omitted')
    restoration=['in',entry['recovery_frame'],entry['destination'],[[entry['donor_target'],-1,1]]]
    k=next(i for i,g in enumerate(d['B']) if g==restoration)
    bad=copy.deepcopy(d);bad['B'].pop(k);assert up.signed_rows(bad)!=original;controls.append('signed restoration omitted')
    bad=copy.deepcopy(d);bad['B'][k][3][0][1]=1;assert up.signed_rows(bad)!=original;controls.append('signed restoration sign reversed')
    bad=copy.deepcopy(selection);bad[1]['destination']=bad[0]['destination']
    try:transform(c,bad)
    except AssertionError:controls.append('overlapping targets rejected')
    else:raise AssertionError('overlapping targets accepted')
    def hist(z):
        h=Counter()
        for block in z['blocks'].values():h.update({int(k):n for k,n in block.items()})
        return h
    old,new=hist(c),hist(d);delta={k:new[k]-old[k] for k in new.keys()|old.keys() if new[k]!=old[k]}
    predicted=Counter()
    for e in selection:
        for k,n in e['histogram_delta'].items():predicted[int(k)]+=n
    assert delta=={k:n for k,n in predicted.items() if n} and sum(k*n for k,n in delta.items())==0
    oldcert=json.loads(gzip.decompress((SOURCE/'data/prefix18.json.gz').read_bytes()));audit=json.loads((SOURCE/'data/sink-audit.json').read_text())
    oldgroups=oldcert['A']+oldcert['B'];groups=d['A']+d['B']
    for e in audit['accepted']:
        matches=[i for i,g in enumerate(groups) if g==oldgroups[e['cut_group']]];assert len(matches)==1;e['cut_group']=matches[0]
    data=json.dumps(d,sort_keys=True,separators=(',',':')).encode();(out/'candidate.json').write_bytes(data);(out/'candidate.json.gz').write_bytes(gzip.compress(data,mtime=0));(out/'sink-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    result=dict(status='PASS_SIGNED_PREFIX_RAW_OPERATOR_AND_CONTROLS',pairs=len(selection),all_initial_columns=len(original),histogram_delta=delta,negative_controls=controls,ablation=True,candidate_sha256=hashlib.sha256(data).hexdigest(),sink_cuts=[e['cut_group'] for e in audit['accepted']])
    assert result['candidate_sha256']==json.loads((ROOT/'EXPECTED-DISCOVERY.json').read_text())['candidate_sha256']
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(json.dumps(emit(sys.argv[1]),indent=2))
