"""Symbolic identities and explicit integer-shear CRT construction.

apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
No external dependencies, subprocesses, caches, output files or assertions.
"""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def trim(p):
    p = list(map(F, p))
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return tuple(p)


def add(a, b):
    out = [F(0)] * max(len(a), len(b))
    for i, x in enumerate(a): out[i] += x
    for i, x in enumerate(b): out[i] += x
    return trim(out)


def scale(a, k):
    return trim([k*x for x in a])


def sub(a, b):
    return add(a, scale(b, -1))


def mul(*polys):
    result = (F(1),)
    for p in polys:
        out = [F(0)] * (len(result)+len(p)-1)
        for i, x in enumerate(result):
            for j, y in enumerate(p): out[i+j] += x*y
        result = trim(out)
    return result


def cube_poly(a, b):
    return (mul(a,a,a), scale(mul(a,a,b),3), scale(mul(a,b,b),3), mul(b,b,b))


def tensor_poly(weights, forms):
    total = [(F(0),)] * 4
    for w, (a, b) in zip(weights, forms):
        total = [add(x,mul(w,y)) for x,y in zip(total,cube_poly(a,b))]
    return total


def symbolic_identities(first_factor=32, second_sign=-1):
    """Check Q[r] coefficient identities after clearing only nonzero factors."""
    r, one, zero = (0,1), (1,), (0,)
    s = scale(mul(r,sub(r,one)),F(1,2))
    n = sub(scale(r,2),one)
    target = [zero,scale(s,3),mul(s,n),mul(s,s)]
    u,v = sub(scale(r,3),one),sub(scale(r,3),(5,))
    denominator = scale(mul(u,v),6)
    # This is D*w_j, with D=6(3r-1)(3r-5); node c=(3r-1)/4.
    numerators = [scale(mul(r,sub(r,one),add(r,(13,)),v),-1),
                  mul(r,sub(mul(r,r),one),u),
                  scale(mul(r,sub(r,one),sub(r,(2,))),first_factor)]
    actual1 = tensor_poly(numerators,[(one,zero),(one,one),(one,scale(u,F(1,4)))])
    expected1 = [mul(denominator,t) for t in target]
    weights2 = [scale(s,F(1,9)),scale(s,F(-1,9)),
                scale(mul(s,add(scale(s,3),(second_sign,))),F(1,9))]
    actual2 = tensor_poly(weights2,[((3,),r),((3,),sub(r,one)),(zero,one)])
    return actual1 == expected1 and actual2 == list(map(trim,target))


def cube(a,b):
    return (a**3,3*a*a*b,3*a*b*b,b**3)


def domain(r,m):
    require(type(r) is int and r>=3, 'arity must be an integer >=3')
    require(type(m) is int and m>1 and m%2==1, 'modulus must be an odd integer >1')


def local_data(r):
    s = r*(r-1)//2
    weights3 = [F(-r*(r-1)*(r+13),6*(3*r-1)),
                F(r*(r*r-1),6*(3*r-5)),
                F(16*r*(r-1)*(r-2),3*(3*r-1)*(3*r-5))]
    weights_away = [F(s,9),F(-s,9),F(s*(3*s-1),9)]
    # Five chronological shear slots, acting on a,b,a,b,a respectively.
    words3 = [(c,0,0,0,0) for c in (F(0),F(1),F(3*r-1,4))]
    words_away = [(F(t,3),-3,F(-2,3),1,2) for t in (r,r-1)]
    words_away.append((1,-1,1,0,0))
    return weights3,weights_away,words3,words_away


def residue(value,m):
    if m==1: return 0
    value = F(value)
    require(gcd(value.denominator,m)==1, 'denominator is not a residue unit')
    return value.numerator*pow(value.denominator,-1,m)%m


def crt(x,y,a,b):
    if a==1: return y%b
    if b==1: return x%a
    return (x+a*((y-x)*pow(a,-1,b)%b))%(a*b)


def construct(r,m):
    domain(r,m)
    a,b = 1,m
    while b%3==0: a,b = a*3,b//3
    weights3,weights_away,words3,words_away = local_data(r)
    def combine(x,y): return crt(residue(x,a),residue(y,b),a,b)
    weights = [combine(x,y) for x,y in zip(weights3,weights_away)]
    words = [[combine(x,y) for x,y in zip(xs,ys)] for xs,ys in zip(words3,words_away)]
    return weights,words


