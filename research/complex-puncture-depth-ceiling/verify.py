#!/usr/bin/env python3
"""Price the E8 port-count / puncture-depth lever with #1240's exact packing ceiling.

Model (every premise explicit; a favorable relaxation, not a construction):
  * the selected #1094 local word is re-derived from the pinned assembly (profile minus the
    independent idle histogram); its eight rank-8 children are the centre copies;
  * V = 120 - p live E8 lines, 8 V live families per nine-stage replica, coverage law
    mass = 72 W + cst N, idle rank cap 51 (#1240's ceiling.py, unchanged);
  * PR717's P1 per-port knob, as transported in complex-frame-pair-decoders/verify.py
    section G: one port is one source climb (1,1,1,5) and one target climb (1,1,4,1,1) per call.
    Here it is applied linearly in both directions from V = 112 (an extrapolation above 112);
  * eight-term centre with balanced term costs: cst = 8q + s has s terms of rank q+1 and 8-s of
    rank q. This reproduces every split of frame-pair-decoders' attained chain p = 0..24;
  * the attained floor cst(p) = max(72 - p, 56), p <= 24, from complex-frame-pair-decoders.

Sensitivity: the same table with the non-centre word scaled proportionally to V (no intercept).

usage: verify.py [--write]
Jack Galler, with substantial Claude (Anthropic) assistance. Apache-2.0.
"""
import json, sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
import ceiling as C  # noqa: E402  (#1240, pinned in SOURCES.json)

M, STAGES, V0, CST0 = 73, 9, 112, 64
PORT = {1: 7, 4: 1, 5: 1}           # PR717 P1 knob: source (1,1,1,5) + target (1,1,4,1,1) per call
GRID = Q(1, 10 ** 12)
TARGET = Q(1, 99)
FAILS = []


def check(name, ok, msg):
    print(('PASS ' if ok else 'FAIL ') + name + ' | ' + msg)
    if not ok:
        FAILS.append(name)


def dec(x, d=12):
    return f'{float(x):.{d}g}'


def floor_cst(p):
    """Attained exact eight-term decoder floor on the 120-line E8 set (frame-pair-decoders, p <= 24)."""
    C.require(0 <= p <= 24, 'floor is proved only for p <= 24')
    return max(72 - p, 56)


def split(cst):
    q, s = divmod(cst, 8)
    return {r: n for r, n in ((q + 1, s), (q, 8 - s)) if r and n}


def selected_word():
    rec = json.loads((ROOT / 'certificates/selected-result.json').read_text())
    asm = json.loads((ROOT / rec['certificate']).read_text())
    ind = json.loads((ROOT / 'research/community-frontier1094-audit/INDEPENDENT1094.json').read_text())
    H = {int(r): n for r, n in asm['complex_profile'].items()}
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    N, W = ind['price']['calls'], ind['price']['live']
    C.require(W * STAGES == 8 * V0 * N, 'live stock is not 8 V per replica')
    C.require(sum(r * n for r, n in H.items()) == (M - 1) * W + CST0 * N, 'coverage identity fails')
    local = {}
    for r, n in H.items():
        k = n - idle.get(r, 0)
        C.require(k >= 0 and k % N == 0, 'local rank not uniform per call')
        if k:
            local[r] = k // N
    return rec, asm, local


def word(noncentre, V, cst, proportional=False):
    if proportional:
        d = {r: Q(n * V, V0) for r, n in noncentre.items()}
    else:
        d = dict(noncentre)
        for r, n in PORT.items():
            d[r] = d.get(r, 0) + (V - V0) * n
    for r, n in split(cst).items():
        d[r] = d.get(r, 0) + n
    C.require(all(n >= 0 for n in d.values()), 'knob extrapolation leaves a negative count')
    return {r: n for r, n in d.items() if n}


def cap(noncentre, V, cst, proportional=False):
    return C.ceiling(word(noncentre, V, cst, proportional), M, 8 * V, STAGES, cst, grid=GRID)


