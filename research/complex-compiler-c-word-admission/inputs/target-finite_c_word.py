"""Enumerate and check finite all-column Gaussian C programs on complete owners."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import product


ARITY = {"add":2, "sub":2, "half":1, "clear":1, "neg":1, "i":1,
         "unit":1, "x":2, "s":2, "cz":3, "cx":3, "paid":2}
NAMES = tuple(ARITY)
SCALARS = set(NAMES[:6])


def turn(z, k=1):
    a, b = z
    return ((a,b),(-b,a),(-a,-b),(b,-a))[k%4]


def pm(a,b,sign):
    return a[0]+sign*b[0], a[1]+sign*b[1]


@dataclass(frozen=True)
class Matrix:
    """Integers in row-major order and one power-of-two denominator."""
    den: int
    rows: tuple

    @staticmethod
    def identity(n):
        d=1<<n
        return Matrix(0,tuple(tuple((int(i==j),0) for j in range(d)) for i in range(d)))

    def left(self, op, axes):
        a=axes[0] if axes else 0
        b=axes[1] if len(axes)>1 else 0
        mask=1<<a
        data=[]
        den=self.den
        if op=="paid":
            den+=1
        for j,original in enumerate(self.rows):
            if op=="paid":
                other=self.rows[j^mask]
                # C has (1+i)/2 on the diagonal and (1-i)/2 off diagonal.
                row=tuple(pm(pm(l,r,1),turn(pm(l,r,-1)),1) for l,r in zip(original,other))
            elif op in ("x","cx"):
                src=j^mask if op=="x" else j^((j>>a&1)<<b)
                row=self.rows[src]
            else:
                exponent=1 if op=="unit" else (j>>a&1) if op=="s" else 2*(j>>a&1)*(j>>b&1)
                row=tuple(turn(x,exponent) for x in original)
            data.append(row)
        while den and all(not((u|v)&1) for row in data for u,v in row):
            data=[tuple((u//2,v//2) for u,v in row) for row in data]
            den-=1
        return Matrix(den,tuple(data))


@dataclass(frozen=True)
class Word:
    dimension: int
    productive: int
    owned: int
    ops: tuple

    def valid_syntax(self):
        if self.dimension<2 or self.productive<2 or self.owned<0:
            return False
        rows=self.productive+self.owned
        for op,*args in self.ops:
            if op not in ARITY or len(args)!=ARITY[op] or not 0<=args[0]<rows:
                return False
            if op in ("add","sub"):
                if not 0<=args[1]<rows:
                    return False
            elif op not in SCALARS and any(not 0<=x<self.dimension for x in args[1:]):
                return False
            if op in ("cz","cx") and args[1]==args[2]:
                return False
        return True

    def funded(self):
        paid=sum(op[0]=="paid" for op in self.ops)
        return paid**500 < self.productive**500 * self.dimension**499

    def all_columns(self):
        if not self.valid_syntax():
            return False
        eye=Matrix.identity(self.dimension)
        one=Fraction(1),Fraction(0)
        rows=[{(i,eye):one} for i in range(self.productive)]+[{} for _ in range(self.owned)]
        for op,reg,*args in self.ops:
            old=rows[reg]
            if op in ("add","sub"):
                new=dict(old)
                for key,z in rows[args[0]].items():
                    new[key]=pm(new.get(key,(0,0)),z,1 if op=="add" else -1)
            elif op=="clear":
                new={}
            elif op in ("half","neg","i"):
                if op=="half":
                    new={k:(z[0]/2,z[1]/2) for k,z in old.items()}
                else:
                    new={k:turn(z,1 if op=="i" else 2) for k,z in old.items()}
            else:
                new={}
                for (owner,mat),z in old.items():
                    key=owner,mat.left(op,args)
                    new[key]=pm(new.get(key,(0,0)),z,1)
            rows[reg]={key:z for key,z in new.items() if z!=(0,0)}
        target=eye
        for axis in range(self.dimension):
            target=target.left("paid",(axis,))
        return all(rows[i]=={(i,target):one} for i in range(self.productive))


def parse(code):
    """Use unary integer fields; the header gives N, W and owned field count."""
    if not code.endswith("0"):
        return None
    tokens=iter(len(x) for x in code[:-1].split("0"))
    try:
        n,w,z=next(tokens),next(tokens),next(tokens)
        ops=[]
        for tag in tokens:
            op=NAMES[tag]
            args=[]
            for _ in range(ARITY[op]):
                args.append(next(tokens))
            ops.append((op,*args))
    except (StopIteration,IndexError):
        return None
    return Word(n,w,z,tuple(ops))


def compile_within(p):
    """The length cap pays cold verification. Every fixed finite code is covered eventually."""
    limit=(p.bit_length()-1)//32
    for length in range(1,limit+1):
        for bits in product("01",repeat=length-1):
            candidate=parse("".join(bits)+"0")
            if candidate and candidate.valid_syntax() and candidate.funded() and candidate.all_columns():
                return candidate
    return None
