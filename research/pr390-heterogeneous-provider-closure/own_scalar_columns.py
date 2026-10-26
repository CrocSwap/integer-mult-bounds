"""Fresh independent literal reconstruction and column-wise rational replay.

All input programs remain inert. This file reads only the three literal JSON
inputs and implements the printed scalar/chronological specification itself.
Each completed column block is saved and reused after interruption.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import argparse,datetime,gzip,hashlib,json

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'literal'
OUT=ROOT/'own-scalar-results';OUT.mkdir(exist_ok=True)
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def load(n):
 b=(DATA/n).read_bytes();return json.loads(gzip.decompress(b) if n.endswith('.gz') else b)
def span_rank(vectors):
 piv={}
 for v in vectors:
  while v:
   bit=v.bit_length()-1
   if bit not in piv:piv[bit]=v;break
   v^=piv[bit]
 return len(piv)

cert=load('prefix18.json.gz');pre=load('prewhite.json');sinks=load('sink-audit.json')
frames=cert['frames'];ports=cert['ports'];width=2*cert['v']+cert['R'];v=cert['v']
require((cert['h'],v,cert['R'],width)==(9,120,783,1023),'wrong literal dimensions')
require(len(frames)==948 and all(span_rank(f)==len(f) for f in frames),'dependent frame')
require(set(ports)=={q for q in range(512) if bin(q).count('1') in (3,7)},'incorrect E8 port stock')
require(all(frames[cert['start'][j]]==[q] for j,q in enumerate(ports)),'wrong source entry frame')
require(all(cert['start'][j]==0 for j in range(v,width)),'preconditioning not in common base')
require(frames[1]==[256,128,64,32,16,8,4,2,1],'full frame is not a coordinate permutation')
for j,q in enumerate(ports):
 target=frames[cert['final'][v+j]]
 require(len(target)==8 and span_rank(target)==8 and all(bin(u&q).count('1')%2==0 for u in target),'target exit not q-perp')
for helper in range(2*v,width):
 require(cert['final'][helper]==1,'ordinary helper exit not frame 1 before sink override')
for row in sinks['accepted']:
 q=ports[{355:84,403:99}[row['sink_helper']]]
 require((row['sink_helper'],row['frame'],q) in [(355,206,508),(403,221,499)],'sink identity changed')
 target=frames[row['frame']]
 require(len(target)==8 and span_rank(target)==8 and all(bin(u&q).count('1')%2==0 for u in target),'sink exit not q-perp')

sink_by_cut={r['cut_group']:r for r in sinks['accepted']}
require({r['sink_helper'] for r in sink_by_cut.values()}=={355,403},'sink stock differs')

def reconstruct(backward):
 current=cert['start'][:];exit_frames=cert['final'][:]
 for r in sinks['accepted']:exit_frames[r['sink_helper']]=r['frame']
 operations=[];edges=Counter();children=Counter();centre_calls=0
 def advance(role,new):
  old=current[role]
  if old==new:return
  require(len(frames[old])<len(frames[new]),'nonascending ordinary frame walk')
  require(span_rank(frames[old]+frames[new])==len(frames[new]),'nonnested frame walk')
  r=len(frames[new])-len(frames[old]);current[role]=new;edges[old,new]+=1;children[r]+=1
 def shear(dst,src,a,b,common=None):
  require(dst!=src and a!=0 and b>0,'invalid shear')
  if common is not None:
   require((dst>=width or current[dst]==common) and (src>=width or current[src]==common),'unequal exact frame IDs')
  if backward:dst,src,a=src,dst,-a
  operations.append((dst,src,a,b))
 for key in ['pre_target_dirty_cancellation_gates','pre_helper_inverse_gates']:
  for dst,src,a,b in pre[key]:
   require(dst>=v and src>=v,'preconditioning reads unmatched source frame')
   shear(dst,src,a,b,0)
 group_number=0
 for phase in ['A','CENTRES','B']:
  if phase=='CENTRES':
   require(all(current[v+j]==0 for j in range(v)),'copied-centre target not in base frame')
   for slot,source,f in cert['ret']:
    scratch=width+slot;require(current[source]==f,'copied-centre source frame')
    require(slot in range(8) and f==1,'unexpected retained centre')
    operations.append((scratch,None,0,1))
    scat=[(v+j,a,b) for j,row in enumerate(cert['scat']['table']) for k,a,b in row if k==slot]
    if not backward:
     operations.append((scratch,source,1,1))
     operations.extend((target,scratch,a,b) for target,a,b in scat)
    else:
     operations.extend((scratch,target,a,b) for target,a,b in scat)
     operations.append((source,scratch,-1,1))
    operations.append((scratch,None,0,1));children[len(frames[f])]+=1;centre_calls+=1
   continue
  for group in cert[phase]:
   direction,f,anchor,terms=group[:4]
   extra=group[4] if direction=='out' else []
   require(direction in ['in','out'],'unknown group direction')
   for role in [anchor]+[term[0] for term in terms]+extra:advance(role,f)
   for role,a,b in terms:
    dst,src=(anchor,role) if direction=='in' else (role,anchor)
    shear(dst,src,a,b,f)
   r=sink_by_cut.get(group_number)
   if r:
    for role in [r['sink_helper']]+[term[0] for term in r['uncompute']]:advance(role,r['frame'])
    for role,a,b in r['uncompute']:shear(r['sink_helper'],role,a,b,r['frame'])
   group_number+=1
 require(group_number==len(cert['A'])+len(cert['B']),'group chronology length')
 for role,new in enumerate(exit_frames):advance(role,new)
 for key in ['post_source_inverse_gates','post_full_helper_clean_repair_gates']:
  for dst,src,a,b in pre[key]:
   require(dst not in [355,403] and src not in [355,403],'cleanup touches early sink')
   require(current[dst]==current[src]==1,'cleanup lacks common full frame')
   shear(dst,src,a,b,1)
 primitive=0
 for dst,src,a,b in operations:
  if src is None:primitive+=1;continue
  den=b;small=0
  for prime in [2,3]:
   while den%prime==0:den//=prime;small+=1
  require(den==1,'unsupported rational denominator')
  primitive+=3+abs(a).bit_length()+bin(abs(a)).count('1')+small
 return operations,{'children':dict(sorted(children.items())),'frame_edges':[[lo,hi,n] for (lo,hi),n in sorted(edges.items())],'frame_occurrences':sum(edges.values()),'centres':centre_calls,'scalar_adds':sum(src is not None for _,src,_,_ in operations),'scalar_clears':sum(src is None for _,src,_,_ in operations),'real_primitive_upper':2*primitive,'exit_frames':exit_frames}

def replay_column(operations,column,backward):
 vector=[Q(0)]*(width+8);vector[column]=Q(1)
 for dst,src,a,b in operations:
  if src is None:vector[dst]=Q(0)
  elif vector[src]:vector[dst]+=Q(a,b)*vector[src]
 expected=[Q(0)]*(width+8)
 if column<width:expected[column]=Q(1)
 if not backward and column<v:expected[v+column]=Q(1)
 if backward and v<=column<2*v:expected[column-v]=Q(-1)
 require(vector==expected,'wrong complete live/scratch column '+str((backward,column)))
 return hashlib.sha256(str([(j,str(x)) for j,x in enumerate(vector) if x]).encode()).hexdigest()

def main():
 modes=[]
 for backward in [False,True]:
  name='backward' if backward else 'forward';ops,invoice=reconstruct(backward)
  pin=hashlib.sha256(json.dumps(ops).encode()).hexdigest()
  (OUT/(name+'-own-word.json.gz')).write_bytes(gzip.compress(json.dumps(ops).encode(),mtime=0))
  all_columns=[]
  for start in range(0,width+8,64):
   path=OUT/(name+'-columns-%04d.json'%start)
   if path.exists():
    saved=json.loads(path.read_bytes());require(saved['word_sha256']==pin and saved['passed'],'checkpoint word drift');all_columns.extend(saved['column_digests']);continue
   stop=min(start+64,width+8);digests=[replay_column(ops,j,backward) for j in range(start,stop)]
   record={'start':start,'stop':stop,'word_sha256':pin,'passed':True,'column_digests':digests,'completed_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   path.write_text(json.dumps(record,indent=2)+'\n');all_columns.extend(digests)
   print(name,'columns',start,stop,'PASS',flush=True)
  require(len(all_columns)==1031,'incomplete all-live plus active-scratch proof')
  invoice.update(word_sha256=pin,checked_live_columns=width,checked_dirty_helper_columns=783,checked_initial_active_scratch_columns=8,complete_column_operator_sha256=hashlib.sha256(json.dumps(all_columns).encode()).hexdigest(),passed=True)
  modes.append(invoice);(OUT/(name+'-invoice.json')).write_text(json.dumps(invoice,indent=2)+'\n')
 require(modes[0]['children']==modes[1]['children'] and modes[0]['frame_edges']==modes[1]['frame_edges'],'orientation child mismatch')
 require(modes[0]['real_primitive_upper']==modes[1]['real_primitive_upper']==165748,'literal primitive count mismatch')
 report={'status':'OWN_EXACT_1031_COLUMNS_BOTH_ORIENTATIONS_PASS','histogram':modes[0]['children'],'rank_mass':sum(int(r)*n for r,n in modes[0]['children'].items()),'frame_occurrences':modes[0]['frame_occurrences'],'unique_frame_edges':len(modes[0]['frame_edges']),'orientations':modes,'candidate_or_saved_checker_executed':False,'method':'Independently reconstructed instructions and column-wise Fraction state interpreter; eight initially-dirty active scratch columns included'}
 (OUT/'OWN-SCALAR-VERDICT.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)
if __name__=='__main__':main()
