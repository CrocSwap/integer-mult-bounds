"""F2 payload identity elision and exact nested address-MOVE fusion.
The inherited signed source decoder is retained as producer evidence.
All odd-prime address projectors and routes remain unchanged.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
p = 10 port (DreamingOfClouds, Anthropic Claude assistance): h, copies and scatter reads from word_pins.shape,
word counts pinned in word-pins.json; the unused-stream census ranges over the actual 2v+R streams.
"""
from array import array
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time
from word_pins import expect,shape
if not __debug__:raise SystemExit('assertions required')

def transform(records, nstreams):
    out = array('i')
    pending = {}
    chains = []
    removed = Counter()
    hist = Counter()
    merged = 0
    maxchain = 0
    uses = Counter()

    def flush(a):
        nonlocal merged, maxchain
        if a in pending:
            old, new, rank, count, first, last = pending.pop(a)
            if rank:
                hist[rank] += 1
            out.extend((0, a, old, new, rank, 0))
            merged += count - 1
            maxchain = max(maxchain, count)
            if count > 1:
                chains.append(dict(stream=a, old=old, new=new, rank=rank, moves=count, first=first, last=last))
    for index in range(0, len(records), 6):
        op, a, b, c, f, z = records[index:index + 6]
        if op == 1 and c % 2 == 0:
            removed[c] += 1
            continue
        if op == 0:
            assert z == 0
            if a in pending:
                old, prev, rank, count, first, last = pending[a]
                assert prev == b, ('disconnected movechain', a, prev, b)
                pending[a] = (old, c, rank + f, count + 1, first, index // 6)
            else:
                pending[a] = (b, c, f, 1, index // 6, index // 6)
            continue
        assert op in (1, 2, 3)
        flush(a)
        flush(b)
        if op == 1:
            uses[a] += 1
            uses[b] += 1
        elif op == 2:
            hist[z] += 1
            uses[a] += 1
            uses[b] += 1
        out.extend((op, a, b, c, f, z))
    for a in sorted(pending):
        flush(a)
    return (out, dict(removed_even_adds=dict(removed), removed_even_add_count=sum(removed.values()), merged_move_count=merged, max_chain=maxchain, fused_chains=len(chains), paid_histogram=dict(sorted(hist.items())), paid_calls=sum(hist.values()), paid_rank_mass=sum((r * n for r, n in hist.items())), surviving_additions=sum((out[k] == 1 for k in range(0, len(out), 6))), output_records=len(out) // 6, unused_streams=[i for i in range(nstreams) if not uses[i]], stream_use_counts=dict(uses)), chains)

def run(producer,output_dir=None):
    begun=time.monotonic();W,C=producer['W'],producer['C'];v=W.v;S=shape();h=W.h;assert h==S['h'] and v==S['v'];n=2*v+len(producer['context']['regs'])
    old=producer['records'];out,stats,chains=transform(old,n);oldmeta=producer['physical']
    expect('removed_even_adds',stats['removed_even_add_count']);expect('surviving_additions',stats['surviving_additions'])
    expect('local_paid_rank_mass',stats['paid_rank_mass']);assert stats['merged_move_count']==0
    initial=producer['initial_state'];ZERO,FULL=producer['ZERO'],producer['FULL']
    # Independent required-frame census: ignore all original MOVE instructions.
    # Use only surviving gate operands, copy sources and mathematical endpoints.
    needs={i:[] for i in initial};copies=Counter();copy=None
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6]
        if op==1 and c%2:
            needs[a].append(f)
            if b!=n:needs[b].append(f)
            else:assert copy is not None
        elif op==2:
            assert copy is None;copy=(a,b,c);needs[a].append(c);copies[z]+=1
        elif op==3:assert copy==(a,b,c);copy=None
    assert copy is None and copies=={S['center_rank']:S['centers']}
    final={i:FULL for i in initial}
    for t in range(v):final[v+t]=W.register(W.module.kernel([C.cov[t]],W.h)[0])
    census=Counter(copies);per_role={};pairs=set()
    for i,oldf in initial.items():
        H=Counter()
        for f in needs[i]+[final[i]]:
            assert C.sub(oldf,f);rank=C.dimf[f]-C.dimf[oldf]
            if rank:H[rank]+=1
            pairs.add((oldf,f));oldf=f
        per_role[i]=H;census.update(H)
    assert census==Counter({int(r):c for r,c in stats['paid_histogram'].items()})
    # Read back the actual annihilator rows as a separate reflected ledger.
    # A(new) annihilating B(old) states new^perp <= old^perp exactly.
    reflected_pairs=0;endpoint_frames={f for pair in pairs for f in pair};nondeg_bases=set()
    for f in endpoint_frames:
        assert len(C.B[f])==C.dimf[f] and len(C.A[f])+C.dimf[f]==h
        key=tuple(map(tuple,C.B[f]))
        if key not in nondeg_bases:
            assert C.nondeg(f),'singular required endpoint frame'
            nondeg_bases.add(key)
    for oldf,newf in sorted(pairs):
        assert len(C.A[newf])<=len(C.A[oldf])
        assert all(W.module.dot(a,b)==0 for a in C.A[newf]for b in C.B[oldf])
        reflected_pairs+=1
    # Validate the actual transformed instruction stream against its own frames.
    state=dict(initial);copy=None;used=set(initial.values());hist=Counter();cat=Counter();coeff=Counter();centers=[];count=0
    scalar=hashlib.sha256();tagged=hashlib.sha256();category_names=oldmeta['category_names']
    def event(d,row):d.update(json.dumps(row,separators=(',',':')).encode());d.update(b'\n')
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==0:
            assert state[a]==b and C.sub(b,c) and C.dimf[c]-C.dimf[b]==f
            # Complement reflection reverses containment and preserves the gap.
            assert (h-C.dimf[b])-(h-C.dimf[c])==f
            state[a]=c;used.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert c%2 and state[a]==state[b]==f and a!=b
            kind=category_names[z];source=copy['source']if b==n else b
            event(scalar,[a,source,c]);event(tagged,[a,b,c,f,kind]);count+=1;cat[kind]+=1;coeff[abs(c)]+=1;used.add(f)
        elif op==2:
            assert copy is None and b==n and state[a]==c and f==ZERO and z==S['center_rank']
            state[b]=f;hist[z]+=1;copy=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and copy is not None and (a,b,c)==(copy['source'],copy['temporary'],copy['frame']) and state[b]==f==ZERO
            copy.update(after_event=count,scatter_reads=count-copy['first_event']);assert copy['scatter_reads']==S['scatter_reads']
            centers.append(copy);copy=None;del state[b]
    assert copy is None and state==final and hist==census
    assert count==expect('surviving_additions',count) and coeff==expect('surviving_coefficients',dict(coeff)) and len(centers)==S['centers']
    delta=Counter(hist);delta.subtract(Counter({int(r):c for r,c in oldmeta['paid_histogram'].items()}));delta={r:c for r,c in delta.items()if c}
    assert delta=={}
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for i,H in per_role.items():(sourceH if i<v else targetH if i<2*v else internalH).update(H)
    receipt=dict(status='PASS_FRESH_PARITY_FUSION_AND_INDEPENDENT_REQUIRED_FRAME_CENSUS',removed_even_add_count=stats['removed_even_add_count'],remaining_payload_additions=count,merged_moves=stats['merged_move_count'],chains=chains,local_histogram_delta=delta,both_reflected_ledgers=True,unchanged_all_input_output_frames=True,unique_required_frame_pairs=len(pairs),explicit_reflected_annihilator_pairs=reflected_pairs,nondegenerate_endpoint_bases=len(nondeg_bases),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),producer_scalar_sha256=oldmeta['scalar_projection_sha256'],producer_tagged_sha256=oldmeta['tagged_scalar_sha256'],transform_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    meta=dict(oldmeta);meta.update(status='PASS_PHYSICAL_P10_PARITY_FUSED_EXACT_FRAME_AND_SCALAR_PROJECTION',scalar_projection_sha256=scalar.hexdigest(),tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-S['centers'],used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=hashlib.sha256(json.dumps(C.B[f],separators=(',',':')).encode()).hexdigest())for f in sorted(used)],parity_transform=receipt,producer_physical_emitter_sha256=oldmeta['physical_emitter_sha256'],physical_emitter_sha256=receipt['transform_sha256'])
    result=dict(producer);result.update(records=out,physical=meta,result=meta,producer_physical=oldmeta,parity_census=receipt)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True)
        (p/'records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'physical.json').write_text(json.dumps(meta,indent=2)+'\n')
        (p/'parity.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS parity fusion',count,'ADDs',len(out)//6,'records',flush=True)
    return result
