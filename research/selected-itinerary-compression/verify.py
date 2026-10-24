"""Independent source Cursor, full emitted word, and physical recursive replay."""
import argparse
from contextlib import contextmanager
from dataclasses import replace
from hashlib import sha256
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHYSICAL = 'research/selected-bit-physical-caller'
sys.path.insert(0, str(HERE))
from itinerary import need, frozen, compiler, Sink, PlanIndex

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
        need(message in str(error), 'wrong rejection: '+str(error))
        return
    raise ValueError('control accepted: '+message)


def controls(source, digest):
    import macro_code
    from macro_code import Residual
    from plan import Plan, Command, Reference
    from residual_blocks import Cursor
    from itertools import product
    # Enumerate independently using the original Cursor, not our rank formula.
    cases = blocks = 0
    for width in range(5):
        for kinds in product(('add','sign','child'), repeat=width):
            plan=Plan(2,1,False,tuple(Command(k,0,1,Reference('unit')) for k in kinds))
            cursor=Cursor(plan); expected=[]
            while not cursor.done: expected.append(cursor.take())
            indexed=PlanIndex.build(plan)
            need([indexed.at(i) for i in range(indexed.count)]==expected, 'independent Cursor enumeration')
            cases+=1; blocks+=len(expected)
    plan=Plan(2,1,True,()); cursor=Cursor(plan)
    need([PlanIndex.build(plan).at(i) for i in range(3)]==[cursor.take() for _ in range(3)],'good Cursor')
    definition=Residual(0,plan,0,True,((1,0),(0,1)))
    def sink():
        result=Sink([('node',)]);result.append(('residual_begin','idle',definition));return result
    bad=sink();rejected(lambda:bad.append(('block',replace(definition),('forward',0,0))),'source block mismatch')
    bad=sink();rejected(lambda:bad.append(('block',definition,('good',1,0))),'source block mismatch')
    bad=sink();rejected(lambda:bad.append(('residual_end','idle',definition)),'missing block')
    bad=sink();rejected(lambda:bad.append(('residual_end','other',definition)),'end identity')
    bad=sink();rejected(lambda:bad.append(('return',)),'operation inside residual')
    rejected(lambda:sink().finish(),'unterminated residual')
    rejected(lambda:PlanIndex.build(replace(plan,commands=[])),'mutable plan field')
    good=sink()
    for i in range(3):good.append(('block',definition,PlanIndex.build(plan).at(i)))
    good.append(('residual_end','idle',definition));word=good.finish()
    object.__setattr__(plan,'rank',0)
    rejected(lambda:word[2],'plan mutation')
    object.__setattr__(plan,'rank',1)
    changed=source.replace(b'operations = [("node",)]',b'operations = list((("node",),))')
    rejected(lambda:compiler(macro_code,changed,digest),'emitter source hash')
    rejected(lambda:compiler(macro_code,changed,sha256(changed).hexdigest()),'unsupported emitter shape')
    for key in (-len(word)-1,len(word)):
        try: word[key]
        except IndexError: pass
        else: raise ValueError('out-of-range accepted')
    try: word[1.2]
    except TypeError: pass
    else: raise ValueError('non-index accepted')
    need(word[-1]==word[len(word)-1] and word[::-1]==tuple(word)[::-1] and word[True]==word[1], 'tuple index behavior')
    return dict(cursor_cases=cases+1,cursor_blocks=blocks+3,rejecting_controls=10,index_boundary_controls=4)


