"""Read and independently replay stored full-target route opcodes and coefficients."""
import gzip,json,hashlib,time,sys
from pathlib import Path
from collections import Counter
import numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bucketed as b

def replay(path,P,addresses):
 result=b.load_receipt(path);S=result['source_ports'];T=result['target_ports'];ns=len(S);nh=result['helper_count'];nt=len(T)
 proof_sha256=b.proof_payload_binding(path,result)
 raw=P[T]@P[S].T;b.need(not (raw%4).any(),'route integral pairings');t=raw//4
 expected=4*t-t*t*t
 for row,target in enumerate(T):
  for col,source in enumerate(S):
   if target==source:expected[row,col]+=48
 b.need(expected.tolist()==result['coefficient_numerators'],'actual all coefficient entries')
 b.need(result['coefficients_denominator']==48,'coefficient denominator')
 positions={int(p):i for i,p in enumerate(T)}
 frames={f's{i}':b.span([int(addresses[p])]) for i,p in enumerate(S)}
 frames.update({f'h{i}':() for i in range(nh)});frames.update({f't{p}':() for p in T})
 paths={r:[] for r in frames}
 # Implicit identity target columns avoid allocating nt-square storage.
 H=np.concatenate((np.zeros((nh,ns),dtype=np.int64),np.eye(nh,dtype=np.int64)),axis=1)
 Y=np.zeros((nt,ns+nh),dtype=np.int64)
 dual=np.zeros((ns+nh,ns+nh+nt),dtype=np.int64);dual[:,:ns+nh]=48*np.eye(ns+nh,dtype=np.int64)
 network=path.parent/result['expanded_network_gzip_filename'];digest=hashlib.sha256();counts=Counter();frame_cache={}
 with gzip.open(network,'rb') as stream:
  for payload in stream:
   digest.update(payload);event=json.loads(payload);op=event['op'];counts[op]+=1
   if op=='climb':
    register=event['register'];new=tuple(event['frame']);old=frames[register]
    if new not in frame_cache:
     b.need(new==b.span(new),'canonical route frame');frame_cache[new]=True
    b.need(b.inside(old,new),'nested ordinary route climb')
    d=len(new)-len(old)
    if d:paths[register].append(d)
    frames[register]=new
   elif op=='add':
    a,z=event['dst'],event['src'];n=event['numerator'];d=event['denominator']
    b.need(a in frames and z in frames and frames[a]==frames[z],'route common current frame')
    if a.startswith('t'):
     b.need(z.startswith('h') and d==48,'route scatter form')
     row=positions[int(a[1:])];lane=int(z[1:]);Y[row]+=n*H[lane]
     dual[ns+lane,ns+nh+row]-=n
    else:
     b.need(a.startswith('h') and z.startswith('s') and d==1,'route gather form')
     lane=int(a[1:]);source=int(z[1:]);H[lane,source]+=n;dual[source]-=n*dual[ns+lane]
   else:raise ValueError('unrecognized route opcode '+op)
 b.need(sum(counts.values())==result['expanded_event_count'],'route event count')
 b.need(digest.hexdigest()==result['expanded_network_sha256'],'expanded route payload binding')
 b.need(np.array_equal(Y[:,:ns],expected) and not Y[:,ns:].any(),'forward all-column source/dirty block')
 b.need(not H[:,:ns].any() and np.array_equal(H[:,ns:],np.eye(nh,dtype=np.int64)),'forward helper restoration')
 b.need(np.array_equal(dual[:,:ns+nh],48*np.eye(ns+nh,dtype=np.int64)),'same-order dual source/helper block')
 b.need(np.array_equal(dual[:ns,ns+nh:],-expected.T) and not dual[ns:,ns+nh:].any(),'same-order dual target/helper block')
 for r,frame in frames.items():
  want=b.cap(int(addresses[int(r[1:])])) if r.startswith('t') else b.FULL
  b.need(frame==want,'route endpoint')
 mass=sum(sum(p) for p in paths.values());b.need(mass==result['total_local_transition_rank'],'route transition mass')
 b.need(counts['add']==2*np.count_nonzero(expected)+2*nh,'route scalar ADD count')
 return {'status':'PASS_INDEPENDENT_STORED_ROUTE_REPLAY','artifact':str(network.relative_to(b.ROOT)),
         'source_ports':ns,'target_ports':nt,'ordinary_helpers':nh,'all_input_columns':ns+nh+nt,
         'event_count':sum(counts.values()),'ADD_count':counts['add'],'CLIMB_count':counts['climb'],
         'transition_rank':mass,'arbitrary_dirt_forward_and_same_order_dual':'PASS',
         'expanded_sha256':digest.hexdigest(),'receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'canonical_receipt_proof_sha256':proof_sha256}

def main():
 started=time.monotonic();roots,_,ports,profiles=b.geometry.construct_shell();P=ports[(profiles&4)==0,:16].astype(np.int64)
 _,addresses,_=b.geometry.binary_labels(roots,P)
 results=[replay(b.PKG/'routes'/name,P,addresses) for name in ('RESULT.json','MASK-2-RESULT.json','MASK-4-RESULT.json')]
 out={'status':'PASS_ALL_THREE_STORED_ROUTE_NETWORKS','routes':results,'elapsed_seconds':time.monotonic()-started,
      'storage_source_sha256':hashlib.sha256((b.PKG/'artifact.py').read_bytes()).hexdigest(),
      'scope':'Fully stored finite route streams and all independent source/target/helper columns, scalar and common-frame chronology. Standalone compensation blocks; no free K composition, full circuit or supplier admission.'}
 (Path(__file__).with_name('ROUTES.json')).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()
