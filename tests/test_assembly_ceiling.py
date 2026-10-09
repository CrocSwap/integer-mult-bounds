"""Exact tests for the closed-form kappa ceiling and reduced feasibility check.

Apache-2.0; drafted with Claude Code (Anthropic Claude). Arithmetic only. Research files load
lazily: a moved or malformed file fails only the tests that use it, and the message names it.
"""
import ast
import contextlib
import functools
import importlib.util
import json
import os
import random
import sys
import unittest
from decimal import Decimal
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace

if not __debug__:
    raise RuntimeError('run without -O: the original reference uses bare asserts')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import assembly_ceiling as A
import structured_bulk_assembly as S

PREFIXES = ('original', 'balanced')
ORIGINAL_FILES = tuple('certificates/%s-network.json' % name for name in (
    'structured-bulk', 'copied-centers', 'partial-gauge', 'stopped-product',
    'three-stage-cover', 'paired-cube'))
BALANCED_FILES = (
    'certificates/joint-dual-kappa.json', 'certificates/skip-frame-kappa.json',
    'research/climbed-48/certificate.json', 'research/copied-fixed/certificate.json',
    'research/copied-fixed-reversed/certificate.json', 'research/copied-reversed/certificate.json',
    'research/enlarged-positive-frame-networks/runs/mapped-positive-negative-composition/certificate.json',
    'research/gaussian-parity-synthesis/references/pr46/research/copied-fixed/certificate.json',
    'research/matrix-exponent-synthesis/bridge/pr48/research/copied-fixed/certificate.json',
    'research/matrix-exponent-synthesis/candidate/arithmetic.json',
    'research/matrix-exponent-synthesis/candidate/pinned62-certificate.json',
    'research/matrix-exponent-synthesis/catalogue/inputs/community-pr46-certificate.json',
    'research/matrix-exponent-synthesis/catalogue/inputs/community-pr48-certificate.json',
    'research/matrix-exponent-synthesis/history/pr58/candidate/arithmetic.json',
    'research/matrix-exponent-synthesis/history/pr58/candidate/pinned58-certificate.json',
    'research/matrix-exponent-synthesis/history/pr60/candidate/arithmetic.json',
    'research/matrix-exponent-synthesis/history/pr60/candidate/pinned60-certificate.json',
    'research/pair-assembly/certificate.json', 'research/pair-assembly/frame/frame-certificate.json',
    'research/positive-skip/certificate.json', 'research/skip-clones/certificate.json',
    'research/skip-strips/certificate.json', 'research/skip-suffix/certificate.json',
    'research/split-skip/certificate.json',
)
FIXTURES = (tuple(('original', f) for f in ORIGINAL_FILES)
            + tuple(('balanced', f) for f in BALANCED_FILES))
BRIDGE_FILE = 'research/copied-fixed/certificate.json'
BALANCED_REFERENCE = 'research/copied-fixed/balanced_assembly.py'
TINY = Q(1, 10**30)


@contextlib.contextmanager
def fixture_file(relative):
    """Turn any loading failure into an AssertionError that names the research file."""
    try:
        yield ROOT/relative
    except Exception as error:
        raise AssertionError('%s: %s: %.200s' % (relative, type(error).__name__, error)) from error


@functools.lru_cache(maxsize=None)
def balanced_reference():
    # A unique module name; research/ never goes on sys.path (verify.py name collisions).
    with fixture_file(BALANCED_REFERENCE) as path:
        spec = importlib.util.spec_from_file_location('_assembly_ceiling_test_balanced_ref', path)
        module = importlib.util.module_from_spec(spec)
        saved, sys.dont_write_bytecode = sys.dont_write_bytecode, True
        try:
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = saved
        return module


@functools.lru_cache(maxsize=None)
def load_case(prefix, relative):
    """The certified point of one research file, read only when a test asks for it."""
    with fixture_file(relative) as path:
        with open(path) as handle:
            asm = json.load(handle)['assembly']
        balanced = prefix == 'balanced'
        h = 'h' if balanced else 'eta'
        params = {k: Q(asm['parameters'][k]) for k in
                  ('a_bit', 'a_complex', 'beta', h, 'kappa', 'q', 'c', 'epsilon')}
        constraints = {k: Q(v) for k, v in
                       asm['constraints' if balanced else 'strict_constraints'].items()}
        case = SimpleNamespace(
            asm=asm, params=params, constraints=constraints, a=params['a_bit'],
            b=params['a_complex'], beta=params['beta'], e=params[h], kappa=params['kappa'],
            gap=constraints['literal_scalar_guard'], degree_gap=constraints['row_product_gap'],
            minimum=Q(asm['minimum_margin']), absorption=Q(asm['absorption_gap']), bridge=None)
        if balanced:
            case.bridge, case.scoped_limit = asm['finite_bridge'], Q(asm['scoped_limit'])
            case.replay = balanced_reference().assembly(
                case.bridge, case.a, case.kappa, beta=case.beta, h=case.e, a_complex=case.b)
        return case


def default_gaps(prefix):
    if prefix == 'original':
        return Q(1), Q(1)
    bridge = load_case('balanced', BRIDGE_FILE)
    return bridge.gap, bridge.degree_gap


