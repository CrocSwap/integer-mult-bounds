"""Exact consolidation of PR620's archived free asymmetric sink screen.

Contributor @woklerx; substantial OpenAI Codex assistance. Apache-2.0.
Geometry and feasibility model credited to Joel Pulikkan (PR620), building
on DreamingOfClouds (PR595). No upstream source is executed or modified.
"""
import argparse
import ast
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'
PREFIX = 'research/e8-decoder-floors-and-cold14-notes/'
FILES = tuple(PREFIX + p for p in (
    'README.md', 's2-decoder/REPORT.md', 's2-decoder/asym.py',
    's2-decoder/geo.py', 's2-decoder/e8units.py')) + (
    'docs/research/community-k492-review.md',)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # JSON object keys are strings on disk; normalize keys before sorting.
    normalized = json.loads(json.dumps(value))
    return json.dumps(normalized, sort_keys=True, separators=(',', ':'))


def checked_sources(root=ROOT, package=HERE):
    pins = json.loads((package / 'SOURCES.json').read_text(encoding='utf-8'))
    require(pins['base'] == BASE, 'base mismatch')
    require(set(pins['files']) == set(FILES), 'source inventory mismatch')
    for name in FILES:
        raw = (root / name).read_bytes().replace(b'\r\n', b'\n')
        require(sha256(raw).hexdigest() == pins['files'][name], 'source mismatch: ' + name)
    snapshot = (package / 'BASE-SELECTED.json').read_bytes().replace(b'\r\n', b'\n')
    require(sha256(snapshot).hexdigest() == pins['selected_snapshot_sha256'], 'snapshot mismatch')
    selected = json.loads(snapshot)
    require(selected['kappa'] == '1661960547713947/1000000000000000000', 'frozen kappa mismatch')
    require(selected['audited_source_head'] == '1960cfa919a0945d0ca4cb14ea96237000037903', 'frozen head mismatch')


