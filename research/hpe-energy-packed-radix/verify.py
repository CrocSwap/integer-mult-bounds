"""Exact energy-ball packing checks and source-bound HPE fixtures; Apache-2.0.

Arham Tahir with substantial OpenAI Codex assistance. No new Lean theorem.
Only the retained closed literal parser is reused, not its gate interpreter.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 512
ZERO = (0, 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, 'duplicate JSON key: ' + key)
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def energy(values):
    return sum(a*a + b*b for a, b in values)


def pack(values, base):
    a = b = 0
    for x, y in reversed(values):
        a, b = base*a + x, base*b + y
    return a, b


def admissible_radix(radius, base):
    require(type(radius) is int and radius >= 1, 'positive integer radius')
    require(type(base) is int and base >= 2*radius, 'energy-ball radix requires B >= 2R')


def integer_ball(dimensions, remaining):
    """Every ordered integer vector of the given dimension and squared norm cap."""
    if dimensions == 0:
        yield ()
        return
    bound = math.isqrt(remaining)
    for value in range(-bound, bound+1):
        for tail in integer_ball(dimensions-1, remaining-value*value):
            yield (value,) + tail


def gaussian_ball(length, squared_radius):
    for values in integer_ball(2*length, squared_radius):
        yield tuple(zip(values[::2], values[1::2]))


def ball_checks():
    cases = []
    total = 0
    for radius in (1, 2, 3):
        for length in (1, 2, 3):
            seen = {}
            for values in gaussian_ball(length, radius*radius):
                code = pack(values, 2*radius)
                require(code not in seen, 'energy-ball collision at the proved boundary')
                seen[code] = values
            total += len(seen)
            cases.append({'radius': radius, 'complex_length': length, 'vectors': len(seen)})
    # Nonzero kernel vectors have squared norm at least B^2+1. Check all
    # vectors of norm squared <= B^2 and the attaining two-digit relation.
    kernel_vectors = 0
    for base in range(2, 7):
        for values in gaussian_ball(2, base*base):
            if any(v != ZERO for v in values):
                require(pack(values, base) != ZERO, 'shorter packing-kernel vector')
            kernel_vectors += 1
        relation = ((base, 0), (-1, 0))
        require(pack(relation, base) == ZERO and energy(relation) == base*base+1,
                'sharp kernel relation')
    unsafe = 0
    for radius in range(1, 33):
        for base in range(1, 2*radius):
            u = (((base+1)//2, 0), ZERO)
            v = ((-(base//2), 0), (1, 0))
            require(u != v and max(energy(u), energy(v)) <= radius*radius,
                    'unsafe witness must satisfy both energy bounds')
            require(pack(u, base) == pack(v, base), 'unsafe integer-radix witness')
            ui = tuple((-b, a) for a, b in u)
            vi = tuple((-b, a) for a, b in v)
            require(pack(ui, base) == pack(vi, base) and ui != vi, 'imaginary witness')
            try:
                admissible_radix(radius, base)
            except ValueError:
                unsafe += 1
            else:
                raise ValueError('unsafe radix admitted')
    # The componentwise bound |digit| <= B alone permits (B,-1), while
    # the energy hypothesis excludes it by exactly one squared unit.
    relation = ((2, 0), (-1, 0))
    require(pack(relation, 2) == ZERO and max(abs(a) for a, _ in relation) <= 2
            and energy(relation) == 5, 'component-only false inference')
    # Each column has energy <= 1, but a row does not. This defeats substituting
    # column bounds for row bounds in the packed operator implication.
    first = [((1, 0), ZERO), (ZERO, ZERO)]
    second = [((-1, 0), (1, 0)), (ZERO, ZERO)]
    require([pack(row, 2) for row in first] == [pack(row, 2) for row in second],
            'column-only false equality')
    require(all(sum(row[j][0]**2+row[j][1]**2 for row in matrix) <= 1
                for matrix in (first, second) for j in (0, 1)), 'column-only premises')
    require(energy(second[0]) == 2, 'row bound is the missing premise')
    return {'gaussian_balls': cases, 'vectors': total, 'short_kernel_vectors_checked': kernel_vectors,
            'unsafe_integer_radices': unsafe,
            'controls': ['adjacent_and_smaller_radix_collisions', 'imaginary_collisions',
                         'component_bounds_do_not_replace_energy',
                         'column_bounds_do_not_replace_row_bounds', 'strict_kernel_energy_gap']}


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def binary_map(rows, address):
    return sum(((row & address).bit_count() & 1) << bit for bit, row in enumerate(rows))


def diagonal_phase(q, alpha, address):
    active = [j for j in range(9) if address & (1 << j)]
    return (sum(alpha[j] for j in active)
            + 2*sum((q[j] >> k) & 1 for j in active for k in active if j < k)) % 4


def compile_circuit(gates):
    """Validate a closed grammar; compile permutations as forward scatter maps."""
    operations = []
    count = 0
    for gate in gates:
        require(isinstance(gate, list) and gate, 'nonempty literal gate')
        tag = gate[0]
        if tag == 'pm':
            require(len(gate) == 3 and all(isinstance(v, list) and len(v) == 9 for v in gate[1:]),
                    'permutation shape')
            require(all(type(v) is int and 0 <= v < N for row in gate[1:] for v in row),
                    'permutation masks')
            forward = tuple(binary_map(gate[1], j) for j in range(N))
            inverse = tuple(binary_map(gate[2], j) for j in range(N))
            require(all(forward[inverse[j]] == inverse[forward[j]] == j for j in range(N)),
                    'unitary permutation/inverse')
            operations.append(('P', forward))
        elif tag == 'dg':
            require(len(gate) == 3 and all(isinstance(v, list) and len(v) == 9 for v in gate[1:]),
                    'diagonal shape')
            require(all(type(v) is int and v >= 0 for row in gate[1:] for v in row), 'diagonal integers')
            operations.append(('D', tuple(diagonal_phase(gate[1], gate[2], j) for j in range(N))))
        elif tag in ('xg', 'cg'):
            require(len(gate) == (2 if tag == 'xg' else 3), 'X/C shape')
            require(type(gate[1]) is int and 0 <= gate[1] < N, 'involutive XOR domain')
            if tag == 'cg':
                require(type(gate[2]) is bool, 'C sign')
                operations.append(('C', (gate[1], 1 if gate[2] else -1)))
                count += 1
            else:
                operations.append(('X', gate[1]))
        elif tag == 'ph':
            require(len(gate) == 2 and type(gate[1]) is int and gate[1] >= 0, 'global phase')
            operations.append(('F', gate[1] % 4))
        else:
            raise ValueError('unknown literal gate')
    return operations, count


def execute(compiled, values):
    values = list(values)
    require(len(values) == N, 'vector length')
    for tag, data in compiled[0]:
        if tag == 'P':
            result = [ZERO]*N
            for address, value in enumerate(values):
                result[data[address]] = value
            values = result
        elif tag == 'D':
            values = [rotate(v, p) for v, p in zip(values, data)]
        elif tag == 'F':
            values = [rotate(v, data) for v in values]
        elif tag == 'X':
            values = [values[j ^ data] for j in range(N)]
        else:
            mask, sign = data
            if mask == 0:
                values = [(2*a, 2*b) for a, b in values]
                continue
            result = [ZERO]*N
            for j in range(N):
                k = j ^ mask
                if j > k:
                    continue
                a, b = values[j]
                c, d = values[k]
                real, imag = a+c, b+d
                dr, di = -sign*(b-d), sign*(a-c)
                result[j], result[k] = (real+dr, imag+di), (real-dr, imag-di)
            values = result
    return values


def adjoint(gates):
    out = []
    for gate in reversed(gates):
        tag = gate[0]
        if tag == 'pm':
            out.append([tag, gate[2], gate[1]])
        elif tag == 'dg':
            out.append([tag, gate[1], [(-v) % 4 for v in gate[2]]])
        elif tag == 'cg':
            out.append([tag, gate[1], not gate[2]])
        elif tag == 'ph':
            out.append([tag, (-gate[1]) % 4])
        else:
            out.append(list(gate))
    return out


def direct_execute(gates, values):
    """Second gate oracle: direct source pullback and pointwise C formula."""
    values = list(values)
    for gate in gates:
        tag = gate[0]
        if tag == 'pm':
            values = [values[binary_map(gate[2], j)] for j in range(N)]
        elif tag == 'dg':
            values = [rotate(v, diagonal_phase(gate[1], gate[2], j)) for j, v in enumerate(values)]
        elif tag == 'ph':
            values = [rotate(v, gate[1]) for v in values]
        elif tag == 'xg':
            values = [values[j ^ gate[1]] for j in range(N)]
        else:
            sign = 1 if gate[2] else -1
            result = []
            for j, (a, b) in enumerate(values):
                c, d = values[j ^ gate[1]]
                result.append((a-sign*b+c+sign*d, b+sign*a+d-sign*c))
            values = result
    return values


def packed_equal(left, right, bits):
    kl, kr = left[1], right[1]
    common = max(kl, kr)
    require(type(bits) is int and bits >= 1, 'positive radix bits')
    admissible_radix(1 << common, 1 << bits)
    initial = [(1 << (bits*j), 0) for j in range(N)]
    a, b = execute(left, initial), execute(right, initial)
    return all((x[0] << (common-kl), x[1] << (common-kl))
               == (y[0] << (common-kr), y[1] << (common-kr)) for x, y in zip(a, b))


def source_checks():
    pins = {}
    for row in read_json(HERE/'SOURCES.json')['files']:
        if row['usage'] == 'input':
            actual = hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
            require(actual == row['sha256'], 'source drift: ' + row['path'])
            pins[row['path']] = actual
    parser_path = ROOT/'research/hpe-lean-semantic-binding/verify.py'
    spec = importlib.util.spec_from_file_location('retained_literal_parser', parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    _, circuits = parser.literal_data((ROOT/'research/hyperplane-end-lean/HyperplaneEnd/Exact.lean').read_text(encoding='utf-8'))
    pairs, controls = [], []
    row_count = oracle_count = 0
    for index in (1, 2, 3):
        lhs, rhs = circuits[f'lhsLit{index}'], circuits[f'rhsLit{index}']
        left, right = compile_circuit(lhs), compile_circuit(rhs)
        kl, kr = left[1], right[1]
        common = max(kl, kr)
        require(packed_equal(left, right, common+1), 'energy-radix exact source equality')
        require(packed_equal(left, right, common+2), 'PR1859 sufficient radix')
        require(packed_equal(left, right, 2*common+2), 'retained coarse radix')
        la, ra = compile_circuit(adjoint(lhs)), compile_circuit(adjoint(rhs))
        digest = hashlib.sha256()
        sample_left, sample_right = {}, {}
        for address in range(N):
            basis = [ZERO]*N
            basis[address] = (1, 0)
            # Conjugate adjoint columns to obtain forward rows, the coefficients
            # relevant to packing input coordinates. Column bounds alone fail.
            a = [(x << (common-kl), (-y) << (common-kl)) for x, y in execute(la, basis)]
            b = [(x << (common-kr), (-y) << (common-kr)) for x, y in execute(ra, basis)]
            require(a == b and energy(a) == energy(b) == 4**common, 'complete scaled row/energy')
            digest.update((canonical(a)+'\n').encode())
            if address in (0, 1, 255, 511):
                sample_left[address], sample_right[address] = a, b
            row_count += 2
        for gates, compiled, sample_rows in ((lhs, left, sample_left), (rhs, right, sample_right)):
            fixtures = []
            for address in (0, 1, 255, 511):
                basis = [ZERO]*N
                basis[address] = (1, 0)
                fixtures.append((address, basis))
            fixtures.append((None, [((7*j % 11)-5, (3*j % 7)-3) for j in range(N)]))
            for address, initial in fixtures:
                actual = execute(compiled, initial)
                require(actual == direct_execute(gates, initial), 'separate gate oracle')
                if address is not None:
                    scale = common-compiled[1]
                    require(all((actual[j][0] << scale, actual[j][1] << scale) == row[address]
                                for j, row in sample_rows.items()), 'adjoint/forward transpose binding')
                oracle_count += 1
        phase = compile_circuit(rhs + [['ph', 1]])
        character = compile_circuit([['dg', [0]*9, [2]+[0]*8]] + rhs)
        require(not packed_equal(left, phase, common+1), 'global phase must be retained')
        require(not packed_equal(left, character, common+1), 'input character must be retained')
        initial = [(1 << ((common+1)*j), 0) for j in range(N)]
        require(execute(left, initial) != execute(right, initial), 'omitted normalization')
        try:
            packed_equal(left, right, common)
        except ValueError:
            pass
        else:
            raise ValueError('unsupported radix admitted')
        controls.extend([f'pair{index}_phase', f'pair{index}_input_character',
                         f'pair{index}_omitted_scale', f'pair{index}_undersized_radix'])
        pairs.append({'pair': index, 'C_left': kl, 'C_right': kr, 'radius': 1 << common,
                      'radix_bits': common+1, 'previous_unitary_radix_bits': common+2,
                      'original_radix_bits': 2*common+2,
                      'largest_input_bits': (common+1)*(N-1)+1,
                      'scaled_row_sha256': digest.hexdigest(), 'row_squared_energy': 4**common})
    bad = [['pm', [0]*9, [1 << j for j in range(9)]]]
    for label, gates in (('nonunitary_permutation', bad), ('out_of_domain_X', [['xg', N]]),
                         ('nonboolean_C_sign', [['cg', 1, 1]])):
        try:
            compile_circuit(gates)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError(label+' accepted')
    return {'pairs': pairs, 'scaled_rows_checked': row_count, 'separate_oracle_executions': oracle_count,
            'controls': controls, 'input_sha256': pins}


def run():
    source = source_checks()
    balls = ball_checks()
    return {'status': 'PASS_HPE_ENERGY_PACKED_RADIX', 'source': source, 'energy_balls': balls,
            'new_lean_proof': False, 'selected_checker_changed': False, 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='Explicit output receipt path; normal replay is read-only')
    args = parser.parse_args()
    result = run()
    if args.write:
        args.write.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    else:
        require(canonical(result) == canonical(read_json(HERE/'RESULT.json')), 'receipt mismatch')
    print(result['status'], 'rows='+str(result['source']['scaled_rows_checked']),
          'ball_vectors='+str(result['energy_balls']['vectors']))


if __name__ == '__main__':
    main()