def replaced(p, **changes):
    return SimpleNamespace(**dict(vars(p), **changes))


def run(function, prefix, p):
    """A.check or A.feasible on a point-like object (a certified case or a base point)."""
    return function(p.a, p.b, p.kappa, p.beta, prefix=prefix, backoff=p.e,
                    literal_scalar_guard=p.gap, row_product_gap=p.degree_gap)


def derived(prefix, a, b, beta, e, kappa):
    """Quantities of the claim, from the module's own prefix formulas."""
    spec = A.PREFIXES[prefix]
    q = a*(1 - 2*e)
    c, eps, G = spec.c(q, e), spec.epsilon(q, e), spec.ceiling(q, e)
    return SimpleNamespace(a=a, b=b, beta=beta, e=e, kappa=kappa, q=q, c=c, eps=eps, G=G,
                           K=G - kappa, s=(1 - beta)*b - a, r=(G + 1 - eps)/2)


# Explicit expressions (over derived()) for every coverage row of status 'identity'.
IDENTITIES = {
    'original': {
        'complex_above_bit': lambda P: P.s + P.beta*P.b,
        'q_below_leaf': lambda P: P.s + 2*P.a*P.e,
        'c_positive': lambda P: P.q*(1 + P.e),
        'q_below_reservations': lambda P: P.e*P.q,
        'lambda_above_tau': lambda P: P.a*P.e,
        'K_geometry': lambda P: P.G + P.e,
        'lambda_above_sigma': lambda P: (P.b - P.a) + P.a*P.e,
        'epsilon_below_one': lambda P: P.G + P.e + P.eps*P.c,
        'K_dominates_log': lambda P: P.eps*P.c,
        'phase_local': lambda P: P.G + 7*P.e/8 + P.eps*P.c,
        'phase_boundary': lambda P: P.G + 3*P.e/8 + P.eps*P.c/2,
        'gamma_sublinear': lambda P: (P.e + P.eps*P.c)/2,
        'alpha_positive': lambda P: P.G + (P.e + P.eps*P.c)/2,
        'original_prefix_above_kappa': lambda P: P.K + P.e,
        'coordinate_movement_above_kappa': lambda P: P.K + 2*P.a*P.e + P.q*(1 - P.eps),
        'Gaussian_arithmetic_above_kappa': lambda P: P.K + 3*P.e/8 + P.eps*P.c/2,
        'scalar_work_above_kappa': lambda P: P.K + 7*P.e/8 + P.eps*P.c,
    },
    'balanced': {
        'a_below_b': lambda P: P.s + P.beta*P.b,
        'q_below_leaf': lambda P: P.s + 2*P.a*P.e,
        'c_positive': lambda P: P.q + P.e/4,
        'lambda_above_tau': lambda P: P.a*P.e,
        'lambda_above_sigma': lambda P: (P.b - P.a) + P.a*P.e,
        'epsilon_below_one': lambda P: P.G + P.e,
        'K_dominates_log': lambda P: P.eps*P.c,
        'phase_local': lambda P: P.G + 7*P.e/8,
        'phase_boundary': lambda P: P.G + 3*P.e/8,
        'alpha_positive': lambda P: P.G + P.e/2,
        'g1_above_kappa': lambda P: P.K + P.e,
        'g2_above_kappa': lambda P: P.K + 2*P.a*P.e + P.q*(1 - P.eps),
        'g5_above_kappa': lambda P: P.K + 3*P.e/8,
        'g6_above_kappa': lambda P: P.K + 7*P.e/8,
    },
}


def uniform(rng, lo, hi, den=1000):
    return Q(rng.randint(int(lo*den), int(hi*den)), den)


def sample_point(rng, near):
    """One (a, b, beta, backoff) point: feasible-looking (near) or wild."""
    def ten(lo, hi):
        return Q(1, 10**rng.randint(lo, hi))
    if near:
        beta = rng.choice((uniform(rng, Q(1, 100), Q(99, 100)), ten(1, 8), 1 - ten(1, 8)))
        e = rng.choice((uniform(rng, Q(1, 1000), Q(499, 1000)), ten(1, 12), Q(1, 2) - ten(1, 9)))
        b = rng.choice((uniform(rng, Q(1, 1000), Q(1, 32), 10**5), Q(1, 32) - ten(3, 12)))
        a = (1 - beta)*b*rng.choice((uniform(rng, Q(1, 1000), 1), 1 - ten(3, 12)))
        return a, b, beta, e
    beta = (uniform(rng, Q(1, 100), Q(99, 100)), uniform(rng, -1, 2), ten(1, 8), 1 - ten(1, 8),
            uniform(rng, Q(1, 10), Q(9, 10)), uniform(rng, 0, 1))[rng.randrange(6)]
    e = rng.choice((uniform(rng, Q(1, 1000), Q(499, 1000)), ten(1, 12), Q(1, 2) - ten(1, 9),
                    uniform(rng, -1, 2), Q(1, 2), uniform(rng, Q(1, 1000), Q(499, 1000))))
    b = rng.choice((uniform(rng, Q(1, 1000), Q(1, 32), 10**5), uniform(rng, -1, 1), Q(1, 32),
                    uniform(rng, Q(1, 32), 1), uniform(rng, Q(1, 1000), Q(1, 32), 10**5)))
    base = (1 - beta)*b
    a = (base*uniform(rng, Q(1, 1000), 1), base, base*uniform(rng, 1, 3), uniform(rng, -1, 1),
         uniform(rng, 0, Q(1, 4), 10**4), uniform(rng, 0, 5),
         base*uniform(rng, Q(1, 1000), 1))[rng.randrange(7)]
    return a, b, beta, e


