"""Check signed leaf multiplication and cross its predecessor's native FFT threshold."""

from pathlib import Path
from random import Random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from fine_ring import Trace
from word_multiply import BASE_BITS, physical_product, product

if __name__=="__main__":
    tr=Trace()
    rng=Random(1729)
    cases=[(0,-1),(-1,0),(-(1<<500),1<<612),(7,-3),(-31,-31)]
    for width in (1,4,8,32,127,563,BASE_BITS):
        x,y=rng.getrandbits(width),rng.getrandbits(width)
        cases.extend([(x,y),(x,-y),(-x,-y)])
    for x,y in cases:
        if product(x,y,tr)!=x*y:
            raise ArithmeticError("fixed radix leaf")
    if tr.fast_words or tr.scalar_products!=len(cases):
        raise ArithmeticError("unexpected bounded scalar dispatch")
    x,y=-65543,98311
    if physical_product(x,y)!=x*y:
        raise ArithmeticError("wrong signed native FFT product")
    print("PASS bounded signed leaf cases",len(cases),"production child at 17 bits",x*y)
