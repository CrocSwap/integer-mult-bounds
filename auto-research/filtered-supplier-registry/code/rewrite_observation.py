"""Construct a response-equivalent gate rewrite and regenerate inverse cleanup.
CLI --input INPUT_WORD.json.gz --out NEW_OUTPUT_DIRECTORY. Frozen filtered531 witness.
"""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,copy,hashlib,sys,argparse
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();src,out=args.input,args.out;assert not out.exists();old=json.loads(gzip.decompress(src.read_bytes()));w=copy.deepcopy(old);V=len(w['ports']);N=2*V+w['report']['R'];part,index,u='A',645,245;e=w[part][index];assert e==['add',31,240,1,2,[296,168,120,6]];t,s=e[1:3];assert u not in {t,s}and not V<=u<2*V and not V<=t<2*V and t not in w['centers']and u not in w['centers']
assert all(a[0]!='add' or V<=a[1]<2*V or not V<=a[2]<2*V for sec in ['A','cut','B'] for a in w[sec]), 'background reads only background'
assert all(V<=a[1]<2*V for a in w['cut']), 'cut has no un-reversed background writes'
H=[{r-V:Q(1)}if V<=r<2*V else {}for r in range(N)]
for a in reversed(w['A'][index+1:]+w['cut']+w['B']):
 z=a[1]
 if a[0]=='scale':
  q=Q(a[2],a[3]);H[z]={j:q*x for j,x in H[z].items()}
 else:
  v=a[2];assert z!=v;q=Q(a[3],a[4])
  for j,x in H[z].items():
   H[v][j]=H[v].get(j,Q(0))+q*x
   if not H[v][j]:del H[v][j]
assert H[t]and H[u];j=min(H[t]);lam=H[t][j]/H[u][j];assert H[t]=={a:lam*x for a,x in H[u].items()};assert lam==-2
q=Q(e[3],e[4])*lam;assert not q.denominator&(q.denominator-1);w[part][index]=['add',u,s,q.numerator,q.denominator,e[-1]]
full=old['cleanup'][0][-1]
def inverse(e):
 e=copy.deepcopy(e)
 if e[0]=='add':e[3]*=-1
 else:e[2],e[3]=e[3],e[2]
 e[-1]=copy.deepcopy(full);return e
w['cleanup']=[inverse(e)for e in reversed(w['A']+w['B'])if not V<=e[1]<2*V]
def span(F):
 S={0}
 for a in F:S|={x^a for x in S}
 return frozenset(S)
def chains(z):
 tr=[[]for _ in range(N)]
 for r in range(N):tr[r].append(span([z['ports'][r]]if r<V else z.get('start_extra',{}).get(str(r),[])))
 for sec in ['A','B']:
  if sec=='B':
   for r,F in zip(z['centers'],z['center_frames']):tr[r].append(span(F))
   for r,F in z.get('target_levels',{}).items():tr[V+int(r)].append(span(F))
  for a in z[sec]:
   for r in [a[1]]+([a[2]]if a[0]=='add'else []):tr[r].append(span(a[-1]))
 for r in range(N):tr[r].append(span([x for x in range(512)if not(x&z['ports'][r-V]).bit_count()%2])if V<=r<2*V else span(full))
 return [[f for i,f in enumerate(c)if i==0 or f!=c[i-1]]for c in tr]
assert chains(old)==chains(w);assert old['start_extra']==w['start_extra'] and old['center_frames']==w['center_frames']
assert len(w['A'])==len(old['A']) and len(w['cleanup'])==len(old['cleanup'])
out.mkdir();data=gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0);(out/'FULL-WORD.json.gz').write_bytes(data)
r=dict(status='PASS_CONSTRUCTIVE_OBSERVATIONAL_GATE_RETARGET',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),part=part,index=index,old_event=e,new_event=w[part][index],suffix_response_ratio=str(lam),suffix_old_column={str(k):str(v)for k,v in H[t].items()},suffix_new_column={str(k):str(v)for k,v in H[u].items()},all_deduplicated_frame_chains_identical=True,entrance_widths_unchanged=True,paid_histogram_unchanged=True,cleanup_regenerated=True,scope='Constructive nonzero-response retarget, not dead-store deletion. Full changed scalar and physical audits remain required; no independent kappa gain claimed.')
(out/'OBSERVATIONAL-REWRITE.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
