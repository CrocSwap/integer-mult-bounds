#!/usr/bin/env python3
"""Recompute the sixth-stage grid cap and the candidate's complete rational invoice."""
from collections import Counter
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from itertools import islice
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from upstream import install
install()
from band_product import production_supplier
from binary_receiver import Receiver, source_rule
from calibration import (COMPLEX_C, GAP, LAST_TICK, NEAR_RAW, PRODUCTIVE_TILT,
                         SPLIT_TILT, prices)
from check_profile import RAW_LEFT, RAW_RIGHT, check, check_stop_dispatch, reject
from independent_binary_price import crossing_limit, mass, rank_price, raw_moments
from linear_geometry import ceil_log2
from module_atoms import balanced_widths
from outer_budget import qualify
from periodic import Job
from positive import power_le
from powered import Port, PoweredWord
from resources import requirements
from strict_moment import certify
from strong_binary import graph, caller, native_word


def decimal(q, n=40):
    with localcontext() as ctx:
        ctx.prec = n
        return str(Decimal(q.numerator) / Decimal(q.denominator))


def six_stage_ceiling(raw_right):
    """Inductively dominate each grid rate with zero debits and the raw ceiling.

    This is an upper bound for the specific six-stage price algorithm when
    bit_c < raw_right. It is not a bound for other callers or other grids.
    """
    previous = Q(0)
    rates = []
    for _ in range(5):
        limit = (249 * raw_right + previous) / 250
        previous = Q((limit * 10**18).__floor__() - 1, 10**18)
        rates.append(previous)
    return rates, (249 * raw_right + previous) / 250


def power_430_toy():
    """Exercise the 430-level interpreter on a one-port finite owner control."""
    source = Port(('toy-productive',), 1)
    paid = Port(('toy-paid',), 1)
    toy = PoweredWord(1, (source,), (paid,), 430, 1, 1, 1)
    class Physical:
        calls = 0
        def raw(self, inputs, columns):
            ((tag, job),) = inputs
            check(tag == source.tag and columns == 1, 'toy raw binding')
            self.calls += 1
            yield paid.tag, job
        def fresh(self, *_args):
            raise AssertionError('The one-port control does not discard a target')
        def retire(self, *_args):
            raise AssertionError('The one-port control owns no extra field')
    physical = Physical()
    field = Job('preserved-owner', (0,))
    check(tuple(toy.native((field,), 1, physical)) == (field,) and physical.calls == 430,
          '430-level powered interpreter preserves the toy owner')


