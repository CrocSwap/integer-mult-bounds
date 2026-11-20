"""Apply disjoint address shears to complete rows through ordinary B1 rectangles."""
from dataclasses import dataclass
from itertools import chain

from fine_ring import Tape


FLIP = (("roll", "y", "first", 1), ("swap", "t", "b"),
        ("roll", "b", "endbits", 1), ("swap", "t", "b"),
        ("roll", "y", "second", 1), ("swap", "t", "b"),
        ("roll", "b", "undo_endbits", -1), ("swap", "t", "b"))
LOAD = (("swap", "u", "b"), ("roll", "b", "startbits", 1), ("swap", "u", "b"))
UNLOAD = (("swap", "u", "b"), ("roll", "b", "startbits", -1), ("swap", "u", "b"))
WORD = FLIP + LOAD + FLIP + UNLOAD


def copy(source, target, count):
    for _ in range(count):
        target.append(source.read())


def image(i, a, b, width):
    if a <= i < a+width:
        return i+b-a
    if b <= i < b+width:
        return i+a-b
    return i


def exchange_number(i, a, b, width):
    z = ((i >> a) ^ (i >> b)) & ((1 << width)-1)
    return i ^ (z << a) ^ (z << b)


def placement(n, h, reservoir):
    for slot in range(3):
        a = n-(3*reservoir+slot+1)*h
        b = 0 if slot == 2 else n-(slot+1)*h
        if a != b:
            yield min(a,b), max(a,b)


def literal(field, pairs):
    for a,b in pairs:
        buckets = [Tape(field.width,field.trace) for _ in range(4)]
        field.home()
        count = len(field.cells)
        for i in range(count):
            buckets[2*((i>>a)&1)+((i>>b)&1)].append(field.read())
        field.release()
        result = Tape(buckets[0].width,buckets[0].trace)
        for bank in buckets:
            bank.home()
        for i in range(count):
            x = (i>>a)&1
            result.append(buckets[2*x+(x^((i>>b)&1))].read())
        for bank in buckets:
            bank.release()
        field = result
    return field


def radix(keys, values, bits, unit):
    """Stable full-key passes on the exceptional records of one row."""
    count = len(keys.cells)
    if count < 2:
        keys.home()
        values.home()
        return keys, values
    for bit in range(bits):
        kk = [Tape(keys.width,keys.trace) for _ in range(2)]
        vv = [Tape(values.width,values.trace) for _ in range(2)]
        keys.home()
        values.home()
        for _ in range(count):
            key = keys.read()
            z = (key[0] >> bit)&1
            kk[z].append(key)
            copy(values, vv[z], unit)
        keys.release()
        values.release()
        keys = Tape(kk[0].width,kk[0].trace)
        values = Tape(vv[0].width,vv[0].trace)
        for k,v in zip(kk,vv,strict=True):
            k.home()
            v.home()
            copy(k,keys,len(k.cells))
            copy(v,values,len(v.cells))
            k.release()
            v.release()
    keys.home()
    values.home()
    return keys, values


@dataclass
class ShearReceipt:
    ordinary: int = 0
    literal: int = 0
    batches: int = 0
    rotations: int = 0
    repaired_records: int = 0


