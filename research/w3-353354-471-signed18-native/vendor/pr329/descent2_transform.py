"""Second exact frame retiming after the terminal sinks (post-sink concave descent).

The kernel, early-restoration and terminal-sink stages change many frames of the gen5 word, so a second retiming pass
on the final transcript pays again. Selected ADD gates receive new nondegenerate frames: a frame already on one of the
gate's operand chains, the constructed minimal join of its operands' preceding chain frames (with the operand source
span if needed) or the constructed maximal meet of their following chain frames (PR #291's constructed frames), or a
common frame for a connected block of chain-adjacent gates (PR #270's plateau blocks). Rule: greedy descent of the
deficit-fixed concave ledger sum r ln(120/r) (PR #287, rohanarun). This module is PR #287's descent_transform.py with
the endpoint checks generalised to the post-sink word: every register keeps its actual start and end frame (sources and
targets as before, restored helpers keep their early endpoints), the scalar/COPY projection is byte-identical, chains
are nested, COPY lifetimes are unchanged, every retimed gate frame contains the exact integer source span of each
non-target operand (recomputed here from the actual word), every endpoint basis is nondegenerate, both reflected
annihilator ledgers are rebuilt, and the scalar word is replayed over F2 forward and inverse (kernel_transform.replay).
Adapted with Anthropic Claude assistance; Apache-2.0.
"""
from array import array
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time,importlib.util
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent
from word_pins import shape as _shape
_S=_shape();_H=_S['h'];_V=_S['v'];_M=_S['m'];_CR=_S['center_rank'];_NC=_S['centers'];_SCAT=_S['scatter_reads'];_DEF=_S['deficit']

def sha_basis(B):
    return hashlib.sha256(json.dumps([list(r) for r in B],separators=(',',':')).encode()).hexdigest()

def transform(producer,selection):
    W,C=producer['W'],producer['C'];old=producer['records'];initial=dict(producer['initial_state']);v=W.v;n=len(initial)
    assert hashlib.sha256(old.tobytes()).hexdigest()==selection['input_raw_sha256'],'descent2 selection bound to a different word'
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
    # Endpoints: the producer's actual final frames; the old word must end exactly there.
    final=dict(producer['final_state']);replayed=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:replayed[old[k+1]]=old[k+3]
    assert replayed==final,'producer final state differs from the old word'
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
        assert C.sub(before,f),('descent2 frame nesting',s,before,f)
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
    return out,initial,final,changed,spans,hashlib.sha256(projection(out)).hexdigest()

