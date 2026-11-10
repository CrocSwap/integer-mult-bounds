"""Failure controls and boundary cases for current two-output services.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import json
import sys
import types

sys.path.insert(0,str(Path(__file__).resolve().parent))
from physical import A,IR,ROOT,Tape,encode_symbols
from source_binding import check_inputs,check_payload
from tables import compile_swap,source_literal,need
from fixtures import check_case,execute,encode_field,decode_field


def reject(call,fragment):
    try:call()
    except ValueError as exc:
        need(fragment in str(exc),'named failure: '+str(exc));return
    raise ValueError('negative control accepted: '+fragment)


def raw_failure(table,left,right,fragment):
    public=[Tape(left,origin=17),Tape(right,origin=29)]
    before=[t.body() for t in public];work=[Tape(origin=41),Tape(origin=53)]
    reject(lambda:A.execute_table(table,tuple(public+work)),fragment)
    need(all(t.writes==0 and t.body()==old for t,old in zip(public,before)),
         'malformed input rejection before public writes')


def main():
    check_inputs();done=[]
    def record(name):done.append(name)
    swap,_=compile_swap('SWAP');signed,_=compile_swap('SIGNED_SWAP')
    for values,name in [((-8,0),'first_component_most_negative'),((0,-8),'last_component_most_negative')]:
        allowed,result=check_case(signed,'SIGNED_SWAP',values,(2,3),(4,4))
        need(not allowed and 'overflow' in result['error'],'ordered first-operand signed guard')
        record(name)
    for op,table,xs,ys,widths,name in [
            ('SWAP',swap,(-1,0),(0,-1),(1,1),'width_one_swap'),
            ('SIGNED_SWAP',signed,(0,0),(-1,-1),(1,1),'width_one_signed_zero'),
            ('SIGNED_SWAP',signed,(1,-7),(-8,-8),(4,4),'minimum_second_operand_allowed'),
            ('SIGNED_SWAP',signed,(-3,-3),(-3,-3),(4,4),'equal_values_distinct_ports'),
            ('SIGNED_SWAP',signed,(0,-7,-1,-255),(-1,7,1,255),(1,4,2,9),'matched_heterogeneous_widths')]:
        allowed,_=check_case(table,op,xs,ys,widths);need(allowed,'boundary positive control');record(name)
    for left,right,fragment,name in [
            ((),(),'nonempty complex','empty_fields'),
            (encode_symbols((2,)),encode_symbols((2,)),'positive component','empty_components'),
            (encode_symbols((0,)),encode_symbols((0,)),'unterminated','missing_delimiters'),
            (encode_symbols((0,2)),encode_symbols((0,2)),'nonempty complex','odd_component_count'),
            ((0,1),(0,1),'codeword','partial_physical_code'),
            (encode_field((0,0),(2,2)),encode_field((0,0),(1,1)),'component shape','unequal_widths'),
            (encode_field((0,0),(2,2)),encode_field((0,0,0,0),(2,2,2,2)),'field frontier','unequal_record_counts')]:
        raw_failure(swap,left,right,fragment);record(name)
    caller=json.loads((ROOT.parents[1]/'research/p104-productive-controller/CONTROLLER.json').read_text())
    site=next(i for i,r in enumerate(caller['physical_events']) if r[0]=='SIGNED_SWAP')
    raw=tuple(caller['physical_events'][site]);fields=(raw[1]*104,raw[2]*104)
    event=IR.Event('SERVICE',fields,('outer',site,0,raw))
    need(source_literal(event,caller)[0]=='SIGNED_SWAP','actual signed source')
    reject(lambda:source_literal(IR.Event('SERVICE',(fields[0],fields[0]),event.token),caller),'distinct ordered')
    record('logical_owner_alias')
    t=Tape();admin=[Tape(origin=101+10*i,marker=A.BASE) for i in range(4)]
    reject(lambda:A.Controller((),2,(t,t),*admin,rows=None,services={},stack_class=object),'all physical ports distinct')
    record('physical_tape_alias')
    reject(lambda:source_literal(IR.Event('SERVICE',fields[::-1],event.token),caller),'ordered field binding')
    record('reversed_source_port_order')
    changed=('SWAP',)+raw[1:]
    reject(lambda:source_literal(IR.Event('SERVICE',fields,('outer',site,0,changed)),caller),'exact outer')
    record('changed_source_opcode')
    reject(lambda:source_literal(IR.Event('SERVICE',fields,('outer',site+1,0,raw)),caller),'exact outer')
    record('wrong_source_site')
    reject(lambda:source_literal(IR.Event('SERVICE',fields,('unit-fragment',event.token,event.token)),caller),'wrapper grammar')
    record('malformed_wrapper')
    reject(lambda:compile_swap('ADD'),'two-output source operation');record('unsupported_operation')
    for manifest,key,base in [('SOURCES.json','path',ROOT.parents[1]),('DEPENDENCIES.json','local_path',ROOT)]:
        rows=json.loads((ROOT/manifest).read_text())['files']
        row=next(r for r in rows if manifest=='DEPENDENCIES.json' or r['usage']=='input')
        data=(base/row[key]).read_bytes()
        reject(lambda:check_payload(data+b'\n',row,row[key]),'source byte pin')
        record('corrupt_'+manifest.split('.')[0].lower())
    source=(ROOT/'tables.py').read_text()
    mutants=[
        ('omitted_negation',"negate = op == 'SIGNED_SWAP'",'negate = False','SIGNED_SWAP',(1,1),(2,2),'permutation/sign endpoint'),
        ('wrong_output_order',"b.emit('write',0,y);b.emit('write',1,z)","b.emit('write',0,z);b.emit('write',1,y)",'SWAP',(1,1),(2,2),'permutation/sign endpoint'),
        ('omitted_overflow_guard','failure = negate and sx==1 and sz==1','failure = False','SIGNED_SWAP',(0,-8),(2,3),'signed admission iff'),
        ('early_public_write',"b.emit('write',2,z);b.emit('move',2,1)","b.emit('write',0,z);b.emit('write',2,z);b.emit('move',2,1)",'SIGNED_SWAP',(1,-8),(2,3),'rejection before either public write')]
    for name,old,new,op,xs,ys,fragment in mutants:
        need(source.count(old)==1,'unique controlled mutation')
        module=types.ModuleType('swap_mutant_'+name)
        exec(compile(source.replace(old,new),name,'exec'),module.__dict__)
        table,_=module.compile_swap(op)
        reject(lambda:check_case(table,op,xs,ys,(4,4)),fragment);record(name)
    # A literal inverse uses the same signed table with reversed ordered ports.
    original=((-7,3),(-8,7));result=execute(signed,*original,(4,4))
    need(result['error'] is None,'signed inverse first admission')
    public,work=result['public'],result['work']
    for t in work:A.retire(t)
    A.execute_table(signed,(public[1],public[0],*work))
    for t in work:A.retire(t)
    need(tuple(decode_field(t.body())[0] for t in public)==original,'literal ordered inverse restores both sources')
    record('ordered_inverse_restores')
    # All extra work is retired; the descriptor is untouched at its origin.
    work=[Tape((1,0)*10+(1,),origin=41),Tape((0,1)*7+(0,),origin=53),Tape((1,)*9,origin=67)]
    context=Tape((0,1)*33,origin=79,readonly=True);before=context.body()
    allowed,result=check_case(signed,'SIGNED_SWAP',(3,-7),(-8,7),(4,4),work=work,contexts=(context,))
    need(allowed and context.body()==before and context.writes==0,'complete dirty-work and protected-context contract')
    record('dirty_work_extra_inventory_and_context')
    # The unchanged table executor alone does not erase encoded work.
    public=[Tape(encode_field(v,(4,4)),origin=17+12*i) for i,v in enumerate(((2,-2),(3,-3)))]
    work=[Tape(origin=41),Tape(origin=53)];A.execute_table(swap,tuple(public+work))
    need(any(not t.blank() for t in work),'omitted retirement detected');record('omitted_physical_retirement')
    warm=execute(swap,(1,-1)*64,(2,-2)*64,(32,)*128)['work'];old_backing=[t.highwater for t in warm]
    _,small=check_case(signed,'SIGNED_SWAP',(0,-1),(-4,3),(3,3),work=warm)
    _,fresh=check_case(signed,'SIGNED_SWAP',(0,-1),(-4,3),(3,3))
    need((small['actions'],small['steps'])==(fresh['actions'],fresh['steps'])
         and [t.highwater for t in warm]==old_backing,'current-volume warm reuse without historical rescan')
    record('shrinking_call_retained_backing')
    result=execute(signed,(1,-8),(2,3),(4,4))
    need(result['error'] and any(t.pos!=t.origin for t in result['public']+result['work'])
         and any(not t.blank() for t in result['work']),'immediate reject has no physical rollback')
    record('explicit_rejection_cleanup_boundary')
    result=dict(check='controls',count=len(done),controls=done,small_fresh_actions=fresh['actions'],
                small_fresh_table_steps=fresh['steps'],retained_highwater=old_backing)
    need(result==json.loads((ROOT/'RESULT.json').read_text())['controls'],'committed exact control receipt')
    print(json.dumps(result,sort_keys=True));print('PASS_CURRENT_SWAP_FLAT_TABLES_CONTROLS')


if __name__=='__main__':main()
