#!/usr/bin/env python3
"""Independent audit of PR #4629's 213-helper re-padding ledger and its price.

Apache-2.0.  Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance.

Does NOT import PR #4629's build.py, verify.py or scan_kernels.py.  It reads:

  * PR #4629's written artifacts, vendored byte-for-byte from head
    2cf7d081118f6f702aa317816d231b41ce073579 (Git blob and SHA-256 pinned below);
  * PR4470's base word from main's shipped `research/joint-helper-lattice/native_joint.py`
    (`construct()`), only to obtain the base frames, roles and program;
  * optionally (`--replay`) main's shipped `literal_replay` on the written word.

Everything else (span arithmetic, the quotient image of every base frame, the
paid-rank walk, helper widths, the invoice and the two-constraint screen in
50-digit Decimal) is written here.

    python3.12 -B verify.py            # ~10 s
    python3.12 -B verify.py --replay   # also runs the shipped literal replay
"""
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter
from decimal import Decimal, getcontext
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
getcontext().prec = 50

PR_HEAD = '2cf7d081118f6f702aa317816d231b41ce073579'
VENDORED = {
    'PR4629-QUOTIENT-WORD.json.gz': (
        'research/complex-ambient-quotient/QUOTIENT-WORD.json.gz',
        '31444b48850cbe220d4ddbf88496722682581fb8',
        '10155f81100e9cd6283f1d9dfd071bc0c3e0e89dc3794a66e4129a1f34d99dc4'),
    'PR4629-QUOTIENT-PROGRAMS.json.gz': (
        'research/complex-ambient-quotient/QUOTIENT-PROGRAMS.json.gz',
        '7fe7923f34d0233d60a51cfd369002765491e870',
        '52d70e135c0ea30439932c19c815c4cd5d6e784372dfc8069ce6786d1c0d955c'),
}
KERNEL = 153
ROLES, MAINS = 632, 224
PORTS, PAIRS, SPLIT, CALLS = 112, 16, 7, 18
U, CUT, GAMMA = Decimal(1)/Decimal(5), Decimal(20), Decimal('0.97')

# Numbers stated by others, which this verifier recomputes (not inputs).
PR4629_CLAIM = dict(helpers={3: 2, 6: 7, 7: 47, 8: 139, 9: 213},
                    paid={1: 2177, 2: 424, 3: 389, 4: 147, 5: 50, 8: 8},
                    deficit=1688, surplus=3776, kappa='0.015637149091', block7_stated=-1264)
FRONTIER = dict(helpers={4: 28, 7: 7, 8: 47, 9: 326},
                paid={1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}, kappa='0.003020165977')
# petalas #4627 (head b5d71c72) declared profiles for #4596-style 1-helper padding.
PETALAS = {153: dict(helpers={3: 2, 4: 26, 6: 7, 7: 47, 8: 325, 9: 1},
                     paid={1: 1991, 2: 424, 3: 389, 4: 147, 5: 24, 8: 8},
                     kappa='0.016567169219'),
           511: dict(helpers={3: 2, 4: 26, 6: 7, 7: 47, 8: 325, 9: 1},
                     paid={1: 2034, 2: 382, 3: 412, 4: 139, 5: 36, 8: 8},
                     kappa='0.012091850234')}


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


# ---------------------------------------------------------------- GF(2) spans
def span(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in out}
    s = frozenset(out)
    need(len(s) == 1 << len(basis), 'dependent basis %r' % (basis,))
    return s


def dim(s):
    return len(s).bit_length() - 1


PIVOT = (KERNEL & -KERNEL).bit_length() - 1


def phi(v):
    """PR #4629's stated surjection F2^9 -> F2^8 with kernel span{153}."""
    if (v >> PIVOT) & 1:
        v ^= KERNEL
    return (v & ((1 << PIVOT) - 1)) | ((v >> (PIVOT + 1)) << PIVOT)


def image(s):
    return frozenset(phi(x) for x in s)


