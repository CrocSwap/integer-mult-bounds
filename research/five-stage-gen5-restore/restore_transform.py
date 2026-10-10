"""Exact early restoration of gen5 cleanup helpers (PR280's lever, on the gen5 word).

At the first cleanup ADD of the word every data target already has its scalar
endpoints. A selected helper a whose only later scalar incidence is one write
`a -= c*b` with a donor b that is not written in between has that write moved
to the cut: a and b advance from their current frames to their rational span
E (a nondegenerate 23-dimensional frame), the unchanged ADD runs at E and a
retires at E instead of climbing to the full frame; b continues as before. The
ADD commutes over the integers with every crossed gate because none of them
reads a, writes a or writes b, so the exact signed scalar operator (all source,
target and dirty columns) is unchanged; only the event order, the MOVE
partition and a's endpoint change. The scalar hash therefore changes and is
recomputed; the scalar word is replayed column by column by scalar_check.

Each restored helper ends at E with entrance sigma: its five-stage residual is
D_(E - sigma) of rank dim E - dim sigma and the single direction E^perp is
never touched, so it is completed together with the entrance (bank_check
builds the (sigma, E) chart; raw_ledger.rebind_restore recounts). Prepared by
Rohan Arun with Anthropic Claude assistance; Apache-2.0.
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
    cats=producer['physical']['category_names'];cleanup=cats.index('cleanup_gate')
    cut=next(k//6 for k in range(0,len(old),6)if old[k]==1 and old[k+5]==cleanup)
    assert cut==selection['cut_record']
    # Current frames at the cut and the complete later incidence of every stream, from the actual word.
    state=dict(initial);atcut=None;later={};written_after={};copy=None
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if i==cut:atcut=dict(state)
        if op==0:state[a]=c;continue
        if op==2:assert copy is None and i<cut;copy=(a,b,c);state[b]=f;continue
        if op==3:assert copy==(a,b,c) and i<cut;copy=None;del state[b];continue
        if i>=cut:
            assert b!=n
            later.setdefault(a,[]).append(('w',b,i));written_after.setdefault(a,[]).append(i)
            later.setdefault(b,[]).append(('r',a,i))
    assert copy is None and atcut is not None
    final=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    helpers={};donors=set();entries=[]
    for r in selection['entries']:
        i=r['record'];a,b=r['helper'],r['donor']
        op,x,y,c,f,z=old[6*i:6*i+6]
        assert i>cut and op==1 and (x,y)==(a,b) and [a,b,c,z]==r['scalar'] and f==producer['FULL']
        assert 2*v<=a<n and 2*v<=b<n and a not in helpers and b not in donors and a not in donors and b not in helpers
        assert later[a]==[('w',b,i)],('helper has another later incidence',a)
        assert not any(cut<=w<i for w in written_after.get(b,[])),('donor written before the moved gate',b)
        fa,fb=atcut[a],atcut[b];assert C.dimf[fa]==r['helper_dimension'] and C.dimf[fb]==r['donor_dimension']
        E=W.register(C.B[fa]+C.B[fb])
        assert C.dimf[E]==r['end_dimension']==23 and sha_basis(C.B[E])==r['end_basis_sha256'] and C.nondeg(E)
        assert C.sub(fa,E) and C.sub(fb,E) and C.sub(E,producer['FULL']) and final[a]==final[b]==producer['FULL']
        assert C.sub(initial[a],fa) and C.dimf[initial[a]]==r['entrance_dimension']
        helpers[a]=(i,b,c,z,E);donors.add(b);entries.append(dict(record=i,helper=a,donor=b,entrance_frame=initial[a],entrance_dimension=C.dimf[initial[a]],helper_frame_at_cut=fa,donor_frame_at_cut=fb,end_frame=E,end_dimension=C.dimf[E],end_basis_sha256=sha_basis(C.B[E])))
    assert len(helpers)==selection['selected_helper_count']>0 and not(set(helpers)&donors)
    # Exact integer source spans: the moved gate's frame must contain the span of both operands after the gate.
    columns=[{i:1}if i<v else{}for i in range(n)];center=None;spans={}
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==0:continue
        if op==2:center=a;continue
        if op==3:center=None;continue
        if k//6==cut:
            for h,(i,b2,c2,z2,E) in helpers.items():
                ca=dict(columns[h])
                for s,x in columns[b2].items():
                    y=ca.get(s,0)+c2*x
                    if y:ca[s]=y
                    else:del ca[s]
                spans[h]=sorted(set(ca)|set(columns[b2]))
        source=center if b==n else b;ca=columns[a]
        for s,x in columns[source].items():
            y=ca.get(s,0)+c*x
            if y:ca[s]=y
            else:del ca[s]
    for h,(i,b,c,z,E) in helpers.items():
        for s in spans[h]:assert all(W.module.dot(x,C.chi[s])==0 for x in C.A[E]),('restoration frame omits operand source span',h,s)
    moved={i for i,b,c,z,E in helpers.values()}
    state=dict(initial);out=array('i');copy=None;emitted=0
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('restoration frame nesting',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0
        out.extend((0,s,before,f,gap,0));state[s]=f
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==0:continue
        if i==cut:
            for h,(j,b2,c2,z2,E) in sorted(helpers.items(),key=lambda x:x[1][0]):
                move(h,E);move(b2,E);out.extend((1,h,b2,c2,E,z2));emitted+=1
        if i in moved:continue
        if op==1:
            if copy is not None:assert a!=copy[0] and b!=copy[0]
            move(a,f)
            if b==n:assert f==producer['ZERO'] and copy is not None
            else:move(b,f)
            out.extend((op,a,b,c,f,z))
        elif op==2:
            assert copy is None and b==n;move(a,c);state[b]=f;copy=(a,b,c);out.extend((op,a,b,c,f,z))
        else:
            assert op==3 and copy==(a,b,c) and state[a]==c and state[b]==f
            out.extend((op,a,b,c,f,z));del state[b];copy=None
    assert copy is None and emitted==len(helpers)
    for h,(i,b,c,z,E) in helpers.items():final[h]=E
    for s in sorted(final):move(s,final[s])
    assert state==final
    def projection(a):
        result=[]
        for k in range(0,len(a),6):
            op,x,y,c,f,z=a[k:k+6]
            if op:result.append((op,x,y,c,z))
        return result
    # The multiset of scalar events is unchanged; only the selected writes moved to the cut.
    po,pn=projection(old),projection(out);assert len(po)==len(pn) and Counter(po)==Counter(pn)
    ecut=sum(1 for k in range(0,6*cut,6)if old[k])
    assert po[:ecut]==pn[:ecut] and [e for e in po[ecut:]if not(e[0]==1 and e[1]in helpers)]==pn[ecut+len(helpers):]
    assert pn[ecut:ecut+len(helpers)]==[(1,h,b,c,z)for h,(i,b,c,z,E)in sorted(helpers.items(),key=lambda x:x[1][0])]
    return out,final,entries,spans,cut

def run(producer,output_dir=None,selection_path=None):
    begun=time.monotonic();W,C=producer['W'],producer['C'];v=W.v;n=len(producer['initial_state'])
    path=Path(selection_path)if selection_path else HERE/'restore-selection.json'
    selection=json.loads(path.read_text());old=producer['records'];oldmeta=producer['physical'];initial=producer['initial_state'];ZERO,FULL=producer['ZERO'],producer['FULL']
    out,final,entries,spans,cut=transform(producer,selection)
    restored={e['helper']:e['end_frame']for e in entries}
    assert all(final[i]==FULL for i in initial if i<v or (i>=2*v and i not in restored))
    assert all(final[h]==E and C.dimf[E]==23 for h,E in restored.items())
    for t in range(v):
        f=final[v+t];assert C.dimf[f]==23 and all(W.module.dot(C.cov[t],b)==0 for b in C.B[f])
    needs={i:[]for i in initial};copies=Counter();copy=None
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
    assert count==oldmeta['weighted_scalar_events']==selection['expected_scalar_additions'] and coeff==dict((int(k),v)for k,v in oldmeta['coefficient_histogram'].items()) and len(centers)==24
    assert cat=={k:v for k,v in oldmeta['categories'].items()}
    delta=Counter(hist);delta.subtract(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}));delta={r:c for r,c in delta.items()if c}
    assert delta=={int(r):c for r,c in selection['expected_local_histogram_delta'].items()},('combined local delta',delta)
    assert sum(r*c for r,c in hist.items())==selection['expected_rank_mass']==oldmeta['paid_rank_mass']-len(restored)
    assert sum(hist.values())==oldmeta['positive_rank_moves']+24+selection['expected_added_calls']
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for i,H in per_role.items():(sourceH if i<v else targetH if i<2*v else internalH).update(H)
    idle={h:24-C.dimf[E]for h,E in restored.items()}
    receipt=dict(status='PASS_EARLY_RESTORATION_AT_THE_CLEANUP_CUT_AND_BOTH_REFLECTED_LEDGERS',restored_helper_count=len(restored),cut_record=cut,remaining_payload_additions=count,local_histogram_delta=delta,added_calls=selection['expected_added_calls'],rank_mass_drop=len(restored),both_reflected_ledgers=True,unchanged_data_input_output_frames=True,unchanged_copy_lifetimes=True,operand_source_spans_contained=True,integer_commutation_checked=True,scalar_event_multiset_unchanged=True,checked_operand_spans=sum(len(s)for s in spans.values()),unique_required_frame_pairs=len(pairs),explicit_reflected_annihilator_pairs=len(pairs),nondegenerate_endpoint_bases=len(nondeg_bases),helper_endpoint_dimension_histogram=dict(Counter(C.dimf[E]for E in restored.values())),completion_idle_histogram=dict(Counter(idle.values())),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),producer_scalar_sha256=oldmeta['scalar_projection_sha256'],scalar_projection_sha256=scalar.hexdigest(),selection_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),entries=entries,seconds=time.monotonic()-begun)
    meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL527_EARLY_RESTORED_EXACT_FRAME_AND_SCALAR_PROJECTION',scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-24,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha_basis(C.B[f]))for f in sorted(used)],helper_endpoint_frames={str(h):E for h,E in sorted(restored.items())},restore_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,restore_census=receipt)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'physical.json').write_text(json.dumps(meta,indent=2)+'\n')
        (p/'restore.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (p/'restore-per-role.json').write_text(json.dumps({s:dict(H)for s,H in per_role.items()},indent=2)+'\n')
        (p/'restore-used-bases.json').write_text(json.dumps({f:dict(basis=C.B[f],annihilator=C.A[f])for f in sorted(used)},separators=(',',':'))+'\n')
    print('PASS early restoration',len(restored),'helpers',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
