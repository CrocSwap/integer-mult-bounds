"""Adversarial controls execute the actual selected clearing function."""
from pathlib import Path
from collections import Counter
source=Path(__file__).with_name('kernel_acquire.txt').read_text()
namespace={};exec('def factory(reclaim,slots,pending,retired,blocks,frames,stats,contains,profile_cost,xor,new,retired_index):\n'+source+' return acquire\n',namespace)
class Index:
 def __init__(self):self.removed=[]
 def remove(self,*a):self.removed.append(a)
def trial(signals,pending,retired,anchors,blocks=None,frames=None):
 slots=dict(signals);pending=dict(pending);retired=set(retired);blocks=blocks or [{'frame':(0,7),'rank':3}];frames=frames or {s:0 for s in slots};stats=Counter();index=Index();operations=[]
 def contains(a,b):return b[0]&a[0]==b[0] and a[1]&b[1]==a[1]
 def xor(s,a,g):assert contains(blocks[frames[a]]['frame'],blocks[g]['frame']);slots[s]^=slots[a];operations.append((s,a,g))
 def new(g):return 99
 def cost(s,g):return 10 if s in (0,1)else 1
 run=namespace['factory'](True,slots,pending,retired,blocks,frames,stats,contains,cost,xor,new,index)
 out=run(0,anchors);return out,slots,retired,stats,index,operations
# A genuine kernel relation replaces two expensive controls with one cheap control.
r=trial({0:1,1:2,2:3,3:3},{},{3},[0,1,2]);assert r[0]==3 and r[1][3]==0 and r[3]['zero_circuit_toggles']>0 and r[5]==[(3,2,0)] and len(r[4].removed)==1
# An independent dirty component cannot be claimed cleared.
r=trial({0:1,1:2,3:512},{},{3},[0,1]);assert r[0]==99 and r[1][3]==512 and not r[5] and not r[4].removed
# A pending source whose future frame cannot contain the clearing frame is excluded.
r=trial({0:1,3:1},{0:1},{3},[],[{'frame':(0,7),'rank':3},{'frame':(0,1),'rank':1}],{0:1,3:0});assert r[0]==99 and r[1][3]==1 and not r[5]
# The same signal with a compatible future endpoint is admissible and paid once.
r=trial({0:1,3:1},{0:0},{3},[]);assert r[0]==3 and r[1][3]==0 and r[3]['live_anchor_xors']==1 and len(r[5])==1
print('PASS four actual-source null-circuit controls')
