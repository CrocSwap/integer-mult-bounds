"""Actual signed target-prefix prototype, isolated from immutable95."""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import json,gzip,hashlib,struct,subprocess,sys,copy
P=Path(__file__).resolve().parent;R=P.parents[4];S=R/'experiments/stage-search/pr445-signed95-eleven/signed';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cands=read(R/'experiments/architecture/independent-audit/TARGET-PREFIX-SIGNED.json')['candidates'];cs=read(P/'PAIR-SELECTION.json')['pairs']
w=read(S/'word.json');base=copy.deepcopy(w);olddecoder=read(S/'decoder-and-dirt.json');oldframes=read(S/'records/frames.json')['frames'];sub=lambda a,b:all(sum(x*y for x,y in zip(row,col))==0 for row in oldframes[str(a)]['B']for col in oldframes[str(b)]['A'])
for e in cs:
 u,d,G=e['receiver'],e['donor'],e['frame'];w['D'].append([0,u,[d]]);sc={int(k):v for k,v in e['scatter_new'].items()};w['scatter'][u-120]=sorted(sc)
 B=[];inserted=0;cut=max(i for i,(f,a,ss)in enumerate(w['B'])if a==d and f==G)
 for i,(f,a,ss) in enumerate(w['B']):
  if a==u and sub(f,G):continue
  B.append([f,a,ss])
  if i==cut:B.append([G,u,[d]]);inserted+=1
 assert inserted==1;w['B']=B
scatter_coeff={e['receiver']:{int(k):v for k,v in e['scatter_new'].items()}for e in cs}
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(P/'word.json').write_bytes(raw);(P/'word.json.gz').write_bytes(gzip.compress(raw,mtime=0));(P/'SELECTION.json').write_bytes((S/'SELECTION.json').read_bytes())
subprocess.run([sys.executable,'-B',str(R/'experiments/bit-search/pr434/source/research/split-centres-global/vendor/export_records.py'),str(P/'word.json'),str(P/'records')],check=True)
E=list(struct.iter_unpack('<6i',(P/'records/249-records.bin').read_bytes()));F={int(k):v for k,v in read(P/'records/frames.json')['frames'].items()};st=read(P/'records/249-states.json');sel=read(S/'SELECTION.json');co={(d,e['pivot']):-c for e in sel['entries']for d,c in e['donor_coefficients']};groups=defaultdict(list)
for e in sel['entries']:
 for d,c in e['donor_coefficients']:groups[d,e['frame']].extend([e['pivot']]*abs(c))
np=len(groups);nc=len(read(S/'baseline.json')['C'])
def coeff(phase,i,a,b):
 if phase=='A'and i<np:return 1 if co[a,b]>0 else-1
 if phase=='C':return -1 if i<nc else(-1 if co[a,b]>0 else 1)
 return 1
expected={z:[coeff(ph,i,a,b)for i,(f,a,ss)in enumerate(w[ph])for b in ss]for z,ph in [(2,'A'),(4,'B'),(5,'C')]}
def add(a,b,c):
 for k,v in list(b.items()):
  n=a.get(k,0)+c*v
  if n:a[k]=n
  elif k in a:del a[k]
rows=[{i:1}for i in range(980)]
for e in cs:add(rows[e['receiver']],rows[e['donor']],-1)
for ph in ['A','B']:
 if ph=='B':
  ret=[dict(rows[a])for a in w['ret']]
  for t,ks in enumerate(w['scatter']):
   for k in ks:add(rows[120+t],ret[k],scatter_coeff.get(120+t,{}).get(k,1))
 for i,(f,a,ss)in enumerate(w[ph]):
  for b in ss:add(rows[a],rows[b],coeff(ph,i,a,b))
M=[];K=[]
for t in range(120):
 x=dict(rows[120+t]);assert x.pop(120+t)==1;assert not any(120<=k<240 for k in x);M.append({str(k):v for k,v in x.items()if k<120});K.append({str(k):v for k,v in x.items()if k>=240})
assert M==olddecoder['M']and K==olddecoder['K'],'Rebuilt decoder or dirt response changed'
network=[(e['receiver'],e['donor'],-1)for e in cs]
for i,(f,a,ss)in enumerate(w['A']):network.extend((a,b,coeff('A',i,a,b))for b in ss)
for t,ks in enumerate(w['scatter']):network.extend((120+t,w['ret'][k],scatter_coeff.get(120+t,{}).get(k,1))for k in ks)
for i,(f,a,ss)in enumerate(w['B']):network.extend((a,b,1)for b in ss)
for t in range(120):
 cov={120+t:1}
 for a,b,c in reversed(network):
  q=cov.get(a,0)
  if q:cov[b]=cov.get(b,0)+c*q
 assert {k:v for k,v in cov.items()if v}==rows[120+t],('independent target adjoint',t)

D=[(1,120+t,int(k),-v,0,1)for t,row in enumerate(K)for k,v in sorted(row.items(),key=lambda z:int(z[0]))];signed=list(D);idx=Counter();pre={(e['receiver'],e['donor'])for e in cs}
retidx=-1
for op,a,b,c,f,z in E:
 if op==2:retidx+=1
 if op==1 and z==3:c=scatter_coeff.get(a,{}).get(retidx,1)
 if op==1 and z==1:
  if(a,b)in pre:signed.append((op,a,b,-1,f,z))
  continue
 if op==1 and z in expected:c=expected[z][idx[z]];idx[z]+=1
 signed.append((op,a,b,c,f,z))