KAPPA_MODES = ('below', 'at', 'above', 'half', 'zero', 'negative')


def pick_kappa(rng, prefix, a, e, mode):
    if a > 0 and 0 < e < Q(1, 2):
        G = A.ceiling(a, prefix=prefix, backoff=e)
        return {'below': G - Q(1, 10**15), 'at': G, 'above': G + Q(1, 10**15), 'half': G/2,
                'zero': Q(0), 'negative': -uniform(rng, Q(1, 1000), 1)}[mode]
    return uniform(rng, -1, 1)


def run_reference(prefix, a, b, beta, e, kappa, gap, degree_gap, bridge=None):
    """(accepted, failing names or None, result) from the in-tree reference; None to skip."""
    if prefix == 'original':
        mini = {'semantic': {'strict_literal_gap': gap, 'C0': 1}, 'rows': {'degree_gap': degree_gap}}
        try:
            return True, None, S.assembly(a, b, mini, kappa, eta=e, beta=beta)
        except ZeroDivisionError:
            return None
        except AssertionError as error:
            names = set(error.args[0]) if error.args and isinstance(error.args[0], dict) else None
            return False, names, None
    reference = balanced_reference()
    bridge = bridge or load_case('balanced', BRIDGE_FILE).bridge
    try:
        return True, None, reference.assembly(bridge, a, kappa, beta=beta, h=e, a_complex=b)
    except ZeroDivisionError:
        return None
    except reference.InvalidAssembly as error:
        try:
            parsed = ast.literal_eval(str(error))
        except (ValueError, SyntaxError):
            parsed = None
        return False, (set(parsed) if isinstance(parsed, dict) else None), None


class Exact(unittest.TestCase):
    def setUp(self):
        # Certificates hold numerators of thousands of digits: lift the int/str limit per test.
        old = sys.get_int_max_str_digits()
        sys.set_int_max_str_digits(0)
        self.addCleanup(sys.set_int_max_str_digits, old)

    def same(self, x, y, label):
        # Not assertEqual: a failure message would str() numerators of thousands of digits.
        self.assertTrue(x == y, label)

    def compare(self, prefix, a, b, beta, e, kappa, gap, degree_gap, stats=None, bridge=None):
        """Differential check of one point against the in-tree reference.

        The balanced reference takes a finite bridge that fixes the two gap constants.
        """
        if prefix == 'balanced' and bridge is None:
            self.assertTrue((gap, degree_gap) == default_gaps('balanced'), 'balanced bridge gaps')
        ref = run_reference(prefix, a, b, beta, e, kappa, gap, degree_gap, bridge)
        if ref is None:
            if stats is not None:
                stats['skipped'] += 1
            return None
        accepted, names, result = ref
        v = A.check(a, b, kappa, beta, prefix=prefix, backoff=e,
                    literal_scalar_guard=gap, row_product_gap=degree_gap)
        label = '%s point a=%s b=%s beta=%s e=%s kappa=%s' % (prefix, a, b, beta, e, kappa)
        self.assertEqual(v.ok, accepted, label + ' failing=%s names=%s' % (v.failing, names))
        self.assertTrue(set(v.reference_names) <= set(A.COVERAGE[prefix]), label)
        if accepted:
            self.assertTrue(v.complete and v.failing == () and v.reference_names == (), label)
            self.assertEqual(v.ceiling, result['minimum_margin'], label)
            self.assertEqual(v.headroom, result['absorption_gap'], label)
            self.assertLess(kappa, v.ceiling, label)
            self.assertLess(v.ceiling, a/(1 + 2*a) if prefix == 'original' else a/(1 + a), label)
            self.assertLess(kappa, Q(1, 34) if prefix == 'original' else Q(1, 33), label)
        elif names is not None:
            self.assertTrue(names and names <= set(A.COVERAGE[prefix]), label)
            unevaluated = {n for n, s in v.slacks.items() if s is None}
            covered = set(v.reference_names) | {
                n for n in names if unevaluated & set(A.COVERAGE[prefix][n].by)}
            self.assertTrue(names <= covered, label + ' uncovered=%s' % sorted(names - covered))
        if stats is not None:
            stats['accepted' if accepted else 'rejected'] += 1
        return accepted, names, v


