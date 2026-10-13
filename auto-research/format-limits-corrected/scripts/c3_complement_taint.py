"""Rigidity of the complement sink (Lemma R): on the 112-target, 9-bit-port decoder every target has exactly one
admissible sink, the standard one.

Setting (frames and the common-frame identity: upstream/build/sections/03-motifs.tex:154-186; the route operator
C_sink C_source^-1 of a complex interface: 03-motifs.tex:568-640; the recursive contract: 05-layers.tex:141-154).
A word is a scalar program on registers 0..n-1, n = 2V+R, V = 112 ports.  Registers 0..V-1 are the sources s
(port vector u_s in F_2^9), V..2V-1 the targets T_t, 2V.. the helper and centre registers; its events are
['add', t, s, ...] (register t receives register s) in three phases A, cut, B.  A target T_t must end at a sink
V_t = w_t^perp with w_t odd-weight and w_t . u_t = 1 (the standard sink is w_t = u_t, V_t = u_t^perp; every other
choice is a 'complement' sink).

Two quantities are computed, both over GF(2) with 9-bit integers (bit 0 = least significant):

* lower closure lo(r): the smallest frame register r can stand at in ANY frame assignment of the same scalar word
  whose only drops are the centre drops at the cut.  Sources start at <u_s>; targets, helpers and centres start at 0
  (an entrance is a choice, 0 is the most permissive); every 'add' puts both registers at one common frame, so both
  get lo(t)+lo(s) (monotone from then on); at the cut every centre drops to 0 (the most permissive drop).  The final
  frame of T_t is at least lo(T_t), so any sink must satisfy lo(T_t) <= w_t^perp, i.e. w_t is orthogonal to lo(T_t);
  u_t in lo(T_t) would make the word illegal.
* drop-free source taint of T_t: the set of sources whose content reaches T_t along 'add' events (centres reset at
  the cut).  A source s whose content reaches T_t drop-free must be lossless, i.e. w_t . u_s = 0.

Lemma R: if the taint of T_t spans u_t^perp then w_t = u_t is the only complement sink of t.
Measured here: the taint of T_t is exactly the Gram-orthogonal neighbourhood {s != t : u_s . u_t = 0} (52 sources,
span of dimension 8 = u_t^perp), the most permissive closure has dimension 8 on all 112 targets, and w_t = u_t is the
only admissible sink on all 112; nothing reaches a target in phase A, no target carries its own source.

Further checks on one word (#569 width7/eight):
* kmin: for a complement sink w != u_t (w odd, w . u_t = 1) the violated correctors are the taint sources s with
  w . u_s = 1; 'newly allowed' are sources s with u_s . u_t = 1 (illegal under u_t^perp) and w . u_s = 0.
  The minimum over w of the violated count is 20 on every target.
* positive control: the instrument does see freedom when it exists.  For the target T_0 and the complement sink
  w_0 (the first minimiser of the violated count) delete (i) the 3 events that write taint carrying a violated source
  into T_0 -- this does NOT free T_0, because the gate closure is stickier than the content taint -- and
  (ii) the 4 gates touching T_0 whose partner frame (at that point of the closure) is not inside w_0^perp -- now T_0
  has dim 7 and the two admissible sinks {u_0, w_0}, while the other 111 targets stay forced.

Words: #569 width7-eight and fourcold-eight, #571 combined-eight-local (DominikScholz), #531 direct-delivery504
(icekylinx, file of main).  Run: python3 c3_complement_taint.py
"""
import gzip
import json
import time
from collections import Counter

from report import check, finish, DATA, VENDOR, main_file

V = 112          # ports (sources) and targets
NB = 9           # port bits

# ---------------------------------------------------------------------------------------------------------------
# expected values (from the recorded measurements)
EXPECTED = {
    'dim': 8,                  # dim lo(T_t) = dim u_t^perp
    'n_taint': 52,             # |{s != t : u_s . u_t = 0}|
    'kmin': 20,                # min over complement sinks w of the number of violated correctors
    # (violated, newly allowed) over all (t, w), w odd, w.u_t = 1, w != u_t: 127 sinks per target
    'kdist': {(20, 32): 336, (22, 30): 5376, (24, 28): 896, (24, 32): 448, (28, 28): 896, (28, 32): 448,
              (30, 30): 5376, (32, 32): 336, (52, 0): 112},
    'w0': 0b110000001,         # first minimiser for target 0, printed as 110000001
    'w0_violated': 20,
    'taint_filter_removed': 3,      # events writing violated taint into T_0
    'closure_filter_removed': 4,    # gates touching T_0 whose partner frame is not inside w0^perp
    'closure_dims': {7: 1, 8: 111},
    'closure_admissible': {1: 111, 2: 1},
}

