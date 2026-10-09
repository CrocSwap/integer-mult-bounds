"""Source-assisted BIT global word: exact finite construction, no optimized Python."""
if not __debug__: raise RuntimeError("Exact verifier requires assertions; do not use -O")
from pathlib import Path
import sys,json,hashlib
from collections import Counter,defaultdict
HERE=Path(__file__).resolve().parent
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();BASE=args.output_dir.resolve();BASE.mkdir(parents=True,exist_ok=True);REF=HERE.parents[1]
sys.path.insert(0,str(REF/'scripts'));import paired_cube_bit_physical as P
from check_paired_cube_bit import dot
M=json.loads((BASE/'emitted-word.json').read_text());chk=P.loaded();chk.frames();chk.decoder();chk.geometry()
dim=chk.dimf; sub=chk.sub;h=chk.h;v=chk.v;full=M['full_frame'];R=M['R'];ops=M['ops'];rootroles=M['rootroles'];roots=M['roots'];pairs=M['pairs'];gauge={z['role']:z for z in M['gauges']};donors=dict(pairs);merge={b:a for a,b in pairs}
roleops=defaultdict(list);roleframes=defaultdict(list);support=[0]*R; ancestry=[0]*R
used_frames={op[3] for op in ops}|set(M['rootframes'])|{z['frame'] for z in M['gauges']}|{full}
for entry in M['k']['entries']:
 used_frames.update(entry['carrier_chain']);used_frames.update(entry['passive_chain'])
assert all(chk.nondeg(f) for f in used_frames), 'Every used geometric frame is nondegenerate'
spanchecks=0
for i,(kind,a,b,f) in enumerate(ops):
 assert chk.nondeg(f)
 roleops[a].append(i);roleframes[a].append(f)
 if kind=='a':
  roleops[b].append(i);roleframes[b].append(f)
  combined=support[a]|support[b]  # both operands must fit even when F2 cancellation occurs
 else:
  assert kind=='x';combined=support[a]^(1<<b)
 ancestry[a] |= ancestry[b] if kind=='a' else 1<<b
 mask=ancestry[a]  # conservative noncancelling source ancestry, including cancelled F2 terms
 while mask:
  low=mask&-mask;assert chk.in_frame(chk.chi[low.bit_length()-1],f),('span',i);mask^=low;spanchecks+=1
 support[a]^=support[b] if kind=='a' else 1<<b
rootframe=dict(zip(rootroles,M['rootframes']));local=Counter()
def chain(s):return [gauge[s]['frame'] if s in gauge else None]+roleframes[s]+([rootframe[s]] if s in rootframe else[])+[full]
for s in range(R):
 if s in merge:continue
 seq=chain(s)
 if s in donors:seq=seq[:-1]+chain(donors[s])
 prev=seq[0];d=0 if prev is None else dim[prev]
 for f in seq[1:]:
  assert f is not None
  assert prev is None or sub(prev,f),('chain',s,prev,f)
  assert dim[f]>=d
  if dim[f]>d:local[dim[f]-d]+=1
  prev,d=f,dim[f]
for r,f in zip(roots,M['rootframes']):
 if r['kind']=='center':local[dim[f]]+=1
# Exact original-X timeline: line injections all precede M controls; all precede K mixing.
membership={i:[] for i in range(v)}
for i,(kind,a,b,f) in enumerate(ops):
 if kind=='x':membership[b].append((i,f))
source=Counter()
for e in M['k']['entries']:
 for leaf,chain_ in [(e['carrier'],e['carrier_chain']),(e['passive'],e['passive_chain'])]:
  history=membership[leaf];assert history
  assert history[0][1]==chain_[0]
  assert all(f in (chain_[0],e['mix_frame']) for _,f in history)
  assert all(sub(f1,f2) for (_,f1),(_,f2) in zip(history,history[1:]))
  assert all(sub(f1,f2) for f1,f2 in zip(chain_,chain_[1:]))
  for f1,f2 in zip(chain_,chain_[1:]):source[dim[f2]-dim[f1]]+=1
# Gauged-target chains in actual emitted chronology and retained partner deliveries.
events=defaultdict(list);when={z['role']:(z['read'],i) for i,z in enumerate(reversed(M['gauges']))}
for s in sorted(gauge,key=when.get):
 z=gauge[s];assert M['cut']<=z['read']<=roleops[s][0]
 for t in z['targets']:events[t].append(z['frame'])
for a,b in pairs:
 assert roleops[a][-1]<when[b][0]
 assert sub(roleframes[a][-1],gauge[b]['frame'])
deliveries=defaultdict(list)
for e in M['k']['entries']:deliveries[e['deliver_after_root']].append(e)
for j,r in enumerate(roots):
 if r['kind']=='side':
  for t in r['targets']:events[t].append(M['rootframes'][j])
  for e in deliveries[j]:
   for t in e['receivers']:events[t].append(e['deliver_frame'])
target=Counter()
for t in range(v):
 prev=None;d=0
 for f in events[t]:
  assert prev is None or sub(prev,f),('targetchain',t,prev,f)
  assert all(dot(chk.cov[t],u)==0 for u in chk.B[f])
  if dim[f]>d:target[dim[f]-d]+=1
  prev,d=f,dim[f]
 if d<h-1:target[h-1-d]+=1
children=Counter()
for part in(local,source,target):
 for r,n in part.items():
  if r:children[r]+=3*n
for s,z in gauge.items():
 if s not in merge:children[3*z['dim']]+=1
children[2]+=2*v
W=2*v+R-len(pairs);rank=sum(r*n for r,n in children.items());m=3*h
expected=json.loads((BASE/'current168-network.json').read_text())['combined_fixed_boundary_profile']
assert dict(children)=={int(r):n for r,n in expected['child_histogram'].items()},(children,expected)
assert W==expected['W'] and W*m-rank==expected['delta']
result=dict(status='PASS',scope='Exact emitted elementary-word geometry, source-control chronology, target chronology, all paid chains; independent dirty replay separate',source_head=M['source_head'],R=R,physical_R=R-len(pairs),m=m,W_per_vertex=W,rank_per_vertex=rank,deficit_per_vertex=W*m-rank,operations=len(ops),source_controls=sum(op[0]=='x' for op in ops),span_membership_checks=spanchecks,local_histogram=dict(sorted(local.items())),source_data_histogram=dict(sorted(source.items())),target_data_histogram=dict(sorted(target.items())),child_histogram=dict(sorted(children.items())),exact_network_histogram_equal=True,word_sha256=hashlib.sha256((BASE/'emitted-word.json').read_bytes()).hexdigest())
(BASE/'emitted-physical.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
