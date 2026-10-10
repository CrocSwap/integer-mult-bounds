"""New dirty entrance gauges by exact F2 compensation transport.

The original scalar producer context is preserved. The transformed execution
context adds only the newly checked entrance frames. Address arithmetic remains
in the retained odd-prime rings. Substantial OpenAI Codex assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from copy import copy
from pathlib import Path
import gzip,hashlib,json,time
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent

def sha_basis(B):
    return hashlib.sha256(json.dumps(B,separators=(',',':')).encode()).hexdigest()

def transform(producer,selection):
    W,C=producer['W'],producer['C'];old=producer['records'];n=20107;v=1760;ZERO=producer['ZERO'];initial=dict(producer['initial_state']);context=producer['context']
    assert hashlib.sha256(old.tobytes()).hexdigest()==selection['input_raw_sha256']
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    cats=producer['physical']['category_names'];readcat=cats.index('dirty_read');entries=[];chosen={}
    for row in selection['entries']:
        r=dict(row);stream=r['stream'];role=r['role'];assert stream not in chosen and context['regs'][stream-2*v]==role
        assert role not in W.gauge and role not in W.donor and role not in context['borrow'] and initial[stream]==ZERO
        f=W.register(r['basis']);assert C.dimf[f]==r['rank'] and C.nondeg(f)
        r['frame']=f;chosen[stream]=r;entries.append(r)
    assert len(chosen)==len(selection['entries'])>0 and sum(r['rank']for r in entries)==selection['rank_drop']
    core=[k for k in range(0,len(old),6)if old[k]];cut=core[selection['cut_core_ordinal']]
    assert [old[cut+j]for j in(0,1,2,3,5)]==selection['cut_scalar']
    # Derive the transported response directly from the actual prefix, using
    # independent selected dirty columns rather than a precomputed adjoint table.
    bits={r:1<<i for i,r in enumerate(sorted(chosen))};columns=[bits.get(i,0)for i in range(n)];temporary=None;deleted=[];targetops=0
    for k in range(0,cut+6,6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1:
            assert a not in chosen,'Selected helper mutated before compensation transport cut'
            if b in chosen:
                assert z==readcat and f==ZERO and v<=a<2*v and abs(c)==1
                deleted.append(k//6)
            source=temporary if b==n else b;assert source is not None
            if c%2:columns[a]^=columns[source]
            if v<=a<2*v and v<=b<2*v:targetops+=1
        elif op==2:assert temporary is None;temporary=a
        elif op==3:assert temporary==a;temporary=None
    assert temporary is None and targetops==selection['target_prefix_operations']==441
    wanted=[bits.get(i,0)for i in range(n)]
    for r,row in chosen.items():
        for t in row['targets']:wanted[v+t]^=bits[r]
    assert columns==wanted,'Incorrect literal transported compensation response'
    assert len(deleted)==selection['old_reads']
    for r,row in chosen.items():initial[r]=row['frame']
    final=dict(producer['initial_state'])
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    state=dict(initial);out=array('i');temporary=None;skipped=[];inserted=[]
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('Regauged nonnested actual use',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0
        out.extend((0,s,before,f,gap,0));state[s]=f
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1:
            if z==readcat and b in chosen and f==ZERO:
                assert k<=cut;skipped.append(k//6)
            else:move(a,f);move(b,f);out.extend((op,a,b,c,f,z))
        elif op==2:
            assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c);out.extend((op,a,b,c,f,z))
        elif op==3:
            assert temporary==(a,b,c) and state[a]==c and state[b]==f
            out.extend((op,a,b,c,f,z));del state[b];temporary=None
        if k==cut:
            assert temporary is None
            for row in entries:
                r=row['stream'];f=row['frame'];assert state[r]==f
                for t in row['targets']:
                    move(v+t,f);move(r,f);out.extend((1,v+t,r,1,f,readcat));inserted.append((v+t,r))
    assert temporary is None and skipped==deleted and len(inserted)==selection['new_reads']
    for s in sorted(final):move(s,final[s])
    assert state==final
    # Only the documented dirty reads are replaced. Every other scalar and
    # COPY/ERASE instruction must retain literal chronological order.
    def project(a):
        result=[]
        for k in range(0,len(a),6):
            op,x,y,c,f,z=a[k:k+6]
            if op:result.append((op,x,y,c,z))
        return result
    expected=[]
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op and k//6 not in set(deleted):expected.append((op,a,b,c,z))
        if k==cut:expected.extend((1,a,b,1,readcat)for a,b in inserted)
    assert project(out)==expected
    # Clone only execution metadata. Never expose new gauges to the retained
    # source527 producer replay or silently reinterpret its signed decoder.
    execution_context=dict(context);execution_W=copy(W);execution_W.gauge=dict(W.gauge);execution_W.w=dict(W.w);execution_W.w['gauges']=list(W.w['gauges'])
    for row in entries:
        g=dict(role=row['role'],frame=row['frame'],dim=row['rank'],targets=list(row['targets']))
        execution_W.gauge[row['role']]=g;execution_W.w['gauges'].append(g)
    execution_context['W']=execution_W
    assert all(row['role']not in W.gauge for row in entries)
    proof=dict(stable_cut_core_ordinal=selection['cut_core_ordinal'],actual_cut_record=cut//6,target_prefix_operations=targetops,deleted_reads=skipped,inserted_reads=inserted,literal_prefix_transfer_matches=True,selected_helpers_untouched_before_cut=True,noise_before_cut_only_in_targets=True,producer_context_unchanged=True)
    return out,initial,final,entries,execution_context,proof

def scalar_check(records,selection):
    expected_digest=selection['expected_scalar_sha256'];expected_count=selection['expected_scalar_additions'];expected_coeff={int(k):v for k,v in selection['expected_coefficient_counts'].items()}
    n=20107;v=1760;receipts=[]
    for reverse in(False,True):
        columns=[1<<i for i in range(n)];wanted=columns[:];norms=[1]*n;largest=1;center=None;count=0;coeff=Counter();digest=hashlib.sha256()
        for t in range(v):wanted[v+t]^=1<<t
        for k in(range(len(records)-6,-1,-6)if reverse else range(0,len(records),6)):
            op,a,b,c,f,z=records[k:k+6]
            if op==1:
                if b==n:assert center is not None;b=center
                assert c%2;columns[a]^=columns[b];norms[a]+=abs(c)*norms[b];largest=max(largest,norms[a]);coeff[abs(c)]+=1;count+=1
                digest.update(json.dumps([a,b,-c if reverse else c],separators=(',',':')).encode());digest.update(b'\n')
            elif op==(3 if reverse else 2):assert center is None;center=a
            elif op==(2 if reverse else 3):assert center==a;center=None
        assert center is None and columns==wanted and count==expected_count and coeff==expected_coeff
        if not reverse:assert digest.hexdigest()==expected_digest
        receipts.append(dict(reverse=reverse,all_formal_columns=n,all_source_and_dirty_restored=True,weighted_additions=count,event_sha256=digest.hexdigest(),coefficient_counts=dict(coeff),max_intermediate_row_l1=largest))
    assert [r['max_intermediate_row_l1']for r in receipts]==[selection['expected_forward_row_l1'],selection['expected_inverse_row_l1']]
    return dict(forward=receipts[0],inverse=receipts[1])

def run(producer,output_dir=None,selection_path=None):
    begun=time.monotonic();W,C=producer['W'],producer['C'];v=W.v;n=20107
    path=Path(selection_path)if selection_path else HERE/'regauge-selection.json'
    selection=json.loads(path.read_text());old=producer['records'];oldmeta=producer['physical'];initial=producer['initial_state'];ZERO,FULL=producer['ZERO'],producer['FULL']
    out,initial,final,entries,execution_context,transport=transform(producer,selection)
    scalar_receipt=scalar_check(out,selection)
    assert all(final[i]==FULL for i in initial if i<v or i>=2*v)
    for t in range(v):
        f=final[v+t];assert C.dimf[f]==23 and all(W.module.dot(C.cov[t],b)==0 for b in C.B[f])
    # Census is independently rebuilt only from actual surviving ADD needs,
    # frozen COPY source frames, and fixed endpoints, ignoring emitted MOVEs.
    needs={i:[] for i in initial};copies=Counter();copy=None
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==1:
            assert c%2;needs[a].append(f)
            if b!=n:needs[b].append(f)
            else:assert copy is not None and f==ZERO
        elif op==2:
            assert copy is None;copy=(a,b,c);needs[a].append(c);copies[z]+=1
        elif op==3:assert copy==(a,b,c);copy=None
    assert copy is None and copies=={22:24}
    census=Counter(copies);per_role={};pairs=set()
    for s,before in initial.items():
        H=Counter()
        for f in needs[s]+[final[s]]:
            assert C.sub(before,f);rank=C.dimf[f]-C.dimf[before]
            if rank:H[rank]+=1
            pairs.add((before,f));before=f
        per_role[s]=H;census.update(H)
    endpoint_frames={f for pair in pairs for f in pair};nondeg_bases=set()
    for f in endpoint_frames:
        assert len(C.B[f])==C.dimf[f] and len(C.A[f])+C.dimf[f]==24
        key=tuple(map(tuple,C.B[f]))
        if key not in nondeg_bases:assert C.nondeg(f);nondeg_bases.add(key)
    for a,b in pairs:
        assert len(C.A[b])<=len(C.A[a])
        assert all(W.module.dot(x,y)==0 for x in C.A[b]for y in C.B[a])
        assert len(C.A[a])-len(C.A[b])==C.dimf[b]-C.dimf[a]
    state=dict(initial);copy=None;used=set(initial.values());hist=Counter();cat=Counter();coeff=Counter();centers=[];count=0
    scalar=hashlib.sha256();tagged=hashlib.sha256();category_names=oldmeta['category_names']
    def event(d,row):d.update(json.dumps(row,separators=(',',':')).encode());d.update(b'\n')
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==0:
            assert state[a]==b and C.sub(b,c) and C.dimf[c]-C.dimf[b]==f
            assert (24-C.dimf[b])-(24-C.dimf[c])==f
            state[a]=c;used.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert c%2 and state[a]==state[b]==f and a!=b
            kind=category_names[z];source=copy['source']if b==n else b
            event(scalar,[a,source,c]);event(tagged,[a,b,c,f,kind]);count+=1;cat[kind]+=1;coeff[abs(c)]+=1;used.add(f)
        elif op==2:
            assert copy is None and b==n and state[a]==c and f==ZERO and z==22
            state[b]=f;hist[z]+=1;copy=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and copy is not None and (a,b,c)==(copy['source'],copy['temporary'],copy['frame']) and state[a]==c and state[b]==f==ZERO
            copy.update(after_event=count,scatter_reads=count-copy['first_event']);assert copy['scatter_reads']==220
            centers.append(copy);copy=None;del state[b]
    assert copy is None and state==final and hist==census
    assert count==selection['expected_scalar_additions'] and coeff=={int(k):v for k,v in selection['expected_coefficient_counts'].items()} and len(centers)==24
    assert count==oldmeta['weighted_scalar_events']-selection['old_reads']+selection['new_reads']
    assert scalar.hexdigest()==selection['expected_scalar_sha256']
    delta=Counter(hist);delta.subtract(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}));delta={r:c for r,c in delta.items()if c}
    assert delta=={int(r):c for r,c in selection['expected_local_histogram_delta'].items()},('combined local delta',delta)
    assert sum(r*c for r,c in hist.items())==oldmeta['paid_rank_mass']-selection['rank_drop']
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for i,H in per_role.items():(sourceH if i<v else targetH if i<2*v else internalH).update(H)
    receipt=dict(status='PASS_SELECTED_GAUGE_TRANSPORT_AND_BOTH_REFLECTED_LEDGERS',selected_gauge_count=len(entries),total_added_entrance_rank=selection['rank_drop'],transport=transport,scalar=scalar_receipt,remaining_payload_additions=count,local_histogram_delta=delta,both_reflected_ledgers=True,unchanged_data_input_output_and_dirty_output_frames=True,changed_dirty_entrances=True,unchanged_copy_lifetimes=True,unique_required_frame_pairs=len(pairs),explicit_reflected_annihilator_pairs=len(pairs),nondegenerate_endpoint_bases=len(nondeg_bases),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),producer_scalar_sha256=oldmeta['scalar_projection_sha256'],producer_tagged_sha256=oldmeta['tagged_scalar_sha256'],selection_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),new_entrances=entries,seconds=time.monotonic()-begun)
    meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL527_REGAUGED_EXACT_FRAME_AND_SCALAR_PROJECTION',scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha_basis(C.B[f]))for f in sorted(used)],regauge_transform=receipt,initial_independent_entrances=dict(Counter(C.dimf[initial[s]]for s in range(2*v,n)if C.dimf[initial[s]])),physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,regauge_census=receipt,initial_state=initial,context=execution_context,W=execution_context['W'],producer_source_context=producer['context'],new_entrances=entries)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'physical.json').write_text(json.dumps(meta,indent=2)+'\n')
        (p/'regauge.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (p/'regauge-per-role.json').write_text(json.dumps({s:dict(H)for s,H in per_role.items()},indent=2)+'\n')
        (p/'regauge-frame-pairs.json').write_text(json.dumps(sorted(pairs),separators=(',',':'))+'\n')
        (p/'regauge-used-bases.json').write_text(json.dumps({f:dict(basis=C.B[f],annihilator=C.A[f])for f in sorted(used)},separators=(',',':'))+'\n')
    print('PASS gauge transport',len(entries),'gauges',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
