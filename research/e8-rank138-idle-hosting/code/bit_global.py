# Adapted for the PR426/source-centre composition by icekylinx with Codex assistance.
"""Source-bound compressed nine-stage bit template and exact scalar audits.

Prepared by Zhihao Chen with OpenAI Codex assistance, Apache-2.0.
The local E8 bit word is Dylan Crow's pinned PR #370 contribution.
"""
import argparse, gzip, hashlib, json, struct, time
from collections import Counter
from pathlib import Path
from residual_routes import generate

import sys as _sys
H,V,L,K,T,M=8,120,9,4,32,64
R=json.loads((Path(_sys.argv[_sys.argv.index('--source')+1])/'bit-source-centres.json').read_bytes())['R']
LOCAL=2*V+R; DATA=2*K*V*T

def tile_banks(width):
    """exact width-64 bank tiling of the per-stage helper slots (8 replicas x R helpers, slot width = 8 - entrance rank);
    returns {(replica, helper): (bank, offset)} and the bank count; every bank is filled exactly (no padding)."""
    slots=sorted(((width[h],rep,h) for rep in range(T) for h in range(R)),key=lambda x:(-x[0],x[1],x[2]))
    bins=[]; place={}
    by={}
    for w_,rep,h in slots: by.setdefault(w_,[]).append((rep,h))
    def take(w_):
        return by[w_].pop(0) if by.get(w_) else None
    # Exact mixed widths: eight width-7 slots plus one width-8; divisor-width remainders filled with width-8 slots.
    for w_ in sorted(by,reverse=True):
        if w_==8: continue
        while by.get(w_):
            b=len(bins); off=0; cont=[]
            if w_==7:
                for _ in range(8): rep,h=take(7); cont.append((rep,h,off,7)); off+=7
                rep,h=take(8); cont.append((rep,h,off,8)); off+=8
            else:
                assert 64%w_==0
                for _ in range(min(64//w_,len(by[w_]))): rep,h=take(w_); cont.append((rep,h,off,w_)); off+=w_
                assert (64-off)%8==0
                while off<64: rep,h=take(8); cont.append((rep,h,off,8)); off+=8
            assert off==64; bins.append(cont)
    while by.get(8):
        cont=[]; off=0
        for _ in range(8): rep,h=take(8); cont.append((rep,h,off,8)); off+=8
        bins.append(cont)
    for b,cont in enumerate(bins):
        for rep,h,off,w_ in cont: place[rep,h]=(b,off,w_)
    assert len(place)==T*R
    return place,len(bins)

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
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--local-check',type=Path,required=True); ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); start=time.monotonic(); out=a.out; out.mkdir(parents=True,exist_ok=True)
    wp=a.source/'bit-source-centres.json'; w=json.loads(wp.read_bytes())
    inherited=Path('inherited/bit-geometry.json.gz')
    geo=json.loads(gzip.decompress(inherited.read_bytes()))
    base=Path('work/pr370-source/research/e8-bit/data/bit/bitE8-r865.json.gz')
    original=json.loads(gzip.decompress(base.read_bytes()))
    assert geo['word_sha256']==sha(base)
    assert w['lines']==original['lines'] and w['form']==original['form']
    # PR436 regenerates the same root-closed frame family in a different order.
    # Bind every actual frame by its exact root set; all record IDs remain actual IDs.
    original_ids={tuple(sorted(fr)):i for i,fr in enumerate(original['frames'])}
    actual_keys=[tuple(sorted(fr)) for fr in w['frames']]
    assert len(original_ids)==len(original['frames'])==len(actual_keys)==len(set(actual_keys))
    assert set(actual_keys)==set(original_ids)
    frame_map=[original_ids[k] for k in actual_keys]
    assert sorted(frame_map)==list(range(len(original['frames'])))
    geo['actual_frame_to_pinned_frame']=frame_map
    geo['frame_binding']='Exact bijection of root sets; frame IDs in emitted records are those of the reconstructed PR436 word.'
    kr=json.loads((a.source/'bit-kernel-receipt.json').read_text()); assert kr['output_sha256'] and len(w['frames'])==len(original['frames'])+kr['new_frames']
    geo['inherited_geometry_sha256']=sha(inherited);geo['word_sha256']=sha(wp)
    geo['reuse_scope']='Unchanged ports and compressed windows; nonzero helper entrances use mixed-width residual slots, with every owner and coordinate checked independently.'
    write(out/'GEOMETRY.json',geo)
    rp=a.local_check/'records/249-records.bin';raw=rp.read_bytes();rec=list(struct.iter_unpack('<6i',raw))
    state=json.loads((a.local_check/'records/249-states.json').read_text())
    fs=json.loads((a.local_check/'records/frames.json').read_text())['frames']
    dims={int(f):z['dim'] for f,z in fs.items()}
    assert (state['v'],state['n'])==(V,LOCAL)
    expected_adds=sum(e[0]==1 for e in rec)
    initial=[state['initial'][str(i)] for i in range(LOCAL)]
    final=[state['final'][str(i)] for i in range(LOCAL)]
    assert all(dims[final[i]]==H for i in range(2*V,LOCAL))
    width={i-2*V:H-dims[initial[i]] for i in range(2*V,LOCAL)}; ENT=sum(H-x for x in width.values()); assert T*(8*R-ENT)%64==0
    place,NB=tile_banks(width); assert NB==T*(8*R-ENT)//64
    isometries=generate(w,dims)
    LIVE=DATA+L*NB
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
        assert center is None and copies==9 and adds==expected_adds
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

    events=recipe(); levels=[-1]*K; schedule=[]; bridge_controls=[]
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
            if s in (1,3,5):
                j=(s+1)//2; assert levels[j]==-1; levels[j]=s
                schedule.append(dict(kind='idle',pair=j,rank=7*(s+1),source_level=-1,target_level=s))
            elif s in (2,4,6):
                j=s//2; assert levels[j]==s-1; levels[j]=s
                schedule.append(dict(kind='idle',pair=j,rank=7,source_level=s-1,target_level=s))
            elif s==8:
                for j in range(4):
                    oldlevel=levels[j]; assert oldlevel==2*j+2
                    schedule.append(dict(kind='idle',pair=j,rank=7*(8-oldlevel),source_level=oldlevel,target_level=8))
                    levels[j]=8
            stages.append(dict(stage=s,all_columns=n,helper_columns=L*R,reverse=rev))
        elif e['kind']=='bridge':
            d,s=e['dst'],e['src']; assert levels[d]==levels[s]
            for t in range(V): vals[2*d*V+t]^=vals[2*s*V+t]; vals[(2*s+1)*V+t]^=vals[(2*d+1)*V+t]
            schedule.append(e)
        else:
            assert levels==[8]*4
            for j in range(K):
                for t in range(V):
                    x=2*j*V+t; y=(2*j+1)*V+t; vals[x],vals[y]=vals[y],vals[x]
            schedule.append(e)
    assert vals==[1<<i for i in range(n)]+[0]
    # Integer scalar eight-bank matrix, with each individual bridge shear omitted.
    def small(skip=-1):
        z=[[int(i==j) for j in range(8)] for i in range(8)]; count=0
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
                for j in range(4): z[2*j],z[2*j+1]=z[2*j+1],[-x for x in z[2*j]]
        return z,count
    ident=[[int(i==j) for j in range(8)] for i in range(8)]
    z,nb=small(); assert z==ident and nb==18
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
                bank,off,w_=place[rep,r]
                owners.append([DATA+s*NB+bank,['bank',off,w_,initial[2*V+r]]])
                assignment.add((s,rep,r,bank,off))
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
        if e['kind']=='idle' and e['rank']: paid[e['rank']]+=2*V*T
    mass=sum(r*c for r,c in paid.items()); assert M*LIVE-mass==312*T
    cf=checks['forward']['cancellation_free_row_l1']; cb=checks['reverse']['cancellation_free_row_l1']
    prefix=(1<<nb)*cf**5*cb**4; charged_prefix=64*((prefix.bit_length()+63)//64);assert prefix<1<<charged_prefix
    print('Fresh prefix bits',prefix.bit_length(),'charged',charged_prefix,flush=True)
    template=dict(version='compressed-nine-e8-bit-v1',m=M,h=H,stages=L,replicas=T,live=LIVE,private_centre_reserve=9,
                  cover='O(I_64/2,F_q) for admitted odd address primes q',loop_order='Each recipe phase: replicas then all cover classes; finish every local invocation before the next.',
                  schedule=schedule,local_programs=streams,calls=calls,bank_padding=None,
                  helper_route='Exact listed residual coordinate isometry, extended by identity on exterior coordinates and permuted to the assigned bank interval.',banks_per_stage=NB,entrance_rank_total=ENT,residual_isometries=isometries,
                  data_route='owner (replica*960 + (2*pair+side)*120+port, d*rho_stage,port)',
                  bit_operator='D_U exchanges the two address halves on projector U; D_I D_P = D_(I-P) exactly.',
                  geometry_sha256=sha(out/'GEOMETRY.json'),source_record_sha256=sha(rp))
    blob=json.dumps(template,separators=(',',':'),sort_keys=True).encode(); (out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
    result=dict(status='PASS_SOURCE_BOUND_NINE_STAGE_BIT_TEMPLATE',h=H,m=M,v=V,R=R,replicas=T,live=LIVE,physical=LIVE+9,
                word_sha256=sha(wp),source_records_sha256=sha(rp),local_checks=checks,scalar_stages=stages,
                independent_unbanked_scalar_columns=n,all_scalar_columns_restored=True,
                geometry_sha256=sha(out/'GEOMETRY.json'),template_sha256=hashlib.sha256(blob).hexdigest(),
                emitted_program_sha256=expanded.hexdigest(),emitted_events=full_event_count,local_invocations=len(calls),
                bank_assignments=len(assignment),banks_per_stage=NB,entrance_rank_total=ENT,mixed_width_slots=True,padding_calls=0,residual_isometries=len(isometries),extra_helper_route_factor_bound=144,
                profile=dict(sorted(paid.items())),paid_calls=sum(paid.values()),rank_mass=mass,deficit=312*T,
                maxchild=max(paid),halving_depth=2,halving_integer_inequality=[64**2,2*42**2],
                local_additions=expected_adds,bridge_additions=18*V*T,copy_erase_episodes=9*L*T,
                global_prefix_bound=str(prefix),global_prefix_bits=prefix.bit_length(),charged_prefix_bits=charged_prefix,
                omitted_bridge_shears_rejected=bridge_controls,
                scope='Complete source-bound finite cover template. Local and unbanked global F2 columns are replayed; arbitrary physical bank dirt follows by injective owner routes and the all-column local theorem. Astronomical cover enumeration and all-size compiler interfaces remain explicit inherited assumptions.',
                seconds=time.monotonic()-start)
    write(out/'GLOBAL.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('local_checks','scalar_stages','global_prefix_bound')}),flush=True)

if __name__=='__main__': main()
