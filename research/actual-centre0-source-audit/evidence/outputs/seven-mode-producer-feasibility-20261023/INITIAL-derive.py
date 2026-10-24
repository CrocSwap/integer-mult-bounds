"""Read pinned source; derive centre output factors only. No candidate/full replay."""
import os,subprocess,json,gzip,hashlib
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent
REPO=P.parent.parent/'integer-mult-bounds'
HEAD='86e474038e05f99a76d41f71d81946ad2327e4a4'
BASE='research/native-involutive-dual/'
def read(name):return subprocess.check_output(['git','-C',str(REPO),'show',HEAD+':'+BASE+name],env=os.environ|{'GIT_NO_LAZY_FETCH':'1'})
def reduce(w,g):return w[:-1]if w and w[-1]==-g else w+(g,)
def add(dst,src,a):
 for k,v in list(src.items()):
  t=dst.get(k,Q())+a*v
  if t:dst[k]=t
  else:dst.pop(k,None)
def field(r):return r[1]+(632 if r[0]=='C'else 0)
a=json.loads(gzip.decompress(read('SOURCE-WORD.json.gz')));R=[[Q(x)for x in r]for r in json.loads(read('R.json'))];p=a['programs']['forward']
centers=[(n,e)for n,e in enumerate(p)if e[0]=='center']
# Formal impulse at the OUTPUT of each physical centre. This extracts the
# literal suffix output factor; no initial owner, helper or Gaussian input runs.
rows=[{}for _ in range(633)]
for n,e in enumerate(p):
 if e[0]=='scalar':
  g=e[1];dst=field(g[1])
  if g[0]=='clear':rows[dst]={}
  elif g[0]=='copy':rows[dst]=rows[field(g[2])].copy()
  elif g[0]=='add':add(rows[dst],rows[field(g[2])],Q(g[3],g[4]))
  elif g[0]=='scale':rows[dst]={k:v*Q(g[2],g[3])for k,v in rows[dst].items()}
 elif e[0]=='warp':
  dst=field(e[1]);rows[dst]={(k,reduce(w,e[2])):v for(k,w),v in rows[dst].items()}
 elif e[0]=='center':rows[632]={((n-centers[0][0])//26,()):Q(1)}
# All words must be empty for scalar owner-space comparison.
nonempty=[(i,k,w,str(v))for i,row in enumerate(rows)for(k,w),v in row.items()if w]
assert not nonempty,nonempty[:3]
V=[[rows[112+i].get((k,()),Q())for k in range(8)]for i in range(112)]
r0=[row[0]for row in R];target=[sum(R[k][i]*r0[k]for k in range(8))for i in range(112)]
results=[]
for k,(n,e)in enumerate(centers):
 v=[row[k]for row in V];nz=[i for i,x in enumerate(v)if x];t=[i for i,x in enumerate(target)if x]
 first=next(((i,j)for i in range(112)for j in range(i+1,112)if v[i]*target[j]!=v[j]*target[i]),None)
 results.append({'center':k,'source_index':n,'operation':e,'copied_source':p[n-1],'output_nonzeros':len(nz),'proportional_to_Rt_r0':first is None,'first_2x2_minor':None if first is None else {'rows':first,'v':[str(v[i])for i in first],'Rt_r0':[str(target[i])for i in first]},'output_column':[str(x)for x in v]})
result={'source_head':HEAD,'method':'formal centre-output impulses through literal frozen suffix only; no candidate/native input replay','r0':[str(x)for x in r0],'r0_norm2':str(sum(x*x for x in r0)),'Rt_r0':[str(x)for x in target],'centers':results,'source_blobs':{name:hashlib.sha256(read(name)).hexdigest()for name in ['SOURCE-WORD.json.gz','R.json','INVOLUTIVE-WORD.json.gz','BACKWARD-WORD.json.gz','NORMALIZERS.json']}}
(P/'DERIVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k not in ('centers','Rt_r0')},indent=2));print(json.dumps([{k:v for k,v in r.items()if k!='output_column'}for r in results],indent=2))
# Pull back only the literal input read by centre0. Native Gaussian chart
# changes are identities in the authenticated normalized symbolic model.
n0=centers[0][0];read0=field(p[n0-1][1][2]);cov={(read0,()):Q(1)}
for e in reversed(p[:n0-1]):
 if e[0]=='scalar':
  g=e[1];dst=field(g[1]);terms=[(w,v)for(i,w),v in cov.items()if i==dst]
  if g[0]in ('clear','copy'):
   cov={key:v for key,v in cov.items()if key[0]!=dst}
   if g[0]=='copy':
    src=field(g[2])
    for w,v in terms:add(cov,{(src,w):v},Q(1))
  elif g[0]=='add':
   src=field(g[2]);coef=Q(g[3],g[4])
   for w,v in terms:add(cov,{(src,w):v},coef)
  elif g[0]=='scale':
   for w,v in terms:cov[(dst,w)]=v*Q(g[2],g[3])
 elif e[0]=='warp':
  dst=field(e[1]);terms=[(w,v)for(i,w),v in cov.items()if i==dst];cov={key:v for key,v in cov.items()if key[0]!=dst}
  for w,v in terms:add(cov,{(dst,reduce(w,e[2])):v},Q(1))
assert all(not w for(i,w)in cov),[(i,w)for(i,w)in cov if w][:3]
main=[cov.get((i,()),Q())for i in range(112)];helpers={str(i):str(v)for(i,w),v in cov.items()if i>=224}
assert main==R[0]
assert all(i<112 or i>=224 for i,w in cov)
assert all(a['canonical']['start'][int(i)]==0 for i in helpers)
# centre0's source is unaffected by original helper precomp because it reads
# X/helpers, while the common-chart precomp writes Y alone.
result['center0_input_factor']={'read_field':read0,'main':[str(x)for x in main],'helper':helpers,'nonempty_words':False,'Y_coefficients':False}
# F_actual = F_old + R0^T R0/4 - 3 e0 (r0^T R), with helper factor removed.
U=[[(1-12*(i in {0,7,20,23,86,93,108,111}))*R[k][i]/4 for k in range(8)]for i in range(112)]
F=[[Q(i==j)-sum(U[i][k]*R[k][j]for k in range(8))for j in range(112)]for i in range(112)]
G=[[F[i][j]+R[0][i]*R[0][j]/4-3*(i==0)*target[j]for j in range(112)]for i in range(112)]
# Desired F_projector differs from actual only in the restored H8 contribution.
diff=lambda i,j:R[0][i]*R[0][j]/4-target[i]*target[j]/16
result['center0_actual']={'formula':'F_old + outer(R[0],R[0])/4 - 3 outer(e0,r0^T R)','row0':[str(x)for x in G[0]],'col0':[str(row[0])for row in G],'first_projector_mismatch':{'input':0,'output':0,'actual':str(G[0][0]),'desired':'1','difference':str(diff(0,0))},'helper_precomp_removed_terms':len(helpers)*sum(v!=0 for v in V[0:0])if False else len(helpers)*56,'helper_input_factor_nonzeros':len(helpers),'profile':{'1':2208,'2':412,'3':510,'4':127,'5':40,'8':1}}
(P/'DERIVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print('centre0 input main=R0; helper inputs',len(helpers),'actual F00',G[0][0],'F10',G[1][0],'desired F00 1,F10 0')
inv=json.loads(gzip.decompress(read('INVOLUTIVE-WORD.json.gz')));ip=inv['program'];N=6596
assert len(ip)==N+len(p)+456
pre={}
for e in ip[:N]:
 assert e[0]=='scalar'and e[1][0]=='add'and e[2]==0
 g=e[1];pre[(field(g[1]),field(g[2]))]=Q(g[3],g[4])
assert len(pre)==N
h={int(i):Q(v)for i,v in helpers.items()}
updates=[]
for i in range(112):
 v=V[i][0]
 if not v:continue
 for j,q in h.items():
  key=(112+i,j);delta=-v*q;old=pre.get(key,Q());new=old+delta
  updates.append([key[0],key[1],str(old),str(delta),str(new)])
  if new:pre[key]=new
  else:pre.pop(key,None)
assert all(a['canonical']['start'][i]==a['canonical']['start'][j]==0 for i,j in pre)
x=[row[0]for row in G];xx=[sum(row[j]*x[j]for j in range(112))for row in G]
firstsq=next((i for i,v in enumerate(xx)if v!=Q(i==0)),None)
asym=next(((i,j)for i in range(112)for j in range(i+1,112)if G[i][j]!=G[j][i]),None)
result['center0_actual'].update({'precomp_original_nonzero_ADDs':N,'precomp_new_nonzero_ADDs':len(pre),'precomp_delta_terms':len(updates),'involution_e0_first_mismatch':{'output':firstsq,'actual':str(xx[firstsq]),'expected':str(Q(firstsq==0))}if firstsq is not None else None,'first_asymmetric_entry':{'i':asym[0],'j':asym[1],'Gij':str(G[asym[0]][asym[1]]),'Gji':str(G[asym[1]][asym[0]])}if asym else None})
result['constructible_edit_spec']={'precomp':'Replace first6596 ADDs with exact coefficient dictionary old - outer(v_center0,h_center0); omit zero entries. Full delta coefficients retained below.','center_restore':{'involutive_index':N+n0,'old':ip[N+n0],'new':p[n0]},'repair_remove':{'start_inclusive':N+len(p),'end_exclusive':N+len(p)+57,'first':ip[N+len(p)],'last':ip[N+len(p)+56]},'all_other_events':'Retain literal frozen INVOLUTIVE-WORD sequence and source frame descriptors without changes. No emitted or executed candidate supplied.','precomp_deltas':updates}
result['canonical_metadata']={k:a['canonical'][k]for k in ('h','v','ports','local_profile')}
(P/'DERIVATION.json').write_text(json.dumps(result,indent=2)+'\n')
print('new precomp',len(pre),'firstsquare',result['center0_actual']['involution_e0_first_mismatch'],'firstasym',result['center0_actual']['first_asymmetric_entry']);print('canonical',{k:v for k,v in result['canonical_metadata'].items()if k!='ports'})
