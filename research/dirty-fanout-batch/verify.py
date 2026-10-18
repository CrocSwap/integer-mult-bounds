"""Independent free-word/dense checks and deterministic receipt. Stdlib only."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import random

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('fanout', P/'batch.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def symbolic(word, roles):
    # Free noncommutative left action on one independent symbol per dirty role.
    rows = [Counter({(i, ()): 1}) for i in range(roles)]
    for factor, src, dst, sign in word:
        for (origin, letters), value in list(rows[src].items()):
            key = (origin, (factor,)+letters)
            rows[dst][key] += sign*value
            if not rows[dst][key]:
                del rows[dst][key]
    return rows


def expected_symbolic(common, branches, roles):
    rows = [Counter({(i, ()): 1}) for i in range(roles)]
    for i, a in enumerate(branches, 1):
        rows[i][(0, tuple(reversed(common+a)))] += 1
    return rows


def multiply(a, v, modulus=None):
    out = [sum(a[i][j]*v[j] for j in range(len(v))) for i in range(len(v))]
    return out if modulus is None else [x % modulus for x in out]


def expected_dense(initial, matrices, common, branches, modulus):
    out = copy.deepcopy(initial)
    common_value = initial[0][:]
    for f in common:
        common_value = multiply(matrices[f], common_value, modulus)
    for i, a in enumerate(branches, 1):
        value = common_value[:]
        for f in a:
            value = multiply(matrices[f], value, modulus)
        out[i] = [x+y for x, y in zip(out[i], value)]
        if modulus:
            out[i] = [x % modulus for x in out[i]]
    return out


def weighted_cost(factors, prices):
    if len(factors) == 1:
        return prices[factors[0]]
    mid = len(factors)//2
    return 2*(weighted_cost(factors[:mid],prices)+weighted_cost(factors[mid:],prices))


def fixture(m, lengths):
    common = list(range(m))
    branches = []
    pos = m
    for n in lengths:
        branches.append(list(range(pos, pos+n)))
        pos += n
    return common, branches, pos


def main(write=False):
    pins = json.loads((P/'SOURCES.json').read_text())
    for pin in pins['files']:
        raw = (P/pin['path']).read_bytes()
        check(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 '+pin['path'])
        check(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source Git blob')
    symbolic_cases = 0
    invoice_cases = 0
    for m in range(1, 17):
        for k in range(1, 9):
            common, branches, nf = fixture(m, list(range(1, k+1)))
            word, dirt = b.compile_batch(common, branches)
            roles = k+1+dirt
            check(symbolic(word, roles) == expected_symbolic(common, branches, roles), 'free word identity')
            check(symbolic(word+b.inverse(word), roles) == [Counter({(i, ()): 1}) for i in range(roles)], 'literal inverse')
            symbolic_cases += 1
            counts = Counter(f for f, _, _, _ in word)
            right = b.product(common, 0, k+1, list(range(k+2, roles)))
            lefts = [b.product(a, k+1, i, list(range(k+2, roles))) for i,a in enumerate(branches,1)]
            expected = Counter()
            for sub in [right]+lefts:
                expected.update(f for f, _, _, _ in sub)
                expected.update(f for f, _, _, _ in sub)
            check(counts == expected, 'per-factor weighted recurrence')
            check(len(word) == 2*b.leaf_count(m)+2*sum(b.leaf_count(len(a)) for a in branches), 'complete leaf bill')
            for seed in (58, 59, 60):
                prices = [1+(seed+7*f)%19 for f in range(nf)]
                check(sum(prices[f] for f,_,_,_ in word) == 2*weighted_cost(common,prices)+2*sum(weighted_cost(a,prices) for a in branches), 'weighted bill')
                invoice_cases += 1
    # Independently minimize all ordered binary splits; no claim about multiway echoes.
    dp = [0, 1]
    for n in range(2, 65):
        dp.append(min(2*(dp[i]+dp[n-i]) for i in range(1,n)))
    check(all(dp[n] == b.leaf_count(n) for n in range(1,65)), 'binary split optimum')
    rng = random.Random(58)
    dense_cases = 0
    for m, lengths in ((1,[1,2]), (3,[2,3,1]), (8,[1,2,3,4,5])):
        common, branches, nf = fixture(m, lengths)
        word, dirt = b.compile_batch(common, branches)
        roles = len(branches)+1+dirt
        for dimension in (1,2,3):
            for modulus in (None,2,3,5,9):
                matrices = {f:[[rng.randrange(-2,3) for _ in range(dimension)] for _ in range(dimension)] for f in range(nf)}
                for column in range(roles*dimension+3):
                    initial = [[0]*dimension for _ in range(roles)]
                    if column < roles*dimension:
                        initial[column//dimension][column%dimension] = 1
                    else:
                        initial = [[rng.randrange(-7,8) for _ in range(dimension)] for _ in range(roles)]
                    if modulus:
                        initial = [[v%modulus for v in row] for row in initial]
                    want = expected_dense(initial, matrices, common, branches, modulus)
                    for mode in ('batch','separate','grouped'):
                        code,_ = b.compile_batch(common, branches, mode)
                        got = copy.deepcopy(initial)
                        b.run(code,matrices,got,modulus)
                        check(got == want, 'dense differential '+mode)
                        b.run(b.inverse(code),matrices,got,modulus)
                        check(got == initial, 'all-role inverse '+mode)
                    dense_cases += 1
    # Rational, noncommuting two-by-two fixture, independent direct products.
    common, branches, nf = fixture(2,[2,1])
    word,dirt = b.compile_batch(common,branches)
    matrices = {f:[[Fraction(f+1,3),Fraction(1,2)],[Fraction(-1,4),Fraction(f+2,5)]] for f in range(nf)}
    initial = [[Fraction(i+2,7),Fraction(2-i,3)] for i in range(3+dirt)]
    got = copy.deepcopy(initial)
    b.run(word,matrices,got)
    check(got == expected_dense(initial,matrices,common,branches,None), 'rational noncommuting fixture')
    # Deterministic rounded increments are target-independent but need not be linear.
    # Compare with a separate ideal dense product, and demand exact borrowed restoration.
    rounded_cases = 0
    for m, lengths in ((1,[1,2]), (2,[2,1]), (3,[1,2,3])):
        common, branches, nf = fixture(m,lengths)
        code,dirt = b.compile_batch(common,branches)
        roles = len(branches)+1+dirt
        matrices = {f:[[Fraction((f+1)%3-1,3),Fraction(1,2)],
                       [Fraction(-1,4),Fraction((f+2)%3-1,5)]] for f in range(nf)}
        K = max(sum(abs(v) for v in row) for a in matrices.values() for row in a)
        for bits in (4,12,24):
            scale = 1 << bits
            for dirt_value in (-7,0,11):
                initial = [[(i+dirt_value)*scale+1,(2-i+dirt_value)*scale-1] for i in range(roles)]
                state = copy.deepcopy(initial)
                def rounded_run(program):
                    for f,x,y,sign in program:
                        for i,row in enumerate(matrices[f]):
                            value = sum(a*v for a,v in zip(row,state[x]))
                            state[y][i] += sign*(value.numerator//value.denominator)
                rounded_run(code)
                check(state[0] == initial[0] and state[len(branches)+1:] == initial[len(branches)+1:], 'rounded exact restoration')
                scaled_initial = [[Fraction(v,scale) for v in row] for row in initial]
                ideal = expected_dense(scaled_initial,matrices,common,branches,None)
                error = max(abs(Fraction(a,scale)-v) for row,want in zip(state,ideal) for a,v in zip(row,want))
                bound = Fraction(len(code),scale)*(1+K)**(len(code)-1)
                check(error <= bound, 'rounded full-word error bound')
                rounded_run(b.inverse(code))
                check(state == initial, 'rounded literal inverse')
                rounded_cases += 1
    # Exhaust all signed star words shorter than the six-query, two-output construction.
    rejected_words = 0
    target = expected_symbolic([0],[[1],[2]],4)
    alphabet = [(0,0,3,s) for s in (-1,1)] + [(i,3,i,s) for i in (1,2) for s in (-1,1)]
    for length in range(6):
        for candidate in itertools.product(alphabet,repeat=length):
            check(symbolic(candidate,4) != target, 'short star word implements target')
            rejected_words += 1
    controls = []
    common,branches,_ = fixture(3,[2,1])
    word,dirt = b.compile_batch(common,branches)
    roles = 3+dirt
    target = expected_symbolic(common,branches,roles)
    mutations = {
        'omit_final_leaf': word[:-1],
        'reverse_factor_order': b.compile_batch(list(reversed(common)),branches)[0],
        'change_common_source_during_batch': word[:1]+[(99,1,0,1)]+word[1:],
        'omit_common_restoration': [x for x in word if not (x[0] in common and x[3] == -1)],
        'negate_without_reverse': [(f,x,y,-s) for f,x,y,s in word],
        'omit_one_output': [op for op in word if op[2] != 2],
    }
    for name,mutant in mutations.items():
        reference = expected_symbolic(common,branches,roles)
        if name == 'negate_without_reverse':
            reference = [Counter({(i, ()): 1}) for i in range(roles)]
            mutant = word+mutant
        check(symbolic(mutant,roles) != reference, 'accepted mutation '+name)
        controls.append(name)
    def reject(name, fn):
        try:fn()
        except ValueError:controls.append(name)
        else:raise RuntimeError('accepted admission fault '+name)
    reject('empty_common',lambda:b.compile_batch([],[[1]]))
    reject('empty_output_list',lambda:b.compile_batch([0],[]))
    reject('insufficient_scratch',lambda:b.product([0,1],0,1,[]))
    reject('ancestor_alias',lambda:b.product([0,1],0,1,[0]))
    arrays = [[1],[2],[3]]
    reject('target_source_alias',lambda:b.run([(0,0,1,1)],{0:[[2]]},[arrays[0],arrays[0]]))
    reject('coefficient_alias',lambda:b.run([(0,0,1,1)],{0:[arrays[0]]},arrays))
    reject('boolean_sign',lambda:b.run([(0,0,1,True)],{0:[[2]]},arrays))
    # Linearity is essential for dirt independence, despite exact restoration.
    nonlinear = lambda z:z*z
    check(nonlinear(3+2)-nonlinear(3) != nonlinear(2), 'nonlinear control')
    controls.append('nonlinear_left_map_has_dirty_cross_term')
    # Exact grid rounding can preserve dirt but alter the ideal increment.
    rounded = lambda z:z//2
    check(rounded(1+1)-rounded(1) != rounded(1), 'rounding control')
    controls.append('rounded_left_map_is_not_exact_linear_map')
    common,branches,nf = fixture(8,[1,2,3,4,5])
    codes = {mode:b.compile_batch(common,branches,mode)[0] for mode in ('batch','separate','grouped')}
    dirt = b.compile_batch(common,branches)[1]
    invoices = {mode:b.invoice(code,3,6+dirt,nf) for mode,code in codes.items()}
    check([len(codes[x]) for x in ('batch','separate','grouped')] == [246,680,758], 'seed fixture')
    # Independent closed form, rather than replaying invoice()'s tape trace.
    tape_cases = 0
    for n in range(1,6):
        r = 6+dirt
        for code in codes.values():
            total = 0
            for f,x,y,_ in code:
                coefficients = n*n*(r*n+f*n*n)+n*n*(n*n-1)//2
                sources = n*((2*n-1)*x*n+(n-1)**2)
                previous_targets = (n-1)*y*n+(n-1)*(n-2)//2
                jumps = sum(abs(y*n+i-(x*n+n-1)) for i in range(n))
                total += 2*coefficients-sources-previous_targets+jumps+y*n+n-1
            check(total == b.invoice(code,n,r,nf)['head_travel_word_slots'], 'closed-form tape bill')
            tape_cases += 1
    receipt = dict(status='PASS_DIRTY_FANOUT_BATCH',seed=58,base=pins['base'],
                   symbolic_cases=symbolic_cases,weighted_cases=invoice_cases,dense_cases=dense_cases,tape_cases=tape_cases,
                   rational_cases=1,rounded_cases=rounded_cases,short_star_words_rejected=rejected_words,controls=controls,
                   binary_optimum_domain='all ordered binary splits, unweighted n=1..64',
                   seed_case=dict(common_factors=8,left_factors=[1,2,3,4,5],dirty_arrays=dirt,
                                  invoices=invoices,word_sha256={k:hashlib.sha256(json.dumps(v,separators=(',',':')).encode()).hexdigest() for k,v in codes.items()}),
                   scope='Exact linear multi-output interface; no instantiated supplier, rounded inverse theorem, or new kappa')
    encoded = json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    if write:(P/'CERTIFICATE.json').write_text(encoded)
    else:check(encoded == (P/'CERTIFICATE.json').read_text(), 'certificate differs')
    print(f'PASS_DIRTY_FANOUT_BATCH: {symbolic_cases} free-word cases; {dense_cases} dense cases; 680 -> 246 leaves; {dirt} dirty arrays; no new kappa')


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true',help='regenerate, not verify, the certificate')
    main(parser.parse_args().write)
