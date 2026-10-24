"""One-pass norm-six feature pairs without a feature/transform table.

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
The caller borrows G,x,y read-only, consumes each emitted record, and releases
it before requesting the next. Retaining outputs is additional caller storage.
The caller must keep all three inputs immutable for the iterator's lifetime.
No physical/native gate or tape tariff is implied by integer-array slots.
"""

from math import comb
from compression import integer_vector, require, validate_gram

DENOMINATOR = 256


def feature_stream(gram, x, y, a=0, b=4):
    """Yield (feature_key, integer_source, integer_target_numerator).

    Sum source*numerator/256 gives K for integral q(x)=q(y)=6. The iterator
    itself does not enforce the shell precondition or buffer emitted records.
    Its only owned arrays are v, nu, xsq, vsq, each of length d. There is no
    feature list, relation matrix, transform descriptor or output accumulator.
    """
    d = validate_gram(gram, a, b)
    integer_vector(x, d, 'source')
    integer_vector(y, d, 'target')
    v = [0]*d
    for i in range(d):
        total = gram[i][0]*y[0]
        for j in range(1, d):
            total += gram[i][j]*y[j]
        v[i] = total
    nu = [0]*d
    p = v[a]*v[b]
    numerator_a = p*(v[a]+3*v[b])
    numerator_b = p*(3*v[a]+v[b])
    require(numerator_a % 2 == numerator_b % 2 == 0, 'integer parity identity')
    nu[a], nu[b] = numerator_a//2, numerator_b//2
    for i in range(d):
        if i != a and i != b:
            nu[i] = gram[i][b]*nu[a] + gram[i][a]*nu[b] - 8*p*v[i]
    xsq = [u*u for u in x]
    vsq = [u*u for u in v]

    for i in range(d):
        h = gram[i][i]//2
        source = (xsq[i]*x[i]-x[i])//3
        target = 4*vsq[i]*v[i] - 3*h*nu[i]
        yield ('f', i), source, target
    for i in range(d):
        h = gram[i][i]//2
        target = 4*((vsq[i]*v[i]-4*v[i])//3) - (h-3)*nu[i]
        yield ('l', i), x[i], target
    for i in range(d):
        h = gram[i][i]//2
        for j in range(d):
            if i == j or (i == a and j == b) or (i == b and j == a):
                continue
            source = xsq[i]*x[j]
            target = 4*vsq[i]*v[j] - gram[i][j]*nu[i] - h*nu[j]
            yield ('s', i, j), source, target
    for i in range(d):
        for j in range(i+1, d):
            for k in range(j+1, d):
                if ((i == a or j == a or k == a)
                        and (i == b or j == b or k == b)):
                    continue
                source = x[i]*x[j]*x[k]
                target = (8*v[i]*v[j]*v[k] - gram[j][k]*nu[i]
                          - gram[i][k]*nu[j] - gram[i][j]*nu[k])
                yield ('t', i, j, k), source, target


def stream_budget(d):
    """Fixed indexed-integer algorithm bounds, not Python heap measurements."""
    require(type(d) is int and 2 <= d <= 48, 'invalid budget dimension')
    n = comb(d+2, 3)
    return {
        'emitted_pairs': n,
        'immutable_gram_slots': d*d,
        'per_feature_descriptor_slots': 0,
        'target_accumulator_array_slots': 0,
        'owned_vector_slots': 4*d,
        'borrowed_source_target_slots': 2*d,
        'scalar_counter_record_slots_upper': 32,
        'combined_live_slots_upper': 6*d+32,
        'combined_live_plus_gram_slots_upper': d*d+6*d+32,
        'multiplications_upper': d*d+6*d-3+8*n,
        'additions_subtractions_upper': d*d+d-2+3*n,
        'feature_exact_divisions_by_3': 2*d,
        'multiplier_exact_divisions_by_2': 2,
        'public_diagonal_halvings_upper': 3*d,
        'indexed_reads_writes_upper': 128*n+32*d*d,
        'common_target_denominator': DENOMINATOR,
    }