def main(path=None):
    check_stop_dispatch()
    den = 10**21
    check(not power_le(2, den, 1 << 1000) and power_le(1, den, 1 << 1000),
          'last-tick stop comparator')
    with patch('strong_complex.artifacts', return_value=SimpleNamespace(graph=None, layout=None)), \
         patch('strong_complex.word', return_value=object()):
        a, b = production_supplier(9, den), production_supplier(9, 10**20)
        check(a is not b and a.carrier == b.carrier == 512 and a.denominator == den,
              'positive supplier and exact stop cache key')
    production_supplier.cache_clear()

    p = LAST_TICK
    v, c = p.power, p.bit_c
    tick = Q('0.003890115286594445')
    check(p.kappa == tick and p.kappa > NEAR_RAW.kappa, 'improved claimed tick')
    check(Q(0) < RAW_LEFT-c < Q(1,10**20), 'dyadic trial is below bracket within 1e-20')
    targets, paid = raw_moments(graph(), caller())
    crossing_limit(targets, paid)
    check(mass(targets, 1-RAW_LEFT, 0) > mass(paid, 1-RAW_LEFT, 1) and
          mass(paid, 1-RAW_RIGHT, 0) > mass(targets, 1-RAW_RIGHT, 1),
          'directed independently bracketed fixed source crossing')
    upper_grid, upper = six_stage_ceiling(RAW_RIGHT)
    check(tick < upper < tick + Q(1, 10**18), 'next grid tick exceeds six-stage upper cap')

    word = native_word(v)
    check(Counter(x.rank for x in word.targets) == targets and
          Counter(x.rank for x in word.paid) == paid, 'literal source inventories')
    check((word.ambient, word.power, word.floor, word.low_cut, word.high_cut) ==
          (134, 430, 15, 12, 12), 'installed powered source')
    power_430_toy()
    # Bind a real 430-factor productive path and a real paid path to the retained word.
    tj = next(i for i,port in enumerate(word.targets) if port.rank >= 15)
    pj = next(i for i,port in enumerate(word.paid) if 1 <= port.rank <= 4)
    target = word.target((tj,)*v)
    block, = word.blocks((pj,)*v)
    check(target.rank == word.targets[tj].rank**v and target.rank >= 15**v and
          len(target.tag) == v and block.rank == word.paid[pj].rank**v and
          block.first == 0 and len(block.tags) == v, 'actual 430-factor paths')
    tj_low = next(i for i,port in enumerate(word.targets) if port.rank < 15)
    pj_high = next(i for i,port in enumerate(word.paid) if port.rank > 12)
    discarded = word.target((tj_low,)*v)
    first, second = islice(word.blocks((pj_high,)*v), 2)
    check(discarded.rank < 15**v and first.rank == second.rank == 12**v and
          (first.first,second.first) == (0,12**v),
          'real discarded path and consecutive paid split offsets')
    t, z, w = 1-c, SPLIT_TILT, PRODUCTIVE_TILT
    denom = mass(targets, t, 0)
    alpha = mass(paid, t, 1)/denom
    gamma = mass(paid, t+z, 1)/(rank_price(12,z)[0]*denom)
    lam = rank_price(15,w)[1]*mass(targets,t-w,1)/denom
    surplus = 1-alpha**v-2*gamma**v-lam**v
    check(surplus > Q(2,p.floor), 'independent directed classic split surplus')
    check(surplus > Q(3906,10**21), 'reporting precision for actual positive margin')
    certify(word,c,z,w,v,p.floor.bit_length()-2,15)
    corrupt_c = Q((RAW_RIGHT*2**80).__ceil__(),2**80)
    reject(certify,word,corrupt_c,z,w,v,p.floor.bit_length()-2,15)
    check(mass(paid,t,0)+1 > mass(targets,t,1), 'extra rank-one paid occurrence fails')
    check(18_906**v+104_904**v+23_800**v < 2**(18*v) and
          5**13>16*4**13 and 8*(Q(13,4)+Q(1,512))<27 and
          18*(Q(13,4)+Q(1,512))<60 and 15**v>=2*12**v and
          512*v<=min(p.rank_logs), 'split census, enumeration and frame guard')
    check(2**64*(v+1)*2**(28*v)<2**(512*v) and
          872*(Q(13,4)+Q(2,512))*(512*v)<2**(512*v),
          'generation and causal precision guard')

    bit,numeric,stages = prices(p)
    check((bit,numeric,len(stages)) == (31,10,6), 'complete BIT, numerical and stage invoices')
    previous = Q(0)
    stage_report = []
    for i,(h,covered,rate) in enumerate(stages):
        limit = min((249*covered+previous)/250,p.eta)
        margin = limit-rate
        check(margin>0 and previous<rate, f'strict funded stage {i+1}')
        if i<5:
            check(rate<=upper_grid[i] and (rate*10**18).denominator==1,
                  f'grid stage {i+1} obeys upper envelope')
        stage_report.append({'height':h,'rate':str(rate),'limit':str(limit),
                             'strict_margin':str(margin),
                             'margin_floor_e24':(margin*10**24).__floor__()})
        previous = rate
    positive = COMPLEX_C-Q(numeric,p.complex_log)
    gap = Q(1,p.positive_stop_denominator)
    minimum_last_height = (Q(249*bit,250)/(upper-tick-4*gap)).__ceil__()
    check(p.rank_logs[-1] > minimum_last_height and minimum_last_height > sys.maxsize,
          'profile debit forces last height beyond host shift-count range')
    signed = qualify(p.kappa,gap,p.ordinary,positive)
    reject(qualify,p.kappa,GAP,p.ordinary,positive)
    reject(qualify,p.kappa,Q(0),p.ordinary,positive)
    reject(qualify,p.kappa,gap,p.kappa+4*gap,positive)
    reject(qualify,p.kappa,gap,p.ordinary,p.kappa+5*gap)
    reject(prices,replace(p,positive_stop_denominator=GAP.denominator))
    reject(prices,replace(p,kappa=tick+Q(1,10**18)))

    res = requirements(p)
    cuts, s = res['binary_entrance_logs'],res['initial_s']
    for i,h in enumerate(p.rank_logs):
        # The predecessor helper fixes eta=97/25000. This profile uses 39/10000,
        # so compute the actual conservative quotient entry directly.
        qcut = (Q(2*h+64,1)/(1-p.eta)).__ceil__()
        check((1-p.eta)*qcut >= 2*h+64 and qcut < 3*h < 8*h,
              f'quotient entry for stage {i+1}')
        top = cuts[i+1] if i+1<len(cuts) else s
        floor_log = cuts[i-1] if i else 0
        if i+1<len(cuts):
            parent_top = cuts[i+2] if i+2<len(cuts) else s
            check(parent_top+250 < 250*top and cuts[i]+1<top,
                  f'parent recursion bounds for stage {i+1}')
        check(top-floor_log <= 8*h, f'complete stage width for stage {i+1}')
    H=max(p.complex_log,*p.rank_logs)
    # Since (5/4)^13 > 2^4 and the target/paid ratio is >= (5/4)^v,
    # G+1 <= ceil(13H/(4v))+2. This replaces the old G < 2^50 guard.
    Gplus1=(13*H+4*v-1)//(4*v)+2
    nodes=res['raw_structural_nodes_log2_upper'];q=res['native_volume_log2_upper']
    local=4*nodes+8*ceil_log2(H+1)+512
    check(Gplus1<=4*(H+1) and 19+2*nodes+Gplus1.bit_length()<local<q,
          'unbounded-H source slot count fits dynamic native q allowance')
    check(p.positive_stop_denominator.bit_length()+1<512, 'stop comparator control budget')
    check(res['all_size_margin_lower_at_entrance']>0,'all-size stock and precision certificate')
    receiver=Receiver(2,balanced_widths(1),direct=True,profile=p)
    check(receiver.rule is source_rule(v) and receiver.rule.word is word and receiver.stock>0,
          'actual profile reaches receiver on feasible rank control')
    result = {
       'kappa':str(p.kappa),'kappa_decimal':decimal(p.kappa),
       'six_stage_upper_fraction':str(upper),'six_stage_upper_decimal':decimal(upper),
       'upper_scope':'given bit_c < RAW_RIGHT, 5 stages on 1e-18 grid and this price recurrence',
       'raw_interval':[str(RAW_LEFT),str(RAW_RIGHT)],'trial':str(c),'power':v,'band_floor':p.floor,
       'gap':str(gap),'ordinary':str(p.ordinary),'positive_paid_cap':str(positive),'signed':signed,
       'surplus_floor_e21':(surplus*10**21).__floor__(),
       'power_430_toy_owner_control': {'raw_calls':430, 'returned_original_owner':True},
       'bit_debit':bit,'numeric_debit':numeric,'stages':stage_report,
       'upper_grid_rates':[str(a) for a in upper_grid],
       'G_plus_1_upper':Gplus1,'native_slot_log_upper':19+2*nodes+Gplus1.bit_length(),
       'local_exponent':local,'native_q':q,
       'minimum_last_height_with_profile_debit':minimum_last_height,
       'host_py_ssize_max':sys.maxsize,
       'physical_execution_limit': 'Production ranks exceed CPython shift size and available host storage; feasible controls only.',
       'complete_requirements':res}
    content=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if path:
        Path(path).write_text(content)
    else:
        print(content,end='')
    print('PASS_LAST_TICK_ARITHMETIC_AND_FEASIBLE_RECEIVER',decimal(p.kappa),flush=True)


if __name__=='__main__':
    main(sys.argv[1] if len(sys.argv)>1 else None)
