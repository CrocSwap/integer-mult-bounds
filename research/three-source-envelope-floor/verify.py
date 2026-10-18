"""Exact witness replay; the uniform lower bound is the proof in README.md."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def witness(n):
    return [[0, 1]] + [[3+j, 0] for j in range(n)] + [[0, 1]] + [[3+j, 2] for j in range(n)]


def replay(n, auxiliary, word):
    size = 3+n+auxiliary
    rows = [[int(i == j) for j in range(size)] for i in range(size)]
    binary = [1 << i for i in range(size)]
    peak = 1
    for gate in word:
        require(isinstance(gate, list) and len(gate) == 2, 'gate shape')
        d, s = gate
        require(type(d) is int and type(s) is int and 0 <= d < size and 0 <= s < size and d != s, 'gate indices')
        binary[d] ^= binary[s]
        rows[d] = [a+b for a, b in zip(rows[d], rows[s])]
        peak = max(peak, sum(rows[d]))
    expected = [(1 << i) ^ (7 if 3 <= i < 3+n else 0) for i in range(size)]
    require(binary == expected, 'complete dirty endpoint')
    require([sum((v % 2) << j for j, v in enumerate(row)) for row in rows] == binary, 'integer/binary reduction')
    return peak, rows


def validate(certificate):
    require(certificate['schema_version'] == 1 and certificate['claim'] == 'minimum_peak_four_cost_2n_plus_2', 'claim')
    expected_cases = [(n, a) for n in (2, 3, 4, 8, 16, 32, 64) for a in (0, 1, 5)] + [(128, 0)]
    require([(c['targets'], c['auxiliaries']) for c in certificate['cases']] == expected_cases, 'case inventory')
    for c in certificate['cases']:
        n, a, word = c['targets'], c['auxiliaries'], c['word']
        require(word == witness(n), 'attaining word')
        require(c['cost'] == len(word) == 2*n+2, 'cost')
        for actual, direction in ((word, 'forward'), (list(reversed(word)), 'reverse')):
            peak, rows = replay(n, a, actual)
            require(c[direction+'_peak'] == peak == 4, 'peak')
            require(rows[0][1] == 2 and sum(rows[0]) == 3, 'helper positive restoration bill')
    return len(certificate['cases'])


def rejected(fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError):
        return
    raise ValueError('negative control accepted')


def main():
    certificate = json.loads((HERE/'CERTIFICATE.json').read_text(encoding='utf-8'))
    count = validate(certificate)
    rejected(lambda: replay(4, 1, witness(4)[1:]))
    rejected(lambda: replay(4, 1, witness(4)[:-1]))
    rejected(lambda: replay(4, 1, witness(4)+[[0, 0]]))
    for field, value in [('cost', 9), ('forward_peak', 3), ('reverse_peak', 5)]:
        mutant = json.loads(json.dumps(certificate))
        mutant['cases'][6][field] = value
        rejected(lambda: validate(mutant))
    gather = [[0, 1], [0, 2]] + [[j, 0] for j in range(3, 7)] + [[0, 2], [0, 1]]
    require(replay(4, 0, gather)[0] == 5, 'eight-gate control must have peak five')
    direct = [[3, 0], [3, 1], [3, 2]]
    require(replay(1, 0, direct)[0] == 4 and len(direct) < 2*1+2, 'n=1 restriction')
    # Finite illustration of the restored helper parity obstruction.
    restored = [(x, y, z) for x in range(1, 5, 2) for y in range(0, 5, 2) for z in range(0, 5, 2) if x+y+z <= 4]
    require(all(not (x and y and z) for x, y, z in restored), 'restored helper support floor')
    print(f'PASS_THREE_SOURCE_ENVELOPE cases={count} directions={2*count} controls=8 uniform_proof=README no_new_kappa')


if __name__ == '__main__':
    main()
