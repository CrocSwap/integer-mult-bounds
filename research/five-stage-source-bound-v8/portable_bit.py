#!/usr/bin/env python3
"""Fresh portable BIT preparation, physical record and global phase lowering.

Package layout: loader/{source_loader.py,raw_ledger.py,source_inputs/...},
code/{five_stage_source471_physical_telescope_20261009.py,
five_stage_bit_global_lowering_20261009.py,
five_stage_bit_global_lowering_geometry_20261009.py}.

No saved result receipt is read. Small fixed source/digest expectations bind the
new output to the reviewed finite word. The caller owns full scalar/prime audits.
All global cover expansion MUST be phase-major, with a barrier after each phase.
"""
from array import array
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from pathlib import Path
import hashlib, importlib.util, inspect, io, json, sys, time

if not __debug__:
    raise SystemExit('refusing optimized Python: exact checks require assertions')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
CODE_HASHES={
 'five_stage_source471_physical_telescope_20261009.py':'5c28c44e10548c234f8b3454e91c1f34695a20559ce6ff8ced009db6bcbbaf58',
 'five_stage_bit_global_lowering_20261009.py':'2f4fd25eebbfdfbf37e2375e23b4827fda62776dff3b3b64e971dd215b2664bc',
 'five_stage_bit_global_lowering_geometry_20261009.py':'4a619e5d40c05295ef83183ee0d11bee12d0053bab2596ec9cfcd7fea4936157'}
SOURCE='0cbec81a11e758156e9303f63dc8c617601da69523073fdf2a77394d76acf56a'
SCALAR='e74e43692685ad5f716b41b363acb8b443c2c90096634a55f0e3728980713944'
TAGGED='614f19da4288021cd5c10a575ec7759c069962a6030bf30edb047573ed76edf6'
PROGRAM='438a0290268c1f7bc96828ba7a6ce92e05317ca5553264137f3ca9c1dd5fc543'
FINGERPRINT='e51978b8c119a5ab690efe3faffa483865b8215e2100aa77f94dffadf79a71bf'
CATEGORIES=('center','cleanup_gate','dirty_read','forward_gate','gauge_mix','inject',
 'partner_cleanup','partner_delivery','partner_mix','side_root','terminal_post',
 'terminal_pre','terminal_write','uninject')
sha=lambda b:hashlib.sha256(b).hexdigest()

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def phase_major_templates(lower):
    """Yield (name,index,callable) phases; expand every cover class per phase.

    Never call the complete flattened template once per cover class. The rho
    and tau owners can differ between phases, so that class-major order is not
    a legal execution of the proved global program.
    """
    for stage in range(5):
        yield ('helper',stage,lambda s=stage:lower.iter_stage(s))
        if stage in(1,2,4):
            i={1:0,2:1,4:2}[stage]
            yield('idle',i,lambda i=i:lower.iter_idle(i))
            yield('bridge',i,lambda i=i:lower.iter_bridges(i))
    yield('completion',0,lower.iter_completions)
    yield('terminal_exchange',0,lower.iter_exchanges)

def runtime_context(context):
    """Isolate lazy empty-read cache insertions from the canonical source data."""
    result=dict(context)
    for name in ('at','deliveries'):
        result[name]=defaultdict(list,{k:list(rows)for k,rows in context[name].items()})
    return result

