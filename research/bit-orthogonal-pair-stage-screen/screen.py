#!/usr/bin/env python3
# Predecessors: navinor (PR1084, research/bit-orthogonal-pair-decoders: orthogonal-pair label decoders, cost-6 terms,
# the shipped P111 dual root, the P104 bit threshold of section H); eumemic (PR555, research/e8-bit-p111: gen_p3.py,
# the frozen L3 plan, the R439 punctured word and its nine/eleven-stage prices); DreamingOfClouds (PR589 tuned word and
# tune/fastc.py; PR545 punctured-star unit, rank-mass identity and adapt.py); PR493 eleven-stage chain; DaysSky (PR442
# idle-axis hosting windows); themilkman216 (PR968 P104 complex knob scenario, as re-implemented by PR1084).
# Builds on census.py and price.py of this package.
# Prepared with substantial AI assistance (Claude Code, Anthropic); Apache-2.0.
"""Stage screen: price every distinct census outcome of the frozen PR555 L3 reader family at 9 and 11 stages.

    python3 -I -B research/bit-orthogonal-pair-stage-screen/screen.py [--check]

1. Runs census.py --check (regenerates CENSUS.json byte for byte) and price.py (all pricer controls), both imported,
   and independent_census.py (subprocess, python3 -I -B), and requires their exact PASS lines.
2. Prices at R = 439 (the PR589 word's helper count; section 'comparison_at_R439'), with price.price /
   price.price_uniform:
     * every j attained by the census (uniform model, cost6 = j), at L = 9 and L = 11;
     * the shipped reader set (j = 1, dead dual 87 -> P110) and P111 (j = 0) with the plain transplant;
     * the five j = 5 reader sets with their actual dead duals ('transplant-swap', readers = that P), plus the plain
       transplant where every dead dual is live in the PR589 word, plus the j = 4 restriction of the one set whose
       fifth dead dual is line 3 (rule Z keeps lines 0..7 live; its decoder is re-replayed exactly);
     * all 82 admissible reader sets with j >= 4 at L = 11 (transplant-swap);
     * an upper envelope for each hostable (j, L): over ANY nine reader lines and ANY j dead lines, by linearity of the
       moment in the profile counts (see envelope()); it bounds the uniform, transplant and transplant-swap models.
3. Section 'own_R': reads CARRIERS.json.gz (carriers.py: real gen_p3 builds giving each reader set P its own helper
   count R(P), receivers from a bounded search), checks it against the census, and prices
     * every built j >= 4 set at L = 11 with R = R(P) (helper_model='average-helper', a premise);
     * the nine-stage no-bank wall R(P) <= 4v for every built j = 2/3 set;
     * a sensitivity line: for the best j >= 4 set, the largest R' <= R(P) whose eleven-stage c reaches each threshold.
4. Compares every c with the selected bit c (PR589, certificates/selected-result.json) and with two thresholds:
   PR1084's exact recorded P104 threshold b_P104 (+1.3294% over PR589 c; computed against the frontier942 complex
   profile) and 'P104_rebased' = b_now * b_P104 / b_942 (transfer premise: the same relative P104 complex gain applied
   to the current selected complex b_now; exact from the pinned strings).
5. Writes SCREEN.json (deterministic; --check compares byte for byte instead) and prints
   PASS_BIT_ORTHOGONAL_PAIR_STAGE_SCREEN ... as the last line.

Scope: a pricing screen, no word is built here; see SCREEN.json 'premises' for which numbers are exact and which rest
on model premises (transplant proxies, R = 439 in 'comparison_at_R439', the average-helper shift in 'own_R', PR620
asymmetric COPY, slot-model hosting, eleven-stage acceptance by the outer assembly).  No kappa is computed or claimed.
"""
import argparse
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

EXPECT_CENSUS = ('PASS_BIT_P102_ELIGIBLE_CENSUS eligible=19 admissible=17478 jmax=5 '
                 'jdist=0:4515,1:7975,2:3977,3:929,4:77,5:5 at_jmax=5 jmax_duals_outside_0_7=5 eligible_outside_0_7=18 '
                 'decoder_only_EA19=30411 jmax_EA19=5 P102_reachable=no shipped_j=1 shipped_dual=66-87 P110_cst=62 '
                 'controls=6 checks=33')
EXPECT_PRICE = ('PASS_BIT_STAGE_PRICER controls=2 checks=24 rows=24 '
                'P110@9 c=1745584654912925918569/1000000000000000000000000 hostable=True nine-stage-unhostable=8')
EXPECT_INDEP = ('PASS_BIT_P102_INDEPENDENT_CENSUS: eligible 19 (18 outside 0..7); EZA admissible 17478/48620; '
                'EA 30411/92378; j dist {0: 4515, 1: 7975, 2: 3977, 3: 929, 4: 77, 5: 5}; jmax 5 (5 P); '
                'P102 reachable False; shipped j 1 -> P110 cst 62; 127 fields agree')
SELECTED_CERT = 'research/community-frontier1094-audit/ASSEMBLY.json'
PR942_CERT = 'research/community-frontier942-audit/ASSEMBLY.json'
PINS = {
    'research/bit-orthogonal-pair-decoders/RESULTS.json':
        '7f3d6df3ab4dd9fd4a94ab36c444d777f1b45bf8a25ee880d6c1d8a363362e33',
    'research/bit-orthogonal-pair-decoders/SOURCES.json':
        '4a4eb9ff26c3d5825fd2a92e253e52036abe2cf65eaa367ed35c827e8dd32d5f',
    SELECTED_CERT: '1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045',
    PR942_CERT: '4b2894956e594e408e111d806c842f2ed2c32aefcadff93fad69ff0b46f1991a',
}
CARRIERS = 'research/bit-orthogonal-pair-stage-screen/CARRIERS.json.gz'   # package-local; sha256 recorded in SCREEN.json
CHECKS = []


