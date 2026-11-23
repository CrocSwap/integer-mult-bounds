"""Structural dyadic prefix certificates and fixed-denominator carry updates."""
from fractions import Fraction as F
from functools import cache
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'retained'))
import factor_words as fw
import transducer as low


def need(ok,message):
    if not ok:raise ValueError(message)


def pair_add(a,b):return a[0]+b[0],a[1]+b[1]
def pair_max(a,b):return max(a[0],b[0]),max(a[1],b[1])
def twice(a):return 2*a[0],2*a[1]


def ceil_log2_positive(value):
    value=F(value);exponent=max(0,value.numerator.bit_length()-value.denominator.bit_length())
    if value>1<<exponent:exponent+=1
    return exponent


def matrix_certificate(matrix):
    denominators=[value.denominator for row in matrix for value in row]
    need(all(x.bit_count()==1 for x in denominators),'non-dyadic prefix')
    d=max(x.bit_length()-1 for x in denominators)
    norm=max(sum(abs(value) for value in column) for column in zip(*matrix))
    return d,ceil_log2_positive(norm)


def step_matrix(matrix,op):
    kind,i,*args=op
    if kind=='swap':
        j=args[0]
        for row in matrix:row[i],row[j]=row[j],row[i]
    elif kind=='add':
        j,a=args
        for row in matrix:row[i]+=F(a)*row[j]
    elif kind=='scale':
        a=F(args[0])
        for row in matrix:row[i]*=a
    else:raise ValueError('unknown emitted operation')


@cache
def literal_certificate(n,word):
    result=(0,0)
    for direction in (word,tuple(fw.invert_op(op) for op in reversed(word))):
        matrix=[[F(i==j) for j in range(n)] for i in range(n)]
        for op in direction:
            step_matrix(matrix,op)
            result=pair_max(result,matrix_certificate(matrix))
    return result


def certificate(recipe):
    kind=recipe.kind
    if kind=='identity':return 0,0
    if kind=='permutation':
        need(all(op[0]=='swap' for op in recipe.data['ops']),'permutation recipe contains arithmetic')
        return 0,0
    if kind=='literal':return literal_certificate(recipe.n,tuple(tuple(op) for op in recipe.data['ops']))
    if kind in ('inverse','extend'):return certificate(recipe.children[0])
    a,b=map(certificate,recipe.children)
    if kind=='direct_sum':return pair_max(a,b)
    if kind in ('multiply','tensor'):return pair_add(a,b)
    if kind=='conjugate':return pair_add(twice(a),b)
    if kind=='guard':return pair_add(a,twice(b))
    raise ValueError('unknown recipe constructor')


def restore_recipe(data):
    count=fw.Count(**data['count'])
    return fw.Recipe(data['kind'],data['n'],count,tuple(restore_recipe(c) for c in data['children']),data['data'])


ALPHABET=json.loads((HERE/'retained'/'ALPHABET.json').read_text())
ADDS={F(x) for x in ALPHABET['addition_coefficients']}
SCALES={F(x) for x in ALPHABET['scale_coefficients']}


def evaluate_row(word,source,q,cert,trace=False):
    """Cert must be established for the word; optional traces are test output."""
    d,e=cert;need(d>=0 and e>=0,'nonnegative certificate')
    need(q>=3 and q%2==1 and all(0<=x<q for x in source),'canonical odd-radix input')
    values=list(source);p=[0]*len(values);D=1<<d
    W=d+e+9;work_limit=1<<(W-1);stored_limit=1<<(d+e+1)
    steps=[];peak=0;observer=low.Observer()
    for op in word:
        kind,i,*args=op
        need(0<=i<len(values),'target index')
        if kind=='swap':
            j=args[0];values[i],values[j]=values[j],values[i];p[i],p[j]=p[j],p[i]
        else:
            coefficient=F(args[1] if kind=='add' else args[0]);a=coefficient.numerator;den=coefficient.denominator
            s=den.bit_length()-1
            need(coefficient in (ADDS if kind=='add' else SCALES),'outside source alphabet')
            if kind=='add':
                j=args[0];column=low.Column((den,a),s);inputs=(values[i],values[j])
                old=den*p[i]+a*p[j]
            elif kind=='scale':column=low.Column((a,),s);inputs=(values[i],);old=a*p[i]
            else:raise ValueError('unknown arithmetic operation')
            bits,c,_=low.produce(column,low.integer_rows(inputs,q),observer)
            numerator=old+c*D
            peak=max(peak,abs(old),abs(c*D),abs(numerator))
            need(abs(old)<work_limit and abs(c*D)<work_limit and abs(numerator)<work_limit,'work width exceeded')
            need(numerator%den==0,'entire carry numerator is not exactly divisible')
            p[i]=numerator//den;values[i]=low.from_bits(bits)
            need(all(abs(x)<stored_limit for x in p),'stored numerator width exceeded')
        if trace:steps.append((tuple(values),tuple(p)))
    return {'low':values,'numerators':p,'denominator_exponent':d,'signed_work_bits':W,
            'peak':peak,'trace':steps,'first_rows':observer.first_rows,'second_rows':observer.second_rows}
