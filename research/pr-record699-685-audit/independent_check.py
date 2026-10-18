#!/usr/bin/env python3
"""Independent finite checks for PR699 and PR685; imports no repository code.

Apache-2.0. Rohan Guliani (@Rohansguliani), with substantial AI assistance
through Mux (OpenAI GPT-6 Astra and Claude Opus 5.5). Credits: Jeremy Kothe (#699/#676/#659), Chafik Boukhalfa
(#685/#660), icekylinx (#645), eumemic (#589), and their retained predecessors.
This checks finite witnesses, not the all-size multiplication theorem.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def require(condition, label):
    if not condition:
        raise ValueError(label)


@lru_cache(None)
def subspace(vectors):
    # Enumerate the vectors directly, independently of the auditors' elimination.
    result = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, 'nine-bit frame vector')
        result |= {x ^ vector for x in result}
    return frozenset(result)


def space(vectors):
    return subspace(tuple(vectors))


def dimension(vectors):
    size = len(vectors)
    require(size > 0 and size & (size - 1) == 0, 'subspace cardinality')
    return size.bit_length() - 1


def operands(gate):
    require(gate[0] in ('add', 'scale'), 'raw gate type')
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def raw_profile(word):
    v, helpers = word['report']['v'], word['report']['R']
    require((v, word['report']['h'], helpers) == (112, 9, 504), 'raw geometry')
    n = 2*v + helpers
    zero, full = space(()), space(range(1, 512))
    starts = [space((p,)) for p in word['ports']] + [zero]*(n-v)
    for register, frame in word['start_extra'].items():
        starts[int(register)] = space(frame)
    ends = [full]*v + [frozenset(x for x in full if (x & p).bit_count() % 2 == 0)
                      for p in word['ports']] + [full]*helpers
    for register, frame in word['helper_final'].items():
        ends[int(register)] = space(frame)
    current = starts.copy()
    paid = Counter()

    def visit(register, frame):
        require(0 <= register < n and current[register] <= frame, 'frame nesting')
        rank = dimension(frame) - dimension(current[register])
        if rank:
            paid[rank] += 1
        current[register] = frame

    for part in ('A', 'B'):
        if part == 'B':
            levels = {int(t): space(frame) for t, frame in word.get('target_levels', {}).items()}
            require(all(current[v+t] == levels.get(t, zero) for t in range(v)), 'cut target frames')
            for register, frame in zip(word['centers'], word['center_frames']):
                frame = space(frame)
                require(current[register] == frame, 'cut carrier frame')
                targets = {levels.get(g[1]-v, zero) for g in word['cut'] if g[2] == register}
                for target in sorted(targets, key=len, reverse=True):
                    require(target <= frame, 'nested center descent')
                    if target != frame:
                        paid[dimension(frame)-dimension(target)] += 1
                    frame = target
        for gate in word[part]:
            for register in operands(gate):
                visit(register, space(gate[-1]))
    early = dict(word['early_cleanup'])
    require(len(early) == len(word['early_cleanup']), 'distinct early gates')
    for index, frame in word['early_cleanup']:
        for register in operands(word['cleanup'][index]):
            visit(register, space(frame))
    for register, frame in enumerate(ends):
        visit(register, frame)
    require(all(ends[r] == full for i, gate in enumerate(word['cleanup']) if i not in early
                for r in operands(gate)), 'cleanup excludes ended helpers')
    widths = [dimension(ends[r])-dimension(starts[r]) for r in range(2*v, n)]
    require(all(0 < width <= 9 for width in widths), 'positive residual widths')
    require(dict(paid) == {int(k): v for k, v in word['report']['local_profile'].items()}, 'raw paid profile')
    require(sum(k*v for k, v in paid.items()) == word['report']['local_rank_mass'], 'raw rank mass')
    require(Counter(widths) == Counter({int(k): v for k, v in word['report']['width_inventory'].items()}), 'raw widths')
    return paid, widths


def end_of_b(word):
    rows = [{r: Q(1)} for r in range(2*word['report']['v'] + word['report']['R'])]
    for gate in word['A'] + word['cut'] + word['B']:
        target = gate[1]
        if gate[0] == 'scale':
            factor = Q(gate[2], gate[3])
            require(factor != 0, 'invertible scale')
            rows[target] = {k: factor*x for k, x in rows[target].items()}
        else:
            require(gate[0] == 'add' and target != gate[2], 'raw addition')
            factor = Q(gate[3], gate[4])
            for k, x in rows[gate[2]].items():
                value = rows[target].get(k, Q(0)) + factor*x
                if value:
                    rows[target][k] = value
                else:
                    rows[target].pop(k, None)
    return rows


def scalar_program_check(directory, paid):
    canonical = read(directory/'CANONICAL-WORD.json.gz')
    programs = read(directory/'LOCAL-PROGRAMS.json.gz')
    checks = read(directory/'LOCAL-CHECKS.json')
    n, v = 2*canonical['v'] + canonical['R'], canonical['v']
    results = {}
    for orientation, events in programs.items():
        rows = {('L', r): {r: Q(1)} for r in range(n)}
        primitives = macros = 0
        native_paid = Counter()
        for event in events:
            if event[0] in ('climb', 'center'):
                native_paid[event[-1]] += 1
            if event[0] != 'scalar':
                continue
            gate = event[1]
            kind, target = gate[0], tuple(gate[1])
            macros += 1
            if kind == 'clear':
                rows[target] = {}
                cost = 1
            elif kind == 'copy':
                rows[target] = dict(rows[tuple(gate[2])])
                cost = 1
            elif kind == 'scale':
                factor = Q(gate[2], gate[3])
                a, b = abs(factor.numerator), factor.denominator
                require(a > 0 and (a & (a-1)) == 0 and (b & (b-1)) == 0, 'binary unit scale')
                rows[target] = {k: factor*x for k, x in rows[target].items()}
                cost = abs(a.bit_length()-b.bit_length()) + int(factor < 0)
            else:
                require(kind == 'add', 'native scalar operation')
                source, factor = tuple(gate[2]), Q(gate[3], gate[4])
                a, b = abs(factor.numerator), factor.denominator
                require(target != source and a > 0 and (b & (b-1)) == 0, 'dyadic add')
                cost = 3 + (a.bit_length()-1) + a.bit_count() + (b.bit_length()-1)
                destination = rows.setdefault(target, {})
                for k, x in rows[source].items():
                    value = destination.get(k, Q(0)) + factor*x
                    if value:
                        destination[k] = value
                    else:
                        destination.pop(k, None)
            primitives += 2*cost
        for r in range(n):
            expected = {r: Q(1)}
            if orientation == 'forward' and v <= r < 2*v:
                expected[r-v] = Q(1)
            if orientation == 'backward' and r < v:
                expected[v+r] = Q(-1)
            require(rows['L', r] == expected, f'{orientation} exact endpoint row {r}')
        require(all(not row for r, row in rows.items() if r[0] != 'L'), 'private rows erased')
        require(native_paid == paid, 'raw/native paid profiles agree')
        require(primitives == checks[orientation]['real_component_primitive_bound'], 'Horner primitive invoice')
        require(macros == checks[orientation]['scalar_macros'], 'native scalar macro count')
        results[orientation] = dict(columns=n, macros=macros, real_primitives=primitives)
    return results


def owners_check(package, paid, widths):
    plan = read(package/'data/PLAN.json')
    roles = read(package/'data/OWNERS.json.gz')
    helpers, families, intervals = defaultdict(set), defaultdict(set), defaultdict(list)
    require(len(roles) == 72*504, 'complete role count')
    for row in roles:
        t, h, family = row['time'], row['helper'], row['family']
        rep, child, port = row['owner_replica'], row['child'], row['port']
        require(0 <= t < 72 and 0 <= h < 504 and 0 <= rep < 8 and 0 <= port < 112, 'role ranges')
        require(h not in helpers[t] and family not in families[t], 'unique helper and family per call')
        helpers[t].add(h)
        families[t].add(family)
        require((row['stage'], row['replica']) == tuple(plan['order'][t]), 'call chronology')
        require(family == rep*896 + (2*plan['pairs'][str(child)]+plan['sides'][str(child)])*112 + port, 'physical family')
        require(row['copy'] == rep*112+port and row['width'] == widths[h], 'owner width')
        capacity, times = plan['windows'][f'{rep},{child}']
        lo, hi = row['offset'], row['offset']+widths[h]
        require(t in times and 0 <= lo < hi <= capacity, 'owner window and capacity')
        intervals[rep, child, port].append((lo, hi))
    require(all(helpers[t] == set(range(504)) for t in range(72)), 'every helper exactly once')
    idle = Counter()
    for key, (capacity, _) in plan['windows'].items():
        rep, child = map(int, key.split(','))
        for port in range(112):
            end = 0
            for lo, hi in sorted(intervals[rep, child, port]):
                require(lo == end, 'nonoverlapping compact owner footprint')
                end = hi
            if end < capacity:
                idle[capacity-end] += 1
    global_paid = Counter({rank: count*72 for rank, count in paid.items()})
    global_paid.update(idle)
    require(dict(global_paid) == {int(k): v for k, v in plan['profile'].items()}, 'literal global profile')
    require(sum(r*c for r, c in global_paid.items()) == 520704, 'global rank mass')
    slots = Counter(tuple(row[k] for k in ('time', 'family', 'child', 'offset', 'width', 'owner_replica', 'port')) for row in roles)
    return global_paid, idle, slots


DENOM = 10**80


def down(q):
    return Q((q*DENOM).__floor__(), DENOM)


def up(q):
    return -down(-q)


@lru_cache(None)
def log_interval(q):
    require(q >= 1, 'log domain')
    powers = 0
    while q >= 2:
        q /= 2
        powers += 1

    def atanh_series(x):
        z = (x-1)/(x+1)
        term, total = z, Q(0)
        for j in range(96):
            total += 2*term/(2*j+1)
            term *= z*z
        return total, total + 2*term/(193*(1-z*z))

    lo, hi = atanh_series(q)
    if powers:
        ln2lo, ln2hi = atanh_series(Q(2))
        lo += powers*ln2lo
        hi += powers*ln2hi
    return down(lo), up(hi)


def exponential_interval(lo, hi):
    require(0 <= lo <= hi < Q(1, 10), 'exponential domain')

    def series(x):
        term = total = Q(1)
        for j in range(1, 25):
            term *= x/j
            total += term
        return total, term*x/25/(1-x/26)

    lower, _ = series(lo)
    upper, tail = series(hi)
    return down(lower), up(upper+tail)


def moment(profile, m, live, b, surcharge=False):
    lower = upper = Q(0)
    for rank, count in profile.items():
        lo, hi = log_interval(Q(m, rank))
        lo, hi = exponential_interval(b*lo, b*hi)
        lower += Q(rank*count, m*live)*lo
        upper += Q(rank*count, m*live)*hi
    if surcharge:
        lo, hi = log_interval(Q(m))
        lo, hi = exponential_interval(b*lo, b*hi)
        coefficient = Q(32*m*sum(profile.values()), 10**16*live)
        lower += coefficient*lo
        upper += coefficient*hi
    return lower, upper


def endpoint_check(profile, m, live, b, surcharge=False):
    _, upper = moment(profile, m, live, b, surcharge)
    next_lower, _ = moment(profile, m, live, b+Q(1, 10**24), surcharge)
    require(upper < 1 < next_lower, 'strict rational endpoint bracketing')
    return dict(lower=str(b), residual_upper=str(upper-1), next_residual_lower=str(next_lower-1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo699', type=Path, required=True)
    parser.add_argument('--repo685', type=Path, required=True)
    parser.add_argument('--replay699', type=Path, required=True)
    parser.add_argument('--replay685', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    p699 = args.repo699/'research/gauge44-promo-p6k4sw'
    p685 = args.repo685/'research/complex-promo4-cold72'
    promoted = read(args.replay699/'promo/promo/FULL-WORD.json.gz')
    p6n = read(args.replay699/'p6n/p6n/FULL-WORD.json.gz')
    sw4 = read(args.replay699/'sw4/sw4/FULL-WORD.json.gz')
    word685 = read(args.replay685/'promoted/FULL-WORD.json.gz')
    for part in ('A', 'B', 'cut', 'precondition', 'cleanup'):
        require([g[:-1] for g in p6n[part]] == [g[:-1] for g in promoted[part]], 'scalar-preserving promotion')
    require(end_of_b(promoted) == end_of_b(sw4), 'SW4 exact rational equality, all 728 input columns')
    require(promoted['start_extra'] == sw4['start_extra'] and promoted['helper_final'] == sw4['helper_final'], 'width-neutral SW4 endpoints')
    pp, pw = raw_profile(promoted)
    summaries, slots = {}, {}
    for label, package, word, directory in [('699', p699, sw4, args.replay699/'sw4/local'), ('685', p685, word685, args.replay685/'local')]:
        paid, widths = raw_profile(word)
        native = scalar_program_check(directory, paid)
        profile, idle, slots[label] = owners_check(package, paid, widths)
        spec = read(package/'data/SPEC.json')['expected']
        b, kappa = Q(spec['complex_lower']), Q(spec['kappa'])
        native_endpoint = endpoint_check(profile, 73, 7168, b)
        conservative_endpoint = endpoint_check(profile, 73, 7168, Q(spec['conservative_complex_lower']), True)
        bit = read(package/'inputs/PR589-EXPECTED.json')['nine']
        bit_profile = {int(k): v for k, v in bit['profile'].items()}
        c = Q(bit['bit_lower'])
        require(64*bit['bit']['live'] - sum(r*n for r, n in bit_profile.items()) == 10272, 'bit deficit')
        bit_endpoint = endpoint_check(bit_profile, 64, bit['bit']['live'], c, True)
        eta = Q(1, 10**24)
        s = min(c, (1-eta)*b) - Q(1, 10**27)
        a = s + (Q(384599, 10**10)-s)*s**7
        q = a*(1-2*eta)
        margin = (1-eta)*q/(1+q)
        ticks = margin*10**18
        require(ticks.numerator//ticks.denominator == int(kappa*10**18), 'κ is the exact floored 10^-18 grid point')
        require(kappa < margin < kappa + Q(1, 10**18), 'strict kappa grid and closed-form bootstrap')
        require(c > b and 73*7168 - sum(r*n for r, n in profile.items()) == 2560, 'complex binding and deficit')
        summaries[label] = dict(local_profile=dict(paid), width_inventory=dict(Counter(widths)), residual_width=sum(widths), native=native,
                                global_profile=dict(profile), idle=dict(idle), complex_endpoint=native_endpoint,
                                conservative_endpoint=conservative_endpoint, bit_endpoint=bit_endpoint, kappa=str(kappa))
        print('PASS independent finite checks PR'+label, str(kappa), flush=True)
    require(slots['699'] == slots['685'], 'PR685 owner transfer exactly preserves every physical slot')
    swpaid, swwidths = raw_profile(sw4)
    require(Counter(pw) == Counter(swwidths), 'SW4 width inventory unchanged')
    delta = {rank: swpaid[rank]-pp[rank] for rank in set(swpaid)|set(pp) if swpaid[rank] != pp[rank]}
    require(delta == {1: -24, 2: 16, 3: 8, 4: -8}, 'SW4 paid-rank delta')
    result = dict(status='PASS_INDEPENDENT_FINITE_RECOUNT_AND_RATIONAL_INTERVALS', credit='Rohan Guliani (@Rohansguliani)',
                  license='Apache-2.0', assistance='Substantial AI assistance through Mux (OpenAI GPT-6 Astra and Claude Opus 5.5)',
                  pr699_head='03e8d7ca494a083e5053cd6b1228f66b98414479', pr699_base='66849e1475c930fd7732b1a0067ffee7e1e95f60',
                  pr685_head='5fc2a0c4e10558f09f03a8e42559dcf8e381e57e', pr685_base='17ce0c79b7b51c2634b439ea5a2b754f09909693',
                  sw4_exact_rational_b_equality=True, sw4_rank_delta=delta, transferred_physical_slots=36288, results=summaries,
                  scope='No repository-code imports. Exact finite scalar maps, elementary gate invoices, enumerated GF(2) frame ranks, literal owners, independent rational log/exp enclosures and closed-form bootstrap. Not a full theorem or packing-optimality proof.')
    args.out.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
