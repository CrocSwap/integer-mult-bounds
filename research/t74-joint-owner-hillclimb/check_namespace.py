"""Independent register injection for the actual changed native programs.

Reuses the free-warp/Horner test pattern from the PR2288 namespace supplement.
Borrowing/compiler credit remains Cinna Davis (PR2226), Kothe, and WildIdeas;
PR2312 supplies the later width exchange and extra proper ends. This checks
existing emitted programs and does not replace native phase certification.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, collections, gzip, hashlib, json

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
parser.add_argument('--hosted',type=Path,required=True,
    help='Actual final strict/global/hosted directory, not the inherited data template')
parser.add_argument('--base-native',type=Path,required=True)
parser.add_argument('--extra-native',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--owners',type=Path,help='Defaults to PACKAGE/data/OWNERS.json.gz')
args=parser.parse_args()
PKG=args.package.resolve()
RUNTIME=args.hosted.resolve()
NATIVES={'base':args.base_native.resolve(),'extra':args.extra_native.resolve()}
OUT=args.out.resolve()
def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def add(a,b,q):
    for k,v in b.items():
        z=a.get(k,Q(0))+q*v
        if z:a[k]=z
        else:a.pop(k,None)
def scale(a,q):return {k:q*v for k,v in a.items() if q*v}

owner_path=args.owners.resolve() if args.owners else PKG/'data/OWNERS.json.gz'
t=read(RUNTIME/'GLOBAL-TEMPLATE.json.gz');owners=read(owner_path)
base_canon=read(NATIVES['base']/'local/CANONICAL-WORD.json.gz')
R=base_canon['R'];assert R==read(PKG/'CLAIM.json')['native_helpers']
V=base_canon['v'];assert V==112
C=len(base_canon['centers']);assert C==8
NZ=len(base_canon['zero_buffers']);assert 0<NZ<=R
DATA=t['live'];L=2*V+R;PHYS=DATA+C+R+2
assert DATA==66304 and t['physical']==PHYS
assert t['private_namespace']=={'centers':[DATA,DATA+C],
    'reserved_tableau':[DATA+C,DATA+C+R],'coefficient':[PHYS-2,PHYS]}
owned={}
for x in owners:
    key=(x['stage'],x['replica']);row=owned.setdefault(key,{})
    assert x['helper'] not in row and 0<=x['family']<DATA
    row[x['helper']]=x['family']
assert len(owned)==666 and len(owners)==666*R
liveids={}
for c in t['calls']:
    key=(c['stage'],c['replica']);ids=[x[0] for x in c['owners']]
    assert len(ids)==len(set(ids))==L and min(ids)>=0 and max(ids)<DATA
    assert set(owned[key])==set(range(R))
    assert ids[224:]==[owned[key][j] for j in range(R)]
    liveids[key]=ids
assert len(liveids)==666
reports={};source_bindings={'candidate/OWNERS.json.gz':digest(owner_path),
    'hosted/GLOBAL-TEMPLATE.json.gz':digest(RUNTIME/'GLOBAL-TEMPLATE.json.gz')}
for name in ['base','extra']:
    local=NATIVES[name]/'local'
    canon=read(local/'CANONICAL-WORD.json.gz');programs=read(local/'LOCAL-PROGRAMS.json.gz')
    assert canon['R']==R and canon['v']==112
    pid='gauge44' if name=='base' else 'extra'
    registry=t['local_providers'][pid]
    assert registry['R']==R and registry['v']==V and registry['local_programs']==programs
    widths=[len(canon['frames'][f])-len(canon['frames'][s]) for f,s in zip(canon['final'][2*V:],canon['start'][2*V:])]
    assert widths==registry['widths']
    zs=sorted(canon['zero_buffers']);assert len(zs)==len(set(zs))==NZ
    zp={z:DATA+C+j for j,z in enumerate(zs)};cp={j:DATA+j for j in range(C)}
    work=[PHYS-2,PHYS-1];aux=set(zp.values())|set(cp.values())|set(work)
    assert len(aux)==NZ+C+2 and min(aux)==DATA and max(aux)==PHYS-1
    assert max(zp.values())<DATA+C+R and not set(zp.values())&set(work)
    for ids in liveids.values():assert not set(ids)&aux
    directions={}
    for orientation,events in programs.items():
        state={('L',j):{(j,()):Q(1)} for j in range(L)}
        active=set();alloc=collections.Counter();free=collections.Counter();peak=horner=0
        lid=next(iter(liveids.values()))
        def phys(r):
            typ,j=r
            return lid[j] if typ=='L' else cp[j] if typ=='C' else zp[j]
        for e in events:
            if e[0]=='zero_buffer':
                _,kind,z=e
                if kind=='alloc':
                    assert z not in active;active.add(z);state['Z',z]={};alloc[z]+=1;peak=max(peak,len(active))
                else:
                    assert z in active and not state['Z',z];active.remove(z);free[z]+=1
            elif e[0]=='warp':
                r=tuple(e[1]);assert r[0]!='Z' or r[1] in active
                op=e[2];state[r]={(var,w[1:] if w and w[0]==-op else (op,)+w):v for (var,w),v in state[r].items()}
            elif e[0]=='scalar':
                op=e[1];kind=op[0];target=tuple(op[1]);assert phys(target) not in work
                if target[0]=='Z':assert target[1] in active
                if kind=='clear':state[target]={}
                elif kind=='scale':state[target]=scale(state[target],Q(op[2],op[3]))
                else:
                    src=tuple(op[2]);assert phys(src) not in work and phys(src)!=phys(target)
                    if src[0]=='Z':assert src[1] in active
                    if kind=='copy':state[target]=dict(state[src])
                    else:
                        q=Q(op[3],op[4]);a,b=abs(q.numerator),q.denominator
                        assert b&(b-1)==0
                        tmp={}
                        for bit in bin(a)[2:]:
                            tmp=scale(tmp,Q(2))
                            if bit=='1':add(tmp,state[src],Q(1))
                        for _ in range(b.bit_length()-1):tmp=scale(tmp,Q(1,2))
                        assert tmp==scale(state[src],abs(q))
                        add(state.setdefault(target,{}),tmp,Q(1 if q>0 else -1));tmp={};horner+=1
                        assert not tmp
        assert not active and set(alloc)==set(free)==set(zs)
        assert all(alloc[z]==free[z]==1 for z in zs)
        assert all(not v for (typ,j),v in state.items() if typ in ['Z','C'])
        for j in range(L):
            want={(j,()):Q(1)}
            if orientation=='backward' and j<112:want[(112+j,())]=Q(-1)
            if orientation=='forward' and 112<=j<224:want[(j-112,())]=Q(1)
            assert state['L',j]==want,(name,orientation,j)
        directions[orientation]={'arbitrary_L_columns':L,'exact_endpoint':True,
            'buffers_zero_on_allocate_and_free':NZ,'buffers_peak':peak,
            'centers_zero_at_exit':True,'literal_Horner_macros_checked':horner}
    for fn in ['CANONICAL-WORD.json.gz','LOCAL-PROGRAMS.json.gz']:
        source_bindings[f'{name}-native/local/{fn}']=digest(local/fn)
    reports[name]={'Z_to_physical':zp,'directions':directions}
result={'status':'PASS_ACTUAL_CHANGED_PRIVATE_NAMESPACE_INJECTION',
    'geometry':{'live':DATA,'centers':[DATA,DATA+C],
        'reserved_tableau':[DATA+C,DATA+C+R],'coefficient':[PHYS-2,PHYS],
        'physical':PHYS,'buffer_fields':[DATA+C,DATA+C+NZ],
        'remaining_reserve':R-NZ,'native_helpers':R,'arbitrary_local_columns':L,'zero_buffers':NZ},
    'all_calls':len(liveids),'all_helper_owners':len(owners),
    'all_local_families_in_each_call_distinct_and_live':True,
    'all_private_names_disjoint_from_live_and_each_other':True,
    'providers':reports,'source_sha256':source_bindings,
    'scope':'Explicit actual runtime register injection and arbitrary-dirt scalar/free-warp/Horner endpoints. Every buffer fits in the already priced private reserve; native phases and complete finite invoice are separate replay obligations.'}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['providers','source_sha256']},indent=2))
