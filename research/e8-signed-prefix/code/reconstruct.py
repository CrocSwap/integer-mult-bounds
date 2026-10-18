"""Source-bound signed target-prefix reconstruction.
Rehist adapted from PR378; raw operator replay and prefix construction from PR390.
This package adds the R781 composition and signed scale selection, not a new
all-size multiplication theorem. Run without Python -O.
"""
from pathlib import Path
import json,copy,gzip,hashlib,sys,argparse
from fractions import Fraction as Q
from collections import defaultdict,Counter
assert __debug__, 'Assertions must be enabled'
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/helper'))
import candidate_frames
def rehist(c):
    """recompute block histograms and N exactly as gx.check1 counts them (climbs per class, COPY ranks)"""
    v, R = c['v'], c['R']; n = 2 * v + R; dim = [len(f) for f in c['frames']]
    cls = lambda r: 'x' if r < v else 'y' if r < 2 * v else 's'
    cur = list(c['start']); H = {'x': Counter(), 'y': Counter(), 's': Counter(), 'c': Counter()}
    def climb(r, f):
        if cur[r] != f: H[cls(r)][dim[f] - dim[cur[r]]] += 1; cur[r] = f
    for ph in ('A', 'B'):
        if ph == 'B':
            for k, s_, f in c['ret']: H['c'][dim[f]] += 1
        for g in c[ph]:
            regs = [g[2]] + ([t for t, _, _ in g[3]] + list(g[4]) if g[0] == 'out' else [x for x, _, _ in g[3]] if g[0] == 'in' else [])
            for r in regs: climb(r, g[1])
    for r in range(n): climb(r, c['final'][r])
    c['blocks'] = {k: {str(r): x for r, x in sorted(w.items())} for k, w in H.items()}
    c['N'] = sum(r * x for w in H.values() for r, x in w.items())
    return c

def signed_rows(c):
    v,R=c['v'],c['R'];n=2*v+R;row=[{r:Q(1)} for r in range(n)]
    def add(a,b,q):
        for k,z in list(row[b].items()):
            z=row[a].get(k,Q(0))+q*z
            if z:row[a][k]=z
            else:row[a].pop(k,None)
    def phase(gs):
        for g in gs:
            for r,a,b in g[3]:add(r if g[0]=='out' else g[2],g[2] if g[0]=='out' else r,Q(a,b))
    phase(c['A'])
    for t,sc in enumerate(c['scat']['table']):
        for k,a,b in sc:add(v+t,c['ret'][k][1],Q(a,b))
    phase(c['B']);return row
