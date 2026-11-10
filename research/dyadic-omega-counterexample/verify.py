#!/usr/bin/env python3
"""Exact backward free-algebra replay for the dyadic Omega counterexample.

@CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
The word/model and fixed Omega profile retain #628/#2177/#2735 credit.
No predecessor verifier or profile engine is imported.
"""
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    count = 0
    for entry in manifest['files']:
        if entry['usage'] != 'input':
            continue
        raw = (ROOT / entry['path']).read_bytes()
        need(sha256(raw).hexdigest() == entry['sha256'], 'input SHA256: ' + entry['path'])
        import hashlib
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == entry['git_blob'], 'input Git blob: ' + entry['path'])
        count += 1
    return count


def word(n, sign=1, x=0, y=1, depth=2, offset=0, bad_inverse=False):
    """Explicit signed-phase recursion; base event is (source,target,factor,sign)."""
    if n == 1:
        return [(x, y, offset, sign)]
    b = n // 2
    u = lambda s: word(b, s, x, depth, depth + 1, offset, bad_inverse)
    v = lambda s: word(n - b, s, depth, y, depth + 1, offset + b, bad_inverse)
    if sign == 1:
        return u(1) + v(1) + u(-1) + v(-1)
    if bad_inverse:
        return u(-1) + v(-1) + u(1) + v(1)
    return v(1) + u(1) + v(-1) + u(-1)


def source_word_check():
    """Authenticate first, then extract only the pinned, inspected gen definition."""
    path = ROOT / 'research/leaf-destination-transport-bound/check2.py'
    tree = ast.parse(path.read_text(), filename=str(path))
    definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'gen']
    need(len(definitions) == 1, 'unique source gen')
    module = ast.fix_missing_locations(ast.Module(body=definitions, type_ignores=[]))
    namespace = {}
    exec(compile(module, str(path), 'exec'), namespace)
    cases = 0
    for n in list(range(1, 66)) + [128, 256]:
        for sign in (1, -1):
            expected = [event for event, _ in namespace['gen'](n, sign)]
            need(word(n, sign) == expected, 'literal source order ' + str((n, sign)))
            cases += 1
    return cases


def channels(events, cut, register):
    """One reverse row sweep. Each returned dictionary is a separate leaf error."""
    need(type(cut) is int and 0 <= cut <= len(events), 'cut domain')
    row = {register: {(): 1}}
    result = [{} for _ in range(cut)]
    for j in range(cut - 1, -1, -1):
        x, y, factor, sign = events[j]
        need(x != y and sign in (-1, 1), 'legal leaf')
        source = row.get(y, {})
        result[j] = dict(source)  # error is added AFTER this leaf
        target = row.setdefault(x, {})
        for monomial, coefficient in source.items():
            mon = monomial + (factor,)
            value = target.get(mon, 0) + sign * coefficient
            if value:
                target[mon] = value
            else:
                target.pop(mon, None)
    return result


def profile(ch):
    return Counter(sum(abs(c) for c in p.values()) for p in ch if p)


def mass(p):
    return sum(j * count for j, count in p.items())


def digest(ch):
    """SHA256 of JSON [[leaf, [[word-list, signed-coefficient],...]],...].

    Include empty channels; sort words lexicographically; separators ',',':'.
    This convention is reproduced independently by forward_check.py.
    """
    rows = [[i, [[list(w), p[w]] for w in sorted(p)]] for i, p in enumerate(ch)]
    return sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()


def add(*items):
    out = Counter()
    for multiplier, p in items:
        for j, count in p.items():
            out[j] += multiplier * count
    return Counter({j: c for j, c in out.items() if c})


def shift(p, amount):
    return Counter({j + amount: c for j, c in p.items()})


def recurrences(limit):
    """Equations (3),(4),(6),(7),(10), with the credited Omega recurrence."""
    G = [Counter({1: 1})]
    H = [Counter({1: 1})]
    J = [Counter()]
    Y = [Counter({1: 1})]
    Z = [Counter()]
    A = [None, Counter({1: 1})]  # #2735 complementary scratch readouts
    B = [None, Counter({1: 1})]
    R, O = {}, {}
    for h in range(1, limit + 1):
        G.append(add((4, G[-1]), (1, shift(H[-1], 1)), (-1, H[-1])))
        H.append(add((2, H[-1]), (1, shift(H[-1], 1))))
        J.append(add((1, G[h]), (1, shift(H[h], -1)), (-1, H[h]),
                     (-2**h, Counter({0: 1}))))
        Y.append(add((1, Y[-1]), (1, G[h - 1])))
        Z.append(add((1, Y[h - 1]), (2, Z[-1]), (1, J[h - 1])))
        for p in (G[h], H[h], J[h], Y[h], Z[h]):
            need(all(j >= 1 and c > 0 for j, c in p.items()), 'nonzero profile coefficients')
        if h >= 2:
            A.append(add((1, A[-1]), (1, G[h - 1])))
            B.append(add((1, G[h - 1]), (1, A[h - 1]), (2, B[-1])))
            O[h] = add((2, G[h - 1]), (1, A[h - 1]), (2, B[h - 1]))
            k = h - 2
            R[h] = add((2, G[k + 1]), (3, Y[k]), (4, Z[k]), (4, J[k]))
    return G, H, J, Y, Z, R, O


