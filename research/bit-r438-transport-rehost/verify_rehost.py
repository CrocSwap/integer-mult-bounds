#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Window-respecting optimal re-hosting of the R438 bit hosting slack (bit headroom only; no new kappa).

PR1043 (aliromman) removes helper470 from the PR589 R439 bit word.  Its hosting_change folds the nine freed width-8
slots back into their own hosts in every replica and runs no hosting search.  With 438 helpers the PR1023 slot model
has 3996 - 9*438 = 54 width-8 units of slack per replica instead of 45.  This script:

 1. DP.  Proves the unique moment-minimising no-bank slot layout for S = 54 at the certified grid point.  It uses an
    exact top-3 interval DP over (capacity, unused units) built on PR1023's g_interval.  An independent branch-and-bound
    enumeration over all 10,556,685 layouts (sorted lists, provably skipped tails) cross-checks it, and the runner-up gap is reported as a certified interval.
    S = 45 (R439) is a positive control: it reproduces the PR589 selection and PR1023's own width8_optimality.
 2. Windows.  Checks every stage-window-feasible split of the optimum's slack over children 4 and 6 with seed72's
    maxflow_assign and an independent all-subsets Hall test.
 3. Placement.  Builds an explicit placement of all 9*438 helper occurrences per replica with seed14's allocate
    (R = 438).  It must equal PR442's deterministic expander, and it is audited by seed14's placement_audit and by an
    independent audit.  All 32 replica owner maps are also checked.
 4. Endpoints.  Certifies bit endpoints with PR1023's packing.endpoint, using both pinned engines and the inherited
    surcharge.  The idle profile is combined with (a) PR1043's R438 local profile and (b) the transported-word profile
    (declared input).  PR589's c and PR1043's own c, with its own hosting, are reproduced as positive controls.
Negative controls (mutations that must be rejected) are run for every part.

