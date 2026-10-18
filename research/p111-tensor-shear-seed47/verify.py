"""Exact finite P111 two-factor decoder shear census, standard library only.
Prepared for @woklerx with substantial OpenAI Codex assistance. Apache-2.0.
Credits: PR620/757/761 depth-one P111 floors; PR765 tensor-support scope.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
PRIME = 65521


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def strict_load(raw):
    def pairs(items):
        out = {}
        for k,v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    def bad(x):
        raise ValueError('nonfinite JSON value')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def binary_basis(vectors):
    pivots = {}
    kept = []
    for value in vectors:
        x = value
        while x:
            p = x.bit_length()-1
            if p not in pivots:
                pivots[p] = x
                kept.append(value)
                break
            x ^= pivots[p]
    return kept


def basis_q(rows):
    reduced, pivots, chosen = [], [], []
    for index,row in enumerate(rows):
        v = list(map(Fraction,row))
        for b,p in zip(reduced,pivots):
            if v[p]:
                x = v[p]
                v = [a-x*c for a,c in zip(v,b)]
        p = next((i for i,x in enumerate(v) if x),None)
        if p is not None:
            x = v[p]
            reduced.append([a/x for a in v]); pivots.append(p); chosen.append(index)
            if len(reduced) == len(row):
                break
    return [rows[i] for i in chosen]


def rank_mod(rows, width, stop=None):
    pivots = {}
    for row in rows:
        v = [x % PRIME for x in row]
        for p in sorted(pivots):
            x = v[p]
            if x:
                b = pivots[p]
                for j in range(p,width):
                    v[j] = (v[j]-x*b[j]) % PRIME
        p = next((i for i,x in enumerate(v) if x),None)
        if p is not None:
            z = pow(v[p],-1,PRIME)
            pivots[p] = [(x*z)%PRIME for x in v]
            if len(pivots) == (stop or width):
                break
    return len(pivots)


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def tensor(a,b):
    return [x*y for x in a for y in b]


def model():
    raw = (ROOT/SOURCE).read_bytes()
    pins = strict_load((HERE/'SOURCES.json').read_bytes())
    need(set(pins)=={'base_commit','word','word_sha256','predecessors'},'source manifest fields')
    need(pins['word']==SOURCE and pins['base_commit']=='8bddbee377e2f3ce1f1247196c4b290d55767d20',
         'source manifest identity')
    need(hashlib.sha256(raw).hexdigest()==pins['word_sha256'],'selected word source hash mismatch')
    w = strict_load(gzip.decompress(raw)); lines = w['lines']
    need(w['v']==111 and len(lines)==111 and all(len(x)==8 for x in lines),'P111 dimensions')
    need(all(dot(x,x)==4 for x in lines),'E8 normalization')
    gram = [[dot(x,y) for y in lines] for x in lines]
    need(all(x%2==0 for row in gram for x in row),'integral half Gram')
    decoder = [sum(((1+x//2)%2)<<j for j,x in enumerate(row)) for row in gram]
    generators = binary_basis(decoder)
    need(len(generators)==9,'decoder rank')
    supports = []
    for mask in range(1,512):
        support = 0
        for j,g in enumerate(generators):
            if mask>>j&1: support ^= g
        span = basis_q([lines[j] for j in range(111) if support>>j&1])
        supports.append((support,len(span)))
    counts = Counter(r for _,r in supports)
    need(counts=={7:9,8:502},'exact support-rank spectrum')
    readers = sorted(s for s,r in supports if r==7)
    need(len(binary_basis(readers))==9,'rank-seven reader basis')
    # Unique coordinates in the nine reader columns: exhaustive 512-entry table.
    coordinates = {}
    for mask in range(512):
        value = 0
        for j,r in enumerate(readers):
            if mask>>j&1:value ^= r
        need(value not in coordinates,'reader basis dependence')
        coordinates[value] = mask
    sources = [0]*9
    for j,column in enumerate(decoder):
        mask = coordinates[column]
        for t in range(9):
            if mask>>t&1:sources[t] |= 1<<j
    sb = [basis_q([lines[j] for j in range(111) if s>>j&1]) for s in sources]
    rb = [basis_q([lines[j] for j in range(111) if r>>j&1]) for r in readers]
    need(all(len(b)==7 for b in rb) and all(len(b) in (7,8) for b in sb),'product source/reader dimensions')
    need(all(rank_mod([[dot(a,b) for b in rb[t]] for a in sb[t]],7)==7 for t in range(9)),
         'base pairing ranks')
    # Explicit reconstruction checks every source/target coefficient.
    for i in range(111):
        for j in range(111):
            value = sum(((readers[t]>>i)&1)*((sources[t]>>j)&1) for t in range(9))%2
            need(value == ((decoder[i]>>j)&1),'nine-term decoder reconstruction')
    return lines,sources,readers,sb,rb,dict(sorted(counts.items()))


def category_cache(lines, families, opposite):
    cache = {}
    for i in range(9):
        for j in range(9):
            for fixed in (i,j):
                key = (i,j,fixed)
                if key in cache:continue
                categories = [[] for _ in range(4)]
                for t,line in enumerate(lines):
                    tag = ((families[i]>>t)&1)+2*((families[j]>>t)&1)
                    categories[tag].append([dot(line,b) for b in opposite[fixed]])
                cache[key] = [basis_q(rows) if rows else [] for rows in categories]
    return cache


def xor_projected_rows(cache,i,j,k,l,fixed_first,fixed_second):
    first = cache[i,k,fixed_first]; second = cache[j,l,fixed_second]
    for a in range(4):
        for b in range(4):
            if (((a&1)*(b&1)) ^ ((a>>1)*(b>>1))):
                for x in first[a]:
                    for y in second[b]:
                        yield tensor(x,y)


def direct_rows(lines,family,opposite,i,j,k,l,fixed_first,fixed_second):
    left = [[dot(line,b) for b in opposite[fixed_first]] for line in lines]
    right = [[dot(line,b) for b in opposite[fixed_second]] for line in lines]
    for a in range(111):
        for b in range(111):
            if (((family[i]>>a)&1)*((family[j]>>b)&1)) ^ (((family[k]>>a)&1)*((family[l]>>b)&1)):
                yield tensor(left[a],right[b])


def run():
    need(all(PRIME%d for d in range(2,257)),'modulus not prime')
    lines,sources,readers,sb,rb,spectrum = model()
    sc = category_cache(lines,sources,rb)
    rc = category_cache(lines,readers,sb)
    histogram = Counter(); records = []; direct = []
    terms = list(itertools.product(range(9),repeat=2))
    for a,(i,j) in enumerate(terms):
        for b,(k,l) in enumerate(terms):
            if a==b:continue
            left = rank_mod(xor_projected_rows(sc,i,j,k,l,i,j),49,49)
            right_width = len(sb[k])*len(sb[l])
            right = rank_mod(xor_projected_rows(rc,i,j,k,l,k,l),right_width,49)
            cost = 79*49+left+right
            histogram[cost]+=1
            records.append([a,b,left,right])
            # Deterministic independent full-grid constructors: 18 cases,
            # including shared factor and distinct-factor patterns.
            if (a,b) in {(0,1),(0,9),(0,10),(47,0),(0,47),(80,0)} | {(47,x) for x in range(12)}:
                dl = rank_mod(direct_rows(lines,sources,rb,i,j,k,l,i,j),49,49)
                dr = rank_mod(direct_rows(lines,readers,sb,i,j,k,l,k,l),right_width,49)
                need((dl,dr)==(left,right),'independent full-grid rank mismatch')
                direct.append([a,b,dl,dr])
    need(sum(histogram.values())==6480,'ordered shear coverage')
    need(dict(histogram)=={3969:6480},'unexpected lower-rank shear: inspect candidate')
    controls=[]
    def reject(label,fn):
        try:fn()
        except ValueError:controls.append(label);return
        raise ValueError('negative control accepted: '+label)
    reject('wrong shear census',lambda:need(sum(histogram.values())==6481,'coverage'))
    reject('optimistic cost',lambda:need(min(histogram)==3968,'cost'))
    reject('singular pairing',lambda:need(rank_mod([[0]*7]*7,7)==7,'pair rank'))
    reject('missing reader',lambda:need(len(binary_basis(readers[:-1]))==9,'basis rank'))
    def shear_identity(dual=True):
        for a,b,c,d in itertools.product((0,1),repeat=4):
            old=(a*c)^(b*d)
            new=((a^b)*c)^(b*(d^c if dual else d))
            need(old==new,'rank-one shear identity')
    shear_identity()
    reject('omitted dual reader update',lambda:shear_identity(False))
    reject('duplicate JSON key',lambda:strict_load('{"n":1,"n":2}'))
    reject('nonfinite JSON',lambda:strict_load('{"n":NaN}'))
    need(canonical({'n':1})!=canonical({'n':True}),'strict receipt types')
    return {'format':'p111-tensor-shear/1','seed':47,'status':'PASS_P111_TENSOR_SHEARS',
        'base_commit':'8bddbee377e2f3ce1f1247196c4b290d55767d20','base_support_spectrum':spectrum,
        'base_sources':[str(x) for x in sources],'base_readers':[str(x) for x in readers],
        'source_span_dimensions':[len(b) for b in sb], 'reader_span_dimensions':[len(b) for b in rb],
        'tensor_terms':81,'baseline_pairing_rank_sum':3969,'ordered_shears':6480,
        'shear_identity_boolean_inputs':16,
        'changed_pairing_rank_lower_bounds':dict(Counter(x for r in records for x in r[2:])),
        'cost_lower_bound_histogram':dict(histogram),'all_rank_bounds_sha256':hashlib.sha256(canonical(records)).hexdigest(),
        'direct_grid_checks':direct,'controls_rejected':controls,'prime':PRIME,
        'scope':'One elementary GL81 shear from the fixed optimal product basis; not arbitrary recoding, delivery, or a kappa bound.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true');args=parser.parse_args()
    result=run();path=HERE/'CERTIFICATE.json'
    if args.write_certificate:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
    else:need(canonical(strict_load(canonical(result)))==canonical(strict_load(path.read_bytes())),'certificate mismatch')
    print('PASS_P111_TENSOR_SHEARS ordered=6480 cost=3969 direct={} controls={} no_new_kappa'.format(
        len(result['direct_grid_checks']),len(result['controls_rejected'])),flush=True)


if __name__=='__main__':main()
