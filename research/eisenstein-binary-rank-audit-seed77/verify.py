"""Independent binary-rank certificate for the PR2017 scalar copy floor.
Charles Bethin, with substantial OpenAI Codex assistance. Apache-2.0.
Pinned coordinate input: Jonathan Lam / PR798, following GamingPuzzled / PR620.
The rank-witness construction is derived from Jose Manuel / PR2017.
No PR2017 field arithmetic, rank routine, or support sampling is imported.
"""
import importlib.util
import hashlib
import json
import sys
import time
from collections import Counter
from itertools import combinations
from pathlib import Path
from math import isqrt

ROOT = Path(__file__).resolve().parents[2]
P = 2147483647
HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def modular_rref(rows, width):
    a = [[x % P for x in row] for row in rows]
    h = 0
    for j in range(width):
        k = next((i for i in range(h, len(a)) if a[i][j]), None)
        if k is None:
            continue
        a[h], a[k] = a[k], a[h]
        scale = pow(a[h][j], -1, P)
        a[h] = [(x*scale) % P for x in a[h]]
        for i in range(len(a)):
            if i != h and a[i][j]:
                scale = a[i][j]
                a[i] = [(x-scale*y) % P for x, y in zip(a[i], a[h])]
        h += 1
        if h == len(a):
            break
    return tuple(tuple(row) for row in a[:h])


def modular_rank(rows):
    if not rows or not rows[0]:
        return 0
    a = [[x % P for x in row] for row in rows]
    h = 0
    for j in range(len(a[0])):
        k = next((i for i in range(h, len(a)) if a[i][j]), None)
        if k is None:
            continue
        a[h], a[k] = a[k], a[h]
        inv = pow(a[h][j], -1, P)
        for i in range(h+1, len(a)):
            if a[i][j]:
                scale = a[i][j] * inv % P
                for c in range(j, len(a[0])):
                    a[i][c] = (a[i][c]-scale*a[h][c]) % P
        h += 1
        if h == len(a):
            break
    return h


def binary_basis(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return tuple(pivots.values())


def dot(x,y):
    return sum(a*b for a,b in zip(x,y))


def members(mask):
    return [i for i in range(40) if mask >> i & 1]


def coordinates():
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            require(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'source pin: '+item['path'])
    path=ROOT/'research/eisenstein-clique-copy-bound/geometry.py'
    require(hashlib.sha256(path.read_bytes()).hexdigest()=='248df3fb820b5165ca485ad4d43f0271043498c45a59ac1edc310a124073644c','geometry source pin')
    spec=importlib.util.spec_from_file_location('input_geometry',path)
    G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)
    reps,images,adj,_,_=G.geometry()
    rows=[v for pair in zip(reps,images) for v in pair]
    require(len(rows)==80 and all(dot(r,r)==8 for r in rows),'root norm bound')
    return rows,adj


