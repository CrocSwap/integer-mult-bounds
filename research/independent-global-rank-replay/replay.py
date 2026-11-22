#!/usr/bin/env python3
"""Independent forward replay of two P104 native words, with invoice rebuild and mutation controls.

Standard library only (Python 3.11 to 3.14). Run without arguments:

    python3 -I -B research/independent-global-rank-replay/replay.py

It prints one JSON document and ends with PASS, or lists the failed checks and
exits 1. `--write` regenerates RESULT.json; the default run compares its output
with the committed RESULT.json, so script and output stay in step.

What it does, in order:

1. Verifies the sha256 of every input against SOURCES.json.
2. Forward-replays each native word over exact rationals, with every public
   input a free symbol, and checks frames, scalars, MOVE direction, the main
   rows, and that every helper row is the identity with no input shared
   between helper rows.
3. Rebuilds the paid and target profiles (T and P) from the replay and the
   caller data, finds the crossing with one solver, and proves the root is
   unique on [0, 0.01] by a derivative bound.
4. #7000: compares with its record and requires the root to be at least the
   tested value in FULL-RESULT.json.
5. #6030: known-answer test. Rebuilds T and P from the replay, requires them to
   equal the record exactly, solves, and requires the root to lie in the
   recorded interval. The solver never reads the recorded T, P or answer.
6. Mutation controls: real edits of the word (and of the rebuild) that each
   target check must reject, while the unmutated input passes it.

Everything the crossing uses (the invoice formula, the caller tables) comes
from the repository's own records, so matching the record for #7000 is a
reproduction. The replay, the profile rebuild, the #6030 known-answer test and
the controls are the independent parts. See README.md.
"""
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
P7 = 'research/shared-wire-split-composition/'
P6 = 'research/p104-helper470-twin-rung-removal/'
K_MAX = Decimal('0.01')          # search interval for the crossing: [0, K_MAX]
PRECISION = 70                   # decimal digits for the solver
BISECTIONS = 230                 # width 0.01 / 2**230 is below 1e-71
EVENT_LENGTH = {'ADD': 5, 'COPY': 5, 'SCALE': 4, 'MOVE': 5, 'INIT': 3, 'CLEAR': 3}
# Faults that are about scalars or direction, not about the frame chain.
NON_FRAME_FAULTS = {'public_move_not_up', 'zero_scalar'}


class CheckFailure(Exception):
    pass


# ---------------------------------------------------------------- inputs

