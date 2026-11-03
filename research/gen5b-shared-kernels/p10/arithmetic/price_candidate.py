"""Exact conditional PR320 candidate arithmetic with measured local deltas.
Original implementation. No upstream program is imported or executed.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import argparse,json
import reproduce_p10 as base

def integer_delta(value,maximum,name):
    if not isinstance(value,dict):raise ValueError(name+' must be a dictionary')
    result=Counter()
    for r,n in value.items():
        if type(r) is str and r.isascii() and r.isdigit() and str(int(r))==r:r=int(r)
        if type(r) is not int or not 1<=r<=maximum or type(n) is not int:raise ValueError(name+' requires integer ranks/counts in range')
        if n:result[r]=n
    return result

def pack_residuals(residual):
    """Construct and verify full width-100 banks; the volume bound proves optimality.
    Independent pattern enumeration reserves widths 20 and 4 as fillers. A
    bounded greedy construction can reject feasible inputs; it never certifies
    an unconstructed packing. No candidate physical-bank validity is implied.
    """
    remaining=Counter({r:60*n for r,n in residual.items()})
    patterns=[]
    def emit(widths,count):
        if not count:return
        if sum(widths)!=100 or count<0:raise ValueError('Invalid bank pattern')
        need=Counter(widths)
        for r,n in need.items():
            remaining[r]-=n*count
            if remaining[r]<0:raise ValueError('Constructive packing exhausted rank '+str(r))
        patterns.append(dict(widths=list(widths),count=count))
    for r in sorted(set(residual)-{20,4},reverse=True):
        candidates=[]
        for a in range(1,100//r+1):
            for c in range((100-r*a)//20+1):
                rest=100-r*a-20*c
                if rest%4==0:
                    b=rest//4;candidates.append((F(b,a),-a,-c,a,c,b))
        if not candidates:raise ValueError('No constructive pattern for rank '+str(r))
        _,_,_,a,c,b=min(candidates)
        q,left=divmod(remaining[r],a)
        emit([r]*a+[20]*c+[4]*b,q)
        if left:
            fills=[(b,c) for c in range((100-r*left)//20+1) for b in [(100-r*left-20*c)//4] if (100-r*left-20*c)%4==0]
            if not fills:raise ValueError('No remainder bank for rank '+str(r))
            b,c=min(fills);emit([r]*left+[20]*c+[4]*b,1)
    residual_twenty=remaining[20]%5
    if residual_twenty:emit([20]*residual_twenty+[4]*(25-5*residual_twenty),1)
    if remaining[20]%5 or remaining[4]%25:raise ValueError('Remaining fillers cannot tile exactly')
    emit([20]*5,remaining[20]//5);emit([4]*25,remaining[4]//25)
    if any(remaining.values()):raise ValueError('Packing left unused blocks')
    observed=Counter()
    for row in patterns:
        assert sum(row['widths'])==100 and row['count']>0
        for r in row['widths']:observed[r]+=row['count']
    if dict(observed)!=dict(Counter({r:60*n for r,n in residual.items()})):raise ValueError('Packing census mismatch')
    assert 100*sum(row['count'] for row in patterns)==60*base.mass(residual)
    return patterns

@lru_cache(None)
def baseline():
    # Every source is reverified on first use in this process.
    return base.run()

def price(histogram_delta,residual_delta,*,label='provisional'):
    """Price integer one-stage paid-child delta and residual-role-width delta.
    Deltas are relative to pinned PR320 after its final reorder. Must include
    every changed helper/source/target/copy paid child. Residual widths are
    endpoint_rank minus independent_entrance_rank, once per physical helper.
    Entry/endpoint changes, physical sinks, scalar costs and chronology are
    not inferred from the deltas and require separate evidence.
    """
    hd=integer_delta(histogram_delta,20,'histogram_delta');rd=integer_delta(residual_delta,20,'residual_delta')
    if base.mass(hd)!=base.mass(rd):raise ValueError('Histogram and residual delta masses differ; fixed-deficit contract violated')
    initial=baseline()
    helper=Counter({int(r):n for r,n in initial['profile']['final_helper'].items()});helper.update(hd)
    if min(helper.values())<0:raise ValueError('Negative helper child count')
    helper=Counter(base.clean(helper))
    families=Counter({int(r):n for r,n in initial['inventory']['residual_census'].items()});families.update(rd)
    if min(families.values())<0:raise ValueError('Negative residual role count')
    families=Counter(base.clean(families));patterns=pack_residuals(families)
    banks=sum(row['count'] for row in patterns);stock=60*4*960+5*banks;W=F(stock,60)
    priced=Counter({r:5*n for r,n in helper.items()});priced.update({4:1920,19:1920,38:1920,42:1920})
    assert 100*W-base.mass(priced)==2040
    root=base.bracket(priced,100,W);outer=base.assembly(root['lower'])
    supplied_moment=base.moment(priced,100,W,outer['bit_coarse']);assert supplied_moment[1]<1
    delta=outer['kappa']-initial['assembly']['kappa']
    return dict(status='CONDITIONAL_PR320_CANDIDATE_ARITHMETIC',label=label,head=base.HEAD,physical_admission=False,all_size_theorem=False,
        one_stage_histogram_delta=base.clean(hd),residual_role_delta=base.clean(rd),final_helper_histogram=base.clean(helper),
        banked_histogram=base.clean(priced),banked_calls=sum(priced.values()),banked_rank_mass=base.mass(priced),
        residual_census=base.clean(families),physical_R=sum(families.values()),banks_per_stage=banks,literal_stock=stock,
        packing_patterns=patterns,packing_unused_coordinates=0,packing_optimal_for_declared_widths=True,
        unreplicated_stock=W,normalized_stock=F(stock,5),deficit=2040,bit_root_bracket=root,assembly=outer,
        supplied_bit_moment=supplied_moment,kappa_delta=delta,improvement_percent=100*delta/initial['assembly']['kappa'],
        scope='Supplied deltas and retained assembly/complex hypotheses only. Exact chronology, source spans, all-column replays, scalar costs, charts, finite invoice and all-size admission remain separate obligations.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    data=json.loads(args.input.read_text());result=price(data['histogram_delta'],data['residual_delta'],label=data.get('label','provisional'))
    args.output.write_text(json.dumps(base.ae.serial(result),indent=2)+'\n')
    print(json.dumps(base.ae.serial(dict(kappa=result['assembly']['kappa'],kappa_decimal=result['assembly']['kappa_decimal'],kappa_delta=result['kappa_delta'],binding=result['assembly']['binding'],physical_admission=False)),indent=2))
