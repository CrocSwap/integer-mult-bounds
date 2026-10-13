from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,json,copy,hashlib,argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();src,out=a.input,a.out;w=json.loads(gzip.decompress(src.read_bytes()));old=copy.deepcopy(w);V=w['v'];N=2*V+w['R']
assert hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='30990c2ebba280bf1cb4c0ba0ead5f29c484f01bc83ef8e0002205674d77be94','pinned trace20 source'
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

ops=[]
for f,t,ss in w['A']:
 for s in ss:ops.append([f,t,s])

# Keep original IDs while composing the seven explicitly nominated local rewrites.
ops=[[i,*o]for i,o in enumerate(ops)]
MOVES=[(2337,2327,2328,163,484),(2393,2387,2388,199,486),(2402,2394,2395,200,486),(2423,2415,2416,217,487),(2426,2417,2418,218,487),(2454,2444,2445,235,488),(2481,2471,2472,254,489)]
def commute(x,y):return x[2]!=y[3]and y[2]!=x[3]
receipts=[]
for k,l,q,fe,fb in MOVES:
 pk=next(i for i,o in enumerate(ops)if o[0]==k);pl=next(i for i,o in enumerate(ops)if o[0]==l);pq=next(i for i,o in enumerate(ops)if o[0]==q)
 e=ops[pk];b=ops[pl];c=ops[pq];assert pl<pk
 assert(b[2]==e[3])!=(b[3]==e[2]);ct,cs=(e[2],b[3])if b[2]==e[3]else(b[2],e[3]);assert c[2:]==[ct,cs]
 assert all(commute(e,ops[j])for j in range(pl+1,pk));assert all(commute(c,ops[j])for j in range(min(pl,pq),max(pl,pq)+1)if j not in[pk,pl,pq])
 new=[]
 for o in ops:
  if o[0]==l:new.extend([[k,fe,e[2],e[3]],[l,fb,b[2],b[3]]])
  if o[0]not in[k,l,q]:new.append(o)
 ops=new;receipts.append(dict(k=k,l=l,q=q,old_gates=[e,b,c],new_frames=[fe,fb]))
new=[o[1:]for o in ops]
w['A']=[[f,t,[s]]for f,t,s in new];w['C']=[[1,t,list(ss)]for f,t,ss in reversed(w['A'])]
h0,c0=replay(old);h1,c1=replay(w);delta={k:h1[k]-h0[k]for k in sorted(h0.keys()|h1.keys())if h1[k]!=h0[k]};assert c0==c1==[8]*9;assert delta=={1:7,3:-7,4:-7,6:7}
out.mkdir(parents=True,exist_ok=False);raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();data=gzip.compress(raw,compresslevel=9,mtime=0);data=data[:9]+bytes([255])+data[10:];(out/'WORD.json.gz').write_bytes(data)
r=dict(status='PASS_EXACT_STEINBERG_CANCELLATION',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),moves=receipts,all_dirty_columns=N,profile_delta=delta,paid_profile_with_retained_copies=dict(h1+Counter(c1)),retained_total_ranks=c1);(out/'REVIEW.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