# ------------------------------------------------------- independent paid walk
def paid_walk(start, final, program):
    """Own re-derivation of the paid ledger: every role is moved into each
    scalar/warp frame by the minimal nested climb; centres are charged their
    absolute dimension change; every role then climbs to its final frame.
    Frames are spans (frozensets).  Recorded climbs in `program` are ignored,
    exactly as the shipped synthesize ignores them."""
    cur = list(start)
    paid = Counter()
    climbs_into = Counter()

    def climb(r, f):
        if cur[r] == f:
            return
        need(cur[r] < f, 'non-nested climb for role %d' % r)
        paid[dim(f) - dim(cur[r])] += 1
        climbs_into[(r, dim(f) - dim(cur[r]))] += 1
        cur[r] = f

    i = 0
    while i < len(program):
        e = program[i]
        i += 1
        k = e[0]
        if k == 'climb':
            continue
        if k == 'center':
            a, b = e[2], e[3]
            if i < len(program) and program[i][0] == 'center' and program[i][2] == b:
                b = program[i][3]
                i += 1
            need(a < b or b < a, 'centre not nested')
            paid[abs(dim(a) - dim(b))] += 1
        elif k == 'scalar':
            g, f = e[1], e[2]
            if g[0] == 'clear':
                continue
            for r in (g[1:3] if g[0] in ('add', 'copy') else g[1:2]):
                if r[0] == 'L':
                    climb(r[1], f)
        elif k == 'warp':
            r = e[1][1]
            climb(r, e[3])
            cur[r] = e[4]
    end = []
    for r in range(ROLES):
        before = cur[r]
        climb(r, final[r])
        end.append(dim(final[r]) - dim(before))
    return paid, end


def helpers_of(start, final):
    return Counter(dim(final[r]) - dim(start[r]) for r in range(MAINS, ROLES))


def mass(p):
    return sum(r * n for r, n in p.items())


# ----------------------------------------------- invoice and Decimal screen
def invoice(helpers, paid, block):
    T = Counter({r: CALLS * n for r, n in helpers.items()})
    P = Counter({r: CALLS * n for r, n in paid.items()})
    P[1] += PORTS * (2 * PAIRS + 1 - CALLS)
    T[1 + block * (PAIRS + 2)] += 2 * PORTS
    for length in (SPLIT, PAIRS - 1 - SPLIT):
        for j in range(1, length + 1):
            T[1 + block * (j + 1)] += 2 * PORTS
            P[block * (j + 1)] += 2 * PORTS
    return T, P, mass(T) - mass(P)


def mom(p, t):
    return sum(n * (Decimal(r).ln() * t).exp() for r, n in p.items() if n and r > 0)


def ok(T, P, kappa):
    t = 1 - kappa
    mt = mom(T, t)
    return mom(P, t) < mt and mom(P, t + U) < GAMMA * (CUT.ln() * U).exp() * mt


def kappa_of(T, P):
    """Upper end of the first admissible kappa interval on (1e-7, 0.25]
    (the PR's scan convention), bisected 160 times in 50-digit Decimal."""
    lo, hi, steps = Decimal('1e-7'), Decimal('0.25'), 2400
    last = None
    for i in range(steps + 1):
        k = lo + (hi - lo) * i / steps
        if ok(T, P, k):
            last = k
        elif last is not None:
            a, b = last, k
            for _ in range(160):
                m = (a + b) / 2
                a, b = (m, b) if ok(T, P, m) else (a, m)
            return a
    return last


def price(helpers, paid, block=8):
    T, P, s = invoice(helpers, paid, block)
    return s, kappa_of(T, P)


def same12(k, claim):
    return k is not None and abs(k - Decimal(claim)) < Decimal('5e-13')


# --------------------------------------------------------------- inputs
def pinned_artifacts():
    out = {}
    for name, (path, blob, sha) in VENDORED.items():
        data = (HERE / name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == sha, '%s SHA-256 differs from PR head' % name)
        got = subprocess.run(['git', 'hash-object', '--no-filters', str(HERE / name)],
                             capture_output=True, text=True, check=True).stdout.strip()
        need(got == blob, '%s git blob differs from %s:%s' % (name, PR_HEAD, path))
        out[name] = json.loads(gzip.decompress(data))
    return out['PR4629-QUOTIENT-WORD.json.gz'], out['PR4629-QUOTIENT-PROGRAMS.json.gz']


_BASE = []


def base_word():
    if not _BASE:
        sys.path.insert(0, str(ROOT / 'research/joint-helper-lattice'))
        import native_joint as J  # shipped on main; used only for the PR4470 base word
        c, programs, *_ = J.construct()
        _BASE.append((c, programs))
    return json.loads(json.dumps(_BASE[0][0])), _BASE[0][1]


