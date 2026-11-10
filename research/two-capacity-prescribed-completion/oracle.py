"""Literal finite-vector-set and complete-GL oracle for two capacities.

No author code, RREF implementation, primary code or proposed criterion is
imported. The census asks whether an actual invertible linear map exists.
Finite coverage is not an extrapolation to the all-field theorem.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = '1d8841030f20e596c24aa8aace249e7ef744d14ba60e745a6b7668c8166df3c0'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def strict(data):
    def pairs(items):
        out = {}
        for key,value in items:
            need(key not in out,'duplicate JSON key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('nonfinite JSON constant '+value)
    return json.loads(data,object_pairs_hook=pairs,parse_constant=bad)


def typed(value):
    need(type(value) in (dict,list,str,int,type(None)),'typed finite receipt')
    if isinstance(value,dict):
        need(all(type(k) is str for k in value),'string JSON keys')
        for child in value.values():
            typed(child)
    elif isinstance(value,list):
        for child in value:
            typed(child)


def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()


def authenticate():
    raw = (HERE/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST,'SOURCE-PINS digest')
    pins = strict(raw)
    need(type(pins['schema_version']) is int and pins['schema_version'] == 1,'pin schema')
    need(len(pins['files']) == 2,'two inert predecessor documents')
    seen = set()
    for row in pins['files']:
        path = row['path']
        need(path.startswith('inputs/') and '..' not in path and path not in seen,'source path')
        seen.add(path)
        data = (HERE/path).read_bytes()
        need(type(row['bytes']) is int and len(data) == row['bytes'],'source byte count')
        need(hashlib.sha256(data).hexdigest() == row['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],'source Git blob')


class FieldVectors:
    """Vector codes are base-q digits with coordinate0 least significant."""
    def __init__(self,q,n):
        need(q in (2,3,5) and type(n) is int and 0 <= n <= 3,'finite field/domain')
        self.q,self.n,self.size = q,n,q**n
        self.digits = [tuple((x//q**i)%q for i in range(n)) for x in range(self.size)]
        self.add = [[sum(((a+b)%q)*q**i for i,(a,b) in enumerate(zip(x,y)))
                     for y in self.digits] for x in self.digits]
        self.scale = [[sum(((c*a)%q)*q**i for i,a in enumerate(x))
                       for x in self.digits] for c in range(q)]
        self.basis = tuple(q**i for i in range(n))

    def extend(self,space,vector):
        return frozenset(self.add[x][self.scale[c][vector]] for x in space for c in range(self.q))

    def span(self,generators):
        out = frozenset([0])
        for vector in generators:
            need(type(vector) is int and 0 <= vector < self.size,'literal vector code')
            out = self.extend(out,vector)
        return out

    def action(self,columns):
        out = []
        for digits in self.digits:
            y = 0
            for digit,column in zip(digits,columns):
                y = self.add[y][self.scale[digit][column]]
            out.append(y)
        need(sorted(out) == list(range(self.size)),'enumerated basis gives permutation')
        return tuple(out)

    def bases(self,fixed=()):
        start = self.span(fixed)
        need(len(start) == self.q**len(fixed),'independent prescribed columns')
        def walk(columns,space):
            if len(columns) == self.n:
                yield tuple(columns)
                return
            for vector in range(self.size):
                if vector not in space:
                    yield from walk(columns+[vector],self.extend(space,vector))
        return list(walk(list(fixed),start))

    def subspaces(self):
        found = {1:frozenset([0])}
        queue = [frozenset([0])]
        cursor = 0
        while cursor < len(queue):
            space = queue[cursor]
            cursor += 1
            for vector in range(self.size):
                if vector in space:
                    continue
                new = self.extend(space,vector)
                mask = sum(1<<x for x in new)
                if mask not in found:
                    found[mask] = new
                    queue.append(new)
        return [(mask,found[mask]) for mask in sorted(found)]


def image_mask(action,space):
    return sum(1<<action[x] for x in space)


def image_table(field,spaces,columns):
    index = {mask:i for i,(mask,_) in enumerate(spaces)}
    out = []
    for basis in columns:
        action = field.action(basis)
        out.append(tuple(index[image_mask(action,space)] for _,space in spaces))
    return out


def rank_census(r,spaces,images,columns,field,domain_digest):
    m = len(spaces)
    chosen = [image for basis,image in zip(columns,images) if basis[:r] == field.basis[:r]]
    need(chosen,'at least identity prescribed extension')
    supersets = []
    for mask,_ in spaces:
        supersets.append(sum(1<<i for i,(cap,_) in enumerate(spaces) if mask&~cap == 0))
    digest = hashlib.sha256()
    feasible = 0
    for A in range(m):
        for B in range(m):
            possible = [0]*m
            # Union over literal image pairs from actual full GL matrices.
            for image in chosen:
                allowedC,allowedD = supersets[image[A]],supersets[image[B]]
                for C in range(m):
                    if allowedC>>C&1:
                        possible[C] |= allowedD
            bits = bytearray()
            for C in range(m):
                for D in range(m):
                    value = (possible[C]>>D)&1
                    bits.append(value)
                    feasible += value
            digest.update(bits)
            domain_digest.update(bits)
    return {'rank':r,'prescribed_extensions':len(chosen),'cases':m**4,
            'feasible':feasible,'infeasible':m**4-feasible,'feasibility_sha256':digest.hexdigest()}


def domain(q,n):
    field = FieldVectors(q,n)
    spaces = field.subspaces()
    columns = field.bases()
    images = image_table(field,spaces,columns)
    digest = hashlib.sha256()
    ranks = [rank_census(r,spaces,images,columns,field,digest) for r in range(n+1)]
    return {'q':q,'n':n,'subspaces':len(spaces),'subspace_masks':[mask for mask,_ in spaces],
            'GL':len(columns),'ranks':ranks,'cases':sum(row['cases'] for row in ranks),
            'feasible':sum(row['feasible'] for row in ranks),'feasibility_sha256':digest.hexdigest()}


def actual_extensions(field,U,A,B,C,D,fixed=(),ignoreA=False,ignoreB=False):
    matrices = field.bases(fixed)
    prescribed,individualA,individualB,joint = 0,0,0,0
    first = None
    for columns in matrices:
        action = field.action(columns)
        if any(action[x] != x for x in U):
            continue
        prescribed += 1
        a = all(action[x] in C for x in A)
        b = all(action[x] in D for x in B)
        individualA += int(a)
        individualB += int(b)
        if (a or ignoreA) and (b or ignoreB):
            joint += 1
            if first is None:
                first = list(columns)
    return {'prescribed_extensions':prescribed,'capacity_A_extensions':individualA,
            'capacity_B_extensions':individualB,'joint_extensions':joint,'first_joint_columns':first}


def named_cases():
    discriminators,mixed,controls = [],[],[]
    for q in (2,3,5):
        f = FieldVectors(q,3)
        e0,e1,e2 = f.basis
        U = f.span([e0,e1])
        A,B = f.span([f.add[e0][e2]]),f.span([e2])
        C,D = f.span([e0,e2]),f.span([e0,f.add[e1][e2]])
        count = actual_extensions(f,U,A,B,C,D,fixed=(e0,e1))
        need(count['joint_extensions'] == 0,'literal joint obstruction')
        need(count['capacity_A_extensions'] > 0 and count['capacity_B_extensions'] > 0,'individual capacity passes')
        discriminators.append({'q':q,'n':3,'U':sorted(U),'A':sorted(A),'B':sorted(B),
                               'C':sorted(C),'D':sorted(D),**count})
        relaxedA = actual_extensions(f,U,A,B,C,D,fixed=(e0,e1),ignoreA=True)
        relaxedB = actual_extensions(f,U,A,B,C,D,fixed=(e0,e1),ignoreB=True)
        need(relaxedA['joint_extensions'] > 0 and relaxedB['joint_extensions'] > 0,'actual omitted-capacity controls')
        controls.append({'q':q,'name':'omit one of the actual image inclusions',
                         'omitA_extensions':relaxedA['joint_extensions'],'omitB_extensions':relaxedB['joint_extensions']})
        g = FieldVectors(q,2)
        a,b = g.basis
        V = g.span([g.add[a][g.scale[q-1][b]]])
        A,B = g.span([a]),g.span([b])
        count = actual_extensions(g,V,A,B,A,B)
        need(count['joint_extensions'] > 0,'mixed relation must remain feasible')
        mixed.append({'q':q,'n':2,'U':sorted(V),'A':sorted(A),'B':sorted(B),
                      'C':sorted(A),'D':sorted(B),**count})
    return {'discriminating_joint_obstruction':discriminators,
            'feasible_cross_relation':mixed,'controls':controls}


def build():
    authenticate()
    domains = [domain(q,n) for q,n in ((2,0),(2,1),(2,2),(2,3),(3,2),(5,2))]
    return {'schema_version':1,'source_manifest_sha256':MANIFEST,
            'method':'literal finite vector sets; actual complete GL image-pair existence',
            'ordering':'numeric membership mask; vector code baseq coordinate0 least significant',
            'transcript':'r,A,B,C,D nested order; one byte0/1 per feasibility decision',
            'domains':domains,'named_cases':named_cases(),
            'scope':'Finite normalized prescribed-identity maps only; no all-field inference or native/symplectic/phase/cost/kappa admission.'}


def census_projection(result):
    out = []
    for row in result['domains']:
        ranks = [{key:r[key] for key in ('rank','cases','feasible','feasibility_sha256')}
                 for r in row['ranks']]
        out.append({key:row[key] for key in ('q','n','subspace_masks','cases','feasible','feasibility_sha256')})
        out[-1]['ranks'] = ranks
    typed(out)
    return out


def compare_primary(result):
    primary = strict((HERE/'RESULT.json').read_bytes())
    need(type(primary['schema_version']) is int and primary['schema_version'] == 1,'primary receipt schema')
    need(primary['source_manifest_sha256'] == MANIFEST,'primary source binding')
    need(census_projection(primary) == census_projection(result),'complete per-rank/domain census comparison')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    result = build()
    typed(result)
    if args.emit:
        print(encode(result).decode(),end='')
    else:
        retained = strict((HERE/'ORACLE.json').read_bytes())
        typed(retained)
        need(retained == result,'strict retained ORACLE')
        compare_primary(result)
        print('PASS_TWO_CAPACITY_LITERAL_GL_ORACLE')


if __name__ == '__main__':
    main()
