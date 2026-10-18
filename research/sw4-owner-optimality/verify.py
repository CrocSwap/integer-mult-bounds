"""Verify the fixed PR741 owner-profile optimum, using only exact arithmetic."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIDTHS = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}
LOCAL = {1: 2556, 2: 334, 3: 430, 4: 194, 5: 56, 8: 8}
CAPACITIES = {8: 48, 16: 32, 32: 32, 48: 32}
IDLE = {48: 2396, 44: 1, 3: 1, 1: 1}
WIDTH_PRICES = {4: -1, 5: -20, 7: -8, 8: -2, 9: 4}
CAPACITY_PRICES = {8: 2, 16: 4, 32: 8, 48: -13}


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_engine(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'engines'/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_files():
    actual = {p.relative_to(ROOT).as_posix(): sha(p) for p in ROOT.rglob('*')
              if p.is_file() and p != ROOT/'MANIFEST.json' and '__pycache__' not in p.parts}
    require(actual == read(ROOT/'MANIFEST.json'), 'package manifest')
    for row in read(ROOT/'SOURCES.json'):
        raw = (ROOT/row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
                == row['git_blob_sha1'], 'source Git blob')


def inputs():
    return tuple(read(ROOT/'data'/name) for name in
                 ('PLAN.json', 'SPEC.json', 'OWNERS.json.gz',
                  'CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'))


def validate_inputs(plan, spec, owners, word, program):
    require((word['v'], word['h'], word['R']) == (112, 9, 504), 'native dimensions')
    widths = [len(word['frames'][word['final'][h]])-len(word['frames'][word['start'][h]])
              for h in range(224, 728)]
    require(Counter(widths) == WIDTHS, 'native width inventory')
    local = Counter(e[-1] for e in program['forward'] if e[0] in ('climb', 'center'))
    backward = Counter(e[-1] for e in program['backward'] if e[0] in ('climb', 'center'))
    require(local == backward == LOCAL, 'both native paid profiles')
    require(Counter(cap for cap, _ in plan['windows'].values()) == CAPACITIES,
            'capacity inventory')
    calls = plan['provider_calls']
    require(len(calls) == 72 and {c['time'] for c in calls} == set(range(72))
            and all(c['provider'] == 'gauge44' for c in calls), 'complete dispatch')
    require(plan['provider_registry']['gauge44']['widths'] == widths, 'provider widths')
    used, times, helpers = defaultdict(set), defaultdict(set), defaultdict(set)
    for role in owners:
        t, h = role['time'], role['helper']
        key = f"{role['owner_replica']},{role['child']}"
        require(key in plan['windows'], 'owner window')
        cap, allowed = plan['windows'][key]
        slot = key, role['port']
        require(0 <= role['port'] < 112 and t in allowed, 'owner time and port')
        require(0 <= h < 504 and h not in helpers[t] and t not in times[slot],
                'unique complete helper and bin call')
        helpers[t].add(h)
        times[slot].add(t)
        require(role['width'] == widths[h], 'owner actual width')
        cells = set(range(role['offset'], role['offset']+widths[h]))
        require(0 <= role['offset'] and role['offset']+widths[h] <= cap
                and not used[slot] & cells, 'owner footprint')
        used[slot].update(cells)
    require(len(owners) == 72*504 and all(helpers[t] == set(range(504)) for t in range(72)),
            'all helper roles')
    idle = Counter()
    for key, (cap, _) in plan['windows'].items():
        for port in range(112):
            cells = used[key, port]
            require(cells == set(range(len(cells))), 'compacted current footprint')
            if len(cells) < cap:
                idle[cap-len(cells)] += 1
    require(idle == IDLE, 'current idle profile')
    total = Counter({r: 72*c for r, c in local.items()})
    total.update(idle)
    require(dict(total) == {int(r): c for r, c in plan['profile'].items()}
            == {int(r): c for r, c in spec['expected']['global_profile'].items()},
            'global profile binding')
    mass = 112*sum(c*n for c, n in CAPACITIES.items())-72*sum(w*n for w, n in WIDTHS.items())
    require(mass == 115056 == 2397*48, 'idle mass')
    return Q(spec['expected']['complex_lower'])


def dual(prices=WIDTH_PRICES, capacity_prices=CAPACITY_PRICES):
    upper, tables = {}, {}
    for cap in CAPACITIES:
        dp = [None]*(cap+1)
        dp[0] = 0
        for fill in range(1, cap+1):
            choices = [dp[fill-w]+prices[w] for w in prices
                       if fill >= w and dp[fill-w] is not None]
            dp[fill] = max(choices) if choices else None
        tables[cap] = dp
        require(capacity_prices[cap]+dp[cap] <= 0, 'full-bin price')
        for fill, value in enumerate(dp):
            if value is not None:
                rem, score = cap-fill, capacity_prices[cap]+value
                upper[rem] = max(score, upper.get(rem, score))
    base = (112*sum(CAPACITIES[c]*capacity_prices[c] for c in CAPACITIES)
            + 72*sum(WIDTHS[w]*prices[w] for w in WIDTHS))
    require(base == -31136 and upper[0] == 0, 'dual base')
    exclusions = []
    for name, profile in [('all48', {48: 2397}), ('44plus4', {48: 2396, 44: 1, 4: 1})]:
        bound = sum(upper[r]*n for r, n in profile.items())
        require(bound < base, 'strict packing contradiction')
        exclusions.append(dict(name=name, idle=profile, upper=bound, required=base,
                               contradiction=base-bound))
    require(sum(upper[r]*n for r, n in IDLE.items()) == base, 'current dual equality')
    return dict(width_prices=prices, capacity_prices=capacity_prices,
                knapsack=tables, remainder_upper=upper, base=base, exclusions=exclusions)


def competitor_profiles():
    cases = [('t1-no44', {48: 2396, 43: 1, 5: 1}),
             ('t1-other-split', {48: 2396, 44: 1, 2: 2})]
    for t in range(2, 13):
        count, remainder = divmod(48*t, 44)
        profile = {48: 2397-t, 44: count}
        if remainder:
            profile[remainder] = profile.get(remainder, 0)+1
        cases.append((f't{t}-concavity-relaxation', profile))
    return cases


def moments(endpoint):
    require(0 < endpoint < 1, 'concavity domain')
    engine = load_engine('exact_intervals')
    weights = {}
    for r in range(1, 49):
        a, b = engine.log(Q(73, r))
        lo, hi = engine.exp(endpoint*a, endpoint*b)
        weights[r] = Q(r, 73*7168)*lo, Q(r, 73*7168)*hi

    def price(idle):
        profile = Counter({r: 72*n for r, n in LOCAL.items()})
        profile.update(idle)
        return (sum(n*weights[r][0] for r, n in profile.items()),
                sum(n*weights[r][1] for r, n in profile.items()))

    lo, hi = price(IDLE)
    require(hi < 1, 'current strict moment')
    cases = []
    for name, idle in competitor_profiles():
        require(sum(r*n for r, n in idle.items()) == 115056, 'competitor mass')
        lower, upper = price(idle)
        require(lower > 1, 'relaxed competitor exclusion')
        cases.append(dict(name=name, idle=idle, lower=str(lower), upper=str(upper),
                          strict_margin=str(lower-1)))
    period = 12*weights[44][0]-11*weights[48][1]
    require(period > 0, 'positive eleven-step period')
    return dict(endpoint=str(endpoint), current=[str(lo), str(hi)], competitors=cases,
                period_lower=str(period))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    verify_files()
    out = args.out.resolve()
    require(not out.exists() and not out.is_relative_to(ROOT), 'new external output directory')
    endpoint = validate_inputs(*inputs())
    result = dict(status='PASS_FIXED_SUPPLIER_OWNER_PROFILE_OPTIMALITY',
                  source_head='e516b1463606840a15f80aac1995d64ce0092e89',
                  widths=WIDTHS, local_profile=LOCAL, capacities=CAPACITIES,
                  idle_mass=115056, optimal_idle=IDLE, dual=dual(), moments=moments(endpoint),
                  scope='Fixed supplier, 72 calls and capacity inventory. Different idle profiles '
                        'fail the moment at the current admitted endpoint; matching profiles tie. '
                        'No changed supplier, dispatch, capacity or all-size theorem claim.')
    out.mkdir(parents=True)
    (out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS_FIXED_SUPPLIER_OWNER_PROFILE_OPTIMALITY')


if __name__ == '__main__':
    main()
