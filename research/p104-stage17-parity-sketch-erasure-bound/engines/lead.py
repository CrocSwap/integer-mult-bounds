"""Five-parity erased-map rank bound on the exact two stage-17 lanes."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from json import dumps,loads
from math import comb
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'lead/inputs/CALLER.json':'255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'round214/lead/inputs/PROJECTOR.json':'c36cb8d3fae7bccd15566c2f83f2d2bd8abeeb334381cbf3212d5d9b3d965c35',
    'round214/lead/inputs/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}


def rank2(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length()-1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def main():
    assert __debug__
    alarm(20)
    for name,digest in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest
    caller = loads((ROOT/'lead/inputs/CALLER.json').read_bytes())
    assert caller['events'][4646] == caller['events'][4660] == ['B','IDLE_ONE',36,[17]]
    assert len(caller['types']['B']['ports']) == 8
    proj = loads((ROOT/'round214/lead/inputs/PROJECTOR.json').read_bytes())
    assert proj['rank'] == 2 and proj['inclusive_window'] == [4646,4660]
    m,k = 16,5
    mask = (1<<m)-1
    q = lambda x: comb(x.bit_count(),2)%2
    rows = [sum((q((1<<i)^(1<<j))^q(1<<i)^q(1<<j))<<j for j in range(m)) for i in range(m)]
    assert rows == [mask^(1<<i) for i in range(m)] and rank2(rows) == m
    least_restriction_rank = m-2*k
    max_bias = F(1,2**(least_restriction_rank//2))
    max_residue = (1+max_bias)/2
    required = 2*(1-max_residue)
    probes = [mask,3,12,48,192]
    assert rank2(probes) == k
    counts = Counter((sum(((x&v).bit_count()%2)<<i for i,v in enumerate(probes)),x.bit_count()%4)
                     for x in range(1<<m))
    assert len({sum(counts[j,r] for r in range(4)) for j in range(1<<k)}) == 1
    empirical = F(max(counts.values()),1<<(m-k))
    assert empirical == max_residue == F(9,16)
    fixed_fraction = F(sum(comb(32,j) for j in range(0,33,4)),1<<32)
    assert fixed_fraction >= F(1,4)
    capacity_per_volume = F(3,4)
    min_volume = required/capacity_per_volume
    h = run_path(str(ROOT/'round214/lead/inputs/pricing.py'))['power_bounds']
    lo,hi = map(F,('0.00364665195644044790699554028334161','0.00364665195644044790699554028334162'))
    funded_volume_upper = 2*h(8,lo)[1]/h(16,hi)[0]
    gross_upper = 16*h(8,lo)[1]-8*min_volume*h(16,hi)[0]
    assert min_volume == F(7,6) > F(1003,1000) > funded_volume_upper and gross_upper < 0
    alarm(0)
    print(dumps({'pins':PINS,'width':2,'clocks':[4646,4660],'parity_cap':k,'polar_rank':m,
                 'restricted_rank_lower':least_restriction_rank,'residue_fraction_upper':str(max_residue),
                 'control_probes':probes,'control_max_fraction':str(empirical),
                 'target_displacement_per_old_lane_lower':str(required),'normalized_core_fixed_fraction':str(fixed_fraction),
                 'core_capacity_per_volume_upper':str(capacity_per_volume),'required_volume_lower':str(min_volume),
                 'funded_volume_upper':str(funded_volume_upper),'gross_upper':str(gross_upper),
                 'control_cap':1,'runner_cap_seconds':20},sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
