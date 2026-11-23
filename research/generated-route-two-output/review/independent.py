"""Independent modular, matrix and finite-transition review.

Prepared for Jerry Chen / @CubeJerry with OpenAI assistance. Apache-2.0.
Does not import or run the author's check.py. The frozen transducer is the
implementation under test; expected values use modular inverses and dense
rational right products. Literal source bytes are compiled without .pyc use.
"""
import argparse
from fractions import Fraction as F
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path
import random
import sys
from types import ModuleType


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_bytes(raw, name):
    module = ModuleType(name)
    module.__file__ = '<authenticated-transducer>'
    sys.modules[name] = module
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def digest(data):
    return sha256(data).hexdigest()


def authenticate(package):
    origin_bytes = (package/'ORIGINS.json').read_bytes()
    require(digest(origin_bytes) == 'dd8a63a52021c9429adda3db378cf79f314566602ee4dc582b60ee2aff87d06c',
            'Unreviewed origin manifest')
    require(digest((package/'PROOF.md').read_bytes()) == '5de0684584f6fd9fe80cfa91b1c6ac24f9ca408ca6e59ff1ac11c758acfe40ae',
            'Unreviewed proof bytes')
    origin = json.loads(origin_bytes)
    pins = {}
    for row in origin['files']:
        data = (package/row['path']).read_bytes()
        require(digest(data) == row['sha256'], 'Source SHA256: '+row['path'])
        obj = b'blob '+str(len(data)).encode()+b'\0'+data
        require(sha1(obj).hexdigest() == row['git_blob'], 'Source Git blob: '+row['path'])
        pins[row['path']] = digest(data)
    return pins


