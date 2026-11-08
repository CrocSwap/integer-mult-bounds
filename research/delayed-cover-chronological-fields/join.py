"""Statically splice the raw-field port into the unchanged #6719 root table.

The old two-site complement grammar remains its own toy endpoint. This file
adds chronological source-label pushes/pops and complete raw-field visits at
every real leaf. It does not install a numerical BIT leaf.
"""
from pathlib import Path
import importlib.util
import sys
import producer as p

_spec=importlib.util.spec_from_file_location('fields_natural_root',Path(__file__).resolve().parent/'vendor6719/root_prefix.py')
source=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=source;_spec.loader.exec_module(source)


def build(low=4,q=3,dimension=1):
    old,meta=source.build(low,q,dimension)
    code=old.tapes; tapes=old.tapes+10
    service,sm=p.build(q,dimension,2,input_markers={p.WIDTH:source.R.BASE,p.FIBRE:source.R.BASE,p.PAYLOAD:p.LEFT})
    ports={p.WIDTH:meta['width'],p.CODES:code,p.FIBRE:meta['R_body_input'],p.PAYLOAD:0}
    ports.update({role:code+role-3 for role in range(4,p.TAPES)})
    rows=list(old.instructions); hooks={}; patches=[]

    def append(program, target=None):
        offset=len(rows)
        for row in program.instructions:
            op=row[0]
            if op=='branch': rows.append((op,row[1],tuple((s,k+offset) for s,k in row[2]),row[3]+offset))
            elif op=='goto': rows.append((op,row[1]+offset))
            elif op=='halt': rows.append(('goto',target) if target is not None else row)
            else: rows.append(row)
        return offset+program.entry,offset

    def restore_instruction(a, row, continuation):
        if row[0]=='move': a.move(row[1],row[2]);a.halt()
        elif row[0]=='write': a.write(row[1],row[2]);a.halt()
        else: raise ValueError('this splice expects the actual first unit move')

    def push(a, value=None):
        fail=a.fresh('bad_code_stack'); ready=a.fresh('code_top')
        a.branch(code,{p.RIGHT:ready},fail);a.label(ready)
        done=a.fresh('pushed')
        if value is None:
            zero,one=a.fresh('call0'),a.fresh('call1')
            a.branch(meta['phase'],{p.Z:zero,p.O:one},fail)
            for label,bit in ((zero,p.Z),(one,p.O)):
                a.label(label);a.write(code,bit);a.goto(done)
        else: a.write(code,p.Z);a.goto(done)
        a.label(done);a.move(code,1);a.write(code,p.Z);a.move(code,1)
        a.write(code,p.WE);a.move(code,1);a.write(code,p.RIGHT)
        past=a.fresh('continue');a.goto(past);a.label(fail);a.reject('chronological source-code push');a.label(past)

    def pop(a):
        fail=a.fresh('bad_code_pop')
        for symbol in (p.RIGHT,p.WE,p.Z):
            yes=a.fresh('stack_symbol');a.branch(code,{symbol:yes},fail);a.label(yes)
            a.write(code,p.BL);a.move(code,-1)
        yes=a.fresh('code_low_bit');a.branch(code,{p.Z:yes,p.O:yes},fail);a.label(yes)
        a.write(code,p.RIGHT)
        past=a.fresh('pop_done');a.goto(past);a.label(fail);a.reject('chronological source-code pop');a.label(past)

    pc=meta['events']['push_begin'];a=p.m.Assembler(tapes);push(a)
    # The source event begins with its declared blank-control branch.
    branch=old.instructions[pc]
    if branch[0]!='branch': raise ValueError('actual source push entry')
    a.halt(); start,_=append(a.finish(),pc)
    # Execute the source first branch at a one-instruction relay so the hook
    # does not jump back through its own patched entry.
    relay=len(rows);rows.append(branch)
    # The final HALT position is before failure labels, so redirect every
    # newly linked jump to pc to the retained branch relay.
    for k in range(start,relay):
        if rows[k]==('goto',pc): rows[k]=('goto',relay)
    rows[pc]=('goto',start);patches.append(pc);hooks['push']=start

    pc=meta['events']['pop_end'];a=p.m.Assembler(tapes);pop(a)
    restore_instruction(a,old.instructions[pc],pc+1)
    start,_=append(a.finish(),pc+1);rows[pc]=('goto',start);patches.append(pc);hooks['pop']=start

    leaf=meta['events']['leaf'];a=p.m.Assembler(tapes);push(a,0);p.c.emit_rewind(a,code,'codes_for_consumer');a.halt()
    start,offset=append(a.finish(),0);leaf_start=start
    prefix_halts=[k for k in range(offset,len(rows)) if rows[k]==('goto',0)]
    service_offset=len(rows)
    for row in service.instructions:
        op=row[0]
        if op=='branch': rows.append((op,ports[row[1]],tuple((s,k+service_offset) for s,k in row[2]),row[3]+service_offset))
        elif op in ('write','move'): rows.append((op,ports[row[1]],row[2]))
        elif op=='goto': rows.append((op,row[1]+service_offset))
        elif op=='halt': rows.append(('goto',-1))
        else: rows.append(row)
    service_halts=[k for k in range(service_offset,len(rows)) if rows[k]==('goto',-1)]
    for k in prefix_halts: rows[k]=('goto',service_offset+service.entry)
    a=p.m.Assembler(tapes);loop,more,found=(a.fresh(s) for s in ('code_end','code_more','code_found'))
    a.label(loop);a.branch(code,{p.RIGHT:found},more);a.label(more);a.move(code,1);a.goto(loop);a.label(found)
    pop(a);restore_instruction(a,old.instructions[leaf],leaf+1)
    after,_=append(a.finish(),leaf+1)
    for k in service_halts: rows[k]=('goto',after)
    rows[leaf]=('goto',leaf_start);patches.append(leaf)
    hooks.update(leaf=leaf_start,ready=service_offset+sm['events']['ready'],service_cleanup=service_offset+sm['events']['cleanup'])

    halts=[k for k,row in enumerate(old.instructions) if row[0]=='halt']
    if len(halts)!=1: raise ValueError('one exact source final halt')
    pc=halts[0];a=p.m.Assembler(tapes);yes=a.fresh('empty_stack')
    a.branch(code,{p.RIGHT:yes},a.fresh('unused_failure'))
    # Use an explicit reject destination, including for an unmatched stack.
    fail=a.instructions[-1][3];a.label(yes);a.write(code,p.BL);a.move(code,-1)
    ok=a.fresh('marker');a.branch(code,{p.LEFT:ok},fail);a.label(ok);a.write(code,p.BL);a.halt()
    a.label(fail);a.reject('complete root code-stack retirement')
    start,_=append(a.finish());rows[pc]=('goto',start);patches.append(pc)
    a=p.m.Assembler(tapes);a.write(code,p.LEFT);a.move(code,1);a.write(code,p.RIGHT);a.halt()
    entry,_=append(a.finish(),old.entry)
    return p.m.Program(tuple(rows),tapes,entry),{**meta,'tapes':tapes,'source_tapes':old.tapes,
        'source_instructions':len(old.instructions),'service_instructions':len(service.instructions),
        'service_ports':ports,'hooks':hooks,'patches':patches,'code_stack':code},old