@contextmanager
def fixture(single=False, replicas=1):
    import check_nested_model as model
    from macro_binding import ToyBinding
    from cardinal_counts import Count
    from directory import Context
    from words import Arena, Ring
    catalogue=model.Catalogue()
    if single:
        class SingleCodes(model.ToyCodes):
            def __init__(self):
                super().__init__();self.size,self.limit,self.bits=2,8,3
        catalogue.codes=SingleCodes()
        catalogue.low_classes=lambda: (catalogue.codes.unrank(i) for i in range(2))
    class Topology(model.Topology):
        def call(self,stage,replica):
            base=super().call(stage,0)
            return replace(base,owners=tuple(replace(owner,family=replica) for owner in base.owners))
    topology=Topology(catalogue);topology.families=topology.replicas=replicas
    arena,indices=Arena(3),Arena(8)
    modulus=arena.input(2);ring=Ring(modulus);context=Context(ring,catalogue.codes)
    plans=model.compile_coefficients(catalogue,context,indices,model.UnitIncoming(context))
    class Binding(ToyBinding):
        def check_stock(self,runtime):
            expected=Count.literal((2 if runtime.root else 1) if single else (6 if runtime.root else 1))
            try:need(expected.equals(runtime.count('unused')),'fixture independent fresh stock')
            finally:expected.close()
    binding=Binding(catalogue,plans)
    context.close();ring.close()
    try:yield topology,binding,arena,indices,modulus
    finally:
        arena.free(modulus)
        need(not arena.live and not indices.live,'closed fixture banks')


def full_word(source,digest):
    import macro_code
    receipts=[]
    with fixture(replicas=2) as (topology,binding,*_):
        for mode in (0,1):
            emitted=[]
            compact=compiler(macro_code,source,digest,emitted.append)(topology,binding,mode)
            need(len(compact.operations)==len(emitted),'same complete PC domain')
            # This tee captures the ORIGINAL emitted tuples with identical wrappers.
            for pc,old in enumerate(emitted):
                got=compact.operations[pc]
                need(got==old,'full word equality')
                if old[0]=='block':need(got[1] is old[1],'original block identity')
                if old[0] in ('residual_begin','residual_end'):need(got[2] is old[2],'original boundary identity')
            # A separate unmodified emitter call checks values/order and source globals.
            before=macro_code.compile_node(topology,binding,mode)
            # Residual constants are immutable mapping proxies, outside frozen(plan).
            def semantic(operation):
                result=[]
                for x in operation:
                    if hasattr(x,'plan'):
                        result.append((x.code,frozen(x.plan),x.identifier,x.common,x.low,x.axis,tuple(sorted((repr(k),v) for k,v in x.constants.items()))))
                    else:result.append(x)
                return tuple(result)
            need([semantic(x) for x in before.operations]==[semantic(x) for x in compact.operations],'independent whole original emitter')
            receipts.append(compact.operations.census())
    return receipts