def transform(c,selection):
 v=c['v'];n=2*v+c['R'];nA=len(c['A']);d=copy.deepcopy(c);flat=[];version=[0]*n
 for gi,g in enumerate(c['A']+c['B']):
  for r,a,b in g[3]:
   t,s=(r,g[2])if g[0]=='out'else(g[2],r);assert not(v<=s<2*v)
   flat.append((gi,t,s,g[1],version[s],Q(a,b)));version[t]+=1
 destinations=[x['destination']for x in selection];donors={x['donor_target']for x in selection};assert len(set(destinations))==len(destinations)and not(set(destinations)&donors)
 destcuts={};addat=defaultdict(list);setups=[]
 def gate(f,t,s,q):
  assert q.denominator in(1,2,3,6)
  return [['in',f,t,[[s,1 if q>0 else-1,q.denominator]]]for _ in range(abs(q.numerator))]
 for e in selection:
  i,j,cut,E=[e[k]for k in('destination','donor_target','cut_group','recovery_frame')];q=Q(e['scale_numerator'],e['scale_denominator']);assert c['start'][i]==c['start'][j]==0
  destcuts[i]=cut;setups+=gate(0,i,j,-q);rows={}
  for gi,t,s,f,ve,a in flat:
   if gi<nA or gi>cut or t not in(i,j):continue
   key=s,ve,f
   if key not in rows:rows[key]=[Q(0),gi]
   rows[key][0]+=a if t==i else-q*a
  for (s,ve,f),(a,gi) in rows.items():
   if a:addat[gi]+=gate(f,i,s,a)
  addat[cut]+=gate(E,i,j,q)
 B=list(setups)
 for bi,g in enumerate(c['B']):
  gi=nA+bi;g=copy.deepcopy(g)
  if g[0]=='out':g[3]=[z for z in g[3]if z[0]not in destcuts or gi>destcuts[z[0]]];B.append(g)
  elif g[2]in destcuts and gi<=destcuts[g[2]]:B.extend(['out',g[1],s,[],[]]for s,_,_ in g[3])
  else:B.append(g)
  B.extend(addat.get(gi,[]))
 d['B']=B;d['derived_from']=c['derived_from']+' | signed prefix stars with unchanged donors'
 return rehist(d)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);args=ap.parse_args();out=args.output;assert not out.exists();out.mkdir(parents=True)
 raw=candidate_frames.build((ROOT/'data/far783.json.gz').read_bytes());(out/'base.json').write_bytes(raw)
 assert hashlib.sha256(raw).hexdigest()=='3df4c637c69840d53a0137eadbe16e25add617984bbe4da099d059f026192f1e'
 c=json.loads(raw);selection=json.loads((ROOT/'data/selection.json').read_text());assert len(selection)==25
 d=transform(c,selection);original=signed_rows(c);assert signed_rows(d)==original
 assert transform(c,[])['blocks']==c['blocks']
 controls=[]
 bad=copy.deepcopy(d);bad['B'].pop(0);assert signed_rows(bad)!=original;controls.append('missing setup rejected')
 # Negate a restoration of a negative-scale pair: it must alter the raw map.
 e=next(z for z in selection if z['scale_numerator']==-1)
 bad=copy.deepcopy(d);at=next(i for i,g in enumerate(bad['B']) if g[0]=='in' and g[1]==e['recovery_frame'] and g[2]==e['destination'] and g[3]==[[e['donor_target'],-1,1]])
 bad['B'][at][3][0][1]=1;assert signed_rows(bad)!=original;controls.append('wrong negative restoration sign rejected')
 wrong=copy.deepcopy(selection);wrong[1]['destination']=wrong[0]['destination']
 try:transform(c,wrong)
 except AssertionError:controls.append('duplicate destination rejected')
 else:raise AssertionError('duplicate destination accepted')
 def hist(z):
  h=Counter()
  for b in z['blocks'].values():h.update({int(r):n for r,n in b.items()})
  return h
 a,b=hist(c),hist(d);delta={str(r):b[r]-a[r]for r in a.keys()|b.keys()if b[r]!=a[r]}
 assert delta=={'1':-8,'2':-8,'3':-7,'4':-8,'6':-14,'7':23}
 body=json.dumps(d,sort_keys=True,separators=(',',':')).encode();assert body==gzip.decompress((ROOT/'data/signed25.json.gz').read_bytes())
 assert hashlib.sha256(body).hexdigest()=='a4e42aa1663f5ad0da48cee6fe8514b205e43cf6e791b80674dbc7506a098a32'
 (out/'candidate.json').write_bytes(body);(out/'candidate.json.gz').write_bytes(gzip.compress(body,mtime=0))
 result={'status':'PASS_EXACT_SIGNED_PREFIX_RECONSTRUCTION','live_columns':1021,'pairs':25,'positive_scales':16,'negative_scales':9,'distinct_donors':25,'histogram_delta':delta,'controls':controls,'base_sha256':hashlib.sha256(raw).hexdigest(),'candidate_json_sha256':hashlib.sha256(body).hexdigest(),'scope':'Raw scalar matrix equality and exact histogram; phase, physical template, finite invoice and moments checked separately.'}
 (out/'RECONSTRUCTION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