def load(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def input_pins(root=ROOT):
    sources = json.loads((PKG / 'SOURCES.json').read_text())
    return {row['path']: row['sha256'] for row in sources['files'] if row['usage'] == 'input'}


def verify_pins(root=ROOT, pins=None):
    """Return the list of inputs whose bytes differ from their pin."""
    bad = []
    for path, want in (pins or input_pins(root)).items():
        got = hashlib.sha256((Path(root) / path).read_bytes()).hexdigest()
        if got != want:
            bad.append(path)
    return bad


# ------------------------------------------------------------- GF(2) frames

def reduce_basis(vectors):
    basis = {}
    for v in vectors:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                break
    return basis


class Frames:
    """Frame table: dimension and containment of GF(2) subspaces, cached."""

    def __init__(self, bases):
        self.bases = [list(b) for b in bases]
        self.dims = [len(reduce_basis(b)) for b in self.bases]
        self._contains = {}

    def contains(self, big, small):
        key = (big, small)
        if key not in self._contains:
            both = self.bases[big] + self.bases[small]
            self._contains[key] = len(reduce_basis(both)) == self.dims[big]
        return self._contains[key]

    def strictly_up(self, a, b):
        return self.contains(b, a) and self.dims[b] > self.dims[a]


def chain_check(frames, parts):
    """Check a split chain of two or more consecutive parts.

    parts is a list of (initial_frame, final_frame) for the fields in order.
    Requires: each part nested and strictly up, each part ends where the next
    begins, and the part ranks add up to the rank of the whole chain. Returns
    (ok, ranks).
    """
    ranks = []
    ok = len(parts) >= 2
    for k, (a, b) in enumerate(parts):
        ok &= frames.strictly_up(a, b)
        ranks.append(frames.dims[b] - frames.dims[a])
        if k + 1 < len(parts):
            ok &= b == parts[k + 1][0]
    ok &= sum(ranks) == frames.dims[parts[-1][1]] - frames.dims[parts[0][0]]
    return bool(ok), ranks


# ------------------------------------------------------------------ replay

def main_ids(word):
    live = set(word['live'])
    mains = live | {x + 112 for x in live}
    hosted = word.get('hosted')
    if hosted:
        mains |= set(hosted['X2']) | set(hosted['Y2'])
    return mains


def expected_main_rows(word):
    """The main block the word declares: a unit shear on ordinary ports, the
    declared mix on the hosted D ports, and the declared hosted X2/Y2 pairs.

    Convention (read off the words, and consistent with their declared alpha,
    beta, alpha2, beta2). A shear port x with partner y = x + 112 maps x -> x,
    y -> x + y. When the word declares hosted ports, the shear ports are the
    live ports listed in Dports; every other live port is a mix port and maps
    x -> x + alpha y, y -> beta x + (1 - beta) y. A hosted pair maps
    X2 -> X2 + alpha2 Y2, Y2 -> Y2 + beta2 X2. Without hosted ports every
    live port is a shear port.
    """
    live = word['live']
    hosted = word.get('hosted')
    shear_ports = set(live)
    if hosted:
        if hosted['mode'] != 'mix-t0':
            raise ValueError('unknown hosted mode ' + str(hosted['mode']))
        shear_ports = {live[p] for p in hosted['Dports']}
    rows = {}

    def put(j, row):
        if j in rows:
            raise ValueError('main row listed twice: ' + str(j))
        rows[j] = {k: v for k, v in row.items() if v}

    for x in live:
        y = x + 112
        if x in shear_ports:
            put(x, {x: F(1)})
            put(y, {x: F(1), y: F(1)})
        else:
            alpha, beta = F(hosted['alpha']), F(hosted['beta'])
            put(x, {x: F(1), y: alpha})
            put(y, {x: beta, y: 1 - beta})
    if hosted:
        alpha2, beta2 = F(hosted['alpha2']), F(hosted['beta2'])
        for xi, yi in zip(hosted['X2'], hosted['Y2']):
            put(xi, {xi: F(1), yi: alpha2})
            put(yi, {yi: F(1), xi: beta2})
    return rows


class Replay:
    pass


def addto(dst, src, q):
    for k, v in src.items():
        z = dst.get(k, 0) + q * v
        if z:
            dst[k] = z
        else:
            dst.pop(k, None)


def replay(word, frames):
    """Forward replay over exact rationals. Every public input is a symbol."""
    n = word['public']
    total = n + word['owned_fields']
    mains = main_ids(word)
    helpers = [r for r in range(n) if r not in mains]
    val = [{r: F(1)} if r < n else None for r in range(total)]
    cur = [word['initial'][r] if r < n else None for r in range(total)]
    paid, faults, info = Counter(), Counter(), Counter()
    dims = frames.dims

    def live(*rows):
        for r in rows:
            if val[r] is None:
                faults['dead_row_used'] += 1
                return False
        return True

    for e in word['program']:
        op = e[0]
        if op not in EVENT_LENGTH:
            faults['unknown_op'] += 1
            continue
        if len(e) != EVENT_LENGTH[op]:
            faults['malformed_event'] += 1
            continue
        r = e[1]
        if op == 'ADD':
            s, q, fr = e[2], F(e[3]), e[4]
            if q == 0:
                faults['zero_scalar'] += 1
            if cur[r] != fr or cur[s] != fr:
                faults['add_frame_mismatch'] += 1
            if live(r, s):
                addto(val[r], val[s], q)
        elif op == 'COPY':
            s, q, fr = e[2], F(e[3]), e[4]
            if q == 0:
                faults['zero_scalar'] += 1
            if cur[r] != fr or cur[s] != fr:
                faults['copy_frame_mismatch'] += 1
            if live(r, s):
                if val[r]:
                    faults['copy_onto_nonzero'] += 1
                val[r] = {k: q * v for k, v in val[s].items()}
        elif op == 'SCALE':
            q, fr = F(e[2]), e[3]
            if q == 0:
                faults['zero_scalar'] += 1
            if cur[r] != fr:
                faults['scale_frame_mismatch'] += 1
            if live(r):
                val[r] = {k: q * v for k, v in val[r].items()}
        elif op == 'MOVE':
            a, b, owned = e[2], e[3], e[4]
            if cur[r] != a:
                faults['move_from_wrong_frame'] += 1
            if owned != (r >= n):
                faults['move_owned_flag'] += 1
            if not (frames.contains(b, a) or frames.contains(a, b)):
                faults['move_not_nested'] += 1
            if r < n and not frames.strictly_up(a, b):
                faults['public_move_not_up'] += 1
            if r >= n and dims[b] < dims[a]:
                info['owned_moves_down'] += 1
            rank = abs(dims[b] - dims[a])
            if rank == 0:
                faults['move_rank_zero'] += 1   # never added to the paid profile
            else:
                paid[rank] += 1
            cur[r] = b
        elif op == 'INIT':
            if r < n:
                faults['init_public'] += 1
            elif val[r] is not None:
                faults['init_live'] += 1
            else:
                val[r] = {}
                cur[r] = e[2]
        elif op == 'CLEAR':
            if r < n:
                faults['clear_public'] += 1
            elif val[r] is None:
                faults['clear_dead'] += 1
            else:
                if cur[r] != e[2]:
                    faults['clear_frame_mismatch'] += 1
                if val[r]:
                    # Allowed: the owned-erasure rule permits clearing a nonzero
                    # owned field. Reported as information, not a fault.
                    info['owned_erasures_nonzero'] += 1
                val[r] = None
                cur[r] = None
    for r in range(n):
        if cur[r] != word['final'][r]:
            faults['final_frame_mismatch'] += 1
        if val[r] is None:
            faults['public_row_dead'] += 1
    rp = Replay()
    rp.word, rp.frames, rp.n, rp.mains, rp.helpers = word, frames, n, mains, helpers
    rp.val, rp.cur, rp.paid, rp.faults, rp.info = val, cur, paid, faults, info
    rp.owned_left_live = sum(1 for r in range(n, total) if val[r] is not None)
    # Per-field credit as the invoice uses it: rank of the final frame over the initial one.
    rp.credit = Counter()
    rp.credit_bad = 0
    for j in helpers:
        a, b = word['initial'][j], word['final'][j]
        rank = dims[b] - dims[a]
        if rank <= 0 or not frames.contains(b, a):
            rp.credit_bad += 1
        else:
            rp.credit[rank] += 1
    return rp


def double_credit_findings(rp):
    """The double-credit test: every helper row is the identity, no input is
    shared between helper rows, and no helper row reads a main input."""
    val, helpers, mains = rp.val, rp.helpers, rp.mains
    not_identity = [j for j in helpers if val[j] != {j: F(1)}]
    owners = defaultdict(list)
    for j in helpers:
        for i in val[j]:
            owners[i].append(j)
    shared = sorted((i, js) for i, js in owners.items() if len(js) > 1)
    reads_main = [j for j in helpers if any(i in mains for i in val[j])]
    return dict(non_identity_helper_rows=len(not_identity), shared_inputs=len(shared),
                helper_rows_reading_main=len(reads_main),
                first_non_identity=not_identity[:5], first_shared=[[i, js] for i, js in shared[:5]])


def main_row_findings(rp):
    expected = expected_main_rows(rp.word)
    wrong = []
    if set(expected) != rp.mains:
        wrong.append('main set differs from declared mains')
    wrong += [j for j, row in expected.items() if rp.val[j] != row]
    return dict(main_rows=len(expected), main_rows_wrong=len(wrong), first_wrong=wrong[:5])


def evaluate(rp, record_paid, record_credit):
    """Named checks for one replayed word. Each is a pass/fail fact."""
    f = rp.faults
    dc = double_credit_findings(rp)
    mr = main_row_findings(rp)
    checks = {
        'frame_chain': not any(k not in NON_FRAME_FAULTS for k in f),
        'nonzero_scalars': f['zero_scalar'] == 0,
        'public_moves_up': f['public_move_not_up'] == 0,
        'owned_rows_cleared': rp.owned_left_live == 0,
        'helper_credit_positive_nested': rp.credit_bad == 0,
        'main_rows': mr['main_rows_wrong'] == 0,
        'double_credit': (dc['non_identity_helper_rows'] == 0 and dc['shared_inputs'] == 0
                          and dc['helper_rows_reading_main'] == 0),
        'record_profiles': dict(rp.paid) == record_paid and dict(rp.credit) == record_credit,
    }
    return checks, dict(faults=dict(f), information=dict(rp.info), double_credit=dc, main=mr)


# ---------------------------------------------------------- crossing solver

class Moment:
    """m(k) = sum_r (T[r] - P[r]) r^(1-k), the signed concave moment."""

    def __init__(self, T, P):
        T = {r: c for r, c in T.items() if c}
        P = {r: c for r, c in P.items() if c}
        if not T and not P:
            raise ValueError('empty profile: no target and no paid rank')
        bad = sorted(r for r in set(T) | set(P) if not isinstance(r, int) or r < 1)
        if bad:
            raise ValueError('rank must be a positive integer; found ' + repr(bad))
        self.coef = {r: T.get(r, 0) - P.get(r, 0) for r in sorted(set(T) | set(P))}
        self.T, self.P = T, P
        with localcontext() as cx:
            cx.prec = PRECISION
            self.logs = {r: Decimal(r).ln() for r in self.coef}

    def value(self, k):
        with localcontext() as cx:
            cx.prec = PRECISION
            k = Decimal(k)
            return sum(Decimal(c) * Decimal(r) * (-k * self.logs[r]).exp()
                       for r, c in self.coef.items() if c)

    def derivative_upper(self, k_max):
        """An upper bound for m'(k) on [0, k_max].

        m'(k) = - sum c_r r ln(r) r^(-k). A positive c_r term is largest in
        absolute value at k = 0 only for negative c, and smallest in size at
        k = k_max for positive c, so bound each term on its worst side.
        """
        with localcontext() as cx:
            cx.prec = PRECISION
            k_max = Decimal(k_max)
            total = Decimal(0)
            for r, c in self.coef.items():
                if c == 0 or r == 1:
                    continue
                w = Decimal(c) * Decimal(r) * self.logs[r]
                total -= w * (-k_max * self.logs[r]).exp() if c > 0 else w
            return total

    def sign_changes(self):
        seq = [c for c in self.coef.values() if c]
        return sum(1 for a, b in zip(seq, seq[1:]) if (a > 0) != (b > 0))


def solve(T, P, k_max=K_MAX):
    """The unique crossing of m on [0, k_max], with its proof obligations.

    Raises ValueError if m(0) <= 0, m(k_max) >= 0, or the derivative bound does
    not show m is strictly decreasing on the whole interval (interior check).
    """
    m = Moment(T, P)
    u = m.derivative_upper(k_max)
    with localcontext() as cx:
        cx.prec = PRECISION
        lo, hi = Decimal(0), Decimal(k_max)
        m0, mk = m.value(lo), m.value(hi)
        if not (m0 > 0 and mk < 0):
            raise ValueError('no sign change on [0, %s]' % k_max)
        if not u < 0:
            raise ValueError('derivative bound %s does not show a monotone moment' % u)
        for _ in range(BISECTIONS):
            mid = (lo + hi) / 2
            if m.value(mid) > 0:
                lo = mid
            else:
                hi = mid
        root = (lo + hi) / 2
    return dict(root=root, moment=m, derivative_upper=u, m_at_0=m0, m_at_kmax=mk)


def digits(d, places=60):
    return format(d, '.%df' % places)


# ------------------------------------------------------------- profiles

def rank_mass(hist):
    return sum(r * c for r, c in hist.items())


def surplus(T, P):
    return sum(r * (T.get(r, 0) - P.get(r, 0)) for r in set(T) | set(P))


def build_7000(rp, caller):
    """T and P for #7000: per-call native credit and paid ranks from the replay,
    plus the caller's QUERY, IDLE_ONE and diagonal terms (crossing formula of
    the repository's invoice)."""
    T, P, calls = Counter(), Counter(), 0
    for e in caller['events']:
        if e[0] == 'J':
            calls += 1
            T.update(rp.credit)
            P.update(rp.paid)
        else:
            ports = len(caller['types'][e[0]]['ports'])
            if e[1] == 'QUERY':
                P[1] += ports
            elif e[1] == 'IDLE_ONE':
                P[8 * len(set(e[3]))] += ports
    for d in caller['types'].values():
        for dg in d['diagonal']:
            if not all(v in (0, 1) for v in dg[2:]):
                raise ValueError('repeated stage power in caller diagonal')
            T[dg[0] % 2 + 8 * sum(dg[2:])] += len(d['ports'])
    return T, P, calls


def clean(hist):
    return {int(r): int(c) for r, c in hist.items() if c}


def declared_splits(root, word, frames, helpers):
    """Splits named by the package's two proof files (pivot helper and cut frame).

    The head is the pivot. Its unsplit exit frame is the modal final frame of the
    helpers with the same initial frame. Tail candidates are helpers that start
    at the cut frame and end at the exit frame; every candidate is chain-checked.
    The tail's rank is derived from the frames, not written down.
    """
    out = []
    for name in ('data/split759.proof.json', 'data/split759_450.proof.json'):
        proof = load(Path(root) / P7 / name)
        pivot, cut = proof['pivot'], proof['frame']
        init, fin = word['initial'][pivot], word['final'][pivot]
        exit_frame = Counter(word['final'][j] for j in helpers
                             if word['initial'][j] == init).most_common(1)[0][0]
        tails = [t for t in helpers if word['initial'][t] == cut and word['final'][t] == exit_frame]
        chains = [chain_check(frames, [(init, fin), (cut, exit_frame)]) for _ in tails]
        head_rank = frames.dims[fin] - frames.dims[init]
        whole = frames.dims[exit_frame] - frames.dims[init]
        out.append(dict(source=name, pivot=pivot, cut_frame=cut, head_rank=head_rank,
                        tail_rank=whole - head_rank, unsplit_rank=whole, tail_candidates=tails,
                        chain_ok=bool(tails) and fin == cut and all(ok for ok, _ in chains)))
    return out


def sensitivities_7000(T, P, calls, splits):
    """Information only: how far the crossing moves under named changes."""
    out = {}
    base = solve(T, P)['root']
    by_rank = {}
    for r in sorted(r for r in T if r < 10):
        T2 = Counter(T)
        T2[r] -= calls            # one credited field of this rank loses its credit in every call
        by_rank[str(r)] = digits(solve(T2, P)['root'], 30)
    out['one_field_of_rank_loses_credit_each_call'] = by_rank
    T1 = Counter(T)
    for s in splits:
        T1[s['head_rank']] -= calls
        T1[s['tail_rank']] -= calls
        T1[s['unsplit_rank']] += calls
    out['splits_valued_as_unsplit'] = dict(
        rank_mass_change=surplus(T1, P) - surplus(T, P), crossing=digits(solve(T1, P)['root'], 30),
        crossing_minus_base=digits(solve(T1, P)['root'] - base, 12))
    return out


# --------------------------------------------------------------- the runs

def run_7000(root, frames, word, rp, record):
    caller = load(Path(root) / P7 / 'data/caller.json')
    T, P, calls = build_7000(rp, caller)
    inv = record['invoice']
    rec_T, rec_P = clean(inv['T']), clean(inv['P'])
    sol = solve(T, P)
    root_v = sol['root']
    tested = F(record['gate']['tested'])
    claim = F(record['gate']['claim'])
    lo, hi = (F(x) for x in record['gate']['raw_bracket'])
    rec_cross = Decimal(inv['raw_crossing'])
    checks = {
        'T_equals_record': clean(T) == rec_T,
        'P_equals_record': clean(P) == rec_P,
        'surplus_equals_record': surplus(T, P) == int(inv['S']),
        'root_unique_on_interval': sol['derivative_upper'] < 0,
        'moment_positive_at_tested': sol['moment'].value(Decimal(tested.numerator) / Decimal(tested.denominator)) > 0,
        'root_at_least_tested': F(root_v) >= tested,
        'claim_at_most_tested': claim <= tested,
        'root_in_recorded_bracket': lo < F(root_v) < hi,
        'root_matches_record_digits': abs(root_v - rec_cross) < Decimal('1e-55'),
    }
    splits = declared_splits(root, word, frames, rp.helpers)
    checks['declared_splits_chain_ok'] = all(s['chain_ok'] for s in splits)
    res = dict(
        calls=calls, credit_hist_per_call=dict(sorted(rp.credit.items())), credit_mass_per_call=rank_mass(rp.credit),
        paid_hist_per_call=dict(sorted(rp.paid.items())), paid_mass_per_call=rank_mass(rp.paid),
        rank_surplus=surplus(T, P), crossing=digits(root_v), recorded_crossing=inv['raw_crossing'],
        tested=str(tested), claim=str(claim), derivative_upper_bound_on_interval=digits(sol['derivative_upper'], 3),
        sign_changes_by_rank=sol['moment'].sign_changes(),
        declared_splits=splits, sensitivities=sensitivities_7000(T, P, calls, splits))
    return checks, res, (T, P, calls, sol)


def known_6030(root, frames6, word6, rp6, include_query=True):
    """Known-answer test. Solves from the rebuilt T and P; reads the record only
    afterwards, to compare."""
    result = load(Path(root) / P6 / 'RESULT.json')
    expect = load(Path(root) / P6 / 'EXPECT.json')
    pc, cc = result['physical_caller'], result['complete_cost']
    calls = pc['full_calls']
    ports = len(word6['live'])
    T, P = Counter(), Counter()
    for r, c in rp6.credit.items():
        T[r] += calls * c
    for r, c in rp6.paid.items():
        P[r] += calls * c
    for r, c in pc['main_targets'].items():
        T[int(r)] += c
    for r, c in pc['whole_idle_jobs'].items():
        P[int(r)] += c
    if include_query:
        P[1] += cc['query_shears'] * ports
    sol = solve(T, P)                 # the solver has seen only the rebuilt profiles
    root_v = sol['root']
    lo, hi = (F(x) for x in expect['interval'])
    checks = {
        'ports_equal_record': ports == pc['ports'],
        'T_equals_record': clean(T) == clean(cc['targets']),
        'P_equals_record': clean(P) == clean(cc['paid']),
        'productive_equals_expect': sum(T.values()) == expect['productive_fields'],
        'paid_calls_equal_expect': sum(P.values()) == expect['paid_calls'],
        'surplus_equals_expect': surplus(T, P) == expect['rank_mass_surplus'],
        'root_unique_on_interval': sol['derivative_upper'] < 0,
        'root_in_recorded_interval': lo < F(root_v) < hi,
    }
    res = dict(calls=calls, ports=ports, query_term=cc['query_shears'] * ports if include_query else 0,
               credit_mass_per_call=rank_mass(rp6.credit), paid_mass_per_call=rank_mass(rp6.paid),
               productive=sum(T.values()), paid=sum(P.values()), rank_surplus=surplus(T, P),
               crossing=digits(root_v), interval=[str(lo), str(hi)],
               derivative_upper_bound_on_interval=digits(sol['derivative_upper'], 3),
               sign_changes_by_rank=sol['moment'].sign_changes())
    return checks, res


# ---------------------------------------------------------------- controls

def with_program(word, program):
    mutated = dict(word)
    mutated['program'] = program
    return mutated


def first_index(program, pred):
    for i, e in enumerate(program):
        if pred(e):
            return i
    raise ValueError('no event to mutate')


def mutations(word, mains):
    """Real edits of the word. Each returns (mutated word, description)."""
    n = word['public']
    prog = word['program']
    out = {}
    # The reviewer's leak: helper 1478 reads helper 759 while both sit in frame 660.
    p = list(prog)
    p.insert(40637, ['ADD', 1478, 759, '1', 660])
    out['shared_input_between_split_tails'] = (
        with_program(word, p), 'insert ADD 1478 += 759 at event 40637 (frame 660)', 'double_credit', set())
    # A different kind: flip the sign of one main-row ADD.
    i = first_index(prog, lambda e: e[0] == 'ADD' and e[1] in mains and e[2] in mains)
    p = list(prog)
    e = list(p[i])
    e[3] = str(-F(e[3]))
    p[i] = e
    out['main_row_sign_flip'] = (
        with_program(word, p), 'flip the scalar of the ADD at event %d (main row %d)' % (i, e[1]), 'main_rows', set())
    # A scalar fault with no effect on any value: an ADD by zero.
    i = first_index(prog, lambda e: e[0] == 'ADD')
    p = list(prog)
    p.insert(i + 1, p[i][:3] + ['0'] + p[i][4:])
    out['zero_scalar_add'] = (
        with_program(word, p), 'insert a copy of the ADD at event %d with scalar 0' % i, 'nonzero_scalars', set())
    # A public MOVE that goes down and back up: legal frames, wrong direction, extra paid rank.
    i = first_index(prog, lambda e: e[0] == 'MOVE' and e[1] < n)
    r, a, b = prog[i][1], prog[i][2], prog[i][3]
    p = list(prog)
    p[i + 1:i + 1] = [['MOVE', r, b, a, False], ['MOVE', r, a, b, False]]
    out['public_move_down_and_up'] = (
        with_program(word, p), 'after the public MOVE at event %d insert MOVE %d %d->%d and back' % (i, r, b, a),
        'public_moves_up', {'record_profiles'})
    # A public MOVE removed: the frame chain breaks.
    p = list(prog)
    del p[i]
    out['public_move_removed'] = (
        with_program(word, p), 'delete the public MOVE at event %d' % i, 'frame_chain', {'record_profiles'})
    return out


def run_controls(root, frames, word, mains, native_record):
    rec_paid, rec_credit = native_record
    results = {}
    for name, (mutated, text, target, allowed) in mutations(word, mains).items():
        rp = replay(mutated, frames)
        checks, _ = evaluate(rp, rec_paid, rec_credit)
        failed = {k for k, v in checks.items() if not v}
        results[name] = dict(edit=text, target_check=target, failed_checks=sorted(failed),
                             rejected=target in failed and failed <= {target} | allowed)
    return results


def run_profile_controls(T, P, calls, sol7, tested, root, frames6, word6, rp6):
    """Controls on the rebuild and the crossing check."""
    out = {}
    # 1. Rebuild #6030 without the query term (the reviewer's 15 x 104 on P[1]).
    checks, res = known_6030(root, frames6, word6, rp6, include_query=False)
    failed = sorted(k for k, v in checks.items() if not v)
    out['6030_without_query_term'] = dict(
        edit='leave the query shears (15 x 104 on P[1]) out of the rebuild', target_check='P_equals_record',
        failed_checks=failed, crossing=res['crossing'],
        rejected='P_equals_record' in failed and 'paid_calls_equal_expect' in failed)
    # 2. Remove one rank-8 credit per call (one tail loses its credit): root must drop below tested.
    T2 = Counter(T)
    T2[8] -= calls
    root2 = solve(T2, P)['root']
    out['7000_one_rank8_credit_lost_per_call'] = dict(
        edit='remove one rank-8 credit in each of the %d calls from T' % calls,
        target_check='root_at_least_tested', crossing=digits(root2, 30),
        failed_checks=['root_at_least_tested'] if F(root2) < tested else [],
        rejected=F(root2) < tested and F(sol7['root']) >= tested)
    return out


def run_all(root=ROOT):
    bad = verify_pins(root)
    if bad:
        raise CheckFailure('input bytes differ from their pins: ' + ', '.join(bad))
    word7 = load(Path(root) / P7 / 'data/final.json.gz')
    record7 = load(Path(root) / P7 / 'FULL-RESULT.json')
    frames7 = Frames(word7['frames'])
    rp7 = replay(word7, frames7)
    rec_paid7, rec_credit7 = clean(record7['native']['paid']), clean(record7['native']['helpers'])
    checks7, info7 = evaluate(rp7, rec_paid7, rec_credit7)
    inv_checks, inv_res, (T, P, calls, sol7) = run_7000(root, frames7, word7, rp7, record7)

    word6 = load(Path(root) / P6 / 'WORD.json.gz')
    record6 = load(Path(root) / P6 / 'RESULT.json')
    frames6 = Frames(word6['frames'])
    rp6 = replay(word6, frames6)
    rec_paid6, rec_credit6 = clean(record6['local']['paid']), clean(record6['local']['helpers'])
    checks6, info6 = evaluate(rp6, rec_paid6, rec_credit6)
    kn_checks, kn_res = known_6030(root, frames6, word6, rp6)

    controls = run_controls(root, frames7, word7, rp7.mains, (rec_paid7, rec_credit7))
    controls.update(run_profile_controls(T, P, calls, sol7, F(record7['gate']['tested']),
                                         root, frames6, word6, rp6))
    result = {
        'status': None,
        'base_commit': json.loads((PKG / 'SOURCES.json').read_text())['base_commit'],
        'input_sha256': input_pins(root),
        'word_7000': dict(events=len(word7['program']), public=word7['public'], mains=len(rp7.mains),
                          helpers=len(rp7.helpers), checks=checks7, **info7),
        'invoice_7000': dict(checks=inv_checks, **inv_res),
        'word_6030': dict(events=len(word6['program']), public=word6['public'], mains=len(rp6.mains),
                          helpers=len(rp6.helpers), checks=checks6, **info6),
        'known_answer_6030': dict(checks=kn_checks, **kn_res),
        'controls': controls,
    }
    failures = []
    for section in ('word_7000', 'invoice_7000', 'word_6030', 'known_answer_6030'):
        failures += [section + ':' + k for k, v in result[section]['checks'].items() if not v]
    failures += ['control:' + k for k, v in controls.items() if not v['rejected']]
    result['status'] = 'PASS' if not failures else 'FAIL'
    result['failures'] = failures
    return json.loads(json.dumps(result, default=str, sort_keys=True))


def main(argv):
    try:
        result = run_all()
    except (CheckFailure, ValueError) as error:
        print('FAIL', error)
        return 1
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    result_path = PKG / 'RESULT.json'
    if '--write' in argv:
        result_path.write_text(text)
    print(text, end='')
    if result['failures']:
        print('FAIL', ', '.join(result['failures']))
        return 1
    if '--write' not in argv and (not result_path.exists() or result_path.read_text() != text):
        print('FAIL RESULT.json differs from this run; rerun with --write and review the change')
        return 1
    print('PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
