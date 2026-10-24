"""Independent set-based row audit; no original dimension/transport helpers.
JoyboyBrian with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from model import need


def vectors(mask):
    answer=[]
    while mask:
        bit=mask & -mask
        answer.append(bit.bit_length()-1)
        mask-=bit
    return answer


def dim(mask):
    n=mask.bit_count()
    need(n > 0 and n & (n-1) == 0, 'Power-of-two subspace size')
    return n.bit_length()-1


def transport(columns,mask):
    result=0
    for v in vectors(mask):
        image=0
        for j,column in enumerate(columns):
            if v >> j & 1:
                image ^= column
        result |= 1 << image
    return result


def subspace(mask):
    generated={0}
    for v in vectors(mask):
        if v not in generated:
            generated |= {u ^ v for u in tuple(generated)}
    need(generated == set(vectors(mask)), 'Domain entry is a subspace')


def interval_count(d):
    total=0
    for k in range(d+1):
        n=z=1
        for j in range(k):
            n *= (2**d-2**j)
            z *= (2**k-2**j)
        need(n % z == 0, 'Gaussian count integral')
        total += n//z
    return total


def canonical(row,low,high):
    return tuple(sorted((k,c) for k,c in row.items() if c)),low,high


def audit(ns,edge,values):
    D,x,yd=ns['D'],ns['x'],ns['yd']
    expected=Counter()
    used=[]
    checked=set()
    for v,domain in D.items():
        need(len(domain) == len(set(domain)) == interval_count(dim(ns['hi'][v])-dim(ns['lo'][v])), 'Complete independent interval census')
        for value in domain:
            need(value & ns['lo'][v] == ns['lo'][v] and value & ns['hi'][v] == value, 'Interval membership')
            if value not in checked:
                subspace(value);checked.add(value)
        need(len(x[v]) == len(domain), 'Frame columns aligned')
        used.extend(x[v])
        expected[canonical(dict.fromkeys(x[v],1),1,1)]+=1
        need([values[k] for k in x[v]] == [F(value == ns['s'].original_values[v]) for value in domain], 'Integral actual source marginal')
    edges=Counter((a,b,tuple(m)) for b,parents in enumerate(ns['g'].parents) for a,m in parents)
    need(edges == ns['E'], 'Complete original graph edge multiset')
    pair_edges=set()
    for (a,b,m),count in edges.items():
        if a not in D or b not in D:
            continue
        pair_edges.add((a,b,m))
        ranks=set()
        for ia,A in enumerate(D[a]):
            moved=transport(m,A)
            allowed=[ib for ib,B in enumerate(D[b]) if moved & B == moved]
            need(allowed,'Source has compatible targets')
            ranks.update(dim(D[b][ib])-dim(A) for ib in allowed)
            if len(allowed) < len(D[b]):
                row={x[b][ib]:-1 for ib in allowed}
                row[x[a][ia]]=1
                expected[canonical(row,float('-inf'),0)]+=1
        ys=yd[a,b,m]
        need(set(ys) == ranks,'Exact attainable rank set')
        used.extend(ys.values())
        expected[canonical(dict.fromkeys(ys.values(),1),1,1)]+=1
        row={k:dim(B) for k,B in zip(x[b],D[b])}
        for k,A in zip(x[a],D[a]):
            row[k]=row.get(k,0)-dim(A)
        for r,k in ys.items():
            row[k]=-r
            need(ns['cost'][k] == count*ns['prices'][r], 'Original rank-discount objective coefficient')
        expected[canonical(row,0,0)]+=1
    need(set(yd) == pair_edges,'All and only flexible-pair selectors')
    need(sorted(used) == list(range(len(values))),'Every column exactly accounted for')
    actual=Counter(canonical(r,l,u) for r,l,u in zip(ns['rows'],ns['lb'],ns['ub']))
    need(expected == actual,'Independent complete row multiset')
    a,b,m=edge
    # Generate the displayed rank-zero/rank-two pair from its stated basis.
    elems={0}
    for v in (5,11,16,35,64,128,256):
        elems |= {u^v for u in tuple(elems)}
    C=sum(1<<v for v in elems)
    B=ns['s'].original_values[b]
    need(C in D[a] and C in D[b] and B in D[b], 'Displayed endpoint domains')
    need(transport(m,C)==C and dim(C)==7 and dim(B)==9,'Displayed allowed ranks zero and two')
    return {'independent_rows':sum(expected.values()),'independent_columns':len(used),
            'unique_domain_subspaces_checked':len(checked),'displayed_rank_pairs_checked':True}


def pair_consistent(ns,edge,values):
    # Nonnegative pair mass with two one-hot marginals is uniquely determined.
    a,b,m=edge
    chosen=[]
    for node in (a,b):
        support=[V for V,k in zip(ns['D'][node],ns['x'][node]) if values[k]]
        need(len(support)==1,'One-hot pair face')
        chosen.append(support[0])
    actual=dim(chosen[1])-dim(chosen[0])
    need(all(values[k] == F(r==actual) for r,k in ns['yd'][edge].items()),'Pair-consistency excludes ghost ranks')
