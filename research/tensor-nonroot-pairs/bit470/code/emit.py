# Eight-replica whole-family pooling by Rohan Arun with OpenAI Codex. Upstream notices retained.
# Kernel integration of PR436/PR386 by chafreaky, with OpenAI Codex assistance.
# Original copyright and attribution retained below. This variant uses explicit
# residual isometries and mixed-width banks; the original all-zero-start
# requirement is replaced by the verified kernel entrance contract.
"""Source-bound eleven-stage bit template with 8 independent replicas and no helper banks.
PR386 global identity and PR436 generalization by Zhihao Chen and eumemic,
with their disclosed OpenAI Codex and Anthropic Claude assistance, Apache-2.0.
PR439 explicit residual routes and this replication extension by chafreaky,
with OpenAI Codex assistance. All owner assignments and emitted calls are checked.
Historical PR386 regression is performed by the unchanged parent wrapper.
"""
import argparse, gzip, hashlib, json, struct, time, sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/"vendor/runtime"))

from bank_routes import validate_isometries
import hosting_core as HC

H,L,K,M=8,11,5,78
T=json.loads((HERE.parent/'CONFIG.json').read_text())['replicas']
assert isinstance(T,int) and T>0
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,indent=2)+'\n')

def recipe():
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
    a=ap.parse_args(); start=time.monotonic(); out=a.out; out.mkdir(parents=True,exist_ok=True)
    wp=a.word; w=json.loads(gzip.decompress(wp.read_bytes()))
    V,R=w['v'],w['R']; LOCAL=2*V+R; DATA=2*K*V*T; LIVE=DATA+L*R
    assert (w['h'],V,w['form'])==(8,120,'<x,y>/2')
    geo=json.loads((out/'GEOMETRY.json').read_text())
    assert geo['status']=='PASS_COMPRESSED_ELEVEN_BIT_GEOMETRY'
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
    NB=0;LIVE=DATA
    assert M==8+7*(L-1)
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

    events=recipe(); levels=[-1]*K; schedule=[]; bridge_controls=[]
    # Full scalar replay on separate dirty helpers for all eleven stages.
    # Physical hosting then uses the separately checked injective cover owners.
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
            if s in range(1,2*K-1,2):
                j=(s+1)//2; assert levels[j]==-1; levels[j]=s
                schedule.append(dict(kind='idle',pair=j,rank=7*(s+1),source_level=-1,target_level=s))
            elif s in range(2,2*K,2):
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
    # Integer scalar ten-wire matrix, with each individual bridge shear omitted.
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

    # Freeze and expand the full-helper idle assignment for one replica.
    indexed=[];idx=0
    for e in schedule:
        if e['kind']=='local_cover_sweep': indexed.append(dict(kind='local',stage=e['stage'],pair=e['pair']))
        elif e['kind']=='bridge': indexed.append(dict(kind='bridge',dst=e['dst'],src=e['src']))
        elif e['kind']=='idle':
            e['idx']=idx;indexed.append(dict(kind='idle',idx=idx,pair=e['pair'],rank=e['rank']));idx+=1
    win={i:w for i,w in HC.windows(indexed).items() if w[1] and w[2]}
    ys,zs,proxy=HC.load_selection(HERE.parent/'data/selection.json','bit')
    slots,rem=HC.expand(win,ys,zs,{s:[(i,widths[i%R]) for i in range(R*T)] for s in range(L)},2*V*T)
    hosted={(s,h):(i,cp,off,width) for i,cp,off,width,s,h in slots}
    assert len(slots)==len(hosted)==L*R*T and set(hosted)=={(s,h) for s in range(L) for h in range(R*T)}
    remainder={str(i):{str(r):n for r,n in sorted(Counter(rem[i,cp] for cp in range(2*V*T)).items())} for i in win}
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
                i,cp,off,width=hosted[s,rep*R+r];pair=win[i][0];owner_rep,within=divmod(cp,2*V);side,port=divmod(within,V)
                family=owner_rep*(2*K*V)+(2*pair+side)*V+port
                owners.append([family,['hosted',i,off,width]])
                assignment.add((s,rep,r,family,off))
            assert len({(f,tuple(route)) for f,route in owners})==LOCAL
            assert all(0<=f<LIVE for f,route in owners)
            # Stream one full renamed instruction program into a source-bound
            # digest, including exact owner route descriptors and reflection.
            for z in streams[ori]:
                op=z[0]
                if op==0: paid[z[4]]+=bool(z[4]); mapped=[op,owners[z[1]],*z[2:]]
                else:
                    ox=owners[z[1]]; oy=owners[z[2]] if z[2]<LOCAL else [LIVE,['private',0]]
                    mapped=[op,ox,oy,*z[3:]]
                    if op==2: paid[z[5]]+=1
                expanded.update((json.dumps(mapped,separators=(',',':'))+'\n').encode()); full_event_count+=1
            calls.append(dict(stage=s,replica=rep,pair=p,orientation=ori,owners=owners,local_hash=checks[ori]['sha256']))
    paid.pop(0,None)
    assert len(assignment)==L*T*R and len(calls)==L*T
    for e in schedule:
        if e['kind']=='idle' and e['rank']:
            i=e['idx']
            for cp in range(2*V*T):
                r=rem[i,cp] if i in win else e['rank']
                if r:paid[r]+=1
    mass=sum(r*c for r,c in paid.items());assert M*LIVE-mass==(2*K*V-L*72)*T
    cf=checks['forward']['cancellation_free_row_l1']; cb=checks['reverse']['cancellation_free_row_l1']
    # Independently bound actual physical-family norms in chronological order.
    # Every address route and bit residual is a value permutation. Ignore all
    # cancellation; shared physical owners update the same bound variable.
    physical_norm=[1]*LIVE+[0];prefix=1;callmap={(x['stage'],x['replica']):x for x in calls}
    for e in events:
        if e['kind']=='local':
            for rep in range(T):
                call=callmap[e['stage'],rep];own=call['owners']
                for z in streams[call['orientation']]:
                    op=z[0]
                    if op==0:continue
                    x=own[z[1]][0];y=own[z[2]][0] if z[2]<LOCAL else LIVE
                    if op==1:physical_norm[x]+=abs(z[3])*physical_norm[y]
                    elif op==2:physical_norm[LIVE]=physical_norm[x]
                    else:assert op==3;physical_norm[LIVE]=0
                    prefix=max(prefix,physical_norm[x],physical_norm[LIVE])
        elif e['kind']=='bridge':
            d,ss=e['dst'],e['src']
            for rep in range(T):
                for port in range(V):
                    for x,y in [(rep*1200+2*d*V+port,rep*1200+2*ss*V+port),(rep*1200+(2*ss+1)*V+port,rep*1200+(2*d+1)*V+port)]:
                        physical_norm[x]+=physical_norm[y];prefix=max(prefix,physical_norm[x])
    assert physical_norm[LIVE]==0
    charged_prefix=64*((prefix.bit_length()+63)//64)
    template=dict(version='compressed-eleven-whole-pool4-bit-v1',m=M,h=H,stages=L,replicas=T,live=LIVE,private_centre_reserve=9,
                  cover='O(I_78/2,F_q) for admitted odd address primes q',loop_order='Each recipe phase: replicas then all cover classes; finish every local invocation before the next.',
                  schedule=schedule,local_programs=streams,calls=calls,bank_padding=None,
                  helper_route='Whole-family owner may belong to another replica; exact residual isometry from the listed root basis, extended by identity and mapped onto the assigned pending idle coordinates using PR442 hosting.',
                  residual_isometries=isometries,banks_per_stage=NB,entrance_rank_total=ENT,
                  hosting=dict(windows={str(i):[w[0],w[1],sorted(w[2])] for i,w in win.items()},slots=[list(x) for x in slots],remainders=remainder),
                  data_route='owner (replica*1200 + (2*pair+side)*120+port, d*rho_stage,port)',
                  bit_operator='D_U exchanges the two address halves on projector U; D_I D_P = D_(I-P) exactly.',
                  geometry_sha256=sha(out/'GEOMETRY.json'),source_record_sha256=sha(rp))
    blob=json.dumps(template,separators=(',',':'),sort_keys=True).encode(); (out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
    result=dict(status='PASS_SOURCE_BOUND_ELEVEN_STAGE_HOSTED_BIT_TEMPLATE',h=H,m=M,v=V,R=R,replicas=T,live=LIVE,physical=LIVE+9,
                word_sha256=sha(wp),source_records_sha256=sha(rp),local_checks=checks,scalar_stages=stages,
                independent_unbanked_scalar_columns=n,all_scalar_columns_restored=True,
                geometry_sha256=sha(out/'GEOMETRY.json'),template_sha256=hashlib.sha256(blob).hexdigest(),
                emitted_program_sha256=expanded.hexdigest(),emitted_events=full_event_count,local_invocations=len(calls),
                bank_assignments=0,hosted_residuals=len(assignment),banks_per_stage=NB,entrance_rank_total=ENT,residual_bank_slots=False,padding_calls=0,
                profile=dict(sorted(paid.items())),paid_calls=sum(paid.values()),rank_mass=mass,deficit=(2*K*V-L*72)*T,
                maxchild=max(paid),halving_depth=3,halving_integer_inequality=[M**3,2*max(paid)**3],
                local_additions=ADDS,bridge_additions=6*(K-1)*V*T,copy_erase_episodes=9*L*T,
                global_prefix_bound=str(prefix),global_prefix_bits=prefix.bit_length(),charged_prefix_bits=charged_prefix,
                omitted_bridge_shears_rejected=bridge_controls,
                scope='Complete source-bound finite cover template. Local and unbanked global F2 columns are replayed; idle-data hosting follows conditionally from PR442 plus injective owner routes and the all-column local theorem. Astronomical cover enumeration and all-size compiler interfaces remain explicit inherited assumptions.',
                seconds=time.monotonic()-start)
    write(out/'GLOBAL.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('local_checks','scalar_stages','global_prefix_bound')}),flush=True)

if __name__=='__main__': main()