def shipped_cache_check(word):
    """Main's shipped embedded_cache_roles (requires exactly 213 cold full-ended)."""
    sys.path.insert(0, str(ROOT / 'research/fresh-helper-boundary'))
    import native as F
    X = F.load(ROOT / 'research/kappa-rebuild/complex/native_extensions.py', 'a_cache')
    try:
        X.embedded_cache_roles(word)
        return True
    except ValueError:
        return False


def to_spans(c):
    S = [span(b) for b in c['frames']]
    return S, [S[x] for x in c['start']], [S[x] for x in c['final']]


def map_program(program, S, f=lambda s: s):
    out = []
    for e in program:
        e = json.loads(json.dumps(e))
        if e[0] == 'scalar':
            e[2] = f(S[e[2]])
        elif e[0] in ('warp', 'climb'):
            e[3], e[4] = f(S[e[3]]), f(S[e[4]])
        elif e[0] == 'center':
            e[2], e[3] = f(S[e[2]]), f(S[e[3]])
        out.append(e)
    return out


def logical(program):
    """Scalar and warp events with span frames: the part of a program the
    quotient must preserve (climbs are re-derived, centres checked separately)."""
    return [(e[0], json.dumps(e[1]), e[2]) if e[0] == 'scalar' else
            (e[0], json.dumps(e[1]), e[2], e[3], e[4])
            for e in program if e[0] in ('scalar', 'warp')]


# --------------------------------------------------------------- analysis
def analyse(word, programs, report=True):
    FULL9 = frozenset(range(512))
    base, base_programs = base_word()
    bS, bstart, bfinal = to_spans(base)
    wS, wstart, wfinal = to_spans(word)
    res = {}

    # 1. the written word is phi(base) on every role, except re-padded finals
    need(all(wstart[r] == image(bstart[r]) for r in range(ROLES)), 'a start is not phi(base start)')
    padded = [r for r in range(ROLES) if wfinal[r] != image(bfinal[r])]
    need(all(MAINS <= r and wfinal[r] == FULL9 and wstart[r] == frozenset({0}) for r in padded),
         're-padded role that is a main, not cold, or not ending at F2^9')
    inc = Counter(9 - dim(image(bfinal[r])) for r in padded)
    unpadded_final = [image(bfinal[r]) for r in range(ROLES)]
    res['padded_roles'] = len(padded)
    res['pad_increment_hist'] = dict(sorted(inc.items()))
    res['padded_from_helper_width'] = dict(sorted(Counter(
        dim(image(bfinal[r])) - dim(image(bstart[r])) for r in padded).items()))

    # 2. programs: the written logical program is phi(base logical program)
    for d in ('forward', 'backward'):
        need(logical(map_program(programs[d], wS)) == logical(map_program(base_programs[d], bS, image)),
             '%s scalar/warp program is not the phi-image of the base program' % d)

    # 3. the ninth axis: which frames and events reach it
    union8 = set()
    for s in wS:
        if s != FULL9:
            union8 |= s
    res['ambient_without_F2^9_frame'] = dim(frozenset(union8)) if len(union8) & (len(union8) - 1) == 0 else None
    res['frames_with_vector_ge_256'] = sum(1 for s in wS if max(s) >= 256)
    touch = 0
    for d in ('forward', 'backward'):
        for e in map_program(programs[d], wS):
            if e[0] == 'scalar':
                touch += e[2] == FULL9
            elif e[0] == 'warp':
                touch += FULL9 in (e[3], e[4])
            elif e[0] == 'center':
                touch += FULL9 in (e[2], e[3])
    res['scalar_warp_center_events_in_F2^9'] = touch
    res['roles_ending_in_F2^9'] = sum(1 for r in range(ROLES) if wfinal[r] == FULL9)
    res['mains_ending_in_F2^9'] = sum(1 for r in range(MAINS) if wfinal[r] == FULL9)

    # 4. independent paid ledgers: frontier, written word, written word un-padded
    ledgers = {}
    for name, (st, fi, prog, S, f) in {
            'frontier': (bstart, bfinal, base_programs, bS, lambda s: s),
            'written': (wstart, wfinal, programs, wS, lambda s: s),
            'unpadded': (wstart, unpadded_final, programs, wS, lambda s: s)}.items():
        pf, end = paid_walk(st, fi, map_program(prog['forward'], S, f))
        pb, _ = paid_walk(st, fi, map_program(prog['backward'], S, f))
        need(pf == pb, '%s: forward/backward paid ledgers differ' % name)
        h = helpers_of(st, fi)
        ledgers[name] = dict(helpers=dict(sorted(h.items())), paid=dict(sorted(pf.items())),
                             deficit=mass(pf) - mass(h), end=end)
    res['ledgers'] = {k: {kk: vv for kk, vv in v.items() if kk != 'end'} for k, v in ledgers.items()}
    end_w = ledgers['written']['end']
    res['padded_final_climb_ranks'] = dict(sorted(Counter(end_w[r] for r in padded).items()))
    dP = Counter(ledgers['written']['paid'])
    dP.subtract(ledgers['unpadded']['paid'])
    res['paid_written_minus_unpadded'] = {k: v for k, v in sorted(dP.items()) if v}

    # 5. cold full-ended helper sets and the embedded caches
    f0 = [r for r in range(MAINS, ROLES) if base['start'][r] == 0 and base['final'][r] == 1]
    f1 = [r for r in range(MAINS, ROLES) if word['start'][r] == 0 and word['final'][r] == 1]
    res['cold_full_ended'] = dict(frontier=len(f0), written=len(f1), common=len(set(f0) & set(f1)),
                                  frontier_first8=f0[:8], written_first8=f1[:8])
    res['written_full_ended_from_frontier_width4'] = sum(
        1 for r in f1 if dim(bfinal[r]) - dim(bstart[r]) == 4)

    # 6. per-port q on the written word (rohanarun's split, here on the artifact)
    q0 = sum(1 for p in range(PORTS) if wstart[p] <= wfinal[PORTS + p])
    res['ports_X_entrance_inside_Y_terminal'] = q0
    res['shipped_cache_check'] = {'frontier': shipped_cache_check(base), 'written': shipped_cache_check(word)}
    res['main_widths'] = dict(sorted(Counter(dim(wfinal[r]) - dim(wstart[r]) for r in range(MAINS)).items()))
    return res, ledgers


