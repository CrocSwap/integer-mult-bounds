from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,copy,sys,argparse
parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();src,out=args.input,args.out;w=json.loads(gzip.decompress(src.read_bytes()));V=w['v'];N=2*V+w['R'];old=copy.deepcopy(w);prefix=[];moves=[];A=[];assert hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='8639e22008c24a5690dd250eba702fe5fca85ddd036dcbec20baba77b7e213ba', 'pinned source word'
for i,(f,t,ss)in enumerate(w['A']):
 if len(ss)==2 and all(s<V for s in ss):
  s=ss[0]
  assert all(t not in sources and dest!=s for ff,dest,sources in old['A'][:i]),('not commutable',i)
  assert t not in w['ret'];prefix.append([w['start'][s],t,[s]]);A.append([f,t,ss[1:]]);moves.append(dict(index=i,helper=t,source=s,old_frame=f,new_frame=w['start'][s]))
 else:A.append([f,t,ss])
w['A']=prefix+A;w['C']=[[1,t,list(ss)]for f,t,ss in reversed(w['A'])]
# Independently compute exact rational row bases and subspace nesting.
def basis(vecs):
 B={}
 for rr in vecs:
  row=list(map(Q,rr))
  for c in sorted(B):
   q=row[c];row=[a-q*b for a,b in zip(row,B[c])]
  c=next((i for i,x in enumerate(row)if x),None)
  if c is not None:
   q=row[c];B[c]=[x/q for x in row]
 return B
FB=[basis(w['lines'][i]for i in f)for f in w['frames']];dim=list(map(len,FB));cache={}
def sub(a,b):
 if (a,b)not in cache:cache[a,b]=len(basis(list(FB[a].values())+list(FB[b].values())))==dim[b]
 return cache[a,b]
def replay(z):
 val=[1<<i for i in range(N)];cur=list(z['start']);H=Counter();tops=[]
 def climb(r,f):
  a=cur[r];assert sub(a,f),(r,a,f)
  if dim[f]>dim[a]:H[dim[f]-dim[a]]+=1
  cur[r]=f
 def gates(sec):
  for f,t,ss in z[sec]:
   assert len({t,*ss})==1+len(ss)
   for r in [t,*ss]:climb(r,f)
   for s in ss:val[t]^=val[s]
 gates('D');gates('A');tops.extend(dim[cur[q]]for q in z['ret']);snap=[val[q]for q in z['ret']]
 for t,ks in enumerate(z['scatter']):
  for k in ks:val[V+t]^=snap[k]
 gates('B');gates('C')
 for r,f in enumerate(z['final']):climb(r,f)
 for r in range(N):assert val[r]==((1<<r)^(1<<(r-V))if V<=r<2*V else 1<<r),r
 return H,tops
h0,c0=replay(old);h1,c1=replay(w);assert c0==c1;delta={k:h1[k]-h0[k]for k in sorted(h0.keys()|h1.keys())if h1[k]!=h0[k]};assert sum(k*v for k,v in delta.items())==0;assert len(moves)==60 and delta=={1:60,2:-120,3:60};assert old['B']==w['B'] and old['D']==w['D'] and old['scatter']==w['scatter'] and old['start']==w['start'] and old['final']==w['final']
out.mkdir(parents=True,exist_ok=False);raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();data=gzip.compress(raw,compresslevel=9,mtime=0);data=data[:9]+bytes([255])+data[10:];(out/'WORD.json.gz').write_bytes(data);r=dict(status='PASS_EXACT_SEEDED_COMMUTING_WORD',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_content_sha256=hashlib.sha256(raw).hexdigest(),moves=moves,all_dirty_columns=N,profile_before=dict(h0),profile_after=dict(h1),profile_delta=delta,paid_profile_with_retained_copies=dict(h1+Counter(c1)),retained_total_ranks=c1,helper_widths_unchanged=True,cleanup_literal_inverse=True,scope='Exact F2 endpoints, rational frame incidence and local profile. Official physical/compiler/prefix/invoice admission still required.')
(out/'SEED-REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='moves'}))
