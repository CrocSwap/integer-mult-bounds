"""Check the proof's algebra, complete circuits, source adapter and controls."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from exact import QI, need, unit
from native import Native, act, character_tuple, gram_factor
from native_identity import decide, endpoint, validate
import check_certificate as checker
from examples import cnf_problem, diagonal, late_projector, source_conjugation
import reversible_cnf as reversible

def authenticated_sources():
    pins = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    for row in pins['files']:
        data = (HERE / row['retained']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256 mismatch')
        need(len(data) == row['bytes'], 'source length mismatch')
    sys.path.insert(0, str(HERE / 'source'))
    import monomial
    return monomial, len(pins['files'])


def statistics(points, n):
    return ((len(points) % 4,) + tuple(sum((x >> i) & 1 for x in points) % 4 for i in range(n))
            + tuple(sum(((x >> i) & 1) * ((x >> j) & 1) for x in points) % 2
                    for i in range(n) for j in range(i + 1, n)))


def gram_checks():
    count = 0
    for n in range(1, 6):
        entries = [(i, j) for i in range(n) for j in range(i, n)]
        for mask in range(1 << len(entries)):
            rows = [0] * n
            for k, (i, j) in enumerate(entries):
                if mask >> k & 1:
                    rows[i] |= 1 << j
                    rows[j] |= 1 << i
            vectors = gram_factor(rows)
            need(len(vectors) <= n + 1, 'Gram factor width')
            actual = [sum((sum(((v >> i) & 1) * ((v >> j) & 1) for v in vectors) % 2) << j
                          for j in range(n)) for i in range(n)]
            need(actual == rows, 'literal Gram product')
            count += 1
    return count


def character_checks(rng):
    count = 0
    for n in range(1, 4):
        for first in itertools.product(range(4), repeat=n + 1):
            for tail in itertools.product(range(2), repeat=n * (n - 1) // 2):
                character = first + tail
                points = character_tuple(n, character)
                need(statistics(points, n) == character, 'complete phase-character statistics')
                need(points[:n + 1] == [0] + [1 << i for i in range(n)], 'affine basis retained')
                need(2 * n + 4 <= len(points) <= 2 * n + 7, 'four-width cutoff')
                count += 1
    large = 0
    for n, trials in ((4, 32), (9, 32), (17, 32), (73, 4)):
        for _ in range(trials):
            ch = tuple(rng.randrange(4) for _ in range(n + 1)) + tuple(rng.randrange(2) for _ in range(n * (n - 1) // 2))
            points = character_tuple(n, ch, 2 * n + 8)
            need(statistics(points, n) == ch and len(points) >= 2 * n + 8, 'later-window phase realization')
            large += 1
    return count, large


def random_native(n, rng):
    rows = [1 << i for i in range(n)]
    for _ in range(4 * n):
        i, j = rng.randrange(n), rng.randrange(n)
        if i != j:
            rows[i] ^= rows[j]
    return Native(tuple(rows), rng.randrange(1 << n), rng.randrange(4),
                  tuple(rng.randrange(4) for _ in range(n)),
                  tuple(rng.randrange(1 << n) & ~((1 << (i + 1)) - 1) for i in range(n)))


def group_checks(rng):
    one = [Native((1,), t, c, (a,), (0,)) for t in range(2) for c in range(4) for a in range(4)]
    pairs = [(g, h) for g in one for h in one]
    pairs += [(random_native(n, rng), random_native(n, rng)) for n in (2, 3, 4, 9) for _ in range(32)]
    point_checks = 0
    for g, h in pairs:
        p, inv = g.compose(h), g.inv()
        a, b = checker.normalize(g.json(), g.n), checker.normalize(h.json(), h.n)
        need(checker.compose(a, b) == checker.normalize(p.json(), g.n), 'separate composition formulas')
        need(checker.inverse(a) == checker.normalize(inv.json(), g.n), 'separate inverse formulas')
        need(g.compose(inv) == Native.identity(g.n) == inv.compose(g), 'two-sided inverse')
        for x in range(1 << g.n):
            need(p.image(x) == g.image(h.image(x)), 'literal composed address')
            need(p.exponent(x) == (h.exponent(x) + g.exponent(h.image(x))) % 4, 'literal composed phase')
            need(inv.image(g.image(x)) == x and (g.exponent(x) + inv.exponent(g.image(x))) % 4 == 0,
                 'literal inverse phase')
            point_checks += 1
    return len(pairs), point_checks


def literal_from_algebra(rows, input_role, points):
    out = []
    for row in rows:
        result = {}
        for (i, g), value in row.items():
            if i == input_role:
                key = tuple(g.image(x) for x in points)
                checker.accumulate(result, key, value * unit(sum(g.exponent(x) for x in points)))
        out.append(result)
    return out


def circuit_checks(rng):
    checked, positives, negatives, basis_checks = 0, 0, 0, 0
    for trial in range(120):
        n = 1 + trial % 3
        g, h = random_native(n, rng), random_native(n, rng)
        gs = {'G': g.json(), 'H': h.json(), 'K': g.compose(h).json()}
        prefix = []
        for _ in range(5):
            op = rng.choice(['add', 'query', 'apply', 'scale', 'swap'])
            ins = {'op': op, 'dst': rng.randrange(3)}
            if op in ('add', 'query', 'swap'):
                ins['src'] = rng.randrange(3)
            if op in ('apply', 'query'):
                ins.update(generator=rng.choice(['G', 'H']), inverse=bool(rng.randrange(2)))
            if op in ('add', 'query', 'scale'):
                ins['coefficient'] = rng.choice([0, 1, -1, '1/2', [0, 1], ['1/3', '-1/2']])
            prefix.append(ins)
        left = prefix + [{'op': 'apply', 'dst': 1, 'generator': 'H'}, {'op': 'apply', 'dst': 1, 'generator': 'G'}]
        right = prefix + [{'op': 'apply', 'dst': 1, 'generator': 'K'}]
        if trial % 2:
            right.append({'op': 'add', 'src': 0, 'dst': 2})
        problem = {'axes': n, 'roles': 3, 'generators': gs, 'program': left, 'reference': right}
        cert = decide(problem)
        checker.check(problem, cert)
        if cert['status'] == 'COUNTEREXAMPLE':
            negatives += 1
        else:
            positives += 1
        checked += 1
        generators = validate(problem)
        formal, _ = endpoint(problem, left, generators)
        raw = checker.problem_data(problem)
        for width in (1, 2):
            for points in itertools.product(range(1 << n), repeat=width):
                for source in range(3):
                    direct = checker.literal_endpoint(problem, left, raw, source, points, 100000)
                    need(direct == literal_from_algebra(formal, source, points), 'complete literal endpoint differential')
                    basis_checks += 1
    need(positives >= 60 and negatives >= 30, 'nontrivial positive and negative coverage')
    return checked, positives, negatives, basis_checks


def source_checks(monomial):
    raw = json.loads((HERE / 'source/RIGHT-RECIPE.json').read_text())
    g = Native.parse(raw, 9)
    for x in range(512):
        need(g.image(x) == monomial.column_map(raw, x), 'actual native address convention')
        need(g.exponent(x) == (raw['phase'] + monomial.column_phase(raw, x)) % 4,
             'actual native phase convention')
    probes = 0
    for f in (1, 2, 22, 23, 24, 25):
        points = [(17 * j + 7 * f) % 512 for j in range(f)]
        state = {'v' + str(i): sum(((points[j] >> i) & 1) << (1 + 2 * j) for j in range(f)) for i in range(9)}
        need(monomial.tensor_phase(raw, state, f, 2, 1) == sum(g.exponent(x) for x in points) % 4,
             'source constant phase scales with width')
        probes += 1
    good, bad = source_conjugation(), source_conjugation(True)
    need(decide(good)['status'] == 'IDENTITY_ALL_POSITIVE_WIDTHS', 'actual conjugation identity')
    cert = decide(bad)
    need(cert['status'] == 'COUNTEREXAMPLE' and len(cert['input_points']) % 2 == 1, 'constant omission needs odd witness')
    checker.check(good, decide(good)); checker.check(bad, cert)
    gs = checker.problem_data(bad)
    for x in range(512):
        points = [x, x ^ 511]
        a = checker.literal_endpoint(bad, bad['program'], gs, 0, points, 100000)
        b = checker.literal_endpoint(bad, bad['reference'], gs, 0, points, 100000)
        need(a == b, 'phase mutation is invisible at even width')
    return {'source_addresses': 512, 'tensor_phase_probes': probes, 'even_width_blind_cases': 512,
            'failure_width': len(cert['input_points']), 'discrepancy': cert['discrepancy']}


def projector_checks():
    vanished = 0
    for n in range(1, 5):
        problem = late_projector(n)
        gs = checker.problem_data(problem)
        for f in range(1, n):
            for points in itertools.product(range(1 << n), repeat=f):
                got = checker.literal_endpoint(problem, problem['program'], gs, 0, points, 100000)
                need(got == [{}], 'complete below-rank projector vanishing')
                vanished += 1
        points = tuple(1 << i for i in range(n))
        got = checker.literal_endpoint(problem, problem['program'], gs, 0, points, 100000)
        need(got == [{points: QI(1)}], 'first possible projector width is attained')
    # Each omitted residue has a central projector that only it detects.
    for residue in range(4):
        for f in range(1, 13):
            value = sum((unit(-residue * c) * unit(f * c) for c in range(4)), QI())
            need(value == (4 if f % 4 == residue else 0), 'four-width necessity')
    return vanished, 48


def cnf_checks(rng):
    formulas, assignments, unsat = 0, 0, 0
    for n in range(1, 6):
        for trial in range(16):
            clauses = [[rng.choice((-1, 1)) * rng.randint(1, n) for _ in range(rng.randrange(4))]
                       for _ in range(rng.randrange(1, 8))]
            if trial == 0:
                clauses = [[1], [-1]]
            word = reversible.cnf_word(n, clauses)
            sat = False
            for x in range(1 << n):
                value = all(any(bool(x >> (abs(lit) - 1) & 1) == (lit > 0) for lit in clause) for clause in clauses)
                sat |= value
                need(reversible.evaluate(word, x) == (reversible.A if value else reversible.IDENTITY),
                     'complete CNF permutation truth table')
                assignments += 1
            unsat += not sat
            formulas += 1
    return formulas, assignments, unsat


def reversible_checks():
    need(reversible.compose(reversible.inverse(reversible.B),
         reversible.compose(reversible.inverse(reversible.A), reversible.compose(reversible.B, reversible.A)))
         == reversible.C, 'five-cycle commutator')
    pairs, columns = 0, 0
    for zero in itertools.permutations(range(5)):
        for one in (reversible.IDENTITY, reversible.A, reversible.B, reversible.C):
            problem = reversible.lower_word(1, [(0, zero, one)])
            gs = checker.problem_data(problem)
            need(all(ins['op'] != 'scale' and
                     (ins['op'] not in ('add', 'query', 'swap') or ins['src'] != ins['dst'])
                     for ins in problem['program']), 'only invertible dirty-role operations')
            for x in (0, 1):
                for i in range(5):
                    out = checker.literal_endpoint(problem, problem['program'], gs, i, [x], 100000)
                    expected = [{} for _ in range(5)]
                    expected[(one if x else zero)[i]][(x,)] = QI(1)
                    need(out == expected, 'literal conditional permutation on every dirty column')
                    columns += 1
            pairs += 1
    literal_cnf = 0
    for clauses in ([[1], [-1]], [[1, 2], [-1]], [[1, 2, 3], [-1, -2, -3]]):
        problem = cnf_problem(3, clauses)
        gs = checker.problem_data(problem)
        for x in range(8):
            truth = all(any(bool(x >> (abs(lit) - 1) & 1) == (lit > 0) for lit in clause) for clause in clauses)
            permutation = reversible.A if truth else reversible.IDENTITY
            for source in range(5):
                expected = [{} for _ in range(5)]
                expected[permutation[source]][(x,)] = QI(1)
                out = checker.literal_endpoint(problem, problem['program'], gs, source, [x], 100000)
                need(out == expected, 'complete literal reversible CNF endpoint')
                literal_cnf += 1
    return pairs, columns, literal_cnf


def rejection_checks():
    count = 0
    def rejects(action):
        nonlocal count
        try:
            action()
        except (ValueError, TypeError, KeyError):
            count += 1
        else:
            raise ValueError('negative control was accepted')
    good, bad = source_conjugation(), source_conjugation(True)
    certificate = decide(bad)
    for field, value in [('problem_sha256', '0' * 64), ('axes', 8), ('roles', 1), ('window', [1, 4]),
                         ('input_role', 2), ('output_role', -1), ('discrepancy', ['0', '0']), ('status', 'UNKNOWN'),
                         ('input_points', [-1] * 23), ('output_points', []), ('input_points', [0])]:
        changed = dict(certificate); changed[field] = value
        rejects(lambda c=changed: checker.check(bad, c))
    fake = dict(certificate, status='IDENTITY_ALL_POSITIVE_WIDTHS', residual_terms=0)
    rejects(lambda: checker.check(bad, fake))
    for field, value in [('axes', 0), ('roles', True)]:
        p = copy.deepcopy(good); p[field] = value
        rejects(lambda p=p: decide(p)); rejects(lambda p=p: checker.problem_data(p))
    for mutate in (lambda p: p['generators']['G'].__setitem__('phase', 4),
                   lambda p: p['generators']['G'].__setitem__('matrix_rows', [0] * 9),
                   lambda p: p['program'][3].__setitem__('coefficient', 0.5),
                   lambda p: p['program'][3].__setitem__('coefficient', '1e10000000'),
                   lambda p: p['program'][0].__setitem__('inverse', 1),
                   lambda p: p['program'][0].__setitem__('coefficient', 2),
                   lambda p: p['program'][0].__setitem__('dst', 2)):
        p = copy.deepcopy(good); mutate(p)
        rejects(lambda p=p: decide(p)); rejects(lambda p=p: checker.problem_data(p))
    p = late_projector(2)
    rejects(lambda: decide(p, max_terms=1))
    rejects(lambda: checker.algebra_endpoint(p, p['program'], checker.problem_data(p), 1))
    rejects(lambda: gram_factor([2, 0]))
    rejects(lambda: character_tuple(1, (4, 0)))
    rejects(lambda: character_tuple(1, (0, 0), floor=5))
    empty = {'axes': 1, 'roles': 2, 'generators': {}, 'program': [], 'reference': []}
    rejects(lambda: decide(empty, max_terms=1))
    rejects(lambda: checker.algebra_endpoint(empty, [], {}, 1))
    return count


def committed_examples():
    count = 0
    for path in sorted((HERE / 'examples').glob('*.certificate.json')):
        problem_path = path.with_name(path.name.replace('.certificate.json', '.json'))
        problem, certificate = json.loads(problem_path.read_text()), json.loads(path.read_text())
        checker.check(problem, certificate)
        if not path.name.startswith('late-projector'):
            need(decide(problem) == certificate, 'committed certificate replay')
        count += 1
    need(count == 5, 'complete committed example set')
    return count


def main():
    rng = random.Random(5354)
    monomial, sources = authenticated_sources()
    result = {'status': 'PASS_NATIVE_TENSOR_CUTOFF', 'sources': sources,
              'symmetric_Gram_matrices': gram_checks()}
    result['phase_characters'], result['larger_character_cases'] = character_checks(rng)
    result['native_composition_pairs'], result['literal_native_points'] = group_checks(rng)
    (result['circuits'], result['positive_circuits'], result['negative_circuits'],
     result['literal_dirty_basis_cases']) = circuit_checks(rng)
    result['source_binding'] = source_checks(monomial)
    result['below_rank_projector_basis_cases'], result['central_residue_cases'] = projector_checks()
    result['CNF_formulas'], result['CNF_assignments'], result['unsatisfiable_formulas'] = cnf_checks(rng)
    (result['reversible_branch_pairs'], result['literal_reversible_columns'],
     result['literal_CNF_columns']) = reversible_checks()
    result['rejection_controls'] = rejection_checks()
    result['committed_examples'] = committed_examples()
    result['limits'] = ['No full Clifford/Hadamard theorem', 'Expanded circuit support can be exponential',
                        'No physical supplier, precision, outer admission or new kappa',
                        'No independent human or proof-kernel acceptance']
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
