# SPDX-License-Identifier: Apache-2.0
"""Bounded actual native parent/child return cut, not a completed root run."""
from hashlib import sha256
import json
from state_model import body, need, Meter, fixed_tapes


class CompletedChildCut(Exception):
    pass


def run_cut():
    from fitted_fixture import source_fixture
    from macro_binding import ToyBinding
    from macro_code import compile_node
    from ordinary import Ordinary, unit_program
    from cardinal_counts import Count
    from records import Tape
    from words import Ring
    from session import sealed_constructors, erase_marker
    fixture=source_fixture();base=fixture.fixture_engine()
    binding=ToyBinding(base.binding.catalogue,base.binding.plans)
    topology=base.runtime.topology
    programs=tuple(compile_node(topology,binding,mode) for mode in (0,1))
    engine=Ordinary(2,binding,topology,programs,capacity=128)
    maximum,index_max=Count.literal(2),Count.literal(64)
    for bank,value in ((engine.banks[0],maximum),(engine.banks[3],index_max),
                       (engine.runtime.arena,maximum),(engine.runtime.indices,index_max)):
        bank.prepare(value)
    modulus=engine.banks[0].load(maximum);ring=Ring(modulus)
    size_value,depth_value=Count.literal(4),Count.literal(0)
    size=engine.banks[3].load(size_value);depth=engine.banks[3].load(depth_value)
    program=unit_program(engine.banks[3],ring,size,depth,binding.codes.bits)
    payload,directory=Tape(),Tape()
    for address in range(36*256):
        payload.append(((address*13)^(address>>3)^(address>>7)^0x53)&1)
    payload.rewind();initial=body(payload)
    counts=tuple(Count.literal(x) for x in (1,36,1,1,1))
    target=engine.runtime;cls=type(target)
    original_call=cls.call;original_return=cls.complete_return
    saved={};receipt={}
    def decoded(tape):
        from words import RIGHT
        digits=[]
        for bit in tape.cells[1:]:
            if bit==RIGHT:break
            need(bit in (0,1),'checker binary descriptor');digits.append(bit)
        return sum(bit<<i for i,bit in enumerate(digits))
    def call(machine,grants):
        if machine is target and not saved:
            saved['pc']=machine.pc;saved['mode']=machine.mode;saved['root']=machine.root
            saved['roles']={k:(body(t),t.head) for k,t in machine.roles.items() if k not in ('current','header')}
            granted=({grants[0].slot},{grants[1].slot,grants[2].slot})
            saved['words']=[{slot:(body(bank.words[slot].tape),bank.words[slot].head)
                             for slot in bank.live if slot not in keep}
                            for bank,keep in zip((machine.arena,machine.indices),granted)]
            saved['child_grants']=[w.slot for w in grants]
            saved['child_source']=body(machine.handoff['source'])
            saved['child_width']=decoded(grants[1].tape)
            saved['child_shape']={name:decoded(machine.handoff[name]) for name in ('old_count','rows','before','gap','suffix')}
            saved['parent_slot_labels']=[machine.context.ring.modulus.slot,machine.context.ring.one.slot,
                machine.context.cap.slot,machine.size.slot,machine.depth.slot]
        result=original_call(machine,grants)
        if machine is target and 'encoded_frame' not in saved:
            saved['encoded_frame']=dict(heads=list(machine.numerical.machine.heads),
                nonblank=[len(t) for t in machine.numerical.machine.tapes],
                sha256=sha256(json.dumps([sorted(t.items()) for t in machine.numerical.machine.tapes]).encode()).hexdigest())
        return result
    def returned(machine):
        child=machine is target and not machine.root
        result=original_return(machine)
        if child:
            need(saved and machine.root==saved['root'] and machine.mode==saved['mode'] and
                 machine.pc==saved['pc']+1,'actual saved root/mode/PC restoration')
            for bank,expected in zip((machine.arena,machine.indices),saved['words']):
                need(bank.live==set(expected),'all parent numerical live identities restored')
                need(all((body(bank.words[s].tape),bank.words[s].head)==v for s,v in expected.items()),
                     'all parent numerical bytes and heads restored')
            need(all((body(machine.roles[k]),machine.roles[k].head)==v for k,v in saved['roles'].items()),
                 'all suspended parent stream roles restored except current/header')
            need(body(payload)==initial and payload.head==1,'outer borrowed root input preserved')
            child_width=saved['child_width'];extent=1<<child_width
            gap=saved['child_shape']['gap'];suffix=saved['child_shape']['suffix']
            expected=bytearray(len(saved['child_source']))
            def reverse(value):return sum(((value>>i)&1)<<(child_width-1-i) for i in range(child_width))
            for address,bit in enumerate(saved['child_source']):
                quotient,last=divmod(address,suffix);quotient,second=divmod(quotient,extent)
                quotient,middle=divmod(quotient,gap);prefix,first=divmod(quotient,extent)
                destination=((((prefix*extent+reverse(second))*gap+middle)*extent+reverse(first))*suffix+last)
                expected[destination]=bit
            need(body(machine.tape('current'))==expected,'actual child reversed-interchange endpoint')
            need(machine.numerical.machine.tapes==[{}, {0:'^'}], 'numerical frame popped to parent baseline')
            receipt.update(status='PASS_REACHABLE_NATIVE_CHILD_RETURN_CUT',
                root_width=4,root_rows=36,payload_bits=len(initial),
                native_counts=dict(machine.counts),parent_pc_before=saved['pc'],parent_pc_after=machine.pc,
                child_grants=saved['child_grants'],parent_slot_labels=saved['parent_slot_labels'],
                encoded_parent_frame=saved['encoded_frame'],codec_commands=machine.numerical.codec_counts['commands'],parent_live_slots=[sorted(x) for x in saved['words']],
                returned_bits=len(body(machine.tape('current'))),
                current_sha256=sha256(body(machine.tape('current'))).hexdigest(),
                borrowed_preserved=True,parent_words_preserved=True,parent_roles_preserved=True,
                child_endpoint_checked=True,child_width=saved['child_width'],child_shape=saved['child_shape'],
                codec_heads=list(machine.numerical.machine.heads),
                root_program_completed=False,
                scope='Observer stops immediately after first successful native child return; parent root remains active.')
            raise CompletedChildCut()
        return result
    cls.call=call;cls.complete_return=returned
    meter=Meter(engine,payload,directory,program.tape,*counts,maximum,index_max,size_value,depth_value)
    try:
        with sealed_constructors():
            target.run(payload,directory,program.tape,modulus,size,depth,*counts,mode=1)
    except CompletedChildCut:
        receipt['actions_to_completed_cut']=list(meter.delta())
        # This retires the stopped parent at an actual completed primitive
        # boundary. It is explicit disposal, not completion of its root program.
        before_cleanup=meter.delta()
        target.close_frame();target.finish(0)
        ring.close();engine.banks[0].free(modulus)
        engine.banks[3].free_many(size,depth)
        for bank in engine.banks:bank.erase_owned()
        for tape in (*engine.pool.tapes,engine.output):erase_marker(tape)
        program.tape.clear();payload.clear();directory.clear()
        for value in (*counts,maximum,index_max,size_value,depth_value):value.close()
        receipt['explicit_retirement_actions']=[a-b for a,b in zip(meter.delta(),before_cleanup)]
        receipt['retired_after_completed_cut']=bool(target.closed and all(not bank.live and not bank.initialized
            for bank in (*engine.banks,target.arena,target.indices)))
        need(receipt['retired_after_completed_cut'],'explicit stopped-parent retirement')
        from words import BLANK
        need(all(all(symbol==BLANK for symbol in tape.cells) and tape.head==1 for tape in fixed_tapes(engine)),
             'all native fixture engine roles blank at canonical heads after explicit retirement')
        receipt['all_engine_roles_retired']=True
        return receipt
    finally:
        cls.call=original_call;cls.complete_return=original_return
    raise ValueError('expected actual nonleaf native child return')
