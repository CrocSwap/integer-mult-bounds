#!/usr/bin/env python3
"""Independent exact selected scalar-prefix and small interface controls.

No contributor implementation is imported. This checks a finite source
predicate; REVIEW.md contains the universal argument and its boundary.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def scalar_prefix(path):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == '2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883', 'exact selected word')
    word = json.loads(gzip.decompress(raw))
    scale = 1125
    rows = {i: {i: F(scale)} for i in range(word['public'])}
    charts = dict(enumerate(word['initial']))
    seen = 0
    max_height = 0
    max_mass = F(scale)
    max_numerator_bits = scale.bit_length()
    def inspect(row):
        nonlocal seen, max_height, max_mass
        mass = F(0)
        for value in row.values():
            denominator = value.denominator
            need(denominator & (denominator-1) == 0, 'scaled stored/pre-product coefficient not dyadic')
            max_height = max(max_height, denominator.bit_length()-1)
            mass += abs(value)
            seen += 1
        max_mass = max(max_mass, mass)
    for e in word['program']:
        op, r = e[:2]
        if op == 'INIT':
            need(r not in rows and r >= word['public'], 'fresh owned label')
            rows[r] = {}; charts[r] = e[2]
        elif op == 'CLEAR':
            need(r >= word['public'] and charts[r] == e[2], 'owned clear chart')
            del rows[r]; del charts[r]
        elif op == 'MOVE':
            need(charts[r] == e[2], 'MOVE source chart')
            charts[r] = e[3]
        elif op in ('SCALE', 'ADD', 'COPY'):
            if op == 'SCALE':
                q = F(e[2]); source = rows[r]
                need(charts[r] == e[3], 'SCALE chart')
            else:
                s, q = e[2], F(e[3]); source = rows[s]
                need(r != s and charts[r] == charts[s] == e[4], 'common scalar chart')
                if op == 'COPY':
                    need(r >= word['public'] and not rows[r], 'COPY initialized private zero')
            max_numerator_bits = max(max_numerator_bits, abs(q.numerator).bit_length())
            product = {i:q*v for i,v in source.items() if q*v}
            inspect(product)
            if op in ('SCALE','COPY'):
                rows[r] = product
            else:
                for i, v in product.items():
                    total = rows[r].get(i,F(0)) + v
                    if total: rows[r][i] = total
                    else: rows[r].pop(i,None)
            inspect(rows[r])
        else:
            raise ValueError('unexpected opcode '+op)
    need(set(rows) == set(range(word['public'])), 'complete owner return')
    need([charts[i] for i in range(word['public'])] == word['final'], 'complete chart return')
    for row in rows.values():
        for value in row.values():
            denominator = (value/scale).denominator
            need(denominator & (denominator-1) == 0, 'unscaled completed endpoint has odd denominator')
    need(max_height == 24 and max_mass < 2**37 and max_numerator_bits == 24, 'selected scalar prefix bounds')
    return dict(events=len(word['program']), public=word['public'], coefficient_visits=seen,
                scaled_height=max_height, scaled_mass=str(max_mass), numerator_bits=max_numerator_bits,
                all_stored_and_separate_preproducts_dyadic=True, all_completed_rows_unscale_to_dyadic=True)


def caller_majorant(path):
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == '3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e', 'exact selected caller')
    caller = json.loads(raw)
    mass = [F(1)]*caller['roles']; height = [0]*caller['roles']
    max_mass = pre_mass = F(1); max_height = pre_height = 0
    def debt(q):
        d = q.denominator
        need(d & (d-1) == 0, 'caller coefficient dyadic')
        return d.bit_length()-1
    for e in caller['events']:
        if e[0] == 'J':
            _, stage, aa, bb = e
            # Only actual joint entrances are needed. Bounding all other live
            # roles as entrances, as the retained proof does, is also safe.
            for i in aa + bb[:2]:
                pre_mass=max(pre_mass,mass[i]); pre_height=max(pre_height,height[i])
            r,s,u,v=aa
            mass[s]+=mass[r]; height[s]=max(height[s],height[r])
            mass[u]+=mass[v]; height[u]=max(height[u],height[v])
            r,s,alpha,beta=bb; alpha,beta=F(alpha),F(beta)
            old_m,old_h=mass[:],height[:]
            mass[r]=old_m[r]+abs(alpha)*old_m[s]
            mass[s]=abs(beta)*old_m[r]+abs(1+alpha*beta)*old_m[s]
            height[r]=max(old_h[r],old_h[s]+debt(alpha))
            height[s]=max(old_h[r]+debt(beta),old_h[s]+debt(1+alpha*beta))
        else:
            _,op,*args=e
            if op in ('ADD','QUERY'):
                r,s,c=args; c=F(c)
                mass[r]+=abs(c)*mass[s]; height[r]=max(height[r],height[s]+debt(c))
            elif op=='SCALE':
                r,c=args; c=F(c); mass[r]*=abs(c); height[r]+=debt(c)
            elif op=='SWAP':
                r,s=args
                mass[r],mass[s]=mass[s],mass[r]; height[r],height[s]=height[s],height[r]
            elif op=='LAMBDA':
                r,sign=args; need(sign in (-1,1), 'LAMBDA orientation')
                mass[r]*=2; height[r]+=1
            elif op=='IDLE_ONE':
                pass
            else:
                raise ValueError('unexpected caller opcode '+op)
        max_mass=max(max_mass,max(mass)); max_height=max(max_height,max(height))
    need(max_mass == F('16246698892210214036146399419475929893435/256'), 'literal caller mass agrees')
    need(max_height==163 and pre_height<=154 and max_mass<2**126 and pre_mass<2**124, 'retained caller envelope')
    H = 14174600000000000000
    K = 1920 * 153**1920 * (H+1)**2
    need((4096*K).bit_length() < H, 'selected unfinished-context threshold')
    return dict(events=len(caller['events']), caller_mass=str(max_mass), caller_height=max_height,
                actual_joint_entrance_mass=str(pre_mass), actual_joint_entrance_height=pre_height,
                retained_safe_entrance_height=154, retained_A=178, retained_B=161, retained_c=356,
                context_4096K_bitlength=(4096*K).bit_length(), selected_H=H)


# Gaussian rationals are pairs; matrix calculations below are independent.
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
I = (F(0), F(1))
def add(z,w): return z[0]+w[0], z[1]+w[1]
def mul(z,w): return z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0]
def smul(z,A): return [[mul(z,x) for x in row] for row in A]
def madd(A,B): return [[add(x,y) for x,y in zip(a,b)] for a,b in zip(A,B)]
def dot(a,b):
    out = ZERO
    for x,y in zip(a,b): out = add(out,mul(x,y))
    return out
def mmul(A,B): return [[dot(row,col) for col in zip(*B)] for row in A]
def kron(A,B): return [[mul(A[i][j], B[k][l]) for j in range(len(A[0])) for l in range(len(B[0]))] for i in range(len(A)) for k in range(len(B))]
def identity(n): return [[ONE if i==j else ZERO for j in range(n)] for i in range(n)]


def controls():
    alpha = (F(1,2),F(1,2)); beta = (F(1,2),F(-1,2))
    C = [[alpha,beta],[beta,alpha]]
    X = [[ZERO,ONE],[ONE,ZERO]]
    S = [[ONE,ZERO],[ZERO,I]]
    H0 = [[(F(1,2),F(0))]*2,[(F(1,2),F(0)),(F(-1,2),F(0))]]
    need(mmul(C,C) == X, 'C squared is exact translation')
    need(mmul(X,X) == identity(2), 'C order four')
    need(smul(beta,mmul(S,mmul(C,S))) == H0, 'normalized Walsh endpoint')
    # f=2 whole-array Lambda versus tensoring its one-column SUM.
    Q = kron(C,C)
    whole = madd(smul(alpha,identity(4)),smul(beta,mmul(Q,Q)))
    one = madd(smul(alpha,identity(2)),smul(beta,X))
    wrong_lambda = kron(one,one)
    need(whole != wrong_lambda and whole[1][0] == ZERO and wrong_lambda[1][0] == (F(1,2),F(0)), 'global Lambda sum must not be tensorized')
    need(F(1,3) != F(1,3)**2, 'whole scalar must not be tensorized')
    need(mul(I,I) != I, 'constant phase must be multiplied by f')
    # Completed dyadic endpoint alone does not certify every earlier division.
    need(F(1,3)*3 == 1 and F(1,3).denominator == 3, 'endpoint-only divisibility countercontrol')
    return dict(C_squared_translation=True,C_order_four=True,normalized_Walsh_identity=True,
                rejected_tensor_of_Lambda_sum=True,rejected_tensor_of_exterior_scalar=True,
                rejected_once_only_constant_phase=True,rejected_endpoint_only_divisibility=True,
                Lambda_wrong_cross_term='1/2', Lambda_correct_cross_term='0')


def main():
    p = argparse.ArgumentParser(); p.add_argument('--word',type=Path,required=True)
    p.add_argument('--caller',type=Path,required=True)
    args = p.parse_args()
    print(json.dumps(dict(status='PASS_SELECTED_COMPLEX_INTERFACE', scalar_prefix=scalar_prefix(args.word), caller_majorant=caller_majorant(args.caller), controls=controls()),indent=2))


if __name__ == '__main__': main()