def recursive(compact,source,digest):
    import macro_code
    from macro_machine import Machine
    from cardinal_counts import Count
    from records import Tape
    from words import Arena, BLANK
    from check_runtime import destination
    from check_support import no_decode
    import scheduler
    def body(tape):return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))
    with fixture(single=True) as (topology,binding,arena,indices,modulus):
        emit=compiler(macro_code,source,digest) if compact else macro_code.compile_node
        programs=tuple(emit(topology,binding,mode) for mode in (0,1))
        size,depth=indices.input(4),indices.input(0)
        source_tape,directory,program=Tape(),Tape(),Tape()
        for i in range(1024):source_tape.append(((i*13)^(i>>3)^(i>>7)^0x53)&1)
        source_tape.rewind();original=body(source_tape)
        counts=[Count.literal(v) for v in (1,4,1,1,1)]
        count_inputs=[(body(c.tape),c.tape.head) for c in counts]
        runtime=Machine(binding,topology,programs,Arena(3,512),Arena(8,512))
        saved=[];returns=[];pending=[]
        call=Machine.call;complete=Machine.complete_return
        def traced_call(self,grants):
            continuation=(self.mode,self.pc+1)
            pending.append(continuation);saved.append(continuation)
            return call(self,grants)
        corruptions=[]
        def continuation(self,expected):
            need((self.mode,self.pc)==expected,'actual physical restored PC')
        def traced_return(self):
            root=self.root;answer=complete(self)
            if not root:
                actual=(self.mode,self.pc);expected=pending.pop()
                continuation(self,expected)
                if compact and not corruptions:
                    self.pc-=1
                    rejected(lambda:continuation(self,expected),'actual physical restored PC')
                    corruptions.append((self.mode,self.pc));self.pc+=1
                returns.append(actual)
            return answer
        def forbidden(*args,**kwargs):raise ValueError('logical Invocation forbidden')
        with no_decode(),patch.object(scheduler.Invocation,'__init__',forbidden),patch.object(Machine,'call',traced_call),patch.object(Machine,'complete_return',traced_return):
            output=runtime.run(source_tape,directory,program,modulus,size,depth,*counts,mode=1)
        actual=body(output);expected=bytearray(1024)
        for row in range(4):
            for address in range(256):expected[row*256+destination(address,4,2,(1,1,1,1))]=original[row*256+address]
        need(actual==expected,'independent complete recursive endpoint')
        need(saved and len(saved)==len(returns) and all(pc>0 for _,pc in returns) and not pending,'nonzero continuations')
        need(body(source_tape)==original and not body(directory) and not body(program),'borrowed root streams')
        need(all(t.head==1 for t in (source_tape,directory,program,output)),'borrowed root heads')
        need([(body(c.tape),c.tape.head) for c in counts]==count_inputs,'borrowed Count values and heads')
        need(runtime.closed and not runtime.arena.live and not runtime.indices.live and runtime.geometry_state is None,'closed numerical and geometry state')
        need(runtime.numerical.machine.tapes==[{},{}] and all(all(x==BLANK for x in t.cells) for t in (*runtime.roles.values(),*runtime.handoff.values(),*runtime.pool.tapes)),'complete physical erasure')
        result=dict(payload_sha256=sha256(actual).hexdigest(),instructions=[len(p.operations) for p in programs],counts=runtime.counts,saved=saved,restored=returns,parking=runtime.numerical.machine.counts,codec=runtime.numerical.codec_counts)
        for t in (source_tape,directory,program,output):t.clear()
        for c in counts:c.close()
        indices.free_many(size,depth)
        return result


def measurement(source,digest):
    import gc,time,tracemalloc,platform
    import macro_code
    records=[]
    with fixture(replicas=64) as (topology,binding,*_):
        compact=compiler(macro_code,source,digest)
        for name,emit in (('original',macro_code.compile_node),('compact',compact)):
            gc.collect();tracemalloc.start();start=time.perf_counter()
            code=emit(topology,binding,0)
            elapsed=time.perf_counter()-start;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            records.append(dict(kind=name,seconds=elapsed,retained_bytes=current,peak_bytes=peak,instructions=len(code.operations),records=(len(code.operations) if name=='original' else code.operations.census())))
            del code
    return dict(python=sys.version,platform=platform.platform(),replicas=64,measurement='tracemalloc includes compile only, after coefficient plans and adapter construction',records=records)


def run(measure=False):
    pins=authenticate();source=(ROOT/PHYSICAL/'macro_code.py').read_bytes();digest=pins[PHYSICAL+'/macro_code.py']
    with original_modules(pins) as imports:
        result=dict(controls=controls(source,digest),full_word=full_word(source,digest))
        start=time.perf_counter();before=recursive(False,source,digest);original_seconds=time.perf_counter()-start
        start=time.perf_counter();after=recursive(True,source,digest);compact_seconds=time.perf_counter()-start
        need(before==after,'complete recursive before/after equality')
        result['recursive']=after;result['imported_sources']=len(imports)
        if measure:
            metrics=measurement(source,digest);metrics['recursive_seconds']={'original':original_seconds,'compact':compact_seconds}
            (HERE/'MEASUREMENTS.json').write_text(json.dumps(metrics,indent=2)+'\n')
    authenticate();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--measure',action='store_true');args=parser.parse_args()
    result=run(args.measure)
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True),'deterministic receipt')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