def geometry(root=ROOT):
    tree = ast.parse((root / (PREFIX + 's2-decoder/e8units.py')).read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'hamming_e8')
    assignments = [n for n in function.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'gen' for t in n.targets)]
    require(len(assignments) == 1, 'unique geometry generator')
    gen = ast.literal_eval(assignments[0].value.args[0])
    require(len(gen) == 4 and all(len(r) == 8 and set(r) <= {0, 1} for r in gen), 'generator shape')
    code = {tuple(sum(c[k] * gen[k][i] for k in range(4)) % 2 for i in range(8))
            for c in product((0, 1), repeat=4)}
    supports = sorted(c for c in code if sum(c) == 4)
    require(len(code) == 16 and len(supports) == 14, 'Hamming code census')
    lines = [[2 * int(i == a) for i in range(8)] for a in range(8)]
    for support in supports:
        indices = [i for i, x in enumerate(support) if x]
        for signs in product((1, -1), repeat=3):
            row = [0] * 8
            for i, s in zip(indices, (1,) + signs):
                row[i] = s
            lines.append(row)
    require(len(lines) == 120 and len({tuple(r) for r in lines}) == 120, 'root line census')
    gram = [[sum(x*y for x, y in zip(a, b)) for b in lines] for a in lines]
    require(all(x % 2 == 0 for r in gram for x in r), 'Gram integrality')
    decoder = [sum(((1 + x//2) % 2) << j for j, x in enumerate(row)) for row in gram]
    require(all((decoder[i] >> i) & 1 for i in range(120)), 'odd target labels')
    return lines, decoder


def row_code(decoder):
    pivots = {}
    generators = []
    for row in decoder:
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot in pivots:
                reduced ^= pivots[pivot]
            else:
                pivots[pivot] = reduced
                generators.append(row)
                break
    require(len(generators) == 9, 'decoder rank must be nine')
    words = [0]
    for row in generators:
        words += [word ^ row for word in words]
    require(len(set(words)) == 512, 'all sink functionals')
    return sorted(words[1:])


def minor_basis(lines, indices, prime=101):
    basis, chosen = {}, []
    for index in indices:
        row = [x % prime for x in lines[index]]
        for pivot, old in sorted(basis.items()):
            factor = row[pivot]
            row = [(a-factor*b) % prime for a, b in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = pow(row[pivot], -1, prime)
            basis[pivot] = [x*scale % prime for x in row]
            chosen.append(index)
            if len(chosen) == 8:
                break
    return chosen


def determinant(rows):
    """Bareiss exact integer determinant, independent of modular row selection."""
    a = [list(r) for r in rows]
    n, sign, previous = len(a), 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        p = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j]*p - a[i][k]*a[k][j]
                require(numerator % previous == 0, 'Bareiss exact division')
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = p
    return sign * a[-1][-1]


def build(root=ROOT):
    lines, decoder = geometry(root)
    words = row_code(decoder)
    receipts, determinants, cases, positives = [], {}, 0, 0
    sizes, ranks = Counter(), Counter()
    for word in words:
        support = [i for i in range(8, 120) if word >> i & 1]
        base = minor_basis(lines, support)
        dimension = len(base)
        if dimension == 7:
            coordinate = next((i for i in range(8) if word == decoder[i]), None)
            require(coordinate is not None, 'rank-seven pattern must be an omitted coordinate label')
            require(all(lines[i][coordinate] == 0 for i in support), 'rank-seven upper bound')
            columns = [i for i in range(8) if i != coordinate]
        else:
            require(dimension == 8, 'full pattern support rank')
            columns = list(range(8))
        repairs = {}
        for target in support:
            if word == decoder[target]:
                # Original same-label sink is outside the claimed alternatives.
                z = [i for i in support if i != target]
                require(all(sum(x*y for x, y in zip(lines[i], lines[target])) == 0 for i in z), 'self sink annihilation')
                require(len(minor_basis(lines, z)) == 7, 'self sink rank seven')
                positives += 1
                continue
            chosen = base if target not in base else minor_basis(lines, [i for i in support if i != target])
            require(len(chosen) == dimension and target not in chosen, 'missing full-rank witness')
            key = (tuple(chosen), tuple(columns))
            if key not in determinants:
                value = determinant([[lines[i][j] for j in columns] for i in chosen])
                require(value != 0, 'zero exact minor')
                determinants[key] = value
            if target in base:
                repairs[str(target)] = chosen
            cases += 1
            sizes[len(support) - 1] += 1
            ranks[dimension] += 1
        receipts.append({'pattern': format(word, '030x'), 'rank': dimension, 'columns': columns, 'base': base, 'repairs': repairs})
    require(cases == 28560 and positives == 112, 'domain cardinality')
    return {
        'schema': 1, 'base': BASE, 'status': 'EXACT_ARCHIVED_SCOPE_NO_NEW_KAPPA',
        'sink_patterns': len(words), 'alternative_cases': cases, 'free_alternatives': 0,
        'same_label_positive_controls': positives, 'support_size_histogram': dict(sorted(sizes.items())),
        'rational_rank_histogram': dict(sorted(ranks.items())),
        'geometry_sha256': sha256(canonical(lines).encode()).hexdigest(),
        'decoder_sha256': sha256(canonical(decoder).encode()).hexdigest(),
        'unique_minor_count': len(determinants),
        'determinant_histogram': dict(sorted(Counter(determinants.values()).items())),
        'minors': [{'rows': list(k[0]), 'columns': list(k[1]), 'determinant': v} for k, v in sorted(determinants.items())],
        'patterns': receipts,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    checked_sources()
    actual = build()
    path = HERE / 'CERTIFICATE.json'
    if args.write:
        header = {k: v for k, v in actual.items() if k not in ('minors', 'patterns')}
        output = json.dumps(header, indent=2)[:-2]
        for name in ('minors', 'patterns'):
            output += ',\n  ' + json.dumps(name) + ': [\n'
            output += ',\n'.join('    ' + json.dumps(item, separators=(',', ':')) for item in actual[name])
            output += '\n  ]'
        path.write_text(output + '\n}\n', encoding='utf-8')
    else:
        require(canonical(actual) == canonical(json.loads(path.read_text(encoding='utf-8'))), 'certificate mismatch')
    print('PASS_P112_FREE_SINK_EXACT cases=28560 free=0 self_controls=112 no_new_kappa')


if __name__ == '__main__':
    main()