class CertifiedPoints(Exact):
    def test_certified_points(self):
        # The six original and 24 balanced certified points: the stored margins and constraints
        # are the closed form, the reduced check accepts the point and rejects kappa = ceiling.
        for prefix, name in FIXTURES:
            with self.subTest(prefix=prefix, fixture=name):
                case, spec = load_case(prefix, name), A.PREFIXES[prefix]
                G = A.ceiling(case.a, prefix=prefix, backoff=case.e)
                q = case.a*(1 - 2*case.e)
                self.same(G, case.minimum, 'ceiling equals stored minimum_margin')
                self.same(case.absorption, G - case.kappa, 'absorption_gap = ceiling - kappa')
                for key, want in (('q', q), ('c', spec.c(q, case.e)),
                                  ('epsilon', spec.epsilon(q, case.e))):
                    self.same(case.params[key], want, key)
                self.assertTrue(all(value > 0 for value in case.constraints.values()))
                self.assertEqual(set(A.COVERAGE[prefix]), set(case.constraints))
                self.assertTrue(case.b > case.a)  # the internal branch is dead here
                self.same(Q(case.asm['recurrence']['internal']), 1 - case.a, 'internal = tau')
                v = run(A.check, prefix, case)
                self.assertTrue(v.ok and v.complete and v.failing == () and v.reference_names == ())
                self.same(v.ceiling, G, 'verdict ceiling')
                self.same(v.headroom, case.absorption, 'verdict headroom')
                self.assertTrue(run(A.feasible, prefix, case))
                at = run(A.check, prefix, replaced(case, kappa=G))
                self.assertEqual(at.failing, ('kappa_below_ceiling',))
                self.assertEqual(set(at.reference_names),
                                 {k for k in case.constraints if k.endswith('_above_kappa')})
                if prefix == 'original':
                    self.same(G, Q(case.asm['margins']['compact_phase_layer']), 'compact_phase_layer')
                else:
                    self.assertTrue(case.replay['constraints'] == case.constraints, 'replay constraints')
                    self.same(case.replay['minimum_margin'], case.minimum, 'replay minimum_margin')
                    self.same(case.replay['scoped_limit'], case.scoped_limit, 'replay scoped_limit')
                    self.assertLess(G, case.scoped_limit)
                    self.same(case.scoped_limit, case.a/(1 + case.a), 'scoped limit a/(1+a)')

    def test_balanced_file_list_is_a_subset_of_the_discovered_files(self):
        # Discovery reads only certificate-like names under 1 MB, with a byte scan before parsing.
        paths = list((ROOT/'certificates').glob('*.json'))
        for directory, _, files in os.walk(ROOT/'research'):
            paths += [Path(directory)/f for f in files
                      if f.endswith('.json') and ('certificate' in f or 'arithmetic' in f)]
        found = {path.relative_to(ROOT).as_posix() for path in paths
                 if path.stat().st_size <= 10**6 and b'"finite_bridge"' in path.read_bytes()
                 and b'"scoped_limit"' in path.read_bytes()}
        self.assertEqual(len(BALANCED_FILES), len(set(BALANCED_FILES)))
        self.assertTrue(set(BALANCED_FILES) <= found, sorted(set(BALANCED_FILES) - found))

    def test_balanced_paired_cube_regime(self):
        a, b, beta, h = Q(4613422943, 10**13), Q(4856569, 10**10), Q(1, 10**6), Q(1, 10**8)
        gap, degree_gap = default_gaps('balanced')
        for kappa, accepted in ((Q(4611295, 10**10), True),
                                (A.ceiling(a, prefix='balanced', backoff=h), False)):
            self.assertEqual(self.compare('balanced', a, b, beta, h, kappa, gap, degree_gap)[0],
                             accepted)

    def test_known_ceilings(self):
        original = (((Q(1, 100), Q(1, 40), Q(1, 4), Q(1, 10)), Q(9, 1271)),
                    ((Q(1, 60), Q(3, 100), Q(1, 3), Q(499, 1000)), Q(167, 10000833)),
                    ((Q(1, 200), Q(1, 50), Q(1, 2), Q(1, 4)), Q(3, 1609)),
                    ((Q(1, 1000), Q(1, 100), Q(1, 10), Q(1, 100)), Q(4851, 5009849)),
                    ((Q(1, 64), Q(31249, 10**6), Q(1, 10**6), Q(1, 10**8)),
                     Q(4999999850000001, 329999999849999999)))
        balanced = (((Q(1, 100), Q(1, 40), Q(1, 4), Q(1, 10)), Q(1, 140)),
                    ((Q(1, 60), Q(3, 100), Q(1, 3), Q(499, 1000)), Q(501, 30001000)),
                    ((Q(1, 200), Q(1, 50), Q(1, 2), Q(1, 4)), Q(3, 1604)))
        for prefix, table in (('original', original), ('balanced', balanced)):
            gap, degree_gap = default_gaps(prefix)
            for (a, b, beta, e), want in table:
                with self.subTest(prefix=prefix, a=a, e=e):
                    self.assertEqual(A.ceiling(a, prefix=prefix, backoff=e), want)
                    below = want*(1 - Q(1, 10**6))
                    self.assertTrue(self.compare(prefix, a, b, beta, e, below, gap, degree_gap)[0])
                    out = self.compare(prefix, a, b, beta, e, want, gap, degree_gap)
                    self.assertFalse(out[0])
                    self.assertEqual(out[2].failing, ('kappa_below_ceiling',))

    def test_eta_to_zero_approaches_the_informal_ceilings(self):
        for prefix, limit in (('original', lambda a: a/(1 + 2*a)), ('balanced', lambda a: a/(1 + a))):
            for a in (Q(1, 1000), Q(1, 100), Q(1, 50), Q(1, 32)):
                for k in (3, 6, 9, 12):
                    e = Q(1, 10**k)
                    gap = limit(a) - A.ceiling(a, prefix=prefix, backoff=e)
                    self.assertTrue(0 < gap < e, (prefix, a, k))

    def test_duplicate_classes_and_identities_hold_in_every_certificate(self):
        for prefix in PREFIXES:
            self.assertEqual(set(IDENTITIES[prefix]),
                             {n for n, e in A.COVERAGE[prefix].items() if e.status == 'identity'})
        for prefix, name in FIXTURES:
            with self.subTest(prefix=prefix, fixture=name):
                case, stored = load_case(prefix, name), load_case(prefix, name).constraints
                P = derived(prefix, case.a, case.b, case.beta, case.e, case.kappa)
                v = run(A.check, prefix, case)
                for ref, entry in A.COVERAGE[prefix].items():
                    if entry.status == 'duplicate':
                        factor, _, rep = entry.why.partition('*')
                        target = stored[rep] if rep in stored else v.slacks[rep]
                        self.same(stored[ref], Q(factor)*target, ref + ' = ' + entry.why)
                    elif entry.status == 'reduced':
                        self.same(stored[ref], v.slacks[entry.by[0]], ref + ' is ' + entry.by[0])
                for ref, expression in IDENTITIES[prefix].items():
                    self.same(stored[ref], expression(P),
                              ref + ' identity')


