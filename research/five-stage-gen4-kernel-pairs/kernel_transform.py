"""Response-kernel helper pairs with per-pair cuts on the gen4 word.

Adaptation of #268's kernel_transform.py (PR254 pairs, eumemic / OpenAI Codex) to the
gen4 word, whose compensation reads are chronological: every selected helper has all its
initial dirty reads before its first other use, so each pair (a,b) gets its own cut, the
record index of the later of the two helpers' last initial reads. At that cut the pivot
a is entered at a nondegenerate line E inside both helpers' first frames, the donor pays
b += a at E (kernel_setup) and b -= a at the full frame (kernel_restore); the pivot's
initial reads are removed. The F2 replay of every formal column (forward and inverse)
and two omission controls check the rewritten word; every required frame path is
rebuilt from scalar/COPY events independently of the emitted MOVEs.
Prepared with Anthropic Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from copy import copy
from pathlib import Path
import gzip,hashlib,json,time,sys
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def transform(producer,selection):
    W,C=producer['W'],producer['C'];old=producer['records'];initial=dict(producer['initial_state']);context=producer['context'];v=W.v;n=2*v+len(context['regs']);ZERO=producer['ZERO'];FULL=producer['FULL']
    assert n==selection['n'] and v==selection['v']
    assert sha(old.tobytes())==selection['input_raw_sha256']
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    cats=list(producer['physical']['category_names']);readcat=cats.index('dirty_read')
    assert 'kernel_setup' not in cats and 'kernel_restore' not in cats
    setupcat=len(cats);restorecat=setupcat+1;cats+=['kernel_setup','kernel_restore']
    final=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    entries=[];members=set();chosen={};bycut={}
    for pair in selection['pairs']:
        a,b=pair['a'],pair['b'];assert a!=b and a not in members and b not in members and 2*v<=a<n and 2*v<=b<n
        # The cut is bound by content, not by record index: the later of the two helpers' last initial reads.
        cut=max(i for i in range(len(old)//6)if old[6*i]==1 and old[6*i+5]==readcat and old[6*i+4]==ZERO and old[6*i+2]in(a,b))
        assert [old[6*cut+j]for j in(1,2,3)]==pair['cut_read'],('cut read differs',a,b)
        members.update((a,b));role=context['regs'][a-2*v];partner_role=context['regs'][b-2*v]
        for stream,r in ((a,role),(b,partner_role)):
            assert r not in W.gauge and r not in W.donor and r not in context['borrow'] and initial[stream]==ZERO and final[stream]==FULL
        f=W.register(pair['basis']);assert C.dimf[f]==pair['rank']==1 and C.nondeg(f)
        u=pair['basis'][0];assert 9*sum(x*x for x in u)-sum(u)**2!=0
        row=dict(pair,cut=cut,stream=a,role=role,partner_role=partner_role,frame=f,targets=[]);entries.append(row);chosen[a]=row;bycut.setdefault(cut,[]).append(row)
    assert len(entries)==selection['selected_pairs'] and len(members)==2*len(entries)
    # Literal prefix facts per pair: all initial reads of both helpers precede the pair's cut, both are
    # otherwise untouched up to the cut, and the pivot's reads land only in targets with odd coefficient.
    lastread={};firsttouch={};reads=Counter();temporary=None
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:
            if b in members and z==readcat and f==ZERO and v<=a<2*v and c%2:lastread[b]=i;reads[b]+=1;continue
            for s in (a,b):
                if s in members and s not in firsttouch:firsttouch[s]=(i,f)
        elif op==2:
            if a in members and a not in firsttouch:firsttouch[a]=(i,c)
    first={}
    for row in entries:
        a,b,cut=row['a'],row['b'],row['cut']
        for s in (a,b):
            assert reads[s]>0 and lastread[s]<=cut<firsttouch[s][0],('reads or touches straddle the cut',s)
            first[s]=firsttouch[s][1];assert C.sub(row['frame'],first[s]),('entrance not inside first frame',s)
        row['first_a']=first[a];row['first_b']=first[b];row['removed_reads']=reads[a];initial[a]=row['frame']
    # Replay all selected initial dirty columns through the literal prefix up to the latest cut: the
    # response of every selected helper is confined to targets and its own coordinate, and twins agree.
    latest=max(bycut);bit={s:1<<i for i,s in enumerate(sorted(members))};columns=[bit.get(i,0)for i in range(n+1)];temporary=None
    for k in range(0,6*latest+6,6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1:
            source=temporary if b==n else b;assert source is not None
            if c%2:columns[a]^=columns[source]
        elif op==2:assert temporary is None;temporary=a
        elif op==3:assert temporary==a;temporary=None
    for i,col in enumerate(columns):
        if not v<=i<2*v:assert col==bit.get(i,0),'selected response escapes targets or own coordinate'
    response=[]
    for row in entries:
        a,b=row['a'],row['b'];mask=bit[a]|bit[b];support=[]
        for t in range(v):
            q=columns[v+t]&mask;assert q in(0,mask),('unequal actual prefix columns',a,b,t)
            if q:support.append(t)
        assert support;row['prefix_response_targets']=support;response.append(dict(a=a,b=b,cut=row['cut'],targets=support))
    state=dict(initial);out=array('i');temporary=None;skipped=[]
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('kernel nonnested actual use',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0;out.extend((0,s,before,f,gap,0));state[s]=f
    def add(a,b,c,f,z):
        move(a,f);move(b,f);out.extend((1,a,b,c,f,z))
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:
            if b in chosen and f==ZERO and z==readcat:
                assert i<=chosen[b]['cut'];skipped.append(i)
            else:add(a,b,c,f,z)
        elif op==2:
            assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c);out.extend((op,a,b,c,f,z))
        elif op==3:
            assert temporary==(a,b,c)and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];temporary=None
        if i in bycut:
            assert temporary is None
            for row in bycut[i]:add(row['b'],row['a'],1,row['frame'],setupcat)
    assert len(skipped)==sum(r['removed_reads']for r in entries)and temporary is None
    for s in sorted(final):move(s,final[s])
    for row in entries:add(row['b'],row['a'],-1,FULL,restorecat)
    assert state==final
    # Only selected reads disappear; all others remain in exactly their old order.
    project=lambda aa:[tuple(aa[k+j]for j in(0,1,2,3,5))for k in range(0,len(aa),6)if aa[k]]
    drop=set(skipped);expected=[]
    for k in range(0,len(old),6):
        i=k//6
        if old[k] and i not in drop:expected.append(tuple(old[k+j]for j in(0,1,2,3,5)))
        if i in bycut:expected.extend((1,r['b'],r['a'],1,setupcat)for r in bycut[i])
    expected.extend((1,r['b'],r['a'],-1,restorecat)for r in entries);assert project(out)==expected
    ew=copy(W);ew.gauge=dict(W.gauge);ew.w=dict(W.w);ew.w['gauges']=list(W.w['gauges'])
    for row in entries:
        g=dict(role=row['role'],frame=row['frame'],dim=1,targets=[]);ew.gauge[row['role']]=g;ew.w['gauges'].append(g)
    execution=dict(context);execution['W']=ew
    proof=dict(selected_pairs=len(entries),selected_helpers=len(members),distinct_cuts=len(bycut),earliest_cut=min(bycut),latest_cut=latest,prefix_target_comparisons=len(entries)*v,prefix_response=response,removed_initial_reads=len(skipped),added_setup_and_restores=2*len(entries),selected_helpers_untouched_before_own_cut=True,no_prefix_response_outside_targets_and_own_helper=True,all_old_surviving_scalar_and_copy_events_in_order=True,source_context_preserved=True)
    return out,initial,final,entries,execution,cats,proof,n,v

def replay(records,n,v,reverse=False,omit_category=None):
    columns=[1<<i for i in range(n+1)];wanted=[1<<i for i in range(n)];norm=[1]*(n+1);largest=1;temporary=None;count=0;coeff=Counter();digest=hashlib.sha256()
    for t in range(v):wanted[v+t]^=1<<t
    for k in(range(len(records)-6,-1,-6)if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            if z==omit_category:continue
            assert c%2 and (b!=n or temporary is not None)
            columns[a]^=columns[b];norm[a]+=abs(c)*norm[b];largest=max(largest,norm[a]);count+=1;coeff[abs(c)]+=1
            digest.update(json.dumps([a,temporary if b==n else b,-c if reverse else c],separators=(',',':')).encode());digest.update(b'\n')
        elif op==(3 if reverse else 2):
            assert temporary is None and b==n;temporary=a;columns[b]=columns[a];norm[b]=norm[a]
        elif op==(2 if reverse else 3):
            assert temporary==a and b==n and columns[a]==columns[b];temporary=None
    assert temporary is None
    wrong=[i for i in range(n)if columns[i]!=wanted[i]]
    if omit_category is None:assert not wrong,('kernel scalar failure',reverse,wrong[:20])
    else:assert wrong,'vacuous kernel omitted-gate control'
    return dict(reverse=reverse,formal_columns=n,wrong_rows=len(wrong),all_sources_and_dirty_restored=not wrong,scalar_additions=count,coefficient_counts=dict(coeff),event_sha256=digest.hexdigest(),max_intermediate_row_l1=largest)

def run(producer,output_dir=None,selection_path=None):
    start=time.monotonic();W,C=producer['W'],producer['C'];path=Path(selection_path)if selection_path else HERE/'kernel-selection.json';selection=json.loads(path.read_text())
    out,initial,final,entries,context,cats,proof,n,v=transform(producer,selection);ZERO=producer['ZERO'];FULL=producer['FULL']
    forward=replay(out,n,v);inverse=replay(out,n,v,True);controls=[replay(out,n,v,omit_category=cats.index('kernel_setup')),replay(out,n,v,omit_category=cats.index('kernel_restore'))]
    # Rebuild every required-frame path from scalar/COPY events independently of emitted MOVEs.
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
    # Check actual stream states and COPY/ERASE lifetimes against emitted record metadata.
    state=dict(initial);hist=Counter();cat=Counter();coeff=Counter();used=set(state.values());temporary=None;centers=[];count=0;tagged=hashlib.sha256()
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==0:
            assert state[a]==b and C.sub(b,c)and C.dimf[c]-C.dimf[b]==f and len(C.A[b])-len(C.A[c])==f
            state[a]=c;used.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert state[a]==state[b]==f and a!=b and c%2;count+=1;cat[cats[z]]+=1;coeff[abs(c)]+=1;used.add(f)
            tagged.update(json.dumps([a,b,c,f,cats[z]],separators=(',',':')).encode());tagged.update(b'\n')
        elif op==2:
            assert temporary is None and b==n and state[a]==c and f==ZERO and z==22
            state[b]=f;hist[z]+=1;temporary=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and temporary is not None and (a,b,c)==(temporary['source'],temporary['temporary'],temporary['frame'])and state[a]==c and state[b]==f==ZERO
            temporary.update(after_event=count,scatter_reads=count-temporary['first_event']);assert temporary['scatter_reads']==220;centers.append(temporary);temporary=None;del state[b]
    assert state==final and temporary is None and hist==census and len(centers)==24
    old=Counter({int(r):c for r,c in producer['physical']['paid_histogram'].items()});delta=Counter(hist);delta.subtract(old);delta={r:c for r,c in delta.items()if c}
    assert delta=={int(k):v for k,v in selection['expected_local_delta'].items()}
    assert count==producer['physical']['weighted_scalar_events']-proof['removed_initial_reads']+2*len(entries) and sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass']-len(entries)
    # Physical inventory: frames the preceding stages consumed stay in the determinant inventory (a retimed gate's
    # former frame is still a required base of the virtual word), so prime_check's coverage is a superset check.
    inherited=set()
    for inventory in (producer['physical'],producer.get('producer_physical'),producer.get('descent_producer_physical'),producer.get('parity_producer_physical')):
        if isinstance(inventory,dict):inherited.update(row['frame_id']for row in inventory.get('used_frames',[]))
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    receipt=dict(status='PASS_GEN4_PER_PAIR_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS',proof=proof,scalar=dict(forward=forward,inverse=inverse,controls=controls),selected_pairs=len(entries),rank_drop=len(entries),local_histogram_delta=delta,unchanged_data_input_output_and_dirty_output_frames=True,unchanged_copy_lifetimes=True,both_reflected_ledgers=True,unique_required_frame_pairs=len(pairs),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=sha(producer['records'].tobytes()),output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(path.read_bytes()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL_GEN4_KERNEL_PAIRS',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used|inherited)],kernel_transform=receipt,initial_independent_entrances=dict(Counter(C.dimf[initial[s]]for s in range(2*v,n)if C.dimf[initial[s]])),producer_physical_emitter_sha256=producer['physical'].get('physical_emitter_sha256'),physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,kernel_census=receipt,initial_state=initial,context=context,W=context['W'],kernel_entrances=entries)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'kernel-records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        for name,value in [('kernel',receipt),('kernel-initial',initial),('kernel-entrances',[{k:v for k,v in e.items()if k!='prefix_response_targets'}for e in entries])]:
            (p/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print('PASS kernel pairs',len(entries),'pairs',count,'scalar ADDs',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
