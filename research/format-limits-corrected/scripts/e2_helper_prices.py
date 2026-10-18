"""E2. What a complex helper costs, by class, on the word of PR #569 (DominikScholz).

Question: by how many percent does the pressure root b of PR #569's global word (published conservative
b = 1.60263181098e-3) improve when ONE helper register of a given class is deleted, in all 72 calls, and the hosting is
re-optimised?  The answer is the price of a helper of that class; the published word has 504 helpers per call.

Data (all derived here; nothing is copied from the original measurement except the checked constants of EXPECTED):
  * the two local words of PR #569 (data/vendor/pr569: width7_eight, fourcold_eight; PR #433's FULL-WORD format with the
    start_extra / target_levels extension keys that gk_word.py reads) and PR #569's per-call dispatch
    (data/prices/pr569-provider-calls.json: 63 calls use width7_eight, 9 use fourcold_eight);
  * the word helpers gk_word.py / gk_common.py and PR #523's ASYNC112 hosting windows, files of main.
Per local word, replaying the frame chains register by register gives (i) the paid climbs of every register, hence the
per-call local profile LOC, and (ii) the width of every helper, 9 minus the dimension of its entrance frame, hence the
per-call demand DEM of helper widths to be hosted.  For every non-centre helper the local mass (sum of its paid climbs)
equals its width, so a deleted helper takes its width out of the demand together with the same mass out of the local
profile and the total paid mass stays 520704 (D = 73 * 7168 - 520704 = 2560).

Model of a deletion (hypothetical removal, no dependent registers): helper h leaves every call (in a call of word type
nm its climbs leave LOC[nm] and its width leaves DEM[nm]); the hosting linear programme (e_hosting.py: the relaxation of
the whole-owner hosting model of PR #523's 112-port unit) is re-solved at q = the published b; the new paid profile is the
72 local profiles plus the LP's idle remainders and its b is the moment root b_float (W = 7168).  Price = percent change
of b per deleted helper.

Cells are (role, width in the width7_eight word); the role is told by index range (h < 224 factory scratch registers,
h < 392 face copies, else M copies: 14 blocks of 16 / 12 / 8).  k = 1 deletes the single helper of the cell whose local
fee is closest to the cell mean.  The recorded values are reproduced to the last printed digit (HiGHS through scipy
1.17; the dual simplex and the interior-point method returned the same idle remainders and b on the cells F9, P8, P7,
M5, M4 when tried once).

Claims: E2.inputs, E2.cells, E2.control (zero deletion), E2.k1.<cell> for the seven cells, E2.width-law, E2.table.
The eight LPs (control and seven cells) run in parallel in at most 6 processes.
"""
import multiprocessing as mp
import os
import sys
import time
from collections import Counter

os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
sys.dont_write_bytecode = True

from report import DATA, VENDOR, check, finish, load_json, main_file   # noqa: E402
import e_hosting as hosting                                            # noqa: E402

V = 112                    # data registers per side; helpers are registers 2 V + h
N_HELPERS = 504            # helpers per local word (h = 0..503)
N_FACTORY, N_FACE = 224, 392   # h < 224 factory scratch, h < 392 face copies, else M copies (14 blocks of 16 / 12 / 8)
M = hosting.M
CALLS = hosting.CALLS
Q_PICK = 1.6026e-3         # q at which the representative helper of a cell is chosen
PROVIDER_FILES = {'width7_eight': 'width7-eight-FULL-WORD.json.gz', 'fourcold_eight': 'fourcold-eight-FULL-WORD.json.gz'}
GK_DIR = 'research/direct-delivery504-global/vendor/gk/gk_word.py'
CELL_ORDER = ['F9', 'P9', 'P8', 'P7', 'M8', 'M5', 'M4']

