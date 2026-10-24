"""Actual-tableau Fourier-rank census for block realification, ell=1,3.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
Ranks are exact necessary prices, not a native/phase/recursive admission.
"""
from collections import Counter
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
CE='research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py'


def need(ok,message):
    if not ok:raise ValueError(message)


def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def action(columns,vector):
    out=0
    while vector:
        bit=vector&-vector
        out^=columns[bit.bit_length()-1]
        vector^=bit
    return out


def compose(a,b):return tuple(action(a,col) for col in b)


def tabcols(op):return tuple(x|(z<<op.n) for x,z,_ in op.tab)


def tensor_columns(columns,ell):
    m=len(columns)//2;n=m*ell;mask=(1<<m)-1
    out=[]
    for kind in (0,1):
        for block in range(ell):
            for i in range(m):
                col=columns[kind*m+i]
                out.append(((col&mask)<<(m*block))|((col>>m)<<(n+m*block)))
    return tuple(out)


def tensor_pauli(x,z,m,ell):
    n=m*ell
    return sum(x<<(m*j) for j in range(ell))|sum(z<<(n+m*j) for j in range(ell))


def transvection(columns,w):
    n=len(columns)//2;mask=(1<<n)-1;x=w&mask;z=w>>n
    return tuple(col^(w if (((col&mask)&z).bit_count()+((col>>n)&x).bit_count())%2 else 0)
                 for col in columns)


def f_rank(ce,columns):
    n=len(columns)//2;mask=(1<<n)-1
    return ce.rank([col&mask for col in columns[n:]])


def counter_data(counter):return {str(k):v for k,v in sorted(counter.items()) if v}
def mass(counter):return sum(k*v for k,v in counter.items())


def Kop(ce,columns):
    G=ce.transpose(tuple(columns),9);gi=ce.inv(G,9);tr=ce.transpose(gi,9)
    quadratic=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(tr)) for i,a in enumerate(tr))
    return ce.perm(9,G).then(ce.diag(9,quadratic))


def frame_data(ce,basis):
    """Actual canonical K chart and actual Pauli F^2, never raw BB^t."""
    r=len(basis);F=ce.canonical_frame(9,basis)
    if r in (0,9):K=ce.ident(9)
    else:K=Kop(ce,ce.basis_extend(basis,9))
    x,z,phase=ce.apply(K.tab,((1<<r)-1,0,0))
    need((phase+(x&z).bit_count())%2==0,'Actual square Pauli is Hermitian')
    # Verify the actual global phase of F^2 on all 512 amplitudes of |0>.
    square=F.then(F);vec,den=square.zero_state()
    pauli_tableau=tuple([(1<<i,0,2*((z>>i)&1)) for i in range(9)]+
                        [(0,1<<i,2*((x>>i)&1)) for i in range(9)])
    need(square.tab==pauli_tableau,'Full square-Pauli tableau on all eighteen generators')
    expected=[(0,0)]*512;expected[x]=ce.mul_i((1,0),phase)
    need(den==0 and vec==expected,'Actual F^2 Pauli including absolute phase')
    return F,(x,z,phase),K


