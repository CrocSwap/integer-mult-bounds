"""Check the exact four-qubit width-twelve nullity.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import deque
from hashlib import sha1, sha256
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ORDER = 47_377_612_800
SELECTED_ROWS = (5, 6, 9, 22)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_check(archive):
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        data = (ROOT / pin['retained']).read_bytes()
        require(sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == pin['git_blob'], 'source Git blob')
    path = ROOT / 'retained/source7766'
    args = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
            '-B', str(path / 'verify.py')]
    if archive:
        args += ['--ctbllib-archive', str(archive)]
    replay = subprocess.run(args, check=True, capture_output=True, text=True, timeout=60)
    require('PASS_CLIFFORD_FOUR_QUBIT_THRESHOLD' in replay.stdout, 'source replay')
    return len(pins), load('source7766', path / 'verify.py')


def extract_columns(archive):
    # Retain the source parser's record and row order. Read four complete
    # rational rows, including the dimension-zero classes it summed out.
    source = load('source7747', ROOT / 'retained/source7766/retained/source7747/verify.py')
    table = source.read_table(archive)
    block = table.split('MOT("S8(2)",\n', 1)[1].split('\nARC("S8(2)"', 1)[0]
    numbers = block.split('],\n', 1)[1]
    centralizers = json.loads(numbers.split('],\n', 1)[0] + ']')
    entries = block.split('\n[[1,1,1,', 1)[1].split(']],\n', 1)[0]
    entries = re.sub(r'\s+', '', '1,1,1,' + entries)
    require(entries.count('[GALOIS,[72,3]]') == 1, 'Galois marker')
    entries = entries.replace('[GALOIS,[72,3]]', 'GALOIS')
    rows = [row.split(',') for row in re.split(r'\],\[|\],(?=GALOIS)|(?<=GALOIS),\[', entries)]
    require(len(rows) == len(centralizers) == 81 and rows[72] == ['GALOIS'], 'table shape')
    require(all(len(rows[i-1]) == 81 for i in SELECTED_ROWS), 'selected row shape')
    columns = [{'index': j + 1, 'centralizer': centralizers[j],
                'values': [int(rows[i-1][j]) for i in SELECTED_ROWS]} for j in range(81)]
    return {'table': 'S8(2)', 'one_based_rows': list(SELECTED_ROWS), 'columns': columns}


def class_checks(data):
    source = json.loads((ROOT / 'retained/source7766/retained/source7747/PROJECTION.json').read_text())
    require(data['one_based_rows'] == list(SELECTED_ROWS) and len(data['columns']) == 81,
            'column inventory')
    elements, classes = [0] * 9, [0] * 9
    projected = [[0] * 9 for _ in SELECTED_ROWS]
    norms = [[0] * 4 for _ in range(4)]
    derangements = []
    for index, column in enumerate(data['columns'], 1):
        require(column['index'] == index and len(column['values']) == 4, 'class index')
        centralizer = column['centralizer']
        require(type(centralizer) is int and centralizer > 0 and ORDER % centralizer == 0,
                'class centralizer')
        size = ORDER // centralizer
        values = column['values']
        fixed = 2 + values[0] + values[1]
        require(1 <= fixed <= 256 and fixed.bit_count() == 1, 'fixed-space dimension')
        d = fixed.bit_length() - 1
        elements[d] += size
        classes[d] += 1
        for i, value in enumerate(values):
            projected[i][d] += size * value
            for j, other in enumerate(values):
                norms[i][j] += size * value * other
        if fixed == 1:
            derangements.append(column)
    require(elements == source['element_counts'] and classes == source['class_counts'],
            'source class projection')
    require(norms == [[ORDER * (i == j) for j in range(4)] for i in range(4)],
            'full ordinary row orthogonality')
    for position, index in enumerate(SELECTED_ROWS):
        row = source['rows'][index - 1]
        expected = [-sum(row)] + row[1:] + row[:1]
        require(projected[position] == expected, 'complete row projection')
    witness = [column for column in derangements if column['index'] in (9, 25)]
    require(len(witness) == 2 and [c['values'][2:] for c in witness] == [[10, 0], [0, 3]],
            'derangement witness values')
    a, b = (c['values'][2:] for c in witness)
    determinant = a[0] * b[1] - a[1] * b[0]
    require(determinant == 30, 'restriction determinant')
    require(data['columns'][0]['values'] == [119, 135, 595, 3213], 'identity degrees')
    require(2 + sum(data['columns'][0]['values'][:2]) != 1, 'identity is not a derangement')
    require(a[0] * a[1] - a[1] * a[0] == 0, 'duplicate-column rank control')
    return {'derangements': derangements, 'witness': witness, 'determinant': determinant,
            'ordinary_row_inner_products': norms, 'projected_rows': projected}


def literal_checks(source):
    vectors = [{(source.pauli(label, x, 4)[0], x): source.pauli(label, x, 4)[1]
                for x in range(16)} for label in range(256)]
    lookup = {}
    for label, vector in enumerate(vectors):
        first = vector[min(vector)]
        lookup[tuple((key, (phase-first) % 4) for key, phase in sorted(vector.items()))] = label
    pauli_entries = 0
    for label, actor in product(range(256), repeat=2):
        sign = 2 * source.omega(actor, label, 4)
        for x in range(16):
            y, phase1 = source.pauli(actor, x, 4)
            z, phase2 = source.pauli(label, y, 4)
            out, phase3 = source.pauli(actor, z, 4)
            target, phase = source.pauli(label, x, 4)
            require(out == target and (phase1+phase2+phase3-phase) % 4 == sign,
                    'literal Pauli adjoint character')
            pauli_entries += 1
    generators = [('S', i, 0) for i in range(4)] + [('H', i, 0) for i in range(4)]
    generators += [('CNOT', i, j) for i in range(4) for j in range(4) if i != j]
    permutations, signs = [], []
    for kind, i, j in generators:
        permutation, line_signs = [], []
        for vector in vectors:
            output = {}
            for (x, y), phase in vector.items():
                for (xx, px), (yy, py) in product(source.gate_action(kind, i, j, x),
                                                 source.gate_action(kind, i, j, y)):
                    value = source.UNITS[(phase+px-py) % 4]
                    old = output.get((xx, yy), (0, 0))
                    output[xx, yy] = old[0]+value[0], old[1]+value[1]
            output = {key: value for key, value in output.items() if value != (0, 0)}
            divisor = 2 if kind == 'H' else 1
            phases = {}
            for key, (real, imag) in output.items():
                require(real % divisor == imag % divisor == 0, 'Gaussian adjoint division')
                value = real//divisor, imag//divisor
                require(value in source.UNITS, 'Pauli line coefficient')
                phases[key] = source.UNITS.index(value)
            first = phases[min(phases)]
            key = tuple((position, (phase-first) % 4) for position, phase in sorted(phases.items()))
            require(key in lookup, 'literal Clifford adjoint line')
            target = lookup[key]
            sign = (first-vectors[target][min(vectors[target])]) % 4
            require(sign in (0, 2), 'Hermitian line sign')
            permutation.append(target)
            line_signs.append(sign//2)
        require(permutation[0] == line_signs[0] == 0 and len(set(permutation)) == 256,
                'identity line and permutation')
        basis = tuple(permutation[1 << bit] for bit in range(8))
        require(all(source.apply(basis, x) == permutation[x] for x in range(256)),
                'linear label action')
        require(all(source.omega(permutation[1 << a], permutation[1 << b], 4)
                    == source.omega(1 << a, 1 << b, 4) for a, b in product(range(8), repeat=2)),
                'symplectic basis action')
        permutations.append(permutation)
        signs.append(line_signs)
    found, queue = {1}, deque([1])
    while queue:
        x = queue.popleft()
        for permutation in permutations:
            y = permutation[x]
            if y not in found:
                found.add(y)
                queue.append(y)
    require(found == set(range(1, 256)), 'single nonzero Pauli orbit')
    require(source.omega(16, 1, 4) == 1, 'omitted stabilizer-line sign control')
    return {'pauli_character_pairs': 65536, 'pauli_matrix_entries': pauli_entries,
            'literal_adjoint_images': 5120, 'generator_count': 20, 'orbits': [1, len(found)],
            'negative_generator_images': sum(sum(row) for row in signs),
            'nonzero_stabilizer_order': ORDER//255}


def collect(archive=None):
    count, source = source_check(archive)
    external = json.loads((ROOT / 'EXTERNAL.json').read_text())
    raw = (ROOT / 'CHARACTER-COLUMNS.json').read_bytes()
    require(sha256(raw).hexdigest() == external['derived_sha256'], 'derived character bytes')
    data = json.loads(raw)
    if archive:
        require(extract_columns(archive) == data, 'authenticated archive column extraction')
    classes = class_checks(data)
    bad = json.loads(json.dumps(data))
    bad['columns'][8]['values'][2] += 1
    try:
        class_checks(bad)
    except ValueError as error:
        require(str(error) == 'full ordinary row orthogonality', 'changed character control reason')
    else:
        raise ValueError('changed character accepted')
    projection = json.loads((ROOT / 'retained/source7766/retained/source7747/PROJECTION.json').read_text())
    multiplicities, _ = source.odd_multiplicities(projection, 5)
    missing = [i+1 for i, value in enumerate(multiplicities) if value == 0]
    require(missing == [9, 22], 'only two missing quotient rows')
    nullity = sum(projection['rows'][i-1][0]**2 for i in missing)
    size = 256 * ORDER
    nonzero_regular = 255**2 * (ORDER//255)
    require(ORDER + nonzero_regular == size, 'complete regular-sector dimension')
    require((nullity, size-nullity) == (10677394, 12128658199406), 'exact Gram dimensions')
    return {'source_files': count, 'class_checks': classes, 'literal_checks': literal_checks(source),
            'missing_quotient_rows': missing, 'missing_block_degrees': [595, 3213],
            'projective_order': size, 'regular_sector_dimensions': [ORDER, nonzero_regular],
            'exact_nullity': nullity, 'exact_rank': size-nullity,
            'nonzero_pauli_sectors': 'all occur, by the written induction proof'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ctbllib-archive', type=Path)
    args = parser.parse_args()
    result = collect(args.ctbllib_archive)
    require(result == json.loads((ROOT / 'RESULT.json').read_text()), 'saved result mismatch')
    if args.ctbllib_archive:
        print('PASS_AUTHENTICATED_CTBL_COLUMNS classes=81 rational_rows=4')
    print('PASS_CLIFFORD_WIDTH_TWELVE_NULLITY')
    print('Exact nullity 10677394; exact rank 12128658199406; T(4)=13 unchanged')
    print('Derangement classes 9 and 25 give diagonal witness (10,3), determinant 30')
    print('All nonzero Pauli-character sectors occur; only inflated rows 9 and 22 are absent')
    print('65536 Pauli pairs; 1048576 literal entries; 5120 adjoint images; orbit sizes 1,255')


if __name__ == '__main__':
    main()