# ---- expected values ---------------------------------------------------------------------------------------------
EXPECTED = {
    # per-call local profile (rank: number of paid climbs) of each local word, from the register-by-register replay
    'LOC': {'width7_eight': {1: 2352, 2: 592, 3: 328, 4: 192, 5: 56, 6: 56, 8: 8},
            'fourcold_eight': {1: 2320, 2: 432, 3: 456, 4: 192, 5: 56, 6: 56, 8: 8}},
    # per-call demand of helper widths (width: number of helpers)
    'DEM': {'width7_eight': {4: 8, 5: 48, 7: 32, 8: 128, 9: 288}, 'fourcold_eight': {4: 8, 5: 48, 8: 160, 9: 288}},
    'DISPATCH': {'width7_eight': 63, 'fourcold_eight': 9},
    # PR #569's published global profile, W = 7168, and its idle remainder (rank: count)
    'PUB': {1: 169056, 2: 41184, 3: 25968, 4: 13824, 5: 4032, 6: 4032, 7: 48, 8: 576, 48: 1808},
    'REM': {3: 1200, 7: 48, 48: 1808},
    'MASS': 520704, 'D': 2560,
    'B_PUBLISHED': 1.602631810982070e-3,     # conservative certified b of the published profile (PR #569)
    # zero-deletion LP: objective (to 1e-4), idle remainder, b_float printed 1.602631811e-3
    'CONTROL': {'obj': 78.05857, 'b': 1.602631811e-3},
    # cells: size (non-centre helpers), recorded k = 1 LP objective, b_float, and the price in percent b per helper
    # (3 decimals) ; 'share' = LP objective increase / local fee saved, in percent (1 decimal)
    'CELLS': {
        'F9': dict(size=216, obj=78.30161, b=0.0016048723869705752, pct=0.140, share=6.3),
        'P9': dict(size=64, obj=78.30161, b=0.0016047716270276408, pct=0.134, share=6.6),
        'P8': dict(size=72, obj=78.64326, b=0.0016043095787383996, pct=0.105, share=17.9),
        'P7': dict(size=32, obj=78.94317, b=0.001603832889308516, pct=0.075, share=31.5),
        'M8': dict(size=56, obj=78.64326, b=0.0016044102805557185, pct=0.111, share=17.0),
        'M5': dict(size=48, obj=79.39080, b=0.0016032504527875107, pct=0.039, share=57.4),
        'M4': dict(size=8, obj=78.96089, b=0.0016033092416224345, pct=0.042, share=45.4),
    },
    # offset share bands in percent by width (k = 1): w9 about 6, w8 about 18, w7 31-55, w5 57-65, w4 about 45
    'SHARE_BANDS': {9: (5.0, 7.5), 8: (16.0, 19.0), 7: (31.0, 55.0), 5: (57.0, 65.0), 4: (43.0, 47.0)},
}
TOL_OBJ = 1e-4             # LP objective
TOL_B_REL = 1e-9           # b against the recorded value (LP solutions agree to ~1e-14 across scipy 1.17-1.18)
TOL_TABLE_OBJ = 1e-6       # recorded table against recomputation
TOL_MASS = 1e-6            # rank mass of an LP-derived profile (floating sum of fractional remainders)
TOL_PRINTED = 6e-4         # a value printed with 3 decimals: half a unit of the last digit plus slack
TOL_SHARE = 0.06           # a share printed with 1 decimal
SHARE_ORDER = [9, 8, 7, 5]  # offset share increases as the width falls through 9, 8, 7, 5 (width 4 sits between 7 and 5)


# ---- word replay --------------------------------------------------------------------------------------------------
def load_gk():
    """import gk_word / gk_common of main and set them to the 112-port unit (V = 112, DATA = 7168)"""
    d = main_file(GK_DIR).parent
    sys.path.insert(0, str(d))
    import gk_word as g
    import gk_common as co
    g.V = co.V = V
    g.DATA = co.DATA = hosting.W_DATA
    return g


def per_register_climbs(word, g):
    """paid climbs of every register of a gk word: {register: [climb sizes in order]}.  A climb is a change of the
    register's frame; its size is the rank of the paid child.  This is gk_word.profile with per-register attribution
    (the centre registers also pay the descents through the served target levels)."""
    R = word['report']['R']
    n = 2 * V + R
    P = word['ports']
    cur = {}
    for r in range(n):
        if r < V:
            cur[r] = (P[r],)
        elif r >= 2 * V:
            cur[r] = g.basis(word['start_extra'][str(r)]) if str(r) in word.get('start_extra', {}) else ()
        else:
            cur[r] = ()
    paid = {r: [] for r in range(n)}

    def climb(r, F):
        F = g.basis(F)
        o = cur[r]
        assert g.basis(list(o) + list(F)) == F, ('frame violation', r, o, F)
        if o != F:
            paid[r].append(len(F) - len(o))
            cur[r] = F
    lev = {int(t): g.basis(E) for t, E in word.get('target_levels', {}).items()}
    for seq, part in ((word['A'], 'A'), (word['B'], 'B')):
        if part == 'B':
            for r, f in zip(word['centers'], word['center_frames']):
                assert cur[r] == g.basis(f), 'centre frame'
                served = sorted({lev.get(e[1] - V, ()) for e in word['cut'] if e[2] == r}, key=lambda E: -len(E))
                o = g.basis(f)
                for Lv in served:
                    if Lv != o:
                        paid[r].append(len(o) - len(Lv))
                        o = Lv
        for e in seq:
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
                climb(r, e[-1])
    for r in range(n):
        climb(r, g.FULL if (r < V or r >= 2 * V) else g.perp(P[r - V]))
    return paid