def census(ce,payload,name,ell):
    c=payload['canonical'];programs=payload.get('programs',payload.get('extended'))
    forward=programs['forward'];backward=programs['backward']
    need(Counter(tuple(e[3:]) for e in forward if e[0]=='climb')==
         Counter(tuple(e[3:]) for e in backward if e[0]=='climb'),'Both orientations paid references')
    used={i for e in forward if e[0] in ('climb','warp','center') for i in e[-3:-1]}
    # Explicit extraction avoids event-grammar positions being conflated.
    used=set(c['start'])|set(c['final'])
    for e in forward:
        if e[0] in ('climb','warp'):used.update(e[3:5])
        elif e[0]=='center':used.update(e[2:4])
    regular={};phi={};actual_paulis={};Kcharts={}
    cache={}
    for frame in sorted(used):
        basis=tuple(c['frames'][frame])
        if basis not in cache:cache[basis]=frame_data(ce,basis)
        F,(x,z,p),K=cache[basis]
        normal=tensor_columns(tabcols(F),ell)
        changed=transvection(normal,tensor_pauli(x,z,9,ell))
        identity=tuple(1<<i for i in range(18*ell))
        need(compose(changed,changed)==identity,'Phi(F) is symplectically involutive')
        regular[frame]=normal;phi[frame]=changed;actual_paulis[frame]=(x,z,p);Kcharts[frame]=K
    warps={w['op']:Kop(ce,w['G_columns']) for w in c['warps']}
    def actualwarp(op):
        obj=warps[abs(op)] if op>0 else warps[abs(op)].adjoint()
        return tensor_columns(tabcols(obj),ell)
    relative_cache={};warp_cache={}
    def edge(a,b):
        key=(a,b)
        if key not in relative_cache:
            old=f_rank(ce,compose(regular[b],regular[a]))
            need(old==ell*(len(c['frames'][b])-len(c['frames'][a])) or
                 old==ell*(len(c['frames'][a])-len(c['frames'][b])),'Original exact nested-frame rank')
            relative_cache[key]=f_rank(ce,compose(phi[b],phi[a]))
        return relative_cache[key]
    paid=Counter();oldpaid=Counter();center=Counter();broken=Counter();warp_rows=[];counts=Counter()
    for e in forward:
        if e[0]=='climb':
            _,part,role,a,b,r=e;new=edge(a,b)
            oldpaid[r*ell]+=1;paid[new]+=1;counts['climbs']+=1
        elif e[0]=='center':
            _,role,a,b,r=e;new=edge(a,b)
            oldpaid[r*ell]+=1;paid[new]+=1;center[new]+=1;counts['owned_centers']+=1
        elif e[0]=='warp':
            _,role,op,a,b=e;key=(op,a,b)
            if key not in warp_cache:
                K=actualwarp(op)
                original=compose(regular[b],compose(K,regular[a]))
                need(f_rank(ce,original)==0,'Original exact native warp is free')
                changed=compose(phi[b],compose(K,phi[a]))
                warp_cache[key]=f_rank(ce,changed)
            rank=warp_cache[key];broken[rank]+=1
            if rank:warp_rows.append(dict(operator=op,source=a,target=b,rank=rank,role=role,
                                          source_square_pauli=list(actual_paulis[a]),target_square_pauli=list(actual_paulis[b])))
            counts['warps']+=1
    helpers=Counter();oldhelpers=Counter();helper_rows=[]
    coupled_roles=set(payload.get('source_roles',[])[112:]+payload.get('target_roles',[])[112:]) if name=='coupled120' else set()
    for role in range(224,632):
        a,b=c['start'][role],c['final'][role]
        old=ell*(len(c['frames'][b])-len(c['frames'][a]));new=edge(a,b)
        if role in coupled_roles:continue
        oldhelpers[old]+=1;helpers[new]+=1
        helper_rows.append(dict(role=role,source=a,target=b,old_rank=old,new_rank=new))
    main=Counter()
    for role in list(range(224))+sorted(coupled_roles):main[edge(c['start'][role],c['final'][role])]+=1
    # Fully charged optimistic rank census includes every occurrence of a
    # formerly free warp as a separate paid call of its actual Fourier rank.
    charged=paid+Counter({r:count for r,count in broken.items() if r})
    return dict(word=name,ell=ell,actual_address_dimension=9*ell,
                original_paid=counter_data(oldpaid),new_nested_and_center_paid=counter_data(paid),
                owned_center_paid=counter_data(center),all_warp_costs=counter_data(broken),
                charged_paid=counter_data(charged),productive_helpers=counter_data(helpers),
                original_productive_helpers=counter_data(oldhelpers),optimistic_main_targets=counter_data(main),
                original_paid_mass=mass(oldpaid),new_nested_and_center_paid_mass=mass(paid),
                broken_warp_paid_mass=mass(broken),charged_paid_mass=mass(charged),
                productive_helper_mass=mass(helpers),optimistic_main_mass=mass(main),
                optimistic_local_deficit=mass(charged)-mass(helpers)-mass(main),
                counts=dict(counts),unique_frames=len(used),unique_bases=len(cache),
                unique_paid_pairs=len(relative_cache),unique_warp_classes=len(warp_cache),
                broken_warp_occurrences=warp_rows,helper_rows=helper_rows,
                scope='Actual Clifford canonical frames and phase-bearing K_native recipes; exact Fourier-rank prices including broken warps. Missing main external adapters, absolute phase lowering, changed scalar endpoint proof, target independence, all-f tape closure and recursive moments are not granted admission by this census.')


def main():
    started=time.monotonic()
    pins=read(HERE/'SOURCES.json')
    for row in pins['files']:need(sha256((HERE/row['copy']).read_bytes()).hexdigest()==row['sha256'],'Source '+row['path'])
    ce=load(HERE/'sources'/CE,'realification_actual_clifford')
    jobs=[('selected112','research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'),
          ('coupled120','research/kappa-round5-coupled-main-20261022/INVOLUTIVE-WORD.json.gz')]
    rows=[]
    for name,path in jobs:
        data=read(HERE/'sources'/path)
        for ell in (1,3):
            row=census(ce,data,name,ell);rows.append(row)
            print('PASS_ACTUAL_PHI_RANK_CENSUS',name,ell,'deficit',row['optimistic_local_deficit'],
                  'broken_warp_mass',row['broken_warp_paid_mass'],'elapsed',round(time.monotonic()-started,2),flush=True)
    result=dict(status='PASS_ACTUAL_OPERATOR_BLOCK_REALIFICATION_RANK_CENSUS',new_kappa=False,
                candidate='Phi(F^tensor ell)=S((F^2)^tensor ell)*F^tensor ell, ell odd',
                actual_operator_construction='F=K F_standard K^dagger from exact canonical_frame; F^2=K X_((1<<r)-1) K^dagger including phase, not raw frame Gram.',
                rows=rows,source_manifest_sha256=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(),
                script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.monotonic()-started)
    raw=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    (HERE/'REALIFICATION-CENSUS.json.gz').write_bytes(gzip.compress(raw,mtime=0))


if __name__=='__main__':main()
