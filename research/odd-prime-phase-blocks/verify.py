"""Check exact controls for the two odd prime block theorem."""
from collections import Counter
from functools import cache
from hashlib import sha1, sha256
from itertools import combinations, permutations
from pathlib import Path
import argparse
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def divide(poly, divisor):
    row = list(poly)
    quotient = [0]*(len(row)-len(divisor)+1)
    for i in range(len(quotient)-1, -1, -1):
        quotient[i] = value = row[i+len(divisor)-1]
        for j, c in enumerate(divisor):
            row[i+j] -= value*c
    need(not any(row), 'exact polynomial division')
    return tuple(quotient)


@cache
def cyclotomic(m):
    poly = (-1,)+(0,)*(m-1)+(1,)
    for d in range(1, m):
        if m % d == 0:
            poly = divide(poly, cyclotomic(d))
    return poly


@cache
def reduction(m):
    poly = cyclotomic(m)
    return len(poly)-1, [(i,c) for i,c in enumerate(poly) if c]


def zero(exponents, m, constant=0):
    row = [0]*m
    for e in exponents:
        row[e % m] += 1
    row[0] -= constant
    degree, terms = reduction(m)
    for i in range(m-1, degree-1, -1):
        value = row[i]
        if value:
            for j,c in terms:
                row[i-degree+j] -= value*c
    return not any(row)


def gram(matrix, m):
    n, columns = len(matrix), len(matrix[0])
    for i in range(columns):
        for j in range(columns):
            need(zero([row[j]-row[i] for row in matrix], m, n if i==j else 0), 'exact Gram')
    return columns*columns


def quotient_checks():
    pairs = [(3,5),(3,7),(5,7),(5,11),(7,11),(7,13),(11,13),(13,17)]
    canonical = 0
    for p,q in pairs:
        for modulus in (3,5,9,15,25,27):
            for k in range(p):
                for t in range(1,modulus):
                    for u in range(1,modulus):
                        counts = Counter()
                        for value, count in [(0,q-p+k),(t,p-k),(-u,p-k),(t-u,k)]:
                            counts[value % modulus] += count
                        positive = sorted(c for c in counts.values() if c)
                        need(len(positive) > 1 and positive != [p,q], 'different exceptional subsets')
                        canonical += 1
    # Enumerate actual subsets by a second route, rather than intersection representatives.
    subsets = [set(s) for s in combinations(range(12),5)]
    full = 0
    for left,right in combinations(subsets,2):
        for t,u in ((1,1),(1,2),(2,1),(2,2)):
            values = [(t*(r in left)-u*(r in right)) % 3 for r in range(12)]
            counts = sorted(Counter(values).values())
            need(len(counts)>1 and counts != [5,7], 'full subset-pair exclusion')
            full += 1
    return dict(prime_pairs=pairs,odd_quotient_orders=[3,5,9,15,25,27],canonical_cases=canonical,
                full_p5_q7_modulus3_subset_pairs=full)


def permutation_checks():
    cases = []
    for p in (3,5,7):
        accepted = total = 0
        for permutation in permutations(range(p)):
            ratios = [(i-permutation[i]) % p for i in range(p)]
            need(sum(ratios) % p == 0, 'product of two permutations')
            counts = Counter(ratios)
            possible = any(all(counts[r] <= 1+int(r==extra) for r in range(p)) for extra in range(p))
            if possible:
                need(all(counts[r]==1 for r in range(p)), 'product excludes a missing and repeated root')
                need(zero(ratios,p), 'exact orthogonality of every compatible ratio pattern')
                accepted += 1
            total += 1
        cases.append(dict(p=p,relative_permutations=total,compatible_orthogonal_patterns=accepted))
    control = [0,3,3,5,1]
    need(zero(control,6) and sum([3,3]) % 6 == 0 and not zero([3,3],6), 'even-prime product control')
    return dict(cases=cases,even_prime_control=dict(p=2,q=3,full_zero_sum_exponents=control,
                selected_exponents=[3,3],product_is_one=True,selected_sum_is_zero=False))