def frame(word):
    rows = [[1,0],[0,1]]
    for i,k in zip((0,1,0,1,0),word):
        rows[i] = [x+k*y for x,y in zip(rows[i],rows[1-i])]
    require(rows[0][0]*rows[1][1]-rows[0][1]*rows[1][0]==1,'noninvertible frame')
    return rows


def replay(r,weights,words,restore=True):
    rows, output = [[1,0],[0,1]],[0]*4
    for _ in range(r):
        output = [x+y for x,y in zip(output,cube(*rows[0]))]
        rows[0] = [x+y for x,y in zip(rows[0],rows[1])]
    rows[0] = [x-r*y for x,y in zip(rows[0],rows[1])]
    for q,word in zip(weights,words):
        for i,k in zip((0,1,0,1,0),word):
            rows[i] = [x+k*y for x,y in zip(rows[i],rows[1-i])]
        output = [x-q*y for x,y in zip(output,cube(*rows[0]))]
        if restore:
            for i,k in reversed(list(zip((0,1,0,1,0),word))):
                rows[i] = [x-k*y for x,y in zip(rows[i],rows[1-i])]
    return output,rows


def certificate_ok(r,m,weights,words,restore=True):
    output,rows = replay(r,weights,words,restore)
    return rows==[[1,0],[0,1]] and all((x-y)%m==0 for x,y in zip(output,(r,0,0,0)))


def source_binding():
    pins = json.loads((HERE/'SOURCES.json').read_text())['files']
    checked = 0
    for row in pins:
        if row['usage']!='input': continue
        data = (ROOT/row['path']).read_bytes()
        require(sha256(data).hexdigest()==row['sha256'],'source hash mismatch')
        require(sha256(data+b'\n').hexdigest()!=row['sha256'],'source mutation accepted')
        checked += 1
    return checked


def main():
    inputs = source_binding()
    require(symbolic_identities(),'universal rational identity')
    require(not symbolic_identities(first_factor=31),'wrong third weight accepted')
    require(not symbolic_identities(second_sign=1),'wrong pure-B correction accepted')
    # These three residue cases are exhaustive for integer r modulo3.
    for r in range(3):
        require(r*(r-1)*(r+13)%3==0 and r*(r*r-1)%3==0
                and r*(r-1)*(r-2)%3==0,'missing factor3')
        require((3*r-1)%3!=0 and (3*r-5)%3!=0,'nonunit local denominator')
    cases = [(r,m) for r in range(3,49) for m in range(3,160,2)]
    cases += [(r,m) for r in (3,15,22,24,30,31,97,1000)
              for m in (243,729,363,891,315,22275)]
    for r,m in cases:
        weights,words = construct(r,m)
        for word in words: frame(word)
        require(certificate_ok(r,m,weights,words),f'CRT certificate r={r},m={m}')
    # An integer residue representative is an exact dyadic program, but only
    # its output congruence is certified. Its exact cubic residual is nonzero.
    weights,words = construct(15,33)
    output,rows = replay(15,weights,words)
    require(rows==[[1,0],[0,1]],'scope-control source restoration')
    require(output!=[15,0,0,0] and all((x-y)%33==0 for x,y in zip(output,(15,0,0,0))),
            'modular success was conflated with exact equality')
    badw = weights[:]; badw[0] += 1
    require(not certificate_ok(15,33,badw,words),'wrong query weight accepted')
    badwords = deepcopy(words); badwords[1][0] += 1
    require(not certificate_ok(15,33,weights,badwords),'wrong CRT shear accepted')
    require(not certificate_ok(15,33,weights,words,restore=False),'missing frame inverse accepted')
    require(not certificate_ok(14,33,weights,words),'wrong retained arity accepted')
    try: residue(F(1,3),9)
    except ValueError: pass
    else: raise ValueError('illegal local reduction accepted')
    rejected_domains = 0
    for r,m in ((2,9),(True,9),(F(3),9),(3,1),(3,0),(3,8),(3,-3),(3,True)):
        try: construct(r,m)
        except ValueError: rejected_domains += 1
        else: raise ValueError('invalid domain accepted')
    print(json.dumps({'status':'pass','symbolic_all_arity_identities':2,
                      'integer_shear_modular_certificates':len(cases),
                      'source_inputs_and_mutations':inputs,
                      'algebra_program_rejections':7,'domain_rejections':rejected_domains,
                      'exact_vs_modular_scope_control':'pass'},indent=2))


if __name__=='__main__': main()
