"""Exact algebraic certificate for uniform whole-helper owner optimality.

The integer prices and eleven-step reduction are due to chafreaky, PR795.
The uniform extension, additional exclusions, and algebraic checks are new.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTHS = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}
CAPS = {8: 48, 16: 32, 32: 32, 48: 32}
PRICES = {4: -1, 5: -20, 7: -8, 8: -2, 9: 4}
BONUS = {8: 2, 16: 4, 32: 8, 48: -13}
IDLE = {48: 2396, 44: 1, 3: 1, 1: 1}
LOCAL = {1: 2548, 2: 338, 3: 430, 4: 194, 5: 56, 8: 8}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sources():
    for name, digest in read(HERE/'SOURCES.json').items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest,
             'source pin: '+name)


def bind_selected():
    p = ROOT/'research/gauge44-frames-x'
    with tarfile.open(ROOT/'research/community-frontier799-audit/integrated799-replay.tar.gz') as archive:
        word = json.loads(gzip.decompress(archive.extractfile('native/local/CANONICAL-WORD.json.gz').read()))
        programs = json.loads(gzip.decompress(archive.extractfile('native/local/LOCAL-PROGRAMS.json.gz').read()))
    plan, owners = read(p/'data/PLAN.json'), read(p/'data/OWNERS.json.gz')
    spec = read(p/'data/SPEC.json')
    need((word['v'], word['h'], word['R']) == (112, 9, 504), 'dimensions')
    widths = [len(word['frames'][word['final'][h]])-
              len(word['frames'][word['start'][h]]) for h in range(224, 728)]
    need(Counter(widths) == WIDTHS, 'widths')
    need(Counter(c for c, _ in plan['windows'].values()) == CAPS, 'capacities')
    for direction in ('forward', 'backward'):
        need(Counter(e[-1] for e in programs[direction]
                     if e[0] in ('climb', 'center')) == LOCAL, 'local moment')
    calls = plan['provider_calls']
    need(len(calls) == 72 and {c['time'] for c in calls} == set(range(72))
         and all(c['provider'] == 'gauge44' for c in calls), 'dispatch')
    need(plan['provider_registry']['gauge44']['widths'] == widths, 'registry')
    cells, times, helpers = defaultdict(set), defaultdict(set), defaultdict(set)
    for role in owners:
        t, h = role['time'], role['helper']
        key = f"{role['owner_replica']},{role['child']}"
        need(key in plan['windows'], 'window')
        cap, allowed = plan['windows'][key]
        port = role['port']
        need(t in allowed and 0 <= port < 112 and 0 <= h < 504, 'owner domain')
        slot = key, port
        need(t not in times[slot] and h not in helpers[t], 'duplicate role')
        times[slot].add(t); helpers[t].add(h)
        need(role['width'] == widths[h], 'role width')
        start = role['offset']; used = set(range(start, start+widths[h]))
        need(0 <= start and start+widths[h] <= cap and not used & cells[slot], 'cells')
        cells[slot].update(used)
    need(len(owners) == 72*504 and all(helpers[t] == set(range(504))
                                      for t in range(72)), 'all roles')
    idle = Counter()
    for key, (cap, _) in plan['windows'].items():
        for port in range(112):
            remaining = cap-len(cells[key, port])
            if remaining:
                idle[remaining] += 1
    need(idle == IDLE, 'attained profile')
    total = Counter({r: 72*n for r, n in LOCAL.items()}); total.update(idle)
    need(dict(total) == {int(r): n for r,n in plan['profile'].items()}
         == {int(r): n for r,n in spec['expected']['global_profile'].items()}, 'invoice')
    return dict(helper_roles=len(owners), widths=WIDTHS, capacities=CAPS,
                idle=dict(idle), local=LOCAL)


def dual():
    upper = {}
    for cap in CAPS:
        dp = [0]+[None]*cap
        for fill in range(1, cap+1):
            choices = [dp[fill-w]+PRICES[w] for w in WIDTHS
                       if fill >= w and dp[fill-w] is not None]
            dp[fill] = max(choices) if choices else None
        for fill, value in enumerate(dp):
            if value is not None:
                r = cap-fill
                upper[r] = max(upper.get(r, -10**9), BONUS[cap]+value)
    base = 112*sum(CAPS[c]*BONUS[c] for c in CAPS)+72*sum(WIDTHS[w]*PRICES[w] for w in WIDTHS)
    need(base == -31136 and upper[0] == 0, 'dual baseline')
    need(2397*upper[48] < base, 'all48')
    need(sum(upper[r]*n for r,n in IDLE.items()) == base, 'dual attainment')
    excluded = []
    for largest in range(33, 45):
        other = 48-largest
        if largest not in upper or other not in upper:
            excluded.append(dict(parts=[largest, other], reason='unreachable residual'))
        else:
            bound = 2396*upper[48]+upper[largest]+upper[other]
            need(bound < base, 'two-part exclusion')
            excluded.append(dict(parts=[largest, other], bound=bound, gap=base-bound))
    return dict(upper=upper, base=base, excluded_two_parts=excluded)


def cases():
    answer = [('two-parts', {32: 1, 16: 1, 44: -1, 3: -1, 1: -1})]
    for t in range(2, 13):
        q, r = divmod(48*t, 44)
        counts = {48: 1-t, 44: q-1, 3: -1, 1: -1}
        if r:
            counts[r] = counts.get(r, 0)+1
        answer.append((f't{t}', {r:n for r,n in counts.items() if n}))
    return answer


def cube_root_bounds(r, bits=80):
    scale = 1 << bits
    target = r*r*scale**3
    lo, hi = 0, r*scale+1
    while hi-lo > 1:
        mid = (lo+hi)//2
        if mid**3 <= target:
            lo = mid
        else:
            hi = mid
    need(lo**3 <= target < (lo+1)**3, 'cube bracket')
    return Q(lo, scale), Q(lo if lo**3 == target else lo+1, scale)


def algebraic():
    bounds = {r:cube_root_bounds(r) for r in range(1,49)}
    result=[]
    for name, counts in cases():
        need(sum(r*n for r,n in counts.items()) == 0, 'zero at b=0')
        need(sum(counts.values()) <= 0, 'nonpositive at b=1')
        signs = [1 if counts[r] > 0 else -1 for r in sorted(counts)]
        changes = sum(a != b for a,b in zip(signs, signs[1:]))
        need(changes == 2, 'two sign changes')
        lower = sum(n*bounds[r][0 if n > 0 else 1] for r,n in counts.items())
        need(lower > 0, 'positive at b=1/3')
        result.append(dict(name=name, coefficients=counts, sign_changes=changes,
                           value_at_one=sum(counts.values()), lower_at_third=str(lower)))
    need(len(result) == 12, 'complete reduced cases')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args=parser.parse_args()
    sources()
    result=dict(status='PASS_UNIFORM_OWNER_OPTIMALITY', interval='0 < b <= 1/3',
                selected=bind_selected(), dual=dual(), algebraic=algebraic())
    if args.out:
        need(not args.out.exists(), 'output already exists')
        args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_UNIFORM_OWNER_OPTIMALITY cases=12 roles=36288 interval=(0,1/3]')

if __name__ == '__main__':
    main()
