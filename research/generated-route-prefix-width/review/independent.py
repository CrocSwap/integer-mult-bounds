"""Independent prefix-width review: exact matrices and modular carry oracle.

The retained emitter and prefix evaluator are subjects. No author checker is
loaded. Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path
import random
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def need(value, why):
    if not value:
        raise ValueError(why)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def auth(package):
    pin = json.loads((HERE / 'FROZEN-INPUTS.json').read_text())
    for name, expected in pin['files'].items():
        need(digest((package / name).read_bytes()) == expected, 'input hash: ' + name)
    origins = json.loads((package / 'ORIGINS.json').read_text())
    blobs = {}
    for name, entry in origins['files'].items():
        raw = (package / name).read_bytes()
        need(digest(raw) == entry['sha256'], 'retained sha: ' + name)
        parent = entry.get('retained_parent_origin')
        if parent:
            blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(blob == parent['git_blob'], 'retained git blob: ' + name)
            blobs[name] = blob
    return pin, blobs


def load_subject(package):
    spec = importlib.util.spec_from_file_location('reviewed_prefix_subject', package / 'prefix.py')
    subject = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = subject
    spec.loader.exec_module(subject)
    return subject


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def elementary(n, op):
    """Build a right-action matrix from its mathematical definition."""
    out = identity(n)
    kind, i = op[:2]
    if kind == 'swap':
        j = op[2]
        out[i][i] = out[j][j] = F(0)
        out[i][j] = out[j][i] = F(1)
    elif kind == 'add':
        j, a = op[2:]
        out[j][i] = F(a)
    elif kind == 'scale':
        out[i][i] = F(op[2])
    else:
        raise ValueError('oracle unknown operation')
    return out


def matmul(a, b):
    """General exact matrix product, with zero skipping only."""
    sparse = [[(j, v) for j, v in enumerate(row) if v] for row in b]
    out = [[F(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, av in enumerate(row):
            if av:
                for j, bv in sparse[k]:
                    out[i][j] += av * bv
    return out


def stats(matrix):
    d = 0
    for row in matrix:
        for value in row:
            den = value.denominator
            need(den & (den - 1) == 0, 'non-dyadic oracle matrix')
            d = max(d, den.bit_length() - 1)
    norm = max(sum(abs(row[j]) for row in matrix) for j in range(len(matrix[0])))
    e = 0
    while F(1 << e) < norm:
        e += 1
    return d, e, norm


def normalized(word):
    return [tuple(op[:3]) + (str(F(op[3])),) if op[0] == 'add'
            else (op[0], op[1], str(F(op[2]))) if op[0] == 'scale'
            else tuple(op) for op in word]


def inverse_word(word):
    return [(op[0], op[1], op[2], str(-F(op[3]))) if op[0] == 'add'
            else (op[0], op[1], str(1 / F(op[2]))) if op[0] == 'scale'
            else tuple(op) for op in reversed(word)]


def restore(fw, item):
    return fw.Recipe(item['kind'], item['n'], fw.Count(**item['count']),
                     tuple(restore(fw, x) for x in item['children']), item['data'])


def matrix_prefixes(word, n, cert, counters):
    matrix = identity(n)
    observed = (0, 0)
    for op in word:
        matrix = matmul(matrix, elementary(n, op))
        d, e, norm = stats(matrix)
        need(d <= cert[0] and norm <= (1 << cert[1]), 'prefix certificate exceeded')
        observed = max(observed[0], d), max(observed[1], e)
        counters['matrix_prefixes'] += 1
        counters['matrix_entries'] += n * n
    return matrix, observed


def canonical(value, q):
    return value.numerator * pow(value.denominator, -1, q) % q


def row_oracle(word, source, q, cert, counters):
    d, e = cert
    D = 1 << d
    actual = [F(x) for x in source]
    low = list(source)
    p = [0] * len(source)
    result = []
    peak = 0
    for op in word:
        previous_low, previous_p = list(low), list(p)
        actual = matmul([actual], elementary(len(source), op))[0]
        low = [canonical(v, q) for v in actual]
        carry = [(value - y) * D / q for value, y in zip(actual, low)]
        need(all(v.denominator == 1 for v in carry), 'fixed carry denominator failed')
        p = [int(v) for v in carry]
        need(all(abs(v) < 1 << (d + e + 1) for v in p), 'stored width oracle failed')
        if op[0] != 'swap':
            i = op[1]
            coefficient = F(op[3] if op[0] == 'add' else op[2])
            den, a = coefficient.denominator, coefficient.numerator
            if op[0] == 'add':
                j = op[2]
                Z = den * previous_low[i] + a * previous_low[j]
                old = den * previous_p[i] + a * previous_p[j]
            else:
                Z = a * previous_low[i]
                old = a * previous_p[i]
            c = F(Z - den * low[i], q)
            need(c.denominator == 1 and abs(c) <= 54, 'independent local carry bound')
            c = int(c)
            combined = old + c * D
            need(combined % den == 0 and combined // den == p[i], 'combined exact update')
            need(max(abs(old), abs(c * D), abs(combined)) < 1 << (d + e + 8), 'work width oracle')
            peak = max(peak, abs(old), abs(c * D), abs(combined))
            counters['arithmetic_updates'] += 1
            counters['negative_local_carries'] += c < 0
            counters['d_less_than_s_updates'] += d < den.bit_length() - 1
            counters['nondivisible_individual_terms'] += bool(old % den or (c * D) % den)
        result.append((tuple(low), tuple(p)))
        counters['carry_coordinates'] += len(source)
    return result, peak


def verify_rows(subject, word, n, cert, counters, samples):
    for q, source in samples:
        expected, peak = row_oracle(word, source, q, cert, counters)
        got = subject.evaluate_row(word, source, q, cert, trace=True)
        need(got['trace'] == expected, 'subject per-prefix low/carry differs from rational oracle')
        need(got['peak'] == peak, 'subject work peak')
        need(got['signed_work_bits'] == sum(cert) + 9, 'signed width declaration')
        arithmetic = sum(op[0] != 'swap' for op in word)
        need(got['first_rows'] == got['second_rows'] == arithmetic * q.bit_length(), 'two-pass access census')
        counters['row_runs'] += 1


def rejects(action, label):
    try:
        action()
    except (ValueError, AssertionError, ZeroDivisionError):
        return label
    raise ValueError('negative control survived: ' + label)


def main(package):
    pin, blobs = auth(package)
    subject = load_subject(package)
    fw = subject.fw
    inventory = json.loads((package/'retained/ALPHABET.json').read_text())
    additions = {F(x) for x in inventory['addition_coefficients']}
    scales = {F(x) for x in inventory['scale_coefficients']}
    need(len(additions)==94 and len(scales)==15, 'retained alphabet inventory')
    need(all(-a in additions and a.denominator+abs(a.numerator)<=55 for a in additions), 'addition reversal and joint coefficient bound')
    need(all(1/a in scales and max(abs(a.numerator),a.denominator)<=16 for a in scales), 'scale inversion and coefficient bound')
    need({F(2),F(-2),F(1,2),F(-1,2),F(-1)}<=scales, 'atomic scale alphabet closure')
    cases = json.loads((package / 'retained' / 'CASES.json').read_text())
    counters = dict(matrix_prefixes=0, matrix_entries=0, carry_coordinates=0,
                    arithmetic_updates=0, negative_local_carries=0,
                    d_less_than_s_updates=0, nondivisible_individual_terms=0,
                    row_runs=0, recipe_variants=0)
    rng = random.Random(20261123)
    certificates = {}
    observed = {}
    recipes = [(case['label'], restore(fw, case['recipe']), case) for case in cases]
    seed = recipes[0][1]
    sector = fw.direct_sum(seed, recipes[1][1])
    for rank in range(sector.n + 1):
        recipes.append(('review/guard-rank-' + str(rank), fw.guarded(seed, sector, rank), None))
    small_power = seed
    for r in range(2, 5):
        small_power = fw.tensor(small_power, seed)
        recipes.append(('review/fixed-two-tensor-' + str(r), small_power, None))
    # Diagnostic legal unit word, not a new admitted source seed. Both directions
    # are integral throughout; it forces combined division with d=0<s=1.
    cancellation = fw.literal(2, [('scale', 0, '2'), ('scale', 0, '1/2')], 'review/cancellation')
    recipes.append(('review/cancellation', cancellation, None))
    for label, recipe, source_case in recipes:
        cert = subject.certificate(recipe)
        certificates[label] = list(cert)
        endpoints = {}
        aggregate = (0, 0)
        for inverted in (False, True):
            native = normalized(fw.emit(recipe, inverted))
            if source_case:
                need(native == normalized(source_case['inverse_word' if inverted else 'word']), 'retained chronology changed')
            if inverted:
                # Guards and conjugates invert semantically, but need not equal
                # the literal reversed list because their boundary words persist.
                pass
            for lowered in (False, True):
                word = normalized(fw.expanded_ordered_ops(recipe, inverted)) if lowered else native
                end, found = matrix_prefixes(word, recipe.n, cert, counters)
                aggregate = max(aggregate[0], found[0]), max(aggregate[1], found[1])
                if lowered:
                    need(end == endpoints[(inverted, False)], 'lowered endpoint changed')
                    need(all(op[0] != 'add' or op[1] > op[2] for op in word), 'ordered lowering index')
                    need(all(op[0] != 'scale' or F(op[2]) in (2, -2, F(1,2), F(-1,2), -1) for op in word), 'scale atom closure')
                endpoints[(inverted, lowered)] = end
                samples = [(3, [0] * recipe.n), (5, [4] * recipe.n),
                           (17, [rng.randrange(17) for _ in range(recipe.n)])]
                if label == 'review/cancellation':
                    samples += [(q, [x, q-1-x]) for q in (3,5,7,9,17) for x in range(q)]
                verify_rows(subject, word, recipe.n, cert, counters, samples)
                counters['recipe_variants'] += 1
        need(matmul(endpoints[(False, False)], endpoints[(True, False)]) == identity(recipe.n), 'source inverse matrix identity')
        if recipe.kind == 'literal':
            need(tuple(cert) == aggregate, 'literal minimal dyadic/logarithmic certificate')
        observed[label] = list(aggregate)
    actual = next(recipe for label, recipe, _ in recipes if label == 'actual_relative')
    c0 = subject.certificate(actual)
    need(c0 == (2, 4), 'retained eight-dimensional base certificate')
    current = actual
    symbolic = []
    m0 = actual.count.adds + actual.count.scales
    for r in range(1, 26):
        if r > 1:
            current = fw.tensor(current, actual)
        cert = subject.certificate(current)
        need(cert == (2*r,4*r), 'symbolic fixed-base tensor certificate')
        need(current.n == 8**r and current.count.adds + current.count.scales == r*8**(r-1)*m0, 'symbolic instruction recurrence')
        symbolic.append([r, current.n, sum(cert)+9])
    verify_rows(subject, normalized(fw.emit(actual)), actual.n, c0, counters,
                [((1 << b)-1, [(1 << b)-2 if i % 2 else i for i in range(actual.n)]) for b in (65,257)])
    controls = []
    # Max-row norm 2 but max-column norm 3; canonical row nearly saturates it.
    wrong = [[F(1),F(0),F(0)], [F(1),F(1),F(0)], [F(1),F(0),F(1)]]
    rownorm = max(sum(abs(v) for v in row) for row in wrong)
    controls.append(rejects(lambda: need(stats(wrong)[2] <= rownorm, 'row-norm substituted'), 'wrong-norm-direction'))
    # Understated bound misses growth and later cancellation.
    controls.append(rejects(lambda: matrix_prefixes(normalized(fw.emit(cancellation)),2,(0,0),dict(matrix_prefixes=0,matrix_entries=0)), 'endpoint-only-bound'))
    half = [('scale',0,'1/2')]
    controls.append(rejects(lambda: row_oracle(half,[1,0],3,(0,1),counters.copy()), 'too-small-common-denominator'))
    # p=1 and c=-1 must combine to 0 before /2; termwise floor gives -1.
    controls.append(rejects(lambda: need((1//2)+(-1//2)==(1-1)//2,'termwise floor division'), 'separate-summand-division'))
    mutation = (package/'prefix.py').read_text().replace('numerator=old+c*D','numerator=old')
    mutant = dict(subject.__dict__)
    exec(compile(mutation,str(package/'prefix.py'),'exec'),mutant)
    controls.append(rejects(lambda: need(mutant['evaluate_row']([('scale',0,'2')],[2,0],3,(0,1),True)['trace']==[((1,0),(1,0))], 'lost local carry'), 'lost-elementary-carry'))
    # Wrong coefficient/phase or omitted boundary is visible to full matrix oracle.
    guard = fw.guarded(seed, sector, sector.n)
    gcert = subject.certificate(guard)
    controls.append(rejects(lambda: matrix_prefixes(normalized(fw.emit(guard)),guard.n,subject.certificate(seed),dict(matrix_prefixes=0,matrix_entries=0)), 'omitted-guard-boundaries'))
    conj = fw.conjugate(seed, recipes[1][1])
    controls.append(rejects(lambda: matrix_prefixes(normalized(fw.emit(conj)),conj.n,subject.certificate(recipes[1][1]),dict(matrix_prefixes=0,matrix_entries=0)), 'omitted-conjugation-boundaries'))
    ordered = normalized(fw.expanded_ordered_ops(actual))
    damaged = list(ordered)
    k = next(i for i,op in enumerate(damaged) if op[0]=='swap')
    damaged.pop(k)
    end1,_ = matrix_prefixes(ordered,actual.n,c0,dict(matrix_prefixes=0,matrix_entries=0))
    def check_damaged():
        end2,_ = matrix_prefixes(damaged,actual.n,(100,100),dict(matrix_prefixes=0,matrix_entries=0))
        need(end1==end2,'omitted lowered swap')
    controls.append(rejects(check_damaged,'omitted-lowering-swap'))
    controls.append(rejects(lambda: need(digest((package/'retained/factor_words.py').read_bytes()+b'\n')==pin['files']['retained/factor_words.py'],'corrupted source'),'source-byte-corruption'))
    need(counters['d_less_than_s_updates'] and counters['nondivisible_individual_terms'] and counters['negative_local_carries'],'missing boundary coverage')
    return dict(status='pass',review='independent structural prefix-width review',inputs=pin,
                source_git_blobs=blobs,alphabet_sizes=[len(additions),len(scales)],retained_cases=len(cases),recipe_cases=len(recipes),
                counters=counters,certificates=certificates,observed_prefix_bounds=observed,
                symbolic_fixed_base=symbolic,negative_controls=controls,
                limitations=['finite executable evidence; structural induction supplies universal statement',
                             'no author checker imported or run','symbolic eight-dimensional tensor family not materialized',
                             'fixed-seed tensor O(log N) only; arbitrary selected expression remains open',
                             'logical arithmetic and supplied-row access bound, not Python tape usage or whole multiplier'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = main(args.package.resolve())
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'counters':result['counters'],'controls':len(result['negative_controls'])},sort_keys=True))
