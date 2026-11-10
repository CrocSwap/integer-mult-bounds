#!/usr/bin/env python3
"""Source/precision verification; the physical integration has its own gate.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from sources import load,need,exact_preparation,trusted_exact_serialization
from compiler import FullTensor,Hadamard,canonical,ceil_log2,signature
from reference import (FreshSemanticService,ONE,ZERO,add,mul,decode,raw_h,
                       emitted_exact,source_plan_exact,root_exact,distance_squared)


def digest(values):
    return sha256(canonical([[str(a),str(b)] for a,b in values])).hexdigest()


def error_record(value):
    return dict(zero=value==0,log2_upper=ceil_log2(value) if value else None,
                exact_sha256=sha256(str(value).encode()).hexdigest())


def reject(function,part):
    try:
        function()
    except ValueError as error:
        need(part in str(error),'expected rejecting reason: '+part)
        return str(error)
    raise ValueError('negative control accepted: '+part)


def heterogeneous(dense,lower,source,**options):
    C=source.e.C
    matrices=[[[[2,1],[1,2]],[[3,C(1,1)],[1,3]]],
              [[[4,0],[0,4]],[[2,1],[C(0,1),2]]]]
    return FullTensor(dense,lower,source,matrices,[[False,True],[True,False]],
                      target=12,radius_bits=2,incoming=5,
                      indices=[[[0,1],[1,0]],[[1,0],[0,1]]],**options)


@exact_preparation
def case(program,inputs,label):
    rows=[]
    for number,values in enumerate(inputs):
        service=FreshSemanticService()
        output,work=program.execute(values,service)
        original=[decode(z,program.incoming) for z in values]
        actual=[decode(z,program.bits) for z in output]
        emitted=emitted_exact(program,original)
        logical=source_plan_exact(program,original)
        root=root_exact(program,original)
        need(emitted==logical,'exact global primitive word equals original source tensor')
        source_error=distance_squared(logical,root)
        arithmetic_error=distance_squared(actual,logical)
        total_error=distance_squared(actual,root)
        need(source_error<=program.source_error**2,'actual prepared tensor source error')
        need(arithmetic_error<=program.arithmetic_error**2,'actual global arithmetic error')
        need(total_error<=program.total_error**2 and total_error<program.tau**2,
             'actual complete global root target')
        rows.append(dict(input_number=number,input_sha256=digest(values),
                         exact_source_sha256=digest(logical),exact_root_sha256=digest(root),
                         rounded_output_sha256=digest(output),
                         source_error_squared=error_record(source_error),
                         arithmetic_error_squared=error_record(arithmetic_error),
                         total_error_squared=error_record(total_error),
                         source_work=work,semantic_oracle_work=service.stats))
    return dict(label=label,allocation=program.record(),trajectories=rows,
                limitation='Fresh semantic arithmetic oracle; not a physical supplier or diagonal tariff.')


def local_exact(word,values,all_one=False):
    state=list(values)
    for kind,value in word:
        if kind=='H':
            raw_h(state,[value])
        elif not all_one:
            state=[mul(z,d) for z,d in zip(state,value,strict=True)]
    return state


class WrongMask(FreshSemanticService):
    def __init__(self):
        super().__init__(); self.used=False

    def apply_h(self,state,event):
        if not self.used:
            self.used=True
            event=replace(event,positions=(event.array_bits-1,)+event.positions[1:])
        return super().apply_h(state,event)


class MissingRestoration(FreshSemanticService):
    def apply_h(self,state,event):
        super().apply_h(state,event)
        shift=1 << len(event.positions)
        for i,(a,b) in enumerate(state):
            state[i]=(int(Q(a,shift)),int(Q(b,shift)))
        return state


class WrongCoarsePages(FreshSemanticService):
    def __init__(self):
        super().__init__(); self.used=False

    def apply_diagonal(self,state,event):
        if not self.used and event.pages[0] != event.pages[1]:
            self.used=True
            event=replace(event,pages=(event.pages[0],event.pages[0]))
        return super().apply_diagonal(state,event)


def controls(dense,lower,source,program,probe,high):
    result={}
    original_signatures=[signature(word) for block in program.words for word in block]
    need(any(s != original_signatures[0] for s in original_signatures),
         'actual unpadded Full signatures differ')
    result['unpadded_actual_depths']=[list(row) for row in program.depths]
    unit=[ONE]+[ZERO]*(program.size-1)
    need(local_exact(program.idle_word,unit)==unit,'positive actual identity-padding endpoint')
    wrong=local_exact(program.idle_word,unit,all_one=True)
    need(wrong != unit,'all-one padding must not pass as identity')
    result['all_one_padding']={'wrong_first_value':[str(x) for x in wrong[0]]}
    expected=root_exact(program,[decode(z,program.incoming) for z in probe])
    for label,service in [('wrong_global_coarse_bit',WrongMask()),
                          ('missing_raw_H_restoration',MissingRestoration()),
                          ('wrong_coarse_factor_pages',WrongCoarsePages())]:
        output,_=program.execute(probe,service)
        error=distance_squared([decode(z,program.bits) for z in output],expected)
        need(error>program.tau**2,'mathematical service mutant must violate target: '+label)
        result[label]=error_record(error)
    result['underfunded_global_grid']=reject(
        lambda:heterogeneous(dense,lower,source,fractional_bits=program.bits-1),'funded global common grid')
    p=program.programs[0][0]
    page=next(value for kind,value in p.raw_stages if kind=='D')
    old=page[0]
    try:
        page[0]=source.e.C.wrap(old)+1
        result['changed_actual_source_page']=reject(program.validate,'immutable source raw pages')
    finally:
        page[0]=old
    old_directions=program.directions
    try:
        program.directions=((not old_directions[0][0],)+old_directions[0][1:],)+old_directions[1:]
        result['changed_stored_inverse_request']=reject(program.validate,'unchanged global request')
    finally:
        program.directions=old_directions
    outside=[(0,0)]*program.records
    outside[0]=((1 << (program.incoming+program.radius_bits))+1,0)
    result['actual_global_radius']=reject(lambda:program.execute(outside,FreshSemanticService()),'actual global input')
    tiny=[(1,0)]+[(0,0)]*(high.records-1)
    exact_tiny,_=high.execute(tiny,FreshSemanticService())
    need(exact_tiny==tiny and high.bits==high.incoming,'exact retained incoming-grid witness')
    need(all((int(Q(a,2)),int(Q(b,2)))==(0,0) for a,b in tiny),
         'an extra coarser input rounding loses the identity witness')
    result['incoming_grid_preserved']={'incoming':high.incoming,'exact_nonzero_numerator':1,
                                      'scope':'An uncharged input round changes the trajectory; not an impossibility theorem.'}
    prior_limit=sys.get_int_max_str_digits()
    probe_limit=sys.int_info.str_digits_check_threshold
    try:
        sys.set_int_max_str_digits(probe_limit)
        high.validate();high.record()
        need(sys.get_int_max_str_digits()==probe_limit,'successful exact hash guard restoration')
        try:
            with trusted_exact_serialization():
                need(sys.get_int_max_str_digits()==0,'trusted exact serialization context')
                raise RuntimeError('controlled preparation failure')
        except RuntimeError as error:
            need(str(error)=='controlled preparation failure','deliberate serialization failure')
        need(sys.get_int_max_str_digits()==probe_limit,'failed exact hash guard restoration')
    finally:
        sys.set_int_max_str_digits(prior_limit)
    need(sys.get_int_max_str_digits()==prior_limit,'complete incoming interpreter guard restored')
    result['trusted_exact_serialization_restored']={
        'guard_digits':probe_limit,'incoming':high.incoming,'success_and_exception_restored':True}
    path='research/rational-fft-fixed-h/dense.py'
    result['changed_retained_source_bytes']=reject(
        lambda:load({path:(HERE.parents[1]/path).read_bytes()+b'\n'}),'source SHA256')
    program.validate();high.validate()
    return result


def run():
    dense,lower,source=load()
    program=heterogeneous(dense,lower,source)
    probe=[((i*3)%11-5,(i*5)%7-3) for i in range(program.records)]
    basis=[[(1 << program.incoming,0) if i==j else (0,0)
            for i in range(program.records)] for j in range(program.records)]
    rows=[case(program,basis+[probe],'heterogeneous-two-label-two-axis')]
    high=FullTensor(dense,lower,source,[[[[1,0],[0,1]]]],[[False]],
                    target=8,radius_bits=1,incoming=16384)
    rows.append(case(high,[[(1,0),(0,0)]],'fine-incoming-identity'))
    matrices=[[[[2 if i==j else 0 for j in range(4)] for i in range(4)],
               [[3 if i==j else 0 for j in range(4)] for i in range(4)]]]
    four=FullTensor(dense,lower,source,matrices,[[False,True]],target=8,radius_bits=1,
                    incoming=3,indices=[[[3,2,1,0],[2,0,3,1]]])
    values=[(i%5-2,i%3-1) for i in range(four.records)]
    rows.append(case(four,[values],'nonconsecutive-global-mask'))
    need({e.positions for e in four.events() if isinstance(e,Hadamard)}=={(0,2),(1,3)},
         'actual higher-bit global H signatures')
    faults=controls(dense,lower,source,program,probe,high)
    trajectories=[row for group in rows for row in group['trajectories']]
    nonzero=sum(row['semantic_oracle_work']['nonzero_roundings'] for row in trajectories)
    need(nonzero>0,'actual nonzero global rounded execution')
    return dict(schema_version=1,status='PASS_FULL_GLOBAL_SOURCE',
                claim='Actual synchronized Full source and global numerical contract; physical integration separately gated.',
                summary=dict(source_families=len(rows),trajectories=len(trajectories),
                             global_H_calls=sum(row['source_work']['global_H_calls'] for row in trajectories),
                             global_diagonal_calls=sum(row['source_work']['global_diagonal_calls'] for row in trajectories),
                             observed_nonzero_roundings=nonzero,controls=len(faults),
                             physical_service_executed=False),cases=rows,controls=faults)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    result=run()
    encoded=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode()
    path=HERE/'SOURCE-RESULT.json'
    if args.write:
        path.write_bytes(encoded)
    else:
        need(path.read_bytes()==encoded,'complete deterministic source receipt')
    print(result['status'],json.dumps(result['summary'],sort_keys=True))
    print('SOURCE_RECEIPT_SHA256',sha256(encoded).hexdigest())


if __name__=='__main__':
    main()
