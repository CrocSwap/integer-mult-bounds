"""Small independent finite check of the changed Round20 source/delivery lemmas.

Replays only each 24-row packet prefix, eight early face additions, and the
binary frames of the first/second cross-face reads.  It does not import a
constructor, replay a global word, or perform a phase/hosting audit.
"""
import argparse
import copy
import gzip
import hashlib
import itertools as it
import json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path


def basis(vs):
    out = {}
    for x in vs:
        for p in sorted(out,reverse=True):
            if x>>p&1:x ^= out[p]
        if x:
            p=x.bit_length()-1
            for q in out:
                if out[q]>>p&1:out[q] ^= x
            out[p]=x
    return tuple(out[p] for p in sorted(out,reverse=True))


def inside(F,G):
    return basis(F+G)==G


def determinant(M):
    M=copy.deepcopy(M);d=Q(1);n=len(M)
    for c in range(n):
        p=next((i for i in range(c,n) if M[i][c]),None)
        if p is None:return Q(0)
        if p!=c:M[p],M[c]=M[c],M[p];d=-d
        q=M[c][c];d*=q;M[c]=[x/q for x in M[c]]
        for i in range(c+1,n):
            q=M[i][c]
            if q:M[i]=[x-q*y for x,y in zip(M[i],M[c])]
    return d


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--packets',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    pp=a.packets/'PROTOTYPE.json';mp=a.packets/'PACKET-PROGRAMS.json.gz'
    D=json.loads(pp.read_text());P=D['binary_ports'];roots=D['root_lines']
    modules=json.loads(gzip.decompress(mp.read_bytes()))
    modules={tuple(z['receipt']['block']):z for z in modules}
    face={};own={};requests=defaultdict(list);frontier=[]
    for c,z in sorted(modules.items()):
        ids=z['receipt']['source_lines'];idx={s:i for i,s in enumerate(ids)}
        rows=[[Q(i==j) for j in range(8)] if i<8 else [Q(0)]*8 for i in range(24)]
        frames=[(P[s],) for s in ids]+[()]*16
        for (t,s,num,den),F in zip(z['events'][:40],z['event_frames'][:40]):
            F=basis(F);assert inside(frames[t],F) and inside(frames[s],F)
            frames[t]=frames[s]=F;q=Q(num,den)
            rows[t]=[x+q*y for x,y in zip(rows[t],rows[s])]
        tet=[sorted(s for s in ids if sum(roots[s][i]<0 for i in c)%2==parity) for parity in (0,1)]
        p,q=c[:2],c[2:]
        needed=set()
        for parity,targets in enumerate(tet):
            groups=defaultdict(list)
            for t in targets:groups[roots[t][p[0]]*roots[t][p[1]]].append(t)
            for eps,ts in sorted(groups.items()):
                t,u=sorted(ts);zeta=-Q(2*roots[u][p[0]],roots[t][p[0]])
                e2=roots[t][q[0]]*roots[t][q[1]]
                requests[c,p,eps].append((t,-Q(roots[t][p[0]],2)))
                requests[c,q,e2].append((u,-Q(roots[t][q[0]],2)))
                for target,sgn in ((t,1),(u,-1)):
                    want=[Q(0)]*8
                    for s in tet[1-parity]:
                        gt=Q(sum(x*y for x,y in zip(roots[t],roots[s])),2)
                        gu=Q(sum(x*y for x,y in zip(roots[u],roots[s])),2)
                        want[idx[s]]=-gt/4+sgn*gu/(2*zeta)
                    assert sum(bool(x) for x in want)==2
                    candidates=[]
                    for r,row in enumerate(rows):
                        nz=next((j for j,x in enumerate(row) if x),None)
                        if nz is None or not want[nz]:continue
                        alpha=want[nz]/row[nz]
                        if [alpha*x for x in row]==want:candidates.append((r,alpha))
                    assert len(candidates)==1
                    r,alpha=candidates[0];assert len(frames[r])==2
                    needed.add(r);own[target]=frames[r]
        assert len(needed)==8
        keys=[(p,e) for p in it.combinations(c,2) for e in (-1,1)]
        early=[j for j,e in enumerate(z['events'][40:]) if not ({e[0],e[1]}&needed)]
        assert len(early)==8
        retired=[]
        for j in early:
            t,s,num,den=z['events'][40+j];F=basis(z['event_frames'][40+j])
            assert inside(frames[t],F) and inside(frames[s],F)
            frames[t]=frames[s]=F;qq=Q(num,den)
            rows[t]=[x+qq*y for x,y in zip(rows[t],rows[s])]
            retired.append(s)
        assert len(set(retired))==8 and not set(retired)&needed
        T=[rows[r] for r in retired];d=determinant(T);assert d
        assert abs(d.numerator)&(abs(d.numerator)-1)==0
        assert d.denominator&(d.denominator-1)==0
        assert all(len(frames[r])==2 for r in needed)
        for key,F in zip(keys,z['event_frames'][40:]):face[c,*key]=basis(F)
        frontier.append(dict(block=c,source_lines_112=[s-8 for s in ids],
            own_partial_registers=sorted(needed),early_face_indices=early,
            early_face_keys=[keys[j] for j in early],retired_registers=retired,
            retired_source_matrix=[[str(x) for x in row] for row in T],
            determinant=str(d),own_partial_frames_preserved=True))

    copies={}
    for (c,p,e),F in face.items():
        for target in modules:
            if target!=c and set(p)<=set(target):copies[c,p,e,target]=F
    target_frames=dict(own);first_regs=[];deliveries=[]
    for key,reqs in sorted(requests.items()):
        assert len(reqs)==2
        c,p,e=key;aa,bb=sorted(d for d in modules if d!=c and set(p)<=set(d))
        for j,(target,coef) in enumerate(sorted(reqs)):
            first,second=(aa,bb) if j==0 else (bb,aa)
            r=(first,p,e,second);s=(second,p,e,c)
            E=target_frames[target];assert inside(E,face[c,p,e])
            F=basis(E+copies[r]);assert len(F)==4
            future=basis(face[first,p,e]+face[c,p,e]);assert len(future)==5 and inside(F,future)
            hyper=basis([x for x in range(1,512) if not (x&P[target]).bit_count()%2])
            assert inside(F,hyper)
            target_frames[target]=copies[r]=F;first_regs.append(r)
            deliveries.append(dict(target=target-8,block=c,pair=p,epsilon=e,
                own_frame=list(E),own_face_frame=list(face[c,p,e]),first_source=first,second_source=second,
                first_read_frame=list(F),future_M_frame=list(future),second_copy_key=s,
                target_hyper=list(hyper)))
    assert len(deliveries)==112 and len(set(first_regs))==112
    ordinary=0
    for c in modules:
        for p in it.combinations(c,2):
            aa,bb=sorted(d for d in modules if d!=c and set(p)<=set(d))
            for e in (-1,1):
                if (c,p,e) in requests:continue
                r=(aa,p,e,c);s=(bb,p,e,c)
                F=basis(copies[r]+copies[s]);assert len(F)==5
                assert F==basis(face[aa,p,e]+face[bb,p,e])
                copies[r]=copies[s]=F;ordinary+=1
    assert ordinary==112
    for d in deliveries:
        target=d['target']+8;s=d.pop('second_copy_key')
        F=basis(target_frames[target]+copies[s]);assert len(F)==6
        assert inside(F,tuple(d['target_hyper']))
        d['second_copy_frame_before_read']=list(copies[s]);d['second_read_frame']=list(F)
        target_frames[target]=copies[s]=F
    report=dict(status='PASS_INDEPENDENT_SMALL_FRONTIER_AND_DELIVERY_CHECK',v=112,
        prototype_sha256=hashlib.sha256(pp.read_bytes()).hexdigest(),
        packets_sha256=hashlib.sha256(mp.read_bytes()).hexdigest(),
        center_frontiers=frontier,deliveries=deliveries,
        summary=dict(blocks_with_invertible_early_retired_basis=len(frontier),
            determinant_counts=dict(Counter(x['determinant'] for x in frontier)),
            own_partial_containments=112,first_read_rank4=112,second_read_rank6=112,
            selected_keys_skipped=56,ordinary_M_keys=ordinary,distinct_first_face_copies=112),
        scope='Only the changed local source-frontier and cross-face delivery lemmas. No full scalar response, entrance kernel, phase recipe, or global hosting audit.')
    a.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary'],sort_keys=True))


if __name__=='__main__':main()
