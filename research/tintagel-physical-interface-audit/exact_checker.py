# Independently authored audit checker, revised for this portable packet.
# Changes: relative fixture paths, sparse exact phase coefficients, replay wrapper,
# and a semantic omitted-alignment control. No upstream programs are imported.
import sys
if sys.flags.optimize:
    raise RuntimeError("Exact replay requires assertions; do not use -O or PYTHONOPTIMIZE")
"""Independent finite validation. Stdlib only; source programs are NEVER imported.
Binary matrices are column lists. Complex numerators are integer pairs.
"""
from pathlib import Path
import hashlib, json, gzip
from collections import Counter
from itertools import product

ROOT = Path(__file__).resolve().parent
E8 = ROOT/'sources/pr390'

def parity(x): return x.bit_count() % 2
def eye(n): return tuple(1 << i for i in range(n))
def mv(cols, x):
    y = 0
    while x:
        bit = x & -x
        y ^= cols[bit.bit_length()-1]
        x ^= bit
    return y
def mul(a,b): return tuple(mv(a,x) for x in b)
def tr(a): return tuple(sum(((x >> i)&1)<<j for j,x in enumerate(a)) for i in range(len(a)))
def inv(a):
    n=len(a); rows=[r | (1 << (n+i)) for i,r in enumerate(tr(a))]
    for j in range(n):
        k=next(k for k in range(j,n) if rows[k] >> j & 1)
        rows[j],rows[k]=rows[k],rows[j]
        for k in range(n):
            if k != j and rows[k] >> j & 1: rows[k] ^= rows[j]
    assert tuple(r & ((1<<n)-1) for r in rows)==eye(n)
    return tr(tuple(r>>n for r in rows))
def rank(a):
    piv={}
    for x in a:
        while x:
            b=x.bit_length()-1
            if b not in piv: piv[b]=x;break
            x ^= piv[b]
    return len(piv)
def orth(a): return mul(tr(a),a)==eye(len(a))
def transvection(n,w): return tuple((1<<i) ^ (w if w>>i&1 else 0) for i in range(n))
def port_basis(n,u):
    assert parity(u)==1 and u != (1<<n)-1
    j=next(j for j in range(n) if not u>>j&1)
    p=list(eye(n));p[0],p[j]=p[j],p[0]
    a=mul(transvection(n,u^(1<<j)),p)
    assert a[0]==u and orth(a)
    return a
def projector(b,s):
    dirs=[b[i] for i in s]
    return tuple(mv(dirs, sum(((v>>j)&1)<<i for i,v in enumerate(dirs))) for j in range(len(b)))
def phase_of_matrix(a):
    return (tuple(x.bit_count()%4 for x in a),
            tuple(2*parity(a[i]&a[j]) for i in range(len(a)) for j in range(i+1,len(a))))
