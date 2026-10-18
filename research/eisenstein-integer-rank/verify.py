#!/usr/bin/env python3
"""Complete retained-call comparison and effective exact-domain controls."""
from collections import Counter
from contextlib import redirect_stdout
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import integer_rank as fast
import retained


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError('ineffective rejection: '+label)


def capture(old):
    stream = io.StringIO()
    with redirect_stdout(stream):
        old.main()
    return stream.getvalue()


def experiment():
    old = retained.load()
    original = old.rank
    census = []
    counts = Counter()
    def observed(matrix, field='K'):
        counts[field] += 1
        before = deepcopy(matrix)
        expected = original(matrix, field)
        if field == 'K':
            actual = fast.rank(matrix)
            fast.need(actual == expected, 'retained K call disagreement')
            fast.need(matrix == before, 'integer rank modified retained input')
            payload = [[[str(a), str(b)] for a, b in row] for row in matrix]
            census.append([payload, actual])
        return expected
    old.rank = observed
    original_text = capture(old)
    fast.need(counts == {'K': 359, 'F4': 311, 'Q': 209}, 'retained rank coverage')
    old.rank = original
    retained.install(old)
    accelerated_text = capture(old)
    fast.need(original_text == accelerated_text, 'complete retained output differs')
    receipt = json.loads(original_text[:original_text.rfind('\nPASS_')])
    fast.need(len(receipt['negative_controls']) == 7, 'retained semantic controls')
    controls = []
    zero, one, omega = (F(0), F(0)), (F(1), F(0)), (F(0), F(1))
    dependent = [[one, omega], [omega, (F(-1), F(-1))]]
    fast.need(fast.rank(dependent) == 1, 'Eisenstein multiplication relation')
    controls.append('omega squared equals minus omega minus one')
    fast.need(fast.rank([[(F(2), F(0))]]) == 1, 'unlucky mod-two specialization')
    controls.append('rank not inferred from reduction modulo two')
    huge = 1 << 160
    close = [[one, one], [one, (F(huge+1, huge), F(0))]]
    fast.need(fast.rank(close) == 2 and float(F(huge+1, huge)) == 1.0,
              'exact near-dependence control')
    controls.append('floating near-dependence is not equality')
    matrix = [[one, zero], [zero, one]]
    fast.need(fast.rank(matrix) == 2, 'mutation positive control')
    matrix[1][1] = zero
    fast.need(fast.rank(matrix) == 1, 'input mutation recomputed')
    controls.append('same-object mutation is recomputed')
    controls.append(reject(lambda: fast.rank([[one], []]), 'ragged matrix'))
    controls.append(reject(lambda: fast.rank([[(1.0, 0)]]), 'float entry'))
    controls.append(reject(lambda: fast.rank([[(True, 0)]]), 'boolean entry'))
    old.rank = lambda matrix, field='K': 0 if field == 'K' else original(matrix, field)
    controls.append(reject(lambda: capture(old), 'wrong K rank rejected by unchanged verifier'))
    return {'status': 'PASS_EISENSTEIN_INTEGER_RANK', 'rank_calls': dict(counts),
            'K_call_digest': hashlib.sha256(canonical(census).encode()).hexdigest(),
            'complete_stdout_sha256': hashlib.sha256(original_text.encode()).hexdigest(),
            'retained_receipt': receipt, 'controls': controls,
            'same_object_rank_after_mutation': fast.rank(matrix),
            'scope': 'Optional exact K-rank adapter; complete original verifier and output retained; Q/F4 paths unchanged.'}


def main():
    result = experiment()
    if sys.argv[1:] == ['--write']:
        with (HERE/'RESULT.json').open('x', encoding='utf-8', newline='\n') as out:
            out.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        fast.need(not sys.argv[1:], 'unknown arguments')
        fast.need(canonical(json.loads((HERE/'RESULT.json').read_text())) == canonical(result),
                  'typed receipt mismatch')
    print('PASS_EISENSTEIN_INTEGER_RANK K=359 F4=311 Q=209 retained_controls=7 controls=8')


if __name__ == '__main__':
    main()
