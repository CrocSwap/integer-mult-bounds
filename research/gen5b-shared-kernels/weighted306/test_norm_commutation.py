"""Exhaustive finite regression for the exact unsigned commutation lemma.
No upstream word is executed. Prepared with OpenAI assistance.
"""
from itertools import product

def apply(v,e):
    a,b,c=e;v=v[:];v[a]+=abs(c)*v[b];return v

def check_pair(u,v,initial):
    a,b,c=u;x,y,d=v
    assert a!=b and x!=y and y!=a and x!=b,'forbidden crossing'
    forward1=apply(apply(initial,u),v);forward2=apply(apply(initial,v),u)
    assert forward1==forward2
    iu=(a,b,-c);iv=(x,y,-d)
    reverse1=apply(apply(initial,iv),iu);reverse2=apply(apply(initial,iu),iv)
    assert reverse1==reverse2
    assert max(initial+apply(initial,u)+forward1)==max(forward1)
    assert max(initial+apply(initial,iv)+reverse1)==max(reverse1)
    return True

def run():
    checked=0
    for a,b,x,y in product(range(4),repeat=4):
        if a==b or x==y or y==a or x==b:continue
        for c,d in product((-3,-1,1,3),repeat=2):
            check_pair((a,b,c),(x,y,d),[1,2,5,11]);checked+=1
    rejected=0
    for u,v in [((0,1,1),(2,0,1)),((0,1,1),(1,2,1))]:
        initial=[1,2,5,11]
        try:check_pair(u,v,initial)
        except AssertionError:rejected+=1
        else:raise AssertionError('Invalid crossing accepted')
        assert apply(apply(initial,u),v)!=apply(apply(initial,v),u)
    assert checked==1344 and rejected==2
    result=dict(signed_commuting_pairs=checked,directions_per_pair=2,rejected_crossing_controls=rejected)
    print(f'PASS {checked} signed commuting-pair cases, both directions, and {rejected} forbidden-crossing controls')
    return result
if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    run()