def require(ok, msg):
    if not ok:
        raise AssertionError(msg)
    CHECKS.append(msg)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pinned_json(rel):
    require(sha(ROOT / rel) == PINS[rel], f'pin {rel}')
    return json.loads((ROOT / rel).read_bytes())


def load(name, fname):
    spec = importlib.util.spec_from_file_location(name, HERE / fname)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_captured(fn, argv):
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            fn(argv)
        except SystemExit as exc:
            code = exc.code
    lines = buf.getvalue().strip().splitlines()
    return code, lines[-1] if lines else ''


# --------------------------------------------------------------------------------------------- envelope
def envelope(PR, L, j):
    """Upper envelope of c over every reader set (any nine lines) and every j dead lines, cost6 = j, R = 439.

    For a fixed (L, v = 111 - j) the idle remainder, W and calls are common to all reader sets, and the moment is
    linear in the local counts: removing line t's x/y climbs lowers m*W*moment(c)/calls by D_t(c) = sum over its
    climbs x of G(x, c), G(r, c) = r (m/r)^c + 32 m^2 m^c / 10^16 (engine term incl. bad-residue surcharge); adding an
    average pattern raises it by D_avg(c).  transplant-swap removes |gone| = j + |added| lines and adds |added| <= 9
    average patterns, so moment_S(c) >= A(c) - j D_avg(c) - sum of the top (9 + j) positive excesses D_t - D_avg; the
    plain transplant (added = 0) and uniform (no excess) are bounded by the same expression.  The envelope profile
    attains it; its certified root c_env bounds every set (c_S <= c_env + 10^-24) provided the line ranking used is the
    ranking at the root, which is re-checked with the engine's interval arithmetic at c_env and c_env + 10^-24."""
    wd = PR.word_data()
    tpl = PR.template(L)
    m = tpl['m']
    pats = {}
    for t in range(wd['V']):
        pats.setdefault(tuple(sorted(wd['per'][t] + wd['per'][wd['V'] + t])), []).append(t)

    def ranking(c):
        G = {r: PR._G(r, m, c) for r in range(1, 8)}
        alo = sum(a * G[r][0] for r, a in wd['avg'].items())
        ahi = sum(a * G[r][1] for r, a in wd['avg'].items())
        ex = {k: (sum(G[x][0] for x in k) - ahi, sum(G[x][1] for x in k) - alo) for k in pats}
        keys = sorted(pats, key=lambda k: -(ex[k][0] + ex[k][1]))
        require(all(ex[a][0] > ex[b][1] for a, b in zip(keys, keys[1:])), 'envelope: pattern excesses strictly ordered')
        require(all(ex[k][0] > 0 or ex[k][1] < 0 for k in keys), 'envelope: excess signs certified')
        chosen = [t for k in keys if ex[k][0] > 0 for t in pats[k]][:9 + j]
        return chosen, [list(k) for k in keys if ex[k][0] > 0]

    def profile(chosen):
        loc = {r: Q(n) for r, n in wd['local'].items()}
        for t in chosen:
            for x in wd['per'][t] + wd['per'][wd['V'] + t]:
                loc[x] -= 1
        for r, a in wd['avg'].items():
            loc[r] = loc.get(r, 0) + (len(chosen) - j) * a
        loc[7] -= j
        loc[6] = loc.get(6, 0) + j
        require(all(n >= 0 for n in loc.values()), 'envelope profile nonnegative')
        loc = {r: n for r, n in sorted(loc.items()) if n}
        require(sum(r * n for r, n in loc.items()) == 8 * wd['R'] + 14 * (wd['V'] - j) + 63 - j, 'envelope mass')
        return loc

    c0 = Q(PR.price_uniform(j, j, L)['c_exact'])
    chosen, pos = ranking(c0)
    for _ in range(4):
        loc = profile(chosen)
        res = PR.price_profile(loc, wd['V'] - j, wd['R'], 63 - j, L)
        c = res['c']
        ch1, _ = ranking(c)
        ch2, _ = ranking(c + PR.GRID)
        if ch1 == chosen == ch2:
            break
        chosen = ch1
    else:
        raise AssertionError('envelope ranking did not stabilise')
    out = PR._finish(res, loc, dict(variant='envelope', j=j, cost6=j, dead_ports=None, dead_lines_geom=None))
    out['envelope_lines_removed'] = len(chosen)
    out['envelope_positive_excess_patterns'] = pos
    return out