WORDS = [          # (key, label, path, has recorded entrance-frame variant)
    ('width7_eight', '#569 width7/eight', VENDOR / 'pr569' / 'width7-eight-FULL-WORD.json.gz', True),
    ('fourcold_eight', '#569 fourcold/eight', VENDOR / 'pr569' / 'fourcold-eight-FULL-WORD.json.gz', True),
    ('combined_eight_local', '#571 combined-eight-local', VENDOR / 'pr571' / 'combined-eight-local-FULL-WORD.json.gz', True),
    ('direct504_local', '#531 direct-delivery504 local',
     'research/direct-delivery504-global/evidence/local/FULL-WORD.json.gz', False),
]


# ---------------------------------------------------------------------------------------------------------------
# GF(2) helpers on 9-bit integers
def par(x):
    return bin(x).count('1') & 1


def basis(vs):
    """reduced row echelon basis (tuple, canonical order) of the span of the integers vs."""
    b = {}
    for x in vs:
        for p in sorted(b, reverse=True):
            if x >> p & 1:
                x ^= b[p]
        if x:
            p = x.bit_length() - 1
            for q in list(b):
                if b[q] >> p & 1:
                    b[q] ^= x
            b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


def in_span(x, B):
    return len(basis(list(B) + [x])) == len(B)


def perp_vectors(B):
    return [z for z in range(1, 1 << NB) if all(par(z & b) == 0 for b in B)]


def admissible_sinks(D, u):
    """odd-weight w with w.u = 1 and w orthogonal to the frame D."""
    return [z for z in perp_vectors(D) if par(z & u) and par(z)]


# ---------------------------------------------------------------------------------------------------------------
def lower_closure(word, skip=None, entrances=False):
    """lo(r) for every register.  skip(phase, i, t, s, lo) -> True deletes the i-th event of the phase (an 'add' gate
    of registers t, s); used by the positive control."""
    R = word['report']['R']
    n = 2 * V + R
    P = word['ports']
    lo = {}
    for r in range(n):
        if r < V:
            lo[r] = (P[r],)
        elif entrances and r >= 2 * V and str(r) in word.get('start_extra', {}):
            lo[r] = basis(word['start_extra'][str(r)])
        else:
            lo[r] = ()
    removed = []

    def run(phase, seq):
        for i, e in enumerate(seq):
            if e[0] != 'add':
                continue
            t, s = e[1], e[2]
            if skip is not None and skip(phase, i, t, s, lo):
                removed.append((phase, i, t, s))
                continue
            F = basis(list(lo[t]) + list(lo[s]))
            lo[t] = F
            lo[s] = F

    run('A', word['A'])
    for c in word['centers']:
        lo[c] = ()
    run('cut', word['cut'])
    run('B', word['B'])
    return lo, removed


def closure_report(word, lo):
    """per-target (dim lo, #admissible sinks, w==u forced) plus counters."""
    P = word['ports']
    dims, free = Counter(), Counter()
    illegal = forced = 0
    sinks = {}
    for t in range(V):
        D, u = lo[V + t], P[t]
        if in_span(u, D):
            illegal += 1
            sinks[t] = (len(D), None)
            continue
        ws = admissible_sinks(D, u)
        dims[len(D)] += 1
        free[len(ws)] += 1
        forced += (ws == [u])
        sinks[t] = (len(D), ws)
    return dict(dims=dict(sorted(dims.items())), free=dict(sorted(free.items())), illegal=illegal, forced=forced,
                sinks=sinks)


def source_taint(word, skip=None):
    """taint[r] = set of sources whose content reaches register r drop-free (centres reset at the cut).
    Returns (taint after A, final taint, removed events); skip(phase, i, t, s, taint) deletes an event."""
    n = 2 * V + word['report']['R']
    taint = {r: ({r} if r < V else set()) for r in range(n)}
    removed = []

    def run(phase, seq):
        for i, e in enumerate(seq):
            if e[0] == 'add':
                if skip is not None and skip(phase, i, e[1], e[2], taint):
                    removed.append((phase, i, e[1], e[2]))
                    continue
                taint[e[1]] |= taint[e[2]]
    run('A', word['A'])
    after_A = {t: set(taint[V + t]) for t in range(V)}
    for c in word['centers']:
        taint[c] = set()
    run('cut', word['cut'])
    run('B', word['B'])
    return after_A, taint, removed