class DifferentialGrid(Exact):
    COUNT = 2400

    def run_grid(self, prefix, seed):
        rng = random.Random(seed)
        stats = {'accepted': 0, 'rejected': 0, 'skipped': 0, 'near': 0}
        varied = tuple(Q(1) for _ in range(12)) + (Q(10**30), Q(0), Q(-1), Q(-1, 10**9))
        for i in range(self.COUNT):
            a, b, beta, e = sample_point(rng, i % 2 == 0)
            mode = KAPPA_MODES[i % len(KAPPA_MODES)]
            kappa = pick_kappa(rng, prefix, a, e, mode)
            gap, degree_gap = default_gaps(prefix)
            if prefix == 'original':
                gap, degree_gap = rng.choice(varied), rng.choice(varied)
            out = self.compare(prefix, a, b, beta, e, kappa, gap, degree_gap, stats)
            if out is not None and out[0] and mode in ('below', 'half'):
                stats['near'] += 1
        self.assertGreaterEqual(stats['accepted'], 300, stats)
        self.assertGreaterEqual(stats['rejected'], 1000, stats)
        self.assertGreaterEqual(stats['near'], 200, stats)
        self.assertEqual(stats['accepted'] + stats['rejected'] + stats['skipped'], self.COUNT)

    def test_original_grid(self):
        self.run_grid('original', 20261009)

    def test_balanced_grid(self):
        self.run_grid('balanced', 20261010)

    def test_kappa_modes_around_every_certified_ceiling(self):
        for prefix, name in FIXTURES:
            with self.subTest(prefix=prefix, fixture=name):
                case = load_case(prefix, name)
                G = A.ceiling(case.a, prefix=prefix, backoff=case.e)
                for kappa in (G - Q(1, 10**15), G, G + Q(1, 10**15), G/2, Q(0), -G):
                    out = self.compare(prefix, case.a, case.b, case.beta, case.e, kappa,
                                       case.gap, case.degree_gap, bridge=case.bridge)
                    # Only the balanced reference rejects kappa <= 0.
                    self.assertEqual(out[0], kappa < G if prefix == 'original' else 0 < kappa < G)


def base_point(prefix):
    a, b, beta, e = Q(1, 100), Q(1, 40), Q(1, 4), Q(1, 10)
    gap, degree_gap = default_gaps(prefix)
    return SimpleNamespace(a=a, b=b, beta=beta, e=e, gap=gap, degree_gap=degree_gap,
                           kappa=A.ceiling(a, prefix=prefix, backoff=e)/2)


def ceil_of(prefix, p):
    return A.ceiling(p.a, prefix=prefix, backoff=p.e)


