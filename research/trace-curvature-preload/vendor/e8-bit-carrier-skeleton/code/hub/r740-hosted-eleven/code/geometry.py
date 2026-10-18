"""Exact compressed eleven-stage E8 bit geometry; no external research fetches.

Prepared by Zhihao Chen with OpenAI Codex assistance, Apache-2.0.
Eleven-stage extension by chafreaky with OpenAI Codex assistance.
Uses the E8 root data and port-reflection construction credited to PR #370.
"""
import argparse, gzip, hashlib, json, time
from pathlib import Path
import sympy as S

def dump(p, x): p.write_text(json.dumps(x,indent=2,default=str)+'\n')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def factor(a):
    """Exact elementary factorization, reconstructed from the identity."""
    n=a.rows; z=a.copy(); ops=[]
    for j in range(n):
        p=next(i for i in range(j,n) if z[i,j])
        if p!=j: z.row_swap(p,j); ops.append(['swap',p,j,None])
        if z[j,j]!=1:
            c=1/z[j,j]; z[j,:]=c*z[j,:]; ops.append(['scale',j,None,c])
        for i in range(n):
            if i!=j and z[i,j]:
                c=-z[i,j]; z[i,:]=z[i,:]+c*z[j,:]; ops.append(['add',i,j,c])
    assert z==S.eye(n)
    def replay(skip=-1):
        z=S.eye(n)
        for k in reversed(range(len(ops))):
            if k==skip: continue
            typ,i,j,c=ops[k]
            if typ=='swap': z.row_swap(i,j)
            elif typ=='scale': z[i,:]=z[i,:]/c
            else: z[i,:]=z[i,:]-c*z[j,:]
        return z
    assert replay()==a
    assert ops and replay(0)!=a
    return [[t,i,j,None if c is None else str(c)] for t,i,j,c in ops]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); t0=time.monotonic()
    a.out.mkdir(parents=True,exist_ok=True)
    p=a.source/'data/bit/bitE8-r865.json.gz'; w=json.loads(gzip.decompress(p.read_bytes()))
    assert (w['h'],w['v'],w['R'],w['form'])==(8,120,865,'<x,y>/2')
    lines=[S.Matrix(x) for x in w['lines']]; I=S.eye(8); Z=S.zeros(8)
    assert lines[0]==S.Matrix([2,0,0,0,0,0,0,0])
    ip=lambda u,v:(u.T*v)[0]/2
    gs={0:I}; todo=[0]
    while todo:
        more=[]
        for i in todo:
            for j in range(120):
                if j in gs or abs(ip(lines[i],lines[j]))!=1: continue
                d=lines[i]-lines[j] if ip(lines[i],lines[j])==1 else lines[i]+lines[j]
                r=I-d*d.T/(d.T*d)[0]*2
                gs[j]=r*gs[i]; more.append(j)
        todo=more
    assert len(gs)==120
    recipes=[]; denoms=set(); max_factors=0
    for t,q in enumerate(lines):
        g=gs[t]; assert g.T*g==I and g*lines[0] in (q,-q)
        P=q*q.T/4; K=I-P; A=g[:,1:]
        assert A.T*A==S.eye(7) and A*A.T==K and P*A==S.zeros(8,7)
        rho=P.row_join(A).col_join(A.T.row_join(S.zeros(7)))
        assert rho.T==rho and rho*rho==S.eye(15)
        expected={'P':S.diag(I,S.zeros(7)), 'H':S.eye(15),
                  '0':S.diag(K,S.zeros(7)), 'K':S.diag(K,S.eye(7))}
        for name,U in [('P',P),('H',I),('0',Z),('K',K)]:
            assert rho*S.diag(U,S.eye(7))*rho==expected[name]
        # Exact bit address operators D_U: head/tail exchange on U.
        # Unlike complex C_U, they carry no omitted scalar/translation phase.
        def D(U): return (I-U).row_join(U).col_join(U.row_join(I-U))
        assert D(I)*D(P)==D(K) and D(P)*D(P)==S.eye(16)
        ops=factor(rho); max_factors=max(max_factors,len(ops))
        for typ,i,j,c in ops:
            if c is not None: denoms.add(int(S.Rational(c).q))
        # Compact exact global matrices: these 15 axes are the first eight
        # local coordinates and exterior block s. All other axes are fixed.
        routes=[dict(stage=0,axes=list(range(8)),identity=True)]
        for s in range(1,11):
            axes=list(range(8))+list(range(8+7*(s-1),8+7*s))
            assert len(set(axes))==15 and max(axes)<78
            routes.append(dict(stage=s,axes=axes,elementary_inverse_replay=ops))
        recipes.append(dict(port=t,q=list(map(int,q)),complement_columns=[[str(x) for x in row] for row in A.tolist()],
                            rho15=[[str(x) for x in row] for row in rho.tolist()],routes=routes))
        if t%30==0: print('compressed geometry',t+1,flush=True)
    # Exact nested data levels: local I (or K_q) plus s exterior rank-7
    # blocks. Width 78=8+10*7; each bridge sees identical complete operators.
    idle=[]
    for j in range(1,5):
        idle += [dict(pair=j,source_level=-1,target_level=2*j-1,rank=14*j,phase='before_positive_bridge'),
                 dict(pair=j,source_level=2*j-1,target_level=2*j,rank=7,phase='before_negative_bridge')]
    for j in range(5):
        idle.append(dict(pair=j,source_level=2*j+2,target_level=10,rank=14*(4-j),phase='terminal'))
    assert sum(z['rank'] for z in idle)==308
    # Every residual is hosted in a data family; no helper bank exists.
    slots=[];perms=[]
    out=dict(status='PASS_COMPRESSED_ELEVEN_BIT_GEOMETRY',h=8,m=78,stages=11,
             word_sha256=digest(p),ports=recipes,idle_per_port_and_data_member=idle,
             local_window='U direct_sum E_s, with E_s the first s exterior coordinate 7-blocks',
             ambient_form='I_78/2',bank_slots=slots,bank_permutations=perms,
             route_checks=1320,exact_bit_endpoint_operator_checks=240,
             max_route_factors=max_factors,route_denominators=sorted(denoms),
             bad_prime_factors=sorted({int(q) for d in denoms for q in S.factorint(d)}),
             missing_route_factor_controls=120,bank_free=True,
             scope='All port isometries, stage boundary identities, nested idle ranks, exact bit endpoint operators and coordinate embeddings. No residual banks are used. Full local-word scalar and chronological lowering are checked separately.',
             seconds=time.monotonic()-t0)
    dump(a.out/'GEOMETRY.json',out)
    print(json.dumps({k:v for k,v in out.items() if k not in ('ports','bank_permutations','idle_per_port_and_data_member')}),flush=True)

if __name__=='__main__': main()
