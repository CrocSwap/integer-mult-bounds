"""Exact common-frame retiming of the parity-filtered scalar ADD word.

The selected forward-span and backward-cap frames change only address MOVE
partitions. The scalar instructions, dirty/source endpoints and COPY interfaces
are preserved. Prepared with substantial OpenAI Codex assistance; Apache-2.0.
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
    W,C=producer['W'],producer['C'];old=producer['records'];initial=producer['initial_state'];n=20107
    assert hashlib.sha256(old.tobytes()).hexdigest()==selection['input_raw_sha256']
    assert len(old)//6==selection['source_record_count']
    chosen={};changed=[]
    for r in selection['entries']:
        i=r['record'];assert i not in chosen
        op,a,b,c,f,z=old[6*i:6*i+6]
        assert op==1 and [a,b,c,z]==r['scalar']
        assert C.dimf[f]==r['old_dimension'] and sha_basis(C.B[f])==r['old_basis_sha256']
        g=W.register(r['new_basis'])
        assert C.dimf[g]==r['new_dimension'] and C.nondeg(g)
        assert (C.sub(g,f) if r['direction']=='minimal' else C.sub(f,g))
        chosen[i]=g;changed.append(dict(record=i,old_frame=f,new_frame=g,old_dimension=C.dimf[f],new_dimension=C.dimf[g],basis_sha256=sha_basis(C.B[g]),direction=r['direction']))
    assert len(chosen)==selection['selected_gate_count']==364
    state=dict(initial);final=dict(initial);out=array('i');copy=None
    # Read the original physical endpoints before replacing any MOVE.
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('retimed frame descent',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0
        out.extend((0,s,before,f,gap,0));state[s]=f
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==0:continue
        if op==1:
            f=chosen.get(k//6,f);move(a,f);move(b,f);out.extend((op,a,b,c,f,z))
        elif op==2:
            assert copy is None and b==n;move(a,c);state[b]=f;copy=(a,b,c);out.extend((op,a,b,c,f,z))
        else:
            assert op==3 and copy==(a,b,c) and state[a]==c and state[b]==f
            out.extend((op,a,b,c,f,z));del state[b];copy=None
    assert copy is None
    for s in sorted(final):move(s,final[s])
    assert state==final
    # The complete scalar projection and COPY events are unchanged byte for byte.
    def projection(a):
        result=array('i')
        for k in range(0,len(a),6):
            op,x,y,c,f,z=a[k:k+6]
            if op:result.extend((op,x,y,c,z))
        return result.tobytes()
    assert projection(old)==projection(out)
    return out,final,changed,hashlib.sha256(projection(out)).hexdigest()

def run(producer,output_dir=None,selection_path=None):
    begun=time.monotonic();W,C=producer['W'],producer['C'];v=W.v;n=20107
    path=Path(selection_path)if selection_path else HERE/'retiming-selection.json'
    selection=json.loads(path.read_text());old=producer['records'];oldmeta=producer['physical'];initial=producer['initial_state'];ZERO,FULL=producer['ZERO'],producer['FULL']
    out,final,changed,projection=transform(producer,selection)
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
    assert count==786621 and coeff=={1:785301,3:1320} and len(centers)==24
    assert scalar.hexdigest()==oldmeta['scalar_projection_sha256']
    delta=Counter(hist);delta.subtract(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}));delta={r:c for r,c in delta.items()if c}
    assert delta=={int(r):c for r,c in selection['expected_local_histogram_delta'].items()},('combined local delta',delta)
    assert sum(r*c for r,c in hist.items())==434502
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for i,H in per_role.items():(sourceH if i<v else targetH if i<2*v else internalH).update(H)
    receipt=dict(status='PASS_EXACT_COMMON_FRAME_RETIMING_AND_BOTH_REFLECTED_LEDGERS',selected_gate_count=len(changed),remaining_payload_additions=count,local_histogram_delta=delta,both_reflected_ledgers=True,unchanged_all_input_output_frames=True,unchanged_copy_lifetimes=True,identical_scalar_and_copy_projection_sha256=projection,unique_required_frame_pairs=len(pairs),explicit_reflected_annihilator_pairs=len(pairs),nondegenerate_endpoint_bases=len(nondeg_bases),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),producer_scalar_sha256=oldmeta['scalar_projection_sha256'],producer_tagged_sha256=oldmeta['tagged_scalar_sha256'],selection_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),changed_gates=changed,seconds=time.monotonic()-begun)
    meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL527_RETIMED_EXACT_FRAME_AND_SCALAR_PROJECTION',scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha_basis(C.B[f]))for f in sorted(used)],retiming_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,retiming_census=receipt)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'physical.json').write_text(json.dumps(meta,indent=2)+'\n')
        (p/'retiming.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (p/'retiming-per-role.json').write_text(json.dumps({s:dict(H)for s,H in per_role.items()},indent=2)+'\n')
        (p/'retiming-frame-pairs.json').write_text(json.dumps(sorted(pairs),separators=(',',':'))+'\n')
        (p/'retiming-used-bases.json').write_text(json.dumps({f:dict(basis=C.B[f],annihilator=C.A[f])for f in sorted(used)},separators=(',',':'))+'\n')
    print('PASS frame retiming',len(changed),'gates',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
