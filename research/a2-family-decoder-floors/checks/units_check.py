# The three units: E8 (120 lines), P112 = E8 minus the orthogonal frame F0 (112 lines), P104 = E8 minus F0 and F1 (104 lines; #968's unit, F1 = H4).  Dense label table: h = 9, 511 nonzero classes.
import os
os.environ['UNIT']='E8'
from setup9 import load, E8
from frames_data import load_frames
from lib2 import dot
F0,F1=load_frames()
assert len(F0)==8 and len(F1)==8 and not set(F0)&set(F1)
assert all(dot(E8[a],E8[b])==0 for F in (F0,F1) for a in F for b in F if a!=b)
for unit,n in (('P112',112),('P104',104)):
    L,v,G,frames,nbar,h,basis,cls=load(unit)
    assert (v,h,len(cls),len(set(cls.values())))==(n,9,511,511) and all(cls.values())
    print('PASS unit %s: %d lines, label dimension h = 9, 511 distinct nonzero classes, %d eight-frames'%(unit,v,len(frames)))
from a2lib import cls as c8, h as h8
print('PASS unit E8: 120 lines, label dimension h = %d, %d classes'%(h8,len(c8))); assert (len(E8),h8,len(c8))==(120,9,511)
