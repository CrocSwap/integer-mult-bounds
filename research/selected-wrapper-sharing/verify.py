"""Source-bound wrapper sharing proof controls and real reduced caller replay."""
import argparse
from contextlib import contextmanager
from dataclasses import replace
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL = 'research/selected-bit-physical-caller'
sys.path.insert(0, str(HERE))
from sharing import need, share_codes, snapshot


def authenticate():
    rows = json.loads((HERE/'SOURCES.json').read_text())['files']
    pins = {r['path']: r['sha256'] for r in rows if r['usage']=='input'}
    for name, digest in pins.items():
        need(sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'source hash mismatch: '+name)
    return pins


@contextmanager
def original_modules(pins):
    # Reuse the predecessor's same-byte hash/compile importer; loader admission
    # is intentionally outside this reduced-source runtime experiment.
    path = ROOT/'research/selected-compiler-source-bridge/independent_lifetime.py'
    spec=importlib.util.spec_from_file_location('sharing_source_importer',path)
    prior=importlib.util.module_from_spec(spec);sys.modules[spec.name]=prior;spec.loader.exec_module(prior)
    records={}
    with prior.SourceFinder(ROOT,records,{p:h for p,h in pins.items() if p.startswith(PHYSICAL+'/') and p.endswith('.py')}) as finder:
        loader=importlib.import_module('loader')
        importlib.import_module('sources').ROOT=ROOT
        codec_spec=finder.spec('bank_codec',ROOT/PHYSICAL/'inputs/pr2769/codec.py')
        codec=importlib.util.module_from_spec(codec_spec);sys.modules['bank_codec']=codec;codec_spec.loader.exec_module(codec)
        loader._active=True
        yield records


def rejected(function, message):
    try: function()
    except ValueError as error:
        need(message in str(error), 'wrong control rejection: '+str(error))
        return
    raise ValueError('control accepted: '+message)


def controls():
    from macro_code import Code, Residual
    from plan import Plan
    from macro_machine import Machine
    p=Plan(2,1,True,())
    a=Residual(7,p,0,True,((1,0),(0,1)))
    b=replace(a)
    def segment(d):return (('residual_begin','idle',d),('block',d,('good',1,0)),('residual_end','idle',d))
    code=Code((('node',),*segment(a),*segment(b),('return',)),0)
    shared, counts=share_codes((code,))
    need(counts[0]['original_wrappers']==2 and counts[0]['shared_wrappers']==1,'actual equal-key merge')
    need(shared[0].operations[1][2] is shared[0].operations[4][2], 'shared identity')
    # Field observation is invariant; allocation identity is deliberately not.
    need([snapshot(op[2]) for op in code.operations if op[0]=='residual_begin']==
         [snapshot(op[2]) for op in shared[0].operations if op[0]=='residual_begin'],'field observer')
    need(len({id(op[2]) for op in code.operations if op[0]=='residual_begin'})==2 and
         len({id(op[2]) for op in shared[0].operations if op[0]=='residual_begin'})==1,'identity observer distinguishes sharing')
    bad=list(code.operations);bad[5]=('block',replace(b),('good',1,0))
    rejected(lambda:share_codes((replace(code,operations=tuple(bad)),)),'block identity')
    bad=list(code.operations);bad[6]=('residual_end','other',b)
    rejected(lambda:share_codes((replace(code,operations=tuple(bad)),)),'end identity')
    rejected(lambda:share_codes((replace(code,operations=code.operations[:-2]),)),'unterminated')
    changed=replace(b,code=8)
    rejected(lambda:share_codes((replace(code,operations=(*segment(a),*segment(changed))),)),'changed definition')
    changed=replace(b,plan=replace(p,negative_sign=True))
    rejected(lambda:share_codes((replace(code,operations=(*segment(a),*segment(changed))),)),'changed definition')
    changed=replace(b,code=True)
    rejected(lambda:share_codes((replace(code,operations=(*segment(replace(a,code=1)),*segment(changed))),)),'changed definition')
    changed=replace(b,constants={'x':[]})
    rejected(lambda:share_codes((replace(code,operations=segment(changed)),)),'mutable definition')
    # The real geometry guard distinguishes a forged same-value block wrapper.
    fake=SimpleNamespace(geometry_state=(a,1,2,3,4))
    with Machine.geometry(fake,a) as value:need(value==(1,2,3),'actual geometry same-owner control')
    rejected(lambda:next(Machine.geometry(fake,b).gen),'one active residual geometry')
    # Both modes may have the same source key and different plans/axis programs.
    other=replace(a,axis=0)
    modes, _=share_codes((Code(segment(a),0),Code(segment(other),0)))
    need(modes[0].operations[0][2].axis is None and modes[1].operations[0][2].axis==0,'mode separation')
    rejected(lambda:share_codes((Code((*segment(a),*segment(other)),0),)),'changed definition')
    # Removing residual_end from a different runtime would expose an alias:
    # the already-active first owner now equals the second shared definition.
    with Machine.geometry(fake,shared[0].operations[4][2]) as value:
        need(value==(1,2,3),'stale geometry alias demonstrates lifecycle premise')
    return {'rejecting_controls':9,'identity_observer_is_distinguishing':True,
            'stale_geometry_alias_is_distinguishing':True,'modes_kept_separate':True}