def kmin_stats(word, taint):
    """(min violated per target, Counter over all (t, w != u_t) of (violated, newly allowed))."""
    P = word['ports']
    dist = Counter()
    mins = {}
    argmin0 = None
    for t in range(V):
        u, S = P[t], taint[V + t]
        nonorth = [s for s in range(V) if s != t and par(P[s] & u)]
        best = None
        for z in range(1, 1 << NB):
            if par(z) and par(z & u) and z != u:
                viol = sum(1 for s in S if par(z & P[s]))
                new = sum(1 for s in nonorth if not par(z & P[s]))
                dist[(viol, new)] += 1
                if best is None or viol < best:
                    best = viol
                    if t == 0:
                        argmin0 = z          # first z (increasing) attaining the minimum
        mins[t] = best
    return mins, dist, argmin0


# ---------------------------------------------------------------------------------------------------------------
def load_word(path):
    p = main_file(path) if isinstance(path, str) else path
    return json.loads(gzip.decompress(p.read_bytes()))


def run_word(key, label, path, has_entrance_variant, words_out):
    word = load_word(path)
    words_out[key] = word
    P = word['ports']
    assert len(P) == V and word['report']['R'] == 504
    tag = 'C3t.%s.' % key
    t0 = time.time()

    lo, _ = lower_closure(word)
    rep = closure_report(word, lo)
    is_perp = all(all(par(b & P[t]) == 0 for b in lo[V + t]) for t in range(V))      # lo(T_t) lies in u_t^perp
    check(tag + 'closure_dim8', rep['dims'] == {EXPECTED['dim']: V} and rep['illegal'] == 0 and is_perp,
          '%s: dim lo(T_t) %s on %d targets (= u_t^perp: %s), u_t in lo(T_t): %d' % (label, rep['dims'], V, is_perp, rep['illegal']))
    only_u = all(s[1] == [P[t]] for t, s in rep['sinks'].items())
    check(tag + 'sink_forced', rep['free'] == {1: V} and rep['forced'] == V and only_u,
          '#admissible sinks %s, w_t = u_t forced on %d/%d' % (rep['free'], rep['forced'], V))

    after_A, taint, _ = source_taint(word)
    eq = sum(1 for t in range(V)
             if taint[V + t] == {s for s in range(V) if s != t and not par(P[s] & P[t])})
    nsrc = Counter(len(taint[V + t]) for t in range(V))
    span = Counter(len(basis([P[s] for s in taint[V + t]])) for t in range(V))
    check(tag + 'taint_is_orth_neighbourhood',
          eq == V and dict(nsrc) == {EXPECTED['n_taint']: V} and dict(span) == {EXPECTED['dim']: V},
          'taint == {s != t : u_s.u_t = 0} on %d/%d, #sources %s, span dim %s' % (eq, V, dict(nsrc), dict(span)))
    spanA = Counter(len(basis([P[s] for s in after_A[t]])) for t in range(V))
    check(tag + 'nothing_reaches_targets_in_A', dict(spanA) == {0: V},
          'span dim of the taint after phase A only: %s' % dict(spanA))
    own = sum(1 for t in range(V) if t in taint[V + t])
    check(tag + 'no_own_source', own == 0, 'targets carrying their own source drop-free: %d' % own)

    mins, dist, _ = kmin_stats(word, taint)
    check(tag + 'kmin20', Counter(mins.values()) == Counter({EXPECTED['kmin']: V}),
          'min over complement sinks w != u_t of #violated correctors: %s' % dict(Counter(mins.values())))
    if key == 'width7_eight':
        check(tag + 'kmin_distribution', dict(dist) == EXPECTED['kdist'],
              '(violated, newly allowed) over %d (t, w) pairs: %s' % (sum(dist.values()), sorted(dist.items())))

    if has_entrance_variant:
        lo2, _ = lower_closure(word, entrances=True)
        rep2 = closure_report(word, lo2)
        check(tag + 'closure_with_word_entrances', rep2['dims'] == {EXPECTED['dim']: V} and rep2['free'] == {1: V}
              and rep2['illegal'] == 0,
              'closure with the word\'s own entrance frames (start_extra): dims %s, sinks %s' % (rep2['dims'], rep2['free']))
    else:
        print('NOTE %s: the word stores its helper entrance frames in a convention this closure does not model (frames '
              'taken from the start would put u_t in the closure); the claims above use the most permissive '
              'entrances, every helper at 0, which bound every frame assignment' % label, flush=True)
    return time.time() - t0