# name -> mutator(point, prefix) violating that reduced condition once.
MUTATORS = {
    'bit_positive': lambda p, pre: replaced(p, a=Q(0)),
    'beta_positive': lambda p, pre: replaced(p, beta=Q(0)),
    'beta_below_one': lambda p, pre: replaced(p, beta=Q(1)),
    'backoff_positive': lambda p, pre: replaced(p, e=Q(0)),
    'q_positive': lambda p, pre: replaced(p, e=Q(1, 2)),
    'complex_below_one_over32': lambda p, pre: replaced(p, b=Q(1, 32)),
    'leaf_saving_above_bit': lambda p, pre: replaced(p, a=(1 - p.beta)*p.b),
    'kappa_below_ceiling': lambda p, pre: replaced(p, kappa=ceil_of(pre, p)),
    'literal_scalar_guard': lambda p, pre: replaced(p, gap=Q(0)),
    'row_product_gap': lambda p, pre: replaced(p, degree_gap=Q(0)),
    'kappa_positive': lambda p, pre: replaced(p, kappa=Q(0)),
}
# Failing names expected for the mutated point (a = 0 also zeroes q).
MUTATED_FAILING = {name: (name,) for name in MUTATORS}
MUTATED_FAILING['bit_positive'] = ('bit_positive', 'q_positive')
BRIDGE_CONDITIONS = ('literal_scalar_guard', 'row_product_gap')
# name -> changes to the base point that make this condition's slack exactly s.
SLACK_AT = {
    'bit_positive': lambda p, s, pre: dict(a=s),
    'beta_positive': lambda p, s, pre: dict(beta=s),
    'beta_below_one': lambda p, s, pre: dict(beta=1 - s, a=s*p.b/2 if s > 0 else p.a),
    'backoff_positive': lambda p, s, pre: dict(e=s),
    'q_positive': lambda p, s, pre: dict(e=(1 - s/p.a)/2),
    'complex_below_one_over32': lambda p, s, pre: dict(b=Q(1, 32) - s,
                                                       a=(1 - p.beta)*(Q(1, 32) - s)/2),
    'leaf_saving_above_bit': lambda p, s, pre: dict(a=(1 - p.beta)*p.b - s),
    'kappa_below_ceiling': lambda p, s, pre: dict(kappa=ceil_of(pre, p) - s),
    'literal_scalar_guard': lambda p, s, pre: dict(gap=s),
    'row_product_gap': lambda p, s, pre: dict(degree_gap=s),
    'kappa_positive': lambda p, s, pre: dict(kappa=s),
}


def at_slack(name, s, prefix):
    """Point whose slack for condition `name` is exactly s and every other one positive."""
    p = base_point(prefix)
    p = replaced(p, **SLACK_AT[name](p, s, prefix))
    if name.startswith('kappa'):
        return p
    try:
        return replaced(p, kappa=ceil_of(prefix, p)/2)
    except ValueError:  # the point is outside the ceiling's domain (it is rejected anyway)
        return p


class ReducedConditions(Exact):
    def evaluate(self, prefix, name, p):
        """Verdict for p; also the reference verdict unless the bridge itself was changed."""
        if prefix == 'balanced' and name in BRIDGE_CONDITIONS:
            return None, None, run(A.check, prefix, p)
        return self.compare(prefix, p.a, p.b, p.beta, p.e, p.kappa, p.gap, p.degree_gap)

    def test_each_reduced_condition_violated_once(self):
        for prefix in PREFIXES:
            for cond in A.REDUCED:
                name = cond.name
                p = MUTATORS[name](base_point(prefix), prefix)
                with self.subTest(prefix=prefix, violated=name):
                    accepted, names, v = self.evaluate(prefix, name, p)
                    if prefix not in cond.prefixes:
                        # The original reference accepts kappa <= 0 (documented divergence).
                        self.assertTrue(accepted and v.ok and v.complete)
                        self.assertNotIn(name, v.slacks)
                        continue
                    self.assertFalse(accepted or v.ok)
                    self.assertEqual(v.failing, MUTATED_FAILING[name])
                    self.assertTrue(v.slacks[name] <= 0)
                    stands_for = {r for pre, r in cond.covers if pre == prefix}
                    if names is not None and stands_for and name not in BRIDGE_CONDITIONS:
                        # Rows that are this slack up to a factor fail with it; the kappa
                        # ceiling is only part of each of its seven rows.
                        self.assertTrue(stands_for <= names if cond.kind != 'kappa'
                                        else stands_for & names, (names, stands_for))

    def test_domain_failure_leaves_later_slacks_unevaluated(self):
        v = run(A.check, 'original', replaced(base_point('original'), beta=Q(0)))
        self.assertFalse(v.ok or v.complete)
        self.assertIsNone(v.ceiling)
        self.assertIsNone(v.headroom)
        for cond in A.REDUCED:
            if cond.kind == 'domain':
                self.assertIsNotNone(v.slacks[cond.name])
            elif 'original' in cond.prefixes:
                self.assertIsNone(v.slacks[cond.name])
        self.assertEqual(list(v.slacks), [c.name for c in A.REDUCED if 'original' in c.prefixes])
        self.assertEqual(v.failing, ('beta_positive',))

    def test_exact_boundary_slack_zero_rejected_and_tiny_positive_accepted(self):
        for prefix in PREFIXES:
            for cond in A.REDUCED:
                if prefix not in cond.prefixes:
                    continue
                for s, expect in ((Q(0), False), (TINY, True)):
                    with self.subTest(prefix=prefix, condition=cond.name, slack=s):
                        accepted, _, v = self.evaluate(prefix, cond.name,
                                                       at_slack(cond.name, s, prefix))
                        self.assertEqual(v.slacks[cond.name], s)
                        self.assertEqual(v.ok, expect)
                        if expect:
                            self.assertTrue(v.complete and v.failing == ())
                        else:
                            self.assertEqual(v.failing, MUTATED_FAILING[cond.name]
                                             if cond.name == 'bit_positive' else (cond.name,))
                        if accepted is not None:
                            self.assertEqual(accepted, expect)

    def test_kappa_positive_divergence_between_the_references(self):
        p = base_point('original')
        for kappa in (Q(0), Q(-1), Q(-1, 10**9)):
            for prefix in PREFIXES:
                gap, degree_gap = default_gaps(prefix)
                accepted, names, v = self.compare(prefix, p.a, p.b, p.beta, p.e, kappa, gap,
                                                  degree_gap)
                self.assertEqual(accepted, prefix == 'original')
                self.assertEqual(v.ok, prefix == 'original')
                if prefix == 'balanced':
                    self.assertEqual(v.failing, ('kappa_positive',))
                    self.assertIsNone(names)  # the balanced gate raises a non-dict message

    def test_out_of_domain_points_do_not_raise(self):
        # Both references raise (ZeroDivisionError, InvalidAssembly) where 1+q*(2+eta) or the
        # backoff leaves the domain; check() is total on exact inputs.
        v = A.check(Q(1, 3), Q(1, 40), Q(1, 100), Q(1, 4), prefix='original', backoff=Q(1))
        self.assertFalse(v.ok or v.complete)
        self.assertIn('q_positive', v.failing)
        self.assertFalse(A.check(Q(1), Q(1, 40), Q(1, 100), Q(1, 4), prefix='balanced',
                                 backoff=Q(1)).ok)
        for prefix in PREFIXES:
            for a, b, kappa, beta, e in ((-5, 3, 7, 9, 11), (0, 0, 0, 0, 0),
                                         (10**9, -10**9, 2, -3, 5)):
                v = A.check(a, b, kappa, beta, prefix=prefix, backoff=e)
                self.assertFalse(v.ok)
                self.assertIsNone(v.ceiling)


