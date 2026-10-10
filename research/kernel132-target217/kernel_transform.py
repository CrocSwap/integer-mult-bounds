"""PR254 response-kernel helper pairs composed with PR251's37 entrances.

132-pair construction credited to PR254, commit9ce32ef. Original37-entrance
producer and signed source context are preserved. This composition/audit was
prepared with substantial OpenAI Codex assistance; Apache-2.0.
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
    W,C=producer['W'],producer['C'];old=producer['records'];initial=dict(producer['initial_state']);context=producer['context'];v=1760;n=20107;ZERO=producer['ZERO'];FULL=producer['FULL']
    assert sha(old.tobytes())==selection['input_raw_sha256']
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    cats=list(producer['physical']['category_names']);readcat=cats.index('dirty_read')
    assert 'kernel_setup' not in cats and 'kernel_restore' not in cats
    setupcat=len(cats);restorecat=setupcat+1;cats+=['kernel_setup','kernel_restore']
    cuts=[k for k in range(0,len(old),6)if old[k]==1 and [old[k+j]for j in(0,1,2,3,5)]==selection['cut_scalar']];assert len(cuts)==1;cut=cuts[0]
    entries=[];members=set();chosen={}
    final=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    for pair in selection['pairs']:
        a,b=pair['a'],pair['b'];assert a!=b and a not in members and b not in members and 2*v<=a<n and 2*v<=b<n
        members.update((a,b));role=context['regs'][a-2*v];partner_role=context['regs'][b-2*v]
        for stream,r in ((a,role),(b,partner_role)):
            assert r not in W.gauge and r not in W.donor and r not in context['borrow'] and initial[stream]==ZERO and final[stream]==FULL
        f=W.register(pair['basis']);assert C.dimf[f]==pair['rank']==1 and C.nondeg(f)
        assert all(not W.module.dot(x,y)for x in C.B[f]for y in pair['annihilator']) and len(pair['annihilator'])==23
        u=pair['basis'][0];assert sum(u)==0 and sum(x*x for x in u)==4
        row=dict(pair,stream=a,role=role,partner_role=partner_role,rank=1,frame=f,targets=[]);entries.append(row);chosen[a]=row
    assert len(entries)==132 and len(members)==264 and not members&set(selection['extra16_streams'])
    # Replay all264 selected initial dirty columns through the literal prefix.
    bit={s:1<<i for i,s in enumerate(sorted(members))};columns=[bit.get(i,0)for i in range(n)];temporary=None;deleted=[];reads=Counter();prefix_uses=Counter()
    for k in range(0,cut+6,6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1:
            assert a not in members,'selected helper mutated before kernel cut'
            if b in members:
                assert f==ZERO and z==readcat and v<=a<2*v and c%2
                prefix_uses[b]+=1
                if b in chosen:deleted.append(k//6);reads[b]+=1
            source=temporary if b==n else b;assert source is not None
            if c%2:columns[a]^=columns[source]
        elif op==2:assert temporary is None and a not in members;temporary=a
        elif op==3:assert temporary==a and a not in members;temporary=None
    assert temporary is None and len(deleted)==528 and set(reads.values())=={4}
    for i,col in enumerate(columns):
        if not v<=i<2*v:assert col==bit.get(i,0),'selected response escapes targets or own coordinate'
    response=[]
    for row in entries:
        a,b=row['a'],row['b'];mask=bit[a]|bit[b];support=[]
        for t in range(v):
            q=columns[v+t]&mask;assert q in(0,mask),('unequal actual prefix columns',a,b,t)
            if q:support.append(t)
        assert support;row['prefix_response_targets']=support;response.append(dict(a=a,b=b,targets=support))
    first={}
    for k in range(cut+6,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1:
            for s in(a,b):
                if s in members:first.setdefault(s,f)
        elif op in(2,3)and a in members:first.setdefault(a,c)
    for row in entries:
        for s in(row['a'],row['b']):assert C.dimf[first[s]]==3 and C.sub(row['frame'],first[s])
        row['first_a']=first[row['a']];row['first_b']=first[row['b']];initial[row['a']]=row['frame']
    state=dict(initial);out=array('i');temporary=None;skipped=[]
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('kernel nonnested actual use',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0;out.extend((0,s,before,f,gap,0));state[s]=f
    def add(a,b,c,f,z):
        move(a,f);move(b,f);out.extend((1,a,b,c,f,z))
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1:
            if b in chosen and f==ZERO and z==readcat:
                assert k<=cut;skipped.append(k//6)
            else:add(a,b,c,f,z)
        elif op==2:
            assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c);out.extend((op,a,b,c,f,z))
        elif op==3:
            assert temporary==(a,b,c)and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];temporary=None
        if k==cut:
            assert temporary is None
            for row in entries:add(row['b'],row['a'],1,row['frame'],setupcat)
    assert skipped==deleted and temporary is None
    for s in sorted(final):move(s,final[s])
    for row in entries:add(row['b'],row['a'],-1,FULL,restorecat)
    assert state==final
    # Only selected reads disappear; all others remain in exactly their old order.
    project=lambda aa:[tuple(aa[k+j]for j in(0,1,2,3,5))for k in range(0,len(aa),6)if aa[k]]
    drop=set(deleted);expected=[]
    for k in range(0,len(old),6):
        if old[k] and k//6 not in drop:expected.append(tuple(old[k+j]for j in(0,1,2,3,5)))
        if k==cut:expected.extend((1,r['b'],r['a'],1,setupcat)for r in entries)
    expected.extend((1,r['b'],r['a'],-1,restorecat)for r in entries);assert project(out)==expected
    ew=copy(W);ew.gauge=dict(W.gauge);ew.w=dict(W.w);ew.w['gauges']=list(W.w['gauges'])
    for row in entries:
        g=dict(role=row['role'],frame=row['frame'],dim=1,targets=[]);ew.gauge[row['role']]=g;ew.w['gauges'].append(g)
    execution=dict(context);execution['W']=ew
    assert all(r['role']not in W.gauge for r in entries)
    proof=dict(cut_record=cut//6,selected_pairs=len(entries),selected_helpers=len(members),extra16_overlap=[],all37_overlap=[],prefix_target_comparisons=132*v,prefix_response=response,removed_initial_reads=len(skipped),added_setup_and_restores=264,selected_helpers_untouched=True,no_prefix_response_outside_targets_and_own_helper=True,all_old_surviving_scalar_and_copy_events_in_order=True,source_context_preserved=True)
    return out,initial,final,entries,execution,cats,proof

def replay(records,reverse=False,omit_category=None):
    n=20107;v=1760;columns=[1<<i for i in range(n+1)];wanted=[1<<i for i in range(n)];norm=[1]*(n+1);largest=1;temporary=None;count=0;coeff=Counter();digest=hashlib.sha256()
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
    out,initial,final,entries,context,cats,proof=transform(producer,selection);n=20107;v=1760;ZERO=producer['ZERO'];FULL=producer['FULL']
    forward=replay(out);inverse=replay(out,True);controls=[replay(out,omit_category=cats.index('kernel_setup')),replay(out,omit_category=cats.index('kernel_restore'))]
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
    assert delta=={int(k):v for k,v in selection['expected_local_delta'].items()}=={1:132,2:264,3:-264}
    assert count==producer['physical']['weighted_scalar_events']-264 and sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass']-132
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    receipt=dict(status='PASS_PR254_KERNEL132_ON_PR251_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS',proof=proof,scalar=dict(forward=forward,inverse=inverse,controls=controls),selected_pairs=132,rank_drop=132,local_histogram_delta=delta,unchanged_data_input_output_and_dirty_output_frames=True,unchanged_copy_lifetimes=True,both_reflected_ledgers=True,unique_required_frame_pairs=len(pairs),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=sha(producer['records'].tobytes()),output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(path.read_bytes()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL527_KERNEL132_ON_37_ENTRANCES',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used)],kernel_transform=receipt,initial_independent_entrances=dict(Counter(C.dimf[initial[s]]for s in range(2*v,n)if C.dimf[initial[s]])),physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,kernel_census=receipt,initial_state=initial,context=context,W=context['W'],producer_source_context=producer.get('producer_source_context',producer['context']),new_entrances=list(producer.get('new_entrances',[]))+entries,kernel_entrances=entries)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        for name,value in [('physical',meta),('kernel',receipt),('kernel-initial',initial),('kernel-final',final),('kernel-per-role',{s:dict(H)for s,H in per_role.items()}),('kernel-frame-pairs',sorted(pairs)),('kernel-used-bases',{f:dict(basis=C.B[f],annihilator=C.A[f])for f in sorted(used)}),('kernel-entrances',entries)]:
            (p/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print('PASS kernel132 on PR251',count,'scalar ADDs',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
