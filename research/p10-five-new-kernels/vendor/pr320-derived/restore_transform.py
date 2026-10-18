"""Early helper restoration on the gen5 kernel word (port of PR #280's 440-helper cleanup to this Python pipeline).

Mechanism and selection rule from PR #280 (utcorvusvolat-dotcom, code/cleanup_screen.py, cleanup_emit.py,
docs/cleanup-proof.md) and its endpoint-aware composition in PR #283 (Dugongue, RESTORATION-PROOF.md). At the first
cleanup ADD (the cut) every target already holds its required endpoint. A helper a qualifies when its formal row is
untouched at the cut, its only remaining scalar incidence is a += c*b, b is not written between the cut and that
incidence, and no COPY/ERASE follows the cut. All selected a and b are distinct and disjoint. The shear a += c*b then
commutes over the integers with every crossed scalar gate (no crossed gate reads or writes a, none writes b), so it is
executed at the cut, inside the exact rational join E of the current frames of a and b (dimension 23, nondegenerate
for 9I-J), and a ends at E instead of FULL. The helper's residual projector becomes P_E - P_sigma (rank 3 for a rank-20
entrance sigma); the five-stage completion becomes P_sigma + (I - P_E) and the banks are re-tiled for the actual
residual. The screen is recomputed on the actual input word and must equal the frozen selection.
Checks: integer commutation conditions on the actual suffix; F2 replay of every formal column forward and inverse;
omission control (deleting the moved restorations must fail); every required frame path rebuilt from scalar/COPY
events with both reflected ledgers; all used frames nondegenerate.
Prepared with Anthropic Claude assistance; Apache-2.0.
p = 10 port (Chafik Boukhalfa (chafreaky), Anthropic Claude assistance): h, v, centre copies and scatter reads come
from word_pins.shape and the stage counts are pinned in word-pins.json; the mechanism and checks are unchanged.
"""
from array import array
from collections import Counter
from pathlib import Path
import gzip,hashlib,json,time,sys
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('assertions required')
HERE=Path(__file__).resolve().parent
from word_pins import shape as _shape
_S=_shape();_H=_S['h'];_V=_S['v'];_M=_S['m'];_CR=_S['center_rank'];_NC=_S['centers'];_SCAT=_S['scatter_reads'];_DEF=_S['deficit']
sha=lambda b:hashlib.sha256(b).hexdigest()