class SparseWord:
    def __init__(self,n,h,g,k,pairs):
        self.n, self.h, self.g, self.k = n,h,g,k
        self.y = n-3*h
        self.pairs = tuple(sorted(pairs,key=lambda x:x[1]))
        ends = [b for _,b in self.pairs]
        flat = tuple(chain.from_iterable(self.pairs))
        if (g<1 or k<1 or not ends or len(ends)*g>h or self.y<k
            or len(set(flat))!=len(flat) or any(not 0<=a<self.y for a in flat)
            or ends[-1]+k>self.y or any(a+k>b for a,b in zip(ends,ends[1:]))):
            raise ValueError("invalid sparse target guards")
        self.shifts = {"b":0, "y":h, "t":h+self.y, "u":2*h+self.y}
        self.widths = {"b":h, "y":self.y, "t":h, "u":h}

    def part(self,address,name):
        return (address>>self.shifts[name]) & ((1<<self.widths[name])-1)

    def offset(self,address,op):
        u, t, y = (self.part(address,v) for v in ("u","t","y"))
        result = 0
        name = op[2]
        mask = (1<<self.g)-1
        for i,(a,b) in enumerate(self.pairs):
            at = i*self.g
            z = (u>>at)&1
            digit = (t>>at)&mask
            if name == "first":
                result += 2*z*digit << b
            elif name == "second":
                result += z*(1-2*digit) << b
            elif name == "startbits":
                result += ((y>>a)&1) << at
            elif name == "endbits":
                result += ((y>>b)&1) << at
            else:
                result += (((y>>b)&1)^z) << at
        return result*op[3]

    def inverse(self,address):
        for op in reversed(WORD):
            if op[0] == "swap":
                address = exchange_number(address,self.shifts[op[1]],self.shifts[op[2]],self.h)
            else:
                s,mask = self.shifts[op[1]], (1<<self.widths[op[1]])-1
                delta = self.offset(address,op)
                old = (address>>s)&mask
                address ^= (old ^ ((old-delta)&mask)) << s
        return address

    def ideal(self,address):
        y = self.part(address,"y")
        for a,b in self.pairs:
            address ^= ((y>>a)&1) << (b+self.h)
        return address

    def bad(self,address):
        u,t,y = (self.part(address,v) for v in ("u","t","y"))
        B = 1<<self.g
        span = 1 << (self.k-1)
        for i,(_,b) in enumerate(self.pairs):
            if ((u>>(i*self.g)) & (B-1)) == B-1 or ((t>>(i*self.g)) & (B-1)) == B-1:
                return True
            guard = (y>>(b+1)) & (span-1)
            if not 2*B <= guard < span-2*B:
                return True
        return False

    def run(self,field,suffix,ordinary,receipt):
        n = self.n+suffix
        for op in WORD:
            if op[0] == "swap":
                lo,hi = sorted((self.shifts[op[1]]+suffix,self.shifts[op[2]]+suffix))
                field = ordinary(field,lo,hi,self.h,n)
            else:
                shift,bits = self.shifts[op[1]],self.widths[op[1]]
                span = 1 << (shift+bits+suffix)
                out = Tape(field.width,field.trace)
                for base in range(0,len(field.cells),span):
                    address = (base>>suffix) & ((1<<self.n)-1)
                    start = ((-self.offset(address,op)) % (1<<bits)) << (shift+suffix)
                    field.seek(base+start)
                    copy(field,out,span-start)
                    field.seek(base)
                    copy(field,out,start)
                field.release()
                field = out
                receipt.rotations += 1
        out = Tape(field.width,field.trace)
        unit,row = 1<<suffix,1<<self.n
        field.home()
        for _ in range(len(field.cells)//(row*unit)):
            good = Tape(field.width,field.trace)
            bad = Tape(field.width,field.trace)
            keys = Tape(self.n+2,field.trace)
            for i in range(row):
                if self.bad(i):
                    keys.append((self.ideal(self.inverse(i)),0))
                    copy(field,bad,unit)
                else:
                    copy(field,good,unit)
            receipt.repaired_records += len(keys.cells)
            keys,bad = radix(keys,bad,self.n,unit)
            good.home()
            for i in range(row):
                if self.bad(i):
                    if keys.read()[0] != i:
                        raise ArithmeticError("exceptional shear key misses its actual hole")
                    copy(bad,out,unit)
                else:
                    copy(good,out,unit)
            for tape in (good,bad,keys):
                tape.release()
        field.release()
        receipt.batches += 1
        return out


class ScatteredCNOT:
    """Bind b1(field, width, prefixes, gap, suffix_records) on complete rectangles."""
    def __init__(self,b1):
        self.b1 = b1
        self.receipt = ShearReceipt()

    def ordinary(self,field,lo,hi,width,n):
        if not (0<=lo and lo+width<=hi and hi+width<=n):
            raise ValueError("invalid ordinary block placement")
        count = len(field.cells)
        prefixes = count>>(hi+width)
        field = self.b1(field,width,prefixes,1<<(hi-lo-width),1<<lo)
        if len(field.cells) != count:
            raise ValueError("incomplete ordinary rectangle")
        self.receipt.ordinary += 1
        return field

    def __call__(self,field,pairs,n,p):
        pairs = tuple(pairs)
        flat = tuple(chain.from_iterable(pairs))
        if (not 1<=n or p<2 or not len(field.cells) or len(field.cells)%(1<<n)
            or len(flat)!=len(set(flat)) or any(not 0<=x<n for x in flat)):
            raise ValueError("incomplete or overlapping scattered CNOT request")
        if not pairs:
            return field
        lg = (p-1).bit_length()
        return self.run_parameters(field,pairs,n,lg*lg,4*lg+6,64*(4*lg+6))

    def run_parameters(self,field,pairs,n,suffix,g,k):
        """Use the literal total implementation when the selected fields do not fit."""
        taken = set(chain.from_iterable(pairs))
        N, h = n-suffix,len(pairs)*g
        gap = suffix
        for point in sorted(taken):
            if point < gap:
                continue
            if gap+suffix <= point:
                break
            gap = point+1
        if N<10*h or gap+suffix>n:
            self.receipt.literal += len(pairs)
            return literal(field,pairs)
        field = self.ordinary(field,0,gap,suffix,n)
        edges = tuple(tuple(image(i,0,gap,suffix)-suffix for i in pair) for pair in pairs)
        cohorts = [[],[],[]]
        for a,b in edges:
            for r in range(3):
                low,high = N-(3*r+3)*h,N-3*r*h
                if not (low<=a<high or low<=b<high):
                    cohorts[r].append((a,b))
                    break
        for r,group in enumerate(cohorts):
            if not group:
                continue
            moves = tuple(placement(N,h,r))
            for lo,hi in moves:
                field = self.ordinary(field,lo+suffix,hi+suffix,h,n)
            by_color = {}
            tail = []
            y = N-3*h
            for a,b in group:
                for lo,hi in moves:
                    a,b = image(a,lo,hi,h),image(b,lo,hi,h)
                a,b = a-h,b-h
                if not (0<=a<y and 0<=b<y):
                    raise ArithmeticError("reservoir occupies a listed endpoint")
                if b+k<=y:
                    by_color.setdefault(b%k,[]).append((a,b))
                else:
                    tail.append((a+h+suffix,b+h+suffix))
            for color in sorted(by_color):
                raw = SparseWord(N,h,g,k,by_color[color])
                field = raw.run(field,suffix,self.ordinary,self.receipt)
            field = literal(field,tail)
            self.receipt.literal += len(tail)
            for lo,hi in reversed(moves):
                field = self.ordinary(field,lo+suffix,hi+suffix,h,n)
        return self.ordinary(field,0,gap,suffix,n)
