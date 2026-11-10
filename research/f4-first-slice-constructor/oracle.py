"""Independent F4 carryless arithmetic and literal raw-pencil oracle.

No source Field, author checker or primary program is imported/executed.
Petalas6451 retains the threshold/attainers;6543 the first-success algorithm;
Ali5664 and the retained nonprime-pencil lineage retain their prior work.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = '4ddc2862bf5e8f3a718ec60a9b2c8ed12b97bda679a719c5b4f5db0bd77b15b9'
INPUTS = 'ce46d3e6f89e261e4cb9e4f5260e27c9ab498b619b4bd812f4b00b0d50ad4db8'
FIELDS = {}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def decode(raw):
    def unique(items):
        out = {}
        for key,value in items:
            need(key not in out,'duplicate JSON receipt key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('noninteger/nonfinite receipt number '+value)
    return json.loads(raw,object_pairs_hook=unique,parse_float=bad,parse_constant=bad)


def authenticate():
    raw = (HERE/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST,'source manifest SHA256')
    pins = decode(raw)
    need(type(pins['schema_version']) is int and pins['schema_version'] == 1,'source schema')
    need(len(pins['files']) == 6,'all six source objects authenticated')
    seen = set()
    for row in pins['files']:
        path = row['local_path']
        need(path.startswith('inputs/') and '..' not in path and path not in seen,'source path')
        seen.add(path)
        data = (HERE/path).read_bytes()
        need(type(row['bytes']) is int and len(data) == row['bytes'],'source SHA256 length')
        need(hashlib.sha256(data).hexdigest() == row['sha256'],'source SHA256 '+path)
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],'source Git blob '+path)
    raw = (HERE/'PENCILS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == INPUTS,'literal pencil SHA256')
    data = decode(raw)
    need(data['base_field'] == {'cardinality':4,'characteristic':2,'encoding':'base2 low-first,2=z,3=z+1','modulus':[1,1,1]},'literal base-field specification')
    need(len(data['fixtures']) == 10 and len({x['name'] for x in data['fixtures']}) == 10,'complete named raw-input domain')
    return data['fixtures']


def carryless(a,b):
    """Multiply in F2[z]/(z²+z+1), independently of any field source."""
    out = 0
    while b:
        if b&1:
            out ^= a
        b >>= 1
        a <<= 1
        if a&4:
            a ^= 7
    return out


MUL = tuple(tuple(carryless(a,b) for b in range(4)) for a in range(4))


def trim(poly):
    out = list(poly)
    while len(out)>1 and out[-1] == 0:
        out.pop()
    return out


def evaluate(poly,a):
    value = 0
    for coefficient in reversed(poly):
        value = MUL[value][a]^coefficient
    return value


def irreducible(poly):
    e = len(poly)-1
    return e in (1,2,3) and poly[-1] == 1 and (e == 1 or all(evaluate(poly,a) for a in range(4)))


class Extension:
    def __init__(self,h):
        need(type(h) is list and 2 <= len(h) <= 4,'bounded monic relative degree')
        need(all(type(x) is int and 0 <= x < 4 for x in h),'canonical F4 modulus coefficients')
        need(irreducible(h),'F4 no-root irreducibility in degrees2/3')
        self.h,self.e = h[:],len(h)-1
        self.size = 4**self.e
        self.cache = {}

    def mul(self,a,b):
        if self.e == 1:
            return MUL[a][b]
        if not a or not b:
            return 0
        if a == 1:
            return b
        if b == 1:
            return a
        key = (min(a,b),max(a,b))
        if key in self.cache:
            return self.cache[key]
        x,y = [(a>>(2*i))&3 for i in range(self.e)],[(b>>(2*i))&3 for i in range(self.e)]
        work = [0]*(2*self.e-1)
        for i,c in enumerate(x):
            for j,d in enumerate(y):
                work[i+j] ^= MUL[c][d]
        for k in range(len(work)-1,self.e-1,-1):
            coefficient = work[k]
            work[k] = 0
            for j in range(self.e):
                work[k-self.e+j] ^= MUL[coefficient][self.h[j]]
        value = sum(work[i]<<(2*i) for i in range(self.e))
        self.cache[key] = value
        return value

    def power(self,a,n):
        value = 1
        while n:
            if n&1:
                value = self.mul(value,a)
            a = self.mul(a,a)
            n >>= 1
        return value

    def inv(self,a):
        need(a != 0,'nonzero field pivot')
        value = self.power(a,self.size-2)
        need(self.mul(a,value) == 1,'literal field inverse product')
        return value

    def external(self,a):
        return trim([(a>>(2*i))&3 for i in range(self.e)])

    def internal(self,a):
        need(type(a) is list and 1 <= len(a) <= self.e,'field element array')
        need(all(type(x) is int and 0 <= x < 4 for x in a),'field element F4 codes')
        need(a == trim(a),'canonical trimmed field element')
        return sum(x<<(2*i) for i,x in enumerate(a))


def field(e):
    if e not in FIELDS:
        need(type(e) is int and e in (1,2,3),'bounded relative extension')
        for code in range(4**e):
            h = [(code>>(2*i))&3 for i in range(e)]+[1]
            if irreducible(h):
                FIELDS[e] = Extension(h)
                break
        need(e in FIELDS,'independent small field presentation')
    return FIELDS[e]


def validate_matrices(A,B):
    need(type(A) is list and type(B) is list and len(A) == len(B) <= 17,'bounded square raw pencil')
    n = len(A)
    need(all(type(row) is list and len(row) == n for M in (A,B) for row in M),'square raw rows')
    need(all(type(x) is int and 0 <= x < 4 for M in (A,B) for row in M for x in row),'canonical nonboolean F4 inputs')
    return n


def inverse_matrix(M,K):
    n = len(M)
    work = [row[:]+[int(i==j) for j in range(n)] for i,row in enumerate(M)]
    for column in range(n):
        pivot = next((r for r in range(column,n) if work[r][column]),None)
        if pivot is None:
            return None
        work[column],work[pivot] = work[pivot],work[column]
        scale = K.inv(work[column][column])
        work[column] = [K.mul(x,scale) for x in work[column]]
        for row in range(n):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [a^K.mul(factor,b) for a,b in zip(work[row],work[column])]
    return [row[n:] for row in work]


def multiply_matrix(A,B,K):
    n = len(A)
    out = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                out[i][j] ^= K.mul(A[i][k],B[k][j])
    return out


def check_inverse(M,inv,K):
    identity = [[int(i==j) for j in range(len(M))] for i in range(len(M))]
    need(multiply_matrix(M,inv,K) == identity,'actual slice times inverse')
    need(multiply_matrix(inv,M,K) == identity,'actual inverse times slice')


def slice_matrix(A,B,alpha,K):
    return [[K.mul(alpha,a)^b for a,b in zip(x,y)] for x,y in zip(A,B)]


def serialize_matrix(M,K):
    return [[K.external(x) for x in row] for row in M]


def own_answer(A,B,e,infinity,alpha,inv):
    K = field(e)
    M = A if infinity else slice_matrix(A,B,alpha,K)
    check_inverse(M,inv,K)
    return {'e':e,'infinity':infinity,'field_modulus':K.h,
            'alpha':None if infinity else K.external(alpha),
            'slice':serialize_matrix(M,K),'inverse':serialize_matrix(inv,K)}


def first_success(A,B):
    n = validate_matrices(A,B)
    inv = inverse_matrix(A,field(1))
    if inv is not None:
        return own_answer(A,B,1,True,None,inv)
    bound = 1
    while 4**bound <= n:
        bound += 1
    need(bound <= 3,'finite root-bound extension cap')
    for e in range(1,bound+1):
        K = field(e)
        for alpha in range(K.size):
            M = slice_matrix(A,B,alpha,K)
            inv = inverse_matrix(M,K)
            if inv is not None:
                return own_answer(A,B,e,False,alpha,inv)
    # The final field has more than n affine points; all vanish, hence det=0.
    return None


def det2(M):
    return MUL[M[0]][M[3]]^MUL[M[1]][M[2]]


def poly2(A,B):
    middle = MUL[A[0]][B[3]]^MUL[B[0]][A[3]]^MUL[A[1]][B[2]]^MUL[B[1]][A[2]]
    return trim([det2(B),middle,det2(A)])


def nested(flat):
    return [list(flat[:2]),list(flat[2:])]


def inverse2(M):
    determinant = det2(M)
    need(determinant != 0,'invertible base2x2')
    scalar = MUL[determinant][determinant]
    inv = [MUL[scalar][x] for x in (M[3],M[1],M[2],M[0])]
    check_inverse(nested(M),nested(inv),field(1))
    return inv


def base_census(stream):
    digest = hashlib.sha256()
    singular,stream_bytes = 0,0
    counts = Counter()
    for acode in range(256):
        A = [(acode>>(2*i))&3 for i in range(4)]
        for bcode in range(256):
            B = [(bcode>>(2*i))&3 for i in range(4)]
            determinant = poly2(A,B)
            matrices = [A]+[[MUL[a][x]^y for x,y in zip(A,B)] for a in range(4)]
            values = [det2(M) for M in matrices]
            need(any(values) == (determinant != [0]),'all five projective values and literal determinant polynomial')
            if not any(values):
                singular += 1
                row = [acode,bcode,determinant,'singular',None,None,None,None]
            else:
                point = next(i for i,value in enumerate(values) if value)
                M = matrices[point]
                inv = inverse2(M)
                kind = 'infinity' if point == 0 else 'affine'
                alpha = None if point == 0 else point-1
                counts['infinity' if point == 0 else str(alpha)] += 1
                row = [acode,bcode,determinant,'regular',kind,alpha,nested(M),nested(inv)]
            raw = (canonical(row)+'\n').encode()
            digest.update(raw);stream_bytes += len(raw)
            if stream is not None:
                stream.write(raw)
    return {'cases':65536,'singular':singular,'regular':65536-singular,
            'stream_sha256':digest.hexdigest(),'stream_bytes':stream_bytes,'point_counts':dict(sorted(counts.items()))}


def validate_provided(A,B,answer,minimum):
    n = validate_matrices(A,B)
    need(type(answer['e']) is int and answer['e'] == minimum,'literal least extension degree')
    need(type(answer['infinity']) is bool,'literal projective marker')
    K = Extension(answer['field_modulus'])
    need(K.e == minimum,'returned modulus degree')
    if answer['infinity']:
        need(minimum == 1 and answer['alpha'] is None,'infinity is a base-field slice')
        M = A
    else:
        M = slice_matrix(A,B,K.internal(answer['alpha']),K)
    parsed = []
    for key in ('slice','inverse'):
        value = answer[key]
        need(type(value) is list and len(value) == n and all(type(row) is list and len(row) == n for row in value),'complete supplied matrix')
        parsed.append([[K.internal(x) for x in row] for row in value])
    need(parsed[0] == M,'actual base embedding and alphaA+B source binding')
    check_inverse(M,parsed[1],K)


def reject(callback):
    try:
        callback()
    except ValueError as error:
        return str(error)
    raise ValueError('counterfactual accepted')


def arithmetic_controls(fixtures):
    need(MUL[2][2] == 3 and (2*2)%4 == 0,'actual F4 versus Z4 determinant difference')
    p_roots = [a for a in range(4) if MUL[a][a]^a == 0]
    q_roots = [a for a in range(4) if MUL[MUL[a][a]][MUL[a][a]]^a == 0]
    need(p_roots == [0,1] and q_roots == [0,1,2,3],'p versus q Frobenius roots')
    need(field(2).mul(2,2) == 3 and field(3).mul(2,2) == 3,'genuine nonprime constant embedding')
    row = next(x for x in fixtures if x['answer'] is not None and x['answer']['e'] == 2)
    bad = decode(canonical(row['answer']));bad['field_modulus'] = [1,1,1]
    reducible = reject(lambda:validate_provided(row['A'],row['B'],bad,2))
    bad = decode(canonical(row['answer']));entry = bad['inverse'][0][0];entry[0] ^= 1
    bad['inverse'][0][0] = trim(entry)
    wrong_inverse = reject(lambda:validate_provided(row['A'],row['B'],bad,2))
    base = next(x for x in fixtures if x['name'] == 'nonprime-infinity')
    bad = decode(canonical(base['answer']));bad['slice'][0][0] = [0]
    embedding = reject(lambda:validate_provided(base['A'],base['B'],bad,1))
    noncanonical = reject(lambda:validate_matrices([[True]],[[0]]))
    return {'F4_z_squared':MUL[2][2],'Z4_two_squared':(2*2)%4,
            'actual_constant_matrix':[[2,0],[0,2]],'actual_F4_determinant':det2([2,0,0,2]),
            'actual_F4_inverse':nested(inverse2([2,0,0,2])),
            'p_frobenius_roots':p_roots,'q_frobenius_roots':q_roots,
            'reducible_over_F4':reducible,'altered_inverse':wrong_inverse,
            'collapsed_base_embedding':embedding,'boolean_coefficient':noncanonical}


def compute(stream=None):
    inputs = authenticate()
    census = base_census(stream)
    fixtures = []
    for row in inputs:
        answer = first_success(row['A'],row['B'])
        degree = None if answer is None else answer['e']
        need(degree == row['expected_degree'],'prospective named degree calibration after actual search')
        fixtures.append({'name':row['name'],'A':row['A'],'B':row['B'],
                         'status':'singular' if answer is None else 'regular','answer':answer})
    return {'schema_version':1,'source_manifest_sha256':MANIFEST,'inputs_sha256':INPUTS,
            'method':'Independent carryless F4, all five projective values, adjugate2x2 inverses, independent F16/F64 quotient scans and Gaussian witnesses',
            'census':census,'fixtures':fixtures,'controls':arithmetic_controls(fixtures),
            'scope':'Fixed F4 backend and frozen raw matrices only; inherited thresholds/first-success theorem, general-field complexity, descent,native/physical prices and kappa are not newly proved.'}


def compare_primary(result):
    primary = decode((HERE/'RESULT.json').read_bytes())
    need(type(primary['schema_version']) is int and primary['schema_version'] == 1,'primary receipt schema')
    need(primary['source_manifest_sha256'] == MANIFEST and primary['inputs_sha256'] == INPUTS,'primary source/input receipt binding')
    for key in ('cases','singular','regular','stream_sha256'):
        need(canonical(primary['census'][key]) == canonical(result['census'][key]),'complete literal base stream receipt '+key)
    expected = {row['name']:row for row in result['fixtures']}
    seen = set()
    for row in primary['fixtures']:
        name = row['name']
        need(name in expected and name not in seen,'complete distinct supplied named domain')
        seen.add(name);own = expected[name]
        need(canonical([row['A'],row['B'],row['status']]) == canonical([own['A'],own['B'],own['status']]),'named raw matrix/status binding')
        if own['answer'] is None:
            need(row['answer'] is None,'no fabricated singular witness')
        else:
            validate_provided(row['A'],row['B'],row['answer'],own['answer']['e'])
    need(seen == expected.keys(),'all ten named witnesses checked')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    parser.add_argument('--stream-file',type=Path)
    args = parser.parse_args()
    need(args.stream_file is None or args.emit,'external stream allowed only during emit')
    stream = None
    if args.stream_file is not None:
        target = args.stream_file.resolve()
        need(target != HERE and HERE not in target.parents,'stream path must be external')
        stream = target.open('xb')
    try:
        result = compute(stream)
    finally:
        if stream is not None:
            stream.close()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode((HERE/'ORACLE.json').read_bytes())
        need(canonical(retained) == canonical(result),'strict independent receipt drift')
        compare_primary(result)
        print('PASS_F4_LITERAL_FIRST_SLICE_ORACLE')


if __name__ == '__main__':
    main()
