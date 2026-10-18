#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Construct a literal arbitrary-T source parent, PLAN and SPEC from exact owners.

CLI: --package IMMUTABLE_SOURCE --owners RECONSTRUCTOR_OUTPUT --out FRESH_DIR.
Source lineage and arbitrary-group argument are in replica_parent.py / PARENT-LIFT.md.
This adapter mutates neither the source package nor owner input directory.
"""
import argparse, ast, collections, copy, importlib.util, json, sys
from pathlib import Path
sys.dont_write_bytecode=True
import replica_parent as P
assert __debug__, 'Assertions required'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,required=True);ap.add_argument('--owners',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();base=a.package.resolve();owners=a.owners.resolve();out=a.out.resolve()
    P.require(not out.exists(),'fresh output required')
    source_names=['inputs/PLAN.json','inputs/SPEC.json','inputs/GLOBAL-TEMPLATE.json.gz','new/BORROW-PROVIDERS.json','vendor/build_parent.py']
    input_names=['ORDER.json','OWNERS.json.gz','DISPATCH.json','PROFILE.json','RESULT.json']
    input_hash={str(base/n):P.sha(base/n)for n in source_names}|{str(owners/n):P.sha(owners/n)for n in input_names}
    P.SOURCE=base/'inputs/GLOBAL-TEMPLATE.json.gz'
    plan=P.read(base/'inputs/PLAN.json');spec=P.read(base/'inputs/SPEC.json');providers=P.read(base/'new/BORROW-PROVIDERS.json')
    order=P.read(owners/'ORDER.json');dispatch_rows=P.read(owners/'DISPATCH.json');roles=P.read(owners/'OWNERS.json.gz');profile=P.read(owners/'PROFILE.json')
    T=1+max(r for st,r in order);P.require(T>0,'positive T');P.require(len(order)==9*T,'complete new invocation count')
    parent=P.build(T);geometry=P.check(parent,parent['replica_lift']['groups'])
    sp=importlib.util.spec_from_file_location('retained_physical_source_windows',base/'vendor/build_parent.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
    windows,schedule=mod.actual_windows(parent,order)
    independent=P.expand_schedule(parent,order);P.require(schedule==independent,'independent literal source-event expansion')
    dispatch={(s,r):pid for s,r,pid in dispatch_rows}
    P.require(len(dispatch_rows)==len(order) and set(dispatch)==set(map(tuple,order)),'dispatch bijection')
    P.require(set(dispatch.values())<=set(providers),'known provider')
    for pid,d in providers.items():
        P.require(pid in plan['provider_registry'],'provider in retained registry')
        plan['provider_registry'][pid].update(widths=d['widths'],actual_paid_profile={str(k):v for k,v in sorted({int(k):v for k,v in d['actual_paid_profile'].items()}.items())})
    widths={pid:d['widths']for pid,d in providers.items()};R=len(next(iter(widths.values())))
    P.require(all(len(w)==R for w in widths.values()),'same helper count')
    pairs,sides=plan['pairs'],plan['sides'];helper_seen=collections.defaultdict(set);family_seen=collections.defaultdict(set);used=collections.defaultdict(set)
    for z in roles:
        tm=z['time'];P.require(0<=tm<len(order),'owner time');st,r=order[tm];pid=dispatch[st,r];h=z['helper']
        P.require((z['stage'],z['replica'])==(st,r) and 0<=h<R,'literal helper/call')
        rep,ch,port=z['owner_replica'],z['child'],z['port'];w=widths[pid][h]
        P.require(0<=rep<T and 0<=port<112 and z['width']==w,'owner replica/port/width')
        cap,allowed=windows[f'{rep},{ch}'];P.require(tm in allowed,'strict physical pending window')
        fam=rep*896+(2*pairs[str(ch)]+sides[str(ch)])*112+port
        P.require(z['family']==fam and z['copy']==112*rep+port,'literal family and copy')
        P.require(h not in helper_seen[tm] and fam not in family_seen[tm],'distinct per-call helpers/families')
        helper_seen[tm].add(h);family_seen[tm].add(fam)
        off=z['offset'];P.require(isinstance(off,int)and 0<=off and off+w<=cap,'physical pending capacity')
        cells=set(range(off,off+w));key=rep,ch,port;P.require(not used[key]&cells,'no overlapping residual cells');used[key]|=cells
    P.require(len(roles)==len(order)*R and set(helper_seen)==set(range(len(order))) and all(v==set(range(R))for v in helper_seen.values()),'complete actual role inventory')
    idle=collections.Counter()
    for key,(cap,allowed)in windows.items():
        rep,ch=map(int,key.split(','))
        for port in range(112):
            cells=used[rep,ch,port];P.require(cells==set(range(len(cells))),'compact residual prefix')
            if cap>len(cells):idle[cap-len(cells)]+=1
    paid=collections.Counter(idle)
    for st,r in order:paid.update({int(k):v for k,v in providers[dispatch[st,r]]['actual_paid_profile'].items()})
    P.require(dict(paid)=={int(k):v for k,v in profile.items()},'entire actual paid profile')
    P.require(73*896*T-sum(k*v for k,v in paid.items())==320*T,'full rank mass and deficit')
    stage_template={c['stage']:c for c in plan['provider_calls']}
    plan['provider_calls']=[];plan['per_call_widths']=[]
    for tm,(st,r)in enumerate(order):
        pid=dispatch[st,r];desc=plan['provider_registry'][pid];z=copy.deepcopy(stage_template[st]);orientation='forward'if st%2==0 else'backward'
        P.require(z['orientation']==orientation,'source stage orientation')
        z.update(replica=r,time=tm,provider=pid,local_program_sha256=desc['orientation_program_sha256'][orientation]);plan['provider_calls'].append(z)
        plan['per_call_widths'].append(dict(stage=st,replica=r,time=tm,widths=desc['widths']))
    plan.update(T=T,live=896*T,deficit=320*T,order=order,windows=windows,profile=profile,assignment_sha256=P.sha(owners/'OWNERS.json.gz'),assignment_content_sha256=P.identity(roles),status=f'EXPLICIT_T{T}_STRICT_WINDOW_OWNER_FILL',mode=f'mixed-t{T}-exact-fill',solver_status='Literal fixed owner witness independently rechecked; no solver runs in adapter')
    plan['replica_lift']=dict(replicas=T,parent_template_content_sha256=P.identity(parent),owners_file_sha256=P.sha(owners/'OWNERS.json.gz'),schedule_content_sha256=P.identity(schedule),source_replicas=37,groups=parent['replica_lift']['groups'],phase_recipe_unchanged=True)
    # Discovery computes geometry/numerical expectations, but the descriptive
    # reporting denominator is source metadata and must survive the reset.
    preserved_expected={'gain_baseline_kappa':spec['expected']['gain_baseline_kappa']}
    spec.update(name=f'mixed-t{T}-exact-fill',call_order=order,dispatch=dispatch_rows,providers={},expected=preserved_expected)
    assembly_ast=ast.parse((base/'code/assemble.py').read_text(encoding='utf-8'))
    read_expected={node.slice.value for node in ast.walk(assembly_ast) if isinstance(node,ast.Subscript) and isinstance(node.value,ast.Name) and node.value.id=='X' and isinstance(node.slice,ast.Constant) and isinstance(node.slice.value,str)}
    discovery_computed={'complex_lower','conservative_complex_lower'}
    P.require(read_expected-discovery_computed<=set(preserved_expected),'all noncomputed assembly X metadata retained')
    # Fresh discovery/freezing and outer admission supply all expected values.
    spec['geometry']=dict(replicas=T,stages=plan['L'],pairs=plan['K'],dimension=plan['M'],charged_prefix_bits=1<<(128+37+2*len(order)+4).bit_length(),parent_live=parent['live'],parent_physical=parent['physical'],parent_idle=geometry['parent_idle'],parent_helpers=504)
    out.mkdir(parents=True)
    for name,obj in [('GLOBAL-TEMPLATE.json.gz',parent),('OWNERS.json.gz',roles),('DISPATCH.json',dispatch_rows),('PROFILE.json',profile),('ORDER.json',order),('CONSTRUCTION.json',P.read(owners/'RESULT.json'))]:P.write_new(out/name,obj)
    # Bind canonical output owner serialization while preserving exact role semantics.
    output_owner=out/'OWNERS.json.gz'
    P.require(P.read(output_owner)==roles,'serialized owner semantics')
    # Canonical gzip may differ from emitter gzip. Bind the actual output file everywhere.
    plan['assignment_sha256']=P.sha(output_owner);plan['replica_lift']['owners_file_sha256']=P.sha(output_owner)
    P.write_new(out/'PLAN.json',plan)
    spec['data']={'plan_sha256':P.sha(out/'PLAN.json'),'owners_sha256':P.sha(output_owner)}
    P.write_new(out/'SPEC.json',spec)
    receipt=dict(status='PASS_LITERAL_GENERAL_T_PARENT_PLAN_SPEC',geometry=spec['geometry'],groups=parent['replica_lift']['groups'],input_sha256=input_hash,template_content_sha256=P.identity(parent),new_sha256=P.sha(out/'GLOBAL-TEMPLATE.json.gz'),source_sha256=P.SOURCE_SHA,roles=len(roles),helpers_per_call=R,source_events_per_replica=30,global_tail=[30,31],schedule_content_sha256=P.identity(schedule),profile=dict(sorted(paid.items())),idle=dict(sorted(idle.items())),private_work_shared=514,source_programs_phase_recipes_unchanged=True,discovery_X_metadata=sorted(read_expected-discovery_computed),discovery_computed_X_keys=sorted(read_expected&discovery_computed),phase_scope='Reuses root fresh hash-bound native/phase admission; this adapter checks literal source geometry and complete paid owner profile.',scripts={Path(__file__).name:P.sha(__file__),Path(P.__file__).name:P.sha(P.__file__)})
    P.write_new(out/'PARENT-LIFT-RECEIPT.json',receipt)
    for path,h in input_hash.items():P.require(P.sha(path)==h,'input unchanged after lift')
    print('PASS_LITERAL_GENERAL_T_PARENT_PLAN_SPEC',json.dumps(spec['geometry'],sort_keys=True),flush=True)
if __name__=='__main__':main()
