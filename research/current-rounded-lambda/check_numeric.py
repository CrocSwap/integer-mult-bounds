"""Bounded complete composition, direct address/Gaussian integer oracle."""
from pathlib import Path
import json,sys,time,hashlib
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from lambda_provider import LambdaProvider,S,M
from source_binding import need
from check_fixture import factory,header_bits,encode,endpoint
from ordinary import Ordinary

def load(t,body):t.cells[t.origin:]=bytearray(body);t.head=t.origin;t.high=max(t.high,t.origin+len(body))
def body(t):
 out=[]
 for x in t.cells[t.origin:]:
  if x==6:break
  out.append(x)
 return out

def run_case(rank=1,q=1,sign=1,f=1,h=3,late=False,*,reuse=None):
 recipe=dict(matrix_rows=tuple(1<<i for i in range(rank)),offset=q,linear_Z4=(0,)*rank,quadratic_rows=(0,)*rank,phase=0)
 a=3+rank*f;record=6*(h+1)
 values=dict(outer=1,rows=1,stock=1,row_bits=(1<<a)*record,within_bits=a,record_bits=record,p=max(2,rank*f),d=rank*f,K=1,G=1,H=1,q0=3,qF=0,qB=0,D=rank*f,f=f,rho=0,active_start=2,back_start=2+rank*f,selected_axes=rank*f,entry_start=2,remainder=0,cutoff=rank)
 records=[(0,0)]*(1<<a)
 if late:
  need(h==3,'late fixture width');last=len(records)-1;partner,_=endpoint(last,values,recipe);records[last]=(1,-3);records[partner]=(1,3)
 else:records[0]=(1,0);records[-1]=(-1,0)
 rounded=[]
 for address,x in enumerate(records):
  to,phase=endpoint(address,values,recipe);need(phase==0,'pure source translation')
  y=records[to];ar,ai=x;cr,ci=y
  rounded.append(((ar-sign*ai+cr+sign*ci+1)//2,(ai+sign*ar+ci-sign*cr+1)//2))
 fits=all(-(1<<(h-1))<=z<(1<<(h-1)) for r in rounded for z in r)
 initial=encode([(z,) for z in records],h);expected=encode([(z,) for z in rounded],h) if fits else initial
 if reuse is None:
  owner=LambdaProvider(q,sign,factory,rank=rank);work=[S.codec.DenseTape(3+i%5) for i in range(owner.port_count)];field=S.codec.DenseTape(9);context=S.codec.DenseTape(11)
  owner.bind(work,S.abi.CodedPort(field),S.abi.BinaryContextPort(context))
 else:owner,work,field,context=reuse
 load(field,initial);load(context,header_bits(values))
 load(work[0],[1,0]*19);work[0].head+=31;load(work[1],[0,1]*7);work[1].head+=8
 tapes=(*work,field,context);ancestors=[bytes(t.cells[:t.origin]) for t in tapes];before=sum(t.actions() for t in tapes);start=time.monotonic()
 old=Ordinary.run
 def forbidden(*a,**k):raise ValueError('ordinary-runtime-entry-trap')
 Ordinary.run=forbidden;error=None
 try:
  try:owner.run()
  except ValueError as exc:error=str(exc)
 finally:Ordinary.run=old
 need((error is None)==fits,'complete Lambda range oracle')
 if not fits:need(error=='Lambda signed range or canonical format','named arithmetic failure')
 need(body(field)==expected,'complete direct Gaussian/permutation endpoint')
 need(body(context)==header_bits(values),'complete parent header preserved')
 need(all(t.head==t.origin for t in tapes),'success/failure wrapper heads restored')
 need(all(not body(t) for t in work),'all owned bodies retired including failed partial copy')
 need([bytes(t.cells[:t.origin]) for t in tapes]==ancestors,'protected ancestors')
 need(not any(owner.translation.native.engine.compact.calls.values()),'zero ordinary/Compact runtime invocations')
 result=dict(rank=rank,q=q,sign=sign,f=f,width=h,records=len(records),accepted=fits,error=error,physical_actions=sum(t.actions() for t in tapes)-before,owned_ports=owner.port_count,materialized_private_cells=sum(len(t.cells) for t in work),endpoint_sha256=hashlib.sha256(bytes(body(field))).hexdigest(),ordinary_runtime_calls=0,elapsed_seconds=round(time.monotonic()-start,6),actual_source_nine_axis=(rank==9))
 return result,(owner,work,field,context)

if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'small'
 if mode=='source':r,_=run_case(9,11,1,1,2)
 elif mode=='late':r,_=run_case(late=True)
 elif mode=='inverse-sign':r,_=run_case(sign=-1)
 else:r,_=run_case()
 print(json.dumps(r,sort_keys=True),flush=True)
