"""Independent count-vector dual check and integer DP over every idle mass."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def partitions(n, largest=None):
    if n == 0:
        yield ()
    else:
        for r in range(min(n, largest or n), 0, -1):
            for rest in partitions(n-r, r):
                yield (r,)+rest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists() and not args.out.resolve().is_relative_to(P), 'new external output file')
    expected = read(P/'MANIFEST.json')
    actual = {f.relative_to(P).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in P.rglob('*') if f.is_file() and f != P/'MANIFEST.json'
              and '__pycache__' not in f.parts}
    need(expected == actual, 'manifest')
    plan, spec = read(P/'data/PLAN.json'), read(P/'data/SPEC.json')
    word, programs = read(P/'data/CANONICAL-WORD.json.gz'), read(P/'data/LOCAL-PROGRAMS.json.gz')
    inventory = Counter(len(word['frames'][word['final'][h]])-
                        len(word['frames'][word['start'][h]]) for h in range(224, 728))
    caps = Counter(v[0] for v in plan['windows'].values())
    need(inventory == {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}, 'width inventory')
    need(caps == {8: 48, 16: 32, 32: 32, 48: 32}, 'capacity inventory')
    local = Counter(e[-1] for e in programs['forward'] if e[0] in ('climb', 'center'))
    idle = Counter({int(r): n for r, n in plan['profile'].items()})
    idle.subtract({r: 72*n for r, n in local.items()})
    idle = {r: n for r, n in idle.items() if n}
    need(idle == {48: 2396, 44: 1, 3: 1, 1: 1}, 'idle profile')
    mass = 112*sum(c*n for c, n in caps.items())-72*sum(w*n for w, n in inventory.items())
    need(mass == 115056 and min(inventory) == 4, 'mass and maximum nonempty remainder')
    prices, bonuses = {4: -1, 5: -20, 7: -8, 8: -2, 9: 4}, {8: 2, 16: 4, 32: 8, 48: -13}
    remainders, enumerated = {}, 0
    widths = sorted(inventory)
    for cap in caps:
        for counts in product(*(range(cap//w+1) for w in widths)):
            fill = sum(w*n for w, n in zip(widths, counts))
            if fill > cap:
                continue
            enumerated += 1
            value = bonuses[cap]+sum(prices[w]*n for w, n in zip(widths, counts))
            rem = cap-fill
            remainders[rem] = max(value, remainders.get(rem, value))
    base = 112*sum(caps[c]*bonuses[c] for c in caps)+72*sum(inventory[w]*prices[w] for w in widths)
    need(base == -31136 and remainders[0] == 0, 'dual baseline')
    need(2397*remainders[48] < base, 'all48 exclusion')
    need(2396*remainders[48]+remainders[44]+remainders[4] < base, '44plus4 exclusion')
    need(sum(remainders[r]*n for r, n in idle.items()) == base, 'attained dual equality')
    source = importlib.util.spec_from_file_location('independent_base_two', P/'engines/base_two_moment.py')
    engine = importlib.util.module_from_spec(source)
    source.loader.exec_module(engine)
    b, grid = Q(spec['expected']['complex_lower']), engine.GRID
    need(0 < b < 1, 'endpoint range')
    lower = {}
    for r in range(1, 49):
        lo, _ = engine.moment(73, 7168, [(r, 1)], b)
        need((lo*grid).denominator == 1, 'integer lower grid')
        lower[r] = int(lo*grid)
    fixed = int(engine.moment(73, 7168, [(r, 72*n) for r, n in local.items()], b)[0]*grid)
    current = Counter({r: 72*n for r, n in local.items()})
    current.update(idle)
    current_interval = engine.moment(73, 7168, list(current.items()), b)
    need(current_interval[1] < 1, 'current moment')
    # Unbounded integer partition DP: every non-48 remainder is at most 44.
    # Each transition uses an outward lower bound, so a DP lower bound above
    # one excludes every true profile represented by it.
    dp = [0]+[None]*mass
    for total in range(1, mass+1):
        dp[total] = min(dp[total-r]+lower[r] for r in range(1, min(44, total)+1))
    margins = [(fixed+n48*lower[48]+dp[mass-48*n48]-grid, n48) for n48 in range(2396)]
    minimum, at = min(margins)
    need(minimum > 0, 'all n48 <= 2395 excluded')
    small = [0]+[None]*48
    for total in range(1, 49):
        small[total] = min(small[total-r]+lower[r] for r in range(1, min(43, total)+1))
    no44_margin = fixed+2396*lower[48]+small[48]-grid
    need(no44_margin > 0, 'n48=2396 without rank44 excluded')
    splits = []
    for parts in partitions(4):
        if parts in ((4,), (3, 1)):
            continue
        margin = fixed+2396*lower[48]+lower[44]+sum(lower[r] for r in parts)-grid
        need(margin > 0, 'other partitions of four excluded')
        splits.append(dict(parts=parts, margin=str(Q(margin, grid))))
    need(len(splits) == 3, 'complete four-partition classification')
    result = dict(status='PASS_INDEPENDENT_INTEGER_PARTITION_OPTIMALITY',
                  enumerated_width_patterns=enumerated, dual_base=base,
                  remainder_upper=remainders, current_moment=[str(x) for x in current_interval],
                  endpoint=str(b), dp_states=len(dp), alternative_rank48_counts=len(margins),
                  minimum_dp_margin=str(Q(minimum, grid)), minimum_at_rank48_count=at,
                  no44_margin=str(Q(no44_margin, grid)), other_splits=splits,
                  dp_sha256=hashlib.sha256(json.dumps(dp, separators=(',', ':')).encode()).hexdigest(),
                  scope='Independent width-pattern enumeration and base-two interval engine; '
                        'integer DP covers all non-48 integer partitions at every feasible total mass.')
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print('PASS_INDEPENDENT_INTEGER_PARTITION_OPTIMALITY')


if __name__ == '__main__':
    main()