def positive_control(key, word, label):
    """delete the gates/events that carry the lossless corrections of T_0 and watch the instrument see freedom."""
    P = word['ports']
    tag = 'C3t.posctl.%s.' % key
    T0 = V
    _, taint, _ = source_taint(word)
    _, _, w0 = kmin_stats(word, taint)
    u0 = P[0]
    viol = {s for s in taint[T0] if par(w0 & P[s])}
    check(tag + 'w0', w0 == EXPECTED['w0'] and len(viol) == EXPECTED['w0_violated'],
          '%s: target 0, u_0 = %s, w_0 = %s, violated correctors %d' % (
              label, format(u0, '09b'), format(w0, '09b'), len(viol)))

    # (i) taint-filtered: delete the events writing violated taint into T_0 (from the content taint), then recompute
    #     the gate closure without those events
    def skip_taint(phase, i, t, s, taint_now):
        return t == T0 and bool(taint_now[s] & viol)
    _, _, removed_t = source_taint(word, skip=skip_taint)
    gone = {(ph, i) for ph, i, _, _ in removed_t}
    lo_t, _ = lower_closure(word, skip=lambda ph, i, t, s, lo: (ph, i) in gone)
    rep_t = closure_report(word, lo_t)
    d0, ws0 = rep_t['sinks'][0]
    check(tag + 'taint_filter_does_not_free',
          len(removed_t) == EXPECTED['taint_filter_removed'] and rep_t['dims'] == {EXPECTED['dim']: V}
          and rep_t['free'] == {1: V} and (d0, ws0) == (EXPECTED['dim'], [u0]) and w0 not in ws0,
          'removed %d events (partners %s); dims %s, #admissible %s, T_0 (dim, sinks) = (%d, %s), w_0 admissible: %s' % (
              len(removed_t), [s for _, _, _, s in removed_t], rep_t['dims'], rep_t['free'], d0, ws0, w0 in ws0))

    # (ii) closure-filtered: delete the gates touching T_0 whose partner frame is not inside w0^perp
    def skip_closure(phase, i, t, s, lo_now):
        if T0 not in (t, s):
            return False
        partner = s if t == T0 else t
        return any(par(w0 & b) for b in lo_now[partner])
    lo_c, rm_c = lower_closure(word, skip=skip_closure)
    rep_c = closure_report(word, lo_c)
    d0, ws0 = rep_c['sinks'][0]
    check(tag + 'closure_filter_frees_T0',
          len(rm_c) == EXPECTED['closure_filter_removed'] and rep_c['dims'] == EXPECTED['closure_dims']
          and rep_c['free'] == EXPECTED['closure_admissible'] and rep_c['illegal'] == 0
          and sorted(ws0) == sorted([u0, w0]) and rep_c['forced'] == V - 1,
          'removed gates %s (phase, event, t, s); dims %s, #admissible %s, T_0 (dim, sinks) = (%d, %s), others forced: %d/%d' % (
              rm_c, rep_c['dims'], rep_c['free'], d0, ws0, rep_c['forced'], V - 1))
    # (the gates removed are the correction gates read at T_0: each partner holds a violated source)
    reads_target = sum(1 for e in word['B'] if e[0] == 'add' and V <= e[2] < 2 * V)
    check(tag + 'every_target_read_once', reads_target == V,
          'B events whose source register is a target: %d' % reads_target)


def main():
    t_start = time.time()
    words = {}
    for key, label, path, flag in WORDS:
        dt = run_word(key, label, path, flag, words)
        print('  (%s: %.1f s)' % (key, dt), flush=True)
    t0 = time.time()
    for key in ('width7_eight', 'fourcold_eight', 'combined_eight_local'):
        positive_control(key, words[key], dict((k, l) for k, l, _, _ in WORDS)[key])
    print('  (positive control: %.1f s)' % (time.time() - t0), flush=True)
    print('total %.1f s' % (time.time() - t_start))
    finish()


if __name__ == '__main__':
    main()
