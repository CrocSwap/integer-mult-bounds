"""Apply PR79/82 future-compatible unit-row completion to the private engine.

PR79 completion: Chafik Boukhalfa; PR82 composition: Rohan Arun, both with
OpenAI Codex assistance. Composition
for Thomas DiFiore with OpenAI Codex assistance. Inherited notices apply.
The resulting matrix still contains an independently checked complete basis;
all synthesized swaps and XORs remain serialized and paid.
"""
from hashlib import sha256
from pathlib import Path

FUTURE = '''   def future_priority(i):
    compatible=sum(position[uses[u][1]]>step and contains(b['frame'],blocks[uses[u][1]]['frame']) for u in value_uses[b['inputs'][i]])
    return (-compatible,slots[ins[i]].bit_count(),i)
   for i in sorted(range(len(ins)),key=future_priority):
    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)
'''
STANDARD = '''   for i in range(len(ins)):
    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)
'''

def apply(source):
    anchor='t0=time.time();c,blocks,uses,value_uses,owner,signal,order,contains=build(h);v=len(c.inputs)'
    assert source.count(anchor)==1 and source.count(STANDARD)==1
    return source.replace(anchor,anchor+';position={g:i for i,g in enumerate(order)}').replace(STANDARD,FUTURE)
