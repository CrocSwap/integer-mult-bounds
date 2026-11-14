#!/usr/bin/env python3
"""Read-only exact checks for selected source phases, not numerical transcendence.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The matching-path/poly helper routines are adapted from the credited A10 verifier;
this is primary corroboration. Separate independent review imports none of them.
SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from hashlib import sha256
from itertools import product, permutations
from math import isqrt, prod
from pathlib import Path
import json

class CheckFailure(RuntimeError):
    pass

def require(condition, message):
    if not condition:
        raise CheckFailure(message)

def matching_paths(order, mask):
    n = len(order)
    require(n >= 2 and n & (n - 1) == 0 and sorted(order) == list(range(n)),
            "complete binary vertex order")
    require(0 < mask < n, "nonzero translation mask")
    pos = {x: i for i, x in enumerate(order)}
    mate = [pos[x ^ mask] for x in order]
    adjacency = [[] for _ in order]
    for i, j in enumerate(mate):
        if i < j:
            adjacency[i].append(j)
            adjacency[j].append(i)
            if j < n - 1:
                adjacency[i + 1].append(j + 1)
                adjacency[j + 1].append(i + 1)
    unseen, removed = set(range(n)), set()
    while unseen:
        stack, component = [min(unseen)], set()
        while stack:
            x = stack.pop()
            if x not in component:
                component.add(x)
                stack.extend(adjacency[x])
        unseen -= component
        if all(len(adjacency[x]) == 2 for x in component):
            first = min(component)
            removed.update((first, mate[first]))
    remaining, paths = set(range(n)) - removed, []
    while remaining:
        start = min(x for x in remaining if sum(y in remaining for y in adjacency[x]) == 1)
        path, previous, current = [], None, start
        while current is not None:
            path.append(current)
            next_vertices = [y for y in adjacency[current] if y in remaining and y != previous]
            require(len(next_vertices) <= 1, "retained component is a path")
            previous, current = current, next_vertices[0] if next_vertices else None
        require(len(path) % 2 == 0, "even retained path")
        remaining -= set(path)
        paths.append(path)
    return paths



def trimmed_indices(paths, size):
    require(size >= 0 and size % 2 == 0, "even trimming size")
    require(size <= sum(map(len, paths)), "trimming capacity")
    keep = []
    left = size
    for path in paths:
        take = min(left, len(path))
        keep.extend(path[:take])
        left -= take
    require(left == 0, "exact requested trim")
    return sorted(keep)



def best_certificate(order):
    choices = [(sum(map(len, p)), v, p)
               for v in range(1, len(order)) for p in [matching_paths(order, v)]]
    return max(choices, key=lambda x: x[0])



def add_poly(a, b, sign=1):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + sign * value
        if not out[key]:
            del out[key]
    return out



def multiply_poly(a, b):
    out = {}
    for u, c in a.items():
        for v, d in b.items():
            key = tuple(x + y for x, y in zip(u, v))
            out[key] = out.get(key, 0) + c * d
    return {k: v for k, v in out.items() if v}


def is_prime(s):
    return isinstance(s, int) and not isinstance(s, bool) and s >= 2 and all(
        s % k for k in range(2, isqrt(s) + 1))


def domain(primes, targets, alpha, r):
    require(primes and len(primes) == len(targets), 'matched nonempty axes')
    require(all(is_prime(s) and s % 2 for s in primes), 'odd prime denominators')
    require(len(set(primes)) == len(primes), 'distinct denominators')
    require(all(isinstance(t, int) and not isinstance(t, bool) and t > 0
                and t & (t - 1) == 0 and s < t < 2*s
                for s, t in zip(primes, targets)), 'dyadic strict source ratio')
    require(isinstance(alpha, int) and not isinstance(alpha, bool) and alpha > 0,
            'positive common integer alpha')
    require(isinstance(r, int) and not isinstance(r, bool) and r >= 2 and r % 2 == 0,
            'positive even minor size')
    require(all(2*r < s for s in primes), 'difference coefficient guard')


def nearest(s, t, i):
    return (2*t*i+s)//(2*s)


def odd_lift(residue, s):
    return residue if residue % 2 else residue+s


def difference_pass(s, t, A, r):
    for d in range(-r, r+1):
        for e in range(-r, r+1):
            if (d or e) and ((d-e)*A+2*t*e) % s == 0:
                return False
    return True


def box_pass(s, t, A, r):
    values = [(u*A+v*(2*t-A)) % s for u in range(r+1) for v in range(r+1)]
    return len(values) == len(set(values))


def index_from_A(s, t, A):
    n = (A-(2*t-s))//2
    return n*pow(t-s, -1, s) % s


def select_one(s, t, r):
    for residue in range(1, s):
        A = odd_lift(residue, s)
        if A >= 2*(t-s)+1 and difference_pass(s, t, A, r):
            return A, 2*t-A, index_from_A(s, t, A)
    raise CheckFailure('no source selector survivor')


def physical_exponent(s, t, j, k):
    qj, qk = nearest(s, t, j), nearest(s, t, k)
    return Fraction((t*k-s*qj)**2-(t*k-s*qk)**2, s*s)


def phase_checks():
    cases, residues, boxes, pairs = 0, 0, 0, 0
    guard_successes = []
    for s in range(7, 150, 2):
        if not is_prime(s):
            continue
        t = 1 << s.bit_length()
        for r in (2, 4, 6):
            if 2*r >= s:
                continue
            cases += 1
            good = []
            for residue in range(1, s):
                A = odd_lift(residue, s)
                dp, bp = difference_pass(s, t, A, r), box_pass(s, t, A, r)
                require(dp == bp, 'difference scan equals complete exponent-box injection')
                residues += 1
                boxes += (r+1)**2
                if dp and A >= 2*(t-s)+1:
                    B, i = 2*t-A, index_from_A(s, t, A)
                    require(0 <= i < s-1, 'finite pair does not wrap')
                    require(nearest(s,t,i+1) == nearest(s,t,i)+1, 'same-cell target gap')
                    require(physical_exponent(s,t,i,i+1) == Fraction(A,s), 'literal upper coefficient')
                    require(physical_exponent(s,t,i+1,i) == Fraction(B,s), 'literal lower coefficient')
                    require(A > 0 and B > 0 and A+B == 2*t, 'positive pair determinant premise')
                    require(0 <= nearest(s,t,i) < nearest(s,t,i+1) < t, 'actual target grid')
                    good.append(i)
                    pairs += 1
            require(len(good) == len(set(good)), 'distinct source indices')
            bound = s-1-(t-s)-2*r*r-r
            require(len(good) >= bound, 'universal bad-residue bound')
            if bound > 0:
                selected = select_one(s,t,r)
                require(selected[2] in good, 'sequential selector gives a good actual pair')
                guard_successes.append((s,t,r,len(good),bound))
    return {'cases':cases, 'nonzero_residues':residues,
            'complete_box_values':boxes, 'admitted_pairs':pairs,
            'positive_guard_cases':len(guard_successes),
            'coverage':'all odd primes 7<=s<150, next dyadic t, even r in {2,4,6} with 2r<s'}


def fine_checks():
    fixtures = [(4,[499,503,997],[512,512,1024]),
                (8,[s for s in range(16257,16321) if is_prime(s)], [16384]*4)]
    out=[]
    for p, primes, targets in fixtures:
        require(len(primes) == len(targets), 'fine fixture size')
        N=1 << len(primes)
        R=2*((N+7)//5)
        r=min(R,2*(isqrt(min(primes))//4))
        domain(primes,targets,3,r)
        require(p >= 3 and all(s >= p**4 for s in primes), 'explicit finite size guard')
        for s,t in zip(primes,targets):
            eta=Fraction(1,4*p*p)
            require((1-2*eta)*t < s <= (1-eta)*t, 'actual fine-prime interval')
            require(Fraction(t-s,s) <= Fraction(1,p*p), 'fine gap')
            bound=s-1-(t-s)-2*r*r-r
            require(bound >= Fraction(s,3)-1 > 0, 'square-root-prime count floor')
            A,B,i=select_one(s,t,r)
            require(box_pass(s,t,A,r), 'fine selected exponent-box injection')
            require(physical_exponent(s,t,i,i+1)==Fraction(A,s)
                    and physical_exponent(s,t,i+1,i)==Fraction(B,s), 'fine source coefficients')
            out.append({'p':p,'s':s,'t':t,'r':r,'A':A,'B':B,'index':i,'count_lower_bound':bound})
    return out
def tensor_monomial(x,y,g):
    key=[]
    for bit in range(g):
        xb,yb=(x>>bit)&1,(y>>bit)&1
        key.extend((int(xb==0 and yb==1),int(xb==1 and yb==0)))
    return tuple(key)


def displacement_entries(order,keep,weights=None):
    g=len(order).bit_length()-1
    def monomial(x,y):
        key=tensor_monomial(x,y,g)
        return key if weights is None else (sum(a*b for a,b in zip(key,weights)),)
    rows=[]
    for i in keep:
        row=[]
        for j in keep:
            value={monomial(order[i],order[j]):1}
            if i and j:
                value=add_poly(value,{monomial(order[i-1],order[j-1]):1},-1)
            row.append(value)
        rows.append(row)
    return rows


def poly_det(entries,variables):
    out={}
    for perm in permutations(range(len(entries))):
        sign=(-1)**sum(perm[i]>perm[j] for i in range(len(perm)) for j in range(i+1,len(perm)))
        term={(0,)*variables:sign}
        for i,j in enumerate(perm):
            term=multiply_poly(term,entries[i][j])
            if not term:
                break
        out=add_poly(out,term)
    return out


def substitute(poly,weights):
    out={}
    for key,c in poly.items():
        power=(sum(a*b for a,b in zip(key,weights)),)
        out=add_poly(out,{power:c})
    return out


def polynomial_checks():
    orders=[[0,1],[1,0]]
    orders += [[0]+list(tail) for tail in permutations(range(1,4))]
    orders += [[0,1,2,3,7,5,6,4],[0,1,2,3,4,6,5,7],[0,1,3,2,6,7,5,4]]
    cases=[]
    for order in orders:
        g=len(order).bit_length()-1
        primes,targets=[499,503,997][:g],[512,512,1024][:g]
        r=2*((len(order)+7)//5)
        domain(primes,targets,3,r)
        cap,mask,paths=best_certificate(order)
        require(cap>=r,'A9 capacity in fixed finite fixture')
        keep=trimmed_indices(paths,r)
        phases=[select_one(s,t,r) for s,t in zip(primes,targets)]
        S=prod(primes)
        weights=[x*(S//s) for s,phase in zip(primes,phases) for x in phase[:2]]
        polynomial=poly_det(displacement_entries(order,keep),2*g)
        require(polynomial,'directed polynomial nonzero')
        require(all(max(key)<=r for key in polynomial),'individual variable degree guard')
        symmetric={}
        for key,c in polynomial.items():
            k=tuple(key[2*i]+key[2*i+1] for i in range(g))
            symmetric=add_poly(symmetric,{k:c})
        isolated=tuple(r if mask>>i&1 else 0 for i in range(g))
        require(abs(symmetric.get(isolated,0))==1,'symmetric isolated predecessor coefficient')
        changed=substitute(polynomial,weights)
        require(len(changed)==len(polynomial),'no directed monomial merges')
        direct=poly_det(displacement_entries(order,keep,weights),1)
        require(changed==direct,'entry-first and polynomial-first exact substitution agree')
        cases.append({'order':order,'r':r,'keep':keep,'translation':mask,
                      'directed_terms':len(polynomial),'max_exponent':max(k[0] for k in changed)})
    return {'cases':cases,'polynomials':len(cases),'terms':sum(x['directed_terms'] for x in cases)}


def inverse(a):
    n=len(a)
    b=[[Fraction(x) for x in row]+[Fraction(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if b[i][k]),None)
        require(pivot is not None,'rational inverse exists')
        b[k],b[pivot]=b[pivot],b[k]
        scale=b[k][k]
        b[k]=[x/scale for x in b[k]]
        for i in range(n):
            if i!=k:
                factor=b[i][k]
                b[i]=[x-factor*y for x,y in zip(b[i],b[k])]
    return [row[n:] for row in b]


def controls():
    passed=[]
    def rejected(name,fn):
        try:
            fn()
        except CheckFailure:
            passed.append(name)
        else:
            raise CheckFailure('negative control accepted: '+name)
    rejected('composite denominator',lambda:domain([9],[16],1,2))
    rejected('repeated prime denominator',lambda:domain([31,31],[32,32],1,2))
    rejected('noninteger alpha',lambda:domain([31],[32],Fraction(1,2),2))
    rejected('zero alpha',lambda:domain([31],[32],0,2))
    rejected('nondyadic target',lambda:domain([31],[33],1,2))
    rejected('odd minor size',lambda:domain([31],[32],1,3))
    rejected('difference coefficient guard',lambda:domain([7],[8],1,4))
    s,t,i=7,8,3
    n=t*i-s*nearest(s,t,i)
    require(nearest(s,t,i+1)-nearest(s,t,i)==2,'phase-cut fixture')
    require(physical_exponent(s,t,i,i+1)!=Fraction(2*t-s+2*n,s),'phase-cut formula fails')
    passed.append('phase cut cannot use unit-gap formula')
    s,t,i=31,32,30
    n=t*i-s*nearest(s,t,i)
    A=2*t-s+2*n
    require(A==s and nearest(s,t,i+1)==nearest(s,t,i)+1,'terminal nonzero-residue exclusion')
    passed.append('terminal pair requires zero residue')
    require(not box_pass(31,32,31,2),'zero A loses injection')
    passed.append('zero residue collision')
    A,B,i=select_one(31,32,2)
    require(not box_pass(31,32,A,31),'degree threshold collision')
    require(substitute({(B,0):1,(0,A):-1},[A,B])=={},'high-degree exact exponential relation')
    passed.append('unguarded directed degrees can vanish exactly')
    require(substitute({(1,0,0,0):1,(0,0,1,0):-1},[A*31,B*31,A*31,B*31])=={},
            'repeated-denominator cross-axis collision')
    passed.append('noncoprime source repeat can cancel')
    insufficient=None
    for s in range(7,80,2):
        if is_prime(s):
            t=1<<s.bit_length()
            for r in (2,4,6):
                if 2*r<s and s-1-(t-s)-2*r*r-r<=0:
                    candidates=[a for a in range(1,s) if odd_lift(a,s)>=2*(t-s)+1
                                and box_pass(s,t,odd_lift(a,s),r)]
                    if candidates:
                        insufficient=(s,t,r,candidates[0])
                        break
            if insufficient:
                break
    require(insufficient is not None,'finite sufficient guard is not necessary')
    passed.append('nonpositive count guard does not prove impossibility')
    a=[[Fraction(1),Fraction(1,2),Fraction(1,4)],
       [Fraction(1,3),Fraction(1),Fraction(1,2)],
       [Fraction(1,5),Fraction(1,3),Fraction(1)]]
    require([row[:2] for row in inverse(a)[:2]]!=inverse([row[:2] for row in a[:2]]),
            'inverse and section do not commute')
    passed.append('selected tensor inverse is not larger inverse section')
    return {'passed':passed,'count':len(passed),'insufficient_guard_witness':insufficient}


def authenticate():
    root=Path(__file__).resolve().parent
    pins=json.loads((root/'DEPENDENCIES.json').read_text())
    for item in pins['files']:
        content=(root/item['local']).read_bytes()
        require(len(content)==item['bytes'] and sha256(content).hexdigest()==item['sha256'],
                'retained source bytes: '+item['local'])
    return len(pins['files'])


def main():
    result={'status':'PASS_SELECTED_PHASE_BINARY_RANK',
            'authenticated_inputs':authenticate(), 'phase_checks':phase_checks(),
            'fine_prime_fixtures':fine_checks(), 'directed_polynomials':polynomial_checks(),
            'negative_controls':controls(),
            'limits':'Bounded exact corroboration; universal proof and classical transcendence are separate. No rounding, periodic/full-caller or kappa claim.'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