def rows(values, q):
    B = q.bit_length()
    return lambda: (tuple((v//(2**i)) % 2 for v in (*values, q)) for i in range(B))


def modular_column(coefficients, D, values, q):
    Z = sum(a*x for a, x in zip(coefficients, values))
    y = (Z*pow(D, -1, q)) % q
    c = (Z-D*y)//q
    require(Z-D*y == q*c, 'Independent modular remainder')
    return y, c


def rational_mod(x, modulus):
    if modulus == 1:
        return 0
    return (x.numerator*pow(x.denominator, -1, modulus)) % modulus


def inverse(word):
    answer = []
    for op in word[::-1]:
        if op[0] == 'swap':
            answer.append(op)
        elif op[0] == 'add':
            answer.append(('add', op[1], op[2], str(-F(op[3]))))
        else:
            answer.append(('scale', op[1], str(1/F(op[2]))))
    return answer


def dense_word(n, word):
    M = [[F(i == j) for j in range(n)] for i in range(n)]
    for op in word:
        if op[0] == 'swap':
            i, j = op[1:]
            for row in M:
                row[i], row[j] = row[j], row[i]
        elif op[0] == 'add':
            i, j, a = op[1], op[2], F(op[3])
            for row in M:
                row[i] += a*row[j]
        else:
            i, a = op[1], F(op[2])
            for row in M:
                row[i] *= a
    return M


def right(x, M):
    return [sum((F(a)*M[i][j] for i, a in enumerate(x)), F(0))
            for j in range(len(M))]


def run(package):
    pins = authenticate(package)
    raw = (package/'transducer.py').read_bytes()
    source_hash = digest(raw)
    require(source_hash == '0cef837c03fcc2830fb77585dfa4a328363738f3aa453af8cb49badb14f5f6c6',
            'Unreviewed transducer bytes')
    subject = load_bytes(raw, '_reviewed_carry_transducer')
    alphabet = json.loads((package/'retained/ALPHABET.json').read_text())
    additions = {F(x) for x in alphabet['addition_coefficients']}
    scales = {F(x) for x in alphabet['scale_coefficients']}
    require(len(additions) == 94 and len(scales) == 15, 'Alphabet census')
    require({-x for x in additions} == additions, 'Addition inverse closure')
    require({1/x for x in scales} == scales, 'Scale inverse closure')
    specs = [(str(x), (x.denominator, x.numerator), x.denominator) for x in sorted(additions)]
    specs += [(str(x), (x.numerator,), x.denominator) for x in sorted(scales)]
    census = []
    transition_corners = local_cases = long_cases = 0
    negative_carries = short_input_denominators = 0
    controls = []

    for label, aa, D in specs:
        s = D.bit_length()-1
        require(D == 2**s, 'Dyadic denominator')
        L, H = sum(min(a, 0) for a in aa), sum(max(a, 0) for a in aa)
        U = max(0, H-1)
        first_bits = len(aa)+2*s+max(s, 2).bit_length()+3
        for j in range(L+1, U+1):
            lo, hi = L-max(j, 0), H-min(j, 0)
            first_bits += (hi-lo).bit_length()
            require(lo <= 0 <= hi, 'First-pass zero state')
            for e in product((0, 1), repeat=len(aa)+1):
                increment = sum(a*b for a, b in zip(aa, e))-j*e[-1]
                for old in {lo, hi}:
                    new = (old+increment)//2
                    require(lo <= new <= hi, 'First-pass affine corner invariant')
                    transition_corners += 1
        second_lo, second_hi = 0, 0
        for c in range(L-D+1, U+1):
            lo, hi = L-max(c, 0), H-min(c, 0)
            second_lo, second_hi = min(second_lo, lo), max(second_hi, hi)
            require(lo <= 0 <= hi, 'Second-pass zero state')
            for e in product((0, 1), repeat=len(aa)+1):
                increment = sum(a*b for a, b in zip(aa, e))-c*e[-1]
                for old in {lo, hi}:
                    new = (old+increment)//2
                    require(lo <= new <= hi, 'Second-pass affine corner invariant')
                    require(old+increment == 2*new+(old+increment) % 2, 'Signed bit equation')
                    transition_corners += 1
        census.append((U-L, first_bits, L-D+1, U, second_lo, second_hi))
        column = subject.Column(aa, s)
        require(column.state_bits() == first_bits, 'Implementation logical-state encoding')
        for q in (3, 5, 11):
            for values in product(range(q), repeat=len(aa)):
                y, c = modular_column(aa, D, values, q)
                result, produced, obs = subject.produce(column, rows(values, q))
                got = sum(bit*2**i for i, bit in enumerate(result))
                B = q.bit_length()
                require((got, produced, len(result)) == (y, c, B), 'Modular oracle mismatch')
                require(obs.first_rows == obs.second_rows == B and obs.flush_rows == s,
                        'Actual input and flush row counts')
                require(obs.input_symbols == 2*(len(aa)+1)*B and obs.output_symbols == B,
                        'Actual symbol read/write census')
                require(obs.quotient_updates == (U-L)*B and obs.comparison_updates == len(aa)*B,
                        'Actual comparison census')
                local_cases += 1
                negative_carries += c < 0
                short_input_denominators += B < s
    require(max(x[0] for x in census) == 54 and max(x[1] for x in census) == 388,
            'Finite first-state maxima')
    require(min(x[2] for x in census) == -54 and max(x[3] for x in census) == 54,
            'Carry numerator extrema')
    require(min(x[4] for x in census) == -54 and max(x[5] for x in census) == 86,
            'Second-state extrema')

    rng = random.Random(202611238092)
    extreme = [x for x in specs if x[0] in ('-23/32', '23/32', '-15', '1/16', '-8')]
    for bits in (193, 257, 1025, 4097):
        q = (1 << (bits-1)) | rng.getrandbits(bits-1) | 1
        for label, aa, D in extreme:
            values = tuple(q-1 if i % 2 == 0 else q//2 for i in range(len(aa)))
            expected, c = modular_column(aa, D, values, q)
            out, observed_c, _ = subject.produce(subject.Column(aa, D.bit_length()-1), rows(values, q))
            require(sum(b << i for i, b in enumerate(out)) == expected and c == observed_c,
                    'Long modular oracle')
            long_cases += 1

    cases = json.loads((package/'retained/CASES.json').read_text())
    matrix_cases = inverse_cases = reconstruction_cases = prefix_register_checks = 0
    all_source_opcodes = 0
    for case in cases:
        n, word = case['n'], case['word']
        for op in word+case['inverse_word']:
            if op[0] == 'add':
                require(F(op[3]) in additions, 'Generated addition escaped source alphabet')
            elif op[0] == 'scale':
                require(F(op[2]) in scales, 'Generated scale escaped source alphabet')
            else:
                require(op[0] == 'swap', 'Unknown source opcode')
            all_source_opcodes += 1
        M, Mi = dense_word(n, word), dense_word(n, inverse(word))
        for q in (5, 9, 21):
            row = [rng.randrange(q) for _ in range(n)]
            exact = right(row, M)
            low = [rational_mod(x, q) for x in exact]
            carry = [(x-y)/q for x, y in zip(exact, low)]
            result = subject.evaluate_row(word, row, q)
            require(result['low'] == low, 'Dense right-product low oracle')
            require([F(x, 1 << result['denominator_exponent']) for x in result['carry_numerators']] == carry,
                    'Dense rational carry oracle')
            back = subject.evaluate_row(inverse(word), low, q)
            require(back['low'] == row, 'Separate inverse low execution')
            back_carry = [F(x, 1 << back['denominator_exponent']) for x in back['carry_numerators']]
            require([a+b for a, b in zip(right(carry, Mi), back_carry)] == [0]*n,
                    'Inverse cocycle at committed low output')
            matrix_cases += 1
            inverse_cases += 1
            for w in (1, 2, 5):
                modulus = q**(w-1)
                high = [rng.randrange(modulus) for _ in range(n)]
                whole = [a+q*b for a, b in zip(row, high)]
                whole_expected = [rational_mod(x, q**w) for x in right(whole, M)]
                high_result = [rational_mod(x+y, modulus) for x, y in zip(right(high, M), carry)]
                require([a+q*b for a, b in zip(low, high_result)] == whole_expected,
                        'Independent q-power reconstruction')
                reconstruction_cases += 1
            # Independent prefix ledger: direct modular division supplies local c.
            current = row[:]
            numerators = [0]*n
            den = P = 1
            for op in word:
                if op[0] == 'swap':
                    i, j = op[1:]
                    current[i], current[j] = current[j], current[i]
                    numerators[i], numerators[j] = numerators[j], numerators[i]
                    continue
                i = op[1]
                a = F(op[3] if op[0] == 'add' else op[2])
                D, an = a.denominator, a.numerator
                A = D+abs(an) if op[0] == 'add' else max(D, abs(an))
                nextP = P*A
                if op[0] == 'add':
                    j = op[2]
                    y, c = modular_column((D, an), D, (current[i], current[j]), q)
                    partial = D*numerators[i]+an*numerators[j]
                else:
                    y, c = modular_column((an,), D, (current[i],), q)
                    partial = an*numerators[i]
                require(abs(partial) < 2*nextP, 'Joint D+|a| partial bound')
                require(abs(c*den) < 2*nextP, 'Carry injection bound')
                update = [D*x for x in numerators]
                update[i] = partial+c*den
                require(all(abs(x) < 4*nextP for x in update), 'Every intermediate carry register')
                numerators, current[i], den, P = update, y, den*D, nextP
                require(all(abs(x) < 2*P for x in numerators), 'Completed-prefix carry envelope')
                prefix_register_checks += n+2
            require(current == low and [F(x, den) for x in numerators] == carry,
                    'Independent common-denominator composition')
            require(result['envelope']['signed_work_bits'] >= (4*P).bit_length()+1,
                    'Signed work capacity covers strict4P envelope')

    # Full source ambient: no omitted spectator rows or coordinates.
    port = next(c for c in cases if c['label'] == 'actual_port/17')
    headM = dense_word(15, port['word'])
    ambient_coordinates = 0
    for q in (7, 15):
        for row_index in range(134):
            row = [(row_index+3*j+row_index*j) % q for j in range(134)]
            head = right(row[:15], headM)
            low = [rational_mod(x, q) for x in head]
            carry = [(x-y)/q for x, y in zip(head, low)]
            actual = subject.evaluate_row(port['word'], row, q)
            require(actual['low'][:15] == low and actual['low'][15:] == row[15:],
                    'Full134 low field and spectator return')
            decoded = [F(x, 1 << actual['denominator_exponent']) for x in actual['carry_numerators']]
            require(decoded[:15] == carry and decoded[15:] == [0]*119, 'Full134 carry spectators')
            ambient_coordinates += 134

    # Every odd radix in a larger independently chosen range, not just primes.
    latency_radices = latency_prefixes = 0
    for q in range(5, 1024, 2):
        B = q.bit_length()
        K = 1 << (B-2)
        a, r = divmod(q, K)
        require(a in (2, 3) and 1 <= r < K and K % 2 == 0, 'Odd-radix decomposition')
        zero_outputs = set()
        for t in range(K):
            if a == 3:
                x, y = t+2*K, 2*K
            elif t < r:
                x, y = t+2*K, K
            else:
                x, y = t+K, K
            require(0 <= x < q and 0 <= y < q and q <= x+y < 2*q, 'Canonical crossing completion')
            require(x % K == t and y % K == 0, 'Same complete read prefix')
            require(((x+y) % q) % 2 != t % 2, 'Opposite first output bit')
            zero_outputs.add((t+0) % q)
            latency_prefixes += 1
        require(len(zero_outputs) == K, 'Distinct common-continuation output classes')
        latency_radices += 1
    require((2+4) % 6 % 2 == 0, 'Even-radix parity scope control')
    controls.append('even_radix_invalidates_parity_discriminator')

    # Mutate the actual implementation under test; the independent modular/dense
    # oracle must detect each fault. No author checker is used.
    def caught(call, expected):
        try:
            return call() != expected
        except (ValueError, ZeroDivisionError):
            return True
    noflush = load_bytes(raw.replace(b'for _ in range(column.denominator_exponent):', b'for _ in range(0):'), '_review_no_flush')
    def flush_result():
        bits, c, _ = noflush.produce(noflush.Column((1,), 1), rows((1,), 3))
        return sum(b << i for i, b in enumerate(bits)), c, len(bits)
    require(caught(flush_result, (2, -1, 2)), 'Missing flush mutant survived')
    controls.append('omitted_zero_flush')
    changed = raw.replace(b'updated = [x << s for x in numerators]', b'updated = list(numerators)')
    badshift = load_bytes(changed, '_review_no_denominator_shift')
    word = [('add', 0, 1, '1/2'), ('scale', 1, '1/2')]
    exact = right((0, 1), dense_word(2, word))
    expected_low = [rational_mod(x, 3) for x in exact]
    expected_carry = [(x-y)/3 for x, y in zip(exact, expected_low)]
    def shifted_result():
        result = badshift.evaluate_row(word, (0, 1), 3)
        return result['low'], [F(x, 1 << result['denominator_exponent']) for x in result['carry_numerators']]
    require(caught(shifted_result, (expected_low, expected_carry)), 'Missing global denominator shift survived')
    controls.append('omitted_unaffected_denominator_shift')
    source = raw.decode()
    old = '(states[index] + digit - j * radix) // 2'
    require(old in source, 'Signed-floor mutant source binding')
    altered = source.replace(old, '((1 if states[index]+digit-j*radix >= 0 else -1) * (abs(states[index]+digit-j*radix)//2))')
    badfloor = load_bytes(altered.encode(), '_review_truncated_signed_state')
    detected = False
    for q in (3, 5, 7):
        for x, y in product(range(q), repeat=2):
            expected = modular_column((2, -1), 2, (x, y), q)
            try:
                bits, c, _ = badfloor.produce(badfloor.Column((2, -1), 1), rows((x, y), q))
                detected |= (sum(b << i for i, b in enumerate(bits)), c) != expected
            except ValueError:
                detected = True
    require(detected, 'Signed truncation mutant survived')
    controls.append('truncated_negative_quotient_state')
    damaged = bytearray((package/'retained/ALPHABET.json').read_bytes())
    damaged[-1] ^= 1
    require(digest(damaged) != pins['retained/ALPHABET.json'], 'Source corruption negative control')
    controls.append('source_corruption')

    return dict(schema='independent-low-carry-review/1', status='PASS_INDEPENDENT_LOW_AND_CARRY',
                implementation_sha256=source_hash, source_bindings=pins,
                local_modular_cases=local_cases, negative_carry_cases=negative_carries,
                B_less_than_s_cases=short_input_denominators, long_modular_cases=long_cases,
                transition_interval_corners=transition_corners,
                first_state_bits=388, max_quotient_comparators=54,
                carry_numerator_range=[-54,54], second_state_range=[-54,86],
                dense_matrix_cases=matrix_cases, inverse_cases=inverse_cases,
                q_power_reconstructions=reconstruction_cases,
                prefix_register_checks=prefix_register_checks,
                source_opcodes_checked=all_source_opcodes,
                complete_ambient_coordinates=ambient_coordinates,
                one_pass_radices=latency_radices, one_pass_prefixes=latency_prefixes,
                rejected_controls=controls,
                scope='Finite corroboration plus separate written universal review; not a physical payload route or complete foundational discharge')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(run(args.package.resolve()), sort_keys=True, indent=2)+'\n'
    if args.output:
        args.output.write_text(result)
    print(result, end='')