def small_call(shared):
    import check_nested_model as model
    from macro_binding import ToyBinding
    from macro_code import compile_node
    from macro_machine import Machine
    from cardinal_counts import Count
    from directory import Context
    from records import Tape
    from words import Arena, Ring, BLANK
    from check_runtime import destination
    from check_support import no_decode
    import scheduler
    catalogue=model.Catalogue()
    class Topology(model.Topology):
        families=replicas=2
        def call(self,stage,replica):
            base=super().call(stage,0)
            return replace(base, owners=tuple(replace(o,family=replica) for o in base.owners))
    topology=Topology(catalogue)
    sa,si=Arena(3),Arena(8)
    modulus=sa.input(2);ring=Ring(modulus);context=Context(ring,catalogue.codes)
    plans=model.compile_coefficients(catalogue,context,si,model.UnitIncoming(context))
    class Binding(ToyBinding):
        def check_stock(self,runtime):
            count=Count.literal(1)
            try:need(count.equals(runtime.count('unused')),'first-range two-replica stock')
            finally:count.close()
    binding=Binding(catalogue,plans)
    low=next(catalogue.low_classes())
    mode0,mode1=(binding.residual(0,True,low,m) for m in (0,1))
    need(mode0.axis is None and mode1.axis==0 and snapshot(mode0)!=snapshot(mode1),
         'actual ToyBinding mode changes the compiled definition')
    programs=(compile_node(topology,binding,0),)
    programs,counts=share_codes(programs) if shared else (programs,None)
    context.close();ring.close()
    size,depth=si.input(2),si.input(0)
    source,directory,program=Tape(),Tape(),Tape()
    for i in range(192):source.append(((i*13)^(i>>3)^(i>>7)^0x53)&1)
    source.rewind();before_bytes=bytes(source.cells)
    cs=[Count.literal(v) for v in (1,12,1,1,1)]
    count_inputs=[(bytes(c.tape.cells).rstrip(bytes([BLANK])),c.tape.head) for c in cs]
    runtime=Machine(binding,topology,programs,Arena(3,512),Arena(8,512))
    def no_invocation(*args,**kwargs):raise ValueError('logical Invocation unexpectedly used')
    trace=[]
    runtime.observe=lambda m,kind,*args:trace.append((kind,tuple((snapshot(a) if hasattr(a,'plan') else a) for a in args),m.counts.copy()))
    with no_decode(),patch.object(scheduler.Invocation,'__init__',no_invocation):
        output=runtime.run(source,directory,program,modulus,size,depth,*cs)
    def body(t):return bytes(t.cells[1:]).rstrip(bytes([BLANK]))
    actual=body(output);expected=bytearray(192)
    for row in range(12):
        for address in range(16):expected[row*16+destination(address,2,2,(1,1))]=before_bytes[1+row*16+address]
    need(actual==expected,'independent complete first-range endpoint')
    need(bytes(source.cells)==before_bytes and source.head==1 and not body(directory) and not body(program),'borrowed ports')
    need([(bytes(c.tape.cells).rstrip(bytes([BLANK])),c.tape.head) for c in cs]==count_inputs,'borrowed Count values and heads')
    need(runtime.closed and not runtime.arena.live and not runtime.indices.live and runtime.geometry_state is None,'closed numerical/geometry state')
    need(all(all(c==BLANK for c in t.cells) for t in (*runtime.roles.values(),*runtime.handoff.values(),*runtime.pool.tapes)),'complete work tape erasure')
    receipt={'payload':sha256(actual).hexdigest(),'counts':runtime.counts,'trace':repr(trace),'parking':runtime.numerical.machine.counts,'codec':runtime.numerical.codec_counts}
    for t in (source,directory,program,output):t.clear()
    for c in cs:c.close()
    sa.free(modulus);si.free_many(size,depth)
    need(not sa.live and not si.live,'closed input banks')
    return receipt,counts


def nested_call():
    import macro_checks
    original=macro_checks.compile_node
    before=macro_checks.run()
    def compact(*args,**kwargs):
        return share_codes((original(*args,**kwargs),))[0][0]
    with patch.object(macro_checks,'compile_node',compact):
        after=macro_checks.run()
    need(before==after,'complete nested physical before/after equality')
    return after


def run():
    pins=authenticate()
    with original_modules(pins) as imports:
        result={'controls':controls()}
        before,_=small_call(False);after,sharing=small_call(True)
        need(before==after,'complete physical before/after equality')
        after['trace_sha256']=sha256(after.pop('trace').encode()).hexdigest()
        result['physical']=after;result['sharing']=sharing
        result['nested']=nested_call()
        result['imported_sources']=len(imports)
    prior=json.loads((ROOT/'research/selected-compiler-visitation-audit/EXPECTED.json').read_text())['selected_coefficients_at_N_one']
    need(prior['source_visits']==prior['distinct_keys']*prior['key_multiplicity']==904896 and prior['key_multiplicity']==32,'retained selected coefficient identity')
    result['conditional_selected_wrapper_coefficients']={'old':904896,'shared':28278,'ratio':32,'low_count_symbol':'N','source_census_replayed':False}
    authenticate()
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True),'typed deterministic receipt')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
