#!/usr/bin/env python3
"""Integer block-delivery screening, not supplier admission.

Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
M, W, IDLE = 73, Q(896, 9), 1646
BASE_HI = Q(1690054109089, 10**15)
TARGET = Q(21, 20) * BASE_HI
INPUTS = {
    'research/complex-local-word-ceiling/ceiling.py',
    'research/complex-local-word-ceiling/RESULT.json',
    'research/community-frontier1094-audit/ASSEMBLY.json',
    'research/community-frontier1094-audit/INDEPENDENT1094.json',
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = [pin['path'] for pin in pins['files'] if pin['usage']=='input']
    require(len(inputs)==len(INPUTS) and set(inputs)==INPUTS, 'source inventory')
    for pin in pins['files']:
        if pin['usage'] == 'input':
            require(hashlib.sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'],
                    'source drift: ' + pin['path'])
    path = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
    spec = importlib.util.spec_from_file_location('retained_ceiling', path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine


@lru_cache(None)
def binomial_cost(r, a):
    """Independent enclosure of (r/73)^(1-a), using the negative binomial tail.

    For q=1-a and z=1-r/73, (1-z)^q=1-sum(t_n), all t_n>0;
    t_1=q*z, t_(n+1)=t_n*z*(n-q)/(n+1). Every tail ratio is <z.
    Outward integer rounding also encloses accumulated roundoff.
    """
    require(type(r) is int and 1 <= r < M and 0 < a < 1, 'binomial domain')
    scale = 1 << 160
    q, z = 1-a, Q(M-r, M)

    def floor(x):
        return x.numerator // x.denominator

    def ceil(x):
        return -((-x.numerator) // x.denominator)

    lo, hi = floor(q*z*scale), ceil(q*z*scale)
    sum_lo, sum_hi, n = lo, hi, 1
    while True:
        ratio = z*(n-q)/(n+1)
        lo, hi = floor(lo*ratio), ceil(hi*ratio)
        tail = ceil(hi/(1-z))
        if tail <= 1 << 70:  # absolute remainder at most 2^-90
            return Q(scale-sum_hi-tail, scale), Q(scale-sum_lo, scale)
        sum_lo, sum_hi, n = sum_lo+lo, sum_hi+hi, n+1


def partition(k, cap):
    require(type(k) is int and 0 <= k <= WORD[1], 'replacement count')
    require(type(cap) is int and 2 <= cap <= 51, 'block cap')
    count, remainder = divmod(k, cap)
    out = Counter({cap: count}) if count else Counter()
    if remainder:
        out[remainder] += 1
    return dict(sorted(out.items()))


def profile(k, cap):
    out = Counter(WORD)
    out[1] -= k
    out.update(partition(k, cap))
    return {r: n for r, n in sorted(out.items()) if n}


def interval(profile_, a, cost, overhead=None):
    """Old payload mass/idle are fixed; overhead is additional paid work."""
    terms = dict(profile_)
    terms[51] = terms.get(51, 0) + Q(IDLE, 51)
    for r, n in (overhead or {}).items():
        require(type(r) is int and 1 <= r <= 51 and Q(n) >= 0, 'overhead alphabet')
        terms[r] = terms.get(r, 0) + Q(n)
    lo = hi = Q(0)
    for r, n in terms.items():
        c = cost(r, a)
        lo, hi = lo+n*c[0], hi+n*c[1]
    return lo/W, hi/W


def sign(bounds):
    if bounds[1] < 1:
        return -1
    if bounds[0] > 1:
        return 1
    raise ValueError('unresolved strict moment sign')


def threshold(cap, a, cost):
    require(sign(interval(profile(0, cap), a, cost)) == 1, 'baseline must fail target')
    if sign(interval(profile(WORD[1], cap), a, cost)) == 1:
        return None
    lo, hi = 0, WORD[1]
    while hi-lo > 1:
        mid = (lo+hi)//2
        if sign(interval(profile(mid, cap), a, cost)) < 0:
            hi = mid
        else:
            lo = mid
    return hi


def max_extra_ones(k, cap, a, cost):
    bounds = interval(profile(k, cap), a, cost)
    require(bounds[1] < 1, 'overhead needs a feasible relaxation')
    c = cost(1, a)
    lo = (1-bounds[1])*W/c[1]
    hi = (1-bounds[0])*W/c[0]
    # h must be STRICTLY below the affordable real number.
    h = (lo.numerator-1)//lo.denominator
    require(Q(h+1) > hi, 'overhead integer sign unresolved')
    require(sign(interval(profile(k, cap), a, cost, {1:h})) < 0, 'overhead accepted sign')
    require(sign(interval(profile(k, cap), a, cost, {1:h+1})) > 0, 'overhead rejected sign')
    return h, (lo, hi)


def small_partitions(total, cap, lower=1):
    if total == 0:
        yield ()
    for first in range(lower, min(total, cap)+1):
        for rest in small_partitions(total-first, cap, first):
            yield (first,)+rest


def verify():
    C = sources()
    @lru_cache(None)
    def retained(r, a):
        return C.child_cost(r, M, a)
    baseline = json.loads((ROOT / 'research/complex-local-word-ceiling/RESULT.json').read_text())
    asm = json.loads((ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json').read_text())
    owner = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    H = {int(r):n for r,n in asm['complex_profile'].items()}
    idle = {int(r):n for r,n in owner['owner']['idle'].items()}
    calls, live = owner['price']['calls'], owner['price']['live']
    require(calls == 144 and live == 14336 and Q(live,calls) == W, 'selected template')
    require(H == {int(r):n for r,n in owner['owner']['profile'].items()}, 'selected profile')
    require(all(H.get(r,0)-idle.get(r,0) == calls*WORD.get(r,0) for r in set(H)|set(idle)|set(WORD)),
            'source-bound local profile')
    require(sum(r*n for r,n in idle.items()) == calls*IDLE, 'idle mass')
    require(sum(r*n for r,n in H.items()) == 72*live+64*calls, 'coverage mass')
    require(BASE_HI == Q(baseline['ceiling']['a_ceiling']), 'baseline ceiling reference')
    for cost in (retained, binomial_cost):
        require(sign(interval(WORD, BASE_HI, cost)) > 0, 'baseline upper sign')
        require(sign(interval(WORD, Q(baseline['ceiling']['a_relaxation_achievable']), cost)) < 0,
                'baseline lower sign')

    rows = []
    for cap in range(2,52):
        k = threshold(cap,TARGET,retained)
        require(k == threshold(cap,TARGET,binomial_cost), 'independent threshold')
        require(sum(r*n for r,n in profile(WORD[1],cap).items()) == 5586, 'reblocked mass')
        row = {'cap':cap,'minimum_replaced':k}
        if k is not None:
            h, budget = max_extra_ones(WORD[1],cap,TARGET,retained)
            h2, _ = max_extra_ones(WORD[1],cap,TARGET,binomial_cost)
            require(h == h2, 'independent overhead count')
            row.update(partition_at_threshold=partition(k,cap),
                       threshold_moment=[str(x) for x in interval(profile(k,cap),TARGET,retained)],
                       previous_moment=[str(x) for x in interval(profile(k-1,cap),TARGET,retained)],
                       all_rank1_reblocked_extra_rank1_max=h,
                       extra_rank1_budget=[str(x) for x in budget])
        rows.append(row)

    # Exhaustive positive fixtures for the concavity partition theorem.
    fixtures = 0
    for a in (TARGET,Q(1,99)):
        for cap in range(2,9):
            for total in range(1,19):
                optimum = partition(total,cap)
                best_hi = sum(n*binomial_cost(r,a)[1] for r,n in optimum.items())
                for parts in small_partitions(total,cap):
                    if Counter(parts) != Counter(optimum):
                        alternative_lo = sum(binomial_cost(r,a)[0] for r in parts)
                        require(alternative_lo > best_hi, 'integer-partition dominance')
                    fixtures += 1

    rank16 = next(row for row in rows if row['cap']==16)
    k = rank16['minimum_replaced']
    minimal_h, minimal_budget = max_extra_ones(k,16,TARGET,retained)
    require(minimal_h == max_extra_ones(k,16,TARGET,binomial_cost)[0], 'minimal overhead crosscheck')
    rank16['at_threshold_extra_rank1_max'] = minimal_h
    rank16['at_threshold_extra_rank1_budget'] = [str(x) for x in minimal_budget]

    # One added rank-one call per nontrivial output block erases its saving.
    # r*c(1)-c(r) < c(1) for every allowed r; monotonicity extends to a<=TARGET.
    tax_rows = []
    for r in range(2,52):
        engines = []
        for cost in (retained,binomial_cost):
            one, block = cost(1,TARGET), cost(r,TARGET)
            saving = (r-block[1]/one[0], r-block[0]/one[1])
            require(0 < saving[0] <= saving[1] < 1, 'one-call-per-block obstruction')
            engines.append([str(x) for x in saving])
        tax_rows.append({'rank':r, 'saving_in_rank1_call_units':engines})

    # Sharp total overhead rank mass for complete rank-16 payload reblocking.
    # At any fixed mass, the cheapest overhead is itself optimally blocked.
    overhead_rows = []
    for r in (1,2,4,8,16,32,51):
        bounds = interval(profile(2412,16),TARGET,retained)
        c = retained(r,TARGET)
        lo,hi = (1-bounds[1])*W/c[1], (1-bounds[0])*W/c[0]
        h = (lo.numerator-1)//lo.denominator
        require(h+1 > hi, 'overhead rank threshold')
        for cost in (retained,binomial_cost):
            require(sign(interval(profile(2412,16),TARGET,cost,{r:h})) < 0, 'rank overhead pass')
            require(sign(interval(profile(2412,16),TARGET,cost,{r:h+1})) > 0, 'rank overhead fail')
        overhead_rows.append({'rank':r, 'max_calls':h, 'real_budget':[str(lo),str(hi)]})
    for cost in (retained,binomial_cost):
        require(sign(interval(profile(2412,16),TARGET,cost,{10:1})) < 0, 'mass10 overhead pass')
        require(sign(interval(profile(2412,16),TARGET,cost,{11:1})) > 0, 'mass11 overhead fail')
        # For any mass >=51, even fractional rank51 delivery exceeds the bill.
        require(sign(interval(profile(2412,16),TARGET,cost,{51:1})) > 0, 'large overhead fail')

    # Even putting ALL selected rank-one mass at rank 51 cannot pass 1/99.
    target_large = []
    for cost in (retained,binomial_cost):
        bound = interval(profile(2412,51),Q(1,99),cost)
        require(sign(bound) > 0, 'target-scale rank-one-only obstruction')
        target_large.append([str(x) for x in bound])

    controls = 0
    for bad in ((-1,16),(2413,16),(True,16),(16,1),(16,52)):
        try:
            partition(*bad)
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid domain accepted')
    # Added work cannot borrow idle credit. One more than the maximal bill fails.
    h = rank16['all_rank1_reblocked_extra_rank1_max']+1
    bad_profile = Counter(profile(2412,16)); bad_profile[1] += h
    wrong = C.relax(dict(bad_profile),M,896,9,64,TARGET)
    right = interval(profile(2412,16),TARGET,retained,{1:h})
    require(sign(wrong)<0 and sign(right)>0, 'idle-debit mutation must give a false pass')
    controls += 1
    # Non-greedy equal mass and deletion-without-accounting controls.
    require(sum(binomial_cost(r,TARGET)[0] for r in (8,8)) > binomial_cost(16,TARGET)[1],
            'split-block control')
    require(sum(r*n for r,n in {r:n for r,n in WORD.items() if r!=1}.items()) != 5586,
            'deletion is not mass-preserving reblocking')
    controls += 2
    return {'status':'PASS_COMPLEX_RANK_ONE_BLOCK_BUDGET', 'target':str(TARGET),
            'target_definition':'21/20 times the certified baseline primitive ceiling upper bound',
            'local_profile':WORD, 'idle_mass':IDLE, 'rows':rows,
            'one_extra_rank1_per_block_obstruction':tax_rows,
            'rank16_complete_overhead_by_rank':overhead_rows,
            'rank16_complete_max_extra_integer_rank_mass':10,
            'rank_one_only_at_1_over_99':target_large, 'partition_fixtures':fixtures,
            'mathematical_controls':controls,
            'scope':'Optimal cost-alphabet relaxation; no decoder, frame legality or supplier admission.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true')
    args = ap.parse_args()
    result = verify()
    text = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(text)
    else:
        saved = json.loads((HERE/'RESULT.json').read_text())
        require(json.dumps(saved,sort_keys=True) == json.dumps(json.loads(text),sort_keys=True),
                'result drift')  # Preserve integer/bool types as well as values.
    r16 = next(row for row in result['rows'] if row['cap']==16)
    print(result['status'], 'rank16_minimum=',r16['minimum_replaced'],
          'extra_rank1_max=',r16['all_rank1_reblocked_extra_rank1_max'],
          'partition_fixtures=',result['partition_fixtures'],'controls=',result['mathematical_controls'])


if __name__ == '__main__':
    main()