def raw_slacks(prefix, a, b, beta, e, kappa, gap, degree_gap):
    """Every reduced slack computed directly, with no domain-first short-circuit."""
    spec = A.PREFIXES[prefix]
    q = a*(1 - 2*e)
    D = spec.denominator(q, e)
    return {'bit_positive': a, 'beta_positive': beta, 'beta_below_one': 1 - beta,
            'backoff_positive': e, 'q_positive': q,
            'complex_below_one_over32': Q(1, 32) - b,
            'leaf_saving_above_bit': (1 - beta)*b - a,
            'kappa_below_ceiling': None if D == 0 else spec.ceiling(q, e) - kappa,
            'literal_scalar_guard': gap, 'row_product_gap': degree_gap, 'kappa_positive': kappa}


class ByListsAreSufficient(Exact):
    """Whenever the reference reports a constraint as violated, some condition in its `by` list
    has a raw slack <= 0, independently of the module's domain-first evaluation; a `by` list
    that is too short is caught."""

    def check_by_lists(self, prefix, a, b, beta, e, kappa, gap, degree_gap):
        ref = run_reference(prefix, a, b, beta, e, kappa, gap, degree_gap)
        if ref is None or ref[0] or ref[1] is None:
            return 0
        raw = raw_slacks(prefix, a, b, beta, e, kappa, gap, degree_gap)
        checked = 0
        for name in ref[1]:
            known = [raw[c] for c in A.COVERAGE[prefix][name].by]
            if any(s is None for s in known):
                continue
            label = '%s %s a=%s b=%s beta=%s e=%s kappa=%s' % (prefix, name, a, b, beta, e, kappa)
            self.assertTrue(any(s <= 0 for s in known), label)
            checked += 1
        return checked

    def test_random_points(self):
        for prefix, seed in (('original', 71), ('balanced', 72)):
            rng = random.Random(seed)
            checked = 0
            for i in range(1500):
                a, b, beta, e = sample_point(rng, i % 3 == 0)
                kappa = pick_kappa(rng, prefix, a, e, KAPPA_MODES[i % len(KAPPA_MODES)])
                gap, degree_gap = default_gaps(prefix)
                checked += self.check_by_lists(prefix, a, b, beta, e, kappa, gap, degree_gap)
            self.assertGreaterEqual(checked, 1000, prefix)

    def test_negative_backoff_points(self):
        # A negative backoff with every other slack positive is where a `by` list that
        # omits backoff_positive would be insufficient (e.g. compact_leaf = s + 2*a*eta).
        for prefix in PREFIXES:
            gap, degree_gap = default_gaps(prefix)
            for e in (Q(-1), Q(-1, 2), Q(-10), Q(-1, 10**6), Q(-100)):
                p = base_point(prefix)
                with self.subTest(prefix=prefix, backoff=e):
                    ref = run_reference(prefix, p.a, p.b, p.beta, e, Q(1, 10**9), gap, degree_gap)
                    self.assertFalse(ref is not None and ref[0])
                    if prefix == 'original':
                        self.assertGreater(self.check_by_lists(
                            prefix, p.a, p.b, p.beta, e, Q(1, 10**9), gap, degree_gap), 0)


