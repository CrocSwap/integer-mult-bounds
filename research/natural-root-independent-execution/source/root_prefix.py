"""Generate the root descriptors before the exact retained recursive core.

Only assembly sees Python arithmetic. Execution is a single literal fixed-tape
program, using the exact old core plus statically linked prefix and cleanup.
Root inputs are T,R_body,w,unary depth and the complete payload; no A,R,H is
supplied. Standard multiplication/power methods retain predecessor credit.
thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
import gzip
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('root_retained_recursive',HERE/'inputs/core/recursive.py')
R=importlib.util.module_from_spec(spec);sys.modules[spec.name]=R;spec.loader.exec_module(R)
m=R.m


def constant_program(value):
    a=m.Assembler(1);fail=a.fresh('bad_positive_root_descriptor')
    R.multiply_constant(a,0,value,fail,'root_fixed_multiplier')
    a.halt();a.label(fail);a.reject('canonical positive root multiplication input')
    return a.finish()


def builder(low,q,dimension,tapes):
    b=R.Builder(low,q,dimension);b.a=m.Assembler(tapes)
    b.fail=b.a.fresh('invalid_root_descriptor_contract')
    return b


def prefix(low,q,dimension,coremeta,tapes):
    b=builder(low,q,dimension,tapes);a=b.a;p=b.p
    source_T,source_body=tapes-2,tapes-1
    # The reserved return role is unused before entering the old core. Borrow
    # it only for this prefix and retire it before the exact entry handoff.
    dummy_lh=b.return_role
    done=a.fresh('root_A_initial')
    b.copy(source_T,p['repeats_input'],source_marker=R.BASE)
    b.body(source_T,R.BASE);b.body(p['repeats_input'])
    # A positive dummy LH makes the unchanged shape producer deliver quotient
    # one and exactly H*R_input; no new unit-cost variable multiplication.
    b.copy(b.high,dummy_lh,source_marker=R.BASE);b.body(b.high,R.BASE);b.body(dummy_lh)
    b.logical(constant_program(low),{0:dummy_lh},done,'constant_LH');a.label(done)

    def product(source,target,label):
        after=a.fresh(label+'_delivered')
        mapping={0:dummy_lh,1:b.high,2:source,3:b.grant_a,4:target,
                 5:p['repeats'],6:p['block'],7:b.r_guide,8:p['binary_work']}
        b.logical(R.P.build(low),mapping,after,label);a.label(after)
        b.retire(b.grant_a)
        for t in (p['repeats'],p['block'],b.r_guide,p['binary_work']):b.retire(t)

    product(source_body,p['block_input'],'root_R')
    loop,more,finished=(a.fresh(x)for x in ('root_depth','root_A_step','root_descriptors_ready'))
    a.label(loop);a.branch(b.depth,{R.O:more,R.BL:finished},b.fail)
    a.label(more)
    product(p['repeats_input'],b.grant_r,'root_A_times_H')
    b.retire(p['repeats_input']);b.copy(b.grant_r,p['repeats_input'])
    b.body(p['repeats_input']);b.retire(b.grant_r)
    multiplied=a.fresh('root_A_times_L')
    b.logical(constant_program(low),{0:p['repeats_input']},multiplied,'constant_L');a.label(multiplied)
    a.move(b.depth,1);a.goto(loop)
    a.label(finished);b.mark('root_depth_restore');b.origin(b.depth,R.BASE)
    b.mark('root_depth_restored');b.retire(dummy_lh)
    # Every temporary has been physically erased before the old node-entry.
    b.mark('root_descriptor_handoff')
    a.halt();a.label(b.fail);a.reject('positive root T/body/width/depth and blank owned descriptors')
    return a.finish(),dict(b.events)


def cleanup(low,q,dimension,tapes):
    b=builder(low,q,dimension,tapes)
    for t in (b.p['repeats_input'],b.p['block_input']):b.retire(t)
    b.a.halt();b.a.label(b.fail);b.a.reject('owned root descriptors at final cleanup')
    return b.a.finish()


def relocate(program,offset,halt):
    rows=[]
    for row in program.instructions:
        op=row[0]
        if op=='branch':rows.append((op,row[1],tuple((v,k+offset)for v,k in row[2]),row[3]+offset))
        elif op=='goto':rows.append((op,row[1]+offset))
        elif op=='halt':rows.append(('goto',halt)if halt is not None else row)
        else:rows.append(row)
    return rows


def build(low=4,q=3,dimension=1):
    old,meta=R.build(low,q,dimension);tapes=old.tapes+2
    if (low,q,dimension)==(4,3,1):
        retained=json.loads(gzip.decompress((HERE/'inputs/core/TABLE.json.gz').read_bytes()))
        actual=json.loads(json.dumps({'instructions':old.instructions,'tapes':old.tapes,'entry':old.entry}))
        m.need(actual==retained['program'] and json.loads(json.dumps(meta))==retained['metadata'],
               'exact unchanged retained core table before linking')
    before,before_events=prefix(low,q,dimension,meta,tapes);after=cleanup(low,q,dimension,tapes)
    n=len(old.instructions);cleanup_entry=n+len(before.instructions)+after.entry
    entry=meta['events']['node_entry'];handoff=entry-1
    m.need(old.instructions[handoff]==('goto',entry),'exact retained H-to-entry jump')
    halts=[i for i,row in enumerate(old.instructions)if row[0]=='halt']
    m.need(len(halts)==1,'one retained final halt')
    rows=list(old.instructions)
    rows[handoff]=('goto',n+before.entry)
    rows[halts[0]]=('goto',cleanup_entry)
    rows+=relocate(before,n,entry)
    rows+=relocate(after,n+len(before.instructions),None)
    changed=[i for i,row in enumerate(old.instructions)if rows[i]!=row]
    m.need(changed==[handoff,halts[0]],'only the two declared entry/halt links change')
    info={**meta,'tapes':tapes,'T_input':tapes-2,'R_body_input':tapes-1,
          'core_tapes':old.tapes,'core_instructions':len(old.instructions),
          'root_prefix_instructions':len(before.instructions),'root_cleanup_instructions':len(after.instructions),
          'core_link_changes':[{'pc':i,'old':old.instructions[i],'linked':rows[i]}for i in changed],
          'root_events':{k:n+v for k,v in before_events.items()}}
    return m.Program(tuple(rows),tapes,old.entry),info
