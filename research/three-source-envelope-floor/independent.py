"""Independent full truth tables and column-oriented positive replay; no primary imports."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def columns(n, auxiliary, gates):
    m = 3+n+auxiliary
    totals = [0]*m
    for basis in range(m):
        vector = [int(i == basis) for i in range(m)]
        for destination, source in gates:
            need(type(destination) is int and type(source) is int and 0 <= destination < m and 0 <= source < m and destination != source, 'gate')
            vector[destination] += vector[source]
        for output, value in enumerate(vector):
            expected = int(output == basis) ^ int(3 <= output < 3+n and basis < 3)
            need(value % 2 == expected, 'basis endpoint')
            totals[output] += value
    return max(totals)


def truth(n, auxiliary, gates):
    m = 3+n+auxiliary
    for original in range(1 << m):
        values = [(original >> i) & 1 for i in range(m)]
        parity = values[0] ^ values[1] ^ values[2]
        expected = [v ^ (parity if 3 <= i < 3+n else 0) for i, v in enumerate(values)]
        for destination, source in gates:
            values[destination] ^= values[source]
        need(values == expected, 'dirty truth table')
    return 1 << m


def main():
    data = json.loads((HERE/'CERTIFICATE.json').read_text(encoding='utf-8'))
    need(data['claim'] == 'minimum_peak_four_cost_2n_plus_2', 'claim')
    need([(c['targets'], c['auxiliaries']) for c in data['cases']] == [(n, a) for n in (2, 3, 4, 8, 16, 32, 64) for a in (0, 1, 5)]+[(128, 0)], 'inventory')
    truth_inputs = 0
    for c in data['cases']:
        n, a, gates = c['targets'], c['auxiliaries'], c['word']
        need(c['cost'] == len(gates) == 2*n+2, 'cost')
        for word, label in ((gates, 'forward'), (gates[::-1], 'reverse')):
            need(columns(n, a, word) == c[label+'_peak'] == 4, 'positive column envelope')
            if n <= 4:
                truth_inputs += truth(n, a, word)
    # Endpoint-only replay with clean helpers would miss omitted restoration.
    bad = [[0, 1]] + [[3+j, 0] for j in range(4)] + [[3+j, 2] for j in range(4)]
    try:
        truth(4, 1, bad)
    except ValueError:
        pass
    else:
        raise ValueError('missing-restoration control accepted')
    print(f'PASS_INDEPENDENT_ENVELOPE cases={len(data["cases"])} dirty_inputs={truth_inputs} control=1')


if __name__ == '__main__':
    main()
