"""Independent exact bucketed complete-K fixtures and semantic schema replay.

Only explicit K opcodes are reused from the proposed emitter. Scalar and frame
interpretation, bucket indexing, and all-column expected maps are separate.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from itertools import combinations_with_replacement
import importlib.util,sys,json,gzip,hashlib,math,time
import numpy as np
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PKG=HERE.parent;ROOT=PKG.parents[1]
storage_spec=importlib.util.spec_from_file_location('independent_receipt_storage',PKG/'artifact.py')
storage=importlib.util.module_from_spec(storage_spec);storage_spec.loader.exec_module(storage)
load_receipt=storage.load_receipt
sys.path.insert(0,str(ROOT/'research/niemeier-lattices/code'))
import e8_cubed as geometry
import e8_sections as sections
spec=importlib.util.spec_from_file_location('candidate_k',PKG/'k_encoder/network.py')
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)

def need(value,message):
 if not value:raise ValueError(message)

def proof_payload_binding(path,receipt):
 """Bind reconstructed proof fields canonically, independently of gzip bytes."""
 descriptor=json.loads(path.read_text()).get('proof_data')
 if descriptor is None:return None
 need(descriptor['format']=='canonical-json-gzip-v1','proof payload format')
 fields=descriptor['fields'];need(fields==sorted(set(fields)),'proof field inventory')
 payload=(json.dumps({field:receipt[field] for field in fields},sort_keys=True,separators=(',',':'))+'\n').encode()
 digest=hashlib.sha256(payload).hexdigest()
 need(digest==descriptor['canonical_sha256'],'independent canonical reconstructed proof binding')
 return digest

def span(words):
 piv={}
 for raw in words:
  v=int(raw)
  for p in sorted(piv,reverse=True):
   if (v>>p)&1:v^=piv[p]
  if v:
   p=v.bit_length()-1
   for q in list(piv):
    if (piv[q]>>p)&1:piv[q]^=v
   piv[p]=v
 return tuple(piv[q] for q in sorted(piv,reverse=True))

def inside(a,b):return len(span(tuple(a)+tuple(b)))==len(span(b))
FULL=span(1<<i for i in range(17))
def cap(word):
 pivot=next(i for i in range(17) if (word>>i)&1)
 return span((1<<i)|(((word>>i)&1)<<pivot) for i in range(17) if i!=pivot)
def add(dst,src,q,phase):return {'op':'add','dst':dst,'src':src,'q':str(q),'phase':phase}
def climb(r,f,phase):return {'op':'climb','register':r,'frame':list(f),'phase':phase}
def combine(a,b,q):
 out=dict(a)
 for col,val in b.items():
  out[col]=out.get(col,F(0))+q*val
  if not out[col]:del out[col]
 return out

def make_fixture(P,addresses,indices,E,W,dual):
 n=len(indices);groups={}
 for ti,p in enumerate(indices):groups.setdefault(int(addresses[p]),[]).append(ti)
 for label,members in groups.items():
  need(sorted(indices[i] for i in members)==np.flatnonzero(addresses==label).tolist(),'every selected target fiber is complete')
 lanes=[]
 for si,s in enumerate(indices):
  for label,members in sorted(groups.items()):
   if (int(addresses[s])&label).bit_count()%2:continue
   coeff={}
   for ti in members:
    target=indices[ti];raw=int(P[target]@P[s]);need(raw%4==0,'integral fixture dot')
    t=raw//4;q=F(int(target==s))-F(t**3-4*t,48)
    need(bool(q),'all bucket entries nonzero');coeff[ti]=q
   lanes.append({'source_position':si,'source_port':int(s),'target_label':label,
                 'targets':members,'coefficients':{str(i):str(q) for i,q in coeff.items()},'helper':f'h{si}_{label}'})
 def oriented(e):
  if dual and e['op']=='add':e=dict(e);e['dst'],e['src']=e['src'],e['dst'];e['q']=str(-F(e['q']))
  return e
 events=[]
 for lane in lanes:
  for ti,q in lane['coefficients'].items():events.append(oriented(add(f't{ti}',lane['helper'],-F(q),'bucket_dirt_prefix')))
 ke=list(k.k_events(E,W,dual))
 def ko(e):
  if not dual or e['op']!='add' or e['phase']=='K_private_copy_dual':return e
  e=dict(e);e['dst'],e['src']=e['src'],e['dst']
  if e['phase']!='K_scatter':e['q']=str(-F(e['q']))
  return e
 events.extend(ko(e) for e in ke if e['phase']=='K_dirt_prefix')
 for lane in lanes:
  si=lane['source_position'];h=lane['helper']
  events.extend([climb(h,span([int(addresses[indices[si]])]),'bucket_source_line'),oriented(add(h,f's{si}',F(1),'bucket_gather')),climb(h,cap(lane['target_label']),'bucket_cap')])
 events.extend(climb(f's{i}',FULL,'source_full') for i in range(n))
 events.extend(ko(e) for e in ke if e['phase']!='K_dirt_prefix')
 events.extend(climb(f't{i}',cap(int(addresses[p])),'target_cap') for i,p in enumerate(indices))
 for lane in lanes:
  for ti,q in lane['coefficients'].items():events.append(oriented(add(f't{ti}',lane['helper'],F(q),'bucket_scatter')))
 for lane in lanes:
  events.append(climb(lane['helper'],FULL,'bucket_helper_full'))
  events.append(oriented(add(lane['helper'],f"s{lane['source_position']}",F(-1),'bucket_cleanup')))
 starts={f's{i}':list(span([int(addresses[p])])) for i,p in enumerate(indices)}
 starts.update({f't{i}':[] for i in range(n)});starts.update({f'c{i}':[] for i in range(816)})
 starts.update({lane['helper']:[] for lane in lanes})
 return {'indices':indices,'dual':dual,'lanes':lanes,'starts':starts,'events':events}

def interpret(f,addresses):
 frames={r:tuple(v) for r,v in f['starts'].items()};rows={r:{r:F(1)} for r in frames}
 paths={r:[] for r in frames};private=set();private_ranks=[];opcounts=Counter();phases=Counter();peak=0
 for e in f['events']:
  op=e['op'];opcounts[op]+=1;phases[e['phase']]+=1
  if op=='private_begin':
   r=e['register'];need(not private and r not in rows,'private begin/lifetime')
   private.add(r);peak=max(peak,len(private));frames[r]=tuple(e['frame']);rows[r]={}
   need(frames[r] in ((),FULL),'private entrance frame')
  elif op=='private_end':
   r=e['register'];need(private=={r},'private erasure/lifetime');private.remove(r);del frames[r];del rows[r]
  elif op=='private_transition':
   r=e['register'];new=tuple(e['frame']);need(private=={r},'private transition ownership')
   need(set((len(frames[r]),len(new)))=={0,17} and e['rank']==17,'private rank transition')
   frames[r]=new;private_ranks.append(17)
  elif op=='climb':
   need(not private,'ordinary climb during private episode')
   r=e['register'];new=tuple(e['frame'])
   need(len(span(new))==len(new) and inside(frames[r],new),'ordinary frame inclusion')
   d=len(new)-len(frames[r]);need(d>0,'ordinary strict climb');paths[r].append(d);frames[r]=new
  elif op=='add':
   a,b=e['dst'],e['src'];need(a!=b and a in rows and b in rows,'ADD register references')
   need(span(frames[a])==span(frames[b]),'ADD common current frame')
   rows[a]=combine(rows[a],rows[b],F(e['q']))
  else:raise ValueError('unrecognized opcode '+op)
 need(not private and opcounts['private_begin']==opcounts['private_end']==816,'complete private lifecycle')
 wanted={r:{r:F(1)} for r in f['starts']}
 for i in range(len(f['indices'])):
  a,b,q=(f's{i}',f't{i}',F(-1)) if f['dual'] else (f't{i}',f's{i}',F(1))
  wanted[a]=combine(wanted[a],wanted[b],q)
 need(rows==wanted,'exact all-column identity shear or restoration')
 for r in frames:
  expected=cap(int(addresses[f['indices'][int(r[1:])]])) if r.startswith('t') else FULL
  need(span(frames[r])==expected,'endpoint frame')
  need(paths[r]==([16] if r[0] in 'st' else [17] if r.startswith('c') else [1,15,1]),'exact emitted profile')
 edges=sum(len(lane['targets']) for lane in f['lanes']);R=len(f['lanes']);n=len(f['indices'])
 compadds=sum(count for phase,count in phases.items() if phase in ('bucket_dirt_prefix','bucket_gather','bucket_scatter','bucket_cleanup'))
 need(compadds==2*edges+2*R,'bucket ADD count')
 M=sum(count for phase,count in phases.items() if phase=='K_gather')
 need(opcounts['add']==2*edges+2*R+4*M+816,'complete ADD count')
 mass=sum(sum(path) for path in paths.values())
 need(mass==32*n+17*R+17*816,'complete ordinary mass')
 need(sum(private_ranks)==17*816,'private descent mass')
 need(len(f['events'])==2*edges+5*R+2*n+4*M+5*816,'complete event count')
 return {'status':'PASS_ALL_COLUMNS_BUCKETED_COMPLETE_K','ports':n,'dual':f['dual'],'helper_count':R,'edge_fallback_helpers':edges,
         'ordinary_rank_mass':mass,'private_rank_mass':sum(private_ranks),'private_episode_peak':peak,'all_input_columns':len(rows),
         'ADD_count':opcounts['add'],'event_count':len(f['events']),'compensation_ADD_count':compadds,'opcode_counts':dict(opcounts)}

def main():
 started=time.monotonic();roots,_,shell,profiles=geometry.construct_shell();P=shell[(profiles&4)==0,:16].astype(np.int64)
 _,addresses,_=geometry.binary_labels(roots,P)
 A,W,_=k.polynomial_certificate();E,w,q=sections.evaluate_operator_centers(P)
 need(q==8192 and np.array_equal(w,W),'factor evaluator weights')
 mono=list(combinations_with_replacement(range(16),3))
 D=np.array([6//math.prod(math.factorial(c) for c in Counter(m).values()) for m in mono],dtype=np.int64)
 U=np.zeros((816,16),dtype=np.int64)
 for row,m in enumerate(mono):
  for i in range(16):
   U[row,i]=int(any(tuple(sorted((i,j,j)))==m for j in range(16)))
 need(np.array_equal(A.T@(W[:,None]*A),384*np.diag(D)-96*(U@U.T)),'all polynomial certificate entries')
 # Bind every evaluator feature to the homogeneous polynomial certificate,
 # using sparse terms; this replaces the candidate's sampled binding.
 checked=0
 for c in range(816):
  value=np.zeros(len(P),dtype=np.int64)
  for j in np.flatnonzero(A[c]):value+=int(A[c,j])*np.prod(P[:,mono[j]],axis=1)
  need(np.array_equal(value,12*E[:,c]),'all-port feature/certificate binding')
  checked+=len(P)
 factor={'status':'PASS_COMPLETE_POLYNOMIAL_IDENTITY_AND_EVALUATOR_BINDING','polynomial_entries':816**2,
         'actual_feature_entries_bound':checked,'identity':'384 cubic multinomial diagonal -96 norm-lift product; divide by12^2*8192; squared doubled norms16',
         'A_sha256':hashlib.sha256(A.astype('<i8').tobytes()).hexdigest(),'weights_sha256':hashlib.sha256(W.astype('<i8').tobytes()).hexdigest()}
 receipts=[];controls={}
 for n in (8,32):
  reps=[2160,2162,2164,2166] if n==8 else [0,3,287,288]
  indices=[int(i) for rep in reps for i in np.flatnonzero(addresses==addresses[rep])]
  need(len(indices)==n,'duplicate-label fixture size')
  Ef=E[indices];need(np.array_equal((Ef*W)@Ef.T,((P[indices]@P[indices].T//4)**3-4*(P[indices]@P[indices].T//4))*8192//48),'fixture complete K factor')
  for dual in (False,True):
   f=make_fixture(P,addresses,indices,Ef,W,dual);receipt=interpret(f,addresses)
   payload=json.dumps(f,sort_keys=True,separators=(',',':')).encode();name=f'fixture-{n}-'+('dual' if dual else 'forward')+'.json.gz'
   (HERE/name).write_bytes(gzip.compress(payload,mtime=0));receipt.update(artifact=name,uncompressed_sha256=hashlib.sha256(payload).hexdigest());receipts.append(receipt)
   if n==8:
    for phase in ('bucket_scatter','bucket_gather','bucket_cleanup','K_private_erase'):
     index=next(i for i,e in enumerate(f['events']) if e['phase']==phase)
     mutation=list(f['events'])
     if phase=='bucket_scatter':mutation[index]=dict(mutation[index],q=str(2*F(mutation[index]['q'])))
     else:del mutation[index]
     try:interpret(dict(f,events=mutation),addresses)
     except (ValueError,KeyError) as error:controls[f'{n}:{dual}:{phase}']=str(error)
     else:raise ValueError('negative control accepted '+phase)
    index=next(i for i,e in enumerate(f['events']) if e['phase']=='bucket_gather')
    mutation=list(f['events']);wrong=dict(mutation[index])
    wrong['dst' if dual else 'src']='s1';mutation[index]=wrong
    try:interpret(dict(f,events=mutation),addresses)
    except (ValueError,KeyError) as error:controls[f'{n}:{dual}:wrong_source']=str(error)
    else:raise ValueError('wrong source negative control accepted')
 schema=json.loads((PKG/'routes/BUCKETED-SCHEMA.json').read_text());labels,counts=np.unique(addresses,return_counts=True)
 parity=np.array([x.bit_count()%2 for x in range(1<<17)],dtype=np.uint8);R=0;edges=0
 fullscreen=load_receipt(PKG/'routes/FULL-MASK-SCREEN.json')
 cap_proof_sha256=proof_payload_binding(PKG/'routes/FULL-MASK-SCREEN.json',fullscreen)
 need(fullscreen['labels']==labels.tolist(),'full cap witness label inventory')
 for i,label in enumerate(labels):
  neighbor=parity[np.bitwise_and(labels,label)]==0
  R+=int(counts[i])*int(neighbor.sum());edges+=int(counts[i])*int(counts[neighbor].sum())
  witness=fullscreen['cap_span_witness_label_indices'][i]
  need(all(neighbor[j] for j in witness) and span(labels[witness])==cap(int(label)),'independent cap span witness')
 need(R==schema['helper_count']==227312640 and edges==schema['actual_nonzero_source_target_entries']==480337920,'full bucket/edge recount')
 full={'helper_count':R,'weighted_edges':edges,'compensation_ADD_count':2*edges+2*R,'helper_CLIMB_count':3*R,
       'source_target_CLIMB_count':2*len(P),'standalone_compensation_total_events':2*edges+5*R+2*len(P),
       'helper_transition_rank':17*R,'total_compensation_and_data_transition_rank':17*R+32*len(P)}
 for key,value in full.items():
  if key in schema:need(schema[key]==value,'full schema arithmetic '+key)
 full['status']='PASS_FULL_COMPRESSED_SCHEMA_ARITHMETIC_AND_CAP_WITNESSES'
 full['full_opcode_stream_executed']=False
 full['canonical_cap_proof_sha256']=cap_proof_sha256
 out={'status':'PASS_INDEPENDENT_BUCKETED_COMPLETE_K_FIXTURES_AND_FULL_SCHEMA','factor':factor,'fixtures':receipts,'negative_controls':controls,
      'full_schema':full,'elapsed_seconds':time.monotonic()-started,
      'scope':'Fully emitted 8/32-port bucketed complete K plus compensation words, exact arbitrary-dirt and frame replay in both orientations. Full-size counts and finite factor proof only; no execution of billion-event stream, physical compiler, helper-bank admission, precision or kappa claim.',
      'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),PKG/'artifact.py',PKG/'k_encoder/network.py',PKG/'routes/BUCKETED-SCHEMA.json',ROOT/'research/niemeier-lattices/code/e8_sections.py',ROOT/'research/niemeier-lattices/code/e8_cubed.py')}}
 (HERE/'RESULT.json').write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps({'status':out['status'],'elapsed_seconds':out['elapsed_seconds'],'fixtures':receipts,'full_schema':full},sort_keys=True))

if __name__=='__main__':main()
