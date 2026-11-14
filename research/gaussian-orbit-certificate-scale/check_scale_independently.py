"""Independent bounded exact checks; imports no worker implementation."""
from fractions import Fraction
from itertools import permutations, product
from math import factorial, gcd, lcm
import json


def need(x, message):
    if not x:
        raise RuntimeError(message)


def cycle_lengths(p):
    unseen = set(range(len(p))); out = []
    while unseen:
        x = min(unseen); start = x; count = 0
        while x in unseen:
            unseen.remove(x); count += 1; x = p[x]
        need(x == start, 'invalid permutation')
        out.append(count)
    return out


def matrix(n, d, q, v):
    points = list(product(range(n), repeat=d))
    return [[q**sum((a-b)**2 for a,b in zip(x,y))*v**(sum(x)-sum(y))
             for y in points] for x in points]


def automorphisms(a):
    size = len(a); found = []; signatures = []
    for i in range(size):
        signatures.append((tuple(sorted(a[i])),tuple(sorted(a[j][i] for j in range(size)))))
    for p in permutations(range(size)):
        if any(signatures[i] != signatures[p[i]] for i in range(size)):
            continue
        if all(a[i][j] == a[p[i]][p[j]] for i in range(size) for j in range(size)):
            found.append(p)
    return found


def partitions(n, least=1):
    if n == 0:
        yield ()
    for first in range(least,n+1):
        for tail in partitions(n-first,first):
            yield (first,)+tail


def prime(n):
    return n>=2 and all(n%k for k in range(2,int(n**0.5)+1))


def grouped_knapsack(d):
    rows = {0:(1,())}
    for p in range(2,d+1):
        if not prime(p):continue
        old = rows.copy(); power = p
        while power <= d:
            for used,(value,witness) in old.items():
                if used+power <= d and value*power > rows.get(used+power,(0,()))[0]:
                    rows[used+power]=(value*power,witness+(power,))
            power *= p
    return max(rows.values(),key=lambda x:x[0])


def burnside(n, lengths):
    period = lcm(*lengths)
    raw = sum(n**sum(gcd(length,t) for length in lengths) for t in range(period))
    need(raw%period == 0,'nonintegral Burnside result')
    return raw//period


def direct_orbits(n,lengths):
    words = list(product(range(n),repeat=sum(lengths)));where={x:i for i,x in enumerate(words)}
    axes=[];start=0
    for length in lengths:
        axes.extend(start+(j+1)%length for j in range(length));start+=length
    perm=[where[tuple(x[a] for a in axes)] for x in words]
    return len(cycle_lengths(perm))


def rounded(a,bits):
    scale=2**bits
    return [[Fraction((2*x*scale+1)//2,scale) for x in row] for row in a]


def main():
    sym=[]
    for n,d in [(2,1),(2,2),(2,3),(3,1),(3,2)]:
        for v in (Fraction(1),Fraction(3,2)):
            a=matrix(n,d,Fraction(1,2),v);group=automorphisms(a)
            need(len(group)==factorial(d)*(2**d if v==1 else 1),'symmetry classification')
            sym.append({'n':n,'d':d,'v':str(v),'group_size':len(group),
                        'minimum_orbits':min(len(cycle_lengths(p)) for p in group),
                        'max_order':max(lcm(*cycle_lengths(p)) for p in group)})
    families=[]
    for d in range(1,15):
        types=list(partitions(d));maximum=max(lcm(*kind) for kind in types)
        order,powers=grouped_knapsack(d);need(order==maximum,'prime-power order characterization')
        for n in (2,3):
            minimum=min(burnside(n,kind) for kind in types)
            constructed=burnside(n,powers+(1,)*(d-sum(powers)))
            need(Fraction(n**d,order)<=minimum<=constructed,'cycle bounds')
            need(constructed*order<4*n**d,'constant-four construction')
            families.append({'d':d,'n':n,'types':len(types),'g':order,'powers':powers,
                             'minimum_orbits':minimum,'constructed_orbits':constructed})
    correction_checks=0
    for p in range(2,44):
        if not prime(p):continue
        power=p
        while power<=128:
            for n in (2,3,5):
                ratio=Fraction(burnside(n,(power,))*power,n**power)
                need(ratio<=1+Fraction(p-1,n**(p-1)),'prime-power correction')
                correction_checks+=1
            power*=p
    direct=[]
    for n,lengths in [(2,(4,)),(2,(2,3)),(2,(5,)),(2,(2,4)),(2,(3,3)),(2,(3,5)),(3,(3,)),(3,(2,3))]:
        c=direct_orbits(n,lengths);need(c==burnside(n,lengths),'literal orbit traversal')
        direct.append({'n':n,'lengths':lengths,'orbits':c})
    need(burnside(2,(2,3))==12 and burnside(2,(5,))==8,'finite maximum-order false optimum')
    need(burnside(2,(3,3))!=burnside(2,(3,))**2,'noncoprime product control')
    q=Fraction(1,2);v=Fraction(3,2);delta=Fraction(1,512)
    need(4*delta+2*delta*delta<q*q-q**4,'pair separation domain')
    need(2*delta<q*abs(v-1/v),'directed edge separation domain')
    fine=rounded(matrix(2,3,q,v),8)
    need(len(automorphisms(fine))==factorial(3),'fine rounded shifted symmetry')
    tiny_v=1+Fraction(1,2**40)
    tiny=rounded(matrix(2,3,q,tiny_v),8)
    need(tiny==matrix(2,3,q,Fraction(1)),'tiny-shift rounding control')
    need(len(automorphisms(tiny))==48,'tiny shift did not acquire reflections')
    coarse=rounded(matrix(2,2,Fraction(1,4),Fraction(1)),0)
    need(len(automorphisms(coarse))==24,'coarse rounding did not acquire nongeometric symmetry')
    arbitrary=matrix(2,5,q,Fraction(1));total=len(arbitrary);eps=Fraction(1,1024)
    for i in range(total):arbitrary[i][i]+=eps*Fraction(i+1,total+1)
    need(len({arbitrary[i][i] for i in range(total)})==total,'unique diagonal control')
    need(total>Fraction(4*total,grouped_knapsack(5)[0]),'arbitrary perturbation upper countercontrol')
    result={'status':'PASS_INDEPENDENT_ORBIT_SCALE_CHECKS','symmetries':sym,
            'partition_families':families,'prime_power_checks':correction_checks,
            'literal_orbits':direct,'controls':{
                'max_order_not_finite_optimum':True,'noncoprime_product_rejected':True,
                'fine_common_rounding_preserves_shifted_group':True,
                'tiny_shift_rounding_gains_reflections':True,
                'coarse_rounding_gains_noncoordinate_symmetry':True,
                'arbitrary_small_entry_errors_can_destroy_all_symmetries':True},
            'scope':'bounded independent enumeration; universal proof and classical Landau theorem separate; no rank or general runtime lower bound'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
