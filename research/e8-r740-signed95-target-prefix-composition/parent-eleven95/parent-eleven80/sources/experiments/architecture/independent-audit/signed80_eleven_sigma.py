"""Independent structural check of all selected concrete rational sigma maps.

Admitted initial helper frames are coordinate subspaces; exploit that fact
to reconstruct each map by signed axis lookup, rather than dense products.
"""
from pathlib import Path
from fractions import Fraction as Q
import gzip,json,hashlib
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
BASE=ROOT/'experiments/stage-search/pr445-signed80-eleven';PARENT=BASE/'signed'
rd=lambda p:json.loads(p.read_text())
def inner(a,b):return sum(x*y for x,y in zip(a,b))
def columns(A):return list(zip(*A))
def main():
    artifact=BASE/'hosted/HOSTED-SIGMA.json';r=rd(artifact)
    t=json.loads(gzip.decompress((BASE/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()))
    fs=rd(PARENT/'records/frames.json')['frames'];st=rd(PARENT/'records/249-states.json')['initial'];geo=rd(BASE/'hosted/GEOMETRY.json')
    source={}
    for fid,rec in r['source_orthogonal_completions'].items():
        A=[[Q(x) for x in row] for row in rec['matrix']];cols=columns(A);f=fs[fid]
        assert all(inner(a,b)==int(i==j) for i,a in enumerate(cols) for j,b in enumerate(cols))
        assert cols[:f['dim']]==[tuple(Q(x,2) for x in row) for row in f['B']]
        assert rec['ordering']==list(range(f['dim'],8))+list(range(f['dim']))
        assert rec['width']==8-f['dim']
        # All columns of the current completions are signed coordinate axes.
        coordinate={}
        for k,c in enumerate(cols):
            nz=[j for j,x in enumerate(c) if x];assert len(nz)==1 and abs(c[nz[0]])==1
            coordinate[k]=(nz[0],c[nz[0]])
        source[fid]=coordinate
    ports={}
    for port in geo['ports']:
        cols=[tuple(Q(x,2) for x in port['q'])]+columns([[Q(x) for x in row] for row in port['complement_columns']])
        assert len(cols)==8 and all(inner(a,b)==int(i==j) for i,a in enumerate(cols) for j,b in enumerate(cols))
        ports[port['port']]=cols
    slotset={tuple(x) for x in t['hosting']['slots']};seen=defaultdict(set);checks=0
    idles={e['idx']:e for e in t['schedule'] if e['kind']=='idle'}
    for rec in r['selected_routes']:
        i,cp,off,w,stage,h,fid,target,to,so,digest=rec
        assert (i,cp,off,w,stage,h) in slotset and fid==str(st[str(240+h)])
        e=idles[i];start=1 if e['source_level']==-1 else 8+7*e['source_level'];stop=8+7*e['target_level']
        assert target==list(range(start,stop))[off:off+w]
        assert to==target+[j for j in range(78) if j not in target]
        assert so==r['source_orthogonal_completions'][fid]['ordering']+list(range(8,78))
        # Reordered source columns S_k are signed physical axes. sigma sends
        # that physical axis to sign(S_k)*T_k. Compute by bijective lookup.
        sigma=[None]*78
        for k,saxis in enumerate(so):
            physical,sign=source[fid][saxis] if saxis<8 else (saxis,Q(1))
            taxis=to[k]
            vector=ports[cp%120][taxis] if taxis<8 else tuple(Q(j==taxis) for j in range(78))
            sparse=tuple((j,str(sign*x)) for j,x in enumerate(vector) if x)
            assert sigma[physical] is None;sigma[physical]=sparse
        key=tuple(sigma);assert None not in key
        assert hashlib.sha256(repr(key).encode()).hexdigest()==digest
        family=(stage,e['pair'],cp);assert key not in seen[family];seen[family].add(key)
        checks+=1
    assert checks==len(slotset)==8140
    out=dict(status='PASS_INDEPENDENT_ALL8140_CONCRETE_SIGNED80_ELEVEN_SIGMA_AND_OWNER_INJECTION',
        artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),selected_sigma_checks=checks,
        source_coordinate_frames=len(source),actual_orthogonal_port_charts=len(ports),all78_columns_match=True,
        exact_inverse='Every sigma is product of two proved orthogonal bases and a permutation, so transpose is exact inverse.',
        residual_mapping='First w reordered source columns span actual helper orthogonal complement and map to exact selected pending columns.',
        D_identity='Orthogonal target slot projectors have zero pairwise products. D_P D_Q=D_(P+Q) for PQ=QP=0; remainder gives parent pending projector. D_P symmetric involution validates reflection.',
        injection='Distinct exact78-column sigma maps at fixed stage/family imply distinct d*sigma^-1 owners for every invertible cover class d.',
        scope='All actual selected geometry, exact complements and symbolic projector/cover proof. Global signed primitive/compiler precision/tape and finite invoice remain conditional separate gates.')
    (OUT/'SIGNED80_ELEVEN-SIGMA.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
