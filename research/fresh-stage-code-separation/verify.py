"""Check the source data and finite controls for fresh-stage path separation.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def act(columns, x):
    y = 0
    while x:
        bit = x & -x
        y ^= columns[bit.bit_length() - 1]
        x ^= bit
    return y


def transpose(columns):
    return tuple(sum(((c >> j) & 1) << i for i, c in enumerate(columns))
                 for j in range(len(columns)))


def compose(left, right):
    a, b = left
    c, d = right
    return tuple(act(a, x) for x in c), d ^ act(transpose(c), b)


def inverse_orthogonal(operator):
    a, b = operator
    inverse = transpose(a)
    return inverse, act(transpose(inverse), b)


def embed(operator, stage, count):
    columns, beta = operator
    positions = [0] + list(range(1 + 8*stage, 9 + 8*stage))
    def lift(x):
        return sum(((x >> j) & 1) << p for j, p in enumerate(positions))
    out = [1 << j for j in range(1 + 8*count)]
    for p, col in zip(positions, columns):
        out[p] = lift(col)
    return tuple(out), lift(beta)


def signed_apply(operator, x):
    columns, beta = operator
    return act(columns, x), -1 if (beta & x).bit_count() % 2 else 1


# Exact Gaussian numbers are pairs of rational numbers.
def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def q_entries(sign):
    return ((0, (F(1, 2), F(sign, 2))),
            (1, (F(1, 2), F(-sign, 2))))


def n_column(operator, x):
    """Apply Q inverse, M, Q in matrix order Q^-1 M Q."""
    out = defaultdict(lambda: (F(0), F(0)))
    for shift, q in q_entries(1):
        y, s = signed_apply(operator, x ^ shift)
        for back, z in q_entries(-1):
            out[y ^ back] = plus(out[y ^ back], times((s*q[0], s*q[1]), z))
    return {y: z for y, z in out.items() if z != (0, 0)}


def n_entry(operator, y, x):
    return n_column(operator, x).get(y, (F(0), F(0)))


def marker(operator, y, x):
    """Contract an N entry with the literal left Q and right Q inverse."""
    out = (F(0), F(0))
    for a, u in q_entries(1):
        for b, v in q_entries(-1):
            out = plus(out, times(times(u, n_entry(operator, y ^ a, x ^ b)), v))
    return out


def alpha(exponent):
    return (1 - F(-13)**exponent) / 14


def code_power_entry(a, exponent, i, j):
    return alpha(exponent)*a[i][j] + (1-alpha(exponent))*(i == j)


def validate_stages(stages, shared_axes=1):
    need(shared_axes == 1, "The common coordinate space has dimension one")
    need(stages and len(set(stages)) == len(stages), "Each stage has a distinct private block")


def reject(function):
    try:
        function()
    except ValueError:
        return 1
    raise ValueError("A negative control was accepted")


def load():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    objects = {}
    for item in manifest['inputs']:
        raw = (HERE / item['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item['sha256'], 'Pinned source: ' + item['path'])
        if item['path'].endswith('.json'):
            objects[Path(item['path']).name] = json.loads(raw)
    return objects


def source_checks(objects):
    a = [[F(x) for x in row] for row in objects['CODE.json']['A']]
    ports = objects['NORMALIZERS.json']['ports']
    need(len(a) == len(ports) == 112 and all(len(row) == 112 for row in a), '112-owner code')
    need(all(a[i][i] == 0 for i in range(112)), 'Zero code diagonal')
    need(a[0][1] == a[1][0] == F(-1, 2), 'Nonzero alternating witness edge')
    need(len({p['q'] for p in ports}) == 112, 'Distinct port images')
    for i in range(112):
        for j in range(112):
            need(sum(a[i][t]*a[t][j] for t in range(112)) + 12*a[i][j] == 13*(i == j),
                 'Exact code polynomial')
    operators = []
    literal = []
    for index, p in enumerate(ports):
        rows = p['G_rows']
        columns = transpose(rows)
        need(len(columns) == 9 and all(0 <= x < 512 for x in columns), 'Nine-axis map')
        need(all(((x & y).bit_count() % 2) == (i == j)
                 for i, x in enumerate(columns) for j, y in enumerate(columns)), 'Orthogonal map')
        need(p['port'] == index and columns[0] == p['q'], 'Central port image')
        need(p['K_word'] == [['P', rows], ['D', [0]*9,
             [2*((p['Z_mask'] >> j) & 1) for j in range(9)]]], 'Literal signed K word')
        beta = act(transpose(columns), p['Z_mask'])
        operator = columns, beta
        # This second evaluator uses row dot products and the literal output sign.
        table = []
        for x in range(512):
            y = sum(((row & x).bit_count() % 2) << j for j, row in enumerate(rows))
            s = (-1)**((p['Z_mask'] & y).bit_count() % 2)
            need(signed_apply(operator, x) == (y, s), 'Independent signed K action')
            table.append((y, s))
        operators.append(operator)
        literal.append(table)
    for exponent in range(-5, 6):
        if exponent:
            need(alpha(exponent) != 0, 'Nonzero power coefficient')
        # Check the two exact eigenvalues, including negative powers.
        for eigenvalue in (1, -13):
            need(alpha(exponent)*eigenvalue + 1-alpha(exponent) == F(eigenvalue)**exponent,
                 'Power interpolation')
    return a, operators, literal


def path_functions(operators, literal):
    @lru_cache(None)
    def transition(i, j):
        return compose(inverse_orthogonal(operators[i]), operators[j])

    @lru_cache(None)
    def path(owners):
        count = len(owners)-1
        out = tuple(1 << j for j in range(1 + 8*count)), 0
        for stage, (j, i) in enumerate(zip(owners, owners[1:])):
            out = compose(embed(transition(i, j), stage, count), out)
        return out

    inverse_tables = []
    for table in literal:
        inv = [None]*512
        for x, (y, sign) in enumerate(table):
            inv[y] = x, sign
        inverse_tables.append(inv)

    def direct(owners, x):
        sign = 1
        for stage, (j, i) in enumerate(zip(owners, owners[1:])):
            shift = 1 + 8*stage
            local = (x & 1) | (((x >> shift) & 255) << 1)
            y, s = literal[j][local]
            y, t = inverse_tables[i][y]
            x = (x & ~(1 | (255 << shift))) | (y & 1) | ((y >> 1) << shift)
            sign *= s*t
        return x, sign
    return path, direct


def finite_paths(a, path, direct):
    results = []
    total_markers = 0
    for count in (2, 3):
        last = count % 2
        chosen = tuple(j % 2 for j in range(count+1))
        selected = path(chosen)
        maps = set()
        selected_markers = []
        for j in range(1, 1+8*count):
            x, y = 1 << j, selected[0][j]
            selected_markers.append(marker(selected, y, x))
        need(all(z in ((1, 0), (-1, 0)) for z in selected_markers), 'Selected marker coefficient')
        sign_patterns = list(itertools.product((-1, 1), repeat=count))
        active = [0]*len(sign_patterns)
        for middle in itertools.product(range(112), repeat=count-1):
            owners = (0,) + middle + (last,)
            op = path(owners)
            need(op[0] not in maps, 'Distinct complete binary path maps')
            maps.add(op[0])
            # All private columns determine an orthogonal address map.
            if owners != chosen:
                different = next((j for j in range(1, len(op[0])) if op[0][j] != selected[0][j]), None)
                need(different is not None, 'Private-column separation')
                need(marker(op, selected[0][different], 1 << different) == (0, 0),
                     'A literal four-term marker kills this path')
                total_markers += 1
            # Every basis column has a separately evaluated literal source action.
            for j, y in enumerate(op[0]):
                need(direct(owners, 1 << j) == (y, (-1)**((op[1] >> j) & 1)),
                     'Literal path and composed map agree')
            for position, signs in enumerate(sign_patterns):
                if all(code_power_entry(a, s, i, j) for s, j, i in zip(signs, owners, owners[1:])):
                    active[position] += 1
        need(selected[0][0] != 1, 'Selected path moves the central vector')
        for x in (0, 1, 3, (1 << (8*count+1))-1):
            need(len(n_column(selected, x)) == 4, 'Four nonzero conjugated entries')
        results.append(dict(stages=count, all_paths=len(maps), signs=[list(s) for s in sign_patterns],
                            active_paths=active, marker_columns=8*count))
    return results, total_markers


def marker_path_count(a, operators, literal, path, count, inputs, reverse=False):
    """Count every path that survives the marker columns, without path expansion."""
    owners = tuple(j % 2 for j in range(count+1))
    selected = path(owners)
    outputs = [act(selected[0], x) for x in inputs]
    to_mask = lambda xs: sum((x & 1) << j for j, x in enumerate(xs))
    initial = (count % 2, to_mask(outputs)) if reverse else (0, to_mask(inputs))
    final = (0, to_mask(inputs)) if reverse else (count % 2, to_mask(outputs))
    state, peak = {initial: 1}, 1
    tables = [[y for y, sign in table] for table in literal]
    inverses = [[0]*512 for _ in range(112)]
    for i, table in enumerate(tables):
        for x, y in enumerate(table):
            inverses[i][y] = x
    stages = range(count-1, -1, -1) if reverse else range(count)
    for stage in stages:
        shift = 8*stage+1
        incoming = [(x >> shift) & 255 for x in (outputs if reverse else inputs)]
        outgoing = [(x >> shift) & 255 for x in (inputs if reverse else outputs)]
        next_state = defaultdict(int)
        for (owner, central), multiplicity in state.items():
            local = [(v << 1) | ((central >> j) & 1) for j, v in enumerate(incoming)]
            for other in range(112):
                coefficient = a[owner][other] if reverse else a[other][owner]
                if other != owner and not coefficient:
                    continue
                if reverse:
                    # Separate matrix composition, in the reverse direction.
                    op = compose(inverse_orthogonal(operators[other]), operators[owner])
                    images = [act(op[0], x) for x in local]
                else:
                    images = [inverses[other][tables[owner][x]] for x in local]
                if all(y >> 1 == target for y, target in zip(images, outgoing)):
                    next_state[other, to_mask(images)] += multiplicity
        state = next_state
        peak = max(peak, len(state))
    return state.get(final, 0), peak


def short_markers(a, operators, literal, path):
    saved = json.loads((HERE/'MARKERS.json').read_bytes())
    result = []
    for row in saved['candidates']:
        count, inputs = row['stages'], row['markers']
        need(all(type(x) is int and 0 <= x < 1 << (8*count+1) for x in inputs),
             'Marker address domain')
        forward, peak = marker_path_count(a, operators, literal, path, count, inputs)
        backward, _ = marker_path_count(a, operators, literal, path, count, inputs, True)
        need(forward == backward == row['count'] == 1 and peak == row['peak'],
             'Exactly one path survives in both dynamic programs')
        selected = path(tuple(j % 2 for j in range(count+1)))
        for x in inputs:
            need(marker(selected, act(selected[0], x), x) in ((1, 0), (-1, 0)),
                 'Every selected short marker is nonzero')
        result.append(dict(stages=count, markers=len(inputs), paths=forward,
                           maximum_states=peak, add_offset=3*len(inputs)))
    need(marker_path_count(a, operators, literal, path, 2, [])[0] > 1,
         'An empty marker set does not isolate a path')
    return result


def bank_checks(objects, a, path, direct, short):
    banks = []
    for bank in objects['GAUGE.json']['typed_caller']['endpoint']:
        if bank['central_exponent'] != -1:
            continue
        word = bank['code_word_left_to_right']
        stages = [s for s, e in word]
        validate_stages(stages)
        need(bank['operator'] == 'Q^-1 B D' and stages == bank['gaussian_stages'], 'Actual terminal type')
        count = len(word)
        owners = tuple(j % 2 for j in range(count+1))
        op = path(owners)
        need(op[0][0] != 1, 'Actual-bank witness has four-point support')
        for j, y in enumerate(op[0]):
            need(direct(owners, 1 << j) == (y, (-1)**((op[1] >> j) & 1)), 'Actual-bank literal path')
        powers = [-e for s, e in word]
        coefficient = F(1)
        for exponent in powers:
            coefficient *= alpha(exponent)*a[0][1]
        need(coefficient != 0, 'Inverse decoder retains the selected path')
        banks.append(dict(role=bank['role'], stages=count, source_word=word,
                          decoder_execution_powers=powers, marker_columns=next(r['markers'] for r in short if r['stages'] == count),
                          add_lower_bound=f"max(0, 2*f - {next(r['add_offset'] for r in short if r['stages'] == count)})",
                          selected_path_coefficient=str(coefficient)))
    need([b['role'] for b in banks] == list(range(16)), 'All sixteen negative banks')
    return banks


def boundary_checks(a, path):
    controls = 0
    controls += reject(lambda: validate_stages([0, 0]))
    controls += reject(lambda: validate_stages([0, 1], 2))
    controls += reject(lambda: validate_stages([]))
    # Reusing one block gives C*C^-1=I. These scalar identities bind the full
    # monomial blocks because K_i^-1 K_t K_t^-1 K_j = K_i^-1 K_j.
    for i in range(112):
        for j in range(112):
            value = sum(a[i][t]*(a[t][j]+12*(t == j))/13 for t in range(112))
            need(value == (i == j), 'Repeated-stage inverse cancellation')
    # With two common axes, nonidentity gauges can pass between fresh blocks.
    def permutation(images):
        return tuple(1 << j for j in images), 0
    h = permutation([1, 0, 2, 3])
    left = permutation([3, 1, 2, 0])
    right = permutation([2, 1, 0, 3])
    left2, right2 = compose(left, h), compose(h, right)
    need(left != left2 and right != right2, 'Different local factors')
    need(compose(left, right) == compose(left2, right2), 'Two-center factor collision')
    # The actual owner coefficients 2 and 98 have opposite signs. With
    # two shared axes, this change makes their complete monomials equal.
    need(a[0][2]*a[2][1] == -a[0][98]*a[98][1] == F(1, 4),
         'Actual owner coefficients cancel on the changed two-center paths')
    need(compose(left, right)[0][0] != 1, 'Each cancelling term is nonmonomial after Q')
    need(len({1, left[0][0], left2[0][0]}) == 3
         and len({1, right[0][0], inverse_orthogonal(right2)[0][0]}) == 3,
         'The specified port images remain distinct in each changed stage')
    common = compose(left, right)
    other = compose(left2, right2)
    for x in range(16):
        need(n_column(common, x) == n_column(other, x) and len(n_column(common, x)) == 4,
             'The two cancelling terms agree with exact phases at every base input')
    # A wrong Q orientation fails the literal contraction even on a diagonal term.
    op = path((0, 1))
    x, y = 0, 0
    correct = marker(op, y, x)
    wrong = (F(0), F(0))
    for u, cu in q_entries(-1):
        for v, cv in q_entries(-1):
            wrong = plus(wrong, times(times(cu, n_entry(op, y ^ u, x ^ v)), cv))
    need(correct != wrong, 'Wrong marker orientation changes an actual entry')
    controls += 1
    need(alpha(-1) == F(1, 13) and alpha(2) == -12, 'Inverse and square coefficients')
    need(F(1, 4) != F(1, 4)**2, 'Owner coefficients are not tensor powered')
    controls += 1
    return dict(rejection_controls=controls, repeated_stage_inverse=True,
                two_common_axes_collision=True)


def run():
    objects = load()
    a, operators, literal = source_checks(objects)
    path, direct = path_functions(operators, literal)
    census, markers = finite_paths(a, path, direct)
    short = short_markers(a, operators, literal, path)
    banks = bank_checks(objects, a, path, direct, short)
    boundary = boundary_checks(a, path)
    # The written induction has no stage-count bound. These longer paths are controls.
    longer = []
    for count in (1, 4, 8, 16, 19, 32, 64):
        owners = tuple(j % 2 for j in range(count+1))
        op = path(owners)
        need(op[0][0] != 1, 'Long path preserves an earlier private component')
        for x in (0, 1, 3, 1 << (8*count)):
            need(signed_apply(op, x) == direct(owners, x), 'Long literal path check')
            need(len(n_column(op, x)) == 4, 'Long path four-point support')
        longer.append(count)
    return dict(status='PASS_ALL_LENGTH_FRESH_STAGE_SEPARATION_NO_NEW_KAPPA',
                scope='Every nonempty product of distinct fresh stages with nonzero integer powers',
                owner_count=112, normalizer_entries=112*512, code_polynomial_entries=112*112,
                complete_path_censuses=census, literal_killing_markers=markers,
                negative_banks=banks, short_marker_certificates=short,
                long_path_stage_counts=longer, controls=boundary,
                theorem_add_lower_bound='g >= max(0, 2*f - 24*k)',
                selected_kappa_unchanged='0.0030217758')


def main():
    need(sys.argv[1:] in ([], ['--write']), 'Use no arguments or --write')
    result = run()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    destination = HERE/'RESULT.json'
    if sys.argv[1:]:
        need(not destination.exists(), 'Refuse to overwrite the result')
        destination.write_text(encoded)
    else:
        need(destination.read_text() == encoded, 'Exact recorded result')
    print(result['status'])
    print(json.dumps(dict(paths=sum(c['all_paths'] for c in result['complete_path_censuses']),
                          markers=result['literal_killing_markers'], banks=len(result['negative_banks']))))


if __name__ == '__main__':
    main()
