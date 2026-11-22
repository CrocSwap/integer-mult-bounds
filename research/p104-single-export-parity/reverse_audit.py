#!/usr/bin/env python3
"""Single-readout chart-510 substitutions: all surviving pre-MOVE one-owner recodes.

No non-stdlib imports. Default source is a copy of the graph blob from exact
commit 99878b566bfcce80ef7ae2650a1231a203361445; it is checked by both gzip
and expanded SHA-256. Original clocks are preserved as stable labels.
"""
import gzip,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
GZIP_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
EXPANDED_SHA='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'
A=(2336,2344,2416,2439,2448,2451,2482,2655,2698)
B=(2359,2362,2372,2394,2397,2408,2416,2419,2425,2431,2434,2465,2484,2518,2530,2571,2576,2584,2600,2617,2623,2626,2778)

def digest(data): return hashlib.sha256(data).hexdigest()
def load(path):
 raw=Path(path).read_bytes()
 if digest(raw)!=GZIP_SHA: raise ValueError('compressed input SHA mismatch')
 expanded=gzip.decompress(raw)
 if digest(expanded)!=EXPANDED_SHA: raise ValueError('expanded input SHA mismatch')
 graph=json.loads(expanded)
 assert graph['public']==630 and len(graph['program'])==39600 and len(graph['frames'])==636
 assert graph['program'][10034:10040]==[
  ['INIT',2828,510],['ADD',2828,2337,510],['MOVE',2828,510,1],
  ['INIT',2829,510],['ADD',2829,2335,510],['MOVE',2829,510,1]]
 return graph

def bits(x): return [i for i in range(x.bit_length()) if x>>i&1]
def rowxor(it):
 z=0
 for x in it:z^=x
 return z

class Basis:
 def __init__(self,seq=()):
  self.b={}
  for lab,row in seq:self.add(lab,row)
 def add(self,lab,row):
  # Provenance is a frozenset of physical source labels (cancels repeated labels).
  cert=frozenset((lab,))
  while row:
   p=row.bit_length()-1
   if p not in self.b:self.b[p]=(row,cert);return
   a,c=self.b[p];row^=a;cert=cert.symmetric_difference(c)
 def get(self,row):
  cert=frozenset()
  while row:
   p=row.bit_length()-1
   if p not in self.b:return None
   a,c=self.b[p];row^=a;cert=cert.symmetric_difference(c)
  return sorted(cert,key=repr)

def changed(P,which):
 assert which in ('a','b')
 lo,hi,owner,donors=(10037,10040,2829,A) if which=='a' else (10034,10037,2828,B)
 new=[(f'{which}:init',['INIT',owner,1])]+[(f'{which}:add:{j}',['ADD',owner,d,1]) for j,d in enumerate(donors)]
 return [(i,row) for i,row in enumerate(P[:lo])]+new+[(i,row) for i,row in enumerate(P[hi:],hi)]

def trace(G,tape,inject=None):
 n=G['public']; frames=dict(enumerate(G['start'])); v={i:1<<i for i in range(n)}
 retired=[]
 for clk,(op,d,*args) in tape:
  if inject is not None and clk==inject[0]:
   assert op=='MOVE';v[d]^=inject[1]
  if op=='INIT': assert d not in frames;frames[d]=args[0];v[d]=0
  elif op=='MOVE': assert frames[d]==args[0];frames[d]=args[1]
  elif op=='ADD': s,c=args; assert frames[d]==frames[s]==c;v[d]^=v[s]
  elif op=='SWAP':s=args[0];frames[d],frames[s]=frames[s],frames[d];v[d],v[s]=v[s],v[d]
  elif op=='CLEAR': assert frames.pop(d)==args[0];retired.append((d,args[0],v.pop(d)))
  else:raise ValueError(op)
 assert frames==dict(enumerate(G['final']))
 return [v[i] for i in range(n)],retired

def signatures(G,tape):
 n=G['public'];frames=dict(enumerate(G['final']));v={i:1<<i for i in range(n)};result={}
 for clk,(op,d,*args) in reversed(tape):
  if op=='CLEAR':assert d not in frames;frames[d]=args[0];v[d]=0
  elif op=='MOVE':
   assert isinstance(clk,int) and frames[d]==args[1]
   result[clk]=(v[d],d,args[0],args[1]);frames[d]=args[0]
  elif op=='ADD':s,c=args;assert frames[d]==frames[s]==c;v[s]^=v[d]
  elif op=='SWAP':s=args[0];frames[d],frames[s]=frames[s],frames[d];v[d],v[s]=v[s],v[d]
  elif op=='INIT': assert frames.pop(d)==args[0];del v[d]
  else:raise ValueError(op)
 assert frames==dict(enumerate(G['start']))
 return result,[v[i] for i in range(n)]

