# Generalised from PR #443's global_kernel.py to an arbitrary odd stage count S = 2K+1 (compressed window m = 1+7S)
# by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  At the defaults (S = 9, 32 replicas) the emitted
# GLOBAL-TEMPLATE.json.gz and GLOBAL.json equal PR #443's (GLOBAL.json except wall-clock seconds).
# Kernel integration of PR436/PR386 by chafreaky, with OpenAI Codex assistance.
# Original copyright and attribution retained below. This variant uses explicit
# residual isometries and mixed-width banks; the original all-zero-start
# requirement is replaced by the verified kernel entrance contract.
"""Source-bound compressed S-stage (S = 2K+1 odd, default 9) bit template with independent replicas.
PR386 global identity and PR436 generalization by Zhihao Chen and eumemic,
with their disclosed OpenAI Codex and Anthropic Claude assistance, Apache-2.0.
PR439 explicit residual routes and this replication extension by chafreaky,
with OpenAI Codex assistance. All owner assignments and emitted calls are checked.
Historical PR386 regression is performed by the unchanged parent wrapper.
"""
import argparse, gzip, hashlib, json, struct, time
from collections import Counter
from pathlib import Path
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../e8-r740-replica32/code'))
from bank_routes_k import placement, validate_isometries
from config import REPLICAS

H,L,K,T,M=8,9,4,REPLICAS,64      # overwritten in main() from --stages / --replicas
NAMES={5:'FIVE',7:'SEVEN',9:'NINE',11:'ELEVEN',13:'THIRTEEN'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,indent=2)+'\n')