def replay(name, g):
    """paid climbs, local profile, helper widths and centres of one provider word"""
    word = load_json(VENDOR / 'pr569' / PROVIDER_FILES[name])
    assert word['report']['R'] == N_HELPERS
    paid = per_register_climbs(word, g)
    loc = Counter()
    for r, l in paid.items():
        for c in l:
            loc[c] += 1
    se = word.get('start_extra', {})
    width = [9 - len(se[str(2 * V + h)]) if str(2 * V + h) in se else 9 for h in range(N_HELPERS)]
    centres = {c - 2 * V for c in word['centers']}
    dem = dict(sorted(Counter(width).items()))
    return dict(paid=paid, loc=dict(sorted(loc.items())), width=width, dem=dem, centres=centres,
                profile_g=dict(sorted(g.profile(word).items())), widths_g=g.widths_of(word))


def role(h, centres):
    if h in centres:
        return 'C'
    return 'F' if h < N_FACTORY else ('P' if h < N_FACE else 'M')


def fee(climbs, q):
    """pressure fee of a list of paid climbs: sum r ((m / r)^q - 1)"""
    return sum(c * ((M / c) ** q - 1) for c in climbs)


def pick_representative(cell_helpers, w7):
    """the helper of the cell whose local fee (width7_eight word, q = Q_PICK) is closest to the cell mean"""
    fees = {h: fee(w7['paid'][2 * V + h], Q_PICK) for h in cell_helpers}
    mean = sum(fees.values()) / len(fees)
    return min(cell_helpers, key=lambda h: abs(fees[h] - mean))


# ---- scenarios ----------------------------------------------------------------------------------------------------
def deleted_models(words, prov, dele):
    """per-call local profiles and demands when helpers `dele` are deleted in all 72 calls (word type per call)"""
    out_l, out_d = [], []
    for t in range(CALLS):
        w = words[prov[t]]
        l = dict(w['loc'])
        d = dict(w['dem'])
        for h in dele:
            for c in w['paid'][2 * V + h]:
                l[c] -= 1
            d[w['width'][h]] -= 1
        assert all(z >= 0 for z in l.values()) and all(z >= 0 for z in d.values())
        out_l.append({r: z for r, z in l.items() if z})
        out_d.append({x: z for x, z in d.items() if z})
    return out_l, out_d


def local_fee_saved(words, prov, dele, q):
    tot = 0
    for t in range(CALLS):
        for h in dele:
            tot += fee(words[prov[t]]['paid'][2 * V + h], q)
    return tot


def rel(a, b):
    return abs(a / b - 1)


