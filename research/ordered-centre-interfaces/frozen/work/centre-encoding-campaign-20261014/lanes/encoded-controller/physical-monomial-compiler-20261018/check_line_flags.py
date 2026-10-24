#!/usr/bin/env python3
"""Check the physical line-flag ranks from the exact source recipes."""

from collections import Counter
from hashlib import sha256
import gzip
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PAYLOAD = LANES / 'history-encoding/independent-skeleton-20261018/INDEPENDENT-SKELETON-PROGRAMS.json.gz'
COMPILER = LANES / 'new-native-recipes-20261017/sources/vendor/clifford/clifford_exact.py'
PINS = {
    'payload_decompressed': '8fe1147e5cb80d9f1d9ef309b0ee6f42b1a64cc5ebabd19b818623c246c9fd64',
    'compiler': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
}


def need(value, message):
    if not value:
        raise AssertionError(message)


def mm(a, b, n, ce):
    bt = ce.transpose(b, n)
    return tuple(sum(ce.parity(x & y) << j for j, y in enumerate(bt)) for x in a)


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def projection(q, n):
    return tuple(q if q >> i & 1 else 0 for i in range(n))


def recipe_op(record, ce):
    return (ce.diag(9, record['quadratic_rows'], record['linear_Z4'])
            .then(ce.perm(9, record['matrix_rows']))
            .then(ce.xgate(9, record['offset']))
            .then(ce.Op(9, ce.identity(9), [('phase', record['phase'])])))


def check_binary_formula(ce):
    n, count, orthogonal_count = 3, 0, 0
    identity = tuple(1 << i for i in range(n))
    odd = [q for q in range(1 << n) if ce.parity(q)]
    for g in itertools.product(range(1, 1 << n), repeat=n):
        if ce.rank(g) != n:
            continue
        git = ce.transpose(ce.inv(g, n), n)
        for a, b in itertools.product(odd, repeat=2):
            pa, pb = projection(a, n), projection(b, n)
            ua, ub = add(identity, pa), add(identity, pb)
            aa = add(mm(mm(pb, g, n, ce), ua, n, ce), mm(mm(ub, git, n, ce), pa, n, ce))
            bb = add(mm(mm(pb, g, n, ce), pa, n, ce), mm(mm(ub, git, n, ce), ua, n, ce))
            need((ce.rank(aa) == 0) == (ce.mv(ce.transpose(g, n), b) == a), 'Exact zero-rank condition')
            if ce.parity(b & ce.mv(g, a)) == 0:
                need(ce.rank(bb) == n - 2 and ce.rank(aa) == 2, 'Line-flag rank formula')
                orthogonal_count += 1
            count += 1
    return {'invertible_matrices': 168, 'all_cases': count, 'orthogonal_line_cases': orthogonal_count}


def check_provider(provider, ce):
    f = ce.fourier(9)
    ports = provider['canonical']['ports']
    ranks = Counter()
    witnesses = []
    for edge in provider['transfers']:
        s, t = edge['source'], edge['target']
        a, b = ports[s], ports[t]
        e = recipe_op(edge['response']['recipe'], ce)
        ei = recipe_op(edge['inverse_response']['recipe'], ce)
        need(e.then(ei).tab == ce.identity(9), 'Inverse signed table')
        need(e.then(ei).zero_state() == ce.ident(9).zero_state(), 'Inverse global phase')
        g = tuple(edge['response']['recipe']['matrix_rows'])
        need(ce.parity(b & ce.mv(g, a)) == 0, 'Actual source-to-hole line condition')
        u, v = edge['source_frame_basis'], edge['target_frame_basis']
        need(ce.rank(u + [a]) == len(u), 'Source line in source frame')
        need(all(ce.parity(x & b) == 0 for x in v), 'Target frame in target hole')
        cross = ce.cgate(9, a, -1).then(e).then(ce.cgate(9, b, -1)).then(f)
        hole = f.adjoint().then(ce.cgate(9, a)).then(e).then(ce.cgate(9, b, -1)).then(f)
        full = f.adjoint().then(e).then(f)
        rank = lambda op: ce.rank([x for x, z, phase in op.tab[9:]])
        observed = (rank(cross), rank(hole), rank(full))
        need(observed == (7, 2, 0), 'Actual three physical ranks')
        need(ce.mv(ce.transpose(g, 9), b) != a, 'Hole condition is rejected')
        ranks[str(observed)] += 1
        witnesses.append({'source': s, 'target': t, 'q_source': a, 'q_target': b,
                          'G_transpose_q_target': ce.mv(ce.transpose(g, 9), b)})
    return {'checked_edges': len(witnesses), 'rank_histogram': dict(ranks), 'witnesses': witnesses}


def main():
    raw = gzip.decompress(PAYLOAD.read_bytes())
    need(sha256(raw).hexdigest() == PINS['payload_decompressed'], 'Payload pin')
    need(sha256(COMPILER.read_bytes()).hexdigest() == PINS['compiler'], 'Compiler pin')
    spec = importlib.util.spec_from_file_location('line_flag_clifford', COMPILER)
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    spec.loader.exec_module(ce)
    data = json.loads(raw)
    result = {'status': 'PASS_PHYSICAL_LINE_FLAGS', 'pins': PINS,
              'binary_formula': check_binary_formula(ce),
              'providers': {name: check_provider(p, ce) for name, p in data['providers'].items()},
              'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'proof_sha256': sha256((HERE / 'PHYSICAL-MONOMIAL-CODES.md').read_bytes()).hexdigest()}
    (HERE / 'LINE-FLAGS.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])


if __name__ == '__main__':
    main()
