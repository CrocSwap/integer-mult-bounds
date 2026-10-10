"""Source-bound retimed direct sinks and shortened early terminal caches.

A freshly verified dependent read whose prior frame lies in U permits distributive retiming:
x+=c; y+=x becomes y+=x_old at U; y+=c at recovery, and x+=c is
deferred until after a direct pivot feed at the last centre ERASE. Such a
terminal helper is removed and surviving registers are compacted. The fallback
is the shortened-cache route below.

For a terminal helper r with one early write r+=x at U, x later changes only
by x+=c before the last centre ERASE. Preserve r's initial dirty reads and
its early write. After the ERASE, set up target differences, add r into the
pivot at U, then restore r by r-=x; r+=c at the actual common recovery frame.
Redirect later terminal writes into the pivot and scatter at the root frame.
The helper survives, ending at the recovery frame; every data endpoint stays
unchanged. Every selection is rederived from the actual input stream, including
all scalar/COPY incidences and operand lifetimes. No inherited index is reused.
Adapted from credited PR283 terminal-sink mechanics, with OpenAI Codex assistance.
"""
from array import array
from collections import Counter,defaultdict
from pathlib import Path
import gzip,hashlib,json,time,sys,importlib.util
sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('Assertions required')
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
NAMES=['hybrid_setup','hybrid_feed','hybrid_restore_source','hybrid_restore_correction','hybrid_redirect','hybrid_scatter','hybrid_split_read','hybrid_deferred_update']

