"""Independent Fraction minor checks and full row-code coverage, Apache-2.0.

The source-pin and geometry readers are shared, but this checker does not
call the producer's row-code basis, modular elimination, Bareiss or build.
Contributor @woklerx with substantial OpenAI Codex assistance.
"""
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('sink_sources', HERE / 'verify.py')
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
require = source.require


def fraction_determinant(rows):
    a = [list(map(Fraction, row)) for row in rows]
    answer = Fraction(1)
    for col in range(len(a)):
        pivot = next((i for i in range(col, len(a)) if a[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            a[pivot], a[col] = a[col], a[pivot]
            answer *= -1
        value = a[col][col]
        answer *= value
        for i in range(col + 1, len(a)):
            scale = a[i][col] / value
            for j in range(col + 1, len(a)):
                a[i][j] -= scale * a[col][j]
    require(answer.denominator == 1, 'integer determinant')
    return int(answer)


def audit(certificate):
    lines, decoder = source.geometry()
    words = {0}
    for row in decoder:
        words |= {word ^ row for word in words}
    require(len(words) == 512, 'full decoder row code')
    records = certificate['patterns']
    require(len(records) == 511, 'pattern count')
    require({int(r['pattern'], 16) for r in records} == words - {0}, 'pattern coverage')
    minors = {}
    for record in certificate['minors']:
        indices, columns = record['rows'], record['columns']
        require(all(type(i) is int and 0 <= i < 120 for i in indices), 'minor row indices')
        require(all(type(i) is int and 0 <= i < 8 for i in columns), 'minor column indices')
        require(len(indices) == len(columns) and len(set(indices)) == len(indices)
                and len(set(columns)) == len(columns), 'square distinct minor')
        key = (tuple(indices), tuple(columns))
        require(key not in minors, 'duplicate minor')
        value = fraction_determinant([[lines[i][j] for j in columns] for i in indices])
        require(type(record['determinant']) is int and value == record['determinant'] != 0, 'invalid exact minor')
        minors[key] = value
    cases, ranks, used = 0, Counter(), set()
    for record in records:
        word = int(record['pattern'], 16)
        support = {i for i in range(8, 120) if word >> i & 1}
        base, columns, rank = record['base'], record['columns'], record['rank']
        require(type(rank) is int and len(base) == len(columns) == rank, 'rank declaration')
        if rank == 7:
            missing = set(range(8)) - set(columns)
            require(len(missing) == 1, 'coordinate hyperplane shape')
            coordinate = next(iter(missing))
            require(word == decoder[coordinate] and all(lines[i][coordinate] == 0 for i in support), 'rank-seven upper bound')
        else:
            require(rank == 8 and columns == list(range(8)), 'ambient rank-eight upper bound')
        alternatives = {i for i in support if word != decoder[i]}
        require(set(record['repairs']) == {str(i) for i in alternatives if i in base}, 'repair inventory')
        for target in alternatives:
            chosen = record['repairs'].get(str(target), base)
            require(len(chosen) == rank and set(chosen) <= support - {target}, 'witness outside admissible source set')
            key = (tuple(chosen), tuple(columns))
            require(key in minors, 'missing checked minor')
            used.add(key)
            cases += 1
            ranks[rank] += 1
    require(used == set(minors), 'unused minor')
    require(cases == 28560 and certificate['alternative_cases'] == cases, 'case inventory')
    require(certificate['free_alternatives'] == 0, 'false free count')
    require({str(k): v for k, v in ranks.items()} == certificate['rational_rank_histogram'], 'rank histogram')
    return {'cases': cases, 'rank_histogram': dict(sorted(ranks.items())), 'exact_minors': len(minors)}


if __name__ == '__main__':
    source.checked_sources()
    result = audit(json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8')))
    print('PASS_P112_FREE_SINK_INDEPENDENT ' + json.dumps(result, sort_keys=True))
