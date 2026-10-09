"""Independent literal all-column F2 audit; no emitter/checker imports.

Forward and whole-word time reverse are checked on all source, target and
physical dirty columns. Frame-complement geometry is a separate lemma.
"""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,time,random,sys
if sys.flags.optimize:raise RuntimeError("Audit requires enabled assertions; do not use -O")
parser=argparse.ArgumentParser();parser.add_argument('--word',type=Path,default=Path(__file__).with_name('emitted-word.json'));parser.add_argument('--output',type=Path,default=Path(__file__).with_name('independent-all-columns.json'));args=parser.parse_args()
raw=args.word.read_bytes();w=json.loads(raw);v,R=w['v'],w['R'];ops=w['ops'];cut=w['cut'];assert 0<cut<len(ops)
merge={b:a for a,b in w['pairs']};assert len(merge)==len(w['pairs']);assert not set(merge)&set(merge.values())
slot=[merge.get(s,s) for s in range(R)];live=sorted(set(slot));index={s:i for i,s in enumerate(live)}
response=[int(x,16) for x in w['response']]
gauges={g['role']:g for g in w['gauges']};assert len(gauges)==len(w['gauges'])
at=defaultdict(list)
for g in w['gauges']:
 assert cut<=g['read']<len(ops)
 assert sum(1<<t for t in g['targets'])==response[g['role']]
 at[g['read']].append(g['role'])
deliveries=defaultdict(list)
for e in w['k']['entries']:deliveries[e['deliver_after_root']].append(e)
# Disjoint physical coordinate ranges: X, Y, and nonduplicated aliased Z.
X=lambda i:i
Y=lambda i:v+i
Z=lambda s:2*v+index[slot[s]]
ncols=2*v+len(live);initial=[1<<i for i in range(ncols)]
for kind,a,b,f in ops:
 assert kind in ('a','x') and 0<=a<R
 assert (kind=='x' and 0<=b<v) or (kind=='a' and 0<=b<R and slot[a]!=slot[b])
source_M={i:e['mix_frame'] for e in w['k']['entries'] for i in (e['carrier'],e['passive'])}
mutation_x=next(i for i,o in enumerate(ops) if o[0]=='x' and o[3]==source_M[o[2]])
mutation_gauge=next(b for a,b in w['pairs'] if response[b])

def transcript(mutation=None,signed=False):
 events=[]
 def add(a,b,c=1):assert a!=b and c in (-1,1);events.append((a,b,c) if signed else (a,b))
 def read(s):
  mask=response[s]
  while mask:
   b=mask&-mask;add(Y(b.bit_length()-1),Z(s),-1);mask^=b
 def gate(i,inverse=False):
  kind,a,b,f=ops[i]
  if mutation=='omit_forward_new_X' and i==mutation_x and not inverse:return
  if mutation=='omit_inverse_new_X' and i==mutation_x and inverse:return
  add(Z(a),X(b) if kind=='x' else Z(b),-1 if inverse else 1)
 for s in range(R):
  if s not in gauges:read(s)
 for i in range(cut):gate(i)
 for r,s in zip(w['roots'],w['rootroles']):
  if r['kind']=='center':
   for t in r['targets']:add(Y(t),Z(s))
 for i in range(cut,len(ops)):
  for s in at[i]:
   if mutation!='omit_compensated_read' or s!=mutation_gauge:read(s)
  gate(i)
 for j,(r,s) in enumerate(zip(w['roots'],w['rootroles'])):
  if r['kind']!='side':continue
  for t in r['targets']:add(Y(t),Z(s))
  for e in deliveries[j]:
   add(X(e['carrier']),X(e['passive']))
   for t in e['receivers']:add(Y(t),X(e['carrier']))
 for e in w['k']['entries']:add(X(e['carrier']),X(e['passive']),-1)
 for i in reversed(range(len(ops))):gate(i,True)
 return events
expected=list(initial)
for i in range(v):expected[Y(i)]^=initial[X(i)]
def run(events,reverse=False):
 values=list(initial)
 for a,b in reversed(events) if reverse else events:values[a]^=values[b]
 bad=[i for i,(a,b) in enumerate(zip(values,expected)) if a!=b]
 return dict(exact_map=not bad,bad_source_rows=sum(i<v for i in bad),bad_target_rows=sum(v<=i<2*v for i in bad),bad_dirty_rows=sum(i>=2*v for i in bad),first_bad_rows=bad[:3])
t0=time.monotonic();events=transcript();baseline=run(events);reflected=run(events,True);assert baseline['exact_map'] and reflected['exact_map'],(baseline,reflected)
controls={}
for name in ['omit_forward_new_X','omit_inverse_new_X','omit_compensated_read']:
 r=run(transcript(name));assert not r['exact_map'],(name,r);controls[name]=r
# Defining signed lift: each integer shear has a literal unit inverse.
# This certifies the inverse and restored X/Z, not an integer decoder identity.
signed=transcript(signed=True)
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
for c in (-1,1):
 A=[[1,c],[0,1]];B=[[1,-c],[0,1]];assert mm(A,B)==mm(B,A)==[[1,0],[0,1]]
assert len(signed)==len(events) and all((a,b)==e for (a,b,c),e in zip(signed,events))
integer=[]
for seed in (1701,3402):
 rng=random.Random(seed);start=[rng.randrange(-(1<<20),1<<20) for _ in range(ncols)];values=list(start)
 for a,b,c in signed:values[a]+=c*values[b]
 assert values[:v]==start[:v] and values[2*v:]==start[2*v:]
 assert all((values[Y(i)]-start[Y(i)]-start[X(i)])%2==0 for i in range(v))
 for a,b,c in reversed(signed):values[a]-=c*values[b]
 assert values==start
 integer.append(dict(seed=seed,source_and_dirty_restored=True,bit_decoder_parity=True,whole_word_signed_inverse_restored=True))
out=dict(status='PASS',word_sha256=hashlib.sha256(raw).hexdigest(),logical_auxiliary_roles=R,physical_auxiliary_roles=len(live),source_columns=v,target_columns=v,dirty_columns=len(live),total_independent_columns=ncols,literal_elementary_operations=len(events),forward_auxiliary_operations=len(ops),original_source_control_operations=sum(o[0]=='x' for o in ops),gauges=len(gauges),pairs=len(merge),baseline=baseline,full_time_reverse=reflected,negative_controls=controls,integer_lift=dict(exact_unit_shear_inverse_certified=True,global_inverse_argument='Literal reverse word with negated unit coefficients; adjacent inverse pairs cancel over Z on all coordinates.',integer_decoder_identity_claimed=False,sample_replays=integer),mutation_new_X_operation=mutation_x,elapsed_seconds=time.monotonic()-t0,scope='Exact F2 scalar maps: Y+=X, all original X and arbitrary dirty Z restored, every Y column retained. Whole-word inverse has same scalar map in F2. Actual complemented-frame geometry uses the separate reflection lemma and forward frame certification.')
args.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