def phase_of_directions(n,dirs):
    linear=[0]*n; cross=[0]*(n*(n-1)//2)
    for v,e in dirs:
        support=[i for i in range(n) if v>>i&1]
        for pos,i in enumerate(support):
            linear[i]=(linear[i]+e)%4
            for j in support[pos+1:]:
                k=i*(2*n-i-1)//2+j-i-1
                cross[k]=(cross[k]+2*e)%4
    return tuple(linear),tuple(cross)

def padd(p,q): return tuple(tuple((a+b)%4 for a,b in zip(x,y)) for x,y in zip(p,q))
def phase_value(p,z,n):
    s=sum(p[0][i] for i in range(n) if z>>i&1); k=0
    for i in range(n):
        for j in range(i+1,n):
            if (z>>i&1) and (z>>j&1): s+=p[1][k]
            k+=1
    return s%4

def binding(root=ROOT):
    records=json.loads((root/'PROVENANCE.json').read_text())['sources']
    for r in records:
        b=(root/r['packet_path']).read_bytes()
        assert len(b)==r['bytes']
        assert hashlib.sha256(b).hexdigest()==r['sha256']
        assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob']
    return len(records)

def endpoint_provenance(c):
    decoded=gzip.decompress((E8/'data/prefix18.json.gz').read_bytes())
    digest=hashlib.sha256(decoded).hexdigest()
    assert digest=='ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a'
    assert digest in (E8/'research-notes/structural-heterogeneous-proof.md').read_text()
    audit=json.loads((E8/'data/sink-audit.json').read_text())
    mapping={a['sink_helper']:a['frame'] for a in audit['accepted']}
    assert mapping=={355:206,403:221}
    assert c['final'][355]==c['final'][403]==1
    assert c['frames'][206]==[260,132,68,36,20,12,2,1]
    assert c['frames'][221]==[257,129,65,33,17,8,4,3]
    return dict(decoded_sha256=digest,binary_final={355:1,403:1},
                changed_walk_sink_frames=mapping,
                mapping_source='PR390 data/sink-audit.json; code/complex-hetero-compose.py overrides final from accepted records',
                scope='frame contents and declared sink mapping checked; modified walk not executed or certified')

def b3_schedule(h, omit_first_alignment=False):
    m=7*h; allset=set(range(m));pivot={0};block=set(range(h))
    ax=[block | {j for j in range(h,(k+1)*h) if j%h} for k in range(7)]
    ay=[s-pivot for s in ax]
    frames=[pivot.copy(),set()]*3
    rows=[[int(i==j) for j in range(6)] for i in range(6)]
    idle=[[] for _ in range(6)]
    def climb(r,to,paid=True):
        assert frames[r]<=to
        n=len(to-frames[r])
        if n and paid: idle[r].append(n)
        frames[r]=to.copy()
    def add(t,s,a):
        assert frames[t]==frames[s]
        rows[t]=[x+a*y for x,y in zip(rows[t],rows[s])]
    for k in range(7):
        p=0 if k<3 else (k-1)//2;x=2*p;y=x+1
        expected=(pivot,set()) if k==0 else (ax[k-1],ay[k-1])
        assert frames[x]==expected[0] and frames[y]==expected[1]
        # Scalar invocation acts on differently framed X/Y by its assumed route.
        t,s,a=(y,x,1) if k%2==0 else (x,y,-1)
        rows[t]=[u+a*v for u,v in zip(rows[t],rows[s])]
        climb(x,ax[k],False);climb(y,ay[k],False)
        if k in (1,2,3,4):
            q=1 if k<3 else 2
            for r in range(2):
                if not (omit_first_alignment and k==1): climb(2*q+r,frames[2*(q-1)+r])
            if k%2: add(2*q-2,2*q,1);add(2*q+1,2*q-1,-1)
            else: add(2*q+1,2*q-1,1);add(2*q-2,2*q,-1)
    for r in range(6): climb(r,allset if r%2==0 else allset-pivot)
    for q in (2,1): add(2*q-1,2*q+1,-1);add(2*q,2*q-2,1)
    assert rows==[row for p in range(3) for row in [[-int(j==2*p+1) for j in range(6)],[int(j==2*p) for j in range(6)]]]
    expected=[[4*h+2],[4*h+2],[2*h-2,h-1,2*h+4],[2*h-2,h-1,2*h+4],[4*h-4,h-1,6],[4*h-4,h-1,6]]
    assert idle==expected
    assert all(0<r<m for rs in idle for r in rs)
    return idle

def b3_geometry():
    counts=Counter();h=9;n=63;I=eye(n)
    owners=[I,mul(transvection(n,15),transvection(n,30))]
    assert owners[1]!=tr(owners[1])
    for u in range(1,1<<h):
        if parity(u)==0 or u==511:continue
        a=port_basis(h,u);D=a+I[h:]
        for g in owners:
            B=mul(g,D)
            for k in range(1,7):
                pi=list(I)
                for j in range(1,h): pi[j],pi[k*h+j]=pi[k*h+j],pi[j]
                rho=mul(mul(D,pi),tr(D));d=mul(g,rho)
                assert mul(rho,rho)==I and mul(d,D)==mul(B,pi)
                q={j for j in range(h,(k+1)*h) if j%h}
                incoming={*range(h)}|{j for j in range(h,k*h) if j%h}
                out={*range(h)}|q
                for local,expected in [(q|{0},incoming),(q,incoming-{0}),
                                       (q|set(range(h)),out),(q|set(range(1,h)),out-{0})]:
                    assert projector(mul(d,D),local)==projector(B,expected)
                    counts['boundary_matrix_equalities']+=1
            subsets=[{j for j in range(h,(k+1)*h) if j%h} for k in range(1,7)]
            for s in subsets:
                P=projector(B,s)
                assert phase_of_matrix(P)==phase_of_directions(n,[(B[i],B[i].bit_count()) for i in s])
                counts['signed_block_polynomial_equalities']+=1
            line=projector(B,{0});rest=tuple(x^y for x,y in zip(I,line))
            translation=phase_of_directions(n,[(B[0],2)])
            assert padd(phase_of_matrix(I),phase_of_matrix(line))==padd(translation,phase_of_matrix(rest))
            counts['terminal_polynomial_equalities']+=1
    for g in owners:
        prefix=tuple(0 for _ in range(n)); phases=phase_of_matrix(prefix)
        for k in range(7):
            tau=list(I)
            for j in range(h):tau[j],tau[k*h+j]=tau[k*h+j],tau[j]
            d=mul(g,tau);win=projector(d,set(range(h)))
            expected=projector(g,set(range(k*h,(k+1)*h)))
            assert win==expected
            prefix=tuple(x^y for x,y in zip(prefix,win));phases=padd(phases,phase_of_matrix(win))
            assert phases==phase_of_matrix(prefix)
            counts['helper_prefix_equalities']+=1
        assert prefix==I
    for h in range(2,17): b3_schedule(h)
    counts['ports']=255;counts['owners']=2;counts['schedule_dimensions']=15
    return dict(counts,idle_h9=b3_schedule(9),unsigned_counterexample=dict(n=4,direction=14,character=2,rank_one_phase=3,unsigned_phase=1),omitted_terminal_translation=dict(u=1,z=1,phase_error=2))

def rot(a,k):
    x,y=a
    return [(x,y),(-y,x),(-x,-y),(y,-x)][k%4]
def cstep(state,v,sgn):
    out={}
    for x,a in state.items():
        ia=rot(a,sgn); ia2=rot(a,-sgn)
        for key,b in [(x,(a[0]+ia[0],a[1]+ia[1])),(x^v,(a[0]+ia2[0],a[1]+ia2[1]))]:
            old=out.get(key,(0,0));out[key]=(old[0]+b[0],old[1]+b[1])
    return {k:v for k,v in out.items() if v!=(0,0)}
def canonical_diag(E,n):
    ext=list(E)
    for e in eye(n):
        if rank(ext+[e])>len(ext):ext.append(e)
    assert len(ext)==n
    gi=inv(ext)
    Q=tuple((1<<i)^sum(parity(gi[i]&gi[j])<<j for j in range(n)) for i in range(n))
    def diagphase(x):
        return (sum((Q[i]>>i)&1 for i in range(n) if x>>i&1)+
                2*sum((Q[i]>>j)&1 for i in range(n) for j in range(i+1,n) if (x>>i&1) and (x>>j&1)))%4
    return Q,diagphase

def validate_adapter_recipe(recipe,columns):
    assert len(columns)==512
    poly=(recipe['linear_Z4'],recipe['quadratic_coefficients'])
    mismatches=[x for x,(y,p) in enumerate(columns)
                if y != (mv(recipe['matrix_columns'],x)^recipe['offset'])
                or p != (recipe['phase']+phase_value(poly,x,9))%4]
    if mismatches:
        raise ValueError(f"adapter frame {recipe['frame']}: {len(mismatches)}/512 column mismatches; first {mismatches[0]}")
    return len(columns)

def literal_adapters(c,column_cache=None):
    records=[]
    for fid,q in [(206,508),(221,499)]:
        E=c['frames'][fid];U=port_basis(9,q)
        assert len(E)==rank(E)==8 and all(parity(v&q)==0 for v in E)
        Q,diag=canonical_diag(E,9);outputs=[];phases=[]
        for x in range(512):
            state={x:rot((1,0),-diag(x))}
            # T_E^-1 = D_Q (product C_E^-1) D_Q^-1.
            for v in E:state=cstep(state,v,-1)
            state={y:rot(a,diag(y)) for y,a in state.items()}
            # R = F_q T_E^-1, F_q = product over columns U[1:9].
            for v in U[1:]:state=cstep(state,v,1)
            assert len(state)==1,(fid,x,len(state))
            y,a=next(iter(state.items()));outputs.append(y)
            phase=next(k for k in range(4) if a==rot((1<<16,0),k));phases.append(phase)
        offset=outputs[0];M=tuple(outputs[1<<i]^offset for i in range(9));p=phases[0]
        alpha=[(phases[1<<i]-p)%4 for i in range(9)]
        cross=[(phases[(1<<i)|(1<<j)]-p-alpha[i]-alpha[j])%4 for i in range(9) for j in range(i+1,9)]
        assert all(a in (0,2) for a in cross)
        poly=(tuple(alpha),tuple(cross))
        assert rank(M)==9
        for x in range(512):
            assert outputs[x]==mv(M,x)^offset
            assert phases[x]==(p+phase_value(poly,x,9))%4
        assert (offset,p)==((505,3) if fid==206 else (502,3))
        assert alpha==[2 if i==(2 if fid==206 else 0) else 0 for i in range(9)]
        assert all(parity(v&q)==0 for v in U[1:]) and q.bit_count()%4==3
        records.append(dict(frame=fid,normal=q,literal_frame=E,orthogonal_columns=U,offset=offset,phase=p,matrix_columns=M,linear_Z4=alpha,quadratic_coefficients=cross,basis_columns_checked=512,rank8_character_phase=0,rank9_character_phase=3))
        columns=list(zip(outputs,phases))
        validate_adapter_recipe(records[-1],columns)
        if column_cache is not None:column_cache[fid]=columns
    return records

def placement(src,off,n=73):
    remaining=iter(i for i in range(n) if i not in range(off,off+len(src)))
    d={s:off+i for i,s in enumerate(src)}
    return tuple(1<<(d[i] if i in d else next(remaining)) for i in range(n))
def endpoint_banks(c):
    small=[(r,h) for r in range(32) for h in range(240,1023) if h in (355,403)]
    large=[(r,h) for r in range(32) for h in range(240,1023) if h not in (355,403)]
    assignments=[];routes=[];route_ids={};coverage=[set() for _ in range(3131)]
    def put(role,bank,off,r):
        rep,h=role
        if r==8:
            q=508 if h==355 else 499;U=port_basis(9,q)+eye(73)[9:]
            A=mul(placement(list(range(1,9)),off),tr(U))
            assert all(mv(A,U[i])==1<<(off+i-1) for i in range(1,9))
            E=c['frames'][206 if h==355 else 221]
            image=[mv(A,e) for e in E]
            assert rank(image)==8 and all(x&~(((1<<8)-1)<<off)==0 for x in image)
        else:A=placement(list(range(9)),off)
        if A not in route_ids:
            assert orth(A);route_ids[A]=len(routes);routes.append(A)
        assert not coverage[bank]&set(range(off,off+r));coverage[bank].update(range(off,off+r))
        assignments.append((rep,h,bank,off,r,route_ids[A]))
    si=li=padding_per_stage=0
    for bank in range(3131):
        if bank<8:
            put(large[li],bank,0,9);li+=1
            for j in range(8):put(small[si],bank,9+8*j,8);si+=1
        else:
            for j in range(8):put(large[li],bank,9*j,9);li+=1
            assert 72 not in coverage[bank];coverage[bank].add(72)
            padding_per_stage+=1
    assert si==len(small)==64 and li==len(large)==24992
    assert all(s==set(range(73)) for s in coverage)
    byrole={(r,h):(b,off,n,aid) for r,h,b,off,n,aid in assignments}
    recipe=json.loads((ROOT/'source-excerpts/RECIPE-9.json').read_text())
    calls=[];call_count=adapter_count=0;live_families=set()
    for e in recipe:
        if e['kind']!='local':continue
        s,p=e['stage'],e['pair'];ori='backward' if e['reverse'] else 'forward'
        calls.append((s,p,ori))
        for r in range(32):
            call_count+=1
            adapter_count+=sum(byrole[r,h][2]==8 for h in range(240,1023))
            owners=[(r*960+(2*p+h//120)*120+h%120,('data',s,h%120)) for h in range(240)]
            owners += [(30720+s*3131+byrole[r,h][0],('helper',byrole[r,h][3])) for h in range(240,1023)]
            assert len(set(owners))==1023
            assert all(0<=f<58899 for f,_ in owners)
            live_families.update(f for f,_ in owners)
    assert calls==[(0,0,'forward'),(1,0,'backward'),(2,0,'forward'),(3,1,'backward'),(4,1,'forward'),(5,2,'backward'),(6,2,'forward'),(7,3,'backward'),(8,3,'forward')]
    # For owner g=I, correct invocation d=A; wrong g=d*A gives d=A^-1.
    arow=next(t for t in assignments if routes[t[-1]]!=tr(routes[t[-1]]))
    _,h,bank,off,r,aid=arow;A=routes[aid];Ai=tr(A)
    correct=[1<<i for i in range(73)]
    wrong=[v for i,v in enumerate(correct) if i not in range(off,off+r)]+[mv(mul(Ai,Ai),1<<i) for i in range(off,off+r)]
    witness=next(z for z in range(1,512) if sum(parity(v&z) for v in wrong)%4!=z.bit_count()%4)
    assert live_families==set(range(len(live_families)))
    return dict(slots=len(assignments),rank8=si,rank9=li,banks=len(coverage),routes=len(routes),nonsymmetric_routes=sum(a!=tr(a) for a in routes),calls=call_count,padding_calls=len(calls)*padding_per_stage,adapter_uses=adapter_count,live=len(live_families),source_declared_physical=59692,rank_mass_per_stage=sum(t[4] for t in assignments)+padding_per_stage,local_sequence=calls,wrong_inverse=dict(assignment=arow,character=witness,correct_phase=witness.bit_count()%4,wrong_phase=sum(parity(v&witness) for v in wrong)%4))

def completion_small():
    count=0
    # Exhaustive signed multiplicities mod4 for every nonzero direction in F2^3.
    n=3
    for eps in product(range(4),repeat=7):
        dirs=list(zip(range(1,8),eps));K=tuple(mv([v for v,e in dirs if e%2],sum(((v>>i)&1)<<j for j,(v,e) in enumerate([(v,e) for v,e in dirs if e%2]))) for i in range(n))
        p=phase_of_directions(n,dirs)
        found=[]
        for delta in range(8):
            if all(phase_value(p,z,n)==(z.bit_count()+2*parity(delta&z))%4 for z in range(8)):found.append(delta)
        assert bool(found)==(K==eye(n))
        if found:
            ns=[sum(e*((v>>i)&1) for v,e in dirs) for i in range(n)]
            assert found==[sum((((a-1)//2)%2)<<i for i,a in enumerate(ns))]
        count+=1
    return count

