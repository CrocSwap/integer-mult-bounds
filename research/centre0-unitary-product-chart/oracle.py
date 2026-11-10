"""Independent rational-projector and quadratic-field centre0 chart checks.

No predecessor or primary program is imported/executed. Nick Petalas6667
retains the actual weighted-swap construction; Brian5130/Chris R5101 and
their retained native lineage retain source credit. ToikY with substantial
OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN = '261b229749a45c19cb8eb88752018957cd36d4660e4c2dba10733433f7932055'
DISC = 6097
ZERO = (F(0),F(0))
ONE = (F(1),F(0))
H = (F(937),F(-12))
LAMBDA = (F(937),F(12))


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def decode(raw):
    def unique(items):
        out = {}
        for key,value in items:
            need(key not in out,'duplicate JSON key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('noninteger/nonfinite JSON '+value)
    return json.loads(raw,object_pairs_hook=unique,parse_float=bad,parse_constant=bad)


def digest(value):
    return hashlib.sha256((canonical(value)+'\n').encode()).hexdigest()


def authenticate():
    raw = (HERE/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN,'source manifest')
    pins = decode(raw)
    need(type(pins['schema_version']) is int and pins['schema_version'] == 1,'source schema')
    need(len(pins['files']) == 5,'five source objects')
    seen = set()
    for row in pins['files']:
        path = row['local_path']
        need(path.startswith('inputs/') and '..' not in path and path not in seen,'source path')
        seen.add(path)
        body = (HERE/path).read_bytes()
        need(type(row['bytes']) is int and len(body) == row['bytes'],'source length')
        need(hashlib.sha256(body).hexdigest() == row['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest() == row['git_blob'],'source Git blob')


def q(value):
    if type(value) in (int,str,F):
        return F(value),F(0)
    need(type(value) in (list,tuple) and len(value) == 2,'quadratic pair')
    need(all(type(x) in (int,str,F) for x in value),'quadratic rational coefficients')
    return F(value[0]),F(value[1])


def add(a,b):
    return a[0]+b[0],a[1]+b[1]


def neg(a):
    return -a[0],-a[1]


def sub(a,b):
    return add(a,neg(b))


def mul(a,b):
    return a[0]*b[0]+DISC*a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def scale(a,b):
    return a[0]*b,a[1]*b


def inv(a):
    denominator = a[0]*a[0]-DISC*a[1]*a[1]
    need(denominator != 0,'zero quadratic inverse')
    return a[0]/denominator,-a[1]/denominator


def positive(a):
    x,y = a
    if y == 0:
        return x>0
    if x>=0 and y>0:
        return True
    if x<=0 and y<0:
        return False
    return x*x>DISC*y*y if x>0 else DISC*y*y>x*x


def sq(a):
    return [str(a[0]),str(a[1])]


def dot(a,b):
    return sum((x*y for x,y in zip(a,b) if x and y),F(0))


def dotq(a,b):
    aa,ab = [x[0] for x in a],[x[1] for x in a]
    ba,bb = [x[0] for x in b],[x[1] for x in b]
    return dot(aa,ba)+DISC*dot(ab,bb),dot(aa,bb)+dot(ab,ba)


def rational_dot_q(a,b):
    return dot(a,[x[0] for x in b]),dot(a,[x[1] for x in b])


def source():
    R = [[F(x) for x in row] for row in decode((HERE/'inputs/R.json').read_bytes())]
    data = decode((HERE/'inputs/CORRECTED-DERIVATION.json').read_bytes())
    J = data['selected_ports_J']
    need(J == [0,7,20,23,86,93,108,111],'actual selected coordinates')
    need(len(R) == 8 and all(len(row) == 112 for row in R),'actual source dimensions')
    U = [[x/F(4)*(F(-11) if j in J else F(1)) for j,x in enumerate(row)] for row in R]
    for i in range(8):
        for j in range(8):
            need(dot(R[i],R[j]) == 56*int(i == j),'actual RRt')
            need(dot(U[i],U[j]) == F(67,2)*int(i == j),'actual UtU')
            need(dot(R[i],U[j]) == 2*int(i == j),'actual RU')
    G = [[F(i == j)-sum((U[k][i]*R[k][j] for k in range(1,8)),F(0))
          for j in range(112)] for i in range(112)]
    actual = [[F(x) for x in row] for row in data['F_actual']]
    need(G == actual,'all112x112 literal source entries')
    need(G[0][1] == F(11,2) and G[1][0] == F(-1,2),'actual transpose asymmetry')
    return R[1:],U[1:],G


def action(vector,R,U,transpose=False):
    readers,writers = (U,R) if transpose else (R,U)
    coefficients = [rational_dot_q(row,vector) for row in readers]
    out = []
    for j,value in enumerate(vector):
        delta = ZERO
        for row,c in zip(writers,coefficients):
            if row[j]:
                delta = add(delta,scale(c,row[j]))
        out.append(sub(value,delta))
    return out


def active_columns(R,U):
    t = scale(neg(add(ONE,H)),F(1,56))
    need(mul(H,LAMBDA) == ONE and positive(H) and positive(sub(ONE,H)),'positive reciprocal roots')
    need(add(add(mul(H,H),scale(H,F(-1874))),ONE) == ZERO,'source quadratic equation')
    columns,norms,rows = [],[],[]
    for i in range(7):
        v = [add(q(a),scale(t,b)) for a,b in zip(U[i],R[i])]
        w = [add(scale(H,a),scale(t,b)) for a,b in zip(U[i],R[i])]
        gv,gw,cross = dotq(v,v),dotq(w,w),dotq(v,w)
        need(cross == ZERO and gw == mul(H,gv) and positive(gv) and positive(gw),'actual orthogonal unequal norms')
        need(action(v,R,U) == w and action(w,R,U) == v,'actual G active columns')
        need(action(v,R,U,True) == [mul(LAMBDA,x) for x in w],'actual Gt v')
        need(action(w,R,U,True) == [mul(H,x) for x in v],'actual Gt w')
        columns.extend([v,w]);norms.extend([gv,gw])
        rows.append({'index':i+1,'v':[sq(x) for x in v],'w':[sq(x) for x in w],
                     'norm_v':sq(gv),'norm_w':sq(gw),'balanced_pair_norm':sq(gv)})
    for i,a in enumerate(columns):
        for j,b in enumerate(columns):
            need(dotq(a,b) == (norms[i] if i == j else ZERO),'all14x14 actual Gram entries')
    return columns,norms,rows


def projectors(R,U):
    inverse = ((F(56,1872),F(-2,1872)),(F(-2,1872),F(67,3744)))
    gram = ((F(67,2),F(2)),(F(2),F(56)))
    need([[sum(inverse[i][k]*gram[k][j] for k in range(2)) for j in range(2)] for i in range(2)] == [[1,0],[0,1]],'plane Gram inverse')
    P = [[sum((F(56)*u[i]*u[j]-2*u[i]*r[j]-2*r[i]*u[j]+F(67,2)*r[i]*r[j]
               for r,u in zip(R,U)),F(0))/1872 for j in range(112)] for i in range(112)]
    need(all(P[i][j] == P[j][i] for i in range(112) for j in range(112)),'symmetric actual projector')
    trace = sum(P[i][i] for i in range(112))
    need(trace == 14,'active projection rank trace')
    for vector in R+U:
        need([dot(row,vector) for row in P] == vector,'every active source projector image')
    Z = [[F(i == j)-P[i][j] for j in range(112)] for i in range(112)]
    for vector in R+U:
        need(all(dot(vector,[Z[i][j] for i in range(112)]) == 0 for j in range(112)),
             'all complement annihilator coefficients')
    return {'active_rank':14,'complement_rank':98,'active_trace':str(trace),
            'matrix_entries':112*112,'fixed_source_columns':14,
            'complement_annihilator_entries':14*112,
            'projection_sha256':digest([[str(x) for x in row] for row in P]),
            'complement_projection_sha256':digest([[str(x) for x in row] for row in Z]),
            'idempotence_basis':'inverseGram and mutually orthogonal planes, all source images checked'}


def permutation(n):
    return [i^1 if i<14 else i for i in range(n)]


def product_check(n,mode='correct'):
    P = permutation(n)
    stream = hashlib.sha256()
    for j in range(n):
        for k in range(n):
            observed = None
            if P[j] == P[k]:
                row = P[j]
                first = (1 if row%2 == 0 else -1) if row<14 else 0
                second = -first if mode != 'transpose' else first
                sign = -1 if mode == 'sign' and row == 1 else 1
                observed = [row,sign,first+second]
            target = [P[j],1,0] if j == k else None
            if mode == 'output-B' and target is not None and P[j]<14:
                target[2] = -1 if P[j]%2 == 0 else 1
            need(observed == target,'actual normalized Hadamard basis product')
            stream.update((canonical([j,k,observed])+'\n').encode())
    return {'dimension':n,'ordered_basis_pairs':n*n,'literal_pair_stream_sha256':stream.hexdigest()}


def fourier_indices(n):
    # At power-of-two padding Phi_(2N)=X^N+1. Each difference class covers
    # all Gram positions of that class; no enormous cyclotomic matrix is built.
    need(n in (128,256),'fixed Fourier corroboration domain')
    for difference in range(1-n,n):
        coefficients = [0]*n
        for row in range(n):
            exponent = ((2*row+1)*difference)%(2*n)
            coefficients[exponent%n] += 1 if exponent<n else -1
        expected = [n]+[0]*(n-1) if difference == 0 else [0]*n
        need(coefficients == expected,'all exact Fourier Gram difference classes')
    for i in range(n):
        for j in range(n):
            total = i+j
            sign,coordinate = (-1,total-n) if total>=n else (1,total)
            need(total%(2*n) == coordinate+(n if sign<0 else 0),'all negacyclic basis wrap signs')
    return {'padding':n,'Gram_positions':n*n,'difference_classes':2*n-1,
            'negacyclic_basis_pairs':n*n,'normalization':'E*E=N I; E/sqrtN unitary'}


def reject(callback):
    try:
        callback()
    except ValueError as error:
        return str(error)
    raise ValueError('counterfactual accepted')


def controls(columns,norms,R,U):
    wrong_output = reject(lambda:product_check(112,'output-B'))
    wrong_transpose = reject(lambda:product_check(112,'transpose'))
    wrong_sign = reject(lambda:product_check(112,'sign'))
    wrong_ratio = sub(mul(norms[1],inv(norms[0])),ONE)
    need(wrong_ratio != ZERO,'missing pair correction must be observable')
    wrong = [add(q(a),scale(neg(scale(neg(add(ONE,H)),F(1,56))),b)) for a,b in zip(U[0],R[0])]
    need(action(wrong,R,U) != columns[1],'actual bad source-column sign')
    return {'wrong_output':wrong_output,'wrong_transpose':wrong_transpose,'one_sided_sign':wrong_sign,
            'missing_normalization_actual_norm_minus_one':sq(wrong_ratio),
            'wrong_fixed_output_coefficient_square':sq(LAMBDA),
            'wrong_source_column_sign_detected':True,
            'duplicate_json':reject(lambda:decode('{"x":1,"x":2}')),
            'nonfinite_json':reject(lambda:decode('{"x":NaN}'))}


def compute():
    authenticate()
    R,U,G = source()
    columns,norms,active = active_columns(R,U)
    return {'schema_version':1,'source_manifest_sha256':PIN,
            'method':'Independent rational orthogonal projections and exact Qsqrt6097 source actions; no primary basis algorithm',
            'source_G_sha256':digest([[str(x) for x in row] for row in G]),
            'active_planes':active,'projector_certificate':projectors(R,U),
            'full_Hadamard_products':[product_check(n) for n in (112,128,256)],
            'Fourier_index_corrob':[fourier_indices(n) for n in (128,256)],
            'scalar_certificates':{'h':sq(H),'lambda':sq(LAMBDA),'h_lambda':sq(mul(H,LAMBDA)),
                                   'fixed_output_norm':sq(LAMBDA),'fixed_output_condition':sq(mul(LAMBDA,LAMBDA)),
                                   'chart_min_condition_squared':sq(LAMBDA),
                                   'changed_output_norm_squared':sq(ONE)},
            'controls':controls(columns,norms,R,U),
            'scope':'Exact actual-source algebraic Gram/action/product evidence; Fourier all-size and sharp norm statements need the written proof. No physical/native/supplier or kappa admission.'}


def check_primary(result):
    primary = decode((HERE/'RESULT.json').read_bytes())
    need(type(primary['schema_version']) is int and primary['schema_version'] == 1,'primary schema')
    need(primary['source_manifest_sha256'] == PIN,'primary source binding')
    own = result['active_planes']
    supplied = primary['active_planes']
    need(len(supplied) == 7,'all seven supplied planes')
    columns,declared = [],[]
    for wanted,row in zip(own,supplied):
        for key,norm in (('v','norm_v'),('w','norm_w')):
            v = [q(x) for x in row[key]]
            need(len(v) == 112 and v == [q(x) for x in wanted[key]],'all actual supplied active coordinates')
            columns.append(v);declared.append(q(row[key+'_norm']))
    complement = primary['complement_basis']
    need(len(complement) == 98,'complete complementary basis')
    for row in complement:
        v = [q(x) for x in row['vector']]
        need(len(v) == 112 and all(x[1] == 0 for x in v),'rational actual complementary column')
        columns.append(v);declared.append(q(row['norm']))
    R,U,_ = source()
    for i,a in enumerate(columns):
        need(positive(declared[i]),'positive supplied normalization')
        for j in range(i,len(columns)):
            need(dotq(a,columns[j]) == (declared[i] if i == j else ZERO),'every supplied actual Gram entry')
        if i>=14:
            need(action(a,R,U) == a and action(a,R,U,True) == a,'all actual complement action entries')
    need(primary['source_G_sha256'] == result['source_G_sha256'],'all literal source entries digest')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit',action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(canonical(result))
    else:
        retained = decode((HERE/'ORACLE.json').read_bytes())
        need(canonical(retained) == canonical(result),'strict oracle receipt drift')
        check_primary(result)
        print('PASS_CENTRE0_UNITARY_PROJECTOR_ORACLE')


if __name__ == '__main__':
    main()
