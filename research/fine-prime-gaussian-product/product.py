"""Multiply two binary strings through the original-coordinate Gaussian transform."""

import sys
from pathlib import Path
from contextlib import closing
from dataclasses import dataclass
from math import isqrt, prod

if __name__ == "__main__":
    sys.path.insert(0,str(Path(__file__).resolve().parent))

from gaussian_pages import CoefficientAdmissionError
from recovery_radius import page_limit, rounding_numerator

from axis_program import make_axis
from crt_route import Banks, export_field, import_field, original_reshape, route
from catalogue_codec import emit, open_catalogue
from fine_ring import Trace, chirp_middle, times
from c_dispatch import SourceC
from selected_h import SelectedH
from scattered_cnot import ScatteredCNOT
from compact_ordinary import transpose
from word_multiply import product as word_product


@dataclass(frozen=True)
class Geometry:
    sources: tuple
    targets: tuple
    digit_bits: int
    precision: int
    alpha: int
    block: int
    window: int
    batch: int
    use_caller_page_limit: bool = False


def ceil_log(n):
    return (n-1).bit_length()


def prime(n):
    return n >= 3 and n % 2 == 1 and all(n % j for j in range(3,isqrt(n)+1,2))


def choose(n):
    if n <= 144:
        return Geometry((5,7),(8,8),8,128,2,4,24,3)
    if n <= 1800:
        # 899 source points cover 2*ceil(n/4)-1 coefficients throughout this range.
        return Geometry((31,29),(32,32),4,96,2,16,7,3,True)
    b = ceil_log(n)
    p = 6*b
    address = ceil_log((4*n+b-1)//b)
    d = 1 << (((p**997).bit_length()-1)//1000)
    if d < 2 or address < 2*d:
        return None
    ell, extra = divmod(address, d)
    targets = (1 << (ell+1),)*extra + (1 << ell,)*(d-extra)
    q = 8*p
    alpha = 2+isqrt(2*ceil_log(16*p))
    width = 2*alpha*(isqrt(q+1)+1)
    block = 1 << (((p**9).bit_length()-1)//8)
    if 4*width >= block or block > targets[-1]:
        return None
    sources = []
    for t in sorted(set(targets),reverse=True):
        low = max(3,(t*p*p + p*p)//(p*p+1))
        high = 4*t*p*p//(4*p*p+1)
        count = targets.count(t)
        found = []
        for s in range(high if high%2 else high-1,low-1,-2):
            if prime(s):
                found.append(s)
                if len(found)==count:
                    break
        if len(found) != count:
            return None
        sources.extend(found)
    S = prod(sources)
    if not 2*((n+b-1)//b)-1 <= S < 1<<b:
        return None
    return Geometry(tuple(sources),targets,b,q,alpha,block,width,d)


def catalogue(g):
    limit = page_limit(g)
    return tuple(make_axis(s,t,g.alpha,g.block,g.window,g.precision,max_defect=limit)
                 for s,t in zip(g.sources,g.targets,strict=True))


def transform(data, g, pages, opposite, tr, backend):
    padded = original_reshape(data,g.sources,g.targets,g.precision+3,tr,extract=False)
    sparse_moves = 0
    for j,(_,expand,_) in enumerate(pages):
        padded, receipt = expand.run(padded,g.targets,j,g.precision,tr)
        sparse_moves += receipt
    padded = chirp_middle(padded,g.sources,g.targets,g.precision,inverse=opposite,
                          trace=tr,h_backend=backend)
    for j,(_,_,correct) in enumerate(pages):
        padded, receipt = correct.run(padded,g.targets,j,g.precision,tr)
        sparse_moves += receipt
    # The opposite still has an extractor. Holes outside its image can be dirty.
    return original_reshape(padded,g.sources,g.targets,g.precision+3,tr,extract=True), sparse_moves


def pointwise(left,right,q,trace):
    size = len(left)
    with closing(Banks(trace)) as owner:
        x = import_field(left,size,q+3,owner)
        y = import_field(right,size,q+3,owner)
        out = owner.make(q+3)
        x.home()
        y.home()
        for _ in range(size):
            out.append(times(x.read(),y.read(),1 << q,trace))
        return export_field(out)


def recover(values,source_size,q,b,amplification,radius,trace):
    width = 2*b+ceil_log(source_size)+3
    limit = word_product(radius,radius,trace)
    largest = 0
    def scale(x):
        return word_product(word_product(x,source_size,trace),source_size,trace) << amplification
    with closing(Banks(trace)) as owner:
        y = import_field(values,source_size,q+3,owner)
        z = owner.make(width)
        y.home()
        for _ in range(source_size):
            re,im = y.read()
            scaled = scale(re)
            rounded = (scaled+(1 << (q-1))) >> q
            if not 0 <= rounded < 1 << (width-2):
                raise ArithmeticError("coefficient outside its integer range")
            real_error = scaled-(rounded << q)
            imag_error = scale(im)
            squared = word_product(real_error,real_error,trace)+word_product(imag_error,imag_error,trace)
            if squared > limit:
                raise ArithmeticError("observed complex residual exceeds the admitted radius")
            largest = max(largest,squared)
            z.append((rounded,0))
        return export_field(z),largest


def ingress(bits, b, q, n, size):
    padded=bits.zfill(n)
    out = []
    for i in range(0,n,b):
        digit=int(padded[max(0,n-i-b):n-i],2)
        out.append((digit << (q-b-2),0))
    return out + [(0,0)]*(size-len(out))


def carry_scan(coefficients,b,n):
    carry = 0
    little = []
    mask = (1 << b)-1
    for c in coefficients:
        total = c+carry
        carry, digit = total >> b, total & mask
        little.extend(reversed(format(digit,"b").zfill(b)))
    while carry:
        little.append("1" if carry&1 else "0")
        carry >>= 1
    if "1" in little[2*n:]:
        raise ArithmeticError("binary product exceeds twice the input width")
    little.extend("0" for _ in range(2*n-len(little)))
    return "".join(reversed(little[:2*n]))


def elementary(left,right,n):
    # Finite controller branch. The diagnostic reports this path by name.
    def read(s):
        x = 0
        for a in s:
            x = (x<<1) + (a=="1")
        return x
    x = read(left)
    z = 0
    for a in right:
        z <<= 1
        if a=="1":
            z += x
    return format(z,"b").zfill(2*n)


def multiply(left,right):
    backend=SelectedH(SourceC(ScatteredCNOT(transpose)))
    if any(not s or set(s)-{"0","1"} for s in (left,right)):
        raise ValueError("two nonempty unsigned binary strings are required")
    n = max(len(left),len(right))
    g = choose(n)
    if g is None:
        return elementary(left,right,n), {"path":"elementary"}
    q,b = g.precision,g.digit_bits
    S = prod(g.sources)
    try:
        packet = emit(catalogue(g))
        pages = open_catalogue(packet,g)
        packet_bits = 8*len(packet)
        del packet
        gamma = sum(a.output_shift+c.output_shift for _,a,c in pages)
        amplification_bits = 2*b+4+3*gamma
        bound = rounding_numerator(g,pages)
    except CoefficientAdmissionError:
        if n <= 1800:
            raise
        return elementary(left,right,n), {"path":"elementary","reason":"coefficient admission"}
    trace = Trace()
    def crt(data, inverse, w):
        return route(data,g.sources,g.targets,inverse,w,g.batch,trace,backend)
    def forward(bits):
        field = ingress(bits,b,q,n,S)
        return transform(crt(field,False,q+3),g,pages,False,trace,backend)
    u,m0 = forward(left)
    v,m1 = forward(right)
    field = pointwise(u,v,q,trace)
    del u,v
    y,m2 = transform(field,g,pages,True,trace,backend)
    del field
    recovered,largest = recover(y,S,q,b,amplification_bits,bound,trace)
    ordered = crt(recovered,True,2*b+ceil_log(S)+3)
    coeffs = [v for v,_ in ordered]
    bits = carry_scan(coeffs,b,n)
    if trace.live:
        raise ArithmeticError("unreleased transform tape")
    return bits, dict(path="gaussian", sources=g.sources,targets=g.targets,precision=q,
                      digit_bits=b,scale_exponent=gamma,coefficients=coeffs,
                      radius_numerator=bound,radius_denominator=1<<q,
                      max_residual_squared_numerator=largest,
                      catalogue_bits=packet_bits,sparse_layout_bit_travel=m0+m1+m2,trace=vars(trace))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left")
    parser.add_argument("right")
    parser.add_argument("--receipt",action="store_true",help="also print finite diagnostic counters")
    args = parser.parse_args()
    answer, receipt = multiply(args.left,args.right)
    if args.receipt:
        import json
        print(json.dumps({"product":answer,"receipt":receipt}))
    else:
        print(answer)