def cache_screen(producer):
    W,C=producer['W'],producer['C'];v=W.v;old=producer['records'];regs=producer['context']['regs'];n=2*v+len(regs);initial=producer['initial_state'];final=producer['final_state'];Z=producer['ZERO'];F=producer['FULL'];cats=producer['physical']['category_names']
    READ,ROOT,FWD,CLN=map(cats.index,['dirty_read','side_root','forward_gate','cleanup_gate'])
    entry=max(k//6 for k in range(0,len(old),6)if old[k]==3);inc=defaultdict(list);writes=defaultdict(list);twrites=defaultdict(list);treads=set();copied=set();state=dict(initial);at_entry=None
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==0:assert state[a]==b;state[a]=c
        elif op==1:
            inc[a].append(i);writes[a].append(i)
            if b!=n:inc[b].append(i)
            if v<=b<2*v:treads.add(b)
            if v<=a<2*v:twrites[a].append(i)
        elif op in(2,3):inc[a].append(i);copied.add(a)
        if i==entry:at_entry=dict(state)
    assert state==final and at_entry is not None
    rows=[]
    for r in range(2*v,n):
        if initial[r]!=Z or final[r]!=F or r in copied:continue
        pre=Counter();post=Counter();fwd=[];cleanup=[];deliveries=[];rootframes=set();bad=False;read_indices=[]
        for i in inc[r]:
            op,a,b,c,f,z=old[6*i:6*i+6]
            if op!=1:bad=True;break
            if b==r:
                if not(v<=a<2*v):bad=True;break
                if z==READ and f==Z and c==-1 and i<entry:pre[a]+=1;read_indices.append(i)
                elif z==ROOT and c==1:post[a]+=1;rootframes.add(f);deliveries.append(i)
                else:bad=True;break
            elif a==r:
                if z==FWD and c==1:fwd.append(i)
                elif z==CLN and c==-1:cleanup.append(i)
                else:bad=True;break
        if bad or not pre or len(rootframes)!=1 or set(pre)!=set(post)or any(pre[t]!=1 or post[t]!=1 for t in pre):continue
        early=[i for i in fwd if i<=entry]
        if len(early)!=1 or len(fwd)<2:continue
        early=early[0];last=max(fwd);S=set(pre)
        if max(read_indices)>=early or min(deliveries)<=last or (cleanup and min(cleanup)<=max(deliveries)):continue
        if S&treads or S&copied:continue
        pivots=[p for p in sorted(S)if at_entry[p]==Z and not[i for i in twrites[p]if entry<i<=last and old[6*i+2]!=r]]
        if not pivots:continue
        _,_,source,coeff,early_frame,_=old[6*early:6*early+6]
        if source<n and source>=2*v and source not in copied:pass
        else:continue
        sw=[i for i in writes[source]if early<i<=entry]
        if len(sw)!=1:continue
        update=sw[0];_,_,correction,sgn,recovery,_=old[6*update:6*update+6]
        if sgn!=1 or not 2*v<=correction<n or correction in copied or correction in(S|{r,source}):continue
        if any(update<i<=entry for i in writes[correction]):continue
        if at_entry[source]!=recovery or at_entry[correction]!=recovery or not C.sub(early_frame,recovery):continue
        if C.dimf[recovery]not in(5,6)or not C.nondeg(recovery):continue
        pivot=pivots[0];path=[Z,early_frame]+[old[6*i+4]for i in fwd if i!=early]+[next(iter(rootframes)),final[pivot]]
        if not all(C.sub(a,b)for a,b in zip(path,path[1:])):continue
        if any(old[6*i+2]in S or old[6*i+2]==r for i in fwd):continue
        rows.append(dict(role=regs[r-2*v],stream=r,targets=sorted(S),pivot=pivot,early=early,last=last,writes=fwd,cleanups=cleanup,deliveries=deliveries,dirty_reads=read_indices,root_frame=next(iter(rootframes)),early_frame=early_frame,source=source,source_update=update,correction=correction,recovery_frame=recovery,recovery_rank=C.dimf[recovery],entry=entry,source_writes_on_interval=sw,correction_writes_after_update=[]))
    used=set()
    for r in rows:assert not used.intersection(r['targets']);used.update(r['targets'])
    assert not {r['stream']for r in rows}&{s for r in rows for s in(r['source'],r['correction'])}
    return entry,rows


def screen(producer):
    entry,rows=cache_screen(producer);old=producer['records'];v=producer['W'].v;n=2*v+len(producer['context']['regs']);C=producer['C'];Z=producer['ZERO']
    # Actual last scalar/COPY use determines the reconstructed monotone frame;
    # obsolete input MOVEs are not implicit obligations in the new program.
    prior=dict(producer['initial_state']);before={};inc=defaultdict(list)
    candidates={r['source']for r in rows}
    for k in range(0,6*(entry+1),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:
            if b in candidates:before[i]=prior[a]
            if a in candidates:inc[a].append(i)
            if b in candidates:inc[b].append(i)
            prior[a]=f
            if b!=n:prior[b]=f
        elif op in(2,3):prior[a]=c
    for r in rows:
        uses=[i for i in inc[r['source']]if r['early']<i<=entry]
        reads=[i for i in uses if old[6*i+2]==r['source']]
        r['direct']=False
        if len(uses)!=2 or len(reads)!=1 or r['source_update']not in uses:continue
        i=reads[0];op,a,b,c,f,z=old[6*i:6*i+6]
        if not r['source_update']<i or c!=1 or f!=r['recovery_frame']or a in{r['stream'],r['correction'],r['source']}or not 2*v<=a<n:continue
        if not C.sub(before[i],r['early_frame']):continue
        # Exact prior-use frame containment also covers compatible kernel entrances.
        r.update(direct=True,split_read=i,split_destination=a,split_prior_frame=before[i])
    direct=[r for r in rows if r['direct']];changed={r['source']for r in direct}
    assert len(changed)==len(direct)
    assert not changed & {r['correction']for r in rows}
    assert not changed & {r['split_destination']for r in direct}
    return entry,rows

def selection(producer):
    entry,rows=screen(producer)
    return dict(status='FRESH_SOURCE_BOUND_EARLY_HYBRID_SCREEN',n=2*producer['W'].v+len(producer['context']['regs']),v=producer['W'].v,input_raw_sha256=sha(producer['records'].tobytes()),input_scalar_sha256=producer['physical']['scalar_projection_sha256'],entry=entry,selected=len(rows),entries=rows)

def transform(producer,selected):
    assert selected==selection(producer),'Fresh hybrid screen differs from selection'
    W,C=producer['W'],producer['C'];v=W.v;oldn=selected['n'];old=producer['records'];rows=selected['entries'];assert rows
    removed={r['stream']for r in rows if r['direct']};mp={s:i for i,s in enumerate(s for s in range(oldn)if s not in removed)};n=len(mp);mp[oldn]=n
    initial={mp[s]:f for s,f in producer['initial_state'].items()if s not in removed};final={mp[s]:f for s,f in producer['final_state'].items()if s not in removed}
    cats=list(producer['physical']['category_names']);assert not set(NAMES)&set(cats);SET,FEED,RS,RC,REDIR,SCAT,SPLIT,DEFER=range(len(cats),len(cats)+8);cats+=NAMES
    sinks={r['stream']:r for r in rows};redirect={i:r for r in rows for i in r['writes']if i!=r['early']};drop={i for r in rows for i in r['cleanups']+r['deliveries']};last={r['last']:r for r in rows};state=dict(initial);out=array('i');temporary=None
    direct=[r for r in rows if r['direct']];defer={r['source_update']:r for r in direct};split={r['split_read']:r for r in direct};drop.update(i for r in direct for i in r['dirty_reads']+[r['early']])
    def move(s,f):
        s=mp[s];before=state[s]
        if before!=f:assert C.sub(before,f),('hybrid nonnested use',s,before,f);out.extend((0,s,before,f,C.dimf[f]-C.dimf[before],0));state[s]=f
    def add(a,b,c,f,z):
        move(a,f)
        if b!=oldn:move(b,f)
        else:assert temporary is not None
        out.extend((1,mp[a],mp[b],c,f,z))
    for k in range(0,len(old),6):
        op,a,b,c,f,z=old[k:k+6];i=k//6
        if op==1:
            if i in drop or i in defer:pass
            elif i in split:
                r=split[i];assert state[mp[a]]==r['split_prior_frame']and C.sub(state[mp[a]],r['early_frame'])and state[mp[b]]==r['early_frame']
                add(a,b,c,r['early_frame'],SPLIT);add(a,r['correction'],c,f,SPLIT)
            elif i in redirect:add(redirect[i]['pivot'],b,c,f,REDIR)
            else:add(a,b,c,f,z)
        elif op==2:assert temporary is None and a not in sinks;move(a,c);state[n]=f;temporary=(a,b,c);out.extend((op,mp[a],n,c,f,z))
        elif op==3:assert temporary==(a,b,c)and state[mp[a]]==c and state[n]==f;out.extend((op,mp[a],n,c,f,z));del state[n];temporary=None
        if i==selected['entry']:
            assert temporary is None
            for r in rows:
                for t in r['targets']:
                    if t!=r['pivot']:add(t,r['pivot'],-1,producer['ZERO'],SET)
            for r in rows:
                s=r['stream']
                if r['direct']:
                    assert state[mp[r['source']]]==r['early_frame'];add(r['pivot'],r['source'],1,r['early_frame'],FEED)
                else:
                    assert state[mp[s]]==r['early_frame'];add(r['pivot'],s,1,r['early_frame'],FEED)
                    add(s,r['source'],-1,r['recovery_frame'],RS);add(s,r['correction'],1,r['recovery_frame'],RC)
            for r in direct:add(r['source'],r['correction'],1,r['recovery_frame'],DEFER)
        if i in last:
            r=last[i]
            for t in r['targets']:
                if t!=r['pivot']:add(t,r['pivot'],1,r['root_frame'],SCAT)
    assert temporary is None
    for r in rows:
        if not r['direct']:final[mp[r['stream']]]=r['recovery_frame']
    for s in range(oldn):
        if s not in removed:move(s,final[mp[s]])
    assert state==final and all(initial[s]==producer['initial_state'][s]and final[s]==producer['final_state'][s]for s in range(2*v))
    assert [(op,mp[a],mp[b],c,f,z)for k in range(0,len(old),6)for op,a,b,c,f,z in[old[k:k+6]]if op in(2,3)]==[tuple(out[k:k+6])for k in range(0,len(out),6)if out[k]in(2,3)]
    return out,initial,final,rows,cats,n,v,mp,removed

def packed_replay(records,n,reverse,bits,input_indices=None):
    values=[1<<(bits*i)for i in (input_indices if input_indices is not None else range(n+1))];temporary=None
    for k in(range(len(records)-6,-1,-6)if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:
            assert b!=n or temporary is not None
            values[a]+=(-c if reverse else c)*values[b]
        elif op==(3 if reverse else 2):assert temporary is None;temporary=a;values[n]=values[a]
        elif op==(2 if reverse else 3):assert temporary==a and values[n]==values[a];temporary=None
    assert temporary is None;return values[:n]

def norm_bound(records,n,reverse):
    values=[1]*(n+1);largest=1
    for k in(range(len(records)-6,-1,-6)if reverse else range(0,len(records),6)):
        op,a,b,c,f,z=records[k:k+6]
        if op==1:values[a]+=abs(c)*values[b];largest=max(largest,values[a])
        elif op==(3 if reverse else 2):values[n]=values[a]
    return largest

def source_span_audit(records,n,v,C):
    columns=[{i:1}if i<v else {}for i in range(n)];center=None;checked=set();gates=0;dots=0
    for k in range(0,len(records),6):
        op,a,b,c,f,z=records[k:k+6]
        if op==0:continue
        if op==2:assert center is None;center=a;continue
        if op==3:assert center==a;center=None;continue
        source=center if b==n else b;assert source is not None;ca=columns[a]
        for source_index,value in columns[source].items():
            updated=ca.get(source_index,0)+c*value
            if updated:ca[source_index]=updated
            else:ca.pop(source_index,None)
        need=set()
        if not(v<=a<2*v):need.update(ca)
        if b!=n and not(v<=b<2*v):need.update(columns[b])
        for source_index in need:
            if(f,source_index)not in checked:
                for annihilator in C.A[f]:
                    assert sum(x*y for x,y in zip(annihilator,C.chi[source_index]))==0,('cache actual operand source span',k//6,a,b,f,source_index)
                    dots+=1
                checked.add((f,source_index))
        gates+=1
    assert center is None
    return dict(status='PASS_ALL_ACTUAL_INTEGER_OPERAND_SOURCE_SPANS',scalar_gates=gates,distinct_frame_source_pairs=len(checked),exact_annihilator_dots=dots)

def run(producer,output_dir=None,selection_path=None,kernel_path=None):
    start=time.monotonic();spec=importlib.util.spec_from_file_location('cache_kernel_replay',Path(kernel_path)if kernel_path else HERE/'kernel_transform.py');km=importlib.util.module_from_spec(spec);spec.loader.exec_module(km)
    sel=json.loads(Path(selection_path).read_text())if selection_path else selection(producer);out,initial,final,rows,cats,n,v,mp,removed=transform(producer,sel);oldn=sel['n'];W,C=producer['W'],producer['C'];ZERO=producer['ZERO']
    spans=source_span_audit(out,n,v,C)
    forward=km.replay(out,n,v);inverse=km.replay(out,n,v,True);controls={name:{str(rev):km.replay(out,n,v,rev,cats.index(name))for rev in(False,True)}for name in NAMES}
    bounds={f'{word}_{rev}':norm_bound(records,oldn if word=='input'else n,rev)for word,records in [('input',producer['records']),('output',out)]for rev in(False,True)};bits=max(bounds.values()).bit_length()+2;assert 2*max(bounds.values())<2**bits
    for rev in(False,True):
        want=packed_replay(producer['records'],oldn,rev,bits);surviving=[s for s in range(oldn)if s not in removed];got=packed_replay(out,n,rev,bits,surviving+[oldn])
        assert [want[s]for s in surviving]==got,'Signed surviving all-column operator differs'
        assert all(want[s]==1<<(bits*s)for s in removed),'Deleted helper is not restored dirty'
    needs={s:[]for s in initial};copies=Counter();state=dict(initial);hist=Counter();cat=Counter();coeff=Counter();used=set(initial.values());temporary=None;centers=[];count=0;tagged=hashlib.sha256()
    for k in range(0,len(out),6):
        op,a,b,c,f,z=out[k:k+6]
        if op==0:
            assert state[a]==b and C.sub(b,c)and C.dimf[c]-C.dimf[b]==f and len(C.A[b])-len(C.A[c])==f;state[a]=c;used.update((b,c))
            if f:hist[f]+=1
        elif op==1:
            assert state[a]==state[b]==f and a!=b and a!=n and c%2
            if temporary:assert a!=temporary['source']
            needs[a].append(f)
            if b!=n:needs[b].append(f)
            else:assert temporary is not None and f==ZERO
            count+=1;cat[cats[z]]+=1;coeff[abs(c)]+=1;used.add(f);tagged.update(json.dumps([a,b,c,f,cats[z]],separators=(',',':')).encode()+b'\n')
        elif op==2:
            assert temporary is None and b==n and state[a]==c and f==ZERO and z==W.h-2;state[b]=f;hist[z]+=1;copies[z]+=1;needs[a].append(c);temporary=dict(source=a,frame=c,rank=z,temporary=b,first_event=count,copy_output_frame=f)
        else:
            assert op==3 and temporary is not None and(a,b,c)==(temporary['source'],temporary['temporary'],temporary['frame'])and state[a]==c and state[b]==f==ZERO
            temporary.update(after_event=count,scatter_reads=count-temporary['first_event']);assert temporary['scatter_reads']==3*v//W.h;centers.append(temporary);temporary=None;del state[b]
    assert state==final and temporary is None and copies=={W.h-2:W.h}
    census=Counter(copies);reflected=Counter(copies);per_role={};pairs=set()
    for s in initial:
        path=[initial[s]]+needs[s]+[final[s]];H=Counter()
        for a,b in zip(path,path[1:]):
            assert C.sub(a,b);gap=C.dimf[b]-C.dimf[a];pairs.add((a,b))
            if gap:H[gap]+=1
        for a,b in zip(path[::-1],path[::-1][1:]):
            assert all(sum(x*y for x,y in zip(aa,bb))==0 for aa in C.A[a]for bb in C.B[b]);gap=len(C.A[b])-len(C.A[a]);assert gap>=0
            if gap:reflected[gap]+=1
        per_role[s]=H;census.update(H)
    assert reflected==census==hist
    for f in used:assert C.nondeg(f)and len(C.A[f])+len(C.B[f])==W.h and all(sum(x*y for x,y in zip(a,b))==0 for a in C.A[f]for b in C.B[f])
    before=Counter({int(k):v for k,v in producer['physical']['paid_histogram'].items()});delta=Counter(hist);delta.subtract(before);delta={k:v for k,v in delta.items()if v};saving=sum(W.h if r['direct']else W.h-r['recovery_rank']for r in rows)
    assert sum(r*c for r,c in hist.items())==producer['physical']['paid_rank_mass']-saving
    receipt=dict(status='PASS_SOURCE_BOUND_HYBRID_ALL_COLUMN_F2_Z_BOTH_REFLECTED_LEDGERS',selected=len(rows),direct_sinks=len(removed),shortened_caches=len(rows)-len(removed),removed_roles=[producer['context']['regs'][s-2*v]for s in sorted(removed)],rows=rows,operand_source_spans=spans,scope='Fresh source-bound scalar/COPY transformation with all actual operand source spans and exact local reflected ledgers. Changed-projector charts, all finite-prime minors, bank allocation, selector/invoice and full native assembly remain mandatory before any kappa claim.',scalar=dict(forward=forward,inverse=inverse,controls=controls,signed_all_columns=oldn,survivors_use_original_column_positions=True,removed_inputs_vanish_from_survivors=True,removed_outputs_restore_original_dirt=True,original_to_compacted_register_map_sha256=sha(json.dumps(mp,sort_keys=True,separators=(',',':')).encode()),signed_both_orientations=True,signed_packing_bits=bits,signed_prefix_bounds=bounds),endpoint_rank_saving=saving,local_histogram_delta=delta,unchanged_data_input_output_frames=True,unchanged_copy_lifetimes=True,both_reflected_ledgers=True,physical_R=n-2*v,unique_required_frame_pairs=len(pairs),input_raw_sha256=sel['input_raw_sha256'],output_raw_sha256=sha(out.tobytes()),selection_sha256=sha(json.dumps(sel,sort_keys=True,separators=(',',':')).encode()),transform_sha256=sha(Path(__file__).read_bytes()),seconds=time.monotonic()-start)
    inherited={f['frame_id']for inventory in [producer['physical'],producer.get('producer_physical',{})]if isinstance(inventory,dict)for f in inventory.get('used_frames',[])}
    sourceH=Counter();targetH=Counter();internalH=Counter(copies)
    for s,H in per_role.items():(sourceH if s<v else targetH if s<2*v else internalH).update(H)
    receipt.update(source_histogram=dict(sourceH),target_histogram=dict(targetH),internal_histogram_including_copies=dict(internalH),copied_center_histogram=dict(copies))
    meta=dict(producer['physical']);meta.update(status='PASS_PHYSICAL_EARLY_HYBRID',scalar_projection_sha256=forward['event_sha256'],tagged_scalar_sha256=tagged.hexdigest(),weighted_scalar_events=count,coefficient_histogram=dict(coeff),categories=dict(cat),category_names=cats,copied_center_blocks=centers,paid_histogram=dict(sorted(hist.items())),paid_rank_mass=sum(r*c for r,c in hist.items()),positive_rank_moves=sum(hist.values())-W.h,independent_dirty_registers=n-2*v,physical_registers=n,used_frames=[dict(frame_id=f,dimension=C.dimf[f],basis_sha256=sha(json.dumps(C.B[f],separators=(',',':')).encode()))for f in sorted(used|inherited)],cache_transform=receipt,physical_emitter_sha256=receipt['transform_sha256'])
    ends={mp[s]:f for s,f in producer.get('helper_endpoints',{}).items()if s not in removed};ends.update({mp[r['stream']]:r['recovery_frame']for r in rows if not r['direct']});ctx=dict(producer['context']);oldregs=ctx['regs'];ctx['regs']=[role for j,role in enumerate(oldregs)if 2*v+j not in removed];ctx['removed']=set(ctx.get('removed',set()))|{oldregs[s-2*v]for s in removed};ctx['restored_endpoints']={ctx['regs'][s-2*v]:f for s,f in ends.items()}
    result=dict(producer);result.update(context=ctx,records=out,physical=meta,result=meta,initial_state=initial,final_state=final,helper_endpoints=ends,cache_entries=rows,cache_census=receipt)
    if output_dir is not None:
        dest=Path(output_dir);dest.mkdir(parents=True,exist_ok=True);(dest/'cache-records.bin.gz').write_bytes(gzip.compress(out.tobytes(),mtime=0));(dest/'cache.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n');(dest/'selection.json').write_text(json.dumps(sel,sort_keys=True,indent=2)+'\n')
    print('PASS hybrid',len(rows),'direct',len(removed),'residual rank saved',saving,'scalar',count,'paid',sum(hist.values()),flush=True);return result