class Identities(Exact):
    def test_prefix_identities_on_random_domain_points(self):
        rng = random.Random(99)
        for _ in range(600):
            a = uniform(rng, Q(1, 100000), Q(1, 32), 10**6)
            e = rng.choice((uniform(rng, Q(1, 100000), Q(499, 1000), 10**6),
                            Q(1, 10**rng.randint(1, 15))))
            o = derived('original', a, Q(1, 40), Q(1, 4), e, Q(0))
            self.assertEqual(1 - o.eps*(1 + o.c) - o.eps*o.q, e)
            self.assertEqual(o.G, o.eps*o.q)
            self.assertEqual(A.ceiling(a, prefix='original', backoff=e), o.eps*o.q)
            self.assertEqual(o.c, o.q*(1 + e))
            self.assertEqual(o.eps, (1 - e)/(1 + o.c + o.q))
            self.assertLess(o.G, a/(1 + 2*a))
            b = derived('balanced', a, Q(1, 40), Q(1, 4), e, Q(0))
            self.assertEqual(1 - b.eps - b.eps*b.q, e)
            self.assertEqual(1 - b.eps - b.r, e/2)
            self.assertEqual(1 - b.eps*(1 + b.c), e - b.eps*e/4)
            self.assertEqual(A.ceiling(a, prefix='balanced', backoff=e), b.eps*b.q)
            self.assertEqual(b.c, b.q + e/4)
            self.assertEqual(b.eps, (1 - e)/(1 + b.q))
            self.assertLess(b.G, a/(1 + a))
            self.assertLess(Q(0), b.G)


class Validation(Exact):
    BAD = (0.5, float('nan'), float('inf'), True, False, '1/2', None, 1 + 0j, [1], Decimal(1))

    def test_exact_accepts_only_int_and_fraction(self):
        self.assertEqual(A.exact(3, 'x'), Q(3))
        self.assertIs(type(A.exact(3, 'x')), Q)
        for bad in self.BAD:
            with self.subTest(bad=repr(bad)), self.assertRaises(ValueError):
                A.exact(bad, 'x')

    def test_check_and_ceiling_reject_non_exact_inputs(self):
        good = dict(a=Q(1, 100), b=Q(1, 40), kappa=Q(1, 1000), beta=Q(1, 4), backoff=Q(1, 10))
        for field, bad in (('a', 0.5), ('b', True), ('kappa', '1/2'), ('beta', None),
                           ('backoff', 0.1), ('literal_scalar_guard', 0.5)):
            with self.subTest(field=field, bad=repr(bad)), self.assertRaises(ValueError):
                A.check(prefix='original', **dict(good, **{field: bad}))
        for bad in (0.5, True, '1/2', None):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(ValueError):
                    A.ceiling(bad, prefix='balanced', backoff=Q(1, 10))
                with self.assertRaises(ValueError):
                    A.ceiling(Q(1, 100), prefix='balanced', backoff=bad)

    def test_ceiling_domain(self):
        for prefix in PREFIXES:
            for a, e in ((0, Q(1, 10)), (-1, Q(1, 10)), (Q(1, 100), 0), (Q(1, 100), Q(1, 2)),
                         (Q(1, 100), Q(-1, 10)), (Q(1, 100), 1), (Q(1, 100), Q(3, 2))):
                with self.subTest(prefix=prefix, a=a, e=e), self.assertRaises(ValueError):
                    A.ceiling(a, prefix=prefix, backoff=e)

    def test_missing_bridge_constants_mean_not_checked(self):
        p = base_point('original')
        args, kw = (p.a, p.b, p.kappa, p.beta), dict(prefix='original', backoff=p.e)
        v = A.check(*args, **kw)
        self.assertTrue(v.ok and not v.complete and v.failing == ())
        self.assertIsNone(v.slacks['literal_scalar_guard'])
        self.assertIsNone(v.slacks['row_product_gap'])
        with self.assertRaises(TypeError):  # the verdict is read-only
            v.slacks['bit_positive'] = 0
        half = A.check(*args, literal_scalar_guard=Q(1), **kw)
        self.assertTrue(half.ok and not half.complete)
        for gaps in ((None, Q(1)), (Q(1), None), (None, None), (Q(0), Q(1)), (Q(1), Q(-1))):
            self.assertFalse(A.feasible(*args, literal_scalar_guard=gaps[0],
                                        row_product_gap=gaps[1], **kw))
        self.assertTrue(A.feasible(*args, literal_scalar_guard=Q(1), row_product_gap=Q(1), **kw))

    def test_huge_bridge_gaps_are_never_stringified(self):
        # These gaps have thousands of digits: under the default 4300-digit limit any str() or
        # float() on them would raise.
        cases = [load_case('original', 'certificates/%s-network.json' % name)
                 for name in ('three-stage-cover', 'paired-cube')]
        self.assertGreater(max(c.gap.numerator.bit_length() for c in cases), 15000)
        sys.set_int_max_str_digits(4300)  # setUp's cleanup restores the previous limit
        for case in cases:
            self.assertTrue(run(A.feasible, 'original', case))
            bad = run(A.check, 'original', replaced(case, gap=-case.gap))
            self.assertEqual(bad.failing, ('literal_scalar_guard',))


if __name__ == '__main__':
    unittest.main()
