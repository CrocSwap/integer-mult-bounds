"""Serialize the Gaussian program on a signed binary coefficient tape."""

from condensed import ProductPage, SolvePage, Words
from fractions import Fraction
from io import BytesIO

from axis_program import Carve, CirclePass, Factor
from recovery_radius import page_limit


def put_nat(stream,n):
    if n < 0:
        raise ValueError("negative page length")
    while n >= 128:
        stream.write(bytes([(n & 127)|128]))
        n >>= 7
    stream.write(bytes([n]))


def get_nat(stream):
    result = shift = 0
    while True:
        b = stream.read(1)
        if not b:
            raise ValueError("truncated page length")
        result |= (b[0]&127)<<shift
        if b[0] < 128:
            if shift and not b[0]:
                raise ValueError("redundant page length")
            return result
        shift += 7


def read(stream,n):
    data = stream.read(n)
    if len(data)!=n:
        raise ValueError("truncated coefficient catalogue")
    return data


def put_words(out,numbers):
    numbers = tuple(numbers)
    width = max((1+abs(z).bit_length()//8 for z in numbers),default=1)
    put_nat(out,width)
    put_nat(out,len(numbers))
    for z in numbers:
        out.write(z.to_bytes(width,"little",signed=True))


def get_words(src,expected=None):
    width,count = get_nat(src),get_nat(src)
    if width==0 or expected is not None and count!=expected:
        raise ValueError("coefficient word extent")
    return Words(width,read(src,width*count))


def put_circle(out,c):
    put_nat(out,c.side)
    for table in (c.before,c.eigenvalues,c.after):
        put_words(out,(x for z in table for x in z))


def get_circle(src,t):
    side=get_nat(src)
    if not side or side&(side-1) or t%side:
        raise ValueError("local circle extent")
    def pairs():
        it=iter(get_words(src,2*t))
        return tuple(zip(it,it,strict=True))
    return CirclePass(side,pairs(),pairs(),pairs())


def emit(axes):
    out=BytesIO()
    out.write(b"FGP1")
    put_nat(out,len(axes))
    for positions,broad,narrow in axes:
        put_nat(out,broad.carve.target)
        put_words(out,positions)
        out.write(bytes(broad.carve.flags))
        for f in (broad,narrow):
            for z in (f.output_shift,f.work_bits,f.component_width,f.condition_guard,
                      f.defect.numerator,f.defect.denominator):
                put_nat(out,z)
            put_circle(out,f.phase)
            if f.phase_inverse:
                put_circle(out,f.phase_inverse)
            put_nat(out,-f.residual.offsets.start)
            put_words(out,f.residual.coefficients)
            if f.condensed:
                put_words(out,f.condensed.forward)
                put_words(out,f.condensed.backward)
                put_words(out,(x for x,y in f.diagonal_scale))
    return out.getvalue()


def open_catalogue(packet,g):
    src=BytesIO(packet)
    if read(src,4)!=b"FGP1" or get_nat(src)!=len(g.sources):
        raise ValueError("wrong Gaussian catalogue")
    axes=[]
    for s,t in zip(g.sources,g.targets,strict=True):
        if get_nat(src)!=t:
            raise ValueError("wrong original extent")
        positions=tuple(get_words(src,s))
        if positions!=tuple((2*t*j+s)//(2*s) for j in range(s)):
            raise ValueError("wrong original coordinates")
        flags=tuple(read(src,t))
        if any(flag>1 for flag in flags):
            raise ValueError("invalid boundary set")
        carve=Carve(t,flags)
        n=sum(flags)
        factors=[]
        for inverse in (False,True):
            shift,w,head,guard,num,den=(get_nat(src) for _ in range(6))
            if not den or w<g.precision or head<=w or guard<1:
                raise ValueError("unusable coefficient grid")
            defect=Fraction(num,den)
            if defect>=page_limit(g):
                raise ValueError("unresolved Gaussian page")
            phase=get_circle(src,t)
            other=get_circle(src,t) if inverse else None
            width=get_nat(src)
            if 2*width>n or not n:
                raise ValueError("invalid cyclic correction band")
            offsets=range(-width,width+int(2*width!=n))
            residual=ProductPage(n,offsets,w,get_words(src,n*len(offsets)))
            solve=diagonal=None
            if inverse:
                core=n-width
                near=sum(min(i,width) for i in range(core))
                upper=near+core*width+width*(width-1)//2
                forward=get_words(src,upper)
                backward=get_words(src,upper+n)
                solve=SolvePage(n,width,w,forward,backward)
                diagonal=tuple((v,0) for v in get_words(src,t))
            factors.append(Factor(carve,phase,other,residual,solve,diagonal,
                                  shift,defect,w,head,guard))
        axes.append((positions,*factors))
    if src.read(1):
        raise ValueError("trailing catalogue data")
    return tuple(axes)