def priced(ledgers):
    out = {}
    for name in ('frontier', 'written', 'unpadded'):
        L = ledgers[name]
        s8, k8 = price(L['helpers'], L['paid'], 8)
        s7, k7 = price(L['helpers'], L['paid'], 7)
        out[name] = dict(surplus_block8=s8, kappa_block8=k8, surplus_block7=s7, kappa_block7=k7)
    for v, L in PETALAS.items():
        s8, k8 = price(L['helpers'], L['paid'], 8)
        out['petalas_%d' % v] = dict(surplus_block8=s8, kappa_block8=k8)
    return out


def check(res, ledgers, prices):
    W, F = ledgers['written'], ledgers['frontier']
    need(F['helpers'] == FRONTIER['helpers'] and F['paid'] == FRONTIER['paid'],
         'frontier ledger not reproduced')
    need(W['helpers'] == PR4629_CLAIM['helpers'], 'written helper profile != #4629 claim')
    need(W['paid'] == PR4629_CLAIM['paid'], 'written paid profile != #4629 claim')
    need(W['deficit'] == PR4629_CLAIM['deficit'] == ledgers['unpadded']['deficit'], 'deficit')
    need(same12(prices['frontier']['kappa_block8'], FRONTIER['kappa']), 'frontier kappa')
    need(prices['written']['surplus_block8'] == PR4629_CLAIM['surplus'], 'surplus')
    need(same12(prices['written']['kappa_block8'], PR4629_CLAIM['kappa']), 'written kappa')
    # PROOF.md states -1,264 at block 7; the same invoice gives -256 (still < 0).
    need(prices['written']['surplus_block7'] == -256 != PR4629_CLAIM['block7_stated'], 'block-7 surplus')
    need(prices['frontier']['surplus_block7'] == -3280, 'frontier block-7 surplus')
    for v, L in PETALAS.items():
        need(same12(prices['petalas_%d' % v]['kappa_block8'], L['kappa']), 'petalas %d kappa' % v)
    # the audit findings, asserted
    need(res['padded_roles'] == 213, 'padded role count')
    need(res['pad_increment_hist'] == {1: 187, 5: 26}, 'pad increments')
    need(res['padded_final_climb_ranks'] == {1: 187, 5: 26}, 'padded final climbs')
    need(res['paid_written_minus_unpadded'] == {1: 187, 5: 26}, 'paid delta of re-padding')
    need(res['ambient_without_F2^9_frame'] == 8, 'ambient without the padded frame')
    need(res['frames_with_vector_ge_256'] == 1, 'only F2^9 uses the ninth axis')
    need(res['scalar_warp_center_events_in_F2^9'] == 0, 'no operation acts in F2^9')
    need(res['roles_ending_in_F2^9'] == 213 and res['mains_ending_in_F2^9'] == 0, 'F2^9 finals')
    cf = res['cold_full_ended']
    need((cf['frontier'], cf['written'], cf['common']) == (326, 213, 187), 'cold full-ended sets')
    need(res['written_full_ended_from_frontier_width4'] == 26, 'width-4 helpers made full-ended')
    need(res['shipped_cache_check'] == {'frontier': False, 'written': True}, 'shipped cache check')
    need(res['ports_X_entrance_inside_Y_terminal'] == 56, 'per-port q=0 count')


