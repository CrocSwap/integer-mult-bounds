"""Verify factorization on symplectic matrices and check all absolute entries of native gate words."""
from collections import deque
from random import Random
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from bruhat import BASIS, PAIRS, columns_apply, compile_lift, entry_numerator, factor, linear, parity


def need(ok,message):
    if not ok:
        raise ValueError(message)


def project_mono(m,p):
    # Recover the outgoing modulation by evaluating its defining linear character on every input.
    x,z=p>>4,p&15
    shear=sum((((m["linear"][i]&1)*((x>>i)&1))<<i) for i in range(4))
    for i,(a,b) in enumerate(PAIRS):
        if (m["cross"]>>i)&1:
            shear ^= (((x>>a)&1)<<b) | (((x>>b)&1)<<a)
    znew,=[t for t in range(16) if all(parity(t&linear(m,b))==parity((shear^z)&b) for b in BASIS)]
    return (linear(m,x)<<4) | znew


def verify_sym(sym):
    f=factor(sym)
    for i,s in enumerate(sym):
        r=project_mono(f["right"],1<<i)
        swap=((r>>4)^r)&f["mask"]
        need(project_mono(f["left"],s)==(r^swap^(swap<<4)),"Bruhat binary identity")
    return f["mask"].bit_count()


def update_col(p,g):
    op,i,j=g
    x,z=p>>4,p&15
    if op=="H":
        k=((x^z)>>i)&1
        x^=k<<i
        z^=k<<i
    elif op=="S":
        z^=x&(1<<i)
    elif op=="CX":
        z^=((z>>j)&1)<<i
        x^=((x>>i)&1)<<j
    return (x<<4)|z


def native(words):
    eye=[(int(r==c),0) for r in range(16) for c in range(16)]
    e=0
    columns=[1<<i for i in range(8)]
    mat=eye
    for g in words:
        kind,i,j=g
        columns=[update_col(v,g) for v in columns]
        new=[]
        for r in range(16):
            bit=(r>>i)&1
            for c in range(16):
                value=mat[16*r+c]
                if kind=="H":
                    a,b=mat[16*(r&~(1<<i))+c]; u,v=mat[16*(r|(1<<i))+c]
                    if bit: u,v=-u,-v
                    a,b=a+u,b+v
                    value=(a-b,a+b)
                elif kind=="S" and bit or kind=="i":
                    value=(-value[1],value[0])
                elif kind=="X":
                    value=mat[16*(r^(1<<i))+c]
                elif kind=="Z" and bit:
                    value=(-value[0],-value[1])
                elif kind=="CX" and bit:
                    value=mat[16*(r^(1<<j))+c]
                new.append(value)
        mat=new
        e+=kind=="H"
    return columns,mat,e


def main():
    ident=tuple(1<<i for i in range(8))
    smallgens=[(k,i,0) for i in range(2) for k in ("H","S")]+[("CX",0,1),("CX",1,0)]
    seen={ident}
    todo=deque([ident])
    while todo:
        s=todo.popleft()
        verify_sym(s)
        for g in smallgens:
            t=tuple(update_col(v,g) for v in s)
            if t not in seen:
                seen.add(t)
                todo.append(t)
    need(len(seen)==720,"embedded full Sp(4,2)")
    rng=Random(721034)
    gens=[(k,i,0) for k in ("H","S","X","Z","i") for i in range(4)]
    gens += [("CX",i,j) for i in range(4) for j in range(4) if i!=j]
    tests=[ [("H",i,0) for i in range(h)] for h in range(5)]
    tests+= [[rng.choice(gens) for _ in range(28)] for _ in range(45)]
    classes=set()
    for word in tests:
        s,mat,e=native(word)
        classes.add(verify_sym(s))
        f=compile_lift(s,mat,e)
        h=f["mask"].bit_count()
        for i,v in enumerate(mat):
            unscaled=entry_numerator(f,i//16,i%16)
            need(tuple(x<<e for x in unscaled)==tuple(x<<h for x in v),"absolute lift mismatch")
    need(classes==set(range(5)),"all Bruhat ranks")
    for invalid,table in [([1]*8,None),(ident,[(0,0)]*256),(ident,[(2,0)]+[(0,0)]*255)]:
        try:
            compile_lift(invalid,table)
        except ValueError:
            pass
        else:
            raise ValueError("invalid matrix accepted")
    print("PASS all 720 embedded symplectic matrices, 50 absolute four-qubit gate words, "
          "12,800 phased entries, five support ranks and three invalid inputs")


if __name__=="__main__":
    main()
