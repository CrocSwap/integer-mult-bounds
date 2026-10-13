"""Generate, solve, and independently replay the bounded quadratic family."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import numpy as np
from model import ROOT, require, feature_neighbors, encode_rows, rank_rows, inverse, array_hash


def prepare(state, first, second):
    features = state['q']
    selected = list(feature_neighbors(first, second, features, state['adjacency']))
    within = first == second
    variables = 3003 if within else 5929
    count = sum(len(targets)+int(within) for _, targets in selected)
    return variables, count, selected


def constraint_batches(state, first, second, selected):
    q = state['q']
    within = first == second
    a, b = np.triu_indices(77)
    off = a != b
    variables = len(a) if within else 77*77
    words = (variables+64)//64
    for vertex, targets in selected:
        if within:
            target = q[second][[vertex]+targets]
            rows = target[:, b]*q[first][vertex, a]
            rows[:, off] ^= target[:, a[off]]*q[first][vertex, b[off]]
        else:
            rows = (q[first][vertex, None, :, None]*q[second][targets, None, :]).reshape(len(targets), -1)
        augmented = np.zeros((len(rows), words*64), dtype=np.uint8)
        augmented[:, :variables] = rows
        if within:
            augmented[0, variables] = 1
        yield np.packbits(augmented, axis=1, bitorder='little')


def compile_solver(output, compiler=None):
    compiler = compiler or shutil.which('c++') or shutil.which('clang++') or shutil.which('g++')
    require(compiler is not None, 'A C++ compiler is required for quadratic elimination')
    binary = output / 'solve'
    subprocess.run([compiler, '-std=c++17', '-O3', str(ROOT / 'code/solve.cpp'), '-o', str(binary)],
                   check=True, capture_output=True, text=True)
    return binary


def baseline_gram(state, high):
    q, p = state['q'][high], state['p'][high]
    _, indices = rank_rows(encode_rows(q))
    require(len(indices) == 77, 'Quadratic evaluation column rank')
    transform = (inverse(q[indices]) @ p[indices]) & 1
    require(np.array_equal((q @ transform) & 1, p), 'Old profile map lies in quadratic span')
    gram = (transform @ transform.T) & 1
    require(len(rank_rows(encode_rows(gram))[0]) == 9, 'Baseline within Gram rank')
    return gram


def matrix_from_bits(bits, within):
    if not within:
        return bits.reshape(-1, 77, 77)
    a, b = np.triu_indices(77)
    matrices = np.zeros((len(bits), 77, 77), dtype=np.uint8)
    matrices[:, a, b] = bits
    matrices[:, b, a] = bits
    return matrices


def coefficient_bits(matrix, within):
    if within:
        a, b = np.triu_indices(77)
        return matrix[a, b]
    return matrix.reshape(-1)


def check_solutions(state, first, second, selected, matrices):
    within = first == second
    variables = 3003 if within else 5929
    packed = encode_rows(np.array([coefficient_bits(matrix, within) for matrix in matrices]))
    mask = (1 << variables)-1
    checked = 0
    for batch in constraint_batches(state, first, second, selected):
        for row in batch:
            value = int.from_bytes(row.tobytes(), 'little')
            rhs, coefficients = value >> variables, value & mask
            require((coefficients & packed[0]).bit_count() % 2 == rhs, 'Particular constraint replay')
            require(all((coefficients & direction).bit_count() % 2 == 0 for direction in packed[1:]),
                    'Homogeneous direction replay')
            checked += 1
    require(len(rank_rows(packed[1:])[0]) == len(packed)-1, 'Independent homogeneous directions')
    return checked


def solve_pair(state, first, second, output, binary):
    variables, count, selected = prepare(state, first, second)
    name = f'{first}{second}'
    raw_path = output / f'solution-{name}.bin'
    process = subprocess.Popen([str(binary), str(raw_path)], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    digest = hashlib.sha256()
    header = struct.pack('<II', variables, count)
    digest.update(header)
    try:
        process.stdin.write(header)
        for batch in constraint_batches(state, first, second, selected):
            data = batch.tobytes()
            digest.update(data)
            process.stdin.write(data)
        process.stdin.close()
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        code = process.wait()
    except BaseException:
        process.kill()
        process.wait()
        raise
    require(code == 0, f'Quadratic elimination failed: {stderr.decode()} {stdout.decode()}')
    receipt = json.loads(stdout)
    raw = raw_path.read_bytes()
    n, solutions = struct.unpack('<II', raw[:8])
    words = (variables+64)//64
    require(n == variables and len(raw) == 8+solutions*words*8, 'Exact solution file dimensions')
    bits = np.unpackbits(np.frombuffer(raw[8:], dtype=np.uint8).reshape(solutions, words*8),
                         axis=1, bitorder='little')[:, :variables]
    matrices = matrix_from_bits(bits, first == second)
    if first == second:
        matrices[0] = baseline_gram(state, first)
    else:
        require(not matrices[0].any(), 'Homogeneous cross-family zero particular')
    require(check_solutions(state, first, second, selected, matrices) == count,
            'All generated constraints independently replayed')
    np.savez_compressed(output / f'quadratic-{name}.npz', particular=matrices[0], directions=matrices[1:])
    raw_path.unlink()
    receipt.update(profiles=[first, second], constraint_sha256=digest.hexdigest(),
                   particular_rank=len(rank_rows(encode_rows(matrices[0]))[0]),
                   particular_hash=array_hash(matrices[0]), directions_hash=array_hash(matrices[1:]),
                   independent_solution_replay=True)
    return receipt


def solver_negative_controls(binary, output):
    rejected = []
    for name, data in [('inconsistent', struct.pack('<IIQQ', 1, 2, 1, 3)),
                       ('truncated', struct.pack('<II', 1, 1)),
                       ('nonzero_padding', struct.pack('<IIQ', 1, 1, 4)),
                       ('trailing_data', struct.pack('<IIQ', 1, 1, 1)+b'x')]:
        result = subprocess.run([str(binary), str(output/'negative.bin')], input=data, capture_output=True)
        require(result.returncode != 0, f'Solver corruption accepted: {name}')
        rejected.append(name)
    return rejected


def run(state, output, compiler=None):
    output.mkdir(parents=True, exist_ok=True)
    binary = compile_solver(output, compiler)
    results = [solve_pair(state, i, j, output, binary)
               for i, j in ((0, 0), (1, 1), (2, 2), (0, 1), (0, 2), (1, 2))]
    require([x['nullity'] for x in results] == [168, 168, 168, 46, 46, 46],
            'Bounded quadratic family dimensions')
    receipt = dict(status='PASS_QUADRATIC_AFFINE_FAMILY', blocks=results,
        total_free_binary_parameters=sum(row['nullity'] for row in results),
        negative_controls=solver_negative_controls(binary, output),
        scope='Complete symmetric fitting family in three independent quadratic77 feature spaces; no low-rank completion or kappa claim')
    (output/'QUADRATIC.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt
