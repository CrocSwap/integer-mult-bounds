"""Bounded source-lifetime replay, no accelerated native claim. Apache-2.0.
Prepared for Jerry Chen / CubeJerry with OpenAI assistance.
"""
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import argparse
import random
from lifetime import FieldPool, NativeWindow, literal_caller, source_jobs, sources, require

ROOT=Path(__file__).resolve().parent

def normalized(lease, request):
    for stride in request['strides']:
        for start in range(0,len(lease),2*stride):
            for lo in range(start,start+stride):
                hi=lo+stride
                a,b=lease[lo]; c,d=lease[hi]
                require(not any(x%2 for x in (a+c,b+d,a-c,b-d)), 'nonintegral fixture H0')
                lease[lo],lease[hi]=((a+c)//2,(b+d)//2),((a-c)//2,(b-d)//2)

def rejected(call,text):
    try: call()
    except ValueError as error:
        require(text in str(error),'wrong rejection: '+str(error))
        return
    raise ValueError('negative control survived: '+text)

def run_case(raw,sides,P,public_bits,repetition,capacity=7,alias=False,retain_roots=True,repeat_while_held=False):
    T=prod(sides)
    jobs,hmax=source_jobs(raw,sides,P,public_bits)
    jobs=[schedule*repetition for schedule in jobs]
    rng=random.Random(20261123+T+P+repetition)
    def operand():
        return [(rng.choice((-1,1))*rng.randrange(1,1<<(P-4)),
                 rng.choice((-1,1))*rng.randrange(1,1<<(P-4))) for _ in range(T)]
    left,right=operand(),operand()
    reference,_=literal_caller(raw,sides,P,public_bits,jobs)
    expected=reference.convolution_grid(left,right)
    pool=FieldPool(T,capacity)
    window=NativeWindow(T,P,2,hmax,normalized,pool)
    machine,_=literal_caller(raw,sides,P,public_bits,jobs,pool,window,alias)
    if retain_roots:
        a0,b0=pool.make(left,'root-a'),pool.make(right,'root-b')
        result=machine.convolution_grid(a0,b0)
        require(list(a0)==left and list(b0)==right,'borrowed root alias was overwritten')
    else:
        a0=b0=None
        result=machine.convolution_grid(pool.make(left,'root-a'),pool.make(right,'root-b'))
    require(list(result)==expected,'source endpoint mismatch')
    require(pool.created==10 and pool.peak==pool.visited_slots==7,'complete-field census')
    require(len(pool.live)==3,'caller/result boundary owners')
    require(pool.cleared_records==7*T,'complete retired field scans')
    require(all(count=={1:3,2:4,3:6}[phase] for phase,count,_,_ in window.cuts),'native cut census')
    require(all(0 in ids and 1 in ids for _,_,ids,_ in window.cuts),'missing retained roots')
    require(window.scanned_records==3*T*window.calls,'complete wrapper visits')
    require(all(x==(0,0) for x in window.records),'window retirement')
    if repeat_while_held:
        # R still occupies one slot, in addition to both retained roots.
        machine.convolution_grid(a0,b0)
    answer=dict(T=T,calls=window.calls,scanned=window.scanned_records,
                h_values=sorted({x[3] for x in window.cuts}),events=pool.events[:])
    del result,a0,b0
    require(not pool.live and pool.cleared_records==10*T,'fixture final release')
    require(all(slot is None or all(x==(0,0) for x in slot) for slot in pool.storage),'historical field clearing')
    return answer

def run():
    raw=sources(ROOT)
    require(sha256(raw['tensor_word.py']).hexdigest()=='36c5a9a0082c9aa3c6cb2d04a9196af8debce0d551a0525975b710018ea02cac','literal tensor source')
    require(sha256(raw['product.py']).hexdigest()=='29ab6c60f937b7cce58666f5ddd7a921c3197cf72abf91ecca0ff7ad9486850e','literal product source')
    cases=[]
    for sides in ((2,),(4,),(8,),(2,2),(2,4),(4,2),(4,4),(2,2,2,2),
                  (2,4,2,4),(2,2,2,2,2,2,2,2),(2,2,2,2,2,4,4,4)):
        for repetition in (1,3): cases.append(run_case(raw,sides,16,8,repetition))
    controls=[]
    rejected(lambda:run_case(raw,(2,4),16,8,1,capacity=6),'complete-field capacity exceeded')
    controls.append('six_slots_omit_source_owner')
    rejected(lambda:run_case(raw,(2,4),16,8,1,alias=True),'borrowed root alias was overwritten')
    controls.append('forward_copy_aliases_caller_root')
    rejected(lambda:run_case(raw,(2,4),16,8,1,retain_roots=False),'complete-field census')
    controls.append('omit_two_caller_root_owners')
    rejected(lambda:run_case(raw,(2,4),16,8,1,repeat_while_held=True),'complete-field capacity exceeded')
    controls.append('reuse_pool_with_escaped_outer_result')
    pool=FieldPool(4); data=pool.make([(i+1,-i-1) for i in range(4)],'data'); held=[]
    def captured(lease,request):
        held.append(lease)
        normalized(lease,request)
    window=NativeWindow(4,8,2,2,captured,pool)
    window.apply(data,(1,2))
    rejected(lambda:held[0][0],'expired native window lease')
    controls.append('escaped_window_access_after_return')
    window.callback=lambda lease,request:[(0,0)]*4
    rejected(lambda:window.apply(data,(1,)),'native returned an unowned output')
    controls.append('fresh_unaccounted_native_result')
    window.callback=normalized
    rejected(lambda:window.apply([(0,0)]*3,(1,)),'incomplete native field')
    controls.append('true_volume_only_callback_field')
    T=8; FB=2*T*(31+2)+2; FW=2*T*(70+2)+2
    histories=((211,0),(0,307))
    total=7*FB+FW+sum(max(v[i] for v in histories) for i in (0,1))
    simultaneous=max(7*FB,6*FB+FW+max(sum(v) for v in histories))
    require(total>simultaneous,'historical cut distinction')
    controls.append('same_time_peak_replaces_component_histories')
    old=[9]*17
    for i in range(5): old[i]=0
    require(any(old[5:]),'old dirty tail control')
    controls.append('clear_only_current_native_prefix')
    require(sha256(raw['tensor_word.py']+b'\n# altered\n').hexdigest()!=sha256(raw['tensor_word.py']).hexdigest(),'source mutation control')
    controls.append('altered_source_bytes')
    return dict(schema='direct-native-lifetime-evidence/1',status='PASS_SOURCE_LIFETIME_JOIN',
                source_files=len(raw),literal_convolution_cases=len(cases),source_peak_slots=7,
                source_constructions=10,new_source_fields=8,native_cut_counts=[3,4,6],
                native_calls=sum(x['calls'] for x in cases),complete_native_record_visits=sum(x['scanned'] for x in cases),
                complete_field_records=sum(x['T'] for x in cases),largest_field=max(x['T'] for x in cases),
                varying_pack_sizes=sorted({h for x in cases for h in x['h_values']}),
                representative_events=cases[4]['events'],rejected_controls=controls,
                scope='Source-bound caller/window ownership implication under native return and extent contracts; no native implementation or full multiplier storage theorem')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path)
    args=parser.parse_args(); result=json.dumps(run(),sort_keys=True,indent=2)+'\n'
    if args.output: args.output.write_text(result)
    print(result,end='')
