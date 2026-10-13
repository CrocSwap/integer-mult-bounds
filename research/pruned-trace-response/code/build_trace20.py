from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,json,gzip,hashlib,copy
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();src,out=args.input,args.out
w=json.loads(gzip.decompress(src.read_bytes()));old=copy.deepcopy(w);V=w['v'];N=2*V+w['R']
assert hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='19658bad7da646648ff29f79a3acba6c98e5f548c746ea9f14bf3812c9ee4003', 'pinned pruned source'
PASSES=[[[2317, 112, [17, 25]], [2378, 160, [23, 28]], [2407, 184, [19, 24]], [2437, 208, [11, 14]], [2465, 232, [1, 7]], [2474, 236, [115, 117]], [2502, 256, [2, 4]], [2511, 260, [112, 118]], [2541, 280, [8, 13]], [2550, 284, [114, 119]]], [[12, 110, [17, 25]], [24, 159, [23, 28]], [30, 184, [19, 24]], [36, 209, [11, 14]], [42, 234, [1, 7]], [43, 239, [115, 117]], [48, 260, [2, 4]], [49, 265, [112, 118]], [54, 286, [8, 13]], [55, 291, [114, 119]]]]
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

moves=[]
for passnum,rows in enumerate(PASSES):
 ops=[]
 for f,t,ss in w['A']:
  for s in ss:ops.append([len(ops),f,t,s])
 for k,gap,roots in rows:
  pos=next(i for i,o in enumerate(ops)if o[0]==k);anchor=next(i for i,o in enumerate(ops)if o[0]==gap);assert anchor!=pos
  _,oldf,t,s=ops[pos];crossed=ops[anchor:pos]if anchor<pos else ops[pos+1:anchor];assert all(t!=o[3]and s!=o[2]for o in crossed),(k,'noncommuting')
  bb=basis(w['lines'][i]for i in roots);f=next(i for i,b in enumerate(FB)if len(b)==len(bb)and len(basis(list(b.values())+list(bb.values())))==len(b))
  entry=ops.pop(pos);entry[1]=f;ops.insert(anchor if anchor<pos else anchor-1,entry);moves.append(dict(passnum=passnum,original_id=k,before_id=gap,target=t,source=s,old_frame=oldf,new_frame=f))
 w['A']=[[f,t,[s]]for _,f,t,s in ops];w['C']=[[1,t,list(ss)]for f,t,ss in reversed(w['A'])]
h0,c0=replay(old);h1,c1=replay(w);delta={k:h1[k]-h0[k]for k in sorted(h0.keys()|h1.keys())if h1[k]!=h0[k]};assert c0==c1==[8]*9;assert delta=={1:-10,2:10,3:-10,4:-10,6:10}
assert old['B']==w['B']and old['D']==w['D']and old['scatter']==w['scatter']and old['start']==w['start']and old['final']==w['final'];assert len(moves)==20
out.mkdir(parents=True,exist_ok=False);raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();data=gzip.compress(raw,compresslevel=9,mtime=0);data=data[:9]+bytes([255])+data[10:];(out/'WORD.json.gz').write_bytes(data)
r=dict(status='PASS_EXACT_PRUNED_TRACE20',source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(data).hexdigest(),moves=moves,all_dirty_columns=N,profile_before=dict(h0),profile_after=dict(h1),profile_delta=delta,paid_profile_with_retained_copies=dict(h1+Counter(c1)),retained_total_ranks=c1,cleanup_literal_inverse=True)
(out/'REVIEW.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(r))