assert [(op,a,b,c%2 if op==1 else c,f,z)for op,a,b,c,f,z in signed if op!=1 or c%2]==E
(P/'signed-records.bin').write_bytes(b''.join(struct.pack('<6i',*e)for e in signed))
def replay(es,reverse=False):
 A=[{i:1}for i in range(980)]+[{}];norm=[1]*980+[0];peak=1;state={int(k):v for k,v in st['initial'].items()};source=[{i:1}if i<120 else{}for i in range(981)];target_checks=[]
 for op,a,b,c,f,z in reversed(es)if reverse else es:
  if op==0 and not reverse:
   assert state[a]==b and F[b]['dim']<=F[c]['dim'];assert all(sum(x*y for x,y in zip(u,v))==0 for u in F[b]['B']for v in F[c]['A']);state[a]=c
  elif op==1:
   if not reverse:assert state[a]==state[b]==f
   if not reverse and 120<=b<240:
    bad=[s for s in source[b]if any(sum(x*y for x,y in zip(w['lines'][s],ann))for ann in F[f]['A'])];vec=[sum(c*w['lines'][k][j]for k,c in source[b].items())for j in range(8)];ann=[sum(x*y for x,y in zip(vec,v))for v in F[f]['A']];target_checks.append(dict(dst=a,src=b,frame=f,source_terms=len(source[b]),bad_support=bad,summed_functional=vec,summed_annihilator_pairings=ann))
   k=-c if reverse else c;add(A[a],A[b],k);norm[a]+=abs(k)*norm[b];peak=max(peak,norm[a]);add(source[a],source[b],k)
  elif op==(3 if reverse else 2):A[b]=dict(A[a]);norm[b]=norm[a];source[b]=dict(source[a]);state[b]=f
  elif op==(2 if reverse else 3):assert A[b]==A[a];A[b]={};norm[b]=0;source[b]={};state.pop(b,None)
 want=[{i:1}for i in range(980)]+[{}]
 for t,m in enumerate(M):add(want[120+t],{int(k):v for k,v in m.items()},-1 if reverse else 1)
 assert A==want,'all980 endpoint/dirt failure'
 if not reverse:assert state=={int(k):v for k,v in st['final'].items()}
 return dict(prefix=peak,target_controls=target_checks)
fwd=replay(signed);rev=replay(signed,True)
# Literal forward then inverse identity holds for arbitrary correlated input rows.
# Both elementary ADD and sequentialCOPY/ERASE words are exact inverses.

state={int(k):v for k,v in st['final'].items()};RH=Counter()
for op,a,b,c,f,z in reversed(signed):
 if op==0:
  assert state[a]==c and F[c]['dim']>=F[b]['dim'];assert all(sum(x*y for x,y in zip(u,v))==0 for u in F[c]['A']for v in F[b]['B']);state[a]=b
  if f:RH[f]+=1
 elif op==1:assert state[a]==state[b]==f
 elif op==3:assert b==980 and b not in state and state[a]==c;state[b]=f;RH[8]+=1
 else:assert op==2 and state[a]==c and state[b]==f;state.pop(b)
assert state=={int(k):v for k,v in st['initial'].items()}
controls=[]
for name,pred in [('omit_zero_precondition',lambda e:e[0]==1 and e[5]==1 and(e[1],e[2])in pre),('omit_target_mix',lambda e:e[0]==1 and e[5]==4 and 120<=e[2]<240)]:
 bad=list(signed);i=next(i for i,e in enumerate(bad)if pred(e));bad.pop(i)
 try:replay(bad)
 except AssertionError:controls.append(name)
 else:raise AssertionError('mutation accepted '+name)
for name,pred in [('flip_zero_precondition',lambda e:e[0]==1 and e[5]==1 and(e[1],e[2])in pre),('flip_target_mix',lambda e:e[0]==1 and e[5]==4 and 120<=e[2]<240)]:
 bad=list(signed);i=next(i for i,e in enumerate(bad)if pred(e));op,a,b,c,f,z=bad[i];bad[i]=(op,a,b,-c,f,z)
 try:replay(bad)
 except AssertionError:controls.append(name)
 else:raise AssertionError('mutation accepted '+name)
H=Counter()
for op,a,b,c,f,z in E:
 if op==0 and f:H[f]+=1
 elif op==2:H[z]+=1
res=dict(status='PASS_ACTUAL_SIGNED_TARGET_PREFIX_980_DIRT_LITERAL_INVERSE_FRAME_LEDGER_PENDING_TARGET_OPERATOR_ADMISSION',pairs=cs,profile=dict(H),local_rank_mass=sum(r*n for r,n in H.items()),signed_units=sum(abs(c)for op,a,b,c,f,z in signed if op==1),raw_units=sum(abs(c)for op,a,b,c,f,z in E if op==1),independent_adjoint_all120_target_rows=True,rebuilt_K_unchanged=True,reflected_profile=dict(RH),mutation_controls_rejected=controls,forward=fwd,inverse=rev,source_word_sha256=sha(S/'word.json'),word_sha256=hashlib.sha256(raw).hexdigest(),scope='Exact finite scalar/frame candidate. New target-as-source rational operator/compiler/common-frame support and reflected source admissibility remain separate. No global score admission.')
old=read(S/'RESULT.json')
res.update(integer_kernel=old['integer_kernel'],compensation=old['compensation'],arbitrary_helper_dirt_restored_exactly=True,forward_then_signed_inverse_identity=True,exported_F2_record_sha256=sha(P/'records/249-records.bin'),signed_record_sha256=sha(P/'signed-records.bin'),literal_signed_inverse=dict(max_prefix_row_l1=rev['prefix'],formal_columns=980),controls=[dict(name=n,rejected=True)for n in controls])
res['forward']['max_prefix_row_l1']=fwd['prefix']
(P/'decoder-and-dirt.json').write_bytes((S/'decoder-and-dirt.json').read_bytes())
(P/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(res['status'],dict(H),res['signed_units'],fwd['prefix'],rev['prefix']);print('targetsupport',fwd['target_controls'])
