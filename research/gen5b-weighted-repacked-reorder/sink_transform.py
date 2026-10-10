"""Terminal sinks on the gen5 word (port of PR #283's sink-transform.cpp / SINK-PROOF.md to this Python pipeline).

Mechanism from PR #283 (Dugongue; terminal sinks are a credited public source527 mechanism). A zero-to-full helper r
qualifies when its only scalar uses are: one initial dirty compensation read y_t += -r at ZERO for every target t of a
set S (before the copied-centre discard), forward writes r += x (forward_gate) after that discard, one terminal delivery
y_t += r at a common root frame for every t in S after the last forward write, and cleanup writes r -= x after the last
delivery; r is never copied. If no target in S is ever a scalar or COPY source, and the pivot p in S is not written by
anything else between the discard and the last forward write, the forward writes are redirected to y_p, y_t -= y_p
(t in S, t != p) is inserted at ZERO right after the discard and y_t += y_p at the root frame right after the last
forward write; the reads, deliveries and cleanups of r are deleted and the register r is removed. Over the integers
every y_t still receives exactly X = sum of the redirected writes (the dirty value of r cancels in the original and is
never read in the new word), and all other registers are unchanged: no gate reads a target in S, nothing else writes p
in the interval, and r was read only by the deleted reads. Selected target sets are disjoint.
Checks: fresh screen equals the frozen selection; the coefficient pattern (-1 reads, +1 deliveries, +1 writes, -1
cleanups) and the commutation conditions above on the actual word; F2 replay of every remaining formal column forward
and inverse; three omission controls (redirected writes, setup, restore) must fail; every MOVE rebuilt from the actual
operand frames with both reflected ledgers; register IDs compacted (removed roles recorded in the context).
Prepared with Anthropic Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time,sys,importlib.util
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def screen(old,initial,final,n,v,cats,ZERO,FULL):
    Z=cats.index;READ,ROOT,FWD,CLN=Z('dirty_read'),Z('side_root'),Z('forward_gate'),Z('cleanup_gate')
    entry=max(k//6 for k in range(0,len(old),6)if old[k]==3)
    inc={};treads=set();twrites={};copied=set()
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:
            inc.setdefault(a,[]).append(i)
            if b!=n:inc.setdefault(b,[]).append(i)
            if v<=b<2*v:treads.add(b)
            if v<=a<2*v:twrites.setdefault(a,[]).append(i)
        elif op in(2,3):inc.setdefault(a,[]).append(i);copied.add(a)
    out=[]
    for r in range(2*v,n):
        if initial[r]!=ZERO or final[r]!=FULL:continue
        pre=Counter();post=Counter();writes=[];cleanups=[];bad=False;rootf=set();coeff=Counter()
        for i in inc.get(r,[]):
            op,a,b,c,f,z=old[6*i:6*i+6]
            if op!=1:bad=True;break
            if b==r:
                if not(v<=a<2*v):bad=True;break
                if z==READ and i<entry and f==ZERO:pre[a]+=1;coeff['read',c]+=1
                elif z==ROOT:post[a]+=1;rootf.add(f);coeff['deliver',c]+=1;last_delivery=i
                else:bad=True;break
            elif a==r:
                if z==FWD:writes.append(i);coeff['write',c]+=1
                elif z==CLN:cleanups.append(i);coeff['cleanup',c]+=1
                else:bad=True;break
        if bad or not writes or not pre:continue
        S=set(pre)
        if set(post)!=S or any(pre[t]!=1 or post[t]!=1 for t in S) or len(rootf)!=1:continue
        first,last=min(writes),max(writes);deliveries=[i for i in inc[r]if old[6*i+2]==r and old[6*i+5]==ROOT]
        if first<=entry or min(deliveries)<last or (cleanups and min(cleanups)<max(deliveries)):continue
        if S&treads or S&copied:continue   # no target in S is ever a scalar or COPY source
        pivots=[p for p in sorted(S)if not[i for i in twrites.get(p,[])if entry<i<=last and old[6*i+2]!=r]]
        if not pivots:continue
        assert coeff==Counter({('read',-1):len(S),('deliver',1):len(S),('write',1):len(writes),('cleanup',-1):len(cleanups)}),('sink coefficient pattern',r,coeff)
        sources={old[6*i+2]for i in writes};assert not(sources&S) and r not in sources and all(s>=2*v for s in sources)
        out.append(dict(stream=r,targets=sorted(S),pivot=pivots[0],first=first,last=last,writes=writes,cleanups=cleanups,root_frame=rootf.pop(),entry=entry))
    return entry,out

def transform(producer,selection):
    W,C=producer['W'],producer['C'];old=producer['records'];initial=dict(producer['initial_state']);context=producer['context'];v=W.v;regs=list(context['regs']);n=2*v+len(regs);ZERO=producer['ZERO'];FULL=producer['FULL']
    final=dict(producer['final_state']);ends=dict(producer.get('helper_endpoints',{}))
    assert n==selection['n'] and v==selection['v'] and sha(old.tobytes())==selection['input_raw_sha256'],'sink selection bound to a different word'
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    cats=list(producer['physical']['category_names']);assert not {'sink_redirect','sink_setup','sink_restore'}&set(cats)
    REDIR,SETUP,RESTORE=len(cats),len(cats)+1,len(cats)+2;cats+=['sink_redirect','sink_setup','sink_restore']
    entry,rows=screen(old,initial,final,n,v,cats,ZERO,FULL)
    frozen=[(e['role'],tuple(e['targets']),e['pivot'])for e in selection['sinks']]
    fresh=[(regs[r['stream']-2*v],tuple(r['targets']),r['pivot'])for r in rows]
    assert sorted(fresh)==sorted(frozen)and len(frozen)==selection['selected'],'fresh sink screen differs from the frozen selection'
    used=set()
    for r in rows:assert not(used&set(r['targets'])),'overlapping target sets';used.update(r['targets'])
    sinks={r['stream']:r for r in rows};assert not(set(sinks)&set(ends))
    # Compaction of register IDs: helpers after a removed one shift down; the copy temporary is n -> n'.
    mp={};k=0
    for s in range(n):
        if s not in sinks:mp[s]=k;k+=1
    nn=k;mp[n]=nn
    redirected={i:r for r in rows for i in r['writes']};dropped=set()
    for r in rows:
        dropped.update(r['cleanups'])
    for k6 in range(0,len(old),6):
        op,a,b,c,f,z=old[k6:k6+6]
        if op==1 and b in sinks:dropped.add(k6//6)
    lastw={r['last']:r for r in rows}
    state={mp[s]:f for s,f in initial.items()if s not in sinks};out=array('i');temporary=None
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('sink nonnested actual use',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0;out.extend((0,s,before,f,gap,0));state[s]=f
    def add(a,b,c,f,z):
        move(a,f)
        if b!=nn:move(b,f)
        out.extend((1,a,b,c,f,z))
    for k6 in range(0,len(old),6):
        op,a,b,c,f,z=old[k6:k6+6];i=k6//6
        if op==1:
            if i in dropped:pass
            elif i in redirected:add(mp[redirected[i]['pivot']],mp[b],c,f,REDIR)
            else:assert a not in sinks;add(mp[a],mp[b],c,f,z)
        elif op==2:assert temporary is None and a not in sinks;move(mp[a],c);state[nn]=f;temporary=(mp[a],nn,c);out.extend((op,mp[a],nn,c,f,z))
        elif op==3:assert temporary==(mp[a],nn,c)and state[mp[a]]==c and state[nn]==f;out.extend((op,mp[a],nn,c,f,z));del state[nn];temporary=None
        if i==entry:
            assert temporary is None
            for r in rows:
                for t in r['targets']:
                    if t!=r['pivot']:add(mp[t],mp[r['pivot']],-1,ZERO,SETUP)
        if i in lastw:
            r=lastw[i]
            for t in r['targets']:
                if t!=r['pivot']:add(mp[t],mp[r['pivot']],1,r['root_frame'],RESTORE)
    assert temporary is None
    nfinal={mp[s]:f for s,f in final.items()if s not in sinks}
    for s in sorted(nfinal):move(s,nfinal[s])
    assert state==nfinal
    ninitial={mp[s]:f for s,f in initial.items()if s not in sinks}
    nends={mp[s]:f for s,f in ends.items()}
    ctx=dict(context);ctx['regs']=[x for j,x in enumerate(regs)if 2*v+j not in sinks];ctx['removed']=set(context['removed'])|{regs[s-2*v]for s in sinks}
    if 'restored_endpoints' in context:ctx['restored_endpoints']=dict(context['restored_endpoints'])
    assert len(ctx['regs'])==nn-2*v
    proof=dict(selected=len(rows),entry=entry,removed_roles=sorted(regs[s-2*v]for s in sinks),targets=sum(len(r['targets'])for r in rows),redirected_writes=len(redirected),deleted_scalar_events=len(dropped),inserted_setups=sum(len(r['targets'])-1 for r in rows),
        targets_never_sources=True,pivot_unwritten_on_interval=True,coefficient_pattern_checked=True,disjoint_target_sets=True,old_n=n,new_n=nn)
    return out,ninitial,nfinal,nends,rows,ctx,cats,proof,nn,v,mp

def run(producer,output_dir=None,selection_path=None):
    start=time.monotonic()
    spec=importlib.util.spec_from_file_location('sink_kernel_replay',HERE/'kernel_transform.py');km=importlib.util.module_from_spec(spec);spec.loader.exec_module(km)
    W,C=producer['W'],producer['C'];path=Path(selection_path)if selection_path else HERE/'sink-selection.json';selection=json.loads(path.read_text())
    out,initial,final,ends,rows,ctx,cats,proof,n,v,mp=transform(producer,selection);ZERO=producer['ZERO']
    forward=km.replay(out,n,v);inverse=km.replay(out,n,v,True);controls=[km.replay(out,n,v,omit_category=cats.index(x))for x in('sink_redirect','sink_setup','sink_restore')]
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
    assert sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass']-24*proof['selected'],'each removed zero-to-full helper frees exactly its 24 rank'
    assert count==producer['physical']['weighted_scalar_events']-proof['deleted_scalar_events']+2*proof['inserted_setups']
    inherited=set()
    for inventory in (producer['physical'],producer.get('producer_physical')):
        if isinstance(inventory,dict):inherited.update(row['frame_id']for row in inventory.get('used_frames',[]))
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    receipt=dict(status='PASS_GEN5_TERMINAL_SINKS_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS',proof=proof,scalar=dict(forward=forward,inverse=inverse,controls=controls),selected=proof['selected'],physical_R=n-2*v,local_histogram_delta=delta,unchanged_surviving_input_output_frames=True,unchanged_copy_lifetimes=True,both_reflected_ledgers=True,unique_required_frame_pairs=len(pairs),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=sha(producer['records'].tobytes()),output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(path.read_bytes()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL_GEN5_TERMINAL_SINKS',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,independent_dirty_registers=n-2*v,physical_registers=n,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(usedf|inherited)],sink_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(context=ctx,records=out,physical=meta,result=meta,sink_census=receipt,initial_state=initial,final_state=final,helper_endpoints=ends,sink_entries=rows,sink_stream_map=mp)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'sink-records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'sink.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS terminal sinks',proof['selected'],'removed roles',proof['removed_roles'],'n',n,count,'scalar ADDs',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