Usage: python3 -I -B verify_rehost.py [--repo ROOT] [--out RECEIPT.json] [--check RECEIPT.json]
The last line printed is PASS_R438_WINDOW_REHOST ... or FAIL_R438_WINDOW_REHOST ...
Standard-library CPython only.  Inputs come from the repository working tree (sha256 and git-blob pinned) and from
vendor/pr1043 (byte copy, sha256 and git-blob pinned).
"""
import argparse
import hashlib
import json
import os
import sys
import time
import types
from collections import Counter
from fractions import Fraction as Q

TAG = 'R438_WINDOW_REHOST'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Main-tree inputs, read from --repo and pinned by sha256 and git blob id.  The blob ids are those at canonical main
# 0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2 (the research base of this script).
PINS = {
    'research/bit589-width-packing/packing.py':
        ('2bb5515807714807961289e4ee6958c3ad7e0c27bbec4d9212b138c662a6cc7b', 'a6079ee0dd4d8037be477a3c4497f472348bde07'),
    'research/bit589-width-packing/SOURCES.json':
        ('53fe98c8f01de7e32e3110e591d62e60292abb38cc11ecde4839f2eebd3b5fbc', 'f6a97de32691a1d426ac4819aad24c0c8414d97e'),
    'research/e8-bit-p111-tuned/tune/EXPECTED.json':
        ('b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4', 'e293ddc557742637f9f679f083a1a282d87b1b13'),
    'research/e8-bit-p111-tuned/data/selection9-p111.json':
        ('4ab1ed4529683cd184987f8bc3031fb7408b9cd22c25ab9cf541a8aaf896eaf1', 'e69ea66a3add357f570fc5552ab6368b3c8f9bb2'),
    'research/native-complex-moment552/engines/moment.py':
        ('81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482', '7d697cb45203fe72d97037403d6da41f71f3b7fd'),
    'research/native-complex-moment552/engines/base_two_moment.py':
        ('aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098', '14a90fa0e788217856f070382c9e61bd7c603c61'),
    'research/native-complex-moment552/engines/outer.py':
        ('c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c', '43007488ad2c43187c77cc6798beff8b1cd76ad2'),
    'research/bit589-width7-windows-seed72/verify.py':
        ('a5341ed222af84b51cd18645dd6b23e4613c0275cbf2663c94b07a9f916e9e60', '7f79a47146b150c9446e5f45e401d70b5cd12427'),
    'research/bit589-width7-windows-seed72/wopt.py':
        ('a72daf1c7cff422543371a220fd391fe3b33552ac6ed52763f50b0c2f93d9532', '4e0bd3704d1a2be460ed25b363e95918119e8d42'),
    'research/bit589-width7-windows-seed72/windows.py':
        ('a24295a51333b168ab73215f8a4bbb5bf831be829f572d1cde15fc322049c635', '4bb4f075ad5c1a49b4af310094bde6b2a4ea0c2e'),
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/idle-axis-hosting/hosting_core.py':
        ('d8b90cd5d152df3c7c351230863d9e61816ad5e1f21d69bea1a86a5daad559a3', '68b536daa9e6546c0aa046934bf840aaa3c3fde3'),
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py':
        ('57e558c80a2fea6e291587b04afd76dfaee3550729997798b61f33daf90b8ec9', '8864ca9b942a3507171edca0cf6cbaaf10fcf434'),
    'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py':
        ('6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8', '3df12bd632f1fdba825ced57110a1fee82eb2857'),
    'research/bit-helper470-window-placement-seed14/verify.py':
        ('9cceeb610eccd6171585b056020ab6c44d7428de403a9ed035be1df9ae63f55b', 'c716a44e3b920f91918903d3480560e3882fbe80'),
}
# Vendored byte copies (see vendor/pr1043/NOTICE.md).
VENDOR = {
    'vendor/pr1043/CERTIFICATE.json': dict(
        sha256='32c6cd6103006d627909cabdaf5083238c661a6582016a8b21075bd01c892eff',
        git_blob='56400920050c523e6e399f2455137b36c35cf528',
        origin='PR1043 (Ali Romman, @aliromman) head e309e17f83f5759b1ea1fa24a76f24838784cb4d, '
               'research/bit-boundary-persistence/CERTIFICATE.json'),
}

T, STAGES, M, V = 32, 9, 64, 111
COPIES = 2 * V
GRID = Q(1, 10 ** 24)
C0_DECIMAL = '0.001733427039589844234749'              # PR589 R439 selected bit endpoint
PR1043_DECIMAL = '0.001734176288479865766692'          # PR1043's claimed R438 endpoint (own in-place hosting)
SCOUT_A = '0.001734802047828389852783'                 # predicted endpoint (a); checked, not assumed
SCOUT_B = '0.001734846264120199151475'                 # predicted endpoint (b); checked, not assumed
# (b) is a declared input here: the paid local profile of the R438 word after one A-transport (op 2027 -> slot 154 at
# frame 79, a PR1345 transport-atlas move on PR1043's word).  verify_transport.py in this package rebuilds and replays
# that word and recounts this profile; this script only checks its rank mass and child count.
LOCAL_B = {1: 1322, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 18}
# Number of layouts = coefficient of x^S in 1/(1-x) * 1/((1-x)(1-x^2)(1-x^3)) * 1/((1-x)...(1-x^5)) (classes 14/28/42).
EXPECTED_LAYOUTS = {45: 3160688, 54: 10556685}


class Fail(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Fail(message)


def git_blob(raw):
    return hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()


def check_pin(raw, sha, blob, label):
    require(hashlib.sha256(raw).hexdigest() == sha, 'sha256 pin: ' + label)
    require(git_blob(raw) == blob, 'git blob pin: ' + label)


def read_pinned(base, rel, sha, blob):
    path = os.path.join(base, *rel.split('/'))
    with open(path, 'rb') as handle:
        raw = handle.read()
    check_pin(raw, sha, blob, rel)
    return path, raw


def load_module(name, path, raw):
    """Execute the already pinned bytes as a module (no second read of the file)."""
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    exec(compile(raw, path, 'exec'), module.__dict__)
    return module


def grid_decimal(c):
    n = c * 10 ** 24
    require(n.denominator == 1 and n.numerator > 0, 'value on the 1e-24 grid')
    s = str(n.numerator).rjust(25, '0')
    return s[:-24] + '.' + s[-24:]


def fixed(k, n):
    sign = '-' if k < 0 else ''
    s = str(abs(k)).rjust(n + 1, '0')
    return sign + s[:-n] + '.' + s[-n:]


def dfloor(x, n=36):
    return fixed((x.numerator * 10 ** n) // x.denominator, n)


def dceil(x, n=36):
    return fixed(-((-x.numerator * 10 ** n) // x.denominator), n)


def keyed(hist):
    return {str(r): n for r, n in sorted(hist.items()) if n}


def unkeyed(hist):
    return {int(r): n for r, n in hist.items()}


def expect_reject(controls, name, fn, needle, exc=(Exception,)):
    """A negative control: fn must raise, with `needle` in the message."""
    try:
        fn()
    except exc as e:  # noqa: PERF203
        message = '%s: %s' % (type(e).__name__, e)
        require(needle in str(e), 'control %s rejected for the wrong reason: %s' % (name, message))
        controls.append(dict(name=name, rejected=True, reason=message))
        return
    raise Fail('negative control %s was accepted' % name)


# ---------------------------------------------------------------------------------------------------------------------
# 1. Slot layouts: exact interval DP and independent exhaustive enumeration.

def layout_terms(P, slots, c):
    """Moves (capacity, u): one slot of that capacity keeps u unused width-8 places.  Every capacity has a positive
    remainder mod 8, so each slot has exactly one idle child whatever it hosts and the per-child surcharge is the same
    for all layouts.  The idle cost of a layout is then sum_slots g(remainder), g(r) = r (64/r)^c.  Returns the moves,
    certified lower and upper bounds of each move's cost change, and the g intervals."""
    rmin = {cap: cap % 8 for cap in slots}
    require(all(rmin[cap] > 0 for cap in slots), 'some capacity is divisible by 8')
    G = {}
    caps = sorted(cap for cap in slots if cap // 8)
    for cap in sorted(slots):
        for u in range(cap // 8 + 1):
            r = rmin[cap] + 8 * u
            if r not in G:
                G[r] = P.g_interval(r, c)
                require(G[r][0] <= G[r][1], 'g interval order')
    moves = [(cap, u) for cap in caps for u in range(1, cap // 8 + 1)]
    lo = {mv: G[rmin[mv[0]] + 8 * mv[1]][0] - G[rmin[mv[0]]][1] for mv in moves}
    hi = {mv: G[rmin[mv[0]] + 8 * mv[1]][1] - G[rmin[mv[0]]][0] for mv in moves}
    return moves, lo, hi, G, rmin


def topk_dp(moves, lo, S, K):
    """Top-K coin-change DP over move types in a fixed order.  Each count vector arises on exactly one path, and the
    top-K of a union of shifted top-K lists is exact, so this returns the K smallest layout lower bounds exactly."""
    best = [[(Q(0), ())]] + [[] for _ in range(S)]
    for mv in moves:
        u = mv[1]
        new = [list(b) for b in best]
        for s in range(u, S + 1):
            for k in range(1, s // u + 1):
                for v, lay in best[s - k * u]:
                    new[s].append((v + k * lo[mv], lay + ((mv, k),)))
        best = [sorted(b)[:K] for b in new]
    return [(v, tuple(sorted(lay))) for v, lay in best[S]]


def exhaustive_topk(moves, lo, S, K, dyad):
    """Independent check: enumerate every layout as one multiset of unused counts per capacity class, with exact
    integer costs (all bounds are multiples of 1/dyad).  Branch-and-bound on per-class lists sorted by cost.
    Returns the K smallest and the number of layouts covered."""
    ilo = {}
    for mv in moves:
        x = lo[mv] * dyad
        require(x.denominator == 1, 'dyadic bound')
        ilo[mv] = x.numerator
    caps = sorted({cap for cap, _ in moves})
    tables = {}
    for cap in caps:
        umax = max(u for c, u in moves if c == cap)
        table = {U: [] for U in range(S + 1)}

        def parts(rem, largest, acc, cost, cap=cap, table=table):
            if rem == 0:
                return
            for u in range(min(largest, rem), 0, -1):
                for k in range(1, rem // u + 1):
                    acc2 = acc + (((cap, u), k),)
                    cost2 = cost + k * ilo[(cap, u)]
                    used = sum(uu * kk for (_, uu), kk in acc2)
                    table[used].append((cost2, tuple(sorted(acc2))))
                    parts(rem - k * u, u - 1, acc2, cost2)
        table[0].append((0, ()))
        parts(S, umax, (), 0)
        for U in table:
            table[U].sort()
        tables[cap] = table
    top = []                              # sorted list of (cost, layout), at most K
    covered = 0

    def walk(i, rem, base, lay):
        nonlocal covered
        if i == len(caps) - 1:
            lst = tables[caps[i]][rem]
            covered += len(lst)
            for cost, sub in lst:
                v = base + cost
                if len(top) == K and v > top[-1][0]:
                    break
                top.append((v, tuple(sorted(lay + sub))))
                top.sort()
                del top[K:]
            return
        for U in range(rem + 1):
            for cost, sub in tables[caps[i]][U]:
                walk(i + 1, rem - U, base + cost, lay + sub)
    walk(0, S, 0, ())
    return [(Q(v, dyad), lay) for v, lay in top], covered


def idle_of(slots, rmin, layout):
    h = Counter()
    for cap, n in slots.items():
        h[rmin[cap]] += n
    for (cap, u), k in layout:
        h[rmin[cap]] -= k
        h[rmin[cap] + 8 * u] += k
        require(h[rmin[cap]] >= 0, 'more modified slots than slots')
    return Counter({r: n for r, n in h.items() if n})


def gap_interval(G, worse, better):
    """Certified interval of sum g(worse) - sum g(better) for two idle histograms."""
    d = Counter(worse)
    d.subtract(better)
    lo = hi = Q(0)
    for r, n in d.items():
        if n > 0:
            lo += n * G[r][0]
            hi += n * G[r][1]
        elif n < 0:
            lo += n * G[r][1]
            hi += n * G[r][0]
    return lo, hi


def layout_name(layout):
    return ' + '.join('%dx(%d,%d)' % (k, cap, u) for (cap, u), k in sorted(layout, key=lambda t: (-t[1], t[0])))


def certify_optimum(P, slots, S, c_star, W, check_exhaustive, dp_drop=()):
    moves, lo, hi, G, rmin = layout_terms(P, slots, c_star)
    require(S <= min(n for cap, n in slots.items() if cap // 8), 'slot-count limits are not vacuous')
    top = topk_dp([mv for mv in moves if mv not in dp_drop], lo, S, 3)   # dp_drop: negative control only
    require(len(top) == 3, 'fewer than three layouts')
    covered = None
    if check_exhaustive:
        top2, covered = exhaustive_topk(moves, lo, S, 3, P.MOMENT.DYAD)
        require([v for v, _ in top2] == [v for v, _ in top], 'exhaustive enumeration disagrees with the DP (values)')
        require([lay for _, lay in top2[:2]] == [lay for _, lay in top[:2]],
                'exhaustive enumeration disagrees with the DP (layouts)')
    (l_opt, opt), (l_run, run), (l_third, third) = top

    def upper(lay):
        return sum((k * hi[mv] for mv, k in lay), Q(0))
    require(l_run > upper(opt), 'optimum is not certified unique')
    require(l_third > upper(run), 'runner-up is not certified')
    idle_opt, idle_run = idle_of(slots, rmin, opt), idle_of(slots, rmin, run)
    g_lo, g_hi = gap_interval(G, idle_run, idle_opt)
    require(g_lo > 0, 'runner-up gap not positive')
    return dict(c_star=c_star, opt=opt, run=run, third=third, opt_lo=l_opt, run_lo=l_run, idle_opt=idle_opt,
                idle_run=idle_run, G=G, rmin=rmin, lo=lo, hi=hi, gap=(g_lo, g_hi), covered=covered,
                receipt=dict(c_star=grid_decimal(c_star), slack_units=S, optimum=layout_name(opt),
                             optimum_idle_per_replica=keyed(idle_opt), runner_up=layout_name(run),
                             runner_up_idle_per_replica=keyed(idle_run), third=layout_name(third),
                             runner_up_gap_sum_g_per_replica=[dfloor(g_lo), dceil(g_hi)],
                             runner_up_gap_moment=[dfloor(T * g_lo / (M * W), 40), dceil(T * g_hi / (M * W), 40)],
                             exhaustive_layouts_covered=covered))


def claim_is_optimal(cert, claimed):
    """True iff `claimed` is certified strictly cheaper than every other layout (uses the certified top-3)."""
    upper = sum((k * cert['hi'][mv] for mv, k in claimed), Q(0))
    others = [v for v, lay in ((cert['opt_lo'], cert['opt']), (cert['run_lo'], cert['run'])) if lay != claimed]
    return all(v > upper for v in others)


# ---------------------------------------------------------------------------------------------------------------------
# 2. Stage windows.

def hall_check(supply, demand, allowed):
    """All-subsets Hall test for the stage -> child transport (independent of max-flow)."""
    kids = [i for i in sorted(demand) if demand[i]]
    if sum(supply.values()) != sum(demand.values()):
        return False, 'totals differ'
    for mask in range(1, 1 << len(kids)):
        C = [kids[j] for j in range(len(kids)) if mask >> j & 1]
        nbr = set()
        for i in C:
            nbr |= set(allowed[i])
        if sum(demand[i] for i in C) > sum(supply.get(s, 0) for s in nbr):
            return False, 'children %s' % C
    return True, None


def demand_for(config):
    """config = (idle copies of child 4, child holding the one-residual copy); the other 10 - x4 idle copies are in
    child 6.  Children 0, 2, 7, 8 stay full; children 1, 3, 5 (capacity 7) host nothing."""
    x4, partial = config
    d = {0: COPIES * 1, 1: 0, 2: COPIES * 3, 3: 0, 5: 0, 7: COPIES * 3, 8: COPIES * 1}
    for child, idle in ((4, x4), (6, 10 - x4)):
        part = 1 if partial == child else 0
        d[child] = 5 * (COPIES - idle - part) + part
    return d


# ---------------------------------------------------------------------------------------------------------------------
# 3. Independent placement audit (mirrors the slot rules of audit_hosted_k, written without its code).

def audit_slots(slots, hosting, active, R):
    cells, seen = {}, set()
    for i, cp, off, w, s, h in slots:
        require(i in hosting, 'unknown host child')
        pair, cap, stages = hosting[i]
        require(s in stages, 'stage outside window')
        require(pair != active[s], 'host pair active at stage')
        require(0 <= cp < COPIES and 0 <= h < R and 0 <= s < STAGES, 'index domain')
        require(w == 8, 'residual width')
        require(0 <= off and off + w <= cap, 'slot extent')
        occ = cells.setdefault((i, cp), set())
        new = set(range(off, off + w))
        require(not occ & new, 'cell collision')
        occ |= new
        require((s, h) not in seen, 'duplicate (stage, helper)')
        seen.add((s, h))
    require(seen == {(s, h) for s in range(STAGES) for h in range(R)}, 'missing (stage, helper)')
    rem = Counter()
    for i, (pair, cap, stages) in hosting.items():
        for cp in range(COPIES):
            r = cap - len(cells.get((i, cp), ()))
            if r:
                rem[r] += 1
    return rem


def main(args):
    t0 = time.time()
    repo = os.path.abspath(args.repo)
    raw = {}
    for rel, (sha, blob) in PINS.items():
        raw[rel] = read_pinned(repo, rel, sha, blob)
    vend = {}
    for rel, pin in VENDOR.items():
        vend[rel] = read_pinned(HERE, rel, pin['sha256'], pin['git_blob'])[1]
    P = load_module('r438_packing', *raw['research/bit589-width-packing/packing.py'])
    S72 = load_module('r438_seed72_verify', *raw['research/bit589-width7-windows-seed72/verify.py'])
    S14 = load_module('r438_seed14_verify', *raw['research/bit-helper470-window-placement-seed14/verify.py'])
    HC = load_module('r438_pr442_hosting_core', *raw['research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
                                                    'vendor/idle-axis-hosting/hosting_core.py'])
    cert = json.loads(vend['vendor/pr1043/CERTIFICATE.json'])
    controls = []
    pin = VENDOR['vendor/pr1043/CERTIFICATE.json']
    tampered = vend['vendor/pr1043/CERTIFICATE.json'].replace(b'"1": 1321', b'"1": 1320', 1)
    require(tampered != vend['vendor/pr1043/CERTIFICATE.json'], 'tamper control setup')
    expect_reject(controls, 'vendored_pr1043_certificate_tampered',
                  lambda: check_pin(tampered, pin['sha256'], pin['git_blob'], 'vendor/pr1043/CERTIFICATE.json'),
                  'sha256 pin')
    out = dict(status='PASS_' + TAG, scope='bit headroom only; no new kappa; the selected record is complex-bound; every R438 row is conditional on PR1043 (open, not admitted); row (b) also on the transported word of verify_transport.py',
               inputs=dict(main_tree={rel: dict(sha256=s, git_blob=b) for rel, (s, b) in sorted(PINS.items())},
                           vendored={rel: dict(sha256=p['sha256'], git_blob=p['git_blob'], origin=p['origin'])
                                     for rel, p in VENDOR.items()}))

    # -- 0. Baseline binding: PR589 record, PR1023 slot model, PR1043 certificate. ------------------------------------
    record = P.pinned_json('bit_record')
    selection = P.pinned_json('selection')
    model = P.slot_model(record, selection)
    W = record['nine']['bit']['live']
    require((model['R'], model['v'], W, model['calls']) == (439, V, 28416, STAGES * T), 'PR589 record dimensions')
    c0 = Q(record['nine']['bit_lower'])
    require(grid_decimal(c0) == C0_DECIMAL, 'PR589 bit endpoint')
    local439 = Counter(model['local'])
    require(unkeyed(cert['local']['baseline']['profile']) == dict(local439), 'PR1043 baseline local = PR589 record')
    require(unkeyed(cert['hosted']['baseline']['invoice']['bit_profile']) == dict(model['H']),
            'PR1043 baseline hosted profile = PR589 record')
    require(Q(cert['hosted']['baseline']['invoice']['bit_lower']) == c0, 'PR1043 baseline c = PR589 c')
    local_a = Counter(unkeyed(cert['local']['candidate']['profile']))
    require(cert['local']['candidate']['helpers'] == 438 and cert['hosted']['candidate']['invoice']['R'] == 438, 'R438')
    d = Counter(local_a)
    d.subtract(local439)
    require(+d == Counter({2: 2}) and -d == Counter({1: 2, 3: 1, 7: 1}), 'PR1043 local delta {1:-2,2:+2,3:-1,7:-1}')
    for name, loc in (('a', local_a), ('b', Counter(LOCAL_B))):
        require(sum(r * n for r, n in loc.items()) == 8 * 438 + 63 + 14 * V == 5121, 'local rank mass (%s)' % name)
        require(sum(loc.values()) == 2918, 'local child count (%s)' % name)

    # -- 1. Windows and slots. ---------------------------------------------------------------------------------------
    WIN72 = S72.WIN                                    # global_k anchor + three window predicates (seed72 windows.py)
    win14 = S14.windows(S14.schedule())                # seed14's independent transcription: {idx: (pair, rank, stages)}
    require(set(WIN72) == {i for i, (p, r, st) in win14.items() if r and st}, 'hosting children agree')
    require(all(win14[i][1:] == (WIN72[i][0], tuple(WIN72[i][1])) for i in WIN72), 'seed72 and seed14 windows agree')
    require({i: c for i, (c, st) in WIN72.items()} == model['caps'], 'window capacities = PR1023 slot capacities')
    hosting = {i: (win14[i][0], WIN72[i][0], tuple(WIN72[i][1])) for i in sorted(WIN72)}
    sched72 = S72.wopt.windows.schedule()
    active = {e['stage']: e['pair'] for e in sched72 if e['kind'] == 'local_cover_sweep'}
    require(sorted(active) == list(range(STAGES)), 'one local sweep per stage')
    slots = Counter()
    for i, (c, st) in WIN72.items():
        slots[c] += COPIES
    require(slots == model['slots'] == Counter({7: 666, 14: 444, 28: 444, 42: 444}), 'slots per replica')
    units = sum((c // 8) * n for c, n in slots.items())
    S439, S438 = units - STAGES * 439, units - STAGES * 438
    require((units, S439, S438) == (3996, 45, 54), 'width-8 slack per replica')
    out['windows'] = {str(i): dict(pair=p, capacity=c, stages=list(st)) for i, (p, c, st) in hosting.items()}
    out['slots_per_replica'] = keyed(slots)
    out['width8_units_per_replica'] = dict(capacity=units, slack_R439=S439, slack_R438=S438)

    # -- 4a. Endpoint positive controls (needed for the DP grid points). ---------------------------------------------
    def profile(local, idle):
        H = Counter({r: n * STAGES * T for r, n in local.items()})
        for r, n in idle.items():
            H[r] += n * T
        require(all(n > 0 for n in H.values()), 'positive profile entries')
        return dict(sorted(H.items()))

    def price(local, idle, label):
        H = profile(local, idle)
        require(sum(r * n for r, n in H.items()) == 1808352, 'hosted rank mass (%s)' % label)
        require(M * M > 2 * max(H) ** 2, 'halving guard (%s)' % label)
        return P.endpoint(H, W), H

    c_pr589, H_pr589 = price(local439, model['idle_rep'], 'pr589')
    require(c_pr589 == c0 and H_pr589 == dict(model['H']), 'positive control: PR589 endpoint reproduced')
    # PR1043's own hosting_change, re-derived from the frozen selection with seed14's allocate (R = 439).
    alloc439 = S14.allocate(selection['bit'])
    removed = [list(x) for x in alloc439 if x[5] == 470 - 2 * V]
    require(removed == cert['hosting_change']['removed_slots'], 'PR1043 removed slots re-derived')
    rem439, _ = S14.placement_audit(alloc439, win14, frozenset())
    rem_inplace = Counter(rem439)
    for i, cp, off, w, s, h in removed:
        rem_inplace[(i, cp)] += w
    idle_pr1043 = Counter(r for r in rem_inplace.values() if r)
    require(dict(idle_pr1043) == unkeyed(cert['hosting_change']['new_remainders']), 'PR1043 in-place remainders')
    require(Counter(r for r in rem439.values() if r) == model['idle_rep'], 'PR589 remainders from seed14 allocate')
    c_pr1043, H_pr1043 = price(local_a, idle_pr1043, 'pr1043')
    require(H_pr1043 == unkeyed(cert['hosted']['candidate']['invoice']['bit_profile']), 'PR1043 hosted profile')
    require(c_pr1043 == Q(cert['hosted']['candidate']['invoice']['bit_lower']), 'PR1043 endpoint (certificate)')
    require(grid_decimal(c_pr1043) == PR1043_DECIMAL, 'positive control: PR1043 endpoint reproduced')

    # -- 1. Exact DP.  S = 45 positive control, then S = 54. --------------------------------------------------------
    c0_star = c0 + GRID
    cert45 = certify_optimum(P, slots, S439, c0_star, W, check_exhaustive=True)
    require(cert45['covered'] == EXPECTED_LAYOUTS[45], 'exhaustive enumeration covered every S = 45 layout')
    require(cert45['opt'] == (((42, 5), 9),), 'S = 45 optimum is nine fully idle 42-slots')
    require(cert45['idle_opt'] == model['idle_rep'], 'S = 45 optimum = PR589 selected remainders')
    pr1023 = P.width8_optimality(model, c0_star)       # PR1023's own per-unit certificate (hard-coded slack 45)
    require(pr1023['runner_up'] == 'capacity 42, u = 4' and pr1023['slack_units_per_replica'] == 45, 'PR1023 replay')

    # The PR1023 per-unit argument cannot be reused at R438: its hard-coded slack 45 rejects the R438 model.
    model438 = dict(model, R=438, idle_rep=Counter({2: 433, 4: 444, 6: 444, 7: 666, 42: 10, 34: 1}))
    expect_reject(controls, 'pr1023_width8_optimality_hardcoded_45_rejects_R438',
                  lambda: P.width8_optimality(model438, c0_star), 'slack per replica')

    # Endpoint candidates (a) and (b): the DP optimum is computed at each one's own next grid point.
    rows = {}
    certs = {}
    # Candidate layout: the S = 54 DP optimum at c0 + 1e-24.  It is priced with each local profile, and the DP is then
    # re-certified at that profile's own next grid point, where it must return the same layout.
    candidate = certify_optimum(P, slots, S438, c0_star, W, check_exhaustive=False)['idle_opt']
    for name, local, scout in (('a', local_a, SCOUT_A), ('b', Counter(LOCAL_B), SCOUT_B)):
        idle = candidate
        c, H = price(local, idle, name)
        cs = certify_optimum(P, slots, S438, c + GRID, W, check_exhaustive=True)
        require(cs['covered'] == EXPECTED_LAYOUTS[54], 'exhaustive enumeration covered every S = 54 layout (%s)' % name)
        require(cs['idle_opt'] == idle, 'DP optimum at c + 1e-24 is the priced layout (%s)' % name)
        require(grid_decimal(c) == scout, 'scouting endpoint (%s) reproduced' % name)
        certs[name] = cs
        rows['r438_window_optimum_local_' + name] = dict(endpoint=grid_decimal(c), endpoint_fraction=str(c),
                                                          profile=keyed(H), children=sum(H.values()),
                                                          rank_mass=sum(r * n for r, n in H.items()))
        rows['r438_window_optimum_local_' + name]['_c'] = c
    ca = rows['r438_window_optimum_local_a'].pop('_c')
    cb = rows['r438_window_optimum_local_b'].pop('_c')
    require(certs['a']['opt'] == (((42, 4), 1), ((42, 5), 10)), 'R438 optimum = 10 fully idle 42-slots + one (42,4)')
    require(certs['a']['run'] == (((14, 1), 1), ((28, 3), 1), ((42, 5), 10)), 'R438 runner-up')
    require(dict(certs['a']['idle_opt']) == {2: 433, 4: 444, 6: 444, 7: 666, 42: 10, 34: 1}, 'R438 idle profile')
    c_b_inplace, _ = price(Counter(LOCAL_B), idle_pr1043, 'b_inplace')
    c_run_a, _ = price(local_a, certs['a']['idle_run'], 'runner_up_a')
    require(c_pr1043 < c_run_a < ca, 'runner-up layout endpoint lies between PR1043 and the optimum')
    rows['r438_runner_up_layout_local_a'] = dict(endpoint=grid_decimal(c_run_a), layout=layout_name(certs['a']['run']))
    rows['pr589_r439_selected'] = dict(endpoint=grid_decimal(c0), profile=keyed(H_pr589))
    rows['pr1043_r438_inplace_local_a'] = dict(endpoint=grid_decimal(c_pr1043), profile=keyed(H_pr1043),
                                               children=sum(H_pr1043.values()))
    rows['pr1043_r438_inplace_local_b'] = dict(endpoint=grid_decimal(c_b_inplace))
    for key, c in (('r438_window_optimum_local_a', ca), ('r438_window_optimum_local_b', cb),
                   ('pr1043_r438_inplace_local_b', c_b_inplace), ('r438_runner_up_layout_local_a', c_run_a)):
        rows[key]['gain_vs_pr1043_percent'] = dfloor(100 * (c - c_pr1043) / c_pr1043, 8)
        rows[key]['gain_vs_pr589_percent'] = dfloor(100 * (c - c0) / c0, 8)

    # PR1043's in-place layout, as a layout: certified strictly worse than the optimum at c_a + 1e-24.
    ca_cert = certs['a']
    lay1043 = (((14, 1), 1), ((28, 1), 3), ((42, 1), 5), ((42, 5), 9))
    require(idle_of(slots, ca_cert['rmin'], lay1043) == idle_pr1043, 'PR1043 layout = its in-place remainders')
    g1043 = gap_interval(ca_cert['G'], idle_pr1043, ca_cert['idle_opt'])
    require(g1043[0] > 0, 'PR1043 in-place layout is strictly worse than the optimum')
    require(claim_is_optimal(ca_cert, ca_cert['opt']), 'the optimum certifies')
    expect_reject(controls, 'dp_with_move_42_4_dropped_vs_exhaustive',
                  lambda: certify_optimum(P, slots, S438, ca + GRID, W, check_exhaustive=True, dp_drop=((42, 4),)),
                  'exhaustive enumeration disagrees with the DP')
    expect_reject(controls, 'runner_up_claimed_optimal',
                  lambda: require(claim_is_optimal(ca_cert, ca_cert['run']), 'claimed optimum not certified'),
                  'claimed optimum not certified')
    expect_reject(controls, 'pr1043_inplace_layout_claimed_optimal',
                  lambda: require(claim_is_optimal(ca_cert, lay1043), 'claimed optimum not certified'),
                  'claimed optimum not certified')
    bad_idle = Counter(ca_cert['idle_opt'])
    bad_idle[34] -= 1
    bad_idle[2] += 1                                   # silently host the four missing residuals: mass must change
    expect_reject(controls, 'optimum_profile_with_partial_slot_dropped', lambda: price(local_a, +bad_idle, 'bad'),
                  'hosted rank mass')
    for name, c in (('a', ca), ('b', cb)):
        H = profile(local_a if name == 'a' else Counter(LOCAL_B), certs[name]['idle_opt'])

        def accept_next(H=H, c=c):
            lo, hi = P.MOMENT.moment(H, M, W, c + GRID, True)
            require(hi < 1, 'moment at c + 1e-24 is not below one')
        expect_reject(controls, 'endpoint_plus_1e-24_accepted_%s' % name, accept_next, 'not below one')

    out['dp'] = dict(S45_positive_control=dict(cert45['receipt'], pr1023_width8_optimality=dict(
        runner_up_per_unit=pr1023['runner_up'], margin_lower_bound=pr1023['margin_lower_bound'])),
        S54_at_c_a_next=certs['a']['receipt'], S54_at_c_b_next=certs['b']['receipt'],
        pr1043_inplace_layout=dict(layout=layout_name(lay1043), idle_per_replica=keyed(idle_pr1043),
                                   gap_sum_g_per_replica_at_c_a_next=[dfloor(g1043[0]), dceil(g1043[1])],
                                   gap_moment_at_c_a_next=[dfloor(T * g1043[0] / (M * W), 40),
                                                           dceil(T * g1043[1] / (M * W), 40)]))

    # -- 2. Stage-window feasibility (seed72 max-flow, independent Hall test). ----------------------------------------
    supply = {s: 438 for s in range(STAGES)}
    allowed = {i: set(st) for i, (p, c, st) in hosting.items()}
    configs = [(x4, part) for x4 in range(11) for part in (4, 6)]
    feasible = []
    flows = {}
    for cfg in configs:
        dem = demand_for(cfg)
        require(sum(dem.values()) == STAGES * 438, 'demand total')
        x = S72.maxflow_assign(supply, dem, allowed)
        ok, _ = hall_check(supply, dem, allowed)
        require((x is not None) == ok, 'max-flow and Hall disagree at %s' % (cfg,))
        if x is not None:
            require(all(s in allowed[i] and n > 0 for (s, i), n in x.items()), 'flow inside windows')
            require(all(sum(n for (s, i), n in x.items() if i == j) == dem[j] for j in dem), 'flow meets demand')
            require(all(sum(n for (s, i), n in x.items() if s == t) == 438 for t in range(STAGES)), 'flow uses supply')
            feasible.append(cfg)
            flows[cfg] = x
    require(len(feasible) == len(configs), 'every split of the optimum over children 4/6 is window-feasible')

    def tightened(child, stages):
        def run():
            al = dict(allowed)
            al[child] = set(stages)
            dem = demand_for((0, 6))
            ok, why = hall_check(supply, dem, al)
            x = S72.maxflow_assign(supply, dem, al)
            require((x is None) == (not ok), 'max-flow and Hall disagree on the tightened window')
            require(x is not None, 'infeasible: Hall violated by %s' % why)
        return run
    expect_reject(controls, 'window_child4_tightened_to_stages_0_1', tightened(4, (0, 1)), 'Hall violated')
    expect_reject(controls, 'window_child6_tightened_to_stages_7_8', tightened(6, (7, 8)), 'Hall violated')

    def r439_supply():
        x = S72.maxflow_assign({s: 439 for s in range(STAGES)}, demand_for((0, 6)), allowed)
        require(x is not None, 'infeasible: 439 helpers per stage do not fit the R438 optimum')
    expect_reject(controls, 'r439_supply_into_r438_optimum', r439_supply, 'do not fit')
    out['windows_feasibility'] = dict(configs_checked=len(configs), feasible=len(feasible),
                                      note='x4 idle 42-copies in child 4, 10-x4 in child 6, one-residual copy in '
                                           'child 4 or 6; children 0,2,7,8 full; capacity-7 children host nothing')

    # -- 3. Explicit placement of all helper occurrences. -------------------------------------------------------------
    chosen = (0, 6)
    x = flows[chosen]
    patterns = [[0, [8], COPIES], [1, [], COPIES], [2, [8] * 3, COPIES], [3, [], COPIES], [4, [8] * 5, COPIES],
                [5, [], COPIES], [6, [], 10], [6, [8], 1], [6, [8] * 5, COPIES - 11], [7, [8] * 3, COPIES],
                [8, [8], COPIES]]
    sel438 = dict(patterns=patterns, stages=sorted([i, 8, s, n] for (s, i), n in x.items()))
    require(S14.R == 439 and S14.V == V and S14.T == T, 'seed14 constants')
    S14.R = 438                                    # adapt seed14's allocator/audit to R = 438 (module instance only)
    try:
        alloc = S14.allocate(sel438)
        rem438, _ = S14.placement_audit(alloc, win14, frozenset())
        owners = S14.owners_for_replicas(alloc, win14)
    finally:
        S14.R = 439
    require(len(alloc) == STAGES * 438, 'occurrences per replica')
    win_hc = {i: (p, c, frozenset(st)) for i, (p, c, st) in hosting.items()}
    ys = {(i, tuple(pat)): n for i, pat, n in patterns}
    zs = {(i, w, s): n for i, w, s, n in sel438['stages']}
    slots_hc, rem_hc = HC.expand(win_hc, ys, zs, {s: [(h, 8) for h in range(438)] for s in range(STAGES)}, COPIES)
    require(slots_hc == alloc, 'seed14 allocate = PR442 expand (slot for slot)')
    idle_seed14 = Counter(r for r in rem438.values() if r)
    idle_hc = Counter(r for r in rem_hc.values() if r)
    idle_mine = audit_slots(alloc, hosting, active, 438)
    require(idle_seed14 == idle_hc == idle_mine == ca_cert['idle_opt'], 'placement remainders = DP optimum')
    seen = set()
    for stage, rep, h, fam, child, off, w in owners:
        r_, rest = divmod(fam, 8 * V)
        pair2, port = divmod(rest, V)
        require(r_ == rep and pair2 // 2 == hosting[child][0] != active[stage], 'owner family pair')
        require((stage, rep, h) not in seen, 'owner once')
        seen.add((stage, rep, h))
    require(len(seen) == STAGES * T * 438 == 126144, 'all hosted residual roles')
    canon = json.dumps([list(t) for t in alloc], separators=(',', ':')).encode()
    out['placement'] = dict(split='all 10 idle 42-copies and the one-residual copy in child 6', selection=sel438,
                            occurrences_per_replica=len(alloc), hosted_residual_roles=len(seen),
                            idle_per_replica=keyed(idle_seed14), slot_list_sha256=hashlib.sha256(canon).hexdigest(),
                            builders_agree='seed14 allocate == PR442 hosting_core.expand',
                            audits='seed14 placement_audit, independent audit_slots, seed14 owners_for_replicas')

    def mutated(fn):
        lst = [list(t) for t in alloc]
        fn(lst)
        return [tuple(t) for t in lst]

    def first(pred, lst):
        return next(k for k, t in enumerate(lst) if pred(t))

    def m_window(lst):
        k = first(lambda t: t[0] == 4, lst)
        lst[k][4] = 6                                  # child 4 admits stages 0-5
    def m_collision(lst):
        k = first(lambda t: t[0] == 4 and t[2] == 8, lst)
        lst[k][2] = 0
    def m_duplicate(lst):
        k = first(lambda t: t[0] == 2 and t[2] == 8, lst)
        j = first(lambda t: t[4] == lst[k][4] and t[5] != lst[k][5], lst)
        lst[k][5] = lst[j][5]
    def m_missing(lst):
        del lst[-1]
    def m_extent(lst):
        k = first(lambda t: t[0] == 6 and t[1] == COPIES - 11, lst)
        lst[k][2] = 36                                 # 36 + 8 > 42
    def m_domain(lst):
        lst[-1][5] = 438
    def m_width(lst):
        lst[0][3] = 7
    mutations = [('placement_stage_outside_window', m_window, 'outside untouched window', 'stage outside window'),
                 ('placement_cell_collision', m_collision, 'coordinate collision', 'cell collision'),
                 ('placement_duplicate_helper', m_duplicate, 'duplicate helper', 'duplicate (stage, helper)'),
                 ('placement_missing_helper', m_missing, 'missing helper', 'missing (stage, helper)'),
                 ('placement_slot_extent', m_extent, 'slot extent', 'slot extent'),
                 ('placement_helper_out_of_domain', m_domain, 'owner domain', 'index domain'),
                 ('placement_width7_residual', m_width, 'helper residual width', 'residual width')]

    def seed14_audit(lst, win, R=438):
        S14.R = R
        try:
            S14.placement_audit(lst, win, frozenset())
        finally:
            S14.R = 439
    for name, fn, n14, mine in mutations:
        lst = mutated(fn)
        expect_reject(controls, name + '/seed14', lambda lst=lst: seed14_audit(lst, win14), n14)
        expect_reject(controls, name + '/independent', lambda lst=lst: audit_slots(lst, hosting, active, 438), mine)
    # Owner activity: swap the (stage, helper) of the first child-6 role with the first stage-1 role (child j), and
    # widen the windows so that both moved roles are inside them: child 6 gets stage 1 (its pair 0 is the active pair
    # there) and child j gets the child-6 role's stage (where child j's pair is not active).  The occurrence set,
    # widths and cells are unchanged; only the active-data (owner inactivity) rule can reject.
    lst = [list(t) for t in alloc]
    k6 = first(lambda t: t[0] == 6, lst)
    kj = first(lambda t: t[4] == 1, lst)
    j, s6 = lst[kj][0], lst[k6][4]
    require(hosting[6][0] == active[1] and hosting[j][0] != active[s6], 'active-pair control setup')
    (lst[kj][4], lst[kj][5]), (lst[k6][4], lst[k6][5]) = (lst[k6][4], lst[k6][5]), (lst[kj][4], lst[kj][5])
    lst = [tuple(t) for t in lst]
    win14_mut, hosting_mut = dict(win14), dict(hosting)
    for child, extra in ((6, 1), (j, s6)):
        win14_mut[child] = win14[child][:2] + (tuple(sorted(set(win14[child][2]) | {extra})),)
        hosting_mut[child] = hosting[child][:2] + (tuple(sorted(set(hosting[child][2]) | {extra})),)
    expect_reject(controls, 'placement_host_pair_active/seed14', lambda: seed14_audit(lst, win14_mut),
                  'host is active data')
    expect_reject(controls, 'placement_host_pair_active/independent',
                  lambda: audit_slots(lst, hosting_mut, active, 438), 'host pair active at stage')
    expect_reject(controls, 'placement_audited_as_R439/seed14', lambda: seed14_audit(alloc, win14, R=439),
                  'missing helper')
    expect_reject(controls, 'placement_audited_as_R439/independent', lambda: audit_slots(alloc, hosting, active, 439),
                  'missing (stage, helper)')

    # -- 4. Endpoint summary. ----------------------------------------------------------------------------------------
    out['endpoints'] = rows
    out['claims'] = dict(
        optimum_idle_per_replica=keyed(ca_cert['idle_opt']),
        c_window_optimum_local_a=grid_decimal(ca), c_window_optimum_local_b=grid_decimal(cb),
        c_pr1043_inplace=grid_decimal(c_pr1043), c_pr589=grid_decimal(c0),
        certificate='moment(opt, c+1e-24) > 1 by both engines; every other no-bank R438 slot layout has a certified '
                    'larger idle sum at c+1e-24 with the same child count and local profile, hence a larger moment; '
                    'so no layout in the slot model reaches c+1e-24',
        kappa='unchanged; the bit side does not bind')
    out['negative_controls'] = controls
    elapsed = time.time() - t0
    return out, elapsed, ca, cb, c_pr1043


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--repo', default=DEFAULT_REPO,
                    help='repository root (default: the parent of the research/ directory holding this script)')
    ap.add_argument('--out', help='write the JSON receipt here (e.g. RECEIPT.json next to this script)')
    ap.add_argument('--check', help='require the regenerated receipt to equal this file byte for byte')
    a = ap.parse_args()
    if sys.flags.optimize or not __debug__:
        print('FAIL_%s refusing to run under python -O (assert-based checks in pinned modules would be skipped)' % TAG)
        sys.exit(2)
    try:
        receipt, elapsed, ca, cb, c1043 = main(a)
        text = json.dumps(receipt, indent=1, sort_keys=True) + '\n'
        if a.check:
            with open(a.check) as handle:
                require(handle.read() == text, 'receipt differs from ' + a.check)
        if a.out:
            with open(a.out, 'w') as handle:
                handle.write(text)
    except (Exception, SystemExit) as e:  # seed72's need() raises SystemExit
        print('FAIL_%s %s: %s' % (TAG, type(e).__name__, e))
        sys.exit(1)
    print('python %s; %.1f s' % (sys.version.split()[0], elapsed))
    print('PASS_%s S=54 opt=10x(42,5)+1x(42,4) idle={2:433,4:444,6:444,7:666,34:1,42:10} c_a=%s c_b=%s '
          'pr1043_inplace=%s window_splits=22/22 controls=%d no_new_kappa'
          % (TAG, grid_decimal(ca), grid_decimal(cb), grid_decimal(c1043), len(receipt['negative_controls'])))
