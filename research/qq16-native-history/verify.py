#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticated context theorem controls and actual fitted scientific replay."""
import argparse, hashlib, json, subprocess, sys, types
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
STATUS='PASS_QQ16_NATIVE_HISTORY'
NAMES=('RESULT.json','BILL.json','EXECUTION.json')
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def unique(pairs):
    result={}
    for k,v in pairs:
        need(k not in result,'duplicate key');result[k]=v
    return result
def parse(raw):return json.loads(raw,object_pairs_hook=unique)
def typed(value):
    if isinstance(value,dict):return ('dict',tuple((k,typed(v)) for k,v in sorted(value.items())))
    if isinstance(value,list):return ('list',tuple(map(typed,value)))
    return (type(value).__name__,value)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def bootstrap():
    # This verifier and its committed seals are the explicit bootstrap trust.
    seals=parse((HERE/'SEALS.json').read_bytes())
    need(sha((HERE/'runtime.py').read_bytes())==seals['runtime.py'],'local module integrity:runtime.py')
    loader=types.ModuleType('runtime');loader.__file__=str(HERE/'runtime.py');sys.modules['runtime']=loader
    exec(compile((HERE/'runtime.py').read_bytes(),str(HERE/'runtime.py'),'exec'),loader.__dict__)
    pins=loader.authenticated_inputs()
    for name,digest in seals.items():
        need(sha((HERE/name).read_bytes())==digest,'local module integrity:'+name)
    return loader,pins,seals
def check_receipt(name,expected,folder=HERE):
    normalized=parse(json.dumps(expected,sort_keys=True,allow_nan=False))
    need(typed(parse((folder/name).read_bytes()))==typed(normalized),'whole typed receipt mismatch:'+name)
def validate_execution(execution):
    need(set(execution)=={'fitted','native_nested','inherited_bridge'},'complete physical execution receipt')
    fitted=execution['fitted'];pair=fitted['fitted_pair']
    need(len(pair)==2 and all(x['branch']=='fitted' and len(x['roots'])==2 for x in pair),'actual fitted branch receipts')
    need(fitted['delta']==[0,0,0] and fitted['distinct_payload_delta']==[0,0,0],'observed paired actions')
    need({'runtime.arena','runtime.indices'}<=set(fitted['different_queues']),'actual native queue difference')
    need(fitted['fitted_fallback_fitted']==['fitted','fallback','fitted'] and fitted['theorem'] is False,'scope of finite execution')
    for row in fitted['warm_histories']+pair:
        need(row['borrowed_preserved'] is True and row['lifecycle']['status']=='PASS_CLOSED_SIX_ARENA_BOUNDARY','actual complete outer return')
    bridge=execution['inherited_bridge']
    need(bridge['actual_source_endpoint'] is True and len(bridge['matched'])==1 and len(bridge['matched'][0]['calls'])==8,'inherited actual reduced prefix/bridge/suffix replay')
    nested=execution['native_nested']
    need(nested['native_counts']['calls']>=1 and nested['native_counts']['returns']>=1 and nested['parent_pc_after']==nested['parent_pc_before']+1,'actual nested child return')
    need(nested['root_program_completed'] is False and nested['retired_after_completed_cut'] is True and nested['all_engine_roles_retired'] is True,'stopped parent is disposed, not completed')
def inherited_bridge(prior):
    code="""import sys,json
sys.path.insert(0,sys.argv[1])
import comparative_fixture as f
try:
    result=f.experiment(width=2,generations=1,binding_factory=f.BridgeBinding)
    print(json.dumps(result,sort_keys=True))
finally:f.runtime.cleanup()
"""
    command=[sys.executable,'-I','-Werror','-B']
    if sys.flags.optimize:command.append('-O')
    completed=subprocess.run(command+['-c',code,str(prior)],cwd=ROOT,capture_output=True,text=True,timeout=120)
    need(completed.returncode==0 and not completed.stderr,'inherited bridge replay:'+completed.stdout+completed.stderr)
    return parse(completed.stdout)