def normal_form(matrix,p,q,m):
    gram(matrix,m)
    n, columns, factor = p+q,len(matrix[0]),m//(p*q)
    dephased = [[(row[j]-row[0]) % m for j in range(columns)] for row in matrix]
    subsets = []
    for j in range(columns):
        counts = Counter(row[j] % factor for row in dephased)
        majority = max(counts,key=counts.get)
        need(sorted(counts.values()) in ([n],[p,q]), 'column quotient type')
        subset = [r for r in range(n) if (dephased[r][j]-majority) % factor]
        if subset:
            need(len(subset)==p, 'exceptional subset size')
            subsets.append(subset)
    if not subsets:
        answer = [[(row[j]-dephased[0][j]) % m for j in range(columns)] for row in dephased]
        need(all(e % factor == 0 for row in answer for e in row), 'squarefree double dephasing')
        return dict(kind='descended',entries=[[e//factor for e in row] for row in answer])
    chosen = subsets[0]
    need(all(s==chosen for s in subsets), 'common exceptional subset')
    other = [r for r in range(n) if r not in chosen]
    answer = [[(row[j]-dephased[other[0]][j]) % m for j in range(columns)] for row in dephased]
    gamma = answer[chosen[0]]
    top = [[(answer[r][j]-gamma[j]) % m for j in range(columns)] for r in chosen]
    bottom = [answer[r] for r in other]
    need(all(e % (m//p)==0 for row in top for e in row), 'p-root block')
    need(all(e % (m//q)==0 for row in bottom for e in row), 'q-root block')
    top = [[e//(m//p) for e in row] for row in top]
    bottom = [[e//(m//q) for e in row] for row in bottom]
    gram(top,p);gram(bottom,q)
    need(columns<=p and any((e-gamma[0]) % factor for e in gamma), 'essential higher phase')
    for i,r in enumerate(chosen):
        need(answer[r]==[(top[i][j]*(m//p)+gamma[j]) % m for j in range(columns)], 'top reconstruction')
    for i,r in enumerate(other):
        need(answer[r]==[e*(m//q) for e in bottom[i]], 'bottom reconstruction')
    return dict(kind='two_blocks',top_rows=chosen,p_block=top,q_block=bottom,column_phases=gamma)


def alphabet_case(p,q,a,b):
    m = p**a*q**b
    factor = m//(p*q)
    need(len(cyclotomic(m))-1 == (p-1)*(q-1)*factor, 'cyclotomic degree')
    cycles_p = [[(s+i*(m//p)) % m for i in range(p)] for s in range(m//p)]
    cycles_q = [[(s+i*(m//q)) % m for i in range(q)] for s in range(m//q)]
    for cycle in cycles_p+cycles_q:
        need(zero(cycle,m), 'rotated prime cycle')
    pair_count = product_cases = accepted = 0
    for left in cycles_p:
        coset = left[0] % (m//p)
        for right in cycles_q:
            full = left+right
            need(sorted(Counter(e % factor for e in full).values()) in ([p+q],[p,q]), 'two-cycle quotient counts')
            extra = [e for e in right if e % (m//p)==coset]
            need(len(extra)<=1, 'prime cosets meet at most once')
            pool = left+extra
            for selected in combinations(pool,p):
                if sum(selected) % m == (p*coset) % m:
                    need(Counter(selected)==Counter(left), 'odd-prime product rigidity')
                    accepted += 1
                product_cases += 1
            pair_count += 1
    examples = []
    gram_count = mutants = 0
    for columns in sorted({2,p}):
        original = [[(r*j*(m//p)+j) % m for j in range(columns)] for r in range(p)]
        original += [[r*2*j*(m//q) % m for j in range(columns)] for r in range(q)]
        gram_count += gram(original,m)
        cross_ratio = (original[0][1]-original[0][0]-original[p][1]+original[p][0]) % m
        need(cross_ratio==1, 'sharp cross ratio')
        permutation = list(range(0,p+q,2))+list(range(1,p+q,2))
        changed = [[(original[r][j]+17*r*r+5*r+1+3*j*j+11*j+7) % m
                    for j in range(columns)] for r in permutation]
        gram_count += gram(changed,m)
        block = normal_form(changed,p,q,m)
        need(block['kind']==('two_blocks' if factor>1 else 'descended'), 'normal-form branch')
        if factor>1:
            gram_count += 2*columns*columns
        # Relative block phases in the smaller alphabet give the opposite branch.
        squarefree = [[(r*j*(m//p)+j*factor) % m for j in range(columns)] for r in range(p)]
        squarefree += [[r*2*j*(m//q) % m for j in range(columns)] for r in range(q)]
        gram_count += gram(squarefree,m)
        need(normal_form(squarefree,p,q,m)['kind']=='descended', 'squarefree phase control')
        bad = [row[:] for row in original];bad[0][1] = (bad[0][1]+1) % m
        try:
            gram(bad,m)
        except ValueError as error:
            need(str(error)=='exact Gram', 'mutation fails at the intended boundary')
        else:
            raise ValueError('single-entry phase error accepted')
        mutants += 1
        examples.append(dict(columns=columns,cross_ratio_exponent=cross_ratio,normal_form=block))
    # Columns zero and two share a phase class; column one is a different class.
    shared = [[(r*j*(m//p)+int(j==1)) % m for j in range(p)] for r in range(p)]
    shared += [[r*2*j*(m//q) % m for j in range(p)] for r in range(q)]
    gram_count += gram(shared,m)
    shared_form = normal_form(shared,p,q,m)
    need(shared_form['kind']==('two_blocks' if factor>1 else 'descended'), 'same-class block control')
    if factor>1:
        gram_count += 2*p*p
    return dict(p=p,q=q,a=a,b=b,modulus=m,quotient_order=factor,cycle_pairs=pair_count,
                product_submultisets=product_cases,accepted_product_submultisets=accepted,
                exact_Gram_entries=gram_count,single_entry_mutants=mutants,examples=examples,same_class_example=shared_form)


def collect():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (HERE/pin['retained']).read_bytes()
        need(sha256(raw).hexdigest()==pin['sha256'] and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'], 'source bytes')
    source = HERE/'retained/source7775/verify.py'
    completed = subprocess.run([sys.executable,'-W','error',*(['-O'] if sys.flags.optimize else []),'-B',str(source)],capture_output=True,text=True,check=True,timeout=60)
    need('PASS_TWO_PRIME_ALPHABET_DESCENT' in completed.stdout, 'unchanged predecessor replay')
    definitions = [(3,5,1,1),(3,5,2,1),(3,7,1,2),(5,7,1,1),(5,7,2,1),(5,7,1,2),
                   (5,7,2,2),(5,11,2,1),(7,11,2,1),(7,11,1,2),(7,13,2,1),(11,13,2,1)]
    cases = [alphabet_case(*d) for d in definitions]
    return dict(source_files=len(pins),quotient_checks=quotient_checks(),permutation_checks=permutation_checks(),
                alphabets=cases,total_cycle_pairs=sum(c['cycle_pairs'] for c in cases),
                total_product_submultisets=sum(c['product_submultisets'] for c in cases),
                exact_Gram_entries=sum(c['exact_Gram_entries'] for c in cases),
                single_entry_mutants=sum(c['single_entry_mutants'] for c in cases),
                statement='For distinct odd primes p<q and a,b>=1, p+q-row column capacity over mu_(p^a q^b) equals that over mu_(pq).',
                block_statement='Every matrix that cannot descend has at most p columns and a row/column phase normal form [A D; B], with orthogonal columns in A over mu_p and in B over mu_q.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record',action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(collect()))
    if args.record:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()), 'deposited result')
    print('PASS_ODD_PRIME_PHASE_BLOCKS')
    print('General two-block classification, sharp p-column boundary and prime-power capacity equality')
    print('Exact quotient, relative-permutation, cycle-product, phase-gauge and mutation checks pass')
    print('Unchanged p=3 descent and complete eight-row capacity sources pass')
