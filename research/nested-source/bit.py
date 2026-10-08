#!/usr/bin/env python3
"""Exact h32 source-frame + nested-basis bit moment.

Counts for the h32 producer are supplied externally (PR11) and must receive
its full finite audit before this moment is a multiplication bound.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from controlled_bit_rank_moment import counts as old_counts
from batched_bit_rank_moment import rational_log_bounds,serializable

def log_bounds(x):
    x=Q(x); k=0
    while x>2:x/=2;k+=1
    lo,hi=rational_log_bounds(x);l2,h2=rational_log_bounds(2)
    return lo+k*l2,hi+k*h2

def counts(h=32,roles=25224960,nested=True):
    n=old_counts(h,roles);H=h*h;m=h**3;B=n['v']**2*roles;N=n['N']
    # Remove source-frame D0 entrance, replace old sink (H and m-2H)
    # by h corner singles and m-2h middle, then apply new data/A3 blocks.
    n['singleton_calls']-=(H-2*h)*B+(2*H-6*h+4)*2*N
    blocks=[dict(name='stage13_join_middle',chunk_digits=m-4*h,copies=B),
            dict(name='stage2_translated_sink_middle',chunk_digits=m-2*h,copies=B),
            dict(name='stage3_data_middle',chunk_digits=m-2*H-2*h+2,copies=2*N),
            dict(name='stage2_data_entrance_middle',chunk_digits=H-4*h+2,copies=2*N),
            dict(name='stage3_data_corner_middle',chunk_digits=H-2*h+2,copies=2*N)]
    if nested:
        n['singleton_calls']-=h*B
        blocks.append(dict(name='nested_stage2_translated_sink_corner',chunk_digits=h,copies=B))
    n['retained_PR10_bulk_classes']=n.pop('bulk_classes')
    n['recursive_blocks']=blocks
    assert n['singleton_calls']>0
    assert n['singleton_calls']+sum(x['copies']*x['chunk_digits'] for x in blocks)==n['original_rank_sum']
    n['nested']=nested
    return n

def certificate(a=Q(196,10**8),h=32,roles=25224960,nested=True):
    n=counts(h,roles,nested);W=n['W'];m=n['m']
    ratios=[Q(1,m)]+[Q(x['chunk_digits'],m) for x in n['recursive_blocks']]
    weights=[Q(n['singleton_calls'],W*m)]+[Q(x['copies']*x['chunk_digits'],W*m) for x in n['recursive_blocks']]
    logs=[log_bounds(1/x) for x in ratios]
    assert sum(weights)==1-n['eta']
    assert all(0<=a*u<1 for l,u in logs)
    upper=sum((w/(1-a*e[1]) for w,e in zip(weights,logs)),Q(0))
    slope_lower=sum((w*e[0] for w,e in zip(weights,logs)),Q(0))
    assert upper<1
    return dict(status='EXACT NESTED-BASIS BIT MOMENT; FULL H32 PRODUCER AND GLOBAL ASSEMBLY AUDIT REQUIRED',
                a_b=a,tau=1-a,counts=n,ratios=ratios,weights=weights,log_enclosures=logs,
                moment_upper=upper,strict_gap=1-upper,strict_saving_upper=n['eta']/slope_lower,
                above_two_to_minus_19=a>Q(1,2**19),
                dependencies=['PR13 source-frame translation','PR7/PR11 h32 five-subset finite producer with roles25224960',
                              'PR10 controlled basis and mixed-width finite tape interface',
                              'New data-entrance, A3-corner and nested-controlled-basis lemmas'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args()
    out=json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(out)
    print(out,end='')