def forward_screen(G,tape,signature,residual,wanted):
 n=G['public'];frames=dict(enumerate(G['start']));v={i:1<<i for i in range(n)}
 hist=defaultdict(Basis); serial=0
 def record(c,row):
  nonlocal serial
  # Deduplicating on insertion controls history-space memory. Label is a
  # (clock, serial) snapshot, and means retaining its full field for free.
  hist[c].add((current,serial),row);serial+=1
 current='initial'
 for i in range(n):record(frames[i],v[i])
 report=[];live_hits=[];owner_hits=[];history_hits=[]
 for current,(op,d,*args) in tape:
  if op=='MOVE' and signature[current][0]==wanted:
   src=frames[d]; assert src==args[0]
   donors=[(i,v[i]) for i in sorted(frames) if frames[i]==src and i!=d]
   current_basis=Basis(donors)
   witness=current_basis.get(residual)
   with_owner=current_basis.get(residual^v[d])
   owner_witness=None if with_owner is None else sorted(with_owner+[d])
   historical=hist[src].get(residual)
   rec={'clock':current,'owner':d,'source_chart':src,'target_chart':args[1],
        'live_donor_count':len(donors),'live_span_rank':len(current_basis.b),
        'live_hit':witness is not None,'live_witness':witness,
        'owner_overgrant_hit':witness is not None or owner_witness is not None,
        'owner_overgrant_witness':witness if witness is not None else owner_witness,
        'history_rank':len(hist[src].b),'history_hit':historical is not None,
        'history_witness':historical}
   report.append(rec)
   if witness is not None:live_hits.append(rec)
   elif owner_witness is not None:owner_hits.append(rec)
   if historical is not None:history_hits.append(rec)
  if op=='INIT':assert d not in frames;frames[d]=args[0];v[d]=0
  elif op=='MOVE':assert frames[d]==args[0];frames[d]=args[1]
  elif op=='ADD':s,c=args;assert frames[d]==frames[s]==c;v[d]^=v[s]
  elif op=='SWAP':s=args[0];frames[d],frames[s]=frames[s],frames[d];v[d],v[s]=v[s],v[d];record(frames[s],v[s])
  elif op=='CLEAR':assert frames.pop(d)==args[0];del v[d]
  else:raise ValueError(op)
  if d in frames:record(frames[d],v[d])
 assert frames==dict(enumerate(G['final']))
 return report,live_hits,owner_hits,history_hits

def apply(rows, v):
 return sum(((row&v).bit_count()&1)<<i for i,row in enumerate(rows))

def transposition_check(forward,dual):
 return all(((forward[o]>>i)&1)==((dual[i]>>o)&1)
            for o in range(630) for i in range(630))

def insert_before(tape,clock,extra):
 out=[];seen=0
 for label,row in tape:
  if label==clock: out.extend(extra);seen+=1
  out.append((label,row))
 assert seen==1
 return out

def positive_control(G,tape,reference):
 # A deliberate legal fault, using an actually live, separate donor at chart 0
 # on the unchanged first MOVE. The exact same local ADD cancels it. This is
 # a scanner test, not a claimed repair of either target rank-one defect.
 fault=['ADD',630,223,0]
 faulty=insert_before(tape,2,[('control:fault',fault)])
 bad,_=trace(G,faulty)
 sig,dual=signatures(G,faulty)
 target=sig[2][0];residual=1<<223
 assert target and all((a^b)==(residual if target>>i&1 else 0)
                       for i,(a,b) in enumerate(zip(reference,bad)))
 report,live,owner,hist=forward_screen(G,faulty,sig,residual,target)
 own=[x for x in live if x['clock']==2]
 assert own and 630 not in own[0]['live_witness']
 repaired=insert_before(faulty,2,[('control:repair',fault)])
 assert trace(G,repaired)[0]==reference
 # Donor 224 is also live at chart 0 but is the wrong correction.
 wrong=insert_before(faulty,2,[('control:wrong',['ADD',630,224,0])])
 assert trace(G,wrong)[0]!=reference
 return {'clock':2,'owner':630,'sender_chart':0,'corrupt_donor':223,
         'legal_witness':own[0]['live_witness'],'bad_control_donor':224,
         'matching_slots':len(report),'legal_live_hits':len(live),
         'exact_tape_repaired':True,'wrong_donor_rejected':True}

