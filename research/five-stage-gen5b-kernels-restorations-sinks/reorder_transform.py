"""Reordering stage after the terminal sinks: an ADD a += c*b leaves its frame and joins a neighbouring incidence.

Mechanism (toggle-detection view of Khattar-Gidney, arXiv:2407.17966, specialised to this word). On the post-sink word a
delivery y += h of a root helper h at the root frame R (rank 21) is immediately followed, for the same target y, by a
climb to a rank-22 frame F for the next side_root read, while h itself stays at R for its three sibling deliveries
and then climbs R -> FULL for its cleanups. The delivery commutes with every gate between it and y's next incidence
(none of them reads y, none writes h), so it is executed just before that incidence, inside F: y now climbs R' -> F in
one step instead of R' -> R -> F, and h climbs R -> F -> FULL instead of R -> FULL (local delta {21:-1, 22:+1, 3:-1,
2:+1} per move, rank mass unchanged). The same screen also moves 22 forward gates to an earlier incidence frame.
Selection rule (discovery/build_reorder_selection.py): every ADD whose frame is a strict breakpoint of an operand's
path is tried at the frame of each of the six previous/next incidences of either operand; the move is admitted when
no gate on the crossed interval reads a or writes b (and no COPY/ERASE touches a), the rebuilt frame chains of a and b
are nested and the phi ledger decreases; greedy by gain over disjoint operand sets.
Checks here: the frozen moves are re-derived on the actual input word (record content, anchor frame, crossed-interval
contract, disjoint operand sets); F2 replay of every formal column forward and inverse; omitting the moved ADDs fails;
every MOVE rebuilt from operand frames with both reflected ledgers; an independent integer replay modulo 2^61-1 with
pseudo-random dirty inputs gives identical final values for every register; local delta equals the frozen one.
Prepared with Anthropic Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time,sys,importlib.util,bisect
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def integer_replay(records,n,seed=20260710):
    """Exact replay modulo the Mersenne prime 2^61-1 with fixed pseudo-random dirty inputs (all registers and the temporary)."""
    import random
    P=(1<<61)-1;rng=random.Random(seed);val=[rng.randrange(P)for _ in range(n+1)]
    for k in range(0,len(records),6):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:val[a]=(val[a]+c*val[b])%P
        elif op==2:val[n]=val[a]
    return val[:n]

def span_violations(records,W,C,n,v):
    """Exact integer source span of every non-target operand after each gate (PR #287/#291 rule), checked against the
    gate frame for EVERY gate of the word: returns the violating (record, source) pairs."""
    columns=[{i:1} if i<v else {} for i in range(n)];center=None;bad=[]
    for k in range(0,len(records),6):
        op,a,b,c,f,z=records[k:k+6]
        if op==0:continue
        if op==2:assert center is None;center=a;continue
        if op==3:assert center==a;center=None;continue
        source=center if b==n else b;ca=columns[a]
        for s,x in columns[source].items():
            y=ca.get(s,0)+c*x
            if y:ca[s]=y
            else:del ca[s]
        need=set()
        if not(v<=a<2*v):need.update(ca)
        if not(v<=b<2*v) and b!=n:need.update(columns[b])
        for s in need:
            if any(W.module.dot(x,C.chi[s])for x in C.A[f]):bad.append((k//6,s));break
    return bad

def transform(producer,selection,tag='reorder'):
    W,C=producer['W'],producer['C'];old=producer['records'];initial=dict(producer['initial_state']);final=dict(producer['final_state'])
    v=W.v;n=2*v+len(producer['context']['regs'])
    assert n==selection['n'] and v==selection['v'] and sha(old.tobytes())==selection['input_raw_sha256'],'reorder selection bound to a different word'
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    cats=list(producer['physical']['category_names']);assert tag+'_moved' not in cats
    MOVED=len(cats);cats+=[tag+'_moved']
    moves={};ops=set()
    for e in selection['moves']:
        i,T,side=e['record'],e['anchor'],e['side'];op,a,b,c,f,z=old[6*i:6*i+6]
        assert op==1 and [a,b,c]==e['incidence'] and b!=n and cats[z]==e['category'],'moved record content differs'
        assert not({a,b}&ops),'operand sets of the moves must be disjoint';ops|={a,b}
        aop,aa,ab,ac,af,az=old[6*T:6*T+6];assert aop==1 and ({aa,ab}&{a,b}),'anchor must be an ADD incidence of a or b'
        F=af;assert C.dimf[F]==e['frame_rank'] and [list(x)for x in C.B[F]]==e['frame_basis'],'anchor frame differs from the frozen basis'
        assert (side=='before' and T>i) or (side=='after' and T<i)
        lo,hi=(i,T) if side=='before' else (T+1,i)
        for k in range(lo,hi):
            if k==i:continue
            xo,x,y,_,_,_=old[6*k:6*k+6]
            if xo==1:assert y!=a and x!=b,('crossed gate reads a or writes b',i,k)
            elif xo in(2,3):assert x!=a,('crossed copy of a',i,k)
        moves[i]=(a,b,c,F,T,side)
    before={};after={}
    for i,m in moves.items():(before if m[5]=='before' else after).setdefault(m[4],[]).append(i)
    state=dict(initial);out=array('i');temporary=None
    def move(s,f):
        b0=state[s]
        if b0==f:return
        assert C.sub(b0,f),('reorder nonnested use',s,b0,f)
        gap=C.dimf[f]-C.dimf[b0];assert gap>=0;out.extend((0,s,b0,f,gap,0));state[s]=f
    def add(a,b,c,f,z):
        move(a,f)
        if b!=n:move(b,f)
        out.extend((1,a,b,c,f,z))
    def emit_moved(lst):
        for i in sorted(lst):a,b,c,F,T,side=moves[i];add(a,b,c,F,MOVED)
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        emit_moved(before.get(i,()))
        if op==1:
            if i not in moves:add(a,b,c,f,z)
        elif op==2:assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c);out.extend((op,a,b,c,f,z))
        elif op==3:assert temporary==(a,b,c)and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];temporary=None
        emit_moved(after.get(i,()))
    assert temporary is None
    for s in sorted(final):move(s,final[s])
    assert state==final
    project=lambda aa:sorted(tuple(aa[k+j]for j in(0,1,2,3))for k in range(0,len(aa),6)if aa[k]==1)
    assert project(out)==project(old),'only the documented reordering (same multiset of scalar ADDs)'
    proof=dict(selected=len(moves),operand_sets_disjoint=True,crossed_interval_contract=True,categories=dict(Counter(e['category']for e in selection['moves'])),
        shapes=dict(Counter('%s:%d->%d'%(e['category'],e['old_frame_rank'],e['frame_rank'])for e in selection['moves'])))
    return out,initial,final,cats,proof,n,v

def run(producer,output_dir=None,selection_path=None,tag='reorder'):
    start=time.monotonic()
    spec=importlib.util.spec_from_file_location('reorder_kernel_replay',HERE/'kernel_transform.py');km=importlib.util.module_from_spec(spec);spec.loader.exec_module(km)
    W,C=producer['W'],producer['C'];path=Path(selection_path)if selection_path else HERE/(tag+'-selection.json');selection=json.loads(path.read_text())
    out,initial,final,cats,proof,n,v=transform(producer,selection,tag);ZERO=producer['ZERO']
    forward=km.replay(out,n,v);inverse=km.replay(out,n,v,True);controls=[km.replay(out,n,v,omit_category=cats.index(tag+'_moved'))]
    assert not span_violations(out,W,C,n,v),'a gate frame omits an operand source span'
    old=producer['records'];iold=integer_replay(old,n);inew=integer_replay(out,n);assert iold==inew,'integer replay differs'
    needs={s:[]for s in initial};copies=Counter();temporary=None
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==1:
            needs[a].append(f)
            if b!=n:needs[b].append(f)
            else:assert temporary is not None and f==ZERO
        elif op==2:assert temporary is None;temporary=(a,b,c);needs[a].append(c);copies[z]+=1
        elif op==3:assert temporary==(a,b,c);temporary=None
    assert temporary is None and copies=={22:24}
    per_role={};pairs=set();census=Counter(copies);reflected=Counter(copies)
    for s,startframe in initial.items():
        H=Counter();pathframes=[startframe]+needs[s]+[final[s]]
        for a,b in zip(pathframes,pathframes[1:]):
            assert C.sub(a,b);gap=C.dimf[b]-C.dimf[a];assert gap>=0;pairs.add((a,b))
            if gap:H[gap]+=1
        for a,b in zip(reversed(pathframes),list(reversed(pathframes))[1:]):
            assert all(not W.module.dot(x,y)for x in C.A[a]for y in C.B[b]);gap=len(C.A[b])-len(C.A[a]);assert gap>=0
            if gap:reflected[gap]+=1
        per_role[s]=H;census.update(H)
    assert reflected==census
    for f in {x for pair in pairs for x in pair}:assert C.nondeg(f)and len(C.B[f])+len(C.A[f])==24
    state=dict(initial);hist=Counter();cat=Counter();coeff=Counter();usedf=set(state.values());temporary=None;centers=[];count=0;tagged=hashlib.sha256()
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==0:
            assert state[a]==b and C.sub(b,c)and C.dimf[c]-C.dimf[b]==f and len(C.A[b])-len(C.A[c])==f
            state[a]=c;usedf.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert state[a]==state[b]==f and a!=b and c%2;count+=1;cat[cats[z]]+=1;coeff[abs(c)]+=1;usedf.add(f)
            tagged.update(json.dumps([a,b,c,f,cats[z]],separators=(',',':')).encode());tagged.update(b'\n')
        elif op==2:
            assert temporary is None and b==n and state[a]==c and f==ZERO and z==22
            state[b]=f;hist[z]+=1;temporary=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and temporary is not None and (a,b,c)==(temporary['source'],temporary['temporary'],temporary['frame'])and state[a]==c and state[b]==f==ZERO
            temporary.update(after_event=count,scatter_reads=count-temporary['first_event']);assert temporary['scatter_reads']==220;centers.append(temporary);temporary=None;del state[b]
    assert state==final and temporary is None and hist==census and len(centers)==24
    oldH=Counter({int(r):c for r,c in producer['physical']['paid_histogram'].items()});delta=Counter(hist);delta.subtract(oldH);delta={r:c for r,c in delta.items()if c}
    assert delta=={int(k):x for k,x in selection['expected_local_delta'].items()}
    assert sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass'],'reordering keeps the paid rank mass'
    assert count==producer['physical']['weighted_scalar_events']
    inherited=set()
    for inventory in (producer['physical'],producer.get('producer_physical')):
        if isinstance(inventory,dict):inherited.update(row['frame_id']for row in inventory.get('used_frames',[]))
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    receipt=dict(status='PASS_GEN5_REORDER_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS',proof=proof,scalar=dict(forward=forward,inverse=inverse,controls=controls),integer_replay=dict(modulus='2^61-1',registers=n,identical=True),all_gate_frames_contain_operand_source_spans=True,tag=tag,selected=proof['selected'],local_histogram_delta=delta,unchanged_endpoints=True,unchanged_copy_lifetimes=True,both_reflected_ledgers=True,unique_required_frame_pairs=len(pairs),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=sha(old.tobytes()),output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(path.read_bytes()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL_GEN5_REORDER',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(usedf|inherited)],**{tag+'_transform':receipt},physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,**{tag+'_census':receipt})
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/(tag+'-records.bin.gz')).write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/(tag+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS',tag,proof['selected'],'moved ADDs; source spans of every gate checked;',count,'scalar ADDs',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
