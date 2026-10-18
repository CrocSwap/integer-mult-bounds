"""Exact source-bound primary replay; read-only except exclusive --write."""
import argparse
from array import array
import hashlib
import json
from itertools import product
from math import gcd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import model

HERE = Path(__file__).resolve().parent


def encode(z, m):
    i = 0
    for v in z:
        i = i*m + v
    return i


def checked_equal(a, b, label):
    model.need(type(a) is type(b) and a == b, label)


def rebuild():
    old = model.source()
    cases = [0, 0, 0]
    columns = 0
    for m in range(3, 102, 2):
        for k in range(-m, m+1):
            word, summands = model.lower(k, m, old)
            cost = model.classify(k, m)
            checked_equal(sum(e[0] == 'child' for e in word), cost, 'child tariff')
            checked_equal(sum(e[0] == 'affine' for e in word), 6*cost, 'literal affine invoice')
            model.need(all(gcd(u,m)==1 for u in summands), 'admitted summands')
            compiled = model.modular(word,m)
            inverse = model.modular(old.inverse_word(word),m)
            for i in range(8):
                z = tuple(int(i==j) for j in range(8))
                q = model.run(z, compiled,m)
                checked_equal(q,model.direct(z,k,m),'complete active and spectator column')
                checked_equal(model.run(q,inverse,m),z,'inverse column')
                columns += 1
            cases[cost] += 1

    triadic = 0
    for m in (3,5,9,15,21,25,27,35,45,81,99):
        for j in (0,1,2,7,54):
            for sign in (-1,1):
                k=sign*3*(1<<j)
                word,parts=model.lower(k,m,old,triadic=(j,sign))
                compiled=model.modular(word,m)
                if model.classify(k,m)==2:
                    checked_equal(parts,(sign*(1<<j),sign*(1<<(j+1))),'fixed dyadic split')
                for i in range(6):
                    z=tuple(int(i==t) for t in range(6))
                    checked_equal(model.run(z,compiled,m),model.direct(z,k,m),'triadic coefficient')
                inv=model.invoice(j,sign,m,old)
                expect=(0,0,0) if m==3 else (6,36,2) if m%3==0 else (3,18,2)
                checked_equal(tuple(inv[t] for t in ('children','affine','xor')),expect,'fused invoice')
                triadic += 1

    # All physical ADDRESS columns in the excluded nontrivial ring Z/9.
    # Store push permutations, not a logical scalar projection.
    m=9
    permutations={}
    hashes={}
    for k in (-6,-3,3,6):
        j=0 if abs(k)==3 else 1
        word=model.modular(model.lower(k,m,old,triadic=(j,1 if k>0 else -1))[0],m)
        p=array('I')
        for z in product(range(m),repeat=6):
            actual=model.run(z,word,m)
            checked_equal(actual,model.direct(z,k,m),'full nonunit address domain')
            p.append(encode(actual,m))
        permutations[k]=p
        hashes[str(k)]=hashlib.sha256(json.dumps(list(p),separators=(',',':')).encode()).hexdigest()
    n=m**6
    a,b,c,d=(permutations[k] for k in (-3,6,3,-6))
    for i in range(n):
        checked_equal(a[b[a[i]]],i,'dirty target return')
        checked_equal(c[d[c[i]]],i,'inverse target return')
        checked_equal(a[b[i]],c[i],'source positive contribution')
        checked_equal(c[d[i]],a[i],'inverse source negative contribution')
        checked_equal(c[a[i]],i,'complete inverse query')
    # These equalities prove every source, target and spectator BIT column.
    # Additionally execute the literal full DATA program on dirty rows.
    rows=[{0,1,17,n-1},{3,9,81,720,n-2},{2,4,n//2}]
    before=[set(x) for x in rows]
    p=old.fused_program()
    old.run_bits(rows,p,permutations)
    expected=before[0]^{c[i] for i in before[1]}^{a[i] for i in before[1]}
    checked_equal(rows,[expected,before[1],before[2]],'literal dirty DATA endpoint')
    old.run_bits(rows,old.inverse_program(p),permutations)
    checked_equal(rows,before,'literal dirty DATA inverse')

    controls=[]
    def rejects(label,f):
        try:
            f()
        except (ValueError,TypeError):
            controls.append(label)
        else:
            raise ValueError('ineffective control: '+label)
    rejects('original_nonunit_word',lambda:model.modular(old.address_word(3),9))
    rejects('even_ring',lambda:model.classify(3,8))
    rejects('bool_power',lambda:model.classify(True,9))
    rejects('wrong_triadic_binding',lambda:model.lower(3,9,old,triadic=(1,1)))
    wrong=list(old.address_word(1)); e=list(wrong[0]); e[2]=3; wrong[0]=tuple(e)
    rejects('nonunit_diagonal',lambda:model.modular(wrong,9))
    wrong=list(old.address_word(1)); e=list(wrong[0]); e[3]=((5,e[3][0][1]),); wrong[0]=tuple(e)
    rejects('unordered_free_control',lambda:model.modular(wrong,9))
    z=(0,0,0,0,0,1)
    true=model.direct(z,3,9)
    for label,word in (
        ('missing_second_child',old.address_word(1)+tuple(e for e in old.address_word(2) if e[0]!='child')),
        ('wrong_second_sign',old.address_word(1)+old.address_word(-2))):
        model.need(model.run(z,model.modular(word,9),9)!=true,label)
        controls.append(label)
    model.need(gcd(true[0],9)!=1 and true[0]!=0,'one child nonunit obstruction')
    controls.append('one_child_price_rejected')
    # With reverse-ordered free row additions the endpoint itself is free:
    # allowing that enlarged alphabet invalidates the theorem, explicitly.
    model.need(model.direct(z,3,9)[0]!=0,'enlarged alphabet witness')
    controls.append('enlarged_free_alphabet_outside_contract')
    return {'classification_cases':cases,'matrix_columns':columns,'triadic_cases':triadic,
            'full_address_columns':4*n,'dirty_data_columns':3*n,'permutation_sha256':hashes,
            'literal_dirty_forward_inverse':True,'controls':controls,
            'scope':'local0/1/2 child optimum; literal fused6/36/2 on odd multiples of3 greater than3; no global optimum'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    path=HERE/'RESULT.json'
    if args.write:
        model.need(not path.exists(), 'refusing receipt overwrite')
    result=rebuild()
    if args.write:
        with path.open('x',encoding='utf-8') as f:
            json.dump(result,f,indent=2,sort_keys=True); f.write('\n')
    else:
        expected=json.loads(path.read_text(encoding='utf-8'))
        model.need(json.dumps(result,sort_keys=True)==json.dumps(expected,sort_keys=True),'receipt mismatch')
    print('PASS_TRIADIC_NONUNIT_LOWERING cases='+str(sum(result['classification_cases']))+
          ' address_columns='+str(result['full_address_columns'])+' controls='+str(len(result['controls'])))


if __name__=='__main__':
    main()
