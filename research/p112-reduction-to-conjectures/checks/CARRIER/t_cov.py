import random, itertools
from cov import can_cover, rref_basis, inspan
random.seed(7)
n=5
def all_subspaces(d):
    seen=set()
    for vs in itertools.combinations(range(1,2**n),d):
        b=rref_basis(list(vs))
        if len(b)==d: seen.add(b)
    return seen
SUB={d:all_subspaces(d) for d in (1,2,3)}
bad=0
for _ in range(300):
    k=random.randint(2,9); labs=tuple(sorted(random.sample(range(1,2**n),k)))
    ds=tuple(sorted(random.choice([(2,2),(3,2),(3,1),(2,),(3,)]),reverse=True)); s=random.randint(0,2)
    # brute
    def brute():
        for choice in itertools.product(*[list(SUB[d]) for d in ds]):
            rest=[v for v in labs if not any(inspan(v,B) for B in choice)]
            if len(rest)<=s: return True
        return False
    if brute()!=can_cover(labs,ds,s): bad+=1; print('MISMATCH',labs,ds,s)
print('bad',bad)
