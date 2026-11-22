"""Independent capped carving, fill support and layout exponent audit."""
from fractions import Fraction as Q
from pathlib import Path
from itertools import product
import json,hashlib
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'phase_assembly_ultra/CAPPED-OUTER-ARITHMETIC.json'

def carve(n,B,W):
    assert B>2*W and B&(B-1)==0 and n>=2*W
    J=set(range(W))|set(range(n-W,n));blocks=[];c=W;stop=n-W
    while stop-c>=B+W:
        blocks.append(list(range(c,c+B)));J.update(range(c+B,c+B+W));c+=B+W
    while stop-c>4*W:
        rem=stop-c;k=1<<((rem-2*W).bit_length()-1)
        assert k<=B
        J.update(range(c,c+W));blocks.append(list(range(c+W,c+W+k)))
        J.update(range(c+W+k,c+2*W+k));c+=2*W+k
    J.update(range(c,stop))
    assert sorted(J|{j for b in blocks for j in b})==list(range(n))
    assert sum(map(len,blocks))+len(J)==n
    assert all(len(b)<=B and len(b)&(len(b)-1)==0 for b in blocks)
    assert all(b[0]-a[-1]>W for a,b in zip(blocks,blocks[1:]))
    assert len(J)<=10*W*((n+B-1)//B+B.bit_length()+1)
    return blocks,J

def fill_bound(n,blocks,J,W):
    adj=[set(j for j in range(n) if j!=i and abs(i-j)<=W) for i in range(n)]
    for block in blocks:
        for v in block:
            nbr=list(adj[v])
            for x in nbr:
                adj[x].update(y for y in nbr if y!=x);adj[x].discard(v)
            adj[v].clear()
    order={v:i for i,v in enumerate(sorted(J))}
    bandwidth=max((abs(order[i]-order[j]) for i in J for j in adj[i]),default=0)
    assert bandwidth<=2*W
    return bandwidth

def main():
    total=0;examples=[]
    for W in (1,2,3,4):
        for B in (8,16,32,64):
            if B<=2*W:continue
            for n in range(2*W,4*B+1):
                blocks,J=carve(n,B,W);total+=1
            n=4*B+7;blocks,J=carve(n,B,W);bw=fill_bound(n,blocks,J,W)
            examples.append(dict(W=W,B=B,n=n,blocks=len(blocks),boundary=len(J),schur_boundary_bandwidth=bw))
    raw=SOURCE.read_bytes();source=json.loads(raw);p={k:Q(v['rational']) for k,v in source['parameters'].items()}
    e,b,g=p['epsilon'],p['capped_block_power'],p['beta_group'];w=Q(1,2);h=1-e
    exponents=dict(per_group_union_movement=2*g+w-b,total_union_movement=e+g+w-b,
        total_group_scans=e-g,metadata_membership=g+2*h,microbox_key=g,
        global_sparse_key=g+h,guarded_support_span=g,
        sparse_microhalo_volume=g+3-8,
        hypothetical_fullkey_union=e+2*g+h+w-b)
    assert Q(1,2)<b<e<1 and 0<g<e
    assert exponents['metadata_membership']<1
    assert exponents['total_union_movement']<1-p['kappa']
    assert exponents['total_group_scans']<1-p['kappa']
    assert exponents['hypothetical_fullkey_union']<1-p['kappa']
    assert exponents['sparse_microhalo_volume']<0
    out=dict(status='PASS_INDEPENDENT_CAPPED_LAYOUT_EXTENSION',source_sha256=hashlib.sha256(raw).hexdigest(),
        finite_carvings=total,fill_support_examples=examples,
        exponents={k:str(v) for k,v in exponents.items()},
        scope='Capped carving, sparse layout and exponent audit only; anchored Gaussian identities remain separate.')
    (HERE/'CAPPED-LAYOUT-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