def all_flats(rows):
    # Enumerate generator sets directly; no predecessor flat traversal.
    found={(): ()};tested=0
    for size in (1,2,3):
        for gen in combinations(range(40),size):
            rr=[rows[2*i+t] for i in gen for t in (0,1)]
            basis=modular_rref(rr,8)
            require(len(basis) in (2,4,6),'proper span parity')
            if len(basis)==2*size:
                found.setdefault(basis,gen)
            tested+=1
    for gen in combinations(range(40),4):
        basis=modular_rref([rows[2*i+t] for i in gen for t in (0,1)],8)
        if len(basis)==8:
            found[basis]=gen
            break
    else:
        raise ValueError('full span absent')
    result=[]
    for basis,gen in found.items():
        def inside(vector):
            v=[x % P for x in vector]
            for row in basis:
                pivot=next(j for j,x in enumerate(row) if x)
                scale=v[pivot]
                v=[(x-scale*y)%P for x,y in zip(v,row)]
            return not any(v)
        mask=0
        for i in range(40):
            a,b=inside(rows[2*i]),inside(rows[2*i+1])
            require(a==b,'J closure')
            if a:mask|=1<<i
        result.append({'mask':mask,'rank':len(basis)//2,'generators':gen})
    result.sort(key=lambda f:(f['rank'],f['mask']))
    require(len({f['mask'] for f in result})==len(result),'flat closure uniqueness')
    return result,tested


def binary_witness(rows):
    # Regular representation of a+b*omega is [[a,b],[b,a+b]] over F2.
    # The normalized Gram value has numerator (u-v)-(u+2v)*omega,
    # denominator three, where u=<r,s>/4 and v=<r,Js>/4.
    # Three is one modulo two. Only integer dot products are used here.
    L=[0]*80
    for i in range(40):
        for j in range(40):
            d0=dot(rows[2*i],rows[2*j]);d1=dot(rows[2*i],rows[2*j+1])
            require(d0%4==d1%4==0,'input divisibility')
            u,v=d0//4,d1//4
            a,b=(u-v)&1,u&1
            L[2*i] |= (a | (b<<1)) << (2*j)
            L[2*i+1] |= (b | ((a^b)<<1)) << (2*j)
    return L


def witness_pattern(L,adj):
    for i in range(40):
        for j in range(40):
            block=((L[2*i]>>(2*j))&3,(L[2*i+1]>>(2*j))&3)
            if i==j:require(block==(1,2),'unit diagonal block')
            if i!=j and not (adj[i]>>j)&1:require(block==(0,0),'orthogonal zero block')


def flat_pair_audit(rows,flats,L):
    gram=[[dot(x,y) for y in rows] for x in rows]
    prepared=[]
    for f in flats:
        ports=members(f['mask'])
        selected=[2*i+t for i in ports for t in (0,1)]
        rootbasis=[2*i+t for i in f['generators'] for t in (0,1)]
        require(len(rootbasis)==2*f['rank'],'original basis length')
        prepared.append((rootbasis,binary_basis([L[i] for i in selected]),sum(1<<i for i in selected)))
    histogram=Counter();digest=hashlib.sha256();drops=[];ordered=0
    for i,(ri,bi,ci) in enumerate(prepared):
        for j in range(i,len(prepared)):
            rj,bj,cj=prepared[j]
            qr=modular_rank([[gram[x][y] for y in rj] for x in ri])
            br=len(binary_basis([row & cj for row in bi]))
            reverse=len(binary_basis([row & ci for row in bj]))
            check_pair_bound(qr,br,reverse)
            histogram[(qr//2,br//2)]+=1
            if br<qr and len(drops)<4:drops.append([flats[i]['mask'],flats[j]['mask'],qr,br])
            digest.update(f'{flats[i]["mask"]},{flats[j]["mask"]},{qr},{br},{reverse}\n'.encode())
            ordered+=1 if i==j else 2
    return {'unordered_pairs':len(flats)*(len(flats)+1)//2,'ordered_pairs':ordered,
            'rank_histogram':{f'{a},{b}':n for (a,b),n in sorted(histogram.items())},
            'pair_digest':digest.hexdigest(),'rank_drop_examples':drops}


def check_pair_bound(qr,br,reverse):
    require(qr%2==br%2==reverse%2==0,'pair rank parity')
    require(br<=qr and reverse<=qr,'binary rank exceeds rational pairing')
    require(br==reverse,'transpose rank disagreement')


def validate_prime(prime):
    require(prime>8**8,'prime below certified Gram-minor bound')
    require(prime%2 and all(prime%d for d in range(3,isqrt(prime)+1,2)),'modulus is not prime')


def sharp_row_witness(rows,adj,L):
    pattern=[((1<<40)-1)^adj[i] for i in range(40)]
    cost=0
    for i,source in enumerate(pattern):
        cols=[rows[2*j+t] for j in members(source) for t in (0,1)]
        qr=modular_rank([[dot(rows[2*i+t],v) for v in cols] for t in (0,1)])
        require(qr==2,'row-star cost')
        mask=sum(3<<(2*j) for j in members(source))
        require(L[2*i]&mask==1<<(2*i) and L[2*i+1]&mask==1<<(2*i+1),'masked identity')
        cost+=qr//2
    require(cost==40,'sharp total')
    return cost


def negative_controls(rows,adj,L):
    def rejects(fn,fragment):
        try: fn()
        except ValueError as exc:
            require(fragment in str(exc),'wrong negative-control failure')
            return
        raise ValueError('negative control accepted: '+fragment)
    bad=L.copy();bad[0]^=1
    rejects(lambda:witness_pattern(bad,adj),'diagonal')
    orth=next(j for j in range(1,40) if not (adj[0]>>j)&1)
    bad=L.copy();bad[0]^=1<<(2*orth)
    rejects(lambda:witness_pattern(bad,adj),'orthogonal')
    # The identity satisfies the zero/diagonal pattern but not pairing domination.
    identity=[1<<i for i in range(80)];witness_pattern(identity,adj)
    rejects(lambda:check_pair_bound(8,len(binary_basis(identity)),len(binary_basis(identity))),'exceeds rational')
    rejects(lambda:validate_prime(65537),'minor bound')
    # Omitting one of the two rational dimensions would underprice the full pair.
    rejects(lambda:check_pair_bound(4,len(binary_basis(L)),len(binary_basis(L))),'exceeds rational')
    return ['diagonal corruption','orthogonal-zero corruption','pattern-valid identity fails domination',
            'insufficient modulus rejected','halved pairing bill rejected']


def main():
    start=time.monotonic();validate_prime(P)
    rows,adj=coordinates();flats,tested=all_flats(rows);L=binary_witness(rows);witness_pattern(L,adj)
    certificate={'flats':flats,'binary_witness':L}
    require(json.loads(json.dumps(certificate))==json.loads((HERE/'CERTIFICATE.json').read_text()),'complete certificate mismatch')
    result={'generator_sets':tested,'flat_count':len(flats),'flat_rank_counts':dict(Counter(f['rank'] for f in flats)),
            'prime':P,'root_minor_bound':4096,'gram_minor_bound':8**8,'binary_witness_rank':len(binary_basis(L)),
            'pairs':flat_pair_audit(rows,flats,L),'row_star_charge':sharp_row_witness(rows,adj,L),
            'negative_controls':negative_controls(rows,adj,L)}
    require(json.loads(json.dumps(result))==json.loads((HERE/'EXPECTED.json').read_text()),'receipt mismatch')
    print(json.dumps({'sys_version':sys.version,'sys_executable':sys.executable,'result':result,'seconds':time.monotonic()-start},indent=2))
    print('PASS_EISENSTEIN_BINARY_RANK_AUDIT')

if __name__=='__main__':main()