# --------------------------------------------------------------------------------------------- own R(P)
def own_R(PR, CEN, census, enum, b104, t_reb):
    """Section 'own_R': price the reader sets built by carriers.py (CARRIERS.json.gz) with their own gen_p3 helper
    count R(P) instead of R = 439.  Returns (section, sha256 of CARRIERS.json.gz)."""
    raw = (ROOT / CARRIERS).read_bytes()
    cr_sha = hashlib.sha256(raw).hexdigest()
    d = json.loads(gzip.decompress(raw))
    res = d['results']
    HM = 'average-helper'
    # ---- consistency with the census
    pk = 'research/bit-orthogonal-pair-stage-screen/'
    require(d['inputs'][pk + 'census.py'] == sha(HERE / 'census.py') and
            d['inputs'][pk + 'CENSUS.json'] == sha(HERE / 'CENSUS.json'),
            'CARRIERS: built against the current census.py and CENSUS.json')
    jdist = census['j_distribution']['admissible_EZA']
    require(d['census_j_distribution_recomputed'] == jdist, 'CARRIERS: census j distribution = CENSUS.json')
    require(len({tuple(r['P']) for r in res}) == len(res), 'CARRIERS: reader sets distinct')
    tier_j = dict(ship=1, j5=5, j4=4, j3=3, j2=2)
    G = CEN.gram_from_lines()
    ROW = CEN.b0_rows(G)
    ROWIDX = {w: a for a, w in enumerate(ROW)}
    bad = []
    for r in res:
        rec = CEN.analyse(r['P'], G, ROW, ROWIDX)
        if rec is None or not (rec['j'] == r['j'] == tier_j[r['tier']] and rec['dead'] == r['dead_duals']):
            bad.append(r['P'])
    require(not bad, f'CARRIERS: j and dead duals of every record = census.analyse of its P ({len(res)} records)')
    for t in ('j5', 'j4', 'j3', 'j2'):
        n = sum(r['tier'] == t for r in res)
        require(n == d['coverage'][t]['domain'] == jdist[t[1]], f'CARRIERS: tier {t} lists the whole census domain')
    built = [r for r in res if r['status'] == 'built']
    require(all(r['R'] == 420 + 9 + r['x'] and r['x'] == r['extra_carriers'] + r['junk_wires'] and
                r['build_asserts_and_decoder_rows'] == 'PASS' for r in built),
            'CARRIERS: built records R = 429 + x, x = extra carriers + junk wires, gen_p3 asserts PASS')
    require(all(r.get('xcheck_p') == 'PASS' for r in built if r['tier'] in ('ship', 'j5', 'j4')),
            'CARRIERS: xcheck_p PASS for every shipped/j5/j4 build')
    require(all(r['status'] == 'built' or r['status'].startswith('not-run') for r in res),
            'CARRIERS: every record built or not run (no build failures)')
    ctl = d['control_shipped_frozen_receivers']
    ship = [r for r in res if r['tier'] == 'ship']
    require(len(ship) == 1 and ship[0]['P'] == sorted(census['shipped']['P']) and ship[0]['R'] == 439 and
            ship[0]['x'] == 10 and ship[0]['dead_duals'] == [87] and (ctl['R'], ctl['extra_carriers'],
                                                                      ctl['junk_wires']) == (439, 10, 0),
            'CARRIERS control: shipped P (searched and frozen receivers) R = 439, x = 10')

    # ---- (i) eleven stages, every built j >= 4 set at its own R(P)
    at439 = {tuple(e['P']): e for e in enum}
    hi = sorted((r for r in built if r['tier'] in ('j5', 'j4')), key=lambda z: (-z['j'], z['P']))
    require(len(hi) == 82 and {tuple(r['P']) for r in hi} == set(at439), 'own_R: all 82 j >= 4 sets built')
    e5 = hi[0]
    ctl439 = PR.price(e5['dead_duals'], 5, 11, readers=e5['P'], R=439, helper_model=HM)
    require(ctl439['c_exact'] == at439[tuple(e5['P'])]['c_exact'],
            "own_R control: helper_model='average-helper' at R = 439 reproduces the default pricing")
    rows11 = []
    for r in hi:
        x = PR.price(r['dead_duals'], r['j'], 11, readers=r['P'], R=r['R'], helper_model=HM)
        c = Q(x['c_exact'])
        rows11.append(dict(P=r['P'], j=r['j'], R=r['R'], dead=r['dead_duals'], hostable=x['hostable'],
                           c_exact=x['c_exact'], c_decimal=x['c_decimal'], gain_vs_selected_pct=x['gain_vs_selected_pct'],
                           ge_P104=x['hostable'] and c >= b104, ge_P104_rebased=x['hostable'] and c >= t_reb,
                           gain_at_R439_pct=at439[tuple(r['P'])]['gain_vs_selected_pct']))
    cs = [Q(z['c_exact']) for z in rows11]
    best = rows11[cs.index(max(cs))]
    worst = rows11[cs.index(min(cs))]
    eleven = dict(
        model="price.price(dead_duals, j, 11, readers=P, R=R(P), helper_model='average-helper') (transplant-swap, "
              "cost6 = j); the average-helper shift is a PREMISE",
        priced=len(rows11), hostable=sum(z['hostable'] for z in rows11),
        ge_P104=sum(z['ge_P104'] for z in rows11), ge_P104_rebased=sum(z['ge_P104_rebased'] for z in rows11),
        gain_max_pct=best['gain_vs_selected_pct'], gain_min_pct=worst['gain_vs_selected_pct'],
        R_min=min(z['R'] for z in rows11), R_max=max(z['R'] for z in rows11),
        best=best, worst=dict(P=worst['P'], j=worst['j'], R=worst['R'],
                              gain_vs_selected_pct=worst['gain_vs_selected_pct']),
        control_R439=dict(P=e5['P'], c_exact=ctl439['c_exact'], equals_default_pricing=True),
        sets=rows11)
    print(f"own_R L=11: {eleven['hostable']}/{len(rows11)} hostable, >= P104 {eleven['ge_P104']}, >= P104_rebased "
          f"{eleven['ge_P104_rebased']}, gain {eleven['gain_min_pct']}% .. {eleven['gain_max_pct']}% (best R = "
          f"{best['R']}, P = {best['P']})")

    # ---- (ii) nine stages, no-bank wall R(P) <= 4v for the built j = 2/3 sets
    t9 = PR.template(9)
    nine = {}
    for t in ('j3', 'j2'):
        j = tier_j[t]
        rs = [r for r in res if r['tier'] == t]
        bt = [r for r in rs if r['status'] == 'built']
        wall = t9['wall_ratio'] * (111 - j)
        mn = min(bt, key=lambda r: (r['R'], r['P']))
        x = PR.price(mn['dead_duals'], j, 9, readers=mn['P'], R=mn['R'], helper_model=HM)
        require(x['hostable'] == (mn['R'] <= wall), f'own_R {t}: pricer wall verdict = R(P) <= 4v')
        drop = max(min(r['screen']['default_R'] or 10 ** 9, r['screen']['all3_R'] or 10 ** 9) - r['R'] for r in bt)
        nine[t] = dict(domain=len(rs), built=len(bt), not_run=len(rs) - len(bt), coverage=f'{len(bt)}/{len(rs)}',
                       wall=f'R(P) <= 4v = {PR.qstr(wall)} (v = {111 - j})', wall_R_max=int(wall),
                       wall_passing=sum(r['R'] <= wall for r in bt), min_R=mn['R'], min_R_P=mn['P'],
                       min_R_dead=mn['dead_duals'],
                       phase1_R_min_all_screened=d['coverage'][t]['screen_R_min'],
                       max_sweep_drop_from_phase1_R=drop,
                       note='not-run sets were only screened (phase-1 R = best of the default / all-3 receivers, an '
                            'upper bound on their R); the built sets\' one-sweep search lowered phase-1 R by at most '
                            'max_sweep_drop_from_phase1_R',
                       min_R_banked_price_for_reference=dict(
                           L=9, R=mn['R'], hostable=x['hostable'], c_decimal=x['c_decimal'],
                           gain_vs_selected_pct=x['gain_vs_selected_pct'], pricing_mode=x['pricing_mode'],
                           note='fails the no-bank wall; banked price shown for reference only'))
        print(f"own_R L=9 {t}: wall-passing {nine[t]['wall_passing']}/{len(bt)} built ({nine[t]['coverage']} of the "
              f"domain), min R {mn['R']} vs wall {int(wall)}")

    # ---- (iii) sensitivity: helpers the best j >= 4 set would have to shed
    scan, need = [], {'P104': None, 'P104_rebased': None}
    for Rp in range(best['R'], 428, -1):
        x = PR.price(best['dead'], best['j'], 11, readers=best['P'], R=Rp, helper_model=HM)
        c = Q(x['c_exact'])
        scan.append(dict(R=Rp, hostable=x['hostable'], c_exact=x['c_exact'], c_decimal=x['c_decimal'],
                         gain_vs_selected_pct=x['gain_vs_selected_pct']))
        for k, th in (('P104', b104), ('P104_rebased', t_reb)):
            if need[k] is None and x['hostable'] and c >= th:
                need[k] = Rp
        if None not in need.values():
            break
    sens = dict(
        P=best['P'], j=best['j'], R_P=best['R'],
        method="scan R' = R(P), R(P) - 1, ..., 429 (= 420 + 9: no extra carriers or junk wires) with the same "
               "average-helper premise; for each threshold report the first (largest) R' whose hostable c reaches "
               "it; stop once both are reached",
        c_increases_as_R_decreases=all(Q(a['c_exact']) < Q(b['c_exact']) for a, b in zip(scan, scan[1:])),
        thresholds={k: dict(largest_R_reaching=v, fewer_helpers_than_R_P=None if v is None else best['R'] - v)
                    for k, v in need.items()},
        scan=scan)
    print(f"own_R sensitivity (best j>=4 set, R(P) = {best['R']}): P104 at R' = {need['P104']}, "
          f"P104_rebased at R' = {need['P104_rebased']}")
    section = dict(
        source=CARRIERS, source_sha256=cr_sha,
        source_scope=d['claim_scope'], source_coverage=d['coverage'],
        helper_model_premise="helper_model='average-helper': (R(P) - 439) copies of the AVERAGE PR589 helper climb "
                             "pattern are added to (or, for R(P) < 439, removed from) the transplanted local profile; a "
                             "hypothesis, not a replay of the built words' helper climbs",
        eleven_stages=eleven, nine_stages=nine, sensitivity_best_j_ge_4=sens)
    return section, cr_sha