def main():
    t_start = time.time()
    ex = EXPECTED
    g = load_gk()

    # ---- E2.inputs --------------------------------------------------------------------------------------------
    pc = load_json(DATA / 'prices' / 'pr569-provider-calls.json')
    calls = pc['calls']
    assert [c[0] for c in calls] == list(range(CALLS))
    prov = [c[1] for c in calls]
    words = {nm: replay(nm, g) for nm in PROVIDER_FILES}
    disp = dict(Counter(prov))
    loc_ok = all(words[nm]['loc'] == ex['LOC'][nm] and words[nm]['profile_g'] == ex['LOC'][nm] for nm in words)
    dem = {nm: words[nm]['dem'] for nm in words}
    dem_ok = all(dem[nm] == ex['DEM'][nm] and words[nm]['widths_g'] == words[nm]['width'] for nm in words)
    ident_ok = all(sum(words[nm]['paid'][2 * V + h]) == words[nm]['width'][h]
                   for nm in words for h in range(N_HELPERS) if h not in words[nm]['centres'])
    comp = Counter()
    for nm in words:
        for r, z in words[nm]['loc'].items():
            comp[r] += z * disp[nm]
    for r, z in ex['REM'].items():
        comp[r] += z
    comp = dict(sorted(comp.items()))
    mass_pub = hosting.mass(comp)
    check('E2.inputs',
          disp == ex['DISPATCH'] and loc_ok and dem_ok and ident_ok and comp == ex['PUB']
          and mass_pub == ex['MASS'] and hosting.M * hosting.W_DATA - mass_pub == ex['D'],
          'dispatch %s; local profile width7_eight %s, fourcold_eight %s (replay = gk_word.profile); demand %s / %s; '
          'local mass = width for the 496 non-centre helpers of each word; 63 x width7_eight + 9 x fourcold_eight local '
          'profiles + idle remainder %s = published profile %s; mass %d, D %d'
          % (disp, words['width7_eight']['loc'], words['fourcold_eight']['loc'], dem['width7_eight'],
             dem['fourcold_eight'], ex['REM'], comp, mass_pub, hosting.M * hosting.W_DATA - mass_pub))

    # ---- E2.cells ---------------------------------------------------------------------------------------------
    w7 = words['width7_eight']
    cells = {}
    for h in range(N_HELPERS):
        cells.setdefault((role(h, w7['centres']), w7['width'][h]), []).append(h)
    specs = load_json(DATA / 'prices' / 'k1-specs.json')['cells']
    dele, sizes_ok, pick_ok = {}, True, True
    for c in CELL_ORDER:
        key = (specs[c]['role'], specs[c]['width'])
        members = cells[key]
        dele[c] = specs[c]['deleted_helpers']
        sizes_ok &= len(members) == ex['CELLS'][c]['size'] and len(dele[c]) == 1 and dele[c][0] in members
        pick_ok &= pick_representative(members, w7) == dele[c][0]
    check('E2.cells', sizes_ok and pick_ok and len(cells[('F', 9)]) == 216 and len(w7['centres']) == 8,
          'cell sizes %s (+ 8 centre accumulators, not priced); k = 1 helper per cell %s is the helper with the local '
          'fee closest to the cell mean'
          % ({c: ex['CELLS'][c]['size'] for c in CELL_ORDER}, {c: dele[c][0] for c in CELL_ORDER}))

    # ---- the eight LPs in parallel -------------------------------------------------------------------------
    jobs = []
    for name, dl in [('ctl', [])] + [(c, dele[c]) for c in CELL_ORDER]:
        out_l, out_d = deleted_models(words, prov, dl)
        jobs.append((name, out_l, out_d, ex['B_PUBLISHED']))
    nproc = min(6, len(jobs))
    t_lp = time.time()
    with mp.get_context('spawn').Pool(nproc) as pool:
        res = {r['name']: r for r in pool.imap_unordered(hosting.run_job, jobs)}
    wall_lp = time.time() - t_lp
    bad = [n for n, r in res.items() if r['status'] != 0]
    if bad:
        check('E2.control', False, 'LP failed for %s: %s' % (bad, [res[n]['status'] for n in bad]))
        finish()
        return

    # ---- E2.control ---------------------------------------------------------------------------------------------
    c0 = res['ctl']
    b0, obj0 = c0['b'], c0['obj']
    rem_ok = set(c0['rem']) == set(ex['REM']) and all(abs(c0['rem'][r] - z) < 1e-6 for r, z in ex['REM'].items())
    p_pub = {r: float(z) for r, z in ex['PUB'].items()}
    b_pub_profile = hosting.b_float(p_pub, hosting.W_DATA)
    ctl_ok = (abs(obj0 - ex['CONTROL']['obj']) < TOL_OBJ and rem_ok and rel(b0, ex['CONTROL']['b']) < 1e-9
              and rel(b0, ex['B_PUBLISHED']) < 1e-12 and rel(b_pub_profile, b0) < 1e-12 and abs(c0['mass'] - ex['MASS']) < TOL_MASS)
    check('E2.control', ctl_ok,
          'zero-deletion LP objective %.5f, idle remainder %s, b_float %.9e = published conservative b %.12e '
          '(relative difference %.1e); b_float of the published profile %.9e; (%.0f s)'
          % (obj0, {r: round(z, 6) for r, z in c0['rem'].items()}, b0, ex['B_PUBLISHED'], rel(b0, ex['B_PUBLISHED']),
             b_pub_profile, c0['secs']))

    # ---- E2.k1.<cell> -------------------------------------------------------------------------------------------
    shares, lfs = {}, {}
    for c in CELL_ORDER:
        r, e = res[c], ex['CELLS'][c]
        pct = 100 * (r['b'] / b0 - 1)
        lf = local_fee_saved(words, prov, dele[c], b0)
        lfs[c] = lf
        shares[c] = 100 * (r['obj'] - obj0) / lf
        ok = (abs(r['obj'] - e['obj']) < TOL_OBJ and rel(r['b'], e['b']) < TOL_B_REL and abs(pct - e['pct']) < TOL_PRINTED
              and abs(r['mass'] - ex['MASS']) < TOL_MASS)
        check('E2.k1.' + c, ok,
              'delete helper %d (cell of %d): %.4f%% b per helper (printed %.3f); LP objective %.5f (+%.5f); b %.12e '
              '(recorded %.12e, relative difference %.1e); (%.0f s)'
              % (dele[c][0], e['size'], pct, e['pct'], r['obj'], r['obj'] - obj0, r['b'], e['b'], rel(r['b'], e['b']),
                 r['secs']))

    # ---- E2.width-law -------------------------------------------------------------------------------------------
    width_of = {c: specs[c]['width'] for c in CELL_ORDER}
    dobj = {c: res[c]['obj'] - obj0 for c in CELL_ORDER}
    same = all(abs(dobj[a] - dobj[b]) < 1e-9 for a in CELL_ORDER for b in CELL_ORDER if width_of[a] == width_of[b])
    bands = all(ex['SHARE_BANDS'][width_of[c]][0] <= shares[c] <= ex['SHARE_BANDS'][width_of[c]][1]
                for c in CELL_ORDER)
    printed = all(abs(shares[c] - ex['CELLS'][c]['share']) < TOL_SHARE for c in CELL_ORDER)
    by_w = {}
    for c in CELL_ORDER:
        by_w.setdefault(width_of[c], []).append(shares[c])
    mono = all(max(by_w[SHARE_ORDER[i]]) < min(by_w[SHARE_ORDER[i + 1]]) for i in range(len(SHARE_ORDER) - 1))
    # price in fee units per percent of b: (local fee saved - LP objective increase) / (percent b)
    conv = {c: (lfs[c] - dobj[c]) / (100 * (res[c]['b'] / b0 - 1)) for c in CELL_ORDER}
    conv_ok = max(conv.values()) / min(conv.values()) < 1.02
    check('E2.width-law', same and bands and printed and mono and conv_ok,
          'hosting offset = LP objective increase / local fee saved at k = 1 (percent): '
          + ', '.join('%s (w%d) %.1f' % (c, width_of[c], shares[c]) for c in CELL_ORDER)
          + '; equal widths give an identical LP objective increase (%s); the share rises as the width falls through '
          '9, 8, 7, 5 with width 4 (45) between 7 and 5; fee saved less offset per percent b (one conversion constant '
          'for all cells, within 2%%): %.2f..%.2f'
          % (', '.join('w%d %.5f' % (w, dobj[next(c for c in CELL_ORDER if width_of[c] == w)]) for w in (9, 8)),
             min(conv.values()), max(conv.values())))

    # ---- E2.table -----------------------------------------------------------------------------------------------
    tab = load_json(DATA / 'prices' / 'helper-price-table.json')
    rows = {r['name']: r for r in tab['rows']}
    rc = tab['control']
    tab_ok = (abs(rc['lp_objective'] - obj0) < TOL_TABLE_OBJ and rel(rc['b'], b0) < TOL_B_REL
              and all(abs(rc['idle_remainder'][str(r)] - z) < 1e-6 for r, z in c0['rem'].items()))
    for c in CELL_ORDER:
        rw, r = rows[c + '_k1'], res[c]
        tab_ok &= (rw['status'] == tab['status_recomputed'] and rw['deleted_helpers'] == dele[c]
                   and abs(rw['lp_objective'] - r['obj']) < TOL_TABLE_OBJ and rel(rw['b'], r['b']) < TOL_B_REL
                   and abs(rw['mass'] - r['mass']) < TOL_MASS and set(map(int, rw['idle_remainder'])) == set(r['rem'])
                   and all(abs(rw['idle_remainder'][str(k)] - z) < 1e-6 for k, z in r['rem'].items()))
    tab_ok &= all(rw['status'] == (tab['status_recomputed'] if rw['name'] in {c + '_k1' for c in CELL_ORDER}
                                   else tab['status_recorded']) for rw in tab['rows'])
    tab_ok &= all(rel(100 * (rw['b'] / rc['b'] - 1) / rw['k'], rw['pct_b_per_helper']) < 1e-9 if rw['k'] else True
                  for rw in tab['rows'])
    check('E2.table', tab_ok,
          '%d recorded rows in data/prices/helper-price-table.json (all cells at k = 1, 8, 14, whole cell; mixed classes; '
          'sub-classes): the control and the seven k = 1 rows equal the recomputation, the other rows are marked '
          '"%s", every row\'s percent per helper is consistent with its b'
          % (len(tab['rows']), tab['status_recorded']))

    print('total %.1f s (hosting LPs %.1f s wall in %d processes; machine load %s)'
          % (time.time() - t_start, wall_lp, nproc, ' '.join('%.1f' % x for x in os.getloadavg())))
    finish()


if __name__ == '__main__':
    main()