def controls(word, programs, res, ledgers):
    """Deliberately broken inputs must fail."""
    rejected = 0
    # (a) a paid ledger with the re-pad charged as the README describes
    #     ("one rank each") is not what the written word produces
    claimed_desc = Counter(ledgers['unpadded']['paid'])
    claimed_desc[1] += 213
    rejected += dict(sorted(claimed_desc.items())) != ledgers['written']['paid']
    # (b) a tampered vendored artifact is rejected by the pin
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / 'x.gz'
        raw = (HERE / 'PR4629-QUOTIENT-WORD.json.gz').read_bytes()
        bad.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
        rejected += hashlib.sha256(bad.read_bytes()).hexdigest() != VENDORED['PR4629-QUOTIENT-WORD.json.gz'][2]
    # (c) moving one main final changes a role off phi(base): analysis must fail
    broken = json.loads(json.dumps(word))
    broken['final'][0] = broken['start'][0]
    try:
        analyse(broken, programs)
    except SystemExit:
        rejected += 1
    # (d) a perturbed paid profile does not reproduce the claimed kappa
    P = dict(PR4629_CLAIM['paid'])
    P[5] -= 1
    P[4] += 1
    _, k = price(PR4629_CLAIM['helpers'], P, 8)
    rejected += not same12(k, PR4629_CLAIM['kappa'])
    # (e) block 7 pricing of the same ledger is inadmissible
    rejected += price(PR4629_CLAIM['helpers'], PR4629_CLAIM['paid'], 7)[0] < 0
    need(rejected == 5, 'only %d/5 controls rejected' % rejected)
    return rejected


def shipped_replay(word, programs):
    sys.path.insert(0, str(ROOT / 'research/fresh-helper-boundary'))
    import native as F
    V = F.load(ROOT / 'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'a_rows')
    X = F.load(ROOT / 'research/kappa-rebuild/complex/native_extensions.py', 'a_lit')
    c = {'frames': word['frames'], 'start': word['start'], 'final': word['final'], 'v': 112, 'R': 408}
    out = {}
    for d in ('forward', 'backward'):
        syn = F.synthesize(dict(c, precondition=[], A=[], B=[], cut=[], compensation=[],
                                cleanup=[], tail=[]), programs[d])
        rows, rec = X.literal_replay(V, c, syn, d == 'backward')
        bad = sum(rows['L', r] != V.expected(('L', r), [], d == 'backward', False) for r in range(ROLES))
        need(bad == 0 and not rows['C', 0], '%s replay failed' % d)
        out[d] = {int(k): v for k, v in rec['paid_profile'].items()}
    return out


def fmt(k):
    return None if k is None else '%.15f' % k


def main():
    word, programs = pinned_artifacts()
    res, ledgers = analyse(word, programs)
    prices = priced(ledgers)
    check(res, ledgers, prices)
    n = controls(word, programs, res, ledgers)
    if '--replay' in sys.argv:
        rep = shipped_replay(word, programs)
        need(rep['forward'] == rep['backward'] == ledgers['written']['paid'],
             'shipped replay ledger != independent walk')
        res['shipped_replay_paid'] = rep['forward']
    res['prices'] = {k: {kk: (fmt(vv) if 'kappa' in kk else vv) for kk, vv in v.items()}
                     for k, v in prices.items()}
    res['controls_rejected'] = n
    print(json.dumps(res, indent=1, default=str))
    print('PASS_PR4629_REPAD_LEDGER_AUDIT')


if __name__ == '__main__':
    main()
