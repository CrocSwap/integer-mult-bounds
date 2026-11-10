#!/usr/bin/env python3
"""Physical caller replay; host arithmetic is confined to the independent oracle.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter as Observations
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from physical_sources import need,opened


def prepared_source(mode):
    from sources import load
    from compiler import FullTensor,Hadamard,Diagonal
    from reference import FreshSemanticService,decode,root_exact,distance_squared
    dense,lower,source = load()
    C = source.e.C
    if mode == 'scalar':
        scalar = C(2,1)
        matrices,directions = [[[[scalar,0],[0,scalar]]]],[[True]]
        values = [(1,1),(-1,0)]
    else:
        scalars = ((C(2,1),C(3,-1)),(C(3,1),C(2,-1)))
        matrices = [[[[z,0],[0,z]] for z in block] for block in scalars]
        directions = [[True,False],[False,True]]
        values = [(1,1),(-1,0),(0,0),(0,0),(0,1),(0,0),(0,0),(0,0)]
    program = FullTensor(dense,lower,source,matrices,directions,
                         target=8,radius_bits=1,incoming=0)
    oracle = FreshSemanticService()
    expected,semantic_work = program.execute(values,oracle)
    target = root_exact(program,[decode(z,program.incoming) for z in values])
    error = distance_squared([decode(z,program.bits) for z in expected],target)
    need(error <= program.total_error**2 and error < program.tau**2,
         'source oracle meets complete Full target')
    result = dict(label=mode,program=program,values=values,expected=expected,
                  event_types=(Hadamard,Diagonal),allocation=program.record(),
                  semantic_work=semantic_work,oracle_work=oracle.stats,
                  root_error_squared_sha256=sha256(str(error).encode()).hexdigest())
    # Release only our preparation aliases; private program globals are retained.
    for name in ('sources','compiler','reference'):
        sys.modules.pop(name,None)
    return result


def floor_table(bases):
    table = {}
    for a,b in ((997,1000),(1,500)):
        for n in sorted(set(bases)):
            target = n**a
            lo,hi = 0,n+1
            while hi-lo > 1:
                mid = (lo+hi)//2
                if mid**b <= target:
                    lo = mid
                else:
                    hi = mid
            need(lo**b <= target < (lo+1)**b,'exact finite metadata floor certificate')
            table[(a,b,n)] = lo
    certify_table(table,bases)
    return table


def certify_table(table,bases):
    need(set(table) == {(a,b,n) for a,b in ((997,1000),(1,500)) for n in set(bases)},
         'complete finite metadata floor domain')
    for (a,b,n),root in table.items():
        need(type(root) is int and root >= 0 and root**b <= n**a < (root+1)**b,
             'exact finite metadata floor certificate')


@contextmanager
def certified_floors(bases):
    """Checker-only finite specialization; the general helper is unchanged."""
    import active_plan
    import composed_plan
    from cardinal_counts import Count
    from encoded import compare
    from router_metadata import owned
    table = floor_table(bases)
    uses,misses = Observations(),[]
    original_active,original_exposure = active_plan.floor_power,composed_plan.floor_power
    def folded(value,a,b,delegate):
        for base in sorted(set(bases)):
            if (a,b,base) not in table:
                continue
            with owned(Count.literal(base)) as (candidate,):
                if compare(value,candidate) == 0:
                    uses[(a,b,base)] += 1
                    return Count.literal(table[(a,b,base)])
        misses.append([a,b])
        return delegate(value,a,b)
    with patch.object(active_plan,'floor_power',lambda value,a,b:folded(value,a,b,original_active)), \
         patch.object(composed_plan,'floor_power',lambda value,a,b:folded(value,a,b,original_exposure)):
        yield table,uses,misses


def reject(function,part):
    try:
        function()
    except ValueError as error:
        need(part in str(error),'expected rejection reason: '+part)
        return str(error)
    raise ValueError('negative control accepted: '+part)


def actual(case,progress=False,diagnostics=True,reuse=False):
    from cardinal_counts import Count
    from check_support import bits,no_decode
    import check_composed
    from physical_controls import PreparedFull,emit_signed
    from physical_engine import FullPhysical
    from records import Tape
    from session import erase_marker
    from word_product import WordProduct
    from words import BLANK
    program,values = case['program'],case['values']
    root,visits = check_composed.fixture('standard',False)
    observations = Observations()
    owner = FullPhysical(root,WordProduct(),(lambda event:observations.update([event])) if diagnostics else None)
    prepared = PreparedFull(program,Tape,Count,case['event_types'])
    payload = Tape()
    for pair in values:
        for value in pair:
            emit_signed(payload,value,prepared.metadata['incoming_width'])
    payload.rewind()
    borrowed = (payload,prepared.code,*(value.tape for value in prepared.parameters))
    before = [(bytes(tape.cells),tape.head) for tape in borrowed]
    expected = check_composed.encode(case['expected'],program.data_width)
    aliases = []
    for private in (owner.pool.tapes[0],owner.output,owner.word.output,root.output,
                    root.router.output,root.root.current,root.root.plan.roles['precision']):
        meters = tuple((tape.meter.reads,tape.meter.writes,tape.meter.moves)
                       for tape in (*borrowed,*owner.pool.tapes))
        aliases.append(reject(lambda private=private:prepared.run(owner,private),
                              'external distinct physical Full input and metadata ports'))
        bad_count = object.__new__(Count)
        bad_count.tape = private
        replaced = (bad_count,*prepared.parameters[1:])
        aliases.append(reject(lambda replaced=replaced:owner.run(payload,prepared.code,*replaced),
                              'external distinct physical Full input and metadata ports'))
        need(meters == tuple((tape.meter.reads,tape.meter.writes,tape.meter.moves)
                            for tape in (*borrowed,*owner.pool.tapes)),
             'private port rejected before borrowed or wrapper tape traffic')
    start = time.monotonic()
    old_h,old_d = owner.h_event,owner.diagonal
    def report(kind,method,*args):
        result = method(*args)
        if progress:
            print(json.dumps(dict(event=kind,completed=owner.full_calls,
                                  elapsed_seconds=time.monotonic()-start)),file=sys.stderr,flush=True)
        return result
    owner.h_event = lambda *args:report('H',old_h,*args)
    owner.diagonal = lambda *args:report('D',old_d,*args)
    bases = (program.axes,program.data_width+program.axes,program.data_width+2*program.axes)
    meters = {}
    for tape in (*owner.private,*borrowed):
        meter = getattr(tape,'meter',None)
        if meter is None and hasattr(tape,'arena'):
            meter = tape.arena.meter
        if meter is not None:
            meters[id(meter)] = meter
    def totals():
        return {key:sum(getattr(meter,key) for meter in meters.values())
                for key in ('reads','writes','moves')}
    try:
        with certified_floors(bases) as (table,uses,misses):
            initial_actions = totals()
            with no_decode():
                returned = prepared.run(owner,payload)
            final_actions = totals()
            output = bits(returned)
            need(output == expected,'actual complete physical Full endpoint equals independent oracle')
            need(before == [(bytes(tape.cells),tape.head) for tape in borrowed],
                 'all Full borrowed payload, controls and metadata restored')
            owner.idle()
            need(owner.closed and owner.current is None and not owner.pool.live,
                 'closed complete physical Full owner')
            need(all(tape.head == 1 and all(bit == BLANK for bit in tape.cells)
                     for tape in (*owner.pool.tapes,*owner.word.pool.tapes,*owner.word.canonical)),
                 'all wrapper and exact-word owned bodies and markers erased')
            protected = reject(lambda:prepared.run(owner,payload),
                               'consume the previous compiler-boundary output')
            need(not misses,'all finite fixture floor substitutions declared')
            result = dict(status='PASS_PHYSICAL_FULL',label=case['label'],allocation=case['allocation'],
                input=values,output_sha256=sha256(output).hexdigest(),output_bits=len(output),
                source_semantic_work=case['semantic_work'],source_oracle_work=case['oracle_work'],
                root_error_squared_sha256=case['root_error_squared_sha256'],
                actual_calls=dict(owner.full_calls) if diagnostics else None,
                word_scalar_products=owner.arithmetic.products if diagnostics else None,
                word_recursion=dict(owner.word.calls) if diagnostics else None,
                wrapper_calls=dict(owner.calls) if diagnostics else None,
                passive_state=dict(word_products=owner.arithmetic.products,word_calls=dict(owner.word.calls),
                                   wrapper_calls=dict(owner.calls),program_calls=dict(owner.full_calls)),
                actual_H_backend_calls=dict(root.calls),recursive_visits=dict(visits),
                observed_delivery=dict(observations),wrapper_pool_peak=owner.pool.peak,
                word_pool_peak=owner.word.pool.peak,prepared_page_components=prepared.page_components,
                prepared_control_bits=len(bits(prepared.code)),
                private_port_inventory=len(owner.private),private_port_controls=len(aliases),
                diagnostics_enabled=diagnostics,
                physical_tape_actions={key:final_actions[key]-initial_actions[key] for key in initial_actions},
                exact_kernel='physical-ring-product.WordProduct, fixed leaf16 at every width',
                fixture='source standard q2 native binding; actual metadata plan with certified finite floors',
                finite_floor_certificates=[dict(n=n,numerator=a,denominator=b,result=value,
                                                calls=uses[(a,b,n)]) for (a,b,n),value in sorted(table.items())],
                protected_return_control=protected,
                actual_elapsed_seconds=time.monotonic()-start)
            returned.clear()
            erase_marker(returned)
            owner.idle()
            if reuse:
                with no_decode():
                    returned = prepared.run(owner,payload)
                need(bits(returned) == expected,'same physical owner completes another protected return')
                need(before == [(bytes(tape.cells),tape.head) for tape in borrowed],
                     'reused physical owner restores borrowed frames')
                owner.idle()
                need(owner.closed and owner.current is None and not owner.pool.live,
                     'reused physical owner closes its scratch')
                returned.clear()
                erase_marker(returned)
                result['same_owner_reuse'] = dict(status='PASS',output_sha256=sha256(expected).hexdigest())
        return result
    except ValueError as error:
        if ('physical complete input Euclidean radius' in str(error)
                or 'actual complete physical Full endpoint equals independent oracle' in str(error)):
            need(owner.closed and owner.current is None and not owner.pool.live,
                 'declared rejecting control closes parent ownership')
            owner.idle()
            need(before == [(bytes(tape.cells),tape.head) for tape in borrowed],
                 'declared rejecting control restores borrowed frames')
            need(all(tape.head == 1 and all(bit == BLANK for bit in tape.cells)
                     for tape in (*owner.pool.tapes,*owner.word.pool.tapes,*owner.word.canonical)),
                 'declared rejecting control restores wrapper and word scratch')
        raise
    finally:
        if owner.output.read() != BLANK:
            owner.output.clear()
            erase_marker(owner.output)
        prepared.close()
        payload.clear()
        erase_marker(payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode',choices=('scalar','tensor'),default='scalar')
    parser.add_argument('--progress',action='store_true')
    parser.add_argument('--write-result',type=Path)
    args = parser.parse_args()
    case = prepared_source(args.mode)
    if args.progress:
        print(json.dumps(dict(prepared=case['allocation'])),file=sys.stderr,flush=True)
    with opened():
        result = actual(case,args.progress)
    raw = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write_result:
        args.write_result.write_text(raw)
    print(raw,end='')


if __name__ == '__main__':
    main()
