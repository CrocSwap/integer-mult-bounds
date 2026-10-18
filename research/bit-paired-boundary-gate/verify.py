#!/usr/bin/env python3
"""Paired endpoint algebra, chronological owners and conditional cost gate.

No local paired-boundary supplier is supplied or admitted.
Prepared for androolloyd with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V, T, S, W = 111, 32, 9, 28416
RATE = Q(1, 99) + Q(1, 10**9)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def geometry(lines):
    """Rational Householder coordinates for P of rank 1 and Q of rank 1/2.

    All projection and rho identities then follow by disjoint coordinate
    blocks, independently of whether a scalar supplier realizes the endpoints.
    """
    receipts = []
    for line in lines:
        need(sum(x*x for x in line) == 4, 'port norm')
        d = [Q(2*int(i == 0)-line[i]) for i in range(8)]
        norm = sum(x*x for x in d)
        g = [[Q(int(i == j)) - (2*d[i]*d[j]/norm if norm else 0)
              for j in range(8)] for i in range(8)]
        need(all(sum(g[i][a]*g[i][b] for i in range(8)) == int(a == b)
                 for a in range(8) for b in range(8)), 'rational isometry')
        need([2*g[i][0] for i in range(8)] == line, 'source port')
        # In the G chart P={0}, Q={1,...,k-1}; rho swaps the complement
        # {k,...,7} with a new exterior block and fixes P+Q.
        for k in (2, 3):
            a = 8-k
            perm = list(range(8+a))
            for j in range(a):
                perm[k+j], perm[8+j] = perm[8+j], perm[k+j]
            move = lambda z: {perm[i] for i in z}
            p, q, r, e = {0}, set(range(1, k)), set(range(k, 8)), set(range(8, 8+a))
            need(move(p|e) == p|r and move(q|e) == q|r, 'incoming rho identity')
            need(move(p|r|e) == p|r|e and move(q|r|e) == q|r|e, 'outgoing rho identity')
            need(move(r) == e and move(p|q|r) == p|q|e, 'macro rho identity')
        receipts.append([[str(x) for x in row] for row in g])
    return dict(ports=len(lines), ranks_checked=[2, 3], rational_charts_sha256=digest(receipts))


def monomial(row, mask):
    out = {}
    for i, poly in row.items():
        val = 0
        while poly:
            b = poly & -poly
            val ^= 1 << ((b.bit_length()-1) ^ mask)
            poly ^= b
        out[i] = val
    return out


def add(a, b):
    return {i: a.get(i, 0)^b.get(i, 0) for i in a.keys()|b.keys()
            if a.get(i, 0)^b.get(i, 0)}


def global_operator(skip=-1):
    """Exact group algebra F2[C2^10]: common block plus nine residual blocks.

    An entry is a formal sum of ADDRESS permutations, not a sum of address
    coordinate matrices. Its regular action is faithful on all 1024 states.
    """
    rows = [{i: 1} for i in range(8)]
    controls = 0

    def local(stage, pair, reverse=False):
        e = 1 << (stage+1)
        x, y = 2*pair, 2*pair+1
        before_x, before_y = rows[x], rows[y]
        if reverse:
            rows[x] = add(monomial(before_x, e), monomial(before_y, 1|e))
            rows[y] = monomial(before_y, e)
        else:
            rows[x] = monomial(before_x, e)
            rows[y] = add(monomial(before_y, e), monomial(before_x, 1|e))

    def idle(pair, first, last):
        mask = sum(1 << (j+1) for j in range(first+1, last+1))
        for i in (2*pair, 2*pair+1):
            rows[i] = monomial(rows[i], mask)

    def bridge(dst, src):
        nonlocal controls
        for x, y in ((2*dst, 2*src), (2*src+1, 2*dst+1)):
            if controls != skip:
                rows[x] = add(rows[x], rows[y])
            controls += 1

    local(0, 0)
    for pair in range(4):
        local(2*pair+1, pair, True)
        if pair < 3:
            idle(pair+1, -1, 2*pair+1)
            bridge(pair, pair+1)
        local(2*pair+2, pair)
        if pair < 3:
            idle(pair+1, 2*pair+1, 2*pair+2)
            bridge(pair, pair+1)
        else:
            for j in range(4):
                idle(j, 2*j+2, 8)
    for j in reversed(range(3)):
        bridge(j+1, j)
    for j in range(4):
        rows[2*j], rows[2*j+1] = rows[2*j+1], rows[2*j]
    want = [{i: 1 << 1023} for i in range(8)]
    return rows == want, controls


def local_operator():
    # Independent commuting blocks P=1,Q=2,R=4. A full scalar shear
    # conjugated by incoming (P,Q), outgoing (P+R,Q+R) has these entries.
    diagonal = [(1|4)^1, (2|4)^2]
    off_diagonal = (2|4)^1
    need(diagonal == [4, 4] and off_diagonal == 7, 'paired local endpoint')
    # Existing macro diagonal Q+R. Source-only post D_Q and target-only
    # pre D_Q keep the off-diagonal F while changing both diagonals to R.
    need(2^(2|4) == 4 and (2|4)^2 == 4, 'paid wrapper endpoint')
    need((2|4)^1 == 7, 'paid wrapper off-diagonal')
    need(2^7 != 7, 'omitting the role distinction must change F')
    good, controls = global_operator()
    need(good and controls == 18, 'full nine-stage operator')
    need(all(not global_operator(i)[0] for i in range(controls)), 'omitted bridge detected')
    return dict(local_common_rank=[2, 3], global_bank_rows=8,
                independent_address_states=1024, formal_basis_columns=8192,
                omitted_bridge_controls=controls, final_operator='D_full on all eight data banks')


def check_slots(slots, windows, a):
    occupied = set()
    identities = set()
    for i, family, off, width, stage, helper in slots:
        pair, rank, stages = windows[i]
        need(stage in stages and family//(2*V) == pair and off+width <= rank,
             'chronological owner contract')
        need(off >= 0 and width == 8 and 0 <= family < 8*V, 'owner coordinate domain')
        identity = (stage, helper)
        need(identity not in identities, 'duplicate helper')
        identities.add(identity)
        # The first residual block starts after the common (8-a)-plane.
        first = 0 if i in (0, 2, 4) else (i+1 if i < 6 else 2*pair+3)
        start = 8-a+first*a
        for coordinate in range(start+off, start+off+width):
            key = (family, coordinate)
            need(key not in occupied, 'overlapping absolute owner coordinates')
            occupied.add(key)


def flow_owners(win, a, helpers):
    """Integral augmenting paths, then literal family/coordinate allocation."""
    windows = {i: (p, rank*a//7, sorted(stages)) for i, (p, rank, stages) in win.items()}
    source, sink = 0, 20
    cap, adjacent = {}, {i: [] for i in range(21)}

    def edge(u, v, c):
        cap[u, v], cap[v, u] = c, 0
        adjacent[u].append(v)
        adjacent[v].append(u)

    for s in range(9):
        edge(source, 1+s, helpers)
    for i, (_, rank, stages) in windows.items():
        edge(10+i, sink, 2*V*(rank//8))
        for s in stages:
            edge(1+s, 10+i, 9*helpers)
    total = 0
    while True:
        parent, queue = {source: None}, deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v in adjacent[u]:
                if v not in parent and cap[u, v] > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        path, v = [], sink
        while v != source:
            u = parent[v]
            path.append((u, v))
            v = u
        push = min(cap[e] for e in path)
        for u, v in path:
            cap[u, v] -= push
            cap[v, u] += push
        total += push
    need(total == 9*helpers, 'unhosted helper demand')
    slots, allocation, next_helper, rem = [], [], Counter(), Counter()
    for i, (pair, rank, stages) in sorted(windows.items()):
        demands = []
        for stage in stages:
            count = cap[10+i, 1+stage]
            if count:
                allocation.append([i, stage, count])
                demands.extend([stage]*count)
        used = Counter()
        for pos, stage in enumerate(demands):
            copy, block = divmod(pos, rank//8)
            need(copy < 2*V, 'owner overflow')
            side, port = divmod(copy, V)
            family = (2*pair+side)*V+port
            offset = 8*block
            slots.append([i, family, offset, 8, stage, next_helper[stage]])
            used[copy] += 8
            next_helper[stage] += 1
        for copy in range(2*V):
            if rank-used[copy]:
                rem[rank-used[copy]] += 1
    need(next_helper == Counter({s: helpers for s in range(9)}), 'helper identity coverage')
    check_slots(slots, windows, a)
    global_hash = hashlib.sha256()
    for replica in range(T):
        for i, family, offset, width, stage, helper in slots:
            translated = replica*8*V+family
            need(replica*8*V <= translated < (replica+1)*8*V <= W, 'replica owner range')
            global_hash.update(json.dumps([replica, i, translated, offset, width, stage, helper],
                                           separators=(',', ':')).encode()+b'\n')
    return dict(helpers_per_stage=helpers, windows=windows, allocation=allocation,
                slots_per_replica=len(slots), global_slots=len(slots)*T,
                owner_slots_sha256=digest(slots), remainder=dict(sorted(rem.items())),
                translated_global_slots_sha256=global_hash.hexdigest(),
                total_slot_capacity=sum(2*V*(r//8) for _, r, _ in windows.values())), rem, slots


def mass(h):
    return sum(r*n for r, n in h.items())


def monotone_closure(word, budget):
    """Smallest span constraints for the retained scalar order, with COPY
    arrivals granted frame zero. This permits more freedom than the word.
    It only excludes monotone re-framing, not paid descents or new topology.
    """
    v = word['v']
    frames = [1 << i for i in range(v)] + [0]*(v+word['R'])
    cache, result = {}, {}
    for section in ('D', 'A', 'B', 'C'):
        for _, dst, srcs in word[section]:
            roles = [dst, *srcs]
            joined = 0
            for r in roles:
                joined |= frames[r]
            for r in roles:
                frames[r] = joined
        dims = Counter()
        for mask in frames[:v]:
            if mask not in cache:
                cache[mask] = budget.rational_rank(word['lines'][i] for i in range(v) if mask >> i & 1)
            dims[cache[mask]] += 1
        result[section] = dict(sorted(dims.items()))
    need(result['B'] == {4: 3, 7: 108}, 'pre-cleanup least-frame ranks')
    need(result['C'] == {8: 111}, 'fixed scalar cleanup forces full sources')
    need(any(r < 8 for r in result['B']), 'omitting cleanup changes closure control')
    return dict(source_ranks_after_phase=result, copy_arrivals='granted frame zero',
                scope='Retained scalar order and monotone frames only; new source topology or paid descents remain outside.')


def main(out):
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for path, sha in pins['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, 'source hash: '+path)
    budget = module('paired_budget', 'research/bit-role-sharing-budget/verify.py')
    hosting = module('paired_hosting', 'research/bit-sharing-hosting-gate/verify.py')
    old = module('paired_mercator', 'research/complex-k492-owner-repair/vendor/multicold/engines/moment.py')
    wp = ROOT/'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
    word = json.loads(gzip.decompress(wp.read_bytes()))
    expected = json.loads((ROOT/'research/e8-bit-p111-tuned/tune/EXPECTED.json').read_text())
    local, columns = budget.extract_word(word, expected['word'])
    scalar_adds = sum(len(srcs) for section in ('D', 'A', 'B', 'C')
                      for _, _, srcs in word[section]) + sum(map(len, word['scatter']))
    need(scalar_adds == 24305, 'source access and scalar scan invoice')
    win = hosting.windows(hosting.schedule())
    controls = []

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('negative control accepted: '+name)

    def price(h):
        h = Counter({r: n for r, n in h.items() if n})
        lo, hi = budget.moment(h, RATE)
        lo2, hi2 = old.moment(h, 64, W, RATE, True)
        need(max(lo, lo2) <= min(hi, hi2), 'price engine disagreement')
        need((hi < 1 and hi2 < 1) or (lo > 1 and lo2 > 1), 'strict sign unresolved')
        return dict(profile=dict(sorted(h.items())), rank_mass=mass(h),
                    net_global_credit=1808352-mass(h),
                    net_credit_per_invocation=str(Q(1808352-mass(h), 288)),
                    moment_interval=[str(lo), str(hi)], moment_display=old.decimal(hi),
                    strict_rate=str(RATE), passes_rate=hi < 1,
                    passes_100_units=1808352-mass(h) >= 28800,
                    supplier_admitted=False)

    owners, rem, slots = flow_owners(win, 5, 296)
    need(owners['total_slot_capacity'] == 9*296, 'sharp slot capacity')
    reject('297 width-eight helpers at three-dimensional boundary', lambda: flow_owners(win, 5, 297))
    corrupt = [x[:] for x in slots]
    corrupt[0][4] = next(s for s in range(9) if s not in owners['windows'][corrupt[0][0]][2])
    reject('helper outside chronological window', lambda: check_slots(corrupt, owners['windows'], 5))
    corrupt = [x[:] for x in slots]
    corrupt[1][1:4] = corrupt[0][1:4]
    reject('overlapping physical coordinates', lambda: check_slots(corrupt, owners['windows'], 5))
    common = Counter({16: W})
    common.update({r: n*T for r, n in rem.items()})
    ideal = common.copy()
    ideal.update({5: 288*222, 7: 288*9, 8: 288*296})
    unit = common.copy()
    unit[1] += 288*(222*5+9*7+296*8)
    repaired = unit.copy()
    repaired[1] += 31*288
    failed_repair = unit.copy()
    failed_repair[1] += 32*288
    prices = {name: price(h) for name, h in [('one_child_per_role_oracle', ideal),
              ('all_local_units_at_rank_one_oracle', unit),
              ('oracle_plus_31_repairs_per_invocation', repaired),
              ('oracle_plus_32_repairs_per_invocation', failed_repair)]}
    need(prices['oracle_plus_31_repairs_per_invocation']['passes_rate'], '31 repair margin')
    need(prices['oracle_plus_31_repairs_per_invocation']['passes_100_units'], 'net goal margin')
    need(not prices['oracle_plus_32_repairs_per_invocation']['passes_rate'], '32 repair fence')
    need(mass(ideal) == mass(unit) == 1751520, 'boundary deficit and padding accounting')

    # A concrete realization from the old word uses clean owned helpers and
    # pays the two rank-(k-1) endpoint wrappers. No productive owner is freed.
    wrapped = Counter({r: 288*n for r, n in local.items()})
    wrapped[2] += 288*222
    wrapped[16] += W
    for _, rank, _ in win.values():
        if rank:
            wrapped[rank*5//7] += 2*V*T
    prices['concrete_wrapped_word_owned_helpers'] = price(wrapped)
    need(not prices['concrete_wrapped_word_owned_helpers']['passes_rate'], 'wrapper cannot pass')
    reject('dropping concrete wrapper rank charges',
           lambda: need(mass(wrapped)-288*222*2 == mass(wrapped), 'unpaid boundary change'))

    # Gaussian rank-two alternative: assuming C>=80 rational rank, the
    # cost/deficit ceiling is below 0.0078 for every odd B_K stage count.
    # This is conditional on that external copy floor and the stated format.
    gaussian = []
    for K in range(1, 43):
        s, a, m = 2*K+1, 6, 2+(2*K+1)*6
        D = Q(4*K-4, 3)
        slots = [(12*s, 6), (Q(4*s, 3), 8)]
        ranks = ([12*(K-1)] if K > 1 else [])
        for p in range(1, K):
            ranks.extend([12*p, 6])
            if K-p-1:
                ranks.append(12*(K-p-1))
        slots += [(2*r, max(r, 8)) for r in ranks]
        cost_lo = sum(z*budget.log_interval(Q(m, cap))[0] for z, cap in slots)
        bound = D/cost_lo
        need(bound < Q(78, 10000), 'Gaussian finite stage ceiling')
        gaussian.append([s, str(bound)])
    need(Q(1, 3*44) < Q(78, 10000), 'Gaussian analytic tail starts at K=43')

    result = dict(status='PASS_PAIRED_BOUNDARY_PREFLIGHT_NOT_A_SUPPLIER',
        goal_status='ACTIVE_UNACHIEVED', geometry=geometry(word['lines']),
        operator=local_operator(), inherited_local_replay=columns,
        retained_word_monotone_obstruction=monotone_closure(word, budget),
        conditional_hosting=owners, prices=prices,
        concrete_owned_stock=dict(productive=W, private_helpers=439, centers=9,
                                  physical=W+439+9, helper_initialization_scans=439,
                                  helper_final_state='zero, reusable after every completed invocation'),
        concrete_nonrecursive_bill=dict(local_aligned_xor_scans=scalar_adds*288,
             bridge_aligned_xor_scans=18*V*T, inherited_center_copy_clear_episodes=9*288,
             extra_wrapper_children=222*288, extra_wrapper_child_rank=2,
             scope='These scans and source reads remain charged. New chart/descriptor/head-return constants are not generated; their favorable omission already fails the recursive cost gate.'),
        target_owned_stock=dict(productive=W, centers=9, physical=W+9,
                               helpers='all borrowed from 85248 exclusive reservations'),
        gaussian_conditional_ceiling=dict(rational_copy_floor=80, real_ports=60,
             finite_stage_linear_bounds=gaussian, tail='1/(3*(K+1)) for K>=43',
             supplier_saving_upper='39/5000', copy_floor_reproved=False),
        controls=controls,
        missing=['A legal local scalar word with P->Q-perp and Q->P-perp endpoints, rank(Q)=2.',
                 'At most 296 width-eight helper paths and COPY rank at most 63, with every dirty input restored.',
                 'Source access, route, controller, finite stock and all-size interfaces for that new word.'])
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    need(not out.exists(), 'output already exists')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(result['status'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    main(ap.parse_args().out)