# --------------------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--check', action='store_true', help='compare with SCREEN.json byte for byte instead of writing')
    args = ap.parse_args(argv)
    require(__debug__, 'run without -O: the pinned engines signal rejection with assert')

    # ------------------------------------------------ 1. subchecks: census.py --check, price.py, independent_census.py
    CEN = load('bit_stage_census', 'census.py')
    code, last = run_captured(CEN.main, ['--check'])
    require(code in (0, None) and last == EXPECT_CENSUS, f'census.py --check: exit {code}, last line {last!r}')
    print('census.py --check: ' + last)
    PR = load('bit_stage_price', 'price.py')
    try:
        code, last = run_captured(PR.main, [])
    except AssertionError as exc:
        code, last = 1, f'FAIL_BIT_STAGE_PRICER {exc}'
    require(code in (0, None) and last == EXPECT_PRICE, f'price.py: exit {code}, last line {last!r}')
    print('price.py: ' + last)
    proc = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'independent_census.py')], cwd=ROOT,
                          capture_output=True, text=True)
    last = (proc.stdout.strip().splitlines() or [''])[-1]
    require(proc.returncode == 0 and last == EXPECT_INDEP,
            f'independent_census.py: exit {proc.returncode}, last line {last!r}')
    print('independent_census.py: ' + last)
    census = json.loads((HERE / 'CENSUS.json').read_bytes())

    # ------------------------------------------------ selected record and thresholds
    sel = json.loads((ROOT / 'certificates/selected-result.json').read_bytes())
    require(sel['certificate'] == SELECTED_CERT, f'selected certificate is {SELECTED_CERT}')
    asm_path = ROOT / sel['certificate']
    require(sha(asm_path) == sel['certificate_sha256'], 'selected certificate matches its recorded SHA-256')
    asm = pinned_json(SELECTED_CERT)
    c0 = PR.C_PR589_9
    require(Q(asm['bit_lower']) == c0 and asm['binding'] == 'complex',
            'selected assembly: bit_lower = PR589 nine-stage c, complex side binds')
    b_now = Q(asm['complex_lower'])
    require(b_now < c0, 'selected assembly: complex_lower < bit_lower')
    res1084 = pinned_json('research/bit-orthogonal-pair-decoders/RESULTS.json')['pricing']
    src1084 = pinned_json('research/bit-orthogonal-pair-decoders/SOURCES.json')['selected_record']
    b104 = Q(res1084['p104_complex_b'])
    require(Q(res1084['pr589_c']) == c0, 'PR1084 priced against the same PR589 bit c')
    p104_pct = 100 * (b104 / c0 - 1)
    require(PR.dec(p104_pct, 18) == res1084['p104_required_bit_c_above_bit_percent'][:20],
            'P104 threshold percent = PR1084 record')
    # P104 re-based by a transfer premise: b_942 from PR1084's recorded strings, exact Fractions
    b942 = b104 / (1 + Q(res1084['p104_b_change_percent']) / 100)
    require(src1084['certificate'] == PR942_CERT and PINS[PR942_CERT] == src1084['certificate_sha256'],
            'PR1084 selected record = pinned frontier942 assembly')
    c942 = Q(pinned_json(PR942_CERT)['complex_lower'])
    require(abs(b942 - c942) < c942 * Q(1, 10 ** 70),
            'b_942 = p104_complex_b / (1 + p104_b_change_percent/100) matches the frontier942 complex_lower to 1e-70 '
            '(the percent string is a 75-digit decimal)')
    t_reb = b_now * b104 / b942
    reb_pct = 100 * (t_reb / c0 - 1)
    require(PR.dec(t_reb, 18) == '0.001767798399743162', 'P104_rebased = 0.001767798399743162...')
    thresholds = dict(
        P104=dict(c_exact=PR.qstr(b104), c_decimal=PR.dec(b104), pct_over_selected=PR.dec(p104_pct, 6),
                  source='PR1084 RESULTS.json pricing.p104_complex_b (verify.py section H): with bit c >= (1-10^-24) '
                         'b_P104 the PR968 P104 complex budget is no longer capped by the bit side (uncapped kappa '
                         + res1084['p104_uncapped_kappa'] + ')',
                  caveat='computed by PR1084 against the then-selected ' + src1084['certificate'] + ' complex profile '
                         '(kappa ' + src1084['kappa'] + '); not the current ' + sel['certificate'] + ' (kappa ' +
                         sel['decimal'] + '); see P104_rebased for a transfer-premise re-basing'),
        P104_rebased=dict(c_exact=PR.qstr(t_reb), c_decimal=PR.dec(t_reb), pct_over_selected=PR.dec(reb_pct, 6),
                          formula='b_now * p104_complex_b / b_942, b_942 = p104_complex_b / (1 + '
                                  'p104_b_change_percent/100) (PR1084 RESULTS.json pricing, exact Fractions of the '
                                  'recorded strings), b_now = complex_lower of ' + SELECTED_CERT,
                          b_942_exact=PR.qstr(b942), b_now_exact=PR.qstr(b_now), b_now_decimal=PR.dec(b_now),
                          p104_b_change_percent=res1084['p104_b_change_percent'],
                          premise='TRANSFER PREMISE: the same relative P104 complex gain (+' +
                                  PR.dec(Q(res1084['p104_b_change_percent']), 6) + '%) applied to the current selected '
                                  'complex b; PR968/P104 was not re-run against the current complex profile'))
    headroom = dict(bit_over_complex_exact=PR.qstr(c0 / b_now), bit_over_complex_decimal=PR.dec(c0 / b_now),
                    bit_above_complex_pct=PR.dec(100 * (c0 / b_now - 1), 6),
                    note='current selected record: bit_lower / complex_lower (exact); the complex side binds')

    def judge(r):
        c = Q(r['c_exact'])
        return dict(ge_P104=c >= b104, ge_P104_rebased=c >= t_reb,
                    margin_vs_P104_pct_points=PR.dec(100 * (c - b104) / c0, 6),
                    margin_vs_P104_rebased_pct_points=PR.dec(100 * (c - t_reb) / c0, 6))

    rows = []

    def row(rid, outcome, r, n_sets=None, **extra):
        keep = ('L', 'v', 'R', 'cst', 'j', 'cost6', 'hostable', 'c_exact', 'c_decimal', 'gain_vs_selected_pct',
                'variant', 'pricing_mode', 'dead_lines_geom', 'readers_geom', 'W', 'm', 'T')
        d = {k: r[k] for k in keep if k in r}
        d.update(id=rid, outcome=outcome, admissible_sets_with_this_outcome=n_sets, **judge(r), **extra)
        rows.append(d)
        flag = '' if r['hostable'] else ' [fails the no-bank wall at R=439; banked price shown for reference]'
        print(f"{rid:34s} L={r['L']:2d} j={r['j']} v={r['v']} cst={r['cst']} {r['variant']:15s} "
              f"c={r['c_decimal']} {r['gain_vs_selected_pct']:>10s}% P104:{'Y' if d['ge_P104'] else 'n'} "
              f"rebased:{'Y' if d['ge_P104_rebased'] else 'n'}{flag}")
        return d

    jdist = {int(k): n for k, n in census['j_distribution']['admissible_EZA'].items()}
    JS = sorted(jdist)
    require(JS == list(range(6)) and census['j_max']['admissible_EZA'] == 5, 'census attains j = 0..5')
    shipped = census['shipped']
    S = sorted(shipped['P'])
    require(shipped['dual_root']['b'] == 87 and shipped['j'] == 1, 'shipped P: one dual root, line 87')

    # ------------------------------------------------ 2a. shipped reader set (plain transplant = the PR589 word itself)
    for L in (9, 11):
        r = PR.price([], 0, L)
        row(f'P111-shipped@{L}', 'shipped P, nothing extra punctured (j = 0)', r, n_sets=None)
    require(Q(rows[0]['c_exact']) == c0, 'P111@9 = selected bit c')
    for L in (9, 11):
        row(f'P110-shipped@{L}', 'shipped P, dual root 87 punctured (j = 1)', PR.price([87], 1, L))
    # ------------------------------------------------ 2b. every attained j, uniform model
    for L in (9, 11):
        for j in JS:
            row(f'uniform-j{j}@{L}', f'any admissible P with j = {j} (average line pattern)', PR.price_uniform(j, j, L),
                n_sets=jdist[j])
    # ------------------------------------------------ 2c. the j = 5 reader sets with their actual dead duals
    G = CEN.gram_from_lines()
    ROW = CEN.b0_rows(G)
    ROWIDX = {w: a for a, w in enumerate(ROW)}
    best = census['best_examples']
    require(len(best) == 5 == census['j_max']['number_of_admissible_P_at_jmax'] and all(e['j'] == 5 for e in best),
            'the five best examples are exactly the five j = 5 sets')
    for n, e in enumerate(best, 1):
        P, dead = e['P'], e['dead_duals']
        rec = CEN.analyse(P, G, ROW, ROWIDX)
        require(rec['dead'] == dead and rec['j'] == 5, f'example {n}: dead duals re-derived')
        for L in (9, 11):
            row(f'ex{n}-j5-swap@{L}', f'P={P} dead={dead}', PR.price(dead, 5, L, readers=P), n_sets=1)
            if not set(dead) & set(S):
                row(f'ex{n}-j5-plain@{L}', f'P={P} dead={dead} (plain transplant: PR589 lines, shipped P kept)',
                    PR.price(dead, 5, L), n_sets=1)
        if e['dead_in_0_7']:
            keep = [b for b in dead if b >= 8]
            rec2 = dict(rec, dead=keep)
            ext = CEN.exact_extension(P, rec2, ROW)
            require(ext['identity'] and ext['v'] == 111 - len(keep) and sorted(ext['costs']) ==
                    sorted([6] * len(keep) + [7] * (9 - len(keep))),
                    f'example {n} restricted to dead duals outside 0..7: decoder identity, costs {sorted(ext["costs"])}')
            for L in (9, 11):
                row(f'ex{n}-j{len(keep)}-ruleZ-swap@{L}',
                    f'P={P} dead={keep} (dead dual {e["dead_in_0_7"]} kept live, rule Z)',
                    PR.price(keep, len(keep), L, readers=P), n_sets=1,
                    restricted_extension=dict(v=ext['v'], cst=ext['cst'], costs=ext['costs']))
    # ------------------------------------------------ 2d. envelopes for every hostable (j, L)
    t9 = PR.template(9)
    hostable9 = [j for j in JS if 439 <= t9['wall_ratio'] * (111 - j)]
    require(hostable9 == [0, 1], 'nine-stage wall R <= 4v at R = 439: hostable exactly for j <= 1')
    t11 = PR.template(11)
    require(all(439 <= t11['wall_ratio'] * (111 - j) for j in JS), 'eleven-stage wall 11R <= 64v holds for j <= 5')
    env = {}
    for L, js in ((9, hostable9), (11, JS)):
        for j in js:
            r = envelope(PR, L, j)
            env[L, j] = row(f'envelope-j{j}@{L}', f'upper bound over every reader set with j = {j}', r,
                            n_sets=jdist[j], envelope_lines_removed=r['envelope_lines_removed'],
                            envelope_positive_excess_patterns=r['envelope_positive_excess_patterns'])
    # ------------------------------------------------ 2e. all 82 admissible sets with j >= 4 at eleven stages
    high = census['admissible_P_with_j_at_least_4']
    require(len(high) == jdist[4] + jdist[5] == 82, '82 admissible sets with j >= 4')
    enum = []
    for h in high:
        rec = CEN.analyse(h['P'], G, ROW, ROWIDX)
        require(rec['dead'] == h['dead_duals'] and rec['j'] == h['j'], 'high-j set re-derived')
        r = PR.price(h['dead_duals'], h['j'], 11, readers=h['P'])
        require(r['hostable'], 'eleven-stage row hostable')
        jd = judge(r)
        enum.append(dict(P=h['P'], dead=h['dead_duals'], j=h['j'], j_restricted=h['j_restricted'],
                         c_exact=r['c_exact'], gain_vs_selected_pct=r['gain_vs_selected_pct'],
                         ge_P104=jd['ge_P104'], ge_P104_rebased=jd['ge_P104_rebased']))
    summ = {}
    for j in (4, 5):
        g = [Q(x['c_exact']) for x in enum if x['j'] == j]
        summ[str(j)] = dict(sets=len(g), c_min=PR.qstr(min(g)), c_max=PR.qstr(max(g)),
                            gain_min_pct=PR.dec(100 * (min(g) / c0 - 1), 6), gain_max_pct=PR.dec(100 * (max(g) / c0 - 1), 6),
                            ge_P104=sum(1 for c in g if c >= b104), ge_P104_rebased=sum(1 for c in g if c >= t_reb),
                            envelope_c=env[11, j]['c_exact'], all_below_envelope=all(c <= Q(env[11, j]['c_exact']) +
                                                                                    PR.GRID for c in g))
        require(summ[str(j)]['all_below_envelope'], f'j = {j}: every enumerated set lies below its envelope')
        print(f"enumerated j={j} @11: {len(g)} sets, gain {summ[str(j)]['gain_min_pct']}% .. "
              f"{summ[str(j)]['gain_max_pct']}%, >= P104: {summ[str(j)]['ge_P104']}, >= P104_rebased: "
              f"{summ[str(j)]['ge_P104_rebased']}  [R = 439]")

    # ------------------------------------------------ 3. comparison at R = 439 (premise)
    by = {r['id']: r for r in rows}
    nine_env_max = max(Q(env[9, j]['c_exact']) for j in hostable9)
    nine_crosses = nine_env_max >= b104
    nine_crosses_reb = nine_env_max >= t_reb
    require(not nine_crosses and not nine_crosses_reb, 'nine stages: no hostable outcome reaches either threshold')
    low11 = [j for j in JS if j <= 3]
    require(all(not env[11, j]['ge_P104'] for j in low11), 'eleven stages: j <= 3 envelopes below P104')
    j5 = summ['5']
    j4 = summ['4']
    cmp439 = dict(
        premise='R = 439 (the PR589/PR555 word\'s helper count) for EVERY reader set.  This premise is refuted for the '
                'alternative reader sets by CARRIERS.json.gz (real gen_p3 builds: every built non-shipped set has '
                'R(P) >= 446); see own_R for the prices at each set\'s own R(P)',
        nine_stages=dict(
            no_bank_wall_passing_outcomes='j <= 1 only (R = 439 <= 4v needs v >= 110)',
            best_hostable=dict(id='P110-shipped@9', c_exact=by['P110-shipped@9']['c_exact'],
                               gain_pct=by['P110-shipped@9']['gain_vs_selected_pct']),
            envelope_max_gain_pct=PR.dec(100 * (nine_env_max / c0 - 1), 6),
            reaches_P104=nine_crosses, reaches_P104_rebased=nine_crosses_reb,
            note='j >= 2 rows fail the no-bank wall R <= 4v; their banked price (IF HOSTED IN BANKS, not PR589 '
                 'hosting) is shown for reference and not counted as reaching any threshold'),
        eleven_stages=dict(
            all_rows_hostable=all(r['hostable'] for r in rows if r['L'] == 11),
            j5=j5, j4=j4,
            rule_Z_restrictions={r['id']: dict(gain_pct=r['gain_vs_selected_pct'], ge_P104=r['ge_P104'],
                                               ge_P104_rebased=r['ge_P104_rebased'])
                                 for r in rows if 'ruleZ' in r['id'] and r['L'] == 11},
            j_le_3_envelope_max_gain_pct=PR.dec(max(100 * (Q(env[11, j]['c_exact']) / c0 - 1) for j in low11), 6),
            reaches_P104='j = 5: %d/5 sets; j = 4: %d/77 sets; j <= 3: none (envelope)' % (j5['ge_P104'], j4['ge_P104']),
            reaches_P104_rebased='%d sets' % (j5['ge_P104_rebased'] + j4['ge_P104_rebased']),
            note='eleven-stage gains are measured against the selected NINE-stage c; whether the selected outer assembly '
                 'accepts an eleven-stage bit supplier is not checked (PR589 itself at eleven stages is -1.30%)'),
        summary=(f"At R = 439 for every reader set (premise), within the frozen PR555 L3 family (j <= 5): at nine "
                 f"stages the j >= 2 rows fail the no-bank wall (banked price shown for reference) and no wall-passing "
                 f"outcome reaches b_P104 (+{PR.dec(p104_pct, 4)}%) (best "
                 f"+{by['P110-shipped@9']['gain_vs_selected_pct']}%, shipped P110; envelope "
                 f"+{PR.dec(100 * (nine_env_max / c0 - 1), 6)}%). At eleven stages {j5['ge_P104']} of 5 j = 5 sets "
                 f"clear b_P104 (+{j5['gain_min_pct']}% .. +{j5['gain_max_pct']}%), {j5['ge_P104_rebased']} reach "
                 f"P104_rebased (+{PR.dec(reb_pct, 4)}%, transfer premise) (j = 5 envelope "
                 f"+{env[11, 5]['gain_vs_selected_pct']}%); {j4['ge_P104']} of 77 j = 4 sets clear b_P104 (max "
                 f"+{j4['gain_max_pct']}%)."))

    # ------------------------------------------------ 4. own R(P) from real gen_p3 builds
    own, cr_sha = own_R(PR, CEN, census, enum, b104, t_reb)
    o11, o9, sens = own['eleven_stages'], own['nine_stages'], own['sensitivity_best_j_ge_4']

    premises = dict(
        exact=['census: eligibility, admissibility, j distribution, dead duals and decoder identities/pairing ranks '
               '(census.py, exact F2/rational arithmetic on pinned inputs; re-derived independently by '
               'independent_census.py)',
               'P111 at 9 stages = selected bit c and P111 at 11 stages = PR589 tune/EXPECTED.json (exact replay)',
               'every c is a certified 10^-24 lower endpoint of the pinned moment engine for the stated profile',
               'hosting walls R <= 4v (L = 9) and 11R <= 64v (L = 11) and the window max-flow (slot model)',
               'the P104 threshold b_P104 is PR1084\'s exact recorded number (pinned RESULTS.json)',
               'own_R: R(P) of each built record is the helper count of a real gen_p3.build (frozen plan, thirds seed '
               '552, all internal asserts and decoder rows; xcheck_p replay for the shipped, j = 5 and j = 4 sets) '
               'recorded in CARRIERS.json.gz'],
        model=['no word is built here: the local profile of a different puncture is a PROXY built from the PR589 word '
               '(uniform: average line pattern; transplant: PR589 per-line climbs; transplant-swap: PR589 climbs for '
               'lines live in PR589 plus the average pattern for shipped punctured lines that become live)',
               'comparison_at_R439: helpers fixed at R = 439 for every reader set; refuted for alternative sets by '
               'CARRIERS.json.gz (own_R)',
               'own_R: helper_model=\'average-helper\': a set with R(P) helpers adds (R(P) - 439) copies of the AVERAGE '
               'PR589 helper climb pattern; the built words\' own helper climbs are not priced (a hypothesis)',
               'own_R: R(P) comes from a bounded receiver search (an upper bound on gen_p3\'s minimum over receivers, '
               'not proven minimal); j = 2/3 coverage is partial (time cap)',
               'own_R: the gen_p3 words keep the dead root duals LIVE; the helper count of a word that also punctures '
               'them (cost-6 COPY realisation) is not computed',
               'each live root dual term costs 6 via the asymmetric rank-6 COPY span b-perp -> span a-perp (PR620 open)',
               'hosting is the slot model with PR442 windows (no per-call owner map); eleven stages use PR493/PR545 '
               'K = 5, T = 8, m = 78',
               'nine-stage rows failing the no-bank wall are priced in width-64 banks for reference only (PR589 uses '
               'none)',
               'eleven-stage acceptance by the selected outer assembly and the H1-H5 interface are not checked',
               'b_P104 was computed against the frontier942 complex profile; P104_rebased is a transfer premise (same '
               'relative P104 complex gain applied to the current selected complex b)',
               'dead duals in lines 0..7: priced both punctured (j) and kept live (rule Z, j_restricted)'],
        envelope='linearity of the moment in the profile counts at fixed (L, v); ranking re-checked by interval '
                 'arithmetic at c_env and c_env + 10^-24; bounds uniform, transplant and transplant-swap (R = 439)')

    def fsha(rel):
        return sha(ROOT / rel)
    out = dict(
        package='research/bit-orthogonal-pair-stage-screen', script='screen.py',
        claim_scope='pricing screen of the census outcomes (at R = 439 and at each built set\'s own gen_p3 R(P)); no '
                    'word built here, no hosting map, no kappa',
        inputs={rel: fsha(rel) for rel in sorted([
            'research/bit-orthogonal-pair-stage-screen/census.py', 'research/bit-orthogonal-pair-stage-screen/price.py',
            'research/bit-orthogonal-pair-stage-screen/independent_census.py',
            'research/bit-orthogonal-pair-stage-screen/CENSUS.json', CARRIERS, 'certificates/selected-result.json',
            sel['certificate'], *PINS])},
        subchecks=dict(census=EXPECT_CENSUS, price=EXPECT_PRICE, independent_census=EXPECT_INDEP),
        selected=dict(kappa=sel['decimal'], certificate=sel['certificate'], binding=asm['binding'],
                      bit_c_exact=PR.qstr(c0), bit_c_decimal=PR.dec(c0), complex_b_exact=PR.qstr(b_now),
                      complex_b_decimal=PR.dec(b_now), headroom=headroom),
        thresholds=thresholds,
        census_summary=dict(j_distribution=census['j_distribution'], j_max=census['j_max'],
                            counts=census['counts']),
        rows=rows,
        eleven_stage_enumeration_j_ge_4=dict(model='transplant-swap, cost6 = j, R = 439 (premise)', summary=summ,
                                             sets=enum),
        comparison_at_R439=cmp439, own_R=own, premises=premises, checks=list(dict.fromkeys(CHECKS)))
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    path = HERE / 'SCREEN.json'
    if args.check:
        require(path.exists() and path.read_text() == text, 'SCREEN.json reproduces byte for byte')
    else:
        path.write_text(text)
        print('wrote ' + str(path))

    def need(k):
        x = sens['thresholds'][k]
        return (f"R'<={x['largest_R_reaching']}(-{x['fewer_helpers_than_R_P']})" if x['largest_R_reaching'] is not None
                else "none>=429")
    def rel9(t):
        return f"min R {o9[t]['min_R']} {'>' if o9[t]['min_R'] > o9[t]['wall_R_max'] else '<='} {o9[t]['wall_R_max']}"
    nb = sum(o9[t]['built'] for t in ('j3', 'j2'))
    nw = sum(o9[t]['wall_passing'] for t in ('j3', 'j2'))
    print(f"PASS_BIT_ORTHOGONAL_PAIR_STAGE_SCREEN rows={len(rows)} enum11={len(enum)} "
          f"thresholds:P104=+{PR.dec(p104_pct, 4)}%,P104_rebased=+{PR.dec(reb_pct, 4)}%(transfer premise) "
          f"R439(premise): L9 wall-passing j<=1 best=+{by['P110-shipped@9']['gain_vs_selected_pct']}%,env_max=+"
          f"{cmp439['nine_stages']['envelope_max_gain_pct']}%,P104=no,rebased=no; "
          f"L11 j5=+{j5['gain_min_pct']}..+{j5['gain_max_pct']}% P104 {j5['ge_P104']}/5 rebased "
          f"{j5['ge_P104_rebased']}/5, j4 max +{j4['gain_max_pct']}% P104 {j4['ge_P104']}/77 rebased "
          f"{j4['ge_P104_rebased']}/77 | "
          f"own_R: L11 j>=4 {o11['hostable']}/{o11['priced']} hostable, >=P104 {o11['ge_P104']}/{o11['priced']}, "
          f">=rebased {o11['ge_P104_rebased']}/{o11['priced']}, best {o11['best']['gain_vs_selected_pct']}% at "
          f"R={o11['best']['R']} (j={o11['best']['j']}, R439 gain {o11['best']['gain_at_R439_pct']}%), worst "
          f"{o11['gain_min_pct']}%; L9 j2/j3 wall-passing {nw}/{nb} (j3 {o9['j3']['wall_passing']}/"
          f"{o9['j3']['built']} built of {o9['j3']['domain']}, {rel9('j3')}; j2 {o9['j2']['wall_passing']}/"
          f"{o9['j2']['built']} built of {o9['j2']['domain']}, {rel9('j2')}); "
          f"best-set sensitivity "
          f"P104 {need('P104')}, rebased {need('P104_rebased')} | CARRIERS sha256 {cr_sha[:12]} "
          f"checks={len(dict.fromkeys(CHECKS))}")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f'FAIL_BIT_ORTHOGONAL_PAIR_STAGE_SCREEN {exc}')
        sys.exit(1)
