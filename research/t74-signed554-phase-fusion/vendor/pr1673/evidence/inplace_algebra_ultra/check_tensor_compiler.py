"""Beneš routing and fixed-H-word controls for the tensor compiler."""
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path
import sympy as s

ROOT=Path(__file__).parent
H=s.Matrix([[1,1],[1,-1]])
I=s.eye(2)


def benes(p, indices=None):
    """Route input i to output p[i]. Stages are lists of (low,high,flip)."""
    n=len(p)
    if indices is None:
        indices=list(range(n))
    if n==1:
        return []
    if n==2:
        return [[(indices[0],indices[1],bool(p[0]))]]
    inv=[0]*n
    for i,j in enumerate(p):
        inv[j]=i
    color=[None]*n
    for start in range(n):
        if color[start] is not None:
            continue
        color[start]=0
        todo=[start]
        while todo:
            i=todo.pop()
            for j in [i^1,inv[p[i]^1]]:
                want=1-color[i]
                if color[j] is None:
                    color[j]=want
                    todo.append(j)
                else:
                    assert color[j]==want
    first=[(indices[2*j],indices[2*j+1],bool(color[2*j])) for j in range(n//2)]
    last=[]
    for j in range(n//2):
        i=inv[2*j]
        last.append((indices[2*j],indices[2*j+1],bool(color[i])))
    mids=[]
    for c in [0,1]:
        pc=[None]*(n//2)
        for i in range(n):
            if color[i]==c:
                pc[i//2]=p[i]//2
        mids.append(benes(pc,indices[c::2]))
    assert len(mids[0])==len(mids[1])
    return [first]+[a+b for a,b in zip(*mids)]+[last]


def route(p):
    data=list(range(len(p)))
    stages=benes(p)
    for layer in stages:
        used=set()
        xor=None
        for i,j,flip in layer:
            assert i not in used and j not in used
            used.update([i,j])
            assert (i^j)&((i^j)-1)==0
            if xor is None:
                xor=i^j
            assert i^j==xor
            if flip:
                data[i],data[j]=data[j],data[i]
    for i,j in enumerate(p):
        assert data[j]==i
    return len(stages)


def D(a,b):
    return (s.sympify(a),s.sympify(b))


def u3(q):
    """Execution order; matrix endpoint U(q), q nonzero."""
    a=s.Rational(4,5)*q
    assert a!=0
    return [D(1/a,1),'H',D(-3,1),'H',D(2,1),'H',D(-a/8,s.Rational(-1,6))]


def id2():
    return ['H','H',D(s.Rational(1,2),s.Rational(1,2))]


def id3():
    return ['H',D(1,s.I),'H',D(1,s.I),'H',D((1-s.I)/4,(1+s.I)/4)]


def canonical(word):
    out=[D(1,1)]
    for a in word:
        if a=='H':
            out.extend(['H',D(1,1)])
        else:
            old=out[-1]
            out[-1]=D(s.simplify(old[0]*a[0]),s.simplify(old[1]*a[1]))
    return out


def endpoint(word):
    M=I
    for op in word:
        M=(H if op=='H' else s.diag(*op))*M
    return s.simplify(M)


def gateword(kind,value=None,B=10):
    if kind=='upper':
        c=2*B+1
        w=u3(-c)+u3(value+c)
    elif kind=='lower':
        w=list(reversed(gateword('upper',value,B)))
    elif kind=='diag':
        w=[D(*value)]+id2()+id2()+id2()
    elif kind=='swap':
        w=['H',D(1,-1),'H',D(s.Rational(1,2),s.Rational(1,2))]+id2()+id2()
    elif kind=='fft':
        w=[D(1,value),'H']+id2()+id3()
    else:
        raise ValueError(kind)
    w=canonical(w)
    assert len(w)==13 and sum(x=='H' for x in w)==6
    for op in w:
        if op!='H':
            assert op[0]!=0 and op[1]!=0
    return w


def matching_permutation(n,pairs):
    p=[None]*n
    for j,(a,b) in enumerate(pairs):
        p[a],p[b]=2*j,2*j+1
    free=[i for i,v in enumerate(p) if v is None]
    for j,i in enumerate(free,start=2*len(pairs)):
        p[i]=j
    assert sorted(p)==list(range(n))
    return p


def local_layer(n,pairs,words):
    """Produce one matching layer as (bit, diagonal array) then shared H stages."""
    p=matching_permutation(n,pairs)
    stages=[]
    net=benes(p)
    def switch_layers(layer):
        bit=(layer[0][0]^layer[0][1]).bit_length()-1
        diag=[s.Integer(1)]*n
        for i,j,flip in layer:
            diag[j]=-1 if flip else 1
        return [('H',bit),('D',diag),('H',bit),('D',[s.Rational(1,2)]*n)]
    for layer in net:
        stages+=switch_layers(layer)
    for k in range(13):
        if k%2:
            stages.append(('H',0))
        else:
            diag=[]
            for w in words:
                diag.extend(w[k])
            stages.append(('D',diag))
    for layer in reversed(net):
        stages+=switch_layers(layer)
    return stages


def apply_local(v,stages):
    v=list(v)
    for kind,x in stages:
        if kind=='D':
            v=[s.expand(a*b) for a,b in zip(v,x)]
        else:
            q=1<<x
            for i in range(len(v)):
                if not i&q:
                    a,b=v[i],v[i+q]
                    v[i],v[i+q]=s.expand(a+b),s.expand(a-b)
    return v


def local_matrix(n,stages):
    cols=[]
    for j in range(n):
        cols.append(apply_local([s.Integer(i==j) for i in range(n)],stages))
    return s.Matrix.hstack(*(s.Matrix(c) for c in cols))


def tensor_replay(local):
    """Replay global tensor diagonal/H calls, with no enlarged coordinates."""
    g=len(local)
    n=len(local[0][0][1]) if local[0][0][0]=='D' else 4
    # All examples use N=4; different local matchings have common stage shapes.
    n=4
    V=n**g
    cols=[]
    for col in range(V):
        a=[s.Integer(i==col) for i in range(V)]
        for step in range(len(local[0])):
            kinds=[local[j][step][0] for j in range(g)]
            assert len(set(kinds))==1
            if kinds[0]=='D':
                for i in range(V):
                    j=i
                    c=1
                    for axis in range(g):
                        c*=local[axis][step][1][j%n]
                        j//=n
                    a[i]=s.expand(a[i]*c)
            else:
                # This sequential evaluation checks the same tensor H call.
                for axis in range(g):
                    bit=local[axis][step][1]
                    q=(1<<bit)*n**axis
                    for i in range(V):
                        if not (i//n**axis)&(1<<bit):
                            x,y=a[i],a[i+q]
                            a[i],a[i+q]=s.expand(x+y),s.expand(x-y)
        cols.append(a)
    return s.Matrix.hstack(*(s.Matrix(c) for c in cols))


def main():
    routing=[]
    for n in [2,4,8]:
        count=0
        depth=0
        for p in itertools.permutations(range(n)):
            depth=route(p)
            count+=1
        routing.append({'N':n,'permutations':count,'switch_depth':depth})
    rng=random.Random(20261013)
    for n in [16,32,64]:
        for _ in range(100):
            p=list(range(n));rng.shuffle(p);route(p)
        routing.append({'N':n,'random_permutations':100,'switch_depth':2*(n.bit_length()-1)-1})
    words=[]
    for q in [s.Rational(-10),s.Rational(-3,7),s.Rational(0),s.Rational(7,9),s.Rational(10)]:
        for kind in ['upper','lower']:
            w=gateword(kind,q)
            target=s.Matrix([[1,q],[0,1]]) if kind=='upper' else s.Matrix([[1,0],[q,1]])
            assert endpoint(w)==target
            words.append({'kind':kind,'parameter':str(q),'H_calls':6})
    for kind,value,target in [
        ('diag',(s.Rational(2,3),s.Rational(-7,5)),s.diag(s.Rational(2,3),s.Rational(-7,5))),
        ('swap',None,s.Matrix([[0,1],[1,0]])),
        ('fft',s.I,H*s.diag(1,s.I)),
        ('diag',(1,1),I)]:
        assert endpoint(gateword(kind,value))==target
        words.append({'kind':kind,'H_calls':6})
    assert endpoint(id3())==I
    local=[]
    p0=[(0,3),(2,1)]
    p1=[(3,1),(0,2)]
    w0=[gateword('upper',s.Rational(2,7)),gateword('swap')]
    w1=[gateword('fft',s.I),gateword('lower',s.Rational(-3,5))]
    local=[local_layer(4,p0,w0),local_layer(4,p1,w1)]
    matrices=[local_matrix(4,l) for l in local]
    for actual_local,pairs,words_local in zip(matrices,[p0,p1],[w0,w1]):
        expected=s.zeros(4)
        for (a,b),word in zip(pairs,words_local):
            gate=endpoint(word)
            for i,ii in enumerate([a,b]):
                for j,jj in enumerate([a,b]):
                    expected[ii,jj]=gate[i,j]
        assert actual_local==expected
    target=s.kronecker_product(matrices[1],matrices[0])
    actual=tensor_replay(local)
    assert actual==target
    h_calls=sum(kind=='H' for kind,_ in local[0])
    odometers=[]
    for n,g in [(2,1),(2,8),(4,5),(8,4)]:
        table=[[Fraction(((a+1)*(i+2))%7-3,5) for i in range(n)] for a in range(g)]
        digits=[0]*g
        suffix=[Fraction(1)]*(g+1)
        products=0
        movements=g*n
        for a in range(g-1,0,-1):
            suffix[a]=table[a][0]*suffix[a+1]
            products+=1
        for record in range(n**g):
            value=table[0][digits[0]]*suffix[1]
            products+=1
            direct=Fraction(1)
            for a in range(g):
                direct*=table[a][digits[a]]
            assert value==direct
            k=0
            while k<g:
                digits[k]+=1
                if digits[k]<n:
                    break
                digits[k]=0
                k+=1
            if k==g:
                break
            if k:
                movements+=k*n
                for a in range(k,0,-1):
                    suffix[a]=table[a][digits[a]]*suffix[a+1]
                    products+=1
        odometers.append({'N':n,'g':g,'records':n**g,'coefficient_products':products,
                          'products_per_record':products/n**g,
                          'table_movement_bound':movements,
                          'zeros_in_table':any(not x for t in table for x in t)})
    receipt={'status':'pass','arithmetic':'exact symbolic rational/complex',
             'routing':routing,'fixed_H_word_checks':words,
             'coefficient_odometer':odometers,
             'tensor_test':{'N':4,'axes':2,'data_coordinates':16,
                            'input_output_matrix_entries':256,
                            'simultaneous_H_calls':h_calls,
                            'expected_H_calls':8*2+2,'dimension_expansion':False,
                            'different_axis_matchings':True,
                            'different_axis_gate_kinds':True,
                            'local_matching_endpoints_checked':True}}
    (ROOT/'TENSOR-COMPILER-CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
