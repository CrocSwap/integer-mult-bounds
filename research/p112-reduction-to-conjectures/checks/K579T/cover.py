# impl A coverability: U (label set, const bit dropped -> points of F2^8) inside 3 affine 3-flats (cubes) + 1 affine plane?
import sys, itertools
from base import lab
def rank(vs):
  b=[]
  for v in vs:
    for y in b: v=min(v,v^y)
    if v: b.append(v)
  return len(b)
def span_aff(pts):
  x=pts[0]; basis=[]
  for p in pts[1:]:
    v=p^x
    for y in basis: v=min(v,v^y)
    if v: basis.append(v)
  S={x}
  for v in basis: S|={s^v for s in S}
  return S,len(basis)
def cover(U,cubes,planes):
  if not U: return True
  if len(U)>8*cubes+4*planes: return False
  x=min(U); rest=sorted(U-{x}); seen=set()
  for k,dimcap,c2,p2 in ((3,3,cubes-1,planes),(2,2,cubes,planes-1)):
    if (k==3 and cubes==0) or (k==2 and planes==0): continue
    for sub in itertools.combinations(rest,min(k,len(rest))) if len(rest)>=k else [tuple(rest)]:
      S,d=span_aff((x,)+sub)
      cov=frozenset(U&S)
      if (k,cov) in seen: continue
      seen.add((k,cov))
      if cover(U-cov,c2,p2): return True
  return False
def pts_of(mask): return frozenset(lab[t]&255 for t in range(120) if (mask>>t)&1)
if __name__=='__main__':
  ok=0;n=0
  for fn in sys.argv[1:]:
    for line in open(fn):
      f=line.split(); m=int(f[5])|(int(f[6])<<64); n+=1
      if cover(set(pts_of(m)),3,1): ok+=1; print('COVERABLE',line.strip())
  print('survivors',n,'coverable',ok)
