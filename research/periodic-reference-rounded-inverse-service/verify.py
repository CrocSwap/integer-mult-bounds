#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Actual complete periodic service, original-source residual and controls."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
from service import Plan,prepare,execute,up,digest,need


def authenticate():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],
                 'source pin '+item['path'])


def reject(action,label):
    try:action()
    except (ValueError,TypeError):return label
    raise ValueError('control accepted: '+label)


def residual(reference,data,answer,bits):
    # Independent dense column enumeration of original entries, no quantized table.
    n=reference.target_size;s=1<<bits;maximum=Q(0)
    for row in range(n):
        real=-Q(data[row][0],s);imag=-Q(data[row][1],s)
        for col in range(n):
            a=reference.entry('narrow',row,col).value
            if a:
                real+=a*Q(answer[col][0],s);imag+=a*Q(answer[col][1],s)
        maximum=max(maximum,up(abs(real)+abs(imag)))
    return maximum


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',type=Path);args=parser.parse_args()
    start=time.monotonic();authenticate()
    expected=None
    if args.record is None:
        expected=json.loads((HERE/'RESULT.json').read_text())
        need(all(type(v)is int for section in ('bill','setup')
                 for v in expected[section].values()),'integer receipt fields exclude booleans')
    sys.path.insert(0,str(ROOT/'research/rational-unitary-fft'))
    from gaussian_reference import Reference
    from gaussian import INTERVALS
    reference=Reference({INTERVALS:(ROOT/INTERVALS).read_bytes()},384,1,2,4,18,320)
    need(reference.description_hash=='4001280a290db7fe1afbbbed80704821796da86c3de8f86516b8debaf099591c','original reference')
    plan=prepare(reference);setup_seconds=time.monotonic()-start
    print('PREPARED',round(setup_seconds,3),file=sys.stderr,flush=True)
    need((plan.steps,plan.bits)==(276,33),'actual funded parameters')
    n=len(plan.rows);s=1<<plan.bits
    data=tuple((((i*17)%65-32)*s//64,((i*29)%65-32)*s//64) for i in range(n))
    data=list(data);data[0]=(s//2,s//2);data[-1]=(-s,0);data[192]=(s//4,-s//2);data=tuple(data)
    before=digest(data);answer,bill=execute(plan,data)
    need(digest(data)==before and len(answer)==385 and answer[192]==data[192],'borrowed input and all rows/hole')
    entries=reference.entries
    setup=dict(entry_cache=len(entries),weight_cache=len(reference.weights),kernel_cache=len(reference.kernel),
               rational_max_bits=max(max(e.value.numerator.bit_length(),e.value.denominator.bit_length()) for e in entries.values()),
               source_entry_requests=plan.source_entries,
               pi_cache_entries=reference.exp.oracle.pi_interval.cache_info().currsize,
               phase_cache_entries=reference.exp.oracle.root_of_unity.cache_info().currsize,
               max_declared_interval_bits=2*reference.weight_precision+32,
               weight_record_fields=len(next(iter(reference.weights.values()))),
               weight_rational_max_bits=max(max(v.numerator.bit_length(),v.denominator.bit_length())
                   for item in reference.weights.values() for v in item.values() if type(v)is Q))
    need(setup['entry_cache']==3457 and setup['weight_cache']==384,'complete actual coefficient setup')
    wrap=reference.entry('narrow',0,384)
    need(wrap.kind=='cross-period' and wrap.lift==-1 and wrap.value>0,'actual seam preserved')
    # All N² original entries establish support and independent residual.
    for row in range(n):
        supplied={c for c,v in plan.rows[row]}|{row}
        for col in range(n):
            a=reference.entry('narrow',row,col).value
            need(col in supplied or a==0,'all omitted entries exactly zero')
    actual=residual(reference,data,answer,plan.bits)
    error=actual/plan.gap
    need(0<error<=plan.error_bound,'original-source residual inverse certificate')
    ideal=reference.errors['narrow'];need(ideal<plan.gap,'ideal perturbation admission')
    analytic=plan.radius*ideal/(plan.gap*(plan.gap-ideal))
    need(plan.error_bound+analytic<Q(1,1<<20),'combined inherited-analytic and computed error')
    m=sum(map(len,plan.rows));steps=plan.steps-1
    need(bill['products']==2*m*steps and bill['component_roundings']==2*n*steps,'complete work count')
    width=2*plan.bits+max(0,(int(plan.state_bound)+1).bit_length())+2
    need(bill['peak_accumulator_magnitude_bits']+1<=width,'signed accumulator width')
    # Wrong-period control changes the actual returned trajectory, not just a tag.
    altered=tuple(tuple((c,v) for c,v in row if abs(i-c)<=10) for i,row in enumerate(plan.rows))
    wrong_plan=Plan(plan.reference_hash,altered,plan.bits,plan.steps,plan.radius,plan.gap,
                    plan.error_bound,plan.state_bound,plan.source_entries,plan.coefficient_degree)
    wrong,_=execute(wrong_plan,data)
    # Single exact source seam row suffices to reject this dropped-wrap control.
    def row_error(output,row):
        vals=[-Q(data[row][j],s)+sum(reference.entry('narrow',row,c).value*Q(output[c][j],s)
                                 for c in range(n)) for j in range(2)]
        return sum(map(abs,vals))/plan.gap
    need(row_error(wrong,0)>Q(1,1<<20),'dropped wrap really fails requested target')
    bad=list(answer);bad[192]=(0,0)
    need(row_error(bad,192)>Q(1,1<<20),'omitted hole output rejected')
    controls=[reject(lambda:execute(plan,list(data)),'mutable input'),
              reject(lambda:execute(plan,data[:-1]),'missing input row'),
              reject(lambda:execute(plan,((True,0),)+data[1:]),'boolean integer alias'),
              reject(lambda:execute(plan,((2*s,0),)+data[1:]),'radius overflow'),
              'dropped cross-period trajectory','missing hole output','all omitted matrix entries zero']
    # Reuse after rejected inputs; zero case needs no new scientific setup.
    zero=((0,0),)*n;returned,zero_bill=execute(plan,zero)
    need(returned==zero and zero_bill['products']==bill['products'],'reuse and zero complete trajectory')
    record=dict(status='PASS',scope='whole-period host-array inverse, conditional inherited analytic bridge; no physical tape theorem',
                plan=plan.record(),input_sha256=before,output_sha256=digest(answer),setup=setup,
                exact_residual_upper=str(up(actual)),same_reference_error_upper=str(up(error)),
                inherited_analytic_error_upper=str(up(analytic)),combined_error_upper=str(up(plan.error_bound+analytic)),
                bill=bill,signed_accumulator_width_bound=width,verification_dense_entries=n*n,
                wrap=dict(kind=wrap.kind,lift=wrap.lift,value_upper=str(up(wrap.value))),controls=controls)
    encoded=json.dumps(record,indent=2,sort_keys=True)+'\n'
    if args.record:args.record.write_text(encoded)
    else:
        need(json.dumps(record,sort_keys=True)==json.dumps(expected,sort_keys=True),'typed exact receipt mismatch')
    print(encoded,end='')
    print('RUNTIME',round(time.monotonic()-start,3),'PEAK_RSS_RAW',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,file=sys.stderr)

if __name__=='__main__':main()
