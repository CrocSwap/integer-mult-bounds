import json,sys,mpmath as mp
mp.mp.dps=3150
H={int(k):v for k,v in json.load(open(sys.argv[1])).items()};m=73;W=int(sys.argv[2]);D=int(sys.argv[3])
assert m*W-sum(r*n for r,n in H.items())==D,(m*W-sum(r*n for r,n in H.items()))
def f(a,bad):
    s=sum(mp.mpf(r*n)/(m*W)*mp.power(mp.mpf(m)/r,a) for r,n in H.items())
    if bad: s+=mp.mpf(32*m*sum(H.values()))/(mp.mpf(10)**16*W)*mp.power(m,a)
    return s-1
out={}
for bad in (False,True):
    a0=mp.mpf('0.0017')
    r=mp.findroot(lambda a:f(a,bad),a0,tol=mp.mpf(10)**-3120)
    fl=int(mp.floor(r*mp.mpf(10)**3000))
    out['conservative' if bad else 'complex']=str(fl)
    print('bad',bad,mp.nstr(r,40),flush=True)
json.dump(out,open(sys.argv[4],'w'))
