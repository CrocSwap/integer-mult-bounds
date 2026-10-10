"""Exact frame retiming of the parity-fused paired-cube ADD word by concave rank descent (gen5 stage, shape-generalized to the p = 10 word).

Selected ADD gates receive new nondegenerate frames. The scalar instructions,
all source/dirty/target endpoints, COPY interfaces and the rank mass are
preserved; only address MOVE partitions change. Every retimed gate frame must
contain the exact integer source span of each non-target operand, which is
recomputed here from the actual word. Prepared by Rohan Arun with Anthropic
Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent

def sha_basis(B):
    return hashlib.sha256(json.dumps(B,separators=(',',':')).encode()).hexdigest()

def transform(producer,selection):
    W,C=producer['W'],producer['C'];old=producer['records'];initial=producer['initial_state'];v=W.v;n=len(initial)
    assert hashlib.sha256(old.tobytes()).hexdigest()==selection['input_raw_sha256']
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    assert len(old)//6==selection['source_record_count']
    chosen={};changed=[]
    for r in selection['entries']:
        i=r['record'];assert i not in chosen
        op,a,b,c,f,z=old[6*i:6*i+6]
        assert op==1 and b!=n and [a,b,c,z]==r['scalar']
        assert C.dimf[f]==r['old_dimension'] and sha_basis(C.B[f])==r['old_basis_sha256']
        g=W.register(r['new_basis'])
        assert C.dimf[g]==r['new_dimension'] and C.nondeg(g) and not(C.sub(f,g) and C.sub(g,f))
        chosen[i]=g;changed.append(dict(record=i,old_frame=f,new_frame=g,old_dimension=C.dimf[f],new_dimension=C.dimf[g],basis_sha256=sha_basis(C.B[g])))
    assert len(chosen)==selection['selected_gate_count']>0
    final=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    # Exact integer source spans of every non-target operand, from the actual
    # scalar word. Each gate frame must contain the span after the gate.
    columns=[{i:1} if i<v else {} for i in range(n)];center=None;spans={}
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==0:continue
        if op==2:assert center is None;center=a;continue
        if op==3:assert center==a;center=None;continue
        source=center if b==n else b;assert source is not None;ca=columns[a]
        for s,x in columns[source].items():
            y=ca.get(s,0)+c*x
            if y:ca[s]=y
            else:del ca[s]
        if k//6 in chosen:
            need=set()
            if not(v<=a<2*v):need.update(ca)
            if not(v<=b<2*v) and b!=n:need.update(columns[b])
            spans[k//6]=sorted(need)
    assert center is None
    for i,g in chosen.items():
        for s in spans[i]:assert all(W.module.dot(x,C.chi[s])==0 for x in C.A[g]),('retimed frame omits operand source span',i,s)
    state=dict(initial);out=array('i');copy=None
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('descent frame nesting',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0
        out.extend((0,s,before,f,gap,0));state[s]=f
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==0:continue
        if op==1:
            g=chosen.get(k//6,f)
            if copy is not None:assert a!=copy[0] and b!=copy[0] or k//6 not in chosen
            move(a,g)
            if b==n:assert g==f==producer['ZERO'] and copy is not None
            else:move(b,g)
            out.extend((op,a,b,c,g,z))
        elif op==2:
            assert copy is None and b==n;move(a,c);state[b]=f;copy=(a,b,c);out.extend((op,a,b,c,f,z))
        else:
            assert op==3 and copy==(a,b,c) and state[a]==c and state[b]==f
            out.extend((op,a,b,c,f,z));del state[b];copy=None
    assert copy is None
    for s in sorted(final):move(s,final[s])
    assert state==final
    def projection(a):
        result=array('i')
        for k in range(0,len(a),6):
            op,x,y,c,f,z=a[k:k+6]
            if op:result.extend((op,x,y,c,z))
        return result.tobytes()
    assert projection(old)==projection(out)
    return out,final,changed,spans,hashlib.sha256(projection(out)).hexdigest()

def run(producer,output_dir=None,selection_path=None):
    begun=time.monotonic();W,C=producer['W'],producer['C'];v=W.v;n=len(producer['initial_state']);HH=W.h;CENTER=HH-2;CENTERS=HH;SCATTER=3*v//HH   # paired-cube shape: h coordinates, h copied centres of rank h-2, 3v/h scatter reads each
    path=Path(selection_path)if selection_path else HERE/'descent-selection.json'
    selection=json.loads(path.read_text());old=producer['records'];oldmeta=producer['physical'];initial=producer['initial_state'];ZERO,FULL=producer['ZERO'],producer['FULL']
    out,final,changed,spans,projection=transform(producer,selection)
    assert all(final[i]==FULL for i in initial if i<v or i>=2*v)
    for t in range(v):
        f=final[v+t];assert C.dimf[f]==HH-1 and all(W.module.dot(C.cov[t],b)==0 for b in C.B[f])
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
    assert copy is None and copies=={CENTER:CENTERS}
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
        assert len(C.B[f])==C.dimf[f] and len(C.A[f])+C.dimf[f]==HH
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
            assert (HH-C.dimf[b])-(HH-C.dimf[c])==f
            state[a]=c;used.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert c%2 and state[a]==state[b]==f and a!=b
            kind=category_names[z];source=copy['source']if b==n else b
            event(scalar,[a,source,c]);event(tagged,[a,b,c,f,kind]);count+=1;cat[kind]+=1;coeff[abs(c)]+=1;used.add(f)
        elif op==2:
            assert copy is None and b==n and state[a]==c and f==ZERO and z==CENTER
            state[b]=f;hist[z]+=1;copy=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and copy is not None and (a,b,c)==(copy['source'],copy['temporary'],copy['frame']) and state[a]==c and state[b]==f==ZERO
            copy.update(after_event=count,scatter_reads=count-copy['first_event']);assert copy['scatter_reads']==SCATTER
            centers.append(copy);copy=None;del state[b]
    assert copy is None and state==final and hist==census
    assert count==oldmeta['weighted_scalar_events']==selection['expected_scalar_additions'] and coeff==dict((int(k),v)for k,v in oldmeta['coefficient_histogram'].items()) and len(centers)==CENTERS
    assert scalar.hexdigest()==oldmeta['scalar_projection_sha256']
    delta=Counter(hist);delta.subtract(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}));delta={r:c for r,c in delta.items()if c}
    assert delta=={int(r):c for r,c in selection['expected_local_histogram_delta'].items()},('combined local delta',delta)
    assert sum(r*c for r,c in hist.items())==oldmeta['paid_rank_mass']==selection['expected_rank_mass']
    assert sum(hist.values())==oldmeta['positive_rank_moves']+CENTERS-selection['expected_removed_calls']
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for i,H in per_role.items():(sourceH if i<v else targetH if i<2*v else internalH).update(H)
    receipt=dict(status='PASS_CONCAVE_DESCENT_RETIMING_AND_BOTH_REFLECTED_LEDGERS',selected_gate_count=len(changed),remaining_payload_additions=count,local_histogram_delta=delta,removed_calls=selection['expected_removed_calls'],both_reflected_ledgers=True,unchanged_all_input_output_frames=True,unchanged_copy_lifetimes=True,operand_source_spans_contained=True,checked_operand_spans=sum(len(s)for s in spans.values()),identical_scalar_and_copy_projection_sha256=projection,unique_required_frame_pairs=len(pairs),explicit_reflected_annihilator_pairs=len(pairs),nondegenerate_endpoint_bases=len(nondeg_bases),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),producer_scalar_sha256=oldmeta['scalar_projection_sha256'],producer_tagged_sha256=oldmeta['tagged_scalar_sha256'],selection_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),changed_gates=changed,seconds=time.monotonic()-begun)
    meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL527_DESCENT_RETIMED_EXACT_FRAME_AND_SCALAR_PROJECTION',scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha_basis(C.B[f]))for f in sorted(used)],descent_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,descent_census=receipt)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'physical.json').write_text(json.dumps(meta,indent=2)+'\n')
        (p/'descent.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (p/'descent-per-role.json').write_text(json.dumps({s:dict(H)for s,H in per_role.items()},indent=2)+'\n')
        (p/'descent-frame-pairs.json').write_text(json.dumps(sorted(pairs),separators=(',',':'))+'\n')
        (p/'descent-used-bases.json').write_text(json.dumps({f:dict(basis=C.B[f],annihilator=C.A[f])for f in sorted(used)},separators=(',',':'))+'\n')
    print('PASS concave descent retiming',len(changed),'gates',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