def old_cut(h):
    return (11 * 4**(h - 1) - 2) // 3


def new_cut(h):
    return 4**h - (4**(h - 2) + 2) // 3


def K(h):
    numerator = 47 * 4**h - 68 * 3**h + 48 * 2**h - 20
    need(numerator % 24 == 0, 'K integrality')
    return numerator // 24


def Omega(h):
    numerator = 11 * 4**h - 11 * 3**h + 1
    need(numerator % 6 == 0, 'Omega integrality')
    return numerator // 6


def family_mass(h, m):
    need(type(h) is int and type(m) is int and 1 <= m < h, 'family domain')
    k = h - m - 1
    num = ((48 * 4**m - 4) * 4**k
           + (-36 * 4**m - 24 * 2**m + 12 * 3**m + 3) * 3**k
           + 24 * 2**(m + k) - 5)
    need(num % 6 == 0, 'general family integrality')
    return num // 6


def family_from_wrappers(k, m):
    # A separate integer recurrence evaluation of equations (13),(14).
    a = (4 * 4**k - 3 * 3**k + 5) // 6
    b = (8 * 4**k - 15 * 3**k + 12 * 2**k - 5) // 6
    d = 2 * (4**k - 3**k)
    for j in range(1, m + 1):
        b, d = a + 2 * b + 2 * d, 4 * d + (2 * 3**k if j == 1 else 0)
    return a + 2 * b + 2 * (3**(k + m) + d)


def witness_record(ch, cut, register):
    p = profile(ch)
    return {'completed_leaves': cut, 'register': register,
            'profile': {str(j): p[j] for j in sorted(p)},
            'nonzero_channels': sum(p.values()), 'total_mass': mass(p),
            'channel_polynomials_sha256': digest(ch)}


def first_win(p, q):
    left = sorted([j for j, c in p.items() for _ in range(c)], reverse=True)
    right = sorted([j for j, c in q.items() for _ in range(c)], reverse=True)
    a = b = 0
    for i in range(max(len(left), len(right))):
        a += left[i] if i < len(left) else 0
        b += right[i] if i < len(right) else 0
        if a > b:
            return {'budget': i + 1, 'new_mass': a, 'omega_mass': b}
    return None


def make_witness():
    events = word(128)
    ch = channels(events, new_cut(7), 3)
    old = channels(events, old_cut(7), 8)
    return {'schema_version': 1, 'factor_count': 128, 'height': 7,
            'word_leaves': len(events), 'orientation': 1,
            'new': witness_record(ch, new_cut(7), 3),
            'omega': witness_record(old, old_cut(7), 8),
            'strict_excess': mass(profile(ch)) - mass(profile(old)),
            'first_strict_win': first_win(profile(ch), profile(old))}


def reject(call, label):
    try:
        call()
    except (ValueError, KeyError):
        return label
    raise ValueError('negative control unexpectedly passed: ' + label)


def same_json(a, b):
    need(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), 'exact typed receipt mismatch')


