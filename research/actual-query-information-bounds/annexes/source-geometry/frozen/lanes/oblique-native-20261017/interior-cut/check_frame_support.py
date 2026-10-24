#!/usr/bin/env python3
"""Check the scalar transfer support forced by the actual cut frames."""
from fractions import Fraction as F
from pathlib import Path
import gzip,json
from hashlib import sha256
import probe_readiness as p
HERE=Path(__file__).resolve().parent
raw=gzip.decompress((HERE/'ALL-CUT-EDGES.json.gz').read_bytes())
p.need(sha256(raw).hexdigest()=='18c89367243fc7c09411f28a8022884130373ce4886de806f4b011edec030418','Pinned cut inventory')
x=json.loads(raw);word=p.core['providers']['base']['canonical'];ports=word['ports']

def contains(frame,v):
    for basis in sorted(frame,reverse=True):v=min(v,v^basis)
    return v==0

checks=0;support=set()
for product in x['products']:
    frame=word['frames'][product['frame']]
    for t,num,den in x['tail_columns'][product['tail_column']]:
        p.need(all((v&ports[t]).bit_count()%2==0 for v in frame),'Current frame lies in each final target hole')
        for s,ops,num,den in x['source_rows'][product['source_row']]['constrained']:
            if s>=112 or ops:continue
            p.need(contains(frame,ports[s]),'Raw source line lies in current frame')
            p.need((ports[s]&ports[t]).bit_count()%2==0,'Source and target ports are orthogonal')
            support.add((t,s));checks+=1
# The full centre mixer must vanish at all forbidden off-diagonal positions.
basis={};equations=0
for t in range(112):
    for s in range(112):
        if t==s or (ports[t]&ports[s]).bit_count()%2==0:continue
        row={a*8+b:p.r[a].get(t,F(0))*p.r[b].get(s,F(0)) for a in range(8) for b in range(8)}
        row={k:v for k,v in row.items() if v};equations+=1
        while row:
            pivot=min(row)
            if pivot not in basis:
                c=row[pivot];basis[pivot]={k:v/c for k,v in row.items()};break
            p.e.add(row,basis[pivot],-row[pivot])
free=[i for i in range(64) if i not in basis];kernel=[]
for f in free:
    sol={f:F(1)}
    for pivot,row in sorted(basis.items(),reverse=True):
        value=-sum(c*sol.get(k,F(0)) for k,c in row.items() if k!=pivot)
        if value:sol[pivot]=value
    kernel.append(sol)
p.need(len(basis)==63 and len(kernel)==1,'Exact scalar-mixer constraint rank')
p.need(kernel[0]=={9*i:F(1) for i in range(8)},'Only scalar identity centre mixers')
report={'status':'PASS_EXACT_FRAME_SUPPORT_AND_CENTRE_RIGIDITY','inventory_decompressed_sha256':sha256(raw).hexdigest(),'scalar_source_target_checks':checks,'reachable_raw_scalar_pairs':len(support),'forbidden_offdiagonal_equations':equations,'centre_mixer_constraint_rank':len(basis),'centre_mixer_kernel':[{str(k):str(v) for k,v in row.items()} for row in kernel],'scope':'Fixed native source and Y frame paths with added or retuned one-way equal-frame scalar transfers, in the exact free-warp-word model. Physical operator-valued transfers, changed source circuits, and nonmonotone frame paths remain outside this result.'}
report['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
(HERE/'FRAME-SUPPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(report,flush=True)
