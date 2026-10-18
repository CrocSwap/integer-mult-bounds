"""Separate bounded certificate checker; only Python standard-library imports.

Brian Ross with substantial OpenAI Codex assistance, Apache-2.0.
Methodological adaptation (no copied code): Brian Ross's Krenn independent
verifier/semantic-corruption controls at ab446724a61a293a3268c63b9e9e721c6a360561,
and ThetaTwist exact arithmetic at b4ec6c13088b89961834cc675b44b81372199b02.
This is a separate agent-authored implementation, not a human independent proof.

Arithmetic proof: for 1 <= x <= 2, z=(x-1)/(x+1) is in [0,1/3].
log(x) = 2 sum_{j>=0} z^(2j+1)/(2j+1); after K terms its positive
tail is <= 2 z^(2K+1)/((2K+1)(1-z*z)). Range reduction adds k log(2).
For 0<=t<=1, exp(t)=sum_{j>=0}t^j/j!; after degree K the positive
tail is <= [t^(K+1)/(K+1)!]/[1-t/(K+2)]. Every computed term is
rounded outwards using exact integer division on the scale 10**90.
Thus the returned bounds are rational enclosures, without float/libm calls.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import gzip
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE = 10 ** 90
LOG_TERMS = 110
EXP_DEGREE = 72
LAMBDA = Q(32 * 64 ** 2, 10 ** 16)
BASE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
PR555 = {1: 1321, 2: 1342, 3: 80, 4: 47, 5: 102, 6: 10, 7: 18}
IDLE = {2: 13920, 4: 14208, 42: 288, 6: 14208, 7: 21312}
LOW = Q(1733427039589844234749, 10 ** 24)
HIGH = LOW + Q(1, 10 ** 24)
INVENTORY_DIGEST = 'bd1d8b0e52cee5502b12bba071a4b4ab64d1c4cf7e909ed3c3d28ee1058da1e2'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ceilq(x):
    return -(-x.numerator // x.denominator)


def roundout(lo, hi):
    require(lo <= hi, 'invalid independent interval')
    return Q((lo * SCALE).numerator // (lo * SCALE).denominator, SCALE), Q(ceilq(hi * SCALE), SCALE)


def log_reduced(x):
    require(Q(1) <= x <= Q(2), 'log series argument')
    z = (x - 1) / (x + 1)
    term, total = z, Q(0)
    for j in range(LOG_TERMS):
        total += term / (2 * j + 1)
        term *= z * z
    tail = 2 * term / ((2 * LOG_TERMS + 1) * (1 - z * z))
    return roundout(2 * total, 2 * total + tail)


@lru_cache(maxsize=128)
def log_interval(x):
    require(Q(1) <= x <= Q(64), 'fixed log argument')
    k = 0
    while x > 2:
        x /= 2
        k += 1
    lo, hi = log_reduced(x)
    if k:
        l2, h2 = log_reduced(Q(2))
        lo, hi = lo + k * l2, hi + k * h2
    return lo, hi


def exp_point(t):
    require(0 <= t <= 1, 'exp series argument')
    # term integers enclose SCALE*t**j/j!, including all previous rounding.
    term_lo = term_hi = SCALE
    sum_lo = sum_hi = SCALE
    for j in range(1, EXP_DEGREE + 1):
        xlo, xhi = term_lo * t / j, term_hi * t / j
        term_lo = xlo.numerator // xlo.denominator
        term_hi = ceilq(xhi)
        sum_lo += term_lo
        sum_hi += term_hi
    tail_hi = Q(term_hi, SCALE) * t / (EXP_DEGREE + 1) / (1 - t / (EXP_DEGREE + 2))
    return Q(sum_lo, SCALE), Q(sum_hi, SCALE) + tail_hi


@lru_cache(maxsize=512)
def power_interval(base, lower, upper):
    require(0 <= lower <= upper <= Q(1, 10), 'fixed exponent interval')
    ll, lh = log_interval(Q(base))
    return exp_point(lower * ll)[0], exp_point(upper * lh)[1]


def globalize(local):
    result = dict(IDLE)
    for r, c in local.items():
        require(type(r) is int and 1 <= r <= 64 and type(c) is int and c >= 0, 'profile domain')
        result[r] = result.get(r, 0) + 288 * c
    return result


def residual(local, a):
    """Direct F, independent of the deficit/fee decomposition in the pricer."""
    n = globalize(local)
    lo = hi = Q(-64 * 28416)
    for r, c in sorted(n.items()):
        pl, ph = power_interval(Q(64, r), a, a)
        lo += c * r * pl
        hi += c * r * ph
    pl, ph = power_interval(Q(64), a, a)
    lo += LAMBDA * sum(n.values()) * pl
    hi += LAMBDA * sum(n.values()) * ph
    return roundout(lo, hi)


def signed_price(delta, lower=LOW, upper=HIGH):
    lo = hi = LAMBDA * sum(delta.values())
    for r, c in sorted(delta.items()):
        require(type(r) is int and 1 <= r <= 64 and type(c) is int, 'signed delta domain')
        pl, ph = power_interval(Q(r), lower, upper)
        wl, wh = Q(r) / ph, Q(r) / pl
        lo += c * (wl if c >= 0 else wh)
        hi += c * (wh if c >= 0 else wl)
    return roundout(lo, hi)


def status_of(interval):
    lo, hi = interval
    require(lo <= hi, 'reversed interval')
    return 'BETTER' if hi < 0 else 'WORSE_OR_EQUAL' if lo >= 0 else 'UNRESOLVED'


def require_encloses(claim, independently_computed, label):
    a, b = map(Q, claim)
    lo, hi = independently_computed
    require(a <= lo <= hi <= b, label + ': claimed interval misses independent enclosure')


def audit_inventory(manifest):
    # The canonical manifest digest freezes the complete set and all metadata;
    # merely iterating a caller-supplied list would fail to detect omissions.
    canonical = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
    require(hashlib.sha256(canonical).hexdigest() == INVENTORY_DIGEST, 'bad source inventory')
    require(manifest['schema'] == 'pr1048-certified-repair-inputs-v1' and len(manifest['inputs']) == 36, 'inventory schema or count')
    for path, pin in manifest['inputs'].items():
        data = (ROOT / path).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source bytes: ' + path)
        if 'git_blob' in pin:
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            require(hashlib.sha1(blob).hexdigest() == pin['git_blob'], 'Git source bytes: ' + path)
    return len(manifest['inputs'])


def audit_pricing(c):
    require(c['status'] == 'PASS_CERTIFIED_REFERENCE_PRICING', 'pricing status')
    require({int(r): n for r, n in c['baseline_profile'].items()} == BASE, 'PR589 local profile')
    require({int(r): n for r, n in c['global_profile'].items()} == globalize(BASE), 'replication and idle profile')
    require(c['factor'] == 288 and Q(c['lambda_value']) == LAMBDA, 'pipeline or surcharge omitted')
    bounds = tuple(map(Q, c['baseline_bracket']['certified_bracket']))
    require(c['baseline_bracket']['status'] == 'CERTIFIED', 'reference status')
    endpoints = [residual(BASE, x) for x in bounds]
    require(endpoints[0][1] < 0 < endpoints[1][0], 'actual strict endpoint signs')
    require(bounds == (LOW, HIGH), 'PR589 24-digit bracket shifted')
    cases = {
        'PR555_vs_PR589': {r: PR555.get(r, 0) - BASE.get(r, 0) for r in set(PR555) | set(BASE)},
        'abstract_mass_preserving_improvement': {1: -3, 3: 1},
        'abstract_mass_preserving_worsening': {1: 3, 3: -1},
        'exact_profile_tie': {},
    }
    require(set(c['comparisons']) == set(cases), 'comparison coverage')
    results = {}
    for name, delta in cases.items():
        candidate = {r: BASE.get(r, 0) + delta.get(r, 0) for r in set(BASE) | set(delta)}
        require(residual(candidate, Q(0))[1] < 0, 'candidate positive root')
        interval = signed_price(delta)
        claim = c['comparisons'][name]
        require(claim['status'] == status_of(interval), 'incorrect signed comparison: ' + name)
        require_encloses(claim['interval'], interval, name)
        results[name] = dict(status=status_of(interval), interval=list(map(str, interval)))
    require(results['exact_profile_tie']['interval'] == ['0', '0'], 'exact zero-delta equality')
    wide = signed_price({1: -14, 2: 15, 4: -4}, Q(0), Q(1, 10))
    require(wide[0] < 0 < wide[1], 'wide comparison unresolved')
    require_encloses(c['wide_unresolved'], wide, 'wide comparison')
    return dict(status='PASS_SEPARATE_RATIONAL_PRICING_CHECK',
                endpoint_residuals=[list(map(str, x)) for x in endpoints],
                comparisons=results, wide_status=status_of(wide),
                wide_interval=list(map(str, wide)))


def audit_claim(claim):
    delta = {int(r): c for r, c in claim['delta'].items()}
    interval = signed_price(delta, Q(claim['lower']), Q(claim['upper']))
    require(claim['status'] == status_of(interval), 'unresolved sign promoted')


class WordCheck:
    """Separate integer row elimination, event replay and literal-slot checker.

