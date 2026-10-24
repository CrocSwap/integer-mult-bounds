#!/usr/bin/env python3
"""Independent exact audit of #4176's low-class/pivot implication.

The determinant/adjugate reference does not import predecessor arithmetic.
Literal predecessor routines are compared with it, including binary Words.
Prepared for mihir-s-05 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
from math import gcd, prod
from pathlib import Path
import importlib
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = ROOT / 'research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def det(a):
    """Leibniz determinant, including the empty minor; only n<=3 here."""
    n = len(a)
    total = 0
    for p in permutations(range(n)):
        sign = (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i+1, n))
        total += sign * prod(a[i][p[i]] for i in range(n))
    return total


def minor(a, rows, cols):
    return [[a[i][j] for j in cols] for i in rows]


def inverse(a, modulus):
    n = len(a)
    d = det(a) % modulus
    require(gcd(d, modulus) == 1, 'independent inverse requires a unit determinant')
    scale = pow(d, -1, modulus)
    return [[((-1)**(i+j) * det(minor(a, [k for k in range(n) if k != j],
                                    [k for k in range(n) if k != i])) * scale) % modulus
             for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    return [[sum(x*y for x, y in zip(row, col)) % modulus
             for col in zip(*b)] for row in a]


def projection(g, r, modulus):
    return multiply([row[:r] for row in g], inverse(g, modulus)[:r], modulus)


def leading(a, r, modulus):
    return [det(minor(a, range(k), range(k))) % modulus for k in range(1, r+1)]


def is_good(a, r, modulus):
    return all(gcd(x, modulus) == 1 for x in leading(a, r, modulus))


def complementary(g, r, k, signed=True):
    n = len(g)
    first = tuple(range(k))
    total = 0
    for cols in combinations(range(r), k):
        sign = (-1)**(sum(first)+sum(cols)) if signed else 1
        total += sign * det(minor(g, first, cols)) * det(minor(
            g, range(k, n), [j for j in range(n) if j not in cols]))
    return total


def all_gl(n, q):
    for flat in product(range(q), repeat=n*n):
        g = [list(flat[i*n:(i+1)*n]) for i in range(n)]
        if det(g) % q:
            yield g


def diagonal_conjugate(a, weights, modulus):
    inverses = [pow(x, -1, modulus) for x in weights]
    return [[x * weights[i] * inverses[j] % modulus for j, x in enumerate(row)]
            for i, row in enumerate(a)]


def expect_rejection(call, text):
    try:
        call()
    except ValueError as error:
        require(text in str(error), 'wrong rejection: ' + str(error))
    else:
        raise ValueError('missing rejection: ' + text)


def authenticate():
    checked = {}
    for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink(), 'regular source: ' + row['path'])
        digest = sha256(path.read_bytes()).hexdigest()
        require(digest == row['sha256'], 'source digest: ' + row['path'])
        checked[row['path']] = digest
    return checked


def finite_fields(oracle):
    counts, bad_prefix, sign_witness = [], None, None
    for n, q in [(2, 3), (2, 5), (2, 7), (3, 3)]:
        census = Counter()
        gl_count = 0
        for g in all_gl(n, q):
            gl_count += 1
            for r in range(1, n):
                p = projection(g, r, q)
                require(multiply(p, p, q) == p, 'split projector identity')
                minors = leading(p, r, q)
                good = all(minors)
                try:
                    actual = oracle.good_pivots(p, r, q)
                except ValueError:
                    actual = None
                require((actual is not None) == good, 'literal low oracle vs determinant classification')
                if good:
                    require(actual == [x*pow(y, -1, q) % q for x, y in
                                       zip(minors, [1]+minors[:-1])], 'pivot ratios')
                census[(r, good)] += 1
                for k, value in enumerate(minors, 1):
                    f = complementary(g, r, k)
                    require(f % q == det(g)*value % q, 'complementary-minor identity')
                    if sign_witness is None and complementary(g, r, k, False) % q != f % q:
                        sign_witness = dict(q=q, rank=r, k=k, header=g,
                                            correct=f % q, unsigned=complementary(g,r,k,False) % q)
                for weights in product(range(1, q), repeat=n):
                    weighted = diagonal_conjugate(p, weights, q)
                    require(leading(weighted, r, q) == minors, 'diagonal-unit principal minors')
                if r == 2 and not good and minors[-1] and bad_prefix is None:
                    bad_prefix = dict(q=q, rank=r, header=g, projector=p, leading_minors=minors)
        require(gl_count == prod(q**n-q**j for j in range(n)), 'complete GL enumeration')
        for r in range(1, n):
            fraction = Fraction(census[(r, False)], gl_count)
            bound = min(Fraction(1), Fraction(n*r*(q-1), q*(q-2)))
            require(fraction <= bound, 'finite census within proved bound')
            if n == 2:
                require(fraction == Fraction(2*q-1,q*(q+1)), 'independent rank-one projection count')
            counts.append(dict(n=n,q=q,rank=r,gl=gl_count,good=census[(r,True)],
                               bad=census[(r,False)],bad_fraction=str(fraction),bound=str(bound)))
    require(bad_prefix is not None, 'intermediate-minor negative witness')
    require(sign_witness is not None, 'complementary-sign negative witness')
    return counts, bad_prefix, sign_witness


def local_ring_lifts(oracle):
    counts, witness = Counter(), None
    q, modulus = 3, 9
    units = [x for x in range(modulus) if gcd(x, modulus) == 1]
    for low in all_gl(2, q):
        low_good = is_good(projection(low, 1, q), 1, q)
        for digits in product(range(q), repeat=4):
            high = [list(digits[:2]), list(digits[2:])]
            header = [[low[i][j]+q*high[i][j] for j in range(2)] for i in range(2)]
            p = projection(header, 1, modulus)
            require(is_good(p, 1, modulus) == low_good, 'all high lifts preserve branch')
            try:
                pivot = oracle.good_pivots(p, 1, modulus)
            except ValueError:
                pivot = None
            require((pivot is not None) == low_good, 'literal local-ring oracle branch')
            for weights in product(units, repeat=2):
                weighted = diagonal_conjugate(p, weights, modulus)
                require(leading(weighted, 1, modulus) == leading(p, 1, modulus),
                        'all local-ring diagonal units preserve minors')
                counts['weighted_lifts'] += 1
            counts['lifts'] += 1
            counts['good' if low_good else 'bad'] += 1
            if witness is None and p[0][0] and not low_good:
                witness = dict(q=q,modulus=modulus,low=low,high=high,
                               header=header,projector=p,pivot=p[0][0])
    require(witness is not None, 'nonzero nonunit pivot witness')
    return dict(counts), witness


def word_check(words, matrices, forms, data, rank, modulus, expected, use_prepare=False):
    """Execute literal binary arithmetic, not a mock ring; discard rejected arenas."""
    if use_prepare:
        q, low, high, fixed = data
        header = multiply([[low[i][j]+q*high[i][j] for j in range(len(low))]
                           for i in range(len(low))], fixed, modulus)
        reference = projection(header, rank, modulus)
    else:
        reference = data
    for method in ('good_pivots', 'good_form'):
        arena = words.Arena(modulus.bit_length()+1)
        modword = arena.input(modulus)
        ring = words.Ring(modword)
        matrix = matrices.Matrices(ring)
        if use_prepare:
            high_words = [[arena.input(x) for x in row] for row in high]
            p = matrix.prepare(low,high_words,q,fixed,rank)
            matrix.free(high_words)
            require([[x.inspect() for x in row] for row in p] == reference, 'binary prepare vs adjugate reference')
        else:
            p = [[arena.input(x) for x in row] for row in reference]
        try:
            if method == 'good_pivots':
                output = matrix.good_pivots(p, rank)
                pivots = [x.inspect() for x in output]
                arena.free_many(*output)
            else:
                output = forms.good_form(p,rank,ring)
                pivots = [x.inspect() for x in output.pivots]
                output.close(ring)
            accepted = True
        except ValueError as error:
            accepted = False
            require(('good class' in str(error) or 'Schur block' in str(error) or
                     'diagonal endpoint' in str(error)), 'unexpected binary error: '+str(error))
        require(accepted == expected, 'binary '+method+' branch mismatch')
        if accepted:
            minors = leading(reference, rank, modulus)
            require(pivots == [x*pow(y,-1,modulus) % modulus for x,y in
                               zip(minors,[1]+minors[:-1])], 'binary pivot ratios')
            matrix.free(p)
            ring.close()
            arena.free(modword)
            require(not arena.live, 'successful binary fixture frees every owned Word')


def literal_boundaries(words, matrices, forms, sources, nonunit, bad_prefix):
    checked = 0
    for low in all_gl(2,3):
        fixed, high = [[1,1],[0,1]], [[1,2],[2,1]]
        g = multiply([[low[i][j]+3*high[i][j] for j in range(2)] for i in range(2)], fixed, 9)
        expected = is_good(projection(g,1,9),1,9)
        word_check(words,matrices,forms,(3,low,high,fixed),1,9,expected,True)
        checked += 1
    for modulus in (3,9,27,5,25):
        for r in (1,2):
            g = [[1,1,0],[0,1,1],[1,0,1]]  # determinant 2; a unit at every odd prime
            p = projection(g,r,modulus)
            word_check(words,matrices,forms,p,r,modulus,is_good(p,r,modulus))
            checked += 1
    word_check(words,matrices,forms,nonunit['projector'],1,9,False)
    word_check(words,matrices,forms,bad_prefix['projector'],2,3,False)
    # False rank passes a pivot-only test; literal Schur/endpoint checks reject.
    word_check(words,matrices,forms,eye(2),1,9,False)
    checked += 3
    compiled = []
    for q in (3,5):
        for r in (1,2,7,14,42):
            fixed = eye(64)
            fixed[0][1] = Fraction(1,2)
            inv_fixed = eye(64)
            inv_fixed[0][1] = -pow(2,-1,q) % q
            for good in (True,False):
                g = eye(64)
                if not good:
                    g[0],g[r] = g[r],g[0]
                low = multiply(g,inv_fixed,q)
                template = sources.Template(q,r,(),(),(),tuple(map(tuple,fixed)))
                spec = sources.compile_specification(len(compiled),template,low)
                require(spec.good == good, 'actual 64-dimensional source classifier')
                compiled.append(dict(q=q,rank=r,good=good))
    singular = eye(64)
    singular[0][0] = 0
    template = sources.Template(3,1,(),(),(),tuple(map(tuple,singular)))
    expect_rejection(lambda: sources.compile_specification(0,template,eye(64)), 'oracle unit pivot')
    return dict(binary_fixtures=checked,binary_routines_per_fixture=2,
                actual_64d_source_cases=compiled,
                singular_preparation_rejected_by_actual_source=True,
                rejected_arena_scope='Rejected arenas discarded; no failure-path cleanup claim.')


def controls(oracle, bad_prefix, nonunit, sign_witness):
    require(gcd(nonunit['pivot'],9)==3, 'nonzero is not unit control')
    require(bad_prefix['leading_minors'][-1]!=0 and bad_prefix['leading_minors'][0]==0,
            'final minor alone is insufficient')
    require(sign_witness['correct']!=sign_witness['unsigned'], 'omitted complementary sign control')
    require(oracle.good_pivots(eye(2),1,9)==[1], 'pivot-only code does not establish projector rank')
    diagonal, swapped = [[1,0],[0,0]], [[0,0],[0,1]]
    require(is_good(diagonal,1,3) and not is_good(swapped,1,3), 'nondiagonal conjugation changes pointwise branch')
    q=101
    bound=Fraction(2*(q-1),q*(q-2))
    require(not is_good(swapped,1,q) and 1>bound, 'singleton bad low cover has fraction one')
    require(is_good(projection(eye(2),1,3),1,3) and not is_good(projection([[0,1],[1,0]],1,3),1,3),
            'high-digit q multiplier is essential')
    expect_rejection(lambda: inverse([[1,0],[0,0]],9), 'unit determinant')
    return dict(intermediate_minor=bad_prefix,nonzero_nonunit=nonunit,
                missing_complement_sign=sign_witness,
                false_rank='I_2 declared rank 1 passes oracle pivots; both binary endpoint checks reject',
                nondiagonal_weights='coordinate swap changes diag(1,0) from GOOD to BAD',
                incomplete_cover=dict(q=q,n=2,rank=1,full_cover_bound=str(bound),singleton_bad_fraction='1'),
                wrong_high_multiplier='I_2 + [[2,1],[1,2]] is a bad swap mod 3; q times high preserves I_2',
                singular_preparation='independent inverse rejects nonunit determinant')


def run():
    hashes=authenticate()
    # A fresh namespace prevents cached .pyc from replacing authenticated .py.
    with tempfile.TemporaryDirectory(prefix='r437-pivot-cache-') as cache:
        sys.pycache_prefix=cache
        sys.dont_write_bytecode=True
        sys.path.insert(0,str(VENDOR))
        modules={name:importlib.import_module(name) for name in ('words','matrices','forms','oracle','sources')}
        census,bad_prefix,sign_witness=finite_fields(modules['oracle'])
        lifts,nonunit=local_ring_lifts(modules['oracle'])
        boundaries=literal_boundaries(modules['words'],modules['matrices'],modules['forms'],
                                     modules['sources'],nonunit,bad_prefix)
        negatives=controls(modules['oracle'],bad_prefix,nonunit,sign_witness)
    q0=2**80+1
    require(Fraction(2688*(q0-1),q0-2)<2689, 'uniform coefficient at lower cutoff')
    require(Fraction(2689,2**80)<Fraction(1,10**16), 'published epsilon')
    return dict(status='PASS_R437_BAD_CLASS_PIVOT_AUDIT',source_sha256=hashes,
                finite_fields=census,local_ring=lifts,literal_boundaries=boundaries,controls=negatives,
                scope='Scoped written proof plus exact finite/literal-source checks. No full compiler, physical caller, stock, theorem or new kappa admission.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='explicitly regenerate deterministic receipt')
    args=parser.parse_args()
    result=run()
    path=HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:
        require(result==json.loads(path.read_bytes()),'committed result differs from independent replay')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ('finite_fields','local_ring','literal_boundaries')},sort_keys=True))


if __name__=='__main__':
    main()
