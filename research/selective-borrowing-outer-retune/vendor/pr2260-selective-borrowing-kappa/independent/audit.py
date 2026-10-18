"""Independent T8 family-tag and Gaussian-factor audit of literal owners.

No optimizer/emitter/hosting constructor is imported. Window boundaries come
from the pinned parent program including bridge reads and writes. Local ABI
normalization is rechecked using the separately implemented public signed-
Pauli/exact-Gaussian interpreter; this local engine is shared with the native
audit and is explicitly not a third independent native implementation.

For C_v=((1+i)I+(1-i)X_v)/2, all shifts X_v commute on one physical family.
The literal factor multiset, including physical family and positive direction,
therefore suffices for the pending-child operator equality. Untagged global
axis counts do not suffice and are rejected by a cross-family mutation.
"""
import argparse,collections,gzip,hashlib,importlib.util,json,sys,time
from pathlib import Path
sys.dont_write_bytecode=True

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):
    p=Path(path);data=p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix=='.gz' else data)
def packed(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def tuples(value):return tuple(map(tuples,value)) if isinstance(value,list) else value
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def orthogonal_basis(q):
    z=next(i for i in range(9) if not(q>>i&1));u=q^(1<<z)
    indices=list(range(9));indices[0],indices[z]=indices[z],indices[0]
    result=[(1<<i)^(u if u>>i&1 else 0) for i in indices]+[1<<i for i in range(9,73)]
    need(result[0]==q,'port chart first column')
    need(all(((a&b).bit_count()%2)==(i==j) for i,a in enumerate(result) for j,b in enumerate(result)),'actual 73-column orthogonal chart')
    return result

def schedule(parent,plan):
    original=parent['execution_schedule'];groups={};current=None;global_events=[]
    for index,event in enumerate(original):
        if event['kind'] in ('bank_padding_cover_sweep','translate_every_live_family'):
            global_events.append(index);continue
        if event['kind']=='local_cover_sweep':current=event['stage'];groups[current]=[]
        need(current is not None,'source starts with a local invocation')
        groups[current].append(index)
    need(set(groups)==set(range(9)),'all nine actual stage blocks')
    order=[tuple(x) for x in plan['order']]
    need(len(order)==len(set(order))==72,'72 distinct complete T8 calls')
    projection=collections.defaultdict(list);expanded=[];call_positions={};last_touch={};windows={};tags={}
    stage_pairs={x['stage']:x['pair'] for x in parent['recipe'] if x['kind']=='local'}
    for time_index,(stage,replica) in enumerate(order):
        need(stage in groups and 0<=replica<8,'actual stage/replica bounds')
        for source_index in groups[stage]:
            event=original[source_index];position=len(expanded)
            expanded.append((time_index,replica,source_index));projection[replica].append(source_index)
            if event['kind']=='local_cover_sweep':
                pair=stage_pairs[event['stage']];last_touch[replica,pair]=position
                call_positions[time_index]=position
            elif event['kind']=='bridge':
                last_touch[replica,event['src']]=position;last_touch[replica,event['dst']]=position
            elif event['kind']=='idle_cover_sweep':
                for side,child in enumerate(event['child_indices']):
                    tags[child]=(event['pair'],side,source_index)
                    windows[replica,child]=(last_touch.get((replica,event['pair']),-1),position)
    expected=[i for i in range(len(original)) if i not in global_events]
    need(all(projection[r]==expected for r in range(8)),'each replica preserves every actual source event')
    for key,(capacity,times) in plan['windows'].items():
        replica,child=map(int,key.split(','));lower,upper=windows[replica,child]
        actual=[t for t,pos in sorted(call_positions.items()) if lower<pos<upper]
        need(actual==times,('window derived from actual local/bridge events',key,actual,times))
        need((plan['pairs'][str(child)],plan['sides'][str(child)])==tags[child][:2],'frozen pair/side agrees with actual parent')
    return order,call_positions,windows,tags,expanded

def native_files(native_path,wrapper_path,orientation):
    if native_path.is_dir():
        return native_path/('NATIVE-'+orientation.upper()+'.json.gz'),native_path/'ENDPOINT-WRAPPERS.json'
    need(wrapper_path is not None,'explicit wrapper file for a portable native payload')
    return native_path,wrapper_path

def wrappers(trace_path,native_path,wrapper_path,orientation,engine):
    native_path,report_path=native_files(native_path,wrapper_path,orientation)
    trace=read(trace_path);report=read(report_path);native=read(native_path)
    need(report['trace_sha256']==sha(trace_path),'literal normalized trace binding')
    need(report['native_payload_sha256']==hashlib.sha256(gzip.decompress(native_path.read_bytes())).hexdigest(),'literal native payload binding')
    need(report['helper_count']==len(report['helpers'])==len(trace['helper_widths']),'complete helper wrapper domain')
    cache=set();checked=0
    for register,width in trace['helper_widths'].items():
        wrapper=report['helpers'][register];endpoint=trace['endpoints'][register]
        need(wrapper['width']==width==len(endpoint['final'])-len(endpoint['initial']),'actual endpoint residual width')
        need(wrapper['initial']==endpoint['initial'] and wrapper['final']==endpoint['final'],'actual E/F basis binding')
        ref=native['helper_residual_refs'][register]
        need(ref==wrapper['relative_native_ref'],'actual lowered helper reference')
        record=native['records'][ref];recipe=record['recipe']
        need(recipe['rank']==width,'actual positive normalized C width')
        pre=tuples(wrapper['prewrapper']);post=tuples(wrapper['postwrapper']);actual=tuples(record['literal_expected'])
        key=hashlib.sha256(packed([pre,actual,post,width])).hexdigest()
        if key not in cache:
            engine.equal(pre,engine.adjoint(engine.monomial(recipe['right'])),'literal pre R inverse')
            engine.equal(post,engine.adjoint(engine.monomial(recipe['left'])),'literal post L inverse')
            engine.equal(pre+actual+post,engine.fourier(width),'positive C_width tensor identity with exact global phase')
            cache.add(key);checked+=1
        need(wrapper['normalized_operator']=='C_'+str(width)+' tensor I_'+str(9-width),'positive normalized ABI direction')
    need(len(report['data'])==224,'all source and target ABI adapters')
    return report,trace,{'orientation':orientation,'helpers':len(report['helpers']),'unique_literal_operator_checks':checked,'trace_sha256':sha(trace_path),'native_payload_sha256':report['native_payload_sha256'],'wrapper_sha256':sha(report_path)}

def audit(args):
    started=time.monotonic();parent=read(args.parent);phases=read(args.phases);plan=read(args.plan);owners=read(args.owners)
    need(sha(args.parent)==args.parent_sha256,'immutable actual T8 parent gzip source')
    need(parent['exact_data_phase_recipe_sha256']==sha(args.phases),'actual parent phase recipe source')
    need((parent['m'],plan['T'],plan['M'],plan['live'])==(73,8,73,7168),'actual T8 geometry')
    need(phases['m']==73 and len(phases['recipes'])==112,'complete parent physical port recipes')
    order,callpos,windows,tags,expanded=schedule(parent,plan)
    source_calls={(x['stage'],x['replica']):x for x in parent['calls']}
    engine=load('owner_factor_native_independent',args.engine)
    forward,trace,forward_receipt=wrappers(args.forward_trace,args.forward_native,args.forward_wrapper,'forward',engine)
    backward,backtrace,backward_receipt=wrappers(args.backward_trace,args.backward_native,args.backward_wrapper,'backward',engine)
    need(trace['helper_widths']==backtrace['helper_widths'],'same actual residual inventory in both orientations')
    widths={int(k):w for k,w in trace['helper_widths'].items()};bases=[orthogonal_basis(r['q']) for r in phases['recipes']]
    for orientation,report in [('forward',forward),('backward',backward)]:
        for adapter in report['data']:
            register=adapter['register'];port=register%112
            need(adapter['normal']==phases['recipes'][port]['q'],'actual data adapter normal matches source parent port')
            source=(register<112) if orientation=='forward' else (register>=112)
            need((adapter['role'],adapter['position'])==(('source','entry') if source else ('target','exit')),'actual data adapter direction and endpoint')
            need(adapter['recipe']['rank']==0,'all actual data chart adapters are monomial')
    ranks={(x['child'],x['port']):x['rank'] for x in parent['idle_children']}
    need(len(ranks)==len(parent['idle_children'])==2016,'all actual positive-rank parent children')
    for (child,port),rank in ranks.items():
        record=phases['recipes'][port]['idle_children'][child];axes=record['orthogonal_axes']
        need(rank==record['rank']==len(axes),'actual parent rank/axes equality')
        need(len(set(axes))==rank and all(v in bases[port] for v in axes),'literal pending axes in actual orthogonal chart')
    used=collections.defaultdict(set);by_call=collections.defaultdict(dict);hosted_factors=collections.Counter();charts={};roles=[]
    for row in owners:
        time_index=row['time'];stage,replica=order[time_index];helper=row['helper'];width=widths[helper]
        need((row['stage'],row['replica'],row['width'])==(stage,replica,width),'actual role identity and width')
        need(helper not in by_call[time_index],'one actual helper role per invocation')
        owner_replica,child,port=row['owner_replica'],row['child'],row['port'];pair,side,event=tags[child]
        need(0<=owner_replica<8 and 0<=port<112,'actual owner bounds')
        physical=owner_replica*896+(2*pair+side)*112+port
        need(row['family']==physical,'actual parent physical family tag')
        need(row['copy']==owner_replica*112+port,'canonical old copy ABI metadata')
        lower,upper=windows[owner_replica,child]
        need(lower<callpos[time_index]<upper,'complete invocation in actual untouched pending interval')
        call=source_calls[stage,replica];need(physical not in {r[0] for r in call['owners'][:224]},'no alias with actual data input or output')
        rank=ranks[child,port];offset=row['offset'];need(0<=offset and offset+width<=rank,'literal pending coordinate bounds')
        key=(owner_replica,child,port);slots=set(range(offset,offset+width))
        need(not(used[key]&slots),'literal disjoint pending factors');used[key]|=slots
        axes=phases['recipes'][port]['idle_children'][child]['orthogonal_axes'];occupied=axes[offset:offset+width]
        basis=bases[port];indices=[basis.index(v) for v in occupied];spectators=[i for i in range(73) if i not in indices][:9-width]
        permutation=indices+spectators+[i for i in range(73) if i not in indices and i not in spectators]
        need(sorted(permutation)==list(range(73)),'actual complete chart including spectators')
        sigma=[basis[i] for i in permutation];need(sigma[:width]==occupied,'normalized first w axes equal literal pending factors')
        sigma_hash=hashlib.sha256(packed(sigma)).hexdigest();charts[sigma_hash]=sigma
        orientation=call['orientation'];local=(forward if orientation=='forward' else backward)['helpers'][str(helper)]
        need(local['width']==width,'actual orientation-specific normalized child')
        for axis in occupied:hosted_factors[physical,child,axis,1]+=1
        by_call[time_index][helper]=physical
        roles.append({'time':time_index,'helper':helper,'family':physical,'owner_replica':owner_replica,'child':child,'port':port,'offset':offset,'width':width,'normalized_direction':1,'axes':occupied,'spectator_basis_indices':spectators,'sigma_sha256':sigma_hash,'orientation':orientation,'relative_native_ref':local['relative_native_ref']})
    need(len(owners)==len(order)*len(widths),'all helper roles and no extras')
    for t in range(72):
        need(set(by_call[t])==set(widths),'every actual helper exactly once')
        need(len(set(by_call[t].values()))==len(widths),'one complete helper per physical family per invocation')
    expected=collections.Counter();remainders=[];translations=[];remainder_factors=collections.Counter();idle=collections.Counter()
    for (child,port),rank in sorted(ranks.items()):
        pair,side,event=tags[child];recipe=phases['recipes'][port]['idle_children'][child];axes=recipe['orthogonal_axes']
        for replica in range(8):
            family=replica*896+(2*pair+side)*112+port;slots=used[replica,child,port]
            need(slots==set(range(len(slots))),'literal compacted pending prefix')
            for axis in axes:expected[family,child,axis,1]+=1
            rest=axes[len(slots):]
            if rest:idle[len(rest)]+=1
            for axis in rest:remainder_factors[family,child,axis,1]+=1
            remainders.append({'family':family,'replica':replica,'child':child,'port':port,'source_event':event,'rank':len(rest),'axes':rest,'normalized_direction':1,'translation_after':recipe['translation_after']})
            # Kept even when rank zero: the original child's translation is never erased.
            translations.append((family,child,recipe['translation_after']))
    actual=hosted_factors+remainder_factors
    need(actual==expected,'same physical family, source child, literal axis and positive C direction exactly once')
    profile=collections.Counter(idle)
    profile.update({int(r):72*n for r,n in trace['local_profile'].items()})
    mass=sum(r*n for r,n in profile.items());need(mass==520704,'complete independently reconstructed paid rank mass')
    controls=[]
    wrong=actual.copy();first=next(iter(wrong));wrong[first]-=1;wrong[first[:-1]+(-1,)]+=1
    need(+wrong!=expected,'negative C direction control');controls.append('negative_child_direction')
    pair=None
    keys=list(expected)
    for a in keys:
        pair=next(((a,b) for b in keys if a[1]==b[1] and a[0]!=b[0] and a[2]!=b[2] and a[2]<(1<<9) and b[2]<(1<<9)),None)
        if pair:break
    need(pair is not None,'nontrivial cross-family axis control exists');a,b=pair
    wrong=actual.copy();wrong[a]-=1;wrong[b]-=1;wrong[b[0],b[1],a[2],a[3]]+=1;wrong[a[0],a[1],b[2],b[3]]+=1
    need(collections.Counter(k[2] for k,n in wrong.items() for _ in range(n))==collections.Counter(k[2] for k,n in expected.items() for _ in range(n)),'cross-family mutation keeps the untagged global axis bag')
    need(+wrong!=expected,'cross-family axis control');controls.append('cross_family_axis_swap_with_same_global_axis_counts')
    one=next(iter(forward['helpers'].values()));native=read(native_files(args.forward_native,args.forward_wrapper,'forward')[0]);record=native['records'][one['relative_native_ref']]
    circuit=tuples(one['prewrapper'])+tuples(record['literal_expected'])+tuples(one['postwrapper'])
    try:engine.equal(circuit+(('phase',1),),engine.fourier(one['width']),'wrong scalar phase control')
    except ValueError:controls.append('wrong_global_scalar_phase')
    else:raise ValueError('scalar-phase mutation accepted')
    payload={'roles':roles,'charts':charts,'remainders_including_zero_rank_translations':remainders}
    args.out.mkdir(exist_ok=False);payload_path=args.out/'ACTUAL-FAMILY-FACTORS.json.gz';payload_path.write_bytes(gzip.compress(packed(payload),mtime=0))
    result={'status':'PASS_ACTUAL_T8_FAMILY_OPERATOR_PARTITION','owners':len(owners),'calls':72,'helper_count':len(widths),'distinct_actual_73_column_charts':len(charts),'parent_factor_count':sum(expected.values()),'hosted_factor_count':sum(hosted_factors.values()),'remainder_factor_count':sum(remainder_factors.values()),'all_original_child_translations_retained':len(translations),'idle_profile':dict(sorted(idle.items())),'complete_profile':dict(sorted(profile.items())),'rank_mass':mass,'native_ABI_rechecks':[forward_receipt,backward_receipt],'mutations_rejected':controls,'source_sha256':{'parent':sha(args.parent),'phases':sha(args.phases),'plan':sha(args.plan),'owners':sha(args.owners),'forward_trace':sha(args.forward_trace),'backward_trace':sha(args.backward_trace),'native_engine':sha(args.engine)},'actual_factors_sha256':sha(payload_path),'seconds':time.monotonic()-started,'scope':'Exact finite family-tagged Gaussian factor/actual chronology/chart/ABI composition. Shares public local signed-Pauli and exact-Gaussian checker with native audits. No all-size compiler, precision/tape, stock/invoice or analytic transfer is established here.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ['parent','phases','plan','owners','forward-trace','backward-trace','forward-native','backward-native','engine','out']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--forward-wrapper',type=Path);p.add_argument('--backward-wrapper',type=Path)
    p.add_argument('--parent-sha256',required=True)
    audit(p.parse_args())
