"""Full source471 physical frame-tag iterator and paid telescope audit.

Tokens retain actual physical register identities. The exact scalar projection
must match the independently verified complete F2 event digest. All same-frame
moves and copied-center temporary blocks are checked and counted independently.
Default execution prints a compact result; --write saves the witness summary.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parent
AUDIT=BASE/'five_stage_source471_scalar_audit_20261009.py'
setup=AUDIT.read_text().split('result = {')[0]
ns={'__file__':str(AUDIT),'__name__':'physical_telescope_dependency'}
exec(compile(setup,str(AUDIT),'exec'),ns)
W,C=ns['W'],ns['C'];v=W.v;regs=ns['regs'];n=2*v+len(regs)
ZERO=W.register([]);FULL=W.w['full_frame']
state={i:W.w['source_frame'][i]for i in range(v)}
state.update({v+t:ZERO for t in range(v)})
state.update({2*v+j:W.gauge[r]['frame']if r in W.gauge else ZERO for j,r in enumerate(regs)})
caps={}
for t in range(v):
 B,_=W.module.kernel([C.cov[t]],W.h);caps[t]=W.register(B)
 assert C.dimf[caps[t]]==W.h-1
used_frames=set(state.values());derived_target_caps=set(caps.values())
hist=Counter();categories=Counter();frame_edges=Counter();centers=[]
scalar_hash=hashlib.sha256(b'[');tag_hash=hashlib.sha256(b'[')
count=0;center=None;move_count=0;copy_count=0;subchecks=0
subcache={}
def move(i,f):
 global move_count,subchecks
 used_frames.add(f)
 old=state[i]
 if old==f:return
 key=old,f
 if key not in subcache:
  subcache[key]=C.sub(old,f);subchecks+=1
 assert subcache[key],('physical frame descent',i,old,f,C.dimf[old],C.dimf[f])
 d=C.dimf[f]-C.dimf[old];assert d>=0
 if d:hist[d]+=1;move_count+=1
 frame_edges[(old,f)]+=1;state[i]=f
def append_digest(hasher,row,comma):
 if comma:hasher.update(b',')
 hasher.update(json.dumps(row,separators=(',',':')).encode())
def add(x,c,y,f,kind):
 global count
 assert isinstance(x,int)and isinstance(y,int)and x!=y
 move(x,f)
 physical_y=y
 if kind=='center':
  assert center is not None and center['source']==y and f==ZERO
  physical_y=n
 else:move(y,f)
 append_digest(scalar_hash,[x,y,c],count)
 append_digest(tag_hash,[x,physical_y,c,f,kind],count)
 count+=1;categories[kind]+=1
 return x
def center_begin(source,frame):
 global center,copy_count
 assert center is None
 move(source,frame)
 rank=C.dimf[frame];assert rank==22
 center=dict(source=source,frame=frame,rank=rank,first_event=count)
 # A complete-stream copy starts at the original frame and is transformed to
 # ZERO by the exact inverse partial swap. The original stays at its frame.
 hist[rank]+=1;copy_count+=1
 center['temporary']=n;center['copy_output_frame']=ZERO
 centers.append(center)
def center_end():
 global center
 assert center is not None
 center['after_event']=count
 center['scatter_reads']=center['after_event']-center['first_event']
 assert center['scatter_reads']>0
 center=None
# Use original pinned source body, not the scalar observer's modified add.
text=ns['SOURCE_TEXT']
body=text[text.index('def replay('):text.index("if __name__=='__main__':")]
body=body[:body.index(' if binary:want')]
def replace(old,new,expected=1):
 global body
 assert body.count(old)==expected,('source site mismatch',old,body.count(old),expected)
 body=body.replace(old,new)
replace("unit=(lambda i:1)if major else(lambda i:1<<i)if binary else(lambda i:1<<(bits*i))",'unit=lambda i:i')
replace(' def add(x,c,y):return x+abs(c)*y if major else x^y if binary and c&1 else x if binary else x+c*y','')
replace('y[t]=track(add(y[t],-direction*c,value(s)))',"y[t]=track(add(y[t],-direction*c,value(s),W.gauge[s]['frame']if s in W.gauge else ZERO,'dirty_read'))")
replace('a,b,_=W.ops[i];assign(a,add(value(a),sign,value(b)))',"a,b,_=W.ops[i];assign(a,add(value(a),sign,value(b),W.opframe[i]if sign==1 else FULL,'forward_gate'if sign==1 else'cleanup_gate'))")
replace('for n,s in W.source.items():assign(s,add(value(s),1,x[n]))',"for n,s in W.source.items():assign(s,add(value(s),1,x[n],W.w['source_frame'][n],'inject'))")
replace("x[r['partner']]=track(add(x[r['partner']],1,x[r['source']]))","x[r['partner']]=track(add(x[r['partner']],1,x[r['source']],kpair[r['source']]['mix_frame'],'gauge_mix'))")
replace('x[a]=track(add(x[a],1,x[b]))',"x[a]=track(add(x[a],1,x[b],kpair[b]['mix_frame'],'partner_mix'))",2)
replace("for r,s in zip(W.g['roots'],W.w['rootroles']):\n  if r['kind']=='center':\n   for t in r['targets']:","for j,(r,s)in enumerate(zip(W.g['roots'],W.w['rootroles'])):\n  if r['kind']=='center':\n   center_begin(value(s),W.w['root_frame'][j])\n   for t in r['targets']:")
replace("center_reads.append((s,t));y[t]=track(add(y[t],direction,value(s)))","center_reads.append((s,t));y[t]=track(add(y[t],direction,value(s),ZERO,'center'))\n   center_end()")
replace("y[t]=track(add(y[t],-1,y[e['pivot']]))","y[t]=track(add(y[t],-1,y[e['pivot']],ZERO,'terminal_pre'))")
replace("y[e['pivot']]=track(add(y[e['pivot']],direction,value(b)))","y[e['pivot']]=track(add(y[e['pivot']],direction,value(b),W.opframe[i],'terminal_write'))")
replace("y[t]=track(add(y[t],1,y[e['pivot']]))","y[t]=track(add(y[t],1,y[e['pivot']],e['root_frame'],'terminal_post'))")
replace("y[t]=track(add(y[t],direction,value(s)))","y[t]=track(add(y[t],direction,value(s),W.w['root_frame'][j],'side_root'))")
replace("y[t]=track(add(y[t],direction,x[a]))","y[t]=track(add(y[t],direction,x[a],e['deliver_frame'],'partner_delivery'))")
replace("x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']]))","x[e['carrier']]=track(add(x[e['carrier']],-1,x[e['passive']],FULL,'partner_cleanup'))",3)
replace('for n,s in W.source.items():assign(s,add(value(s),-1,x[n]))',"for n,s in W.source.items():assign(s,add(value(s),-1,x[n],FULL,'uninject'))")
body+='\n return dict(center_reads=len(center_reads))\n'
ns.update(dict(ZERO=ZERO,FULL=FULL,add=add,center_begin=center_begin,center_end=center_end))
exec(compile(body,str(ns['HERE']/'replay.py')+' [physical frame tags]','exec'),ns)
local_result=ns['replay']('token')
assert center is None
for i in range(v):move(i,FULL)
for t in range(v):move(v+t,caps[t])
for j,r in enumerate(regs):move(2*v+j,FULL)
scalar_hash.update(b']');tag_hash.update(b']')
assert scalar_hash.hexdigest()=='e74e43692685ad5f716b41b363acb8b443c2c90096634a55f0e3728980713944'
assert count==2569626 and copy_count==24 and local_result['center_reads']==5280
raw=json.loads((BASE/'retimed_source_heads_20261009/raw471_ledger.json').read_text())
expected=Counter({int(k):z for k,z in raw['one_stage_helper_histogram_including_copies'].items()})
assert hist==expected,('paid histogram mismatch',dict(hist),dict(expected))
assert sum(k*z for k,z in hist.items())==435846
# Initial independent helper gauges plus final full frames determine exact
# separated raw residuals. All physical scalar cross blocks were separately
# checked on all20163 columns under the matched event digest.
result=dict(status='PASS_COMPLETE_SOURCE471_PHYSICAL_FRAME_TAG_TELESCOPE',
 source_head='df95878d11190518e45ef9717c9ee05011f88ace',
 scalar_source_sha256=hashlib.sha256(text.encode()).hexdigest(),
 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 scalar_projection_sha256=scalar_hash.hexdigest(),tagged_scalar_sha256=tag_hash.hexdigest(),
 weighted_scalar_events=count,categories=dict(categories),physical_registers=n,
 distinct_frame_inclusion_checks=subchecks,positive_rank_moves=move_count,
 copied_centers=copy_count,center_scatter_reads=local_result['center_reads'],
 temporary_streams_simultaneous=1,copied_center_blocks=centers,
 paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(k*z for k,z in hist.items()),
 used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=hashlib.sha256(json.dumps(C.B[f],separators=(',',':')).encode()).hexdigest(),derived_target_cap=f in derived_target_caps)for f in sorted(used_frames)],
 initial_endpoints='X:Pq,Y:0,independentZ:sigma; source-owned auxiliary roles are actualX aliases',
 final_endpoints='X:H,Y:q-perp,independentZ:H',
 scope='Complete local physical tag telescope, with copied-center quotient blocks, bound to independently checked all-column F2 scalar digest. Five-stage routing/gauge assembly and all-size compiler/prime/tape proofs compose through their separate checked interfaces.')
if '--write'in sys.argv:
 Path(__file__).with_name('five_stage_source471_physical_telescope_20261009_result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:z for k,z in result.items()if k not in('copied_center_blocks','used_frames')},sort_keys=True))
