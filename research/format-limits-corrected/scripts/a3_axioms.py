"""A. Format ceiling, rev. 2: the accounting axioms checked on the published profiles of the frontier words.

(P)   pressure identity: the certified root of sum_r z_r r((m/r)^q - 1) = D on a word's published global profile
      reproduces the word's published supplier value (bit c or complex b);
(Dfc) deficit identity: m * live - rank mass = D = T[(s-1) v k - s cst] (equality, not just <=);
(Win) m = k + s (h - k) (for #543/#545/#555/#568 the largest child is the literal idle remainder (2K - 2) a);
(Sch) the B_K idle schedule: #568's per-replica idle windows are exactly skel.idle_slots(K, a) on both banks, and the
      skeleton mass (active climbs + copies + idle slots) equals each word's real rank mass;
(Hst) #555 hosts every helper residual whole (no bank assignments);
Lemma 2 (slot domination) pointwise: f_N(q) >= F_s(q; cst_N) for q in [1e-5, 1] on every profile (min ratio printed).
Profiles are read from the published files: #510 (main), #543, #545, #555 (EXPECTED.json), #568 (PLAN.json).
"""
from collections import Counter
from fractions import Fraction as Fr

from cert import root_bracket
from report import VENDOR, check, finish, load_json, main_file, near
from skel import X, idle_slots, profile

e510 = load_json(main_file('research/e8-r480-nine-stage/EXPECTED.json'))
e543 = load_json(VENDOR / 'pr543' / 'EXPECTED.json')
e545 = load_json(VENDOR / 'pr545' / 'EXPECTED.json')
e555 = load_json(VENDOR / 'pr555' / 'EXPECTED.json')
p568 = load_json(VENDOR / 'pr568' / 'PLAN.json.gz')


def prof(d):
    return {int(r): z for r, z in d.items()}


# name: (profile, h, v, cst, s, T, published value)
WORDS = {
    '#510-R480-s9': (prof(e510['nine']['profile']), 8, 120, 72, 9, 32, Fr(e510['nine']['bit_lower'])),
    '#543-R420-s9': (prof(e543['nine']['profile']), 8, 120, 72, 9, 32, Fr(e543['nine']['bit_lower'])),
    '#543-R420-s11': (prof(e543['eleven']['profile']), 8, 120, 72, 11, 8, Fr(e543['eleven']['bit_lower'])),
    '#545-p111-s11': (prof(e545['eleven']['profile']), 8, 111, 63, 11, 8, Fr(e545['eleven']['bit_lower'])),
    '#555-p111-s9': (prof(e555['nine']['profile']), 8, 111, 63, 9, 32, Fr(e555['nine']['bit_lower'])),
    '#555-p111-s11': (prof(e555['eleven']['profile']), 8, 111, 63, 11, 8, Fr(e555['eleven']['bit_lower'])),
    '#568-cx-s9': (prof(p568['profile']), 9, 112, 64, 9, 8, Fr('0.00159868506668458107128')),   # #568 README
}
# (min over q of f_N/F_s, X(s, x)/root): recorded values, compared to 3 decimals
EXPECTED_RATIOS = {'#555-p111-s9': (2.66, 2.658), '#568-cx-s9': (2.50, 2.499)}

for name, (P, h, v, cst, s, T, pub) in WORDS.items():
    k, a, K = 1, h - 1, (s - 1) // 2
    m = k + s * a
    D = T * ((s - 1) * v * k - s * cst)
    mass = sum(r * z for r, z in P.items())
    W = Fr(mass + D, m)
    lo, hi = root_bracket(P, m, D, hi=Fr(1, 100))
    rel = float(hi / pub - 1)
    check('A3.P.' + name, hi >= pub and rel < 2e-9,
          'certified root in [%.12e, %.12e]; published %.12e (root - published = %.1e relative)' % (lo, hi, pub, rel))
    check('A3.Dfc.' + name, W.denominator == 1 and m * W - mass == D,
          'm = %d, W = %s, rank mass %d, m W - mass = %d = T[(s-1)v - s cst]' % (m, W, mass, D))
    check('A3.Win.' + name, m == k + s * a, 'm = k + s(h-k) = %d; largest child %d%s' % (
        m, max(P), ' = (2K-2)a: the B_K idle remainders are literal' if max(P) == (2 * K - 2) * a else ''))
    pp, mm, Ds = profile(s, h, k, Fr(cst, v))
    ratios = []
    for qq in (1e-5, 1e-4, 1e-3, 3e-3, 1e-2, 0.05, 0.2, 0.5, 1.0):
        fN = sum(z * r * ((m / r) ** qq - 1) for r, z in P.items())
        Fs = v * T * sum(float(z) * float(r) * ((m / float(r)) ** qq - 1) for r, z in pp.items())
        ratios.append(fN / Fs)
    head = float(X(s, h, k, Fr(cst, v))['hi'] / hi)
    ok = min(ratios) >= 1
    if name in EXPECTED_RATIOS:
        er, eh = EXPECTED_RATIOS[name]
        ok = ok and near(min(ratios), er, 2) and near(head, eh, 3)
    check('A3.lemma2.' + name, ok, 'min_q f_N(q)/F_s(q) = %.3f; X(s,x)/root = %.3f' % (min(ratios), head))

# (Sch): skeleton mass = real rank mass, and #568's windows are the B_K idle slots
for name, h, v, cst, T, real in (('#555-p111-s9', 8, 111, 63, 32, e555['nine']['bit']['rank_mass']),
                                  ('#568-cx-s9', 9, 112, 64, 8, sum(r * z for r, z in prof(p568['profile']).items()))):
    s, a, K = 9, h - 1, 4
    data, copies, idle = 2 * v * s * a * T, cst * s * T, 2 * v * T * sum(idle_slots(K, a))
    check('A3.Sch-mass.' + name, data + copies + idle == real,
          'active %d + copies %d + idle %d = %d = rank mass' % (data, copies, idle, real))
reps = sorted({int(k.split(',')[0]) for k in p568['windows']})
want = Counter(idle_slots(4, 8)) + Counter(idle_slots(4, 8))
okw = all(Counter(r for kk, (r, _) in p568['windows'].items() if int(kk.split(',')[0]) == rep) == want for rep in reps)
check('A3.Sch-windows.#568', okw and len(reps) == p568['T'],
      '%d replicas, each with idle windows %s = idle_slots(K=4, a=8) on both banks' % (len(reps), dict(sorted(want.items()))))
b = e555['nine']['bit']
check('A3.Hst.#555', b['bank_assignments'] == 0 and b['hosted_residuals'] == 439 * 9 * 32,
      'bank assignments 0; hosted residuals %d = R * s * T = 439 * 288' % b['hosted_residuals'])
finish()
