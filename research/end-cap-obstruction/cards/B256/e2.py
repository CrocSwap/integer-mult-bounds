from vr import *
W0=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz')
def fix591(w,posB=245,terms=(283,281,299,297)):
    w=copy.deepcopy(w)
    assert w['B'][585][:3]==['add',591,283]
    del w['B'][585]
    for k,u in enumerate(terms): w['B'].insert(posB+k,['add',591,u,1,1,[]])
    return w
if __name__=='__main__':
    for pos in (240,245,150,0):
        w=fix591(W0,pos); print(pos,'valsame',same_value(W0,w)); r,nw=relax(w)
        print(' widened',nw,'caps',caps(r)[0],prof(r))