def passes(noncentre, V, cst, a, proportional=False):
    """Certified: +1 if relax(a) < 1 (ceiling > a), -1 if relax(a) > 1, error if unresolved."""
    lo, hi = C.relax(word(noncentre, V, cst, proportional), M, 8 * V, STAGES, cst, a)
    C.require(hi < 1 or lo > 1, 'enclosure does not separate 1')
    return hi < 1


def max_cst(noncentre, V, a, proportional=False, top=80):
    """Largest integer cst in [0, top] whose relaxation stays below one at a (None if none).
    relax is strictly increasing in cst: +1 cst adds one unit of mass to a centre child, moving it
    from rank q to q+1, with the idle mass unchanged (total and local mass both rise by one)."""
    if not passes(noncentre, V, 0, a, proportional):
        return None
    lo, hi = 0, top + 1
    C.require(not passes(noncentre, V, top, a, proportional), 'search top too small')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if passes(noncentre, V, mid, a, proportional) else (lo, mid)
    return lo


def main():
    rec, asm, local = selected_word()
    a_bit = Q(asm['bit_lower'])
    check('A.word', local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
          'selected local word re-derived from the pinned assembly: %s' % local)
    noncentre = {r: n for r, n in local.items() if r != 8}
    base = C.ceiling(word(noncentre, V0, CST0), M, 8 * V0, STAGES, CST0, grid=Q(1, 10 ** 15))
    ref = json.loads((ROOT / 'research/complex-local-word-ceiling/RESULT.json').read_text())
    check('A.base', base[1] == Q(ref['ceiling']['a_ceiling']),
          '#1240 ceiling reproduced exactly: a < %s' % dec(base[1], 15))
    a0 = base[1]
    idle = lambda V: 48 * V - 3730   # noqa: E731  idle mass per call = 72*8V/9 + cst - local mass
    check('A.idle', all(C.model(word(noncentre, V, floor_cst(120 - V)), M, 8 * V, STAGES, floor_cst(120 - V))['idle_mass']
                        == idle(V) > 0 for V in range(96, 121)),
          'knob words obey the coverage law with idle mass 48V - 3730 > 0 on V = 96..120')

    # B. the attained floor chain p = 0..24 under the PR717 knob, and the proportional sensitivity.
    chain, best = [], None
    for p in range(25):
        V, cst = 120 - p, floor_cst(p)
        a = cap(noncentre, V, cst)[1]
        ap = cap(noncentre, V, cst, True)[1]
        row = dict(p=p, V=V, cst=cst, centre=split(cst), ratio=str(Q(cst, V)), a_cap=str(a),
                   a_cap_decimal=dec(a), vs_selected_word=dec(a / a0, 6), kappa_cap=dec(a / (1 + a)),
                   proportional_a_cap_decimal=dec(ap), proportional_vs_selected_word=dec(ap / a0, 6))
        chain.append(row)
        if best is None or a > Q(best['a_cap']):
            best = row
    check('B.argmax', best['p'] == 16 and best['V'] == 104,
          'knob model: the floor chain peaks at P104, cst 56, a < %s (x%s), kappa < %s' % (
              best['a_cap_decimal'], best['vs_selected_word'], best['kappa_cap']))
    pbest = max(chain, key=lambda r: Q(r['proportional_a_cap_decimal']))
    check('B.argmax-proportional', pbest['p'] == 16,
          'proportional model also peaks at P104: x%s' % pbest['proportional_vs_selected_word'])
    check('B.unbind', Q(best['a_cap']) > a_bit and C.ceiling(word(noncentre, 104, 56), M, 832, STAGES, 56, grid=GRID)[0] > a_bit,
          'P104 ceiling exceeds the bit primitive %s: the lever can only unbind, not reach 1/99' % dec(a_bit))
    check('B.target', all(Q(r['a_cap']) < TARGET for r in chain) and Q(pbest['proportional_a_cap_decimal']) < TARGET / 5,
          'no p = 0..24 reaches a = 1/99 in either model (best is below 1/5 of it)')

    # C. the cst/V copy ratio is not a monotone proxy under the knob model.
    r112, r98 = chain[8], chain[22]
    check('C.ratio-proxy', r112['ratio'] == r98['ratio'] == '4/7' and C.ceiling(word(noncentre, 98, 56), M, 784, STAGES, 56, grid=GRID)[1] < base[0],
          'P112/cst 64 and P98/cst 56 share ratio 4/7, but P98 is certified below P112 (x%s)' % r98['vs_selected_word'])
    r104 = chain[16]
    check('C.ratio-proxy-proportional', Q(r104['proportional_a_cap_decimal']) > Q(r98['proportional_a_cap_decimal']) > Q(chain[24]['proportional_a_cap_decimal']),
          'proportional model orders P104 > P98 > P96 as ratio 7/13 < 4/7 < 7/12 does')

    # D. one-lever-at-a-time marginals at the selected point.
    port_up = cap(noncentre, 120, CST0)[1]
    port_dn = cap(noncentre, 104, CST0)[1]
    cst_dn = cap(noncentre, V0, 56)[1]
    check('D.port', port_up > a0 > port_dn,
          'ports alone at cst 64: V=120 x%s, V=104 x%s' % (dec(port_up / a0, 5), dec(port_dn / a0, 5)))
    check('D.cst', cst_dn > a0, 'cst alone at V=112: cst 56 gives x%s' % dec(cst_dn / a0, 5))
    # per-port excess spend versus per-port budget increment (#1240's B(a) and p_r(a))
    def unit(a):
        lam = C.child_cost(51, M, a)          # idle price per unit mass is lam / 51
        excess = [Q(0), Q(0)]
        for r, n in PORT.items():
            c = C.child_cost(r, M, a)
            excess[0] += n * (c[0] - r * lam[1] / 51)
            excess[1] += n * (c[1] - r * lam[0] / 51)
        dB = (Q(8, 9) * (1 - 72 * lam[1] / 51), Q(8, 9) * (1 - 72 * lam[0] / 51))
        return excess, dB
    ex0, b0 = unit(a0)
    ex1, b1 = unit(TARGET)
    check('D.port-budget', ex0[1] < b0[0] and ex1[1] < b1[0],
          'per port: excess %s < budget %s at the selected ceiling; excess %s < budget %s at 1/99' % (
              dec(ex0[1], 6), dec(b0[0], 6), dec(ex1[0], 6), dec(b1[1], 6)))

    # E. break-even decoder constants: the largest cst at each V that still beats each target.
    # the selected word's certified achievable end: cst 64 passes at V = 112 by construction
    targets = {'selected_word_ceiling': base[0], 'bit_primitive': a_bit, 'one_over_99': TARGET}
    table = {}
    for V in [82] + list(range(96, 121)):
        table[V] = {k: max_cst(noncentre, V, a) for k, a in targets.items()}
        table[V]['proportional_selected_word_ceiling'] = max_cst(noncentre, V, base[0], True)
    check('E.selected', table[112]['selected_word_ceiling'] == 64 and table[112]['proportional_selected_word_ceiling'] == 64
          and table[104]['selected_word_ceiling'] >= 56,
          'break-even cst: V=112 -> %d (control), V=104 -> %d, V=96 -> %d, V=120 -> %d' % (
              table[112]['selected_word_ceiling'], table[104]['selected_word_ceiling'],
              table[96]['selected_word_ceiling'], table[120]['selected_word_ceiling']))

    def min_ports(a, cst=CST0, top=1 << 13):
        C.require(not passes(noncentre, V0, cst, a) and passes(noncentre, top, cst, a), 'port search window')
        lo, hi = V0, top
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (lo, mid) if passes(noncentre, mid, cst, a) else (mid, hi)
        return hi
    need = {'bit_primitive': min_ports(a_bit), 'one_over_99': min_ports(TARGET)}
    check('E.ports-needed', need['bit_primitive'] <= 120 < need['one_over_99'],
          'knob extrapolated at cst 64: unbinding needs V >= %d; a = 1/99 needs V >= %d, beyond the 120 E8 lines' % (
              need['bit_primitive'], need['one_over_99']))
    check('E.floor', all((table[V]['selected_word_ceiling'] >= floor_cst(120 - V)) == (120 - V in range(8, 19))
                         for V in range(96, 121)),
          'the floor decoder reaches the selected word ceiling exactly for p = 8..18 (V = 102..112; p = 8 is the word)')
    check('E.target', all(table[V]['one_over_99'] is None for V in table),
          'a = 1/99 fails at every V even with cst = 0 (no centre at all)')
    p82 = {c: cap(noncentre, 82, c)[1] for c in (54, 55)}
    check('E.p82', all(a < a0 for a in p82.values()) and table[82]['selected_word_ceiling'] < 54,
          '#1187/#1455 82-port points (cst 55, 54): x%s, x%s; break-even needs cst <= %s' % (
              dec(p82[55] / a0, 5), dec(p82[54] / a0, 5), table[82]['selected_word_ceiling']))

    # F. failure controls
    try:
        cap(noncentre, 77, 56)
        bad = 'accepted'
    except ValueError as e:
        bad = 'rejected: ' + str(e)
    check('F.coverage', bad.startswith('rejected'), 'V = 77 leaves negative idle mass: ' + bad)
    try:
        floor_cst(25)
        bad = 'accepted'
    except ValueError as e:
        bad = 'rejected: ' + str(e)
    check('F.floor-scope', bad.startswith('rejected'), 'the floor is not applied beyond p = 24: ' + bad)
    check('F.monotone', all(passes(noncentre, 104, c, a0) or not passes(noncentre, 104, c + 1, a0) for c in range(0, 72)),
          'pass/fail in cst is monotone at V = 104 (no pass above a fail)')
    no_knob = cap({**noncentre, 1: noncentre[1] + 7 * 8}, 104, 56)[1]
    check('F.knob-matters', no_knob < Q(best['a_cap']),
          'keeping the 56 removed rank-1 children at P104 lowers its ceiling (x%s)' % dec(no_knob / a0, 5))

    result = dict(
        status='PASS' if not FAILS else 'FAIL', failures=FAILS,
        model=dict(m=M, stages=STAGES, families_per_replica='8V', coverage='mass = 72 W + cst N', idle_rank_cap=51,
                   port_knob=PORT, centre_split='balanced eight-term', floor='cst >= max(72 - p, 56), p <= 24',
                   selected_word=local, selected_word_ceiling=str(a0), bit_primitive=str(a_bit)),
        chain=chain, best=best, best_proportional=pbest,
        marginals=dict(ports_120_cst64=dec(port_up / a0, 6), ports_104_cst64=dec(port_dn / a0, 6),
                       v112_cst56=dec(cst_dn / a0, 6),
                       per_port_excess_at_selected=dec(ex0[1]), per_port_budget_at_selected=dec(b0[0]),
                       per_port_excess_at_1_99=dec(ex1[1]), per_port_budget_at_1_99=dec(b1[0])),
        ports_needed_at_cst64=need,
        break_even_cst={str(V): v for V, v in table.items()},
        p82={str(c): dec(a / a0, 6) for c, a in p82.items()},
        scope='Favorable relaxation (#1240 ceiling) under PR717 per-port knob and balanced eight-term centre; no word, '
              'decoder realization, owner map, moment certificate or kappa claim.')
    out = HERE / 'RESULT.json'
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        out.write_text(text)
    else:
        check('Z.result', out.exists() and out.read_text() == text, 'RESULT.json matches the recomputation byte for byte')
    if FAILS:
        print('FAIL_COMPLEX_PUNCTURE_DEPTH_CEILING', FAILS)
        sys.exit(1)
    print('PASS_COMPLEX_PUNCTURE_DEPTH_CEILING best P%d cst %d a_cap %s x%s; 1/99 unreachable at every V' % (
        best['V'], best['cst'], best['a_cap_decimal'], best['vs_selected_word']))


if __name__ == '__main__':
    main()
