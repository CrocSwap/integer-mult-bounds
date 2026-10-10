"""Response-kernel entries (twin pairs and multi-donor families) with per-entry cuts on the gen4 word.

Generalizes the per-pair-cut adaptation of #268's kernel_transform.py (PR254 pairs, eumemic / OpenAI Codex)
to entries with a pivot p, donors D (one donor: twin pair; two or three: collective family, #272-style) and an
entrance E of rank e >= 1 (basis rows), nondegenerate for 9I-J and inside every member's first frame. The entry
cut is the later of the members' last initial (frame-ZERO) compensation reads, bound by content. At the cut each
donor pays d += p at E (kernel_setup); at the end each pays d -= p at the full frame (kernel_restore); the pivot
starts at E and loses its initial reads. A donor may serve several entries along a nested entrance chain (the
emitted MOVEs are checked nested). Correctness is the F2 replay of every formal column, forward and inverse, with
both omission controls; the prefix relation (pivot response = XOR of donor responses) is checked on the literal
prefix; every required frame path is rebuilt from scalar/COPY events independently of the emitted MOVEs.
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
    assert 'higher_kernel_setup' not in cats and 'higher_kernel_restore' not in cats
    setupcat=len(cats);restorecat=setupcat+1;cats+=['higher_kernel_setup','higher_kernel_restore']
    final=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    raw_entries=[dict(pivot=p['a'],donors=[p['b']],cut_read=p['cut_read'],rank=p['rank'],basis=p['basis'],kind='pair')for p in selection['pairs']]
    raw_entries+=[dict(pivot=f['pivot'],donors=list(f['donors']),cut_read=f['cut_read'],rank=f['rank'],basis=f['basis'],kind=f.get('kind','family'))for f in selection.get('families',[])]
    assert len(raw_entries)==selection['selected_pairs']+selection.get('selected_families',0)
    members=set();pivots=set();donorset=set()
    for e in raw_entries:
        p=e['pivot'];assert p not in pivots and 2*v<=p<n;pivots.add(p);members.add(p)
        for d in e['donors']:assert d!=p and 2*v<=d<n;donorset.add(d);members.add(d)
    assert not(pivots&donorset),'pivot used as a donor (non-nilpotent support)'
    # Literal prefix facts: last initial read and first other use of every member.
    lastread={};firsttouch={};reads=Counter()
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:
            if b in members and z==readcat and f==ZERO and v<=a<2*v and c%2:lastread[b]=i;reads[b]+=1;continue
            for s in (a,b):
                if s in members and s not in firsttouch:firsttouch[s]=(i,f)
        elif op==2:
            if a in members and a not in firsttouch:firsttouch[a]=(i,c)
    entries=[];bycut={};memcut={};chosen={}
    for e in raw_entries:
        ms=[e['pivot']]+e['donors']
        for s in ms:
            r=context['regs'][s-2*v];assert r not in W.gauge and r not in W.donor and r not in context['borrow'] and initial[s]==ZERO and final[s]==FULL and reads[s]>0
        cut=max(lastread[s]for s in ms);assert [old[6*cut+j]for j in(1,2,3)]==e['cut_read'],('cut read differs',e['pivot'])
        assert cut<min(firsttouch[s][0]for s in ms),('a member is touched before the entry cut',e['pivot'])
        f=W.register(e['basis']);assert C.dimf[f]==e['rank']==len(e['basis'])>=1 and C.nondeg(f),('entrance',e['pivot'])
        for s in ms:assert C.sub(f,firsttouch[s][1]),('entrance not inside first frame',s)
        row=dict(e,cut=cut,frame=f,role=context['regs'][e['pivot']-2*v],first_frames={str(s):firsttouch[s][1]for s in ms},removed_reads=reads[e['pivot']])
        entries.append(row);chosen[e['pivot']]=row;bycut.setdefault(cut,[]).append(row);initial[e['pivot']]=f
        for s in ms:memcut[s]=max(memcut.get(s,-1),cut)
    for cut in bycut:bycut[cut].sort(key=lambda r:(r['rank'],r['pivot']))
    # Prefix relation on the literal prefix up to the latest cut: pivot response = XOR of donor responses, confined
    # to targets and own coordinates.
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
    relations=0
    for row in entries:
        p=row['pivot'];support=[]
        for t in range(v):
            col=columns[v+t];x=(col>>sorted(members).index(p))&1 if False else bool(col&bit[p])
            y=0
            for d in row['donors']:y^=bool(col&bit[d])
            assert x==y,('prefix relation fails',p,t)
            if x:support.append(t)
        assert support;row['prefix_response_targets']=support;relations+=1
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
            else:
                if not(b in members and z==readcat and f==ZERO and v<=a<2*v):
                    for s in (a,b):
                        if s in members:assert i>memcut[s],('touched before cut',s)
                add(a,b,c,f,z)
        elif op==2:
            assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c);out.extend((op,a,b,c,f,z))
            if a in members:assert i>memcut[a]
        elif op==3:
            assert temporary==(a,b,c)and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];temporary=None
        if i in bycut:
            assert temporary is None
            for row in bycut[i]:
                for d in row['donors']:add(d,row['pivot'],1,row['frame'],setupcat)
    assert len(skipped)==sum(r['removed_reads']for r in entries)and temporary is None
    for s in sorted(final):move(s,final[s])
    for row in entries:
        for d in row['donors']:add(d,row['pivot'],-1,FULL,restorecat)
    assert state==final
    project=lambda aa:[tuple(aa[k+j]for j in(0,1,2,3,5))for k in range(0,len(aa),6)if aa[k]]
    drop=set(skipped);expected=[]
    for k in range(0,len(old),6):
        i=k//6
        if old[k] and i not in drop:expected.append(tuple(old[k+j]for j in(0,1,2,3,5)))
        if i in bycut:expected.extend((1,d,r['pivot'],1,setupcat)for r in bycut[i]for d in r['donors'])
    expected.extend((1,d,r['pivot'],-1,restorecat)for r in entries for d in r['donors']);assert project(out)==expected
    ew=copy(W);ew.gauge=dict(W.gauge);ew.w=dict(W.w);ew.w['gauges']=list(W.w['gauges'])
    for row in entries:
        g=dict(role=row['role'],frame=row['frame'],dim=row['rank'],targets=[]);ew.gauge[row['role']]=g;ew.w['gauges'].append(g)
    execution=dict(context);execution['W']=ew
    gates=sum(len(r['donors'])for r in entries);shared=Counter(Counter(d for r in entries for d in r['donors']).values())
    proof=dict(selected_entries=len(entries),kinds=dict(Counter(r['kind']for r in entries)),selected_helpers=len(members),distinct_cuts=len(bycut),earliest_cut=min(bycut),latest_cut=latest,entrance_rank_histogram=dict(Counter(r['rank']for r in entries)),total_entrance_rank=sum(r['rank']for r in entries),donor_sharing_histogram={str(k):c for k,c in sorted(shared.items())},prefix_relations_checked=relations,prefix_target_comparisons=len(entries)*v,removed_initial_reads=len(skipped),added_setup_and_restores=2*gates,selected_helpers_untouched_before_own_cut=True,no_prefix_response_outside_targets_and_own_helper=True,all_old_surviving_scalar_and_copy_events_in_order=True,source_context_preserved=True)
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
    forward=replay(out,n,v);inverse=replay(out,n,v,True);controls=[replay(out,n,v,omit_category=cats.index('higher_kernel_setup')),replay(out,n,v,omit_category=cats.index('higher_kernel_restore'))]
    needs={s:[]for s in initial};copies=Counter();temporary=None
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==1:
            needs[a].append(f)
            if b!=n:needs[b].append(f)
            else:assert temporary is not None and f==ZERO
        elif op==2:assert temporary is None;temporary=(a,b,c);needs[a].append(c);copies[z]+=1
        elif op==3:assert temporary==(a,b,c);temporary=None
    assert temporary is None and copies=={W.h-2:W.h}
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
    for f in {x for pair in pairs for x in pair}:assert C.nondeg(f)and len(C.B[f])+len(C.A[f])==W.h
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
            assert temporary is None and b==n and state[a]==c and f==ZERO and z==W.h-2
            state[b]=f;hist[z]+=1;temporary=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and temporary is not None and (a,b,c)==(temporary['source'],temporary['temporary'],temporary['frame'])and state[a]==c and state[b]==f==ZERO
            temporary.update(after_event=count,scatter_reads=count-temporary['first_event']);assert temporary['scatter_reads']==3*v//W.h;centers.append(temporary);temporary=None;del state[b]
    assert state==final and temporary is None and hist==census and len(centers)==W.h
    old=Counter({int(r):c for r,c in producer['physical']['paid_histogram'].items()});delta=Counter(hist);delta.subtract(old);delta={r:c for r,c in delta.items()if c}
    assert delta=={int(k):v for k,v in selection['expected_local_delta'].items()}
    assert count==producer['physical']['weighted_scalar_events']-proof['removed_initial_reads']+proof['added_setup_and_restores'] and sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass']-proof['total_entrance_rank']
    # Physical inventory: frames consumed by the preceding stages stay in the determinant inventory.
    inherited=set()
    for inventory in (producer['physical'],producer.get('producer_physical')):
        if isinstance(inventory,dict):inherited.update(row['frame_id']for row in inventory.get('used_frames',[]))
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    receipt=dict(status='PASS_GEN4_PER_ENTRY_CUT_KERNEL_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS',proof=proof,scalar=dict(forward=forward,inverse=inverse,controls=controls),selected_pairs=proof['kinds'].get('pair',0),selected_entries=len(entries),rank_drop=proof['total_entrance_rank'],local_histogram_delta=delta,unchanged_data_input_output_and_dirty_output_frames=True,unchanged_copy_lifetimes=True,both_reflected_ledgers=True,unique_required_frame_pairs=len(pairs),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=sha(producer['records'].tobytes()),output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(path.read_bytes()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL_GEN4_KERNEL_ENTRIES',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-W.h,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used|inherited)],kernel_transform=receipt,initial_independent_entrances=dict(Counter(C.dimf[initial[s]]for s in range(2*v,n)if C.dimf[initial[s]])),producer_physical_emitter_sha256=producer['physical'].get('physical_emitter_sha256'),physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,kernel_census=receipt,initial_state=initial,context=context,W=context['W'],kernel_entrances=entries)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'kernel-records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        for name,value in [('kernel',receipt),('kernel-initial',initial),('kernel-entrances',[{k:v for k,v in e.items()if k!='prefix_response_targets'}for e in entries])]:
            (p/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print('PASS kernel entries',len(entries),dict(proof['kinds']),'rank',proof['total_entrance_rank'],count,'scalar ADDs',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
