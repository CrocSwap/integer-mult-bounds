#!/usr/bin/env python3
"""Authenticated whole-root source comparison and matched physical controls.

Chris R / Clear1nsight with substantial coordinated OpenAI Codex assistance.
Apache-2.0. Finite executions corroborate the written quantified refinement.
"""
import argparse, json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import runtime
need=runtime.need
STATUS='PASS_QQ16_PROTOCOL_COMPARISON'
NAMES=('RESULT.json','BILL.json','EXECUTION.json')

def physical():
    cmd=[sys.executable,'-I','-Werror','-B']
    if sys.flags.optimize:cmd.append('-O')
    cmd.append(str(HERE/'comparative_fixture.py'))
    result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=240)
    need(result.returncode==0 and not result.stderr,'matched physical replay:'+result.stdout+result.stderr)
    return runtime.parse(result.stdout)

def compute():
    pins=runtime.authenticated_inputs()
    runtime.cold()
    try:
        old=runtime.predecessor()
        connection=runtime.module('qq16_comparison_connection',old/'connection.py')
        data,packet,word,parent,service=connection.bindings()
        ledger=runtime.module('qq16_comparison_ledger',HERE/'ledger.py')
        resources=runtime.module('qq16_comparison_resources',HERE/'resources.py')
        protocol=runtime.module('qq16_comparison_protocol',HERE/'protocol.py')
        adapter=runtime.module('qq16_comparison_adapter',HERE/'adapter.py')
        cost=runtime.module('qq16_comparison_cost',old/'cost.py')
        census=ledger.literal_census(data,parent)
        native_source=runtime.module('qq16_comparison_native',old.parents[1]/'research/physical-complex-controller/production_native.py')
        PRIME=native_source.PRIME
        gamma=cost.gamma()
        startup=resources.startup_retirement_bound(PRIME)
        bound=ledger.selected_whole_root_bound(census,gamma,PRIME,startup['actions_upper_bound'])
        from machine import Machine,transfer,copy_symbols,origin
        from parking import Parking,FiniteFields
        from cardinal_counts import Count
        from session import erase_marker
        from records import Tape
        from words import LEFT,BLANK
        primitive=protocol.verify_primitives(Tape,Parking,FiniteFields,transfer,copy_symbols,
                                            origin,erase_marker,LEFT,BLANK)
        cls=adapter.machine_class(Machine,Count,transfer,erase_marker)
        controls=resources.adoption_controls(cls,Tape)
        resource_checks=resources.checks()
        geometry_controls=[]
        for rank in (1,2,8,48,72):
            descriptor=dict(prefixes=3,rows=14336*gamma,front=1,compact_bits=3,
                 before=2,width=146,after=4,back=1,spacing=2,guard=7,residue=1,
                 component_bits=24,coefficients=2,root_width=146)
            geometry_controls.append(ledger.capsule_injection(descriptor,rank,17))
        bill={'census':census,'same_boundary_threshold':ledger.fair_threshold(census),
              'suffix':ledger.suffix_header_cost(census),
              'matched_external_components':ledger.matched_external_header_cost(census),
              'startup_retirement':startup,
              'generic_whole_root_bound':bound,'fixed_inventory':resources.inventory(PRIME),
              'enlarged_guard':resources.guard_recheck(PRIME,gamma),
              'accounting_controls':ledger.rejection_controls(census),
              'geometry_controls':geometry_controls,
              'qq16_incremental_sign':'unresolved: nonchild/service,6972Gamma changed-core calls and native nonheader allocator-context residual on503674Gamma matching-payload calls remain explicit; generic protocol credit is available to B'}
    finally:runtime.cleanup()
    execution=physical()
    execution.update(primitives=primitive,adoption_controls=controls,resources=resource_checks)
    result={'status':STATUS,'scientific_main':'e40a7b454da6a0df53e358aa3265b9c1c39de2c8',
       'predecessor_head':'0b082d22a0e9a442d264ab0633e35ef26c790630',
       'scope':'Source-compatible root-only external child protocol on original arithmetic; all descendants remain original C; full selected literal census and conditional all-size R/W/unit-move refinement.',
       'new_result':'Fair protocol-only baseline shares the exact closed primitive bundle and allocator history, adds1023controller tapes without a second Ordinary engine, and removes top parent serialization on every original root child; startup/retirement and all later calls are charged. Optional guarded child-return adoption removes an additional transfer.',
       'cost_unit':'literal read+write+unit-move actions; separately compiled finite-control charges remain a stated condition, never elapsed-time or scalar-allowance evidence',
       'qq16_decision':'Avoided parent parking is a generic improvement and cannot be credited exclusively to QQ16. The matched suffix header increases by28actions/call; QQ16 incremental affordability remains conditional on the complete stated threshold.',
       'unchanged_kappa':'836330098538459/500000000000000000',
       'remaining':['Original native/ordinary/Compact/source-entry/hosting and row-stock premises.',
          'No production O73 payload or complete RootLayer.run execution.',
          'No all-node external substitution or new supplier/bootstrap/exponent.',
          'A Turing-step dominance claim requires separately bounded finite-control tariffs; an exact cell-action saving is not elapsed runtime.'],
       'authenticated_inputs':{k:runtime.sha(v) for k,v in sorted(pins.items())},
       'implementation_sha256':{p.name:runtime.sha(p.read_bytes()) for p in sorted(HERE.glob('*.py')) if p.name!='test_verify.py'},
       'proof_sha256':{name:runtime.sha((HERE/name).read_bytes()) for name in ('PROOF.md','PROTOCOL.md','COMPARISON.md','RESOURCES.md','BASELINE.md','ADMISSION.json','REUSE.json')},
       'assisted_review':'Separate read-only adversary required at frozen integrated hashes; shared source dependencies are disclosed.'}
    return dict(zip(NAMES,(result,bill,execution)))

def check_receipt(name,obj,folder=HERE):
    expected=runtime.parse(json.dumps(obj,sort_keys=True,allow_nan=False))
    need(runtime.typed(runtime.parse((folder/name).read_bytes()))==runtime.typed(expected),
         'whole typed receipt mismatch:'+name)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    if args.write:need(not any((HERE/n).exists() for n in NAMES),'refuse receipt overwrite')
    objects=compute()
    for name,obj in objects.items():
        if args.write:
            with (HERE/name).open('x') as stream:stream.write(json.dumps(obj,sort_keys=True,indent=2)+'\n')
        else:check_receipt(name,obj)
    print(STATUS)
if __name__=='__main__':main()