def main():
 path=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'strong-bit.json.gz'
 G=load(path);P=G['program'];old=list(enumerate(P));base,old_clears=trace(G,old)
 assert base==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
 # The explicit 630x630 baseline operator is an involution, so multiplying
 # a row by these rows really computes that row times M^{-1}.
 assert all(rowxor(base[i] for i in bits(row))==1<<o for o,row in enumerate(base))
 old_sig,base_dual=signatures(G,old)
 assert transposition_check(base,base_dual) and len(old_sig)==2803
 result={'source':{'commit':'99878b566bfcce80ef7ae2650a1231a203361445',
                    'compressed_sha256':GZIP_SHA,'expanded_sha256':EXPANDED_SHA,
                    'read_mode':'local graph file verified by SHA-256; no non-stdlib imports'},
         'branches':{}}
 for which in ('a','b'):
  tape=changed(P,which); forms,clears=trace(G,tape)
  assert [(r,c) for r,c,v in old_clears]==[(r,c) for r,c,v in clears]
  assert len(clears)==3433 and sum(bool(v) for _,_,v in clears)==3433
  dims={int(i):f['dim'] for i,f in G['frames'].items()}
  def move_hist(t):
   return Counter(abs(dims[row[2]]-dims[row[3]]) for _,row in t if row[0]=='MOVE')
  before_hist,after_hist=move_hist(old),move_hist(tape)
  assert before_hist-after_hist==Counter({1:1}) and not after_hist-before_hist
  old_ops=Counter(row[0] for _,row in old);new_ops=Counter(row[0] for _,row in tape)
  assert new_ops-old_ops==Counter({'ADD':8 if which=='a' else 22})
  assert old_ops-new_ops==Counter({'MOVE':1})
  delta=[a^b for a,b in zip(base,forms)]
  nz=set(delta)-{0}; assert len(nz)==1
  residual=next(iter(nz)); wanted=sum((bool(x))<<i for i,x in enumerate(delta))
  assert residual and wanted
  sigs,dual=signatures(G,tape)
  assert len(sigs)==2802 and transposition_check(forms,dual)
  ell=rowxor(base[i] for i in bits(residual))
  assert ell==residual and ((ell&wanted).bit_count()&1)==1
  assert all(G['start'][i]==0 and G['final'][i]==1 for i in bits(ell))
  collision=apply(base,wanted)
  assert apply(forms,collision)==0 and apply(base,collision)==wanted
  assert (residual&collision).bit_count()&1
  assert rowxor(forms[i] for i in bits(ell))==0
  assert rowxor(base[i] for i in bits(ell))==residual
  odd=[clock for clock,(sig,*_) in sigs.items() if (sig&ell).bit_count()&1]
  assert not odd
  span=Basis((clock,row[0]) for clock,row in sigs.items())
  assert len(span.b)==629 and span.get(wanted) is None
  assert len(Basis(enumerate(forms)).b)==629
  matches=[(i,*row[1:]) for i,row in sorted(sigs.items()) if row[0]==wanted]
  report,live,owner,hist=forward_screen(G,tape,sigs,residual,wanted)
  assert len(matches)==len(report)==len(live)==len(owner)==len(hist)==0
  # Even the closest oracle-injection control must leave a damaged map.
  near=min(sigs,key=lambda i:((sigs[i][0]^wanted).bit_count(),i))
  near_dist=(sigs[near][0]^wanted).bit_count()
  assert near_dist>0 and trace(G,tape,(near,residual))[0]!=base
  control=positive_control(G,tape,forms)
  result['branches'][which]={
   'readout_owners':list(A if which=='a' else B),
   'removed_move_clock':10039 if which=='a' else 10036,
   'residual':bits(residual),'output_signature':bits(wanted),'separator':bits(ell),
   'explicit_nonzero_kernel_input':bits(collision),
   'separator_dot_target':1,'surviving_move_slots':len(sigs),
   'move_slots_odd_against_separator':len(odd),
   'exact_signature_matches':len(matches),'live_donor_hits':len(live),
   'owner_only_overgrant_hits':len(owner),'historical_span_hits':len(hist),
   'output_operator_rank':len(Basis(enumerate(forms)).b),
   'move_signature_span_rank':len(span.b),'private_clear_count':len(clears),
   'nonzero_symbolic_clears':sum(bool(v) for _,_,v in clears),
   'additional_cochart_adds':8 if which=='a' else 22,
   'removed_paid_move_rank':1,
   'signature_nearest_clock':near,'signature_min_hamming_distance':near_dist,
   'oracle_at_nearest_rejected':True,'positive_control':control}
  print(which, 'separator pairs 1 with target and 0 with all',len(sigs),
        'surviving MOVE signatures; signature span rank',len(span.b),
        '; legal synthetic correction at clock 2 passed',flush=True,file=sys.stderr)
 # Actually exercise the graph loader's corruption gate on a changed byte.
 import tempfile
 original=path.read_bytes()
 with tempfile.TemporaryDirectory(prefix='p104-corruption-') as tmp:
  broken=Path(tmp)/'broken.gz';broken.write_bytes(original[:-1]+bytes([original[-1]^1]))
  try:load(broken)
  except ValueError as exc:assert str(exc)=='compressed input SHA mismatch'
  else:raise AssertionError('corrupted graph was accepted')
 result['input_corruption_rejected']=True
 # Deterministic comparison is optional: no source files or receipts are changed.
 print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
