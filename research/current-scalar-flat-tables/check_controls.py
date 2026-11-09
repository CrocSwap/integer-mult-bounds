"""Failure-detection controls for scalar source, arithmetic and physical ABI.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction
import gzip
import json
import sys
import types

sys.path.insert(0,str(Path(__file__).resolve().parent))
from tables import compile_scalar,source_literal,need
from physical import A,IR,ROOT,Tape,execute,encode_symbols,symbols_for
from source_binding import check_inputs,check_dependencies,hashes,check_payload


def reject(call, fragment):
    try:call()
    except ValueError as exc:
        need(fragment in str(exc),'named failure: '+str(exc))
        return
    raise ValueError('negative control accepted: '+fragment)


def raw_failure(table, fields, fragment):
    before=[t.body() for t in fields]
    work=[Tape(origin=101),Tape(origin=111)]
    reject(lambda:A.execute_table(table,tuple(fields+work)),fragment)
    need(all(t.body()==old for t,old in zip(fields,before)),'malformed field changed before validation')


def main():
    check_inputs()
    done=[]
    def record(name):done.append(name)
    t,_=compile_scalar('SCALE','-1/2')
    for value,width,fragment,name in [(-7,4,'inexact','inexact_negative_half'),
                                    (-1,1,'inexact','short_width_below_denominator')]:
        result=execute(t,'SCALE',(0,value),(0,0),width)
        need(result['error'] and fragment in result['error'],'late arithmetic rejects')
        need(result['public'][0].body()==result['before'][0] and result['public'][0].writes==0,
             'whole-field staged failure')
        record(name)
    tneg,_=compile_scalar('SCALE','-1')
    result=execute(tneg,'SCALE',(0,-8),(0,0),4)
    need(result['error'] and 'overflow' in result['error'],'most-negative negation rejects')
    need(result['public'][0].writes==0,'late overflow keeps target');record('late_signed_overflow')
    todd,_=compile_scalar('SCALE','1/3')
    result=execute(todd,'SCALE',(0,2),(0,0),4)
    need(result['error'] and 'quotient' in result['error'],'odd divisibility rejects');record('odd_denominator_inexact')
    for op,q,x,y,w,want in [('SCALE','-1/2',-8,0,4,4),('ADD','2',-7,7,4,7),
                           ('ADD','-1',-8,-8,4,0),('SCALE','1/16',0,0,1,0)]:
        table,_=compile_scalar(op,q);result=execute(table,op,(x,x),(y,y),w)
        need(not result['error'] and result['output']==(want,want),'endpoint-admitted edge control')
        record('edge_'+op+'_'+q+'_'+str(w))
    identity,_=compile_scalar('SCALE','1')
    raw_failure(identity,[Tape(encode_symbols((2,)))],'positive component width');record('empty_component')
    raw_failure(identity,[Tape(encode_symbols((0,)))],'unterminated');record('missing_delimiter')
    raw_failure(identity,[Tape(encode_symbols((0,2)))],'complex field');record('odd_component_count')
    raw_failure(identity,[Tape((0,1))],'codeword');record('partial_physical_code')
    add,_=compile_scalar('ADD','1')
    raw_failure(add,[Tape(encode_symbols(symbols_for((0,0),2))),
                     Tape(encode_symbols(symbols_for((0,0),1)),origin=29)],'component shape')
    record('mismatched_component_width')
    raw_failure(add,[Tape(encode_symbols(symbols_for((0,0),2))),
                     Tape(encode_symbols(symbols_for((0,0,0,0),2)),origin=29)],'field frontier')
    record('mismatched_record_count')
    # This is the actual source-token validator, including independent local
    # roles with equal numerical values versus an illegal physical alias.
    word=json.loads(gzip.decompress((ROOT.parents[1]/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    event=IR.Event('SERVICE',(778,572),('local',1,tuple(word['program'][1])))
    need(source_literal(event,word)[:2]==('ADD',Fraction(1,2)),'actual source literal')
    alias=IR.Event('SERVICE',(778,778),event.token)
    reject(lambda:source_literal(alias,word),'distinct actual');record('physical_alias')
    changed=list(word['program'][1]);changed[-2]='1/4'
    bad=IR.Event('SERVICE',event.fields,('local',1,tuple(changed)))
    reject(lambda:source_literal(bad,word),'exact current');record('altered_coefficient')
    bad=IR.Event('SERVICE',event.fields,('local',2,event.token[2]))
    reject(lambda:source_literal(bad,word),'exact current');record('wrong_source_site')
    bad=IR.Event('SERVICE',event.fields,('unit-fragment',event.token,event.token))
    reject(lambda:source_literal(bad,word),'wrapper grammar');record('malformed_wrapper')
    reject(lambda:compile_scalar('SWAP',1),'scalar operation');record('unsupported_swap_service')
    for manifest,key,base in [('SOURCES.json','path',ROOT.parents[1]),
                              ('DEPENDENCIES.json','local_path',ROOT)]:
        rows=json.loads((ROOT/manifest).read_text())['files']
        row=next(r for r in rows if manifest=='DEPENDENCIES.json' or r['usage']=='input')
        data=(base/row[key]).read_bytes()
        reject(lambda:check_payload(data+b'\n',row,row[key]),'source byte pin')
        record('corrupt_'+manifest.split('.')[0].lower())
    # Source-code mutants preserve the same retained physical executor.
    source=(ROOT/'tables.py').read_text()
    mutants=[('reversed_final_carry',
              'carry != p*sx+r*sy-odd*sq','carry != odd*sq-p*sx-r*sy',
              'SCALE','-1/2',(-8,-8),(0,0),4,(4,4)),
             ('missing_sign_extension',
              'digit(k,carry,sq,sx,sy)','digit(k,carry,sq,0,0)',
              'SCALE','1/2',(-8,-8),(0,0),4,(-4,-4))]
    for name,old,new,op,q,xs,ys,w,expected in mutants:
        need(source.count(old)==1,'unique controlled mutation')
        module=types.ModuleType('scalar_mutant_'+name)
        exec(compile(source.replace(old,new),name,'exec'),module.__dict__)
        table,_=module.compile_scalar(op,q)
        result=execute(table,op,xs,ys,w)
        need(result['error'] is not None or result['output']!=expected,'mutation must be detected')
        record(name)
    # Omitting the actual lifecycle retirement leaves both coded work bodies.
    public=Tape(encode_symbols(symbols_for((2,-2),4)))
    work=[Tape(origin=101),Tape(origin=111)]
    A.execute_table(identity,tuple([public]+work))
    need(not all(t.blank() for t in work),'missing raw retirement detected');record('omitted_physical_retirement')
    # A small call on erased warm backing must do its own current-volume work.
    warm=execute(identity,'SCALE',(1,-1)*64,(0,0)*64,32)['work']
    old_backing=[t.highwater for t in warm]
    small=execute(identity,'SCALE',(1,-1),(0,0),3,work=warm)
    fresh=execute(identity,'SCALE',(1,-1),(0,0),3)
    need(small['actions']==fresh['actions'] and [t.highwater for t in warm]==old_backing,
         'warm backing retained without rescanning erased history')
    record('shrinking_call_reuse')
    result=dict(check='controls',count=len(done),controls=done,
                small_fresh_actions=fresh['actions'],retained_highwater=old_backing)
    expected=json.loads((ROOT/'RESULT.json').read_text())['controls']
    need(result==expected,'committed exact control receipt')
    print(json.dumps(result,sort_keys=True))
    print('PASS_CURRENT_SCALAR_FLAT_TABLES_CONTROLS')


if __name__=='__main__':main()
