"""Isolated H5B + E1/E4 experiment. No baseline file is modified.
E1 interior and bookends are imported from pinned #7633 words.
E4 interior is #7630 E4; its exact rank-one full-chart resettlement is derived afresh.
This is candidate construction, not a proof of the inherited recursive framework.
"""
import base64,copy,gzip,hashlib,json,os,signal,sys,time
from collections import Counter
from decimal import Decimal,localcontext
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[2]
H5B=BASE/"research/hydrogen-bounded-verification-20261117"
ROOT=BASE/"macbook_handoff_pr7624/unpacked/K_handoff"
def canonical(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def load_inputs():
 h=json.loads(gzip.decompress((H5B/"word-hydrogen-frames-restored.json.gz").read_bytes()))
 s,c=[json.loads(gzip.decompress(base64.b64decode((HERE.parent/f"inputs/7633-{x}.b64").read_bytes()))) for x in ("source","candidate")]
 assert canonical(h)=="ad56c629ac587510aa59ad13fde7db3f38e08d4fc09beb70fbb839a8de17b41d"
 assert canonical(s)=="1ea66c263faa51da704d7aae944f3371400afaf5df8a56904ab96319f6554e0e"
 assert canonical(c)=="4961e5e9351fa532a51eb8ff2b534bab6acd50cfd35972027cc483810cf635c3"
 return h,s,c
def e1(w,c,shadow=1568):
 w=copy.deepcopy(w);p=w["program"]
 assert all(e[1]!=shadow and (e[0] not in ("ADD","COPY") or e[2]!=shadow) for e in p)
 pre=copy.deepcopy(c["program"][:12])
 for e in pre:
  if e[1]==1501:e[1]=shadow
  if e[0]=="ADD" and e[2]==1501:e[2]=shadow
 last=max(i for i,e in enumerate(p) if e[0] in ("ADD","COPY","SCALE") and e[-1]==3 and (e[1]==457 or (e[0]!="SCALE" and e[2]==457)))
 out=pre;replaced=0;moves=0
 for i,e in enumerate(p):
  e=list(e)
  if e==["MOVE",457,3,281,False]:
   e=["ADD",242,457,"-1",281];moves+=1
  elif e[0] in ("ADD","COPY","SCALE") and e[-1]==3:
   if e[1]==457:e[1]=shadow;replaced+=1
   if e[0]!="SCALE" and e[2]==457:e[2]=shadow;replaced+=1
  out.append(e)
  if i==last:out.append(["CLEAR",shadow,3])
 assert moves==1 and replaced==36
 out+=copy.deepcopy(c["program"][-192:])
 w["program"]=out;w["initial"][457]=281
 return w,{"shadow":shadow,"chart3_accesses":replaced,"shadow_clear_after_base_event":last,"bookends":"7633 candidate first12/last192"}
def inverse_target_covector(w,q):
 z=q[:];D=set(w["hosted"]["Dports"])
 for i,x in enumerate(w["live"]):
  y=x+112
  if i in D:z[x],z[y]=q[x]-q[y],q[y]
  else:z[x],z[y]=(q[x]-q[y])/2,q[x]+q[y]
 for x,y in zip(w["hosted"]["X2"],w["hosted"]["Y2"]):z[x],z[y]=q[x],q[x]+q[y]
 return z
def e4(w,shadow=1567):
 w=copy.deepcopy(w);out=[];counts=Counter()
 for e in w["program"]:
  if e==["MOVE",490,594,725,False]:e=["MOVE",490,594,883,False];counts["route1"]+=1
  elif e==["ADD",490,296,"1",725]:injection=len(out);e=["ADD",1427,296,"-1",725];counts["add"]+=1
  elif e==["MOVE",490,725,883,False]:counts["route2"]+=1;continue
  out.append(e)
 assert counts=={"route1":1,"route2":1,"add":1}
 n=w["public"];N=n+w["owned_fields"]
 q=[F(0)]*N;q[296]=F(1)
 for e in reversed(out[:injection]):
  op,r=e[:2]
  if op in ("INIT","CLEAR"):q[r]=F(0)
  elif op=="SCALE":q[r]*=F(e[2])
  elif op in ("ADD","COPY"):
   q[e[2]]+=F(e[3])*q[r]
   if op=="COPY":q[r]=F(0)
 v=[F(0)]*N;v[490]=v[1427]=F(-1)
 for e in out[injection+1:]:
  op,r=e[:2]
  if op in ("INIT","CLEAR"):v[r]=F(0)
  elif op=="SCALE":v[r]*=F(e[2])
  elif op in ("ADD","COPY"):
   if op=="COPY":v[r]=F(e[3])*v[e[2]]
   else:v[r]+=F(e[3])*v[e[2]]
 q=inverse_target_covector(w,q)
 assert all(not x or (i<n and w["final"][i]==127) for i,x in enumerate(q))
 assert all(not x or (i<n and w["final"][i]==127) for i,x in enumerate(v))
 inner=sum(x*y for x,y in zip(q,v));assert inner==0
 tail=[["INIT",shadow,127]]
 tail += [["ADD",shadow,i,str(x),127] for i,x in enumerate(q) if x]
 tail += [["ADD",i,shadow,str(-x),127] for i,x in enumerate(v) if x]
 tail += [["CLEAR",shadow,127]]
 w["program"]=out+tail
 return w,{"E4_injection_event":injection,"q":{str(i):str(x) for i,x in enumerate(q) if x},"v":{str(i):str(x) for i,x in enumerate(v) if x},"inner_product":str(inner),"tail_events":len(tail),"shadow":shadow,"derivation":"C=(I+v*q)A; q*v=0; append (I-v*q) using one zero-initialized full-chart accumulator"}
def moment_report(inv,n,old):
 P={int(k):v for k,v in inv["paid"].items()};T={int(k):v for k,v in inv["targets"].items()}
 for k in set(old["paid"])|set(n["paid"]):P[k]=P.get(k,0)+17*(n["paid"].get(k,0)-old["paid"].get(k,0))
 for k in set(old["helpers"])|set(n["helpers"]):T[k]=T.get(k,0)+17*(n["helpers"].get(k,0)-old["helpers"].get(k,0))
 with localcontext() as cx:
  cx.prec=70;logs={r:Decimal(r).ln() for r in T.keys()|P.keys()}
  def m(k):return sum(Decimal(T.get(r,0)-P.get(r,0))*Decimal(r)*(-k*logs[r]).exp() for r in logs)
  lo,hi=Decimal(".00368"),Decimal(".00375")
  for _ in range(200):
   mid=(lo+hi)/2
   if m(mid)>0:lo=mid
   else:hi=mid
  return {"P":P,"T":T,"crossing_decimal_estimate":str((lo+hi)/2),"moment_at_0037_decimal_estimate":str(m(Decimal(".0037"))),"not_interval_certified":True}
def main():
 os.nice(10);signal.alarm(550);sys.path.insert(0,str(BASE/"research/carbon-structural-20261116"))
 import verify_lib as vl
 h,s,c=load_inputs();w1,m1=e1(h,c);w4,m4=e4(h);wj,mj=e4(w1)
 vs={"e1":(w1,m1),"e4":(w4,m4),"joint":(wj,{"e1":m1,"e4":mj})}
 shim=[]
 ind=vl.load_py_in_memory("combo_ind",ROOT/"reference_vendor/independent.py",[("(v&q).bit_count()","bin(v&q).count(\"1\")",1),("a.bit_count()","bin(a).count(\"1\")",1)],shim)
 old=ind.native(h);assert old["bad_inputs"]==[]
 call=json.loads((vl.RET902_DIR/"bench/inputs/7113-CALLER.json").read_text());inv=json.loads((H5B/"invoice-restored.json").read_text())
 report={"baseline_hash":canonical(h),"source_original_native":"reference_vendor/independent.py semantic native engine, only two Python 3.9 popcount normalizations","platform_adapter":shim,"variants":{}}
 for tag,(w,meta) in vs.items():
  raw=gzip.compress(json.dumps(w,separators=(",",":")).encode(),mtime=0);path=HERE/f"word-{tag}.json.gz"
  with path.open("xb") as f:f.write(raw)
  t=time.monotonic();n=ind.native(w)
  item={"canonical_sha256":canonical(w),"gzip_sha256":hashlib.sha256(raw).hexdigest(),"native":n,"ordinary":vl.compute_ordinary_17call(w,call,675),"moment":moment_report(inv,n,old),"counts":dict(Counter(e[0] for e in w["program"])),"construction":meta,"seconds":time.monotonic()-t}
  report["variants"][tag]=item
  print(tag,canonical(w),"native_bad",n["bad_inputs"],"lifetime",n["lifetimes"],"peak",n["owned_peak"],"ordinary",item["ordinary"]["conservative_total"],"crossing",item["moment"]["crossing_decimal_estimate"],"moment.0037",item["moment"]["moment_at_0037_decimal_estimate"],flush=True)
 with (HERE/"quick-report.json").open("x") as f:json.dump(report,f,indent=2);f.write("\n")
if __name__=="__main__":main()
