"""Reconstruct the first productive row and its true placement exchange at the new ranks."""
from fractions import Fraction as F
from itertools import islice
from pathlib import Path
from json import dumps
import sys
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
from upstream import HERE,install
install()
from strong_complex import load_changed,word
from raw48 import ComplexRaw
from periodic import Job
from transport import axes
from unpowered_price import ranks,certify
from installations import GAUSSIAN_C, ENTRY, TERMINAL
from strict_moment import UNIT,power_interval
from retimed_supplier import SCALES
assert SCALES==(1,79)
tar,paid=ranks()
margin,cells=certify(GAUSSIAN_C,(tar,paid))
assert min(cells.values())/sum(tar.values()) > F(1,2**64)
assert max(max(v.numerator.bit_length(),v.denominator.bit_length()) for v in cells.values())<512
raw=word(*load_changed(HERE/"inputs"))
roots=[p for p in raw.targets if p.rank==129 and p.tag[:2]==("root","rotated")]
assert len(roots)==384 and tar[10191]==624 and cells[4424,10191]==1
assert power_interval(10191,GAUSSIAN_C)[1]*100 < UNIT*106
out={}
class Support:
    def __init__(self):self.swaps=[]
    def swap(self,a,b,z,s):self.swaps.append((a,b,z))
class Columns:
    window=1
    swap=None
for H in (ENTRY.complex_log,TERMINAL.complex_log):
    M=1<<H
    U=2*(M//(2048*12087))
    band=2*((3*U)//8)
    left,right=F(band*10191,4424),F((band+2)*10191,4424)
    assert U<left<right<M
    assert M*(right-left)>624*4
    sz=10191*(band-8)
    period=4*(-(-M//(4*sz)))
    tickets=tuple(islice(axes(M,sz,period,0),3))
    sup=Support()
    unit=ComplexRaw(None,{},Columns(),low=0,bundle=1,slots=M)
    route=unit.align(sup,Job(0,tickets),ComplexRaw.axis_list(3,(0,)))
    assert sup.swaps[0]==(1,tickets[1],1)
    out[H]=dict(period=period,tickets=tickets,first_swap=sup.swaps[0])
print(dumps(dict(starts=out,root=roots[0].tag,nonempty=len(cells),minimum_probability_lower="2^-64"),
            indent=2))
