"""Check the signed input reader and the ordinary dispatcher on fenced intervals."""
from contextlib import closing
from dataclasses import replace
from io import BytesIO
from itertools import product
from random import Random
from fiscal_scans import LowCounter, magnitude_bits, rectangle_slab, slab_indices, transfer, zero_bytes


class Window(BytesIO):
    def __init__(self,data,*,short=None,restore=False):
        super().__init__(b'GUARD'+data+b'END')
        self.origin=5
        super().seek(5)
        self.limit=5+len(data)
        self.short=short
        self.restore=restore
        self.moves=[]

    def read(self,size=-1):
        assert size>=0 and self.origin<=self.tell()<=self.limit
        return super().read(min(size,self.limit-self.tell(),self.short or size))

    def seek(self,to,whence=0):
        assert self.restore and (to,whence)==(self.origin,0)
        self.moves.append(abs(self.tell()-to))
        return super().seek(to,whence)


def oracle(data, side, prefix, gap, suffix):
    result=bytearray(len(data))
    for p in range(prefix):
        for a in range(side):
            for g in range(gap):
                for b in range(side):
                    x=(((p*side+a)*gap+g)*side+b)*suffix
                    y=(((p*side+b)*gap+g)*side+a)*suffix
                    result[y:y+suffix]=data[x:x+suffix]
    return result


def check_fixed_product():
    from band_product import Product

    values = (741503, 466013)
    tapes = [BytesIO(b"pre" + value.to_bytes(3, "little") + b"guard") for value in values]
    for source in tapes:
        source.seek(3)
    lengths = tuple(magnitude_bits(source, 3) for source in tapes)
    output = BytesIO()
    machine = Product((3, 5), 8, 136)
    sign, size, coefficients = machine._multiply_tapes(*tapes, output, lengths, True, True)
    assert lengths == (20, 19)
    assert sign and size == 5 and int.from_bytes(output.getvalue(), "little") == 345550037539
    assert list(coefficients[:5]) == [11811, 10996, 4152, 868, 77]
    assert not any(coefficients[5:]) and machine.h_calls == 157248
    for value, source in zip(values, tapes, strict=True):
        assert source.tell() == 3
        assert source.getvalue() == b"pre" + value.to_bytes(3, "little") + b"guard"
    print("signed scanner and fixed-geometry product -345550037539; 157248 H calls")


def main():
    from ordinary_carrier import ordinary_swap,stage_body
    from installations import COMPACT
    from band_product import multiply_tapes
    packets=0
    for n in range(8):
        for w in product((0,1,128,255),repeat=n):
            data=bytes(w); src=Window(data,restore=True)
            assert magnitude_bits(src,n)==int.from_bytes(data,'little').bit_length()
            assert src.moves==[n] and src.tell()==src.origin
            packets+=1
    for n in (65535,65536,65537,131073):
        for data in (bytes(n), bytes(n-1)+b'\x80', b'\x81'+bytes(n-1), b'\xff'*n):
            src=Window(data,restore=True)
            assert magnitude_bits(src,n)==int.from_bytes(data,'little').bit_length() and src.moves==[n]
            packets+=1
        data=Random(n+551).randbytes(n); src=Window(data,short=383); out=BytesIO()
        transfer(src,out,n); assert out.getvalue()==data and src.tell()==src.limit and not src.moves
        out=BytesIO(); zero_bytes(out,n);assert out.getvalue()==bytes(n)
    src=Window(b'\xff\x00',restore=True)
    try:magnitude_bits(src,3)
    except EOFError:pass
    else:raise AssertionError('truncated declared interval passed')
    assert src.moves==[2] and src.tell()==src.origin
    for raw in ((b'\x00', b''),(b'\x01\x02',b'\x03')):
        a,b=(Window(v,restore=True) for v in raw); out=BytesIO()
        sign,length=multiply_tapes(a,len(raw[0]),b,len(raw[1]),out,left_negative=True)
        value=int.from_bytes(raw[0],'little')*int.from_bytes(raw[1],'little')
        assert sign==bool(value) and int.from_bytes(out.getvalue(),'little')==value and length==len(out.getvalue())
        assert a.tell()==a.origin and b.tell()==b.origin
    tests=0
    for bits in (0,1,2,4):
        for p,g,s in ((1,1,1),(3,5,7),(5,3,1)):
            side=1<<bits; data=Random(983+bits+g).randbytes(p*g*s*side**2)
            src=Window(data);dst=BytesIO();ordinary_swap(src,dst,bits,p,g,s)
            assert dst.getvalue()==oracle(data,side,p,g,s) and src.tell()==src.limit and not src.moves
            tests+=1
    small=replace(COMPACT,rank_logs=(1,))
    p,g,s=3,2,2; side=3**4; data=Random(593).randbytes(p*g*s*side**2)
    src=Window(data);dst=BytesIO();stage_body(src,dst,4,p,g,s,1,small)
    assert dst.getvalue()==oracle(data,side,p,g,s) and src.tell()==src.limit and not src.moves
    print('signed magnitude tapes',packets,'plus EOF restoration and two signed product calls')
    print('ordinary dispatcher cold',tests,'direct rank-two slabs',p,'arbitrary direct bytes',len(data))
    for p,g,s in ((2,3,4),(1,1,5)):
        srcdata=Random(p*123).randbytes(p*g*s*4); src=Window(srcdata,short=2); pad=BytesIO();dst=BytesIO()
        for _ in range(p):rectangle_slab(src,pad,2,3,g,s)
        actual=Window(pad.getvalue(),short=3)
        for _ in range(p):rectangle_slab(actual,dst,2,3,g,s,restrict=True)
        assert dst.getvalue()==srcdata and not src.moves and not actual.moves
    print('bounded-copy chunk crossings 4; round-trip rectangle slabs 3')


if __name__=='__main__':
    import sys

    main()
    if "--fixed-product" in sys.argv[1:]:
        check_fixed_product()
