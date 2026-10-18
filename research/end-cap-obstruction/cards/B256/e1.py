from vr import *
import sys
W0=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz')
def leafops(dst,row,skip=()):
    ops=[]
    for j,c in sorted(row.items()):
        if j==dst or j in skip: continue
        ops.append(['add',dst,j,c.numerator,c.denominator,[]])
    return ops
def e1(pos):
    w=copy.deepcopy(W0)
    rows=rows_at(w,'B',585)
    row=rows[283]  # value of 283 read at B585
    ops=leafops(591,row)
    assert w['B'][585][:3]==['add',591,283]
    del w['B'][585]
    w['A'][pos:pos]=ops
    return w
if __name__=='__main__':
    for pos in (0,473):
        w=e1(pos); r,nw=relax(w)
        print(pos,'value same',same_value(W0,r),'widened',nw,'caps',caps(r)[0],prof(r))