def compute(runtime,pins,seals,saved_execution=None):
    runtime.cold()
    try:
        prior=runtime.predecessor()
        connection=runtime.module('history_prior_connection',runtime._prior.predecessor()/'connection.py')
        data,packet,word,parent,service=connection.bindings()
        ledger=runtime.module('history_prior_ledger',prior/'ledger.py')
        census=ledger.literal_census(data,parent)
        state=runtime.module('state_model',HERE/'state_model.py')
        mechanism=runtime.module('history_mechanism',HERE/'mechanism.py')
        lifecycle=runtime.module('history_lifecycle',HERE/'lifecycle.py')
        comparison=runtime.module('history_comparison',HERE/'comparison.py')
        proof_controls=mechanism.checks()
        marker=lifecycle.marker_potential_control()
        bill=comparison.check(prior_census=census,mechanism_contract=proof_controls)
        import monomial_packets, binary, compact_engine, monomial_engine, ordinary, compact_reference
        source_modules={'binary':binary,'compact':compact_engine,'monomial':monomial_engine,'ordinary':ordinary,'reference':compact_reference}
        bill['source_site_controls']=comparison.check_sources({k:Path(v.__file__).read_text() for k,v in source_modules.items()})
        bill['literal_census']=census
        bill['native_codec']=proof_controls
        bill['controller_marker_potential']=marker
        bill['dynamic_allocation_control']=state.allocation_control()
        if saved_execution is None:
            fitted=runtime.module('fitted_fixture',HERE/'fitted_fixture.py')
            nested=runtime.module('history_native_nested',HERE/'native_nested.py')
            execution={'fitted':fitted.run_discriminator(),'native_nested':nested.run_cut(),'inherited_bridge':inherited_bridge(prior)}
        else:execution=saved_execution
        validate_execution(execution)
    finally:runtime.cleanup()
    result={'status':STATUS,'scientific_main':'12fa8c5c844be21bfefb38a19503fbd867a11244','priority_revision':7,
      'frozen_predecessor':'6749e458800f461535d64cc91c017552d9f55e5f',
      'new_result':'Source-relative six-arena phased history action relation plus successful coefficient-payload opacity removes all retained C body cost residuals; no runtime reset or new engine.',
      'cost_currency':'source reads/writes/unit moves; finite-control and historical backing remain separate',
      'complete_reduced_difference':'Delta_N + Delta_shell + 14298088 Gamma + 368 Gamma E1(g) - 16 Gamma E8(g)',
      'qq16_sign':'unresolved: geometric E1/E8 and complete nonchild/shell prices required; stop fixed-mechanism recovery expansion',
      'new_physical_tapes':0,'runtime_resets':0,
      'unchanged_kappa':'836330098538459/500000000000000000',
      'physical_receipt_sha256':sha(canonical(execution)),
      'bill_sha256':sha(canonical(bill)),
      'authenticated_inputs':{k:sha(v) for k,v in sorted(pins.items())},
      'local_seals':seals,
      'remaining':['Inherited successful source/native/Ordinary/Compact/hosting, exact grid/range, row-stock/depth and long-record hypotheses.',
        'No production O73, full RootLayer.run, full nonleaf native root, all-node substitution, supplier/bootstrap or new exponent execution/proof.',
        'No-escaped numerical handles is an ownership premise, not inferred from empty live sets.',
        'A source-action theorem does not prove equal wall time or equal per-role historical backing.',
        'Read-only assisted review shares sources/checkers; no independent human or formal-kernel acceptance.']}
    return dict(zip(NAMES,(result,bill,execution)))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    need(not(args.write and args.check_only),'exclusive replay mode')
    if args.write:need(not any((HERE/n).exists() for n in NAMES),'refuse receipt overwrite')
    runtime,pins,seals=bootstrap()
    saved=parse((HERE/'EXECUTION.json').read_bytes()) if args.check_only else None
    objects=compute(runtime,pins,seals,saved_execution=saved)
    for name,obj in objects.items():
        if args.write:
            with (HERE/name).open('x') as stream:stream.write(json.dumps(obj,sort_keys=True,indent=None if name=='EXECUTION.json' else 2,allow_nan=False)+'\n')
        else:check_receipt(name,obj)
    print(STATUS+'_CHECK_ONLY' if args.check_only else STATUS)
if __name__=='__main__':main()
