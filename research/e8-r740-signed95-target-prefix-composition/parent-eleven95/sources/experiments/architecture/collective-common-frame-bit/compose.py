"""Paid cold collective N²=0 unit-row composition nomination."""
import json,numpy as np,copy,hashlib,gzip,subprocess
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csr_matrix
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;P=R/'experiments/architecture/enlarged-even-donors/pivot954';rows=json.load(open(O/'SPARSE.json'))['rows'];sel=json.load(open(P/'SELECTION.json'));old={d for e in sel['entries']for d,c in e['donor_coefficients']}
groups=sorted({(d,r['frame'])for r in rows for d,c in r['coefficients']});gidx={k:len(rows)+j for j,k in enumerate(groups)};n=len(rows)+len(groups);con=[];hi=[]
for j,r in enumerate(rows):
 for d,c in r['coefficients']:
  a=np.zeros(n);a[j]=1;a[gidx[d,r['frame']]]=-1;con.append(a);hi.append(0)
for h in {r['pivot']for r in rows}|{d for d,f in groups}:
 a=np.zeros(n)
 for j,r in enumerate(rows):
  if r['pivot']==h:a[j]=1
 for d,f in groups:
  if d==h:a[gidx[d,f]]=1
 con.append(a);hi.append(1)
obj=np.r_[np.full(len(rows),-1000.),[0 if d in old else 1 for d,f in groups]]
res=milp(obj,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(csr_matrix(np.array(con)),np.full(len(con),-np.inf),hi),options={'time_limit':30,'mip_rel_gap':0})
assert res.x is not None;chosen=[r for j,r in enumerate(rows)if res.x[j]>.5];ps={r['pivot']for r in chosen};ds={d for r in chosen for d,c in r['coefficients']};assert not ps&ds;assert len(ps)==len(chosen)
for d in ds:assert len({r['frame']for r in chosen if any(a==d for a,c in r['coefficients'])})==1
D=O/'composed';D.mkdir(exist_ok=True);w=json.load(open(P/'word.json'));base=json.load(open(P/'baseline.json'));es=copy.deepcopy(sel['entries'])
for r in chosen:es.append({'pivot':r['pivot'],'entrance':w['frames'][r['frame']],'rank':r['rank'],'frame':r['frame'],'donor_coefficients':r['coefficients']})
allp={e['pivot']for e in es};assert not allp&{d for e in es for d,c in e['donor_coefficients']};groups=defaultdict(list)
for e in es:
 for d,c in e['donor_coefficients']:groups[d,e['frame']].extend([e['pivot']]*abs(c))
z=copy.deepcopy(base);z['frames']=w['frames']
for e in es:z['start'][e['pivot']]=e['frame']
z['A']=[[f,d,sorted(v)]for(d,f),v in sorted(groups.items())]+z['A'];z['C']+=[[base['final'][0],d,sorted(v)]for(d,f),v in sorted(groups.items())];z['D']=[[f,d,[x for x in ss if x not in allp]]for f,d,ss in z['D']]
raw=json.dumps(z,sort_keys=True,separators=(',',':')).encode();(D/'word.json').write_bytes(raw)
with gzip.open(D/'word.json.gz','wb')as f:f.write(raw)
sel.update(entries=es,pivots=len(es),entrance_rank=sum(e['rank']for e in es),donor_count=len({d for e in es for d,c in e['donor_coefficients']}),output_sha256=hashlib.sha256(raw).hexdigest());(D/'SELECTION.json').write_text(json.dumps(sel,indent=2));(D/'baseline.json').write_bytes((P/'baseline.json').read_bytes())
subprocess.run(['python3',str(R/'experiments/bit-search/pr434/source/research/split-centres-global/vendor/export_records.py'),str(D/'word.json'),str(D/'records')],check=True)
s=(P/'signed_source.py').read_text().replace("selection['pivots']==80","selection['pivots']==%d"%len(es));(D/'signed_source.py').write_text(s)
(O/'COMPOSITION-NOMINATION.json').write_text(json.dumps({'status':'EXACT_ROLE_DISJOINT_COLLECTIVE_NOMINATION_PENDING_FULL_REPLAY','solver_status':int(res.status),'new_pivots':len(chosen),'rows':chosen,'pivots':len(es),'entrance_rank':sel['entrance_rank'],'donor_count':sel['donor_count'],'prelude_units':sum(abs(c)for e in es for d,c in e['donor_coefficients']),'word_sha256':hashlib.sha256(raw).hexdigest()},indent=2)+'\n');print('NEW',len(chosen),'TOTAL',len(es),flush=True)