def recipe(K):
    out=[dict(kind='local',stage=0,pair=0,reverse=False)]; stage=1
    for j in range(K):
        out.append(dict(kind='local',stage=stage,pair=j,reverse=True)); stage+=1
        if j<K-1: out.append(dict(kind='bridge',dst=j,src=j+1,coefficient=1))
        out.append(dict(kind='local',stage=stage,pair=j,reverse=False)); stage+=1
        if j<K-1: out.append(dict(kind='bridge',dst=j,src=j+1,coefficient=-1))
    for j in reversed(range(K-1)): out.append(dict(kind='bridge',dst=j+1,src=j,coefficient=1))
    out.append(dict(kind='exchange'))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--local-check',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--isometries',type=Path,required=True)
    ap.add_argument('--stages',type=int,default=9); ap.add_argument('--replicas',type=int,default=REPLICAS)
    ap.add_argument('--no-banks',action='store_true',help='emit the parent without helper bank owners (helpers are placed at hosting emission)')
    a=ap.parse_args(); start=time.monotonic(); out=a.out; out.mkdir(parents=True,exist_ok=True)
    global L,K,T,M
    assert a.stages>=5 and a.stages%2==1; L=a.stages; K=(L-1)//2; T=a.replicas; M=1+7*L; NOBANK=a.no_banks
    if L!=9: assert NOBANK, 'bank tiling is only emitted for the nine-stage layout; use --no-banks and host every residual'
    DEFICIT=T*(2*K*120-9*H*L)
    wp=a.word; w=json.loads(gzip.decompress(wp.read_bytes()) if wp.suffix=='.gz' else wp.read_bytes())
    V,R=w['v'],w['R']; LOCAL=2*V+R; DATA=2*K*V*T; LIVE=DATA+L*R
    assert (w['h'],V,w['form'])==(8,120,'<x,y>/2')
    geo=json.loads((out/'GEOMETRY.json').read_text())
    assert geo['status']=='PASS_COMPRESSED_%s_BIT_GEOMETRY_AND_BANK_BLOCKS'%NAMES[L] and geo['stages']==L and geo['m']==M
    # the port routes depend only on the labels: same 120 label vectors, in the same order
    assert len(geo['ports'])==V and all(p['port']==t and p['q']==w['lines'][t] for t,p in enumerate(geo['ports']))
    rp=a.local_check/'records/249-records.bin'; raw=rp.read_bytes(); rec=list(struct.iter_unpack('<6i',raw))
    state=json.loads((a.local_check/'records/249-states.json').read_text())
    fs=json.loads((a.local_check/'records/frames.json').read_text())['frames']
    dims={int(f):z['dim'] for f,z in fs.items()}
    lg=json.loads((a.local_check/'cout/legality.json').read_text())
    cc=json.loads((a.local_check/'cout/columns.json').read_text())
    assert lg['status'].startswith('PASS') and cc['status'].startswith('PASS')
    assert (state['v'],state['n'])==(V,LOCAL) and lg['copies']==lg['erasures']==9
    ADDS=lg['common_frame_ADDs']
    assert cc['formal_columns_checked']==4*V+R and cc['local_scalar_additions']==ADDS
    initial=[state['initial'][str(i)] for i in range(LOCAL)]
    final=[state['final'][str(i)] for i in range(LOCAL)]
    assert all(dims[final[i]]==H for i in range(2*V,LOCAL))
    widths=[H-dims[initial[i]] for i in range(2*V,LOCAL)]
    ENT=sum(H-z for z in widths)
    if NOBANK: place,NB=None,None; LIVE=DATA
    else:
        place,NB=placement(widths,T,M)
        assert T%8==0 and T*(H*R-ENT)%M==0 and NB==T*(H*R-ENT)//M
        LIVE=DATA+L*NB
    isometries=json.loads(a.isometries.read_text())
    assert validate_isometries(isometries,w['frames'],w['lines'],dims)==set(initial[2*V:])
    streams={}; checks={}; localH=None
    for reverse in (False,True):
        cur=(final if reverse else initial)[:]+[-1]; val=[1<<i for i in range(LOCAL)]+[0]
        norm=[1]*LOCAL+[0]; maxnorm=1; center=None; hist=Counter(); events=[]; copies=0; adds=0
        dim=lambda f:H-dims[f] if reverse else dims[f]
        for op,x,y,c,f,z in (reversed(rec) if reverse else rec):
            if op==0:
                oldf,newf=(c,y) if reverse else (y,c)
                assert cur[x]==oldf and dim(newf)-dim(oldf)==f>=0
                cur[x]=newf
                if f: hist[f]+=1
                events.append([0,x,oldf,newf,f,int(reverse)])
            elif op==1:
                assert cur[x]==cur[y]==f and x!=y and x<LOCAL
                if center is not None: assert x!=center
                if y==LOCAL: assert center is not None
                if c&1: val[x]^=val[y]
                norm[x]+=abs(c)*norm[y]; maxnorm=max(maxnorm,norm[x]); adds+=1
                events.append([1,x,y,-c if reverse else c,f,int(reverse)])
            elif op==(3 if reverse else 2):
                assert center is None and y==LOCAL and cur[x]==c and val[LOCAL]==0
                copy_rank=abs(dim(c)-dim(f)); assert copy_rank==8
                assert z==(0 if reverse else copy_rank)
                center=x; cur[LOCAL]=f; val[LOCAL]=val[x]; norm[LOCAL]=norm[x]
                hist[copy_rank]+=1; copies+=1; events.append([2,x,LOCAL,c,f,copy_rank,int(reverse)])
            else:
                assert op==(2 if reverse else 3)
                assert center==x and y==LOCAL and cur[x]==c and cur[LOCAL]==f
                assert val[LOCAL]==val[x]
                val[LOCAL]=0; norm[LOCAL]=0; cur[LOCAL]=-1; center=None
                events.append([3,x,LOCAL,c,f,z,int(reverse)])
        assert center is None and copies==9 and adds==ADDS
        assert cur[:LOCAL]==(initial if reverse else final)
        for i in range(LOCAL):
            want=(1<<i) ^ ((1<<(i-V)) if V<=i<2*V else 0)
            assert val[i]==want
        assert val[LOCAL]==0
        if localH is None: localH=hist
        else: assert localH==hist
        key='reverse' if reverse else 'forward'; streams[key]=events
        checks[key]=dict(copies=copies,adds=adds,records=len(events),all_columns=LOCAL,
                         cancellation_free_row_l1=maxnorm,profile=dict(sorted(hist.items())),
                         sha256=hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest())
    assert sum(r*n for r,n in localH.items())==H*R-ENT+72+2*V*(H-1)
    assert localH==Counter({int(r):n for r,n in cc['local_raw_H']})

    events=recipe(K); levels=[-1]*K; schedule=[]; bridge_controls=[]
    # Full scalar replay on separate dirty helpers for all nine stages.
    # Physical banking then uses the separately checked injective cover owners.
    n=2*K*V+L*R; vals=[1<<i for i in range(n)]+[0]; temp=n
    stages=[]
    for e in events:
        if e['kind']=='local':
            s,p,rev=e['stage'],e['pair'],e['reverse']; assert levels[p]==s-1
            def mapper(i):
                if i==LOCAL: return temp
                if i<2*V:
                    side=i//V; side=1-side if rev else side
                    return (2*p+side)*V+i%V
                return 2*K*V+s*R+i-2*V
            before=vals[:]; opened=False
            for z in streams['reverse' if rev else 'forward']:
                if z[0]==0: continue
                x,y=mapper(z[1]),mapper(z[2])
                if z[0]==1:
                    if z[3]&1: vals[x]^=vals[y]
                elif z[0]==2:
                    assert not opened; vals[temp]=vals[x]; opened=True
                else:
                    assert opened and vals[temp]==vals[x]; vals[temp]=0; opened=False
            assert not opened
            d=(2*p+(0 if rev else 1))*V; src=(2*p+(1 if rev else 0))*V
            for t in range(V): before[d+t]^=before[src+t]
            assert vals==before
            levels[p]=s; schedule.append(dict(kind='local_cover_sweep',**{k:v for k,v in e.items() if k!='kind'}))
            if s%2==1 and s<=2*K-3:
                j=(s+1)//2; assert levels[j]==-1; levels[j]=s
                schedule.append(dict(kind='idle',pair=j,rank=7*(s+1),source_level=-1,target_level=s))
            elif s%2==0 and 2<=s<=2*K-2:
                j=s//2; assert levels[j]==s-1; levels[j]=s
                schedule.append(dict(kind='idle',pair=j,rank=7,source_level=s-1,target_level=s))
            elif s==2*K:
                for j in range(K):
                    oldlevel=levels[j]; assert oldlevel==2*j+2
                    schedule.append(dict(kind='idle',pair=j,rank=7*(2*K-oldlevel),source_level=oldlevel,target_level=2*K))
                    levels[j]=2*K
            stages.append(dict(stage=s,all_columns=n,helper_columns=L*R,reverse=rev))
        elif e['kind']=='bridge':
            d,s=e['dst'],e['src']; assert levels[d]==levels[s]
            for t in range(V): vals[2*d*V+t]^=vals[2*s*V+t]; vals[(2*s+1)*V+t]^=vals[(2*d+1)*V+t]
            schedule.append(e)
        else:
            assert levels==[2*K]*K
            for j in range(K):
                for t in range(V):
                    x=2*j*V+t; y=(2*j+1)*V+t; vals[x],vals[y]=vals[y],vals[x]
            schedule.append(e)
    assert vals==[1<<i for i in range(n)]+[0]
    # Integer scalar eight-bank matrix, with each individual bridge shear omitted.
    def small(skip=-1):
        z=[[int(i==j) for j in range(2*K)] for i in range(2*K)]; count=0
        def add(d,s,c): z[d]=[x+c*y for x,y in zip(z[d],z[s])]
        for e in events:
            if e['kind']=='local':
                p=e['pair']; add(2*p,2*p+1,-1) if e['reverse'] else add(2*p+1,2*p,1)
            elif e['kind']=='bridge':
                d,s,c=e['dst'],e['src'],e['coefficient']
                for x,y,sgn in [(2*d,2*s,c),(2*s+1,2*d+1,-c)]:
                    if count!=skip: add(x,y,sgn)
                    count+=1
            else:
                for j in range(K): z[2*j],z[2*j+1]=z[2*j+1],[-x for x in z[2*j]]
        return z,count
    ident=[[int(i==j) for j in range(2*K)] for i in range(2*K)]
    z,nb=small(); assert z==ident and nb==6*(K-1)
    for skip in range(nb): assert small(skip)[0]!=ident; bridge_controls.append(skip)

    paid=Counter(); calls=[]; assignment=set(); expanded=hashlib.sha256(); full_event_count=0
    for e in events:
        if e['kind']!='local': continue
        s,p,rev=e['stage'],e['pair'],e['reverse']; ori='reverse' if rev else 'forward'
        for rep in range(T):
            owners=[]
            for i in range(2*V):
                side=i//V; side=1-side if rev else side
                owners.append([rep*(2*K*V)+(2*p+side)*V+i%V, ['data',s,i%V]])
            for r in range(R):
                if NOBANK: break
                bank,offset,width=place[rep,r]
                owners.append([DATA+s*NB+bank,['bank',offset,width,initial[2*V+r]]])
                assignment.add((s,rep,r,bank,offset))
            assert len({(f,tuple(route)) for f,route in owners})==(2*V if NOBANK else LOCAL)
            assert all(0<=f<LIVE for f,route in owners)
            # Stream one full renamed instruction program into a source-bound
            # digest, including exact owner route descriptors and reflection.
            for z in streams[ori]:
                op=z[0]
                if op==0: paid[z[4]]+=bool(z[4])
                elif op==2: paid[z[5]]+=1
                full_event_count+=1
                if NOBANK: continue      # helper owners are assigned (hosted or bank) at hosting emission
                if op==0: mapped=[op,owners[z[1]],*z[2:]]
                else:
                    ox=owners[z[1]]; oy=owners[z[2]] if z[2]<LOCAL else [LIVE,['private',0]]
                    mapped=[op,ox,oy,*z[3:]]
                expanded.update((json.dumps(mapped,separators=(',',':'))+'\n').encode())
            calls.append(dict(stage=s,replica=rep,pair=p,orientation=ori,owners=owners,local_hash=checks[ori]['sha256']))
    paid.pop(0,None)
    assert (NOBANK or len(assignment)==L*T*R) and len(calls)==L*T
    for e in schedule:
        if e['kind']=='idle' and e['rank']: paid[e['rank']]+=2*V*T
    mass=sum(r*c for r,c in paid.items()); assert NOBANK or M*LIVE-mass==DEFICIT
    want=Counter({r:L*T*c for r,c in localH.items()})
    for j in range(1,K): want[14*j]+=2*T*V; want[7]+=2*T*V
    for j in range(K-1): want[14*(K-1-j)]+=2*T*V
    assert dict(sorted(paid.items()))==dict(sorted(want.items()))
    cf=checks['forward']['cancellation_free_row_l1']; cb=checks['reverse']['cancellation_free_row_l1']
    prefix=(1<<nb)*cf**(K+1)*cb**K; CHARGED=192 if prefix.bit_length()<=192 else 64*((prefix.bit_length()+63)//64)
    HD=1
    while not 2*max(paid)**HD<M**HD: HD+=1
    template=dict(version='compressed-%s-e8-bit-v1'%NAMES[L].lower(),m=M,h=H,stages=L,replicas=T,live=LIVE,private_centre_reserve=9,
                  cover='O(I_%d/2,F_q) for admitted odd address primes q'%M,loop_order='Each recipe phase: replicas then all cover classes; finish every local invocation before the next.',
                  schedule=schedule,local_programs=streams,calls=calls,bank_padding=None,
                  helper_route='Exact residual isometry from the listed root basis, extended by identity on exterior coordinates and permuted to the assigned bank interval.',
                  residual_isometries=isometries,banks_per_stage=NB,entrance_rank_total=ENT,
                  data_route='owner (replica*%d + (2*pair+side)*120+port, d*rho_stage,port)'%(2*K*V),
                  bit_operator='D_U exchanges the two address halves on projector U; D_I D_P = D_(I-P) exactly.',
                  geometry_sha256=sha(out/'GEOMETRY.json'),source_record_sha256=sha(rp))
    blob=json.dumps(template,separators=(',',':'),sort_keys=True).encode(); (out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
    result=dict(status='PASS_SOURCE_BOUND_%s_STAGE_BIT_TEMPLATE'%NAMES[L],h=H,m=M,v=V,R=R,replicas=T,live=LIVE,physical=LIVE+9,
                word_sha256=sha(wp),source_records_sha256=sha(rp),local_checks=checks,scalar_stages=stages,
                independent_unbanked_scalar_columns=n,all_scalar_columns_restored=True,
                geometry_sha256=sha(out/'GEOMETRY.json'),template_sha256=hashlib.sha256(blob).hexdigest(),
                emitted_program_sha256=None if NOBANK else expanded.hexdigest(),emitted_events=full_event_count,local_invocations=len(calls),
                bank_assignments=len(assignment),banks_per_stage=NB,entrance_rank_total=ENT,residual_bank_slots=True,padding_calls=0,
                profile=dict(sorted(paid.items())),paid_calls=sum(paid.values()),rank_mass=mass,deficit=None if NOBANK else DEFICIT,
                maxchild=max(paid),halving_depth=HD,halving_integer_inequality=[M**HD,2*max(paid)**HD],
                local_additions=ADDS,bridge_additions=6*(K-1)*V*T,copy_erase_episodes=9*L*T,
                global_prefix_bound=str(prefix),global_prefix_bits=prefix.bit_length(),charged_prefix_bits=CHARGED,
                omitted_bridge_shears_rejected=bridge_controls,
                scope='Complete source-bound finite cover template. Local and unbanked global F2 columns are replayed; arbitrary physical bank dirt follows by injective owner routes and the all-column local theorem. Astronomical cover enumeration and all-size compiler interfaces remain explicit inherited assumptions.',
                seconds=time.monotonic()-start)
    write(out/'GLOBAL.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('local_checks','scalar_stages','global_prefix_bound')}),flush=True)

if __name__=='__main__': main()
