"""Check finite-memory equality or one literal physical entry discrepancy.

No producer import, basis search or elimination. Arithmetic/parser are shared
with the producer. Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
from exact import G, fingerprint, load, matrix, need, parse


def check(data, certificate, max_states=256):
    d, n, p, q, left, right, transitions = parse(data, max_states)
    c = certificate
    need(isinstance(c, dict) and c.get('problem_sha256') == fingerprint(data), 'problem binding')
    need(type(c.get('width_bound')) is int and c['width_bound'] == n, 'width bound')
    if c.get('kind') == 'counterexample':
        need(set(c) == {'kind', 'problem_sha256', 'word', 'output', 'input',
                        'value', 'width_bound'}, 'counterexample fields')
        word, i, j = c['word'], c['output'], c['input']
        need(isinstance(word, list) and 1 <= len(word) <= n, 'positive witness width')
        need(type(i) is int and type(j) is int and 0 <= i < p and 0 <= j < q, 'endpoint channel')
        v = list(left[i])
        for symbol in word:
            need(symbol in transitions, 'unknown witness symbol')
            a = transitions[symbol]
            v = [sum((v[k]*a[k][h] for k in range(n)), G()) for h in range(n)]
        value = sum((v[k]*right[k][j] for k in range(n)), G())
        from exact import scalar
        need(value and value == scalar(c['value']), 'literal nonzero discrepancy')
        return {'status': 'PASS_PHYSICAL_COUNTEREXAMPLE', 'width': len(word),
                'output_column': [int(s.split(',')[0]) for s in word],
                'input_column': [int(s.split(',')[1]) for s in word],
                'output_role': i, 'input_role': j, 'value': value.json()}
    need(c.get('kind') == 'all_positive_widths', 'certificate kind')
    need(set(c) == {'kind', 'problem_sha256', 'rank', 'positive_seed_rank', 'basis',
                    'seeds', 'closure', 'width_bound'}, 'equality fields')
    r = c['rank']
    need(type(r) is int and 0 <= r <= n, 'certificate rank')
    seed_rank = c['positive_seed_rank']
    need(type(seed_rank) is int and 0 <= seed_rank <= r, 'seed rank range')
    # Independence and the advertised seed rank are producer diagnostics. The
    # checker needs only a spanning invariant set, not an optimal basis.
    rows = matrix(c['basis'], r, n)
    need(isinstance(c['seeds'], dict) and set(c['seeds']) == set(transitions), 'all seed symbols')
    need(isinstance(c['closure'], dict) and set(c['closure']) == set(transitions), 'all closure symbols')
    for s, t in transitions.items():
        seeds = matrix(c['seeds'][s], p, r)
        closure = matrix(c['closure'][s], r, r)
        for i in range(p):
            for j in range(n):
                actual = sum((left[i][k]*t[k][j] for k in range(n)), G())
                claimed = sum((seeds[i][k]*rows[k][j] for k in range(r)), G())
                need(actual == claimed, 'positive seed containment')
        for i in range(r):
            for j in range(n):
                actual = sum((rows[i][k]*t[k][j] for k in range(n)), G())
                claimed = sum((closure[i][k]*rows[k][j] for k in range(r)), G())
                need(actual == claimed, 'transition closure')
    for i in range(r):
        for j in range(q):
            need(not sum((rows[i][k]*right[k][j] for k in range(n)), G()), 'all returned channels')
    return {'status': 'PASS_ALL_POSITIVE_WIDTHS', 'invariant_rows': r,
            'states': n, 'local_dimension': d, 'outputs': p, 'inputs': q}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem')
    parser.add_argument('certificate')
    parser.add_argument('--max-states', type=int, default=256)
    args = parser.parse_args()
    import json
    print(json.dumps(check(load(args.problem), load(args.certificate), args.max_states), indent=2))


if __name__ == '__main__':
    main()