Integer elimination multiplies a row by the pivot, subtracts its pivot entry
times the pivot row, then removes its gcd. These are exact rank-preserving
row operations over Q. Unlike coverage.py this uses no Fraction row basis,
register-sequence routine, bisection on touch positions, or legacy imports.
"""
    def __init__(self):
        path = ROOT / 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
        self.word = json.loads(gzip.decompress(path.read_bytes()))
        self.word_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        w = self.word
        self.catalog = tuple(sum(1 << j for j in f) for f in w['frames'])
        self.full = (1 << len(w['lines'])) - 1
        self.ranks = {}
        self.closures = {}
        self.initial = {}
        for section in 'AB':
            flat = [(self.catalog[f], t, u) for f, t, us in w[section] for u in us]
            self.initial[section] = [((section, i), f, t, u) for i, (f, t, u) in enumerate(flat)]
        self.copy_frames = self.snapshot(self.initial)

    def rank(self, mask):
        if mask not in self.ranks:
            rows = [list(v) for i, v in enumerate(self.word['lines']) if mask >> i & 1]
            require(all(type(x) is int for v in rows for x in v), 'integer line coordinates')
            degree = 0
            for col in range(len(self.word['lines'][0])):
                pivot = next((i for i in range(degree, len(rows)) if rows[i][col]), None)
                if pivot is None:
                    continue
                rows[degree], rows[pivot] = rows[pivot], rows[degree]
                for i in range(degree + 1, len(rows)):
                    if not rows[i][col]:
                        continue
                    a, b = rows[degree][col], rows[i][col]
                    row = [a*x - b*y for x, y in zip(rows[i], rows[degree])]
                    divisor = 0
                    for x in row:
                        divisor = gcd(divisor, x)
                    rows[i] = [x // divisor for x in row] if divisor else row
                degree += 1
            self.ranks[mask] = degree
        return self.ranks[mask]

    def closure(self, mask):
        if mask not in self.closures:
            degree = self.rank(mask)
            self.closures[mask] = sum(1 << j for j in range(len(self.word['lines']))
                                      if self.rank(mask | (1 << j)) == degree)
        return self.closures[mask]

    def before(self, state, section):
        current = [self.catalog[i] for i in self.word['start']]
        for f, t, us in self.word['D']:
            for r in (t, *us):
                current[r] = self.catalog[f]
        if section == 'B':
            for _, f, t, u in state['A']:
                current[t] = current[u] = f
        return current

    def snapshot(self, state):
        current = self.before(state, 'B')
        return {r: current[r] for r in self.word['ret']}

    def after(self, state, section):
        current = [self.catalog[i] for i in self.word['final']]
        v = self.word['v']
        for _, _, t, u in state['A'] + state['B']:
            if not v <= t < 2*v:
                current[t] = current[u] = self.full
        if section == 'A':
            for _, f, t, u in reversed(state['B']):
                current[t] = current[u] = f
        return current

    def profile(self, state, selected=None):
        current = [self.catalog[i] for i in self.word['start']]
        profile = Counter()
        def touch(r, f):
            if selected is not None and r not in selected:
                return
            a = current[r]
            require(a & ~f == 0, 'independent word frame descent')
            if a != f:
                change = self.rank(f) - self.rank(a)
                require(change >= 0, 'independent rank descent')
                if change:
                    profile[change] += 1
                current[r] = f
        for f, t, us in self.word['D']:
            for r in (t, *us):
                touch(r, self.catalog[f])
        for _, f, t, u in state['A']:
            touch(t, f)
            touch(u, f)
        for r in self.word['ret']:
            if selected is None or r in selected:
                profile[self.rank(current[r])] += 1
        for _, f, t, u in state['B']:
            touch(t, f)
            touch(u, f)
        v = self.word['v']
        for _, _, t, u in reversed(state['A'] + state['B']):
            if not v <= t < 2*v:
                touch(t, self.full)
                touch(u, self.full)
        for r, f in enumerate(self.word['final']):
            touch(r, self.catalog[f])
        profile.pop(0, None)
        return dict(profile)

    @staticmethod
    def index(state, identity):
        return next(i for i, op in enumerate(state[identity[0]]) if op[0] == identity)

    def apply(self, state, identity, slot, frame):
        result = {s: list(ops) for s, ops in state.items()}
        op = result[identity[0]].pop(self.index(state, identity))
        result[identity[0]].insert(slot, (identity, frame, op[2], op[3]))
        return result

    def literal_moves(self, state, identity):
        section = identity[0]
        ops = state[section]
        index = self.index(state, identity)
        _, old_frame, t, u = ops[index]
        # A forbidden crossing blocks all slots beyond it. This scans every
        # other operation once instead of using the primary commute walker.
        blocked = [i for i, (_, _, a, b) in enumerate(ops)
                   if i != index and (t == b or a == u)]
        first = max((i + 1 for i in blocked if i < index), default=0)
        last = min((i - 1 for i in blocked if i > index), default=len(ops)-1)
        rest = ops[:index] + ops[index+1:]
        pre, post = self.before(state, section), self.after(state, section)
        previous, following, numbers = {}, {}, {}
        for r in (t, u):
            previous[r] = [pre[r]]
            numbers[r] = [0]
            for _, f, a, b in rest:
                touches = r in (a, b)
                previous[r].append(f if touches else previous[r][-1])
                numbers[r].append(numbers[r][-1] + touches)
            following[r] = [post[r]] * (len(rest)+1)
            for j in range(len(rest)-1, -1, -1):
                _, f, a, b = rest[j]
                following[r][j] = f if r in (a, b) else following[r][j+1]
        domains, moves = {}, []
        for slot in range(first, last+1):
            lower = previous[t][slot] | previous[u][slot]
            upper = following[t][slot] & following[u][slot]
            if lower & ~upper:
                continue
            key = lower, upper
            if key not in domains:
                domains[key] = [m for m in sorted(set(self.catalog) | {self.closure(lower)})
                                if lower & ~m == 0 and m & ~upper == 0]
            for mask in domains[key]:
                if slot == index and mask == old_frame:
                    continue
                if section == 'A':
                    resulting = {r: previous[r][-1] if numbers[r][-1] > numbers[r][slot] else mask
                                 for r in (t, u) if r in self.copy_frames}
                    if any(f != self.copy_frames[r] for r, f in resulting.items()):
                        continue
                moves.append((slot, mask, (numbers[t][slot], numbers[u][slot])))
        return moves

    def packed_apply(self, state, move):
        identity = tuple(move['operation'])
        require(self.index(state, identity) == move['current_index'], 'stable operation identity changed')
        frame = int(move['frame_mask'])
        old_id = self.catalog.index(frame) if frame in self.catalog else None
        require(move['original_frame_id'] == old_id, 'frame identity changed')
        require(any(q == move['slot'] and m == frame for q, m, _ in self.literal_moves(state, identity)),
                'packed move outside literal domain')
        after = self.apply(state, identity, move['slot'], frame)
        require(self.snapshot(after) == self.copy_frames, 'retained COPY snapshot changed')
        return after


def profile_delta(left, right):
    return tuple((r, right.get(r, 0)-left.get(r, 0)) for r in sorted(set(left) | set(right))
                 if right.get(r, 0) != left.get(r, 0))


def candidate_hash(moves):
    rows = [[q, str(m), list(sig)] for q, m, sig in moves]
    return hashlib.sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def validate_reconstructed_receipt(c, reconstructed):
    """Compare claims to already computed semantics, never to refreshed hashes."""
    domains = {}
    for row in c['second']:
        key = json.dumps(row['first'], sort_keys=True)
        domains.setdefault(key, []).append((tuple(row['second_operation']), row['candidate_sha256'], row['legal_literal_moves']))
    require(domains == reconstructed['domains'], 'mandatory reconstructed second-operation domain differs')
    advertised = {tuple(sorted((int(r), n) for r, n in row['delta'].items())): row['occurrences']
                  for row in c['exact_local_profile_deltas']}
    require(len(advertised) == len(c['exact_local_profile_deltas']) and advertised == reconstructed['histogram'],
            'reconstructed semantic profile histogram differs')


def coverage_controls(c, reconstructed):
    """Semantic mutations refresh numerical summaries, retaining no hash oracle."""
    rejected = []
    def check(name, corrupted):
        try:
            validate_reconstructed_receipt(corrupted, reconstructed)
        except ValueError as exc:
            rejected.append(dict(name=name, reason=str(exc)))
        else:
            raise ValueError('semantic coverage corruption accepted: ' + name)
    def refresh_summaries(x):
        t = x['totals']
        t['second_moves'] = sum(row['legal_literal_moves'] for row in x['second'])
        t['second_operation_rows'] = len(x['second'])
        t['cross_section_second_moves'] = sum(row['legal_literal_moves'] for row in x['second'] if row['cross_section'])
        t['unique_local_deltas'] = t['full_replayed_delta_classes'] = len(x['exact_local_profile_deltas'])
        t['exact_profile_tie_occurrences'] = sum(row['occurrences'] for row in x['exact_local_profile_deltas'] if not row['delta'])
        t['price_status_occurrences'] = {s: sum(row['occurrences'] for row in x['exact_local_profile_deltas']
                                              if row['certified_price']['status'] == s)
                                       for s in ('BETTER', 'WORSE_OR_EQUAL', 'UNRESOLVED')}
        t['strictly_worse_occurrences'] = sum(row['occurrences'] for row in x['exact_local_profile_deltas']
                                             if Q(row['certified_price']['interval'][0]) > 0)
        grouped = {}
        for row in x['second']:
            grouped.setdefault(json.dumps(row['first'], sort_keys=True), []).append(row)
        for pair in x['equal_profile_different_continuations']:
            for side in ('left', 'right'):
                claim = pair[side]
                rows = grouped.get(json.dumps(claim['first'], sort_keys=True), [])
                data = [[row['second_operation'], row['candidate_sha256'], row['legal_literal_moves']] for row in rows]
                claim['continuation_moves'] = sum(row[2] for row in data)
                claim['continuation_sha256'] = hashlib.sha256(json.dumps(data, separators=(',', ':')).encode()).hexdigest()
    x = deepcopy(c)
    removed = next(row for row in x['second'] if row['cross_section'])
    x['second'].remove(removed)
    key = json.dumps(removed['first'], sort_keys=True), tuple(removed['second_operation'])
    removed_histogram = reconstructed['row_histograms'][key]
    for row in x['exact_local_profile_deltas']:
        delta = tuple(sorted((int(r), n) for r, n in row['delta'].items()))
        row['occurrences'] -= removed_histogram.get(delta, 0)
    x['exact_local_profile_deltas'] = [row for row in x['exact_local_profile_deltas'] if row['occurrences']]
    refresh_summaries(x)
    check('cross_section_row_removed_with_refreshed_counts_digests_and_price_totals', x)
    x = deepcopy(c)
    row = next(row for row in x['exact_local_profile_deltas'] if row['delta'])
    delta = {int(r): n for r, n in row['delta'].items()}
    delta[1] = delta.get(1, 0) + 11
    row['delta'] = {str(r): n for r, n in delta.items()}
    interval = signed_price(delta)
    row['certified_price'] = dict(status=status_of(interval), interval=list(map(str, interval)), reason='refreshed corrupted profile price')
    refresh_summaries(x)
    check('profile_delta_altered_with_refreshed_rational_price_and_totals', x)
    return rejected


def audit_coverage(c):
    require(c['status'] == 'BOUNDED_COVERAGE_RECONSTRUCTED', 'coverage status')
    require(c['scope']['global_neighborhood_claim'] is False and c['scope']['steinberg_in_scope'] is False,
            'bounded coverage promoted')
    require(c['scope']['all_literal_slots'] is True, 'literal slot coverage removed')
    require(tuple(map(Q, c['reference_root_bracket'])) == (LOW, HIGH), 'coverage root bracket')
    checker = WordCheck()
    require(c['source_word_sha256'] == checker.word_sha, 'coverage source word')
    base_profile = checker.profile(checker.initial)
    require(base_profile == BASE, 'separate integer baseline replay')
    require({int(r): n for r, n in c['independent_local_profile'].items()} == BASE, 'coverage baseline claim')
    first_ids = [('A', 2028), ('A', 2076), ('A', 2129), ('A', 281), ('B', 1)]
    require([tuple(x['operation']) for x in c['first']] == first_ids, 'first operation inventory')
    effects = Counter()
    def check_row(state, identity, row, earlier_regs=()):
        moves = checker.literal_moves(state, identity)
        require(len(moves) == row['legal_literal_moves'], 'literal candidate count')
        require(candidate_hash(moves) == row['candidate_sha256'], 'literal candidate domain digest')
        regs = set(state[identity[0]][checker.index(state, identity)][2:]) | set(earlier_regs)
        baseline = checker.profile(checker.initial, regs)
        classes = {}
        row_histogram = Counter()
        for slot, frame, sig in moves:
            key = frame, sig
            if key not in classes:
                after = checker.apply(state, identity, slot, frame)
                classes[key] = profile_delta(baseline, checker.profile(after, regs))
            effects[classes[key]] += 1
            row_histogram[classes[key]] += 1
        require(len(classes) == row['frame_touch_classes'], 'frame/touch class count')
        require(len(set(classes.values())) == row['profile_delta_classes'], 'profile class count')
        return moves, set(classes.values()), row_histogram
    for row, identity in zip(c['first'], first_ids):
        check_row(checker.initial, identity, row)
    groups = {}
    for row in c['second']:
        key = json.dumps(row['first'], sort_keys=True)
        groups.setdefault(key, []).append(row)
    require(len(groups) == c['scope']['selected_first_states'] == 10, 'selected first state inventory')
    cross_count = 0
    continuations = {}
    reconstructed = dict(domains={}, histogram=None, row_histograms={})
    for packed, rows in groups.items():
        first = json.loads(packed)
        identity = tuple(first['operation'])
        require(identity in first_ids, 'undeclared selected first operation')
        after = checker.packed_apply(checker.initial, first)
        regs = set(after[identity[0]][checker.index(after, identity)][2:])
        expected = [op[0] for section in 'AB' for op in after[section] if regs.intersection(op[2:])]
        require([tuple(row['second_operation']) for row in rows] == expected, 'both-section adjacent identity inventory')
        reachable = set()
        continuation_rows = []
        for row, second in zip(rows, expected):
            require(row['cross_section'] is (second[0] != identity[0]), 'cross-section label')
            moves, profiles, row_histogram = check_row(after, second, row, regs)
            reconstructed['row_histograms'][packed, second] = row_histogram
            reachable.update(profiles)
            continuation_rows.append([list(second), candidate_hash(moves), len(moves)])
            if second[0] != identity[0]:
                cross_count += len(moves)
        continuations[packed] = dict(profiles=reachable,
                                     first_delta=profile_delta(base_profile, checker.profile(after)),
                                     digest=hashlib.sha256(json.dumps(continuation_rows, separators=(',', ':')).encode()).hexdigest(),
                                     moves=sum(row[2] for row in continuation_rows))
        reconstructed['domains'][packed] = [(tuple(row[0]), row[1], row[2]) for row in continuation_rows]
    advertised = {}
    statuses = Counter()
    strict_worse = 0
    for row in c['exact_local_profile_deltas']:
        delta = {int(r): n for r, n in row['delta'].items()}
        key = tuple(sorted(delta.items()))
        require(key not in advertised, 'duplicate advertised delta')
        advertised[key] = row['occurrences']
        interval = signed_price(delta)
        price = row['certified_price']
        require(price['status'] == status_of(interval), 'coverage signed comparison')
        require_encloses(price['interval'], interval, 'coverage signed interval')
        candidate = {r: BASE.get(r, 0) + delta.get(r, 0) for r in set(BASE) | set(delta)}
        require(residual(candidate, Q(0))[1] < 0, 'coverage positive root')
        statuses[status_of(interval)] += row['occurrences']
        if interval[0] > 0:
            strict_worse += row['occurrences']
    require(dict(effects) == advertised, 'independent complete profile-delta histogram')
    reconstructed['histogram'] = dict(effects)
    validate_reconstructed_receipt(c, reconstructed)
    totals = c['totals']
    require(totals['first_moves'] == sum(x['legal_literal_moves'] for x in c['first']), 'first total')
    require(totals['second_moves'] == sum(x['legal_literal_moves'] for x in c['second']), 'second total')
    require(totals['second_operation_rows'] == len(c['second']), 'second row total')
    require(totals['cross_section_second_moves'] == cross_count, 'cross-section total')
    require(totals['unique_local_deltas'] == len(effects) and totals['exact_profile_tie_occurrences'] == effects[()], 'delta totals')
    require(totals['price_status_occurrences'] == {k: statuses[k] for k in ('BETTER', 'WORSE_OR_EQUAL', 'UNRESOLVED')}, 'status totals')
    require(totals['strictly_worse_occurrences'] == strict_worse, 'strict worse total')
    witnesses = c['witnesses'] + c['cross_section_omission_witnesses']
    for witness in witnesses:
        after = checker.packed_apply(checker.initial, witness['first'])
        final = checker.packed_apply(after, witness['second'])
        delta = dict(profile_delta(base_profile, checker.profile(final)))
        require(delta == {int(r): n for r, n in witness['local_delta'].items()}, 'full witness replay')
        interval = signed_price(delta)
        require(witness['certified_price']['status'] == status_of(interval), 'witness price')
        require_encloses(witness['certified_price']['interval'], interval, 'witness interval')
    profile_set_differences = []
    def unpack_deltas(values):
        return {tuple(sorted((int(r), n) for r, n in d.items())) for d in values}
    for pair in c['equal_profile_different_continuations']:
        sides = []
        for side in ('left', 'right'):
            claim = pair[side]
            key = json.dumps(claim['first'], sort_keys=True)
            actual = continuations[key]
            require(tuple(sorted((int(r), n) for r, n in claim['first_local_delta'].items())) == actual['first_delta'], 'continuation first profile')
            require(claim['continuation_sha256'] == actual['digest'] and claim['continuation_moves'] == actual['moves'], 'continuation candidate domain')
            require(unpack_deltas(claim['reachable_final_local_deltas']) == actual['profiles'], 'reachable final profile inventory')
            sides.append(actual)
        left, right = sides
        require(left['first_delta'] == right['first_delta'] and left['digest'] != right['digest'], 'equal profile distinct continuation condition')
        only_left, only_right = left['profiles'] - right['profiles'], right['profiles'] - left['profiles']
        require(pair['reachable_profile_sets_equal'] is (left['profiles'] == right['profiles']), 'equal profile incorrectly promoted to continuation equivalence')
        require(unpack_deltas(pair['only_left_final_local_deltas']) == only_left and
                unpack_deltas(pair['only_right_final_local_deltas']) == only_right, 'reachable profile set difference')
        for side, difference in (('left', only_left), ('right', only_right)):
            witnesses_for_side = pair['only_' + side + '_witnesses']
            require(unpack_deltas([x['local_delta'] for x in witnesses_for_side]) == difference, 'set difference witness inventory')
            for witness in witnesses_for_side:
                after = checker.packed_apply(checker.initial, pair[side]['first'])
                final = checker.packed_apply(after, witness['second'])
                exact = profile_delta(base_profile, checker.profile(final))
                require(exact == tuple(sorted((int(r), n) for r, n in witness['local_delta'].items())), 'set difference full witness replay')
        if only_left or only_right:
            profile_set_differences.append(dict(left=pair['left']['first'], right=pair['right']['first'],
                                               only_left=[dict(x) for x in sorted(only_left)],
                                               only_right=[dict(x) for x in sorted(only_right)]))
    return dict(status='PASS_SEPARATE_INTEGER_COVERAGE_AND_RATIONAL_PRICING',
                first_moves=totals['first_moves'], second_moves=totals['second_moves'],
                second_operation_rows=len(c['second']), selected_first_states=len(groups),
                cross_section_second_moves=cross_count, unique_local_deltas=len(effects),
                full_replayed_witnesses=len(witnesses), exact_profile_tie_occurrences=effects[()],
                strictly_worse_occurrences=strict_worse,
                equal_profile_pairs_checked=len(c['equal_profile_different_continuations']),
                reachable_profile_set_differences=profile_set_differences,
                rejection_controls=coverage_controls(c, reconstructed),
                price_status_occurrences={k: statuses[k] for k in ('BETTER', 'WORSE_OR_EQUAL', 'UNRESOLVED')},
                limitation='Legacy nomination labels and synthetic legacy failures are rerun observations, not independently reimplemented here.')


def controls(pricing, manifest):
    rejected = []
    def rejects(name, function):
        try:
            function()
        except ValueError as exc:
            rejected.append(dict(name=name, reason=str(exc)))
        else:
            raise ValueError('semantic corruption accepted: ' + name)

    x = deepcopy(pricing)
    x['baseline_bracket']['certified_bracket'] = [str(LOW - Q(1, 10 ** 24)), str(LOW)]
    rejects('shifted_reference_bracket', lambda: audit_pricing(x))
    x = deepcopy(pricing)
    x['lambda_value'] = '0'
    rejects('omitted_surcharge_parameter', lambda: audit_pricing(x))
    x = deepcopy(pricing)
    # Omission in the numerical interval, while leaving the advertised lambda.
    row = x['comparisons']['abstract_mass_preserving_improvement']
    row['interval'] = [str(Q(v) + 2 * LAMBDA) for v in row['interval']]
    rejects('omitted_surcharge_in_signed_sum', lambda: audit_pricing(x))
    x = deepcopy(pricing)
    row = x['comparisons']['abstract_mass_preserving_worsening']
    # Multiplying a negative coefficient must exchange the two endpoints.
    pl, ph = power_interval(Q(3), LOW, HIGH)
    wrong = (Q(3) - Q(3) / pl + 2 * LAMBDA, Q(3) - Q(3) / ph + 2 * LAMBDA)
    row['interval'] = list(map(str, wrong))
    rejects('negative_coefficient_without_bound_reversal', lambda: audit_pricing(x))
    claim = dict(delta={'1': -14, '2': 15, '4': -4}, lower='0', upper='1/10', status='BETTER')
    rejects('unresolved_sign_promoted_to_better', lambda: audit_claim(claim))
    x = deepcopy(manifest)
    del x['inputs'][next(iter(x['inputs']))]
    rejects('source_inventory_omission', lambda: audit_inventory(x))
    x = deepcopy(manifest)
    x['inputs'][next(iter(x['inputs']))]['sha256'] = '0' * 64
    rejects('source_inventory_corruption', lambda: audit_inventory(x))
    return rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pricing', type=Path, default=HERE / 'evidence/PRICING.json')
    parser.add_argument('--coverage', type=Path)
    args = parser.parse_args()
    pricing = json.loads(args.pricing.read_text())
    manifest = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    count = audit_inventory(manifest)
    result = audit_pricing(pricing)
    result.update(source_files=count, rejection_controls=controls(pricing, manifest),
                  arithmetic=dict(scale_digits=90, log_terms=LOG_TERMS, exp_degree=EXP_DEGREE,
                                  float_or_transcendental_library_calls=0),
                  scope='fixed PR589 endpoints and listed signed comparisons; no neighborhood exhaustion')
    if args.coverage:
        result['coverage'] = audit_coverage(json.loads(args.coverage.read_text()))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
