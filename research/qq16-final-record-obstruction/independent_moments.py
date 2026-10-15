#!/usr/bin/env python3
"""Independent QQ16 two-moment route oracle; no research module imports.

R is reconstructed by backward scalar covectors. Owner routes are reconstructed
as coordinate swaps in a complete orthonormal basis (rather than transvections).
The actual six pairs are checked as full 73-by-73 binary maps. This corroborates
credited moment results; it does not prove the new final-only observation map.

Credit: Ali Romman/#1969 supplies QQ16; Ross Richardson/#2104 supplies the
two-moment rank method; Nick Petalas/#2181 and commdata2338/#2189 extend it.
Philippe Van Velzen commit680d0997621a2cecfef2186ab143377658687825 checks
actual-route moments for all stage triples. This code is an independent
source-binding check, written with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import tarfile

ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
ARCHIVE_SHA256 = '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754'
MEMBERS = {
 'word': ('slots/local/CANONICAL-WORD.json.gz','16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'),
 'program': ('slots/local/LOCAL-PROGRAMS.json.gz','241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
 'phases': ('t16/global/base/work/complex-nine-native/DATA-PHASES.json','c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
}
A=(0,7,20,27,36,46,57,111)
T=(21,37,47,76,81,87,92,110)
U=tuple(p for p in range(112) if p not in A+T)
TRIPLES=((0,1,2),(2,3,4))
IDENTITY=tuple(1<<i for i in range(73))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value,separators=(',',':'),sort_keys=True).encode())


def load(root):
    raw=(root/ARCHIVE).read_bytes()
    require(sha(raw)==ARCHIVE_SHA256,'archive SHA256')
    values={}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
        for name,(path,pin) in MEMBERS.items():
            entries=[e for e in archive.getmembers() if e.name==path]
            require(len(entries)==1 and entries[0].isfile(),'unique regular member '+path)
            data=archive.extractfile(entries[0]).read()
            require(sha(data)==pin,'member SHA256 '+path)
            values[name]=json.loads(gzip.decompress(data) if path.endswith('.gz') else data)
    return values


def register(token):
    kind,index=token
    require(kind in ('L','C'),'register namespace')
    require(0<=index<(704 if kind=='L' else 8),'register index')
    return index+(704 if kind=='C' else 0)


def backward_columns(word,program):
    require((word['v'],word['R'],word['h'])==(112,480,9),'source dimensions')
    cut=program.index(['phase','centers'])
    rows=[]
    for centre in word['centers']:
        cov=[Fraction(0) for _ in range(712)]
        cov[centre]=Fraction(1)
        for event in reversed(program[:cut]):
            if event[0]!='scalar':
                continue
            op=event[1]
            dest=register(op[1])
            if op[0]=='clear':
                cov[dest]=Fraction(0)
            elif op[0]=='scale':
                cov[dest]*=Fraction(op[2],op[3])
            elif op[0]=='copy':
                src=register(op[2])
                require(src!=dest,'copy not self')
                cov[src]+=cov[dest]
                cov[dest]=Fraction(0)
            else:
                require(op[0]=='add','known scalar gate')
                cov[register(op[2])]+=Fraction(op[3],op[4])*cov[dest]
        require(all(x.denominator==1 for x in cov[:112]),'integer R')
        require(not any(cov[112:224]) and not any(cov[704:]),'query Y/private independence')
        rows.append([int(x) for x in cov[:112]])
    require(len(rows)==8,'eight query rows')
    return [tuple(row[p] for row in rows) for p in range(112)]


def gram(columns,ports):
    return [[sum(columns[p][i]*columns[p][j] for p in ports) for j in range(8)] for i in range(8)]


def diagonal(k):
    return [[k*int(i==j) for j in range(8)] for i in range(8)]


def check_geometry(columns, selected_a=A, selected_t=T):
    require(len(columns)==112 and all(len(c)==8 for c in columns),
            'exact query column dimensions')
    require(len(selected_a)==len(selected_t)==8 and
            len(set(selected_a+selected_t))==16 and
            all(type(p) is int and 0<=p<112 for p in selected_a+selected_t),
            'sixteen distinct selected ports')
    ordinary=tuple(p for p in range(112) if p not in selected_a+selected_t)
    require(all(sum(x*x for x in c)==4 and all(x in(-1,0,1) for x in c) for c in columns),'port squared norms')
    require(gram(columns,range(112))==diagonal(56),'full R Gram')
    require(gram(columns,selected_a)==gram(columns,selected_t)==diagonal(4),'selected minor Grams')
    require(gram(columns,ordinary)==diagonal(48),'ordinary query Gram')


def xor_images(columns,vector):
    result=0
    for i,column in enumerate(columns):
        if vector>>i&1:
            result^=column
    return result


def matrix_product(left,right):
    return tuple(xor_images(left,column) for column in right)


def actual_routes(word,phases):
    require(phases['m']==73 and len(phases['recipes'])==112,'phase dimensions')
    routes={stage:[] for stage in range(5)}
    for port,record in enumerate(phases['recipes']):
        require(record['port']==port and record['q']==word['ports'][port],'phase port binding')
        basis=tuple([record['q']]+record['idle_children'][0]['orthogonal_axes'][:8])+IDENTITY[9:]
        require(len(basis)==73 and all(((basis[i]&basis[j]).bit_count()%2)==int(i==j) for i in range(73) for j in range(73)),'full orthonormal route basis')
        for stage in range(5):
            permutation=list(range(73))
            if stage:
                for i in range(8):
                    first,second=1+i,9+8*(stage-1)+i
                    permutation[first],permutation[second]=permutation[second],permutation[first]
            columns=[]
            for unit in IDENTITY:
                value=0
                for i,axis in enumerate(basis):
                    if (unit&axis).bit_count()%2:
                        value^=basis[permutation[i]]
                columns.append(value)
            actual=tuple(columns)
            require(matrix_product(actual,actual)==IDENTITY,'owner involution')
            require(xor_images(actual,record['q'])==record['q'],'fixed port normal')
            if stage==0:
                require(actual==IDENTITY,'stage-zero identity')
            else:
                for i in range(8):
                    require(xor_images(actual,basis[1+i])==IDENTITY[9+8*(stage-1)+i],'actual q-perp to stage-axis swap')
            routes[stage].append(actual)
    return routes


def cross_square(columns,relative):
    # M_g is the complete 8x8 coefficient of owner route g in B_s B_t*.
    coeff={}
    for port,g in zip(U,relative):
        block=coeff.setdefault(g,[[0]*8 for _ in range(8)])
        for i in range(8):
            for j in range(8):
                block[i][j]+=columns[port][i]*columns[port][j]
    # Identity coefficient of C C*: sum_g M_g M_g^T, valid even on collisions.
    square=[[sum(sum(block[i][k]*block[j][k] for k in range(8)) for block in coeff.values()) for j in range(8)] for i in range(8)]
    return coeff,square


def check_cross(columns,relative):
    coeff,square=cross_square(columns,relative)
    require(len(coeff)==96,'distinct actual relative routes')
    require(square==diagonal(192),'cross identity matrix')
    return coeff,square


def verify(root):
    inputs=load(root)
    columns=backward_columns(inputs['word'],inputs['program']['forward'])
    check_geometry(columns)
    routes=actual_routes(inputs['word'],inputs['phases'])
    pairs=sorted({tuple(sorted((s,t))) for triple in TRIPLES for s in triple for t in triple if s!=t})
    checks=[]
    for s,t in pairs:
        relative=[matrix_product(routes[s][p],routes[t][p]) for p in U]
        coeff,square=check_cross(columns,relative)
        reverse=[matrix_product(routes[t][p],routes[s][p]) for p in U]
        _,reverse_square=cross_square(columns,reverse)
        require(reverse_square==square,'anti-homomorphism convention')
        checks.append({'stages':[s,t],'routes':len(coeff),'relative_route_sha256':digest(relative),'cross_identity_matrix':square,'cross_trace_per_owner':sum(square[i][i] for i in range(8))})
    m1=Fraction(3*8)
    m2=Fraction(3*8)+6*Fraction(1536,48**2)
    rank=m1*m1/m2
    defect=rank-16
    require((m1,m2,rank,defect)==(24,28,Fraction(144,7),Fraction(32,7)),'trace/rank arithmetic')
    controls=[]
    bad=[list(c) for c in columns]
    bad[U[0]][0]+=1
    try:
        check_geometry(bad)
    except ValueError:
        controls.append('changed R coefficient rejected')
    else:
        raise ValueError('R mutation passed')
    try:
        check_geometry(columns,(1,)+A[1:],T)
    except ValueError:
        controls.append('wrong selected port rejected')
    else:
        raise ValueError('selected-port mutation passed')
    relative=[matrix_product(routes[0][p],routes[1][p]) for p in U]
    relative[1]=relative[0]
    try:
        check_cross(columns,relative)
    except ValueError:
        controls.append('colliding route rejected')
    else:
        raise ValueError('route collision passed')
    collapsed=[IDENTITY for p in U]
    _,collapsed_square=cross_square(columns,collapsed)
    require(collapsed_square==diagonal(2304),
            'nonregular collapsed-owner action is a distinct trace model')
    try:
        check_cross(columns,collapsed)
    except ValueError:
        controls.append('collapsed-owner action rejected; regular-action trace domain required')
    else:
        raise ValueError('collapsed owner action passed')
    return {'status':'PASS_INDEPENDENT_QQ16_FINAL_ONLY_MOMENTS','archive_sha256':ARCHIVE_SHA256,'archive_members':{name:{'path':path,'sha256':pin} for name,(path,pin) in MEMBERS.items()},'trace_domain':'finite regular owner representation on payload-constant fields; not an arbitrary quotient or nonfree owner action','R_columns_sha256':digest(columns),'centre_sha256':digest([[str(columns[p][i]) for p in range(112)] for i in range(8)]),'ordinary_gram':48,'triples':[list(t) for t in TRIPLES],'pairs':checks,'normalized_moment1_per_owner':str(m1),'normalized_moment2_per_owner':str(m2),'stack_rank_lower_per_owner':str(rank),'conditional_image_lower_per_owner':str(defect),'controls':controls,'scope':'Independent source-bound corroboration of credited moments, not a new moment theorem or verification of final-only controller trajectory.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    print(json.dumps(verify(args.repo),indent=2,sort_keys=True))