def run(prepared_context=None,pr210_root=None,base_bit_root=None,run_geometry=True,
        package_root=None,code_root=None):
    """Return fresh context, compact records, Lowerer and all actual results.

    prepared_context, if supplied, must be the current pinned clean loader's
    namespace. This avoids duplicate preparation for a combined scalar/prime
    verification. No saved PASS, histogram or frame inventory is consumed.
    """
    begun=time.monotonic();package=Path(package_root or HERE).resolve()
    loader_dir=package/'loader';code_dir=Path(code_root or package/'code').resolve()
    for name,digest in CODE_HASHES.items():
        assert sha((code_dir/name).read_bytes())==digest,('changed frozen code',name)
    clean=load('source_loader',loader_dir/'source_loader.py')
    raw_module=load('portable_source471_raw_ledger',loader_dir/'raw_ledger.py')
    pr210=Path(pr210_root or loader_dir/'source_inputs/pr210')
    base=Path(base_bit_root or loader_dir/'source_inputs/base_bit')
    # Validate source bytes even when the caller provides a prepared namespace.
    clean.check_sources(pr210,base)
    context=prepared_context if prepared_context is not None else clean.prepare(pr210,base)
    fingerprint=clean.semantic_fingerprint(context)
    assert fingerprint['combined_sha256']==FINGERPRINT
    assert sha(context['SOURCE_TEXT'].encode())==SOURCE
    raw=raw_module.reconstruct(runtime_context(context))

    physical_path=code_dir/'five_stage_source471_physical_telescope_20261009.py'
    source=physical_path.read_text()
    def patch(old,new):
        nonlocal source
        assert source.count(old)==1,('physical patch boundary changed',old)
        source=source.replace(old,new)
    setup="setup=AUDIT.read_text().split('result = {')[0]\nns={'__file__':str(AUDIT),'__name__':'physical_telescope_dependency'}\nexec(compile(setup,str(AUDIT),'exec'),ns)"
    patch(setup,'ns=prepared_namespace.copy()')
    patch('caps={}','initial_state=state.copy()\ncaps={}')
    patch('subcache={}','subcache={}\nlocal_records=record_storage\nkind_ids={k:i for i,k in enumerate(category_names)}')
    patch('d=C.dimf[f]-C.dimf[old];assert d>=0',
          'd=C.dimf[f]-C.dimf[old];assert d>=0\n local_records.extend((0,i,old,f,d,0))')
    patch('else:move(y,f)','else:move(y,f)\n local_records.extend((1,x,physical_y,c,f,kind_ids[kind]))')
    patch('centers.append(center)','centers.append(center)\n local_records.extend((2,source,n,frame,ZERO,rank))')
    patch("center['after_event']=count",
          "local_records.extend((3,center['source'],n,center['frame'],ZERO,center['rank']))\n center['after_event']=count")
    patch("raw=json.loads((BASE/'retimed_source_heads_20261009/raw471_ledger.json').read_text())",
          'raw=portable_raw')
    records=array('i')
    physical_ns=dict(__file__=str(physical_path),__name__='portable_physical_source471',
        prepared_namespace=runtime_context(context),record_storage=records,category_names=CATEGORIES,portable_raw=raw)
    argv=sys.argv
    try:
        sys.argv=[str(physical_path)]
        with redirect_stdout(io.StringIO()):exec(compile(source,str(physical_path)+' [portable exact bindings]','exec'),physical_ns)
    finally:sys.argv=argv
    physical=physical_ns['result']
    assert physical['scalar_source_sha256']==SOURCE and physical['scalar_projection_sha256']==SCALAR
    assert physical['tagged_scalar_sha256']==TAGGED
    assert set(physical['categories'])==set(CATEGORIES)
    assert physical['weighted_scalar_events']==2569626
    assert physical['paid_histogram']=={int(k):v for k,v in raw['one_stage_helper_histogram_including_copies'].items()}
    assert len(records)//6==2667869
    assert len(physical['used_frames'])==26750
    assert len({r['basis_sha256']for r in physical['used_frames']})==26380

    global_path=code_dir/'five_stage_bit_global_lowering_20261009.py'
    global_module=load('portable_source471_global_lowering',global_path)
    lower=global_module.Lowerer(records,physical_ns)
    # The verified emitter is unchanged; only its one expected-ledger read is
    # replaced by the independently reconstructed current source ledger.
    verifier=inspect.getsource(global_module.verify)
    old="physical=lower.ns['result']; raw=json.loads(RAW.read_text())"
    assert verifier.count(old)==1
    verifier=verifier.replace(old,"physical=lower.ns['result']; raw=portable_raw")
    global_module.__dict__['portable_raw']=raw
    exec(compile(verifier,str(global_path)+' [fresh ledger binding]','exec'),global_module.__dict__)
    global_result=global_module.verify(lower)
    assert global_result['program_sha256']==PROGRAM
    assert global_result['paid_histogram']=={int(k):v for k,v in raw['five_stage_profile']['histogram'].items()}
    # Explicit live-result envelope for the finite accounting consumer. Counts
    # come from emitted opcodes, not a saved outer verification receipt.
    global_result.update(source_head=raw['source_head'],
        scalar_projection_sha256=physical['scalar_projection_sha256'],
        local_tagged_sha256=physical['tagged_scalar_sha256'],
        weighted_stage_additions=global_result['opcode_counts'][1],
        bridge_additions=global_result['opcode_counts'][5],
        total_weighted_additions=global_result['opcode_counts'][1]+global_result['opcode_counts'][5])
    phases=[(name,index)for name,index,method in phase_major_templates(lower)]
    assert phases==[('helper',0),('helper',1),('idle',0),('bridge',0),
        ('helper',2),('idle',1),('bridge',1),('helper',3),('helper',4),
        ('idle',2),('bridge',2),('completion',0),('terminal_exchange',0)]

    assert clean.semantic_fingerprint(context)==fingerprint, 'canonical source semantics changed during physical lowering'
    geometry=None
    if run_geometry:
        geometry_path=code_dir/'five_stage_bit_global_lowering_geometry_20261009.py'
        geometry_source=geometry_path.read_text()
        substitutions={
            "cp=BASE/'five_stage_export_plan_20261009/loader/source_loader.py'":"cp=portable_package_root/'loader/source_loader.py'",
            "ctx=CLEAN.prepare(cp.parent/'source_inputs/pr210',cp.parent/'source_inputs/base_bit')":"ctx=prepared_namespace"}
        for old,new in substitutions.items():
            assert geometry_source.count(old)==1,('geometry patch boundary changed',old)
            geometry_source=geometry_source.replace(old,new)
        geometry_ns=dict(__file__=str(geometry_path),__name__='portable_exact_geometry',
                         portable_package_root=package,prepared_namespace=context)
        argv=sys.argv
        try:
            sys.argv=[str(geometry_path)]
            with redirect_stdout(io.StringIO()):exec(compile(geometry_source,str(geometry_path)+' [shared prepared context]','exec'),geometry_ns)
        finally:sys.argv=argv
        geometry=geometry_ns['result']
        assert geometry['clean_fingerprint']==fingerprint
        assert geometry['status']=='PASS_EXACT_H24_CALLABLE_LOWERING_GEOMETRY'
    assert all(sha((code_dir/n).read_bytes())==h for n,h in CODE_HASHES.items())
    return dict(context=context,W=context['W'],C=context['C'],records=records,lower=lower,
        raw=raw,physical=physical,global_result=global_result,geometry=geometry,
        fingerprint=fingerprint,phase_major_schedule=phases,seconds=time.monotonic()-begun,
        fresh_computation_scope='Fresh source preparation, raw paths, all local physical tags, full global instruction stream and optional exact geometry. Caller performs original-source and independent all-column scalar/prime audits; no saved result receipt is read.')

def summary(result):
    return dict(status='PASS_PORTABLE_FRESH_BIT_PHYSICAL_AND_GLOBAL',
        source_head=result['raw']['source_head'],fingerprint=result['fingerprint'],
        local_record_count=len(result['records'])//6,
        scalar_projection_sha256=result['physical']['scalar_projection_sha256'],
        physical_tagged_sha256=result['physical']['tagged_scalar_sha256'],
        global_result=result['global_result'],geometry=result['geometry'],
        phase_major_schedule=result['phase_major_schedule'],
        seconds=result['seconds'],scope=result['fresh_computation_scope'])

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr210-root',type=Path);parser.add_argument('--base-bit-root',type=Path)
    parser.add_argument('--package-root',type=Path);parser.add_argument('--code-root',type=Path)
    parser.add_argument('--skip-geometry',action='store_true')
    args=parser.parse_args()
    print(json.dumps(summary(run(pr210_root=args.pr210_root,base_bit_root=args.base_bit_root,
        run_geometry=not args.skip_geometry,package_root=args.package_root,code_root=args.code_root)),sort_keys=True))