def screen(old,initial,n,v,C,W,cats,ZERO,FULL):
    """Fresh PR280 screen on the actual word: returns cut and the qualifying (a,b,i,c) rows."""
    cleanup=cats.index('cleanup_gate')
    cut=next(k//6 for k in range(0,len(old),6)if old[k]==1 and old[k+5]==cleanup)
    rows=[1<<j for j in range(n)]+[0];state=dict(initial);temporary=None
    for k in range(0,6*cut,6):
        op,a,b,c,f,z=old[k:k+6]
        if op==0:state[a]=c
        elif op==1:
            if c%2:rows[a]^=rows[b]
        elif op==2:assert temporary is None;temporary=a;rows[n]=rows[a]
        elif op==3:assert temporary==a;temporary=None;rows[n]=0
    assert temporary is None
    assert all(rows[v+j]==(1<<(v+j))^(1<<j)for j in range(v)),'targets incomplete at the cut'
    affected=set()
    for a,x in enumerate(rows[:n]):
        x^=1<<a
        if v<=a<2*v:x^=1<<(a-v)
        while x:k=(x&-x).bit_length()-1;x&=x-1;affected.add(k)
    inc={};writes={};copies=0
    for k in range(6*cut,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:inc.setdefault(a,[]).append(i);inc.setdefault(b,[]).append(i);writes.setdefault(a,[]).append(i)
        elif op in(2,3):copies+=1
    assert copies==0,'COPY/ERASE after the cut'
    out=[]
    for a in range(2*v,n):
        if a in affected or len(inc.get(a,[]))!=1:continue
        i=inc[a][0];op,x,b,c,f,z=old[6*i:6*i+6]
        if x!=a or any(cut<=w<i for w in writes.get(b,[])):continue
        if C.dimf[initial[a]]>=_H:continue
        out.append((a,b,i,c,state[a],state[b]))
    return cut,out,state

def transform(producer,selection):
    W,C=producer['W'],producer['C'];old=producer['records'];initial=dict(producer['initial_state']);context=producer['context'];v=W.v;n=2*v+len(context['regs']);ZERO=producer['ZERO'];FULL=producer['FULL']
    assert n==selection['n'] and v==selection['v']
    assert sha(old.tobytes())==selection['input_raw_sha256'],'restoration selection bound to a different word'
    assert producer['physical']['scalar_projection_sha256']==selection['input_scalar_sha256']
    cats=list(producer['physical']['category_names']);assert 'early_restore' not in cats
    restorecat=len(cats);cats+=['early_restore']
    final=dict(initial)
    for k in range(0,len(old),6):
        if old[k]==0:final[old[k+1]]=old[k+3]
    cut,rows,state=screen(old,initial,n,v,C,W,cats,ZERO,FULL)
    # Keep the screened rows whose exact join is a proper nondegenerate frame; compare with the frozen selection.
    chosen={}
    for a,b,i,c,fa,fb in rows:
        E=W.register([list(x)for x in C.B[fa]]+[list(x)for x in C.B[fb]])
        if C.dimf[E]==_H or not C.nondeg(E):continue
        chosen[a]=dict(helper=a,donor=b,record=i,coefficient=c,frame=E,rank=C.dimf[E],helper_frame=fa,donor_frame=fb,entrance=initial[a])
    frozen={e['helper']:e for e in selection['entries']};assert len(frozen)==len(selection['entries'])==selection['selected']
    assert set(chosen)==set(frozen),'fresh screen differs from the frozen selection'
    for a,e in chosen.items():
        s=frozen[a];assert (s['donor'],s['coefficient'],s['rank'])==(e['donor'],e['coefficient'],e['rank'])
        assert [old[6*e['record']+j]for j in(1,2,3)]==s['incidence'],'incidence content differs'
        assert e['frame']==W.register(s['basis']),'frozen join basis differs'
        assert (C.dimf[e['entrance']],C.dimf[e['helper_frame']],C.dimf[e['donor_frame']],e['rank'])==tuple(s['dims'])
        assert C.sub(e['entrance'],e['helper_frame'])and C.sub(e['helper_frame'],e['frame'])and C.sub(e['donor_frame'],e['frame'])
        assert final[a]==FULL and C.dimf[e['entrance']]<e['rank']
    helpers=set(chosen);donors={e['donor']for e in chosen.values()}
    assert len(donors)==len(chosen) and not(helpers&donors),'helpers and donors must be distinct and disjoint'
    # Integer commutation contract on the crossed interval of each moved shear a += c*b.
    moved={e['record']:e for e in chosen.values()};donorrecord={e['donor']:e['record']for e in chosen.values()};crossed=0;import bisect;records=sorted(moved)
    for k in range(6*cut,len(old),6):
        op,x,y,c,f,z=old[k:k+6];i=k//6
        if op!=1 or i in moved:continue
        assert x not in helpers and y not in helpers,'crossed gate touches a moved helper'
        assert not(x in donorrecord and i<donorrecord[x]),'crossed gate writes a moved donor'
        crossed+=len(records)-bisect.bisect_right(records,i)
    state=dict(initial);out=array('i');temporary=None
    def move(s,f):
        before=state[s]
        if before==f:return
        assert C.sub(before,f),('restoration nonnested actual use',s,before,f)
        gap=C.dimf[f]-C.dimf[before];assert gap>=0;out.extend((0,s,before,f,gap,0));state[s]=f
    def add(a,b,c,f,z):move(a,f);move(b,f);out.extend((1,a,b,c,f,z))
    order=sorted(chosen.values(),key=lambda e:e['helper'])
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if i==cut:
            assert temporary is None
            for e in order:add(e['helper'],e['donor'],e['coefficient'],e['frame'],restorecat)
        if op==1:
            if i in moved:continue
            add(a,b,c,f,z)
        elif op==2:assert temporary is None;move(a,c);state[b]=f;temporary=(a,b,c);out.extend((op,a,b,c,f,z))
        elif op==3:assert temporary==(a,b,c)and state[a]==c and state[b]==f;out.extend((op,a,b,c,f,z));del state[b];temporary=None
    assert temporary is None
    for e in order:final[e['helper']]=e['frame']
    for s in sorted(final):move(s,final[s])
    assert state==final
    project=lambda aa:[tuple(aa[k+j]for j in(0,1,2,3,5))for k in range(0,len(aa),6)if aa[k]]
    expected=[]
    for k in range(0,len(old),6):
        i=k//6
        if i==cut:expected.extend((1,e['helper'],e['donor'],e['coefficient'],restorecat)for e in order)
        if old[k] and i not in moved:expected.append(tuple(old[k+j]for j in(0,1,2,3,5)))
    assert project(out)==expected,'only the documented reordering'
    proof=dict(selected=len(order),cut=cut,crossed_gate_checks=crossed,dims=dict(Counter((C.dimf[e['entrance']],C.dimf[e['helper_frame']],C.dimf[e['donor_frame']],e['rank'])for e in order).most_common()).__repr__(),
        helpers_and_donors_disjoint=True,single_remaining_incidence=True,donor_unwritten_on_crossed_interval=True,no_copy_after_cut=True,targets_complete_at_cut=True,
        endpoint_rank_saving=sum(_H-e['rank']for e in order),residual_histogram=dict(Counter(e['rank']-C.dimf[e['entrance']]for e in order)))
    return out,initial,final,order,cats,proof,n,v

def run(producer,output_dir=None,selection_path=None):
    start=time.monotonic();kt=__import__('importlib').util
    spec=kt.spec_from_file_location('restore_kernel_replay',HERE/'kernel_transform.py');km=kt.module_from_spec(spec);spec.loader.exec_module(km)
    W,C=producer['W'],producer['C'];path=Path(selection_path)if selection_path else HERE/'restore-selection.json';selection=json.loads(path.read_text())
    out,initial,final,entries,cats,proof,n,v=transform(producer,selection);ZERO=producer['ZERO'];FULL=producer['FULL']
    forward=km.replay(out,n,v);inverse=km.replay(out,n,v,True);controls=[km.replay(out,n,v,omit_category=cats.index('early_restore'))]
    needs={s:[]for s in initial};copies=Counter();temporary=None
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==1:
            needs[a].append(f)
            if b!=n:needs[b].append(f)
            else:assert temporary is not None and f==ZERO
        elif op==2:assert temporary is None;temporary=(a,b,c);needs[a].append(c);copies[z]+=1
        elif op==3:assert temporary==(a,b,c);temporary=None
    assert temporary is None and copies=={_CR:_NC}
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
    for f in {x for pair in pairs for x in pair}:assert C.nondeg(f)and len(C.B[f])+len(C.A[f])==_H
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
            assert temporary is None and b==n and state[a]==c and f==ZERO and z==_CR
            state[b]=f;hist[z]+=1;temporary=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and temporary is not None and (a,b,c)==(temporary['source'],temporary['temporary'],temporary['frame'])and state[a]==c and state[b]==f==ZERO
            temporary.update(after_event=count,scatter_reads=count-temporary['first_event']);assert temporary['scatter_reads']==_SCAT;centers.append(temporary);temporary=None;del state[b]
    assert state==final and temporary is None and hist==census and len(centers)==_NC
    old=Counter({int(r):c for r,c in producer['physical']['paid_histogram'].items()});delta=Counter(hist);delta.subtract(old);delta={r:c for r,c in delta.items()if c}
    assert delta=={int(k):v for k,v in selection['expected_local_delta'].items()}
    assert count==producer['physical']['weighted_scalar_events'] and sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass']-proof['endpoint_rank_saving']
    inherited=set()
    for inventory in (producer['physical'],producer.get('producer_physical')):
        if isinstance(inventory,dict):inherited.update(row['frame_id']for row in inventory.get('used_frames',[]))
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    endpoints={e['helper']:e['frame']for e in entries}
    receipt=dict(status='PASS_GEN5_EARLY_RESTORATION_ON_ACTUAL_WORD_AND_BOTH_REFLECTED_LEDGERS',proof=proof,scalar=dict(forward=forward,inverse=inverse,controls=controls),selected=len(entries),endpoint_rank_saving=proof['endpoint_rank_saving'],local_histogram_delta=delta,unchanged_data_input_output_frames=True,changed_helper_endpoints=len(endpoints),unchanged_copy_lifetimes=True,both_reflected_ledgers=True,unique_required_frame_pairs=len(pairs),source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies),input_raw_sha256=sha(producer['records'].tobytes()),output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(path.read_bytes()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL_GEN5_EARLY_RESTORATION',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-_NC,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used|inherited)],restore_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    ctx=dict(producer['context']);ctx['restored_endpoints']={ctx['regs'][a-2*v]:f for a,f in endpoints.items()}
    result=dict(producer);result.update(context=ctx,records=out,physical=meta,result=meta,restore_census=receipt,initial_state=initial,final_state=final,helper_endpoints=endpoints,restore_entries=entries)
    if output_dir is not None:
        p=Path(output_dir);p.mkdir(parents=True,exist_ok=True);(p/'restore-records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0))
        (p/'restore.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS early restoration',len(entries),'helpers endpoint saving',proof['endpoint_rank_saving'],count,'scalar ADDs',sum(hist.values()),'paid calls',len(out)//6,'records',flush=True)
    return result