def checks():
    authenticated = authenticate()
    source_cases = source_word_check()
    G, H, J, Y, Z, R, O = recurrences(100)
    literal_cases = 0
    for h in range(0, 9):
        plus, minus = word(2**h), word(2**h, -1)
        p = (4**h + 2) // 3
        for got, expected in [(channels(plus, p, 1), Y[h]),
                              (channels(minus, 4**h - p, 1), Z[h])]:
            need(profile(got) == expected, 'target-prefix recurrence ' + str(h))
            literal_cases += 1
        if h >= 2:
            for cut, register, expected in [(new_cut(h), 3, R[h]),
                                            (old_cut(h), h + 1, O[h])]:
                need(profile(channels(plus, cut, register)) == expected,
                     'full profile recurrence ' + str((h, cut, register)))
                literal_cases += 1
    family_literal = 0
    for h in range(2, 9):
        events = word(2**h)
        for m in range(1, h):
            k = h - m - 1
            cut = 4**h - (4**k + 2) // 3
            actual = mass(profile(channels(events, cut, m + 2)))
            need(actual == family_mass(h, m), 'general family literal ' + str((h, m)))
            family_literal += 1
    for h in range(2, 101):
        for m in range(1, h):
            k = h - m - 1
            need(family_mass(h, m) == family_from_wrappers(k, m), 'closed family / wrapper recurrence')
            need(family_mass(h, m) <= 2 * (4**h - 3**h), 'scratch upper envelope')
    for h in range(101):
        need(mass(G[h]) == 2 * 4**h - 3**h, 'exit mass')
        need(mass(J[h]) == 2 * (4**h - 3**h), 'scratch mass')
        need(6 * mass(Y[h]) == 4 * 4**h - 3 * 3**h + 5, 'Y closed form')
        need(6 * mass(Z[h]) == 8 * 4**h - 15 * 3**h + 12 * 2**h - 5, 'Z closed form')
        if h >= 2:
            need(mass(R[h]) == K(h) and mass(O[h]) == Omega(h), 'total closed forms')
            need((K(h) > Omega(h)) == (h >= 7), 'family crossing')
    witness = make_witness()
    same_json(witness, json.loads((HERE / 'WITNESS.json').read_text()))
    need(witness['first_strict_win'] == {'budget': 15479, 'new_mass': 26029, 'omega_mass': 26028},
         'first winning error budget')
    controls = []
    controls.append(reject(lambda: need(K(7) <= Omega(7), 'C1 total bound'), 'C1_total_bound'))
    # Omega still wins at a smaller budget: do not claim the new cut is universal.
    new_29 = sum(sorted([j for j, c in R[7].items() for _ in range(c)], reverse=True)[:29])
    old_29 = sum(sorted([j for j, c in O[7].items() for _ in range(c)], reverse=True)[:29])
    need((new_29, old_29) == (175, 176), 'opposite budget comparison')
    controls.append(reject(lambda: need(new_29 >= old_29, 'new universal cut'),
                           'new_cut_does_not_dominate_all_budgets'))
    controls.append(reject(lambda: need(K(6) > Omega(6), 'premature family threshold'),
                           'height_six_is_not_a_counterexample_of_this_family'))
    normal = word(8)
    expected = R[3]
    bad = word(8, bad_inverse=True)
    controls.append(reject(lambda: need(profile(channels(bad, new_cut(3), 3)) == expected,
                                       'bad inverse profile'), 'wrong_inverse_order'))
    dropped = normal[:-len(normal) // 4]
    controls.append(reject(lambda: channels(dropped, new_cut(3), 3), 'missing_restoration_phase'))
    controls.append(reject(lambda: need(profile(channels(normal, len(normal), 3)) == expected,
                                       'endpoint profile'), 'completed_endpoint_instead_of_interior_cut'))
    controls.append(reject(lambda: need(profile(channels(normal, new_cut(3), 1)) == expected,
                                       'wrong register profile'), 'wrong_readout_register'))
    # A top-U injection and its top-U' inverse mate have identical channels here.
    h = 3
    ch = channels(normal, new_cut(h), 3)
    block = 4**(h - 1)
    pairs = [(i, 3 * block - 1 - i) for i in range(block)
             if ch[i] and ch[i] == ch[3 * block - 1 - i]]
    need(bool(pairs), 'nonzero paired channel control')
    i, j = pairs[0]
    independent = 2 * sum(abs(c) for c in ch[i].values())
    merged = {w: ch[i].get(w, 0) - ch[j].get(w, 0) for w in ch[i] | ch[j]}
    need(independent > 0 and sum(abs(c) for c in merged.values()) == 0,
         'independent versus shared opposite errors')
    controls.append('shared_opposite_errors_cannot_replace_independent_symbols')
    mutated = json.loads(json.dumps(witness)); mutated['new']['total_mass'] -= 1
    controls.append(reject(lambda: same_json(witness, mutated), 'understated_receipt'))
    mutated = json.loads(json.dumps(witness)); mutated['schema_version'] = True
    controls.append(reject(lambda: same_json(witness, mutated), 'boolean_integer_receipt'))
    return {'status': 'PASS_DYADIC_OMEGA_COUNTEREXAMPLE', 'source_inputs': authenticated,
            'source_word_comparisons': source_cases, 'literal_profile_comparisons': literal_cases,
            'recurrence_heights': [0, 100], 'general_family_literal_cases': family_literal,
            'general_family_integer_cases': 4950, 'negative_controls': controls,
            'new_mass': K(7), 'omega_mass': Omega(7), 'strict_excess': K(7) - Omega(7)}


if __name__ == '__main__':
    print(json.dumps(checks(), sort_keys=True, indent=2))
