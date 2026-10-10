# pairs_mw_p.py: PR #233's discovery/pairs_mw.py (Chafik Boukhalfa with Anthropic Claude and OpenAI Codex
# assistance, Apache-2.0; vendored unchanged in pr233/pairs_mw.py) with ONE line changed: the gauge rank f in the
# donor weight is h - 4 (the rank of the selected gauges) instead of the literal 18, which equals h - 4 only at
# h = 22. At h = 18 the literal makes every weight 0 (no pairs); see README.md. Identical to pairs_mw.py at h = 22.
# Change by DreamingOfClouds with Anthropic Claude assistance (Apache-2.0).
"""Maximum-weight donor pairing for gauged recipients (weights depend on the donor only, so the
transversal-matroid greedy with augmenting paths is optimal). Explicit legality: donor ungauged non-root with ops,
last frame contained in the recipient gauge, donor dead before the recipient's first operation (or in phase one)."""
from collections import defaultdict
import sys
from paired_cube.frames import contained
def pairs_maxweight(o):
 sys.setrecursionlimit(100000)
 donors=[s for s in range(o.R) if s not in o.gauge and s not in o.roots and o.role_ops[s]]
 recipients=sorted(o.gauge,key=lambda b:(o.position[o.role_ops[b][0]],b));rindex={b:i for i,b in enumerate(recipients)}
 rtime=[o.position[o.role_ops[b][0]] for b in recipients]
 byframe=defaultdict(list)
 for s in donors:byframe[o.frames[o.role_ops[s][-1]]].append(s)
 groups={}
 adj=defaultdict(list)  # donor -> recipient indices
 for b in recipients:
  F=o.gauge[b]
  if F not in groups:groups[F]=[s for D,ss in byframe.items() if contained(D,F) for s in ss]
  t=rtime[rindex[b]]
  for s in groups[F]:
   if o.position[o.role_ops[s][-1]]<t:adj[s].append(rindex[b])
 def weight(s):
  dd=len(o.frames[o.role_ops[s][-1]]);f=o.h-4  # cp10: PR #233 hard-codes f=18 (= h-4 at h=22)
  return 3*o.phi[o.h-dd]+o.phi[3*f]-3*o.phi[f-dd] if f>=dd else -1e9
 order=sorted(adj,key=lambda s:(-weight(s),o.position[o.role_ops[s][-1]],s))
 mr=[-1]*len(recipients);md={}
 def dfs(s,seen):
  for r in adj[s]:
   if r in seen:continue
   seen.add(r)
   if mr[r]<0 or dfs(mr[r],seen):mr[r]=s;md[s]=r;return True
  return False
 for s in order:
  if weight(s)<=0:break
  dfs(s,set())
 result=[]
 for r,s in enumerate(mr):
  if s>=0:
   b=recipients[r];first=o.role_ops[b][0]
   result.append([s,b,None if o.role_ops[s][-1] in o.phase else first])
 stats=dict(donors=len(donors),recipients=len(recipients),edges=sum(map(len,adj.values())),matched=len(result),total_weight=sum(weight(s) for s,_,_ in result))
 return result,stats