def run(producer,output_dir=None,selection_path=None):
    begun=time.monotonic();W,C=producer['W'],producer['C'];v=W.v
    path=Path(selection_path)if selection_path else HERE/'descent2-selection.json'
    selection=json.loads(path.read_text());old=producer['records'];oldmeta=producer['physical'];ZERO,FULL=producer['ZERO'],producer['FULL']
    out,initial,final,changed,spans,projection=transform(producer,selection);n=len(initial)
    assert all(final[i]==FULL for i in initial if i<v)
    for t in range(v):
        f=final[v+t];assert C.dimf[f]==_H-1 and all(W.module.dot(C.cov[t],b)==0 for b in C.B[f])
    assert all(final[s]==producer['final_state'][s] and initial[s]==producer['initial_state'][s] for s in initial)
    spec=importlib.util.spec_from_file_location('descent2_kernel_replay',HERE/'kernel_transform.py');km=importlib.util.module_from_spec(spec);spec.loader.exec_module(km)
    forward=km.replay(out,n,v);inverse=km.replay(out,n,v,True);before=km.replay(old,n,v)
    assert forward['event_sha256']==before['event_sha256']==oldmeta['scalar_projection_sha256']
    # Census rebuilt only from actual surviving ADD needs, frozen COPY source frames and fixed endpoints.
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
    assert copy is None and copies=={_CR:_NC}
    census=Counter(copies);reflected=Counter(copies);per_role={};pairs=set()
    for s,startframe in initial.items():
        H=Counter();path_=[startframe]+needs[s]+[final[s]]
        for a,b in zip(path_,path_[1:]):
            assert C.sub(a,b);rank=C.dimf[b]-C.dimf[a]
            if rank:H[rank]+=1
            pairs.add((a,b))
        for a,b in zip(reversed(path_),list(reversed(path_))[1:]):
            assert all(not W.module.dot(x,y)for x in C.A[a]for y in C.B[b]);gap=len(C.A[b])-len(C.A[a]);assert gap>=0
            if gap:reflected[gap]+=1
        per_role[s]=H;census.update(H)
    assert reflected==census
    endpoint_frames={f for pair in pairs for f in pair};nondeg_bases=set()
    for f in endpoint_frames:
        assert len(C.B[f])==C.dimf[f] and len(C.A[f])+C.dimf[f]==_H
        key=tuple(map(tuple,C.B[f]))
        if key not in nondeg_bases:assert C.nondeg(f);nondeg_bases.add(key)
    for a,b in pairs:
        assert len(C.A[b])<=len(C.A[a]) and all(W.module.dot(x,y)==0 for x in C.A[b]for y in C.B[a]) and len(C.A[a])-len(C.A[b])==C.dimf[b]-C.dimf[a]
    state=dict(initial);copy=None;used=set(initial.values());hist=Counter();cat=Counter();coeff=Counter();centers=[];count=0
    scalar=hashlib.sha256();tagged=hashlib.sha256();cats=oldmeta['category_names']
    def event(d,row):d.update(json.dumps(row,separators=(',',':')).encode());d.update(b'\n')
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==0:
            assert state[a]==b and C.sub(b,c) and C.dimf[c]-C.dimf[b]==f and (_H-C.dimf[b])-(_H-C.dimf[c])==f
            state[a]=c;used.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert c%2 and state[a]==state[b]==f and a!=b
            count+=1;cat[cats[z]]+=1;coeff[abs(c)]+=1;used.add(f);event(tagged,[a,b,c,f,cats[z]])
        elif op==2:
            assert copy is None and b==n and state[a]==c and f==ZERO and z==_CR
            state[b]=f;hist[z]+=1;copy=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and copy is not None and (a,b,c)==(copy['source'],copy['temporary'],copy['frame']) and state[a]==c and state[b]==f==ZERO
            copy.update(after_event=count,scatter_reads=count-copy['first_event']);assert copy['scatter_reads']==_SCAT
            centers.append(copy);copy=None;del state[b]
    assert copy is None and state==final and hist==census
    assert count==oldmeta['weighted_scalar_events']==selection['expected_scalar_additions'] and coeff==dict((int(k),x)for k,x in oldmeta['coefficient_histogram'].items()) and len(centers)==_NC
    delta=Counter(hist);delta.subtract(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}));delta={r:c for r,c in delta.items()if c}
    assert delta=={int(r):c for r,c in selection['expected_local_histogram_delta'].items()},('combined local delta',delta)
    assert sum(r*c for r,c in hist.items())==oldmeta['paid_rank_mass']==selection['expected_rank_mass']
    removed=sum(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}).values())-sum(hist.values());assert removed==selection['expected_removed_calls']
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for i,H in per_role.items():(sourceH if i<v else targetH if i<2*v else internalH).update(H)
    inherited={row['frame_id'] for row in oldmeta.get('used_frames',[])}
    new_bases=sorted({c_['basis_sha256'] for c_ in changed if c_['new_frame'] not in inherited})
    receipt=dict(status='PASS_POST_SINK_CONCAVE_DESCENT_RETIMING_AND_BOTH_REFLECTED_LEDGERS',selected_gate_count=len(changed),move_types=selection.get('move_types',{}),remaining_payload_additions=count,local_histogram_delta=delta,removed_calls=removed,both_reflected_ledgers=True,unchanged_all_input_output_frames=True,unchanged_helper_endpoints=True,unchanged_copy_lifetimes=True,operand_source_spans_contained=True,checked_operand_spans=sum(len(s)for s in spans.values()),identical_scalar_and_copy_projection_sha256=projection,scalar=dict(forward=forward,inverse=inverse),new_bases=len(new_bases),unique_required_frame_pairs=len(pairs),nondegenerate_endpoint_bases=len(nondeg_bases),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),output_raw_sha256=hashlib.sha256(out.tobytes()).hexdigest(),producer_scalar_sha256=oldmeta['scalar_projection_sha256'],selection_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),changed_gates=changed,seconds=time.monotonic()-begun)
    meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL_GEN5_POST_SINK_DESCENT_RETIMED',tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-_NC,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha_basis(C.B[f]))for f in sorted(used|inherited)],descent2_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,descent2_census=receipt)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'descent2-records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'descent2.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS post-sink descent retiming',len(changed),'gates',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
