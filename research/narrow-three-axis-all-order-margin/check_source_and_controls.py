from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parent

def need(condition,message):
 if not condition:
  raise RuntimeError(message)

def nearest(s,t,j):
 return (2*t*j+s)//(2*s)

def exponent(s,t,j,k):
 return Q((t*k-s*nearest(s,t,j))**2-(t*k-s*nearest(s,t,k))**2,s*s)

def plus(a,b,sign=1):
 out=a.copy()
 for key,value in b.items():
  out[key]=out.get(key,0)+sign*value
 return {k:v for k,v in out.items() if v}

def times(a,b):
 out={}
 for aa,x in a.items():
  for bb,y in b.items():
   key=tuple(a+b for a,b in zip(aa,bb))
   out[key]=out.get(key,0)+x*y
 return {k:v for k,v in out.items() if v}

def evaluate(poly,point):
 return sum(value*point[0]**key[0]*point[1]**key[1]*point[2]**key[2]
            for key,value in poly.items())

def main():
 fixtures=json.loads((ROOT/"source-fixture.json").read_text())
 indices=[]
 for row in fixtures:
  p,t,s,m,k=(row[x] for x in ("p","t","s","m","k"))
  need(p==1<<20 and t==1<<1440 and t>=p**72,"finite source size")
  need(s==(k<<m)+1 and k%2 and 0<k<(1<<m),"Proth structure")
  need(pow(row["witness"],(s-1)//2,s)==s-1,"exact primality certificate")
  need(pow(1,(s-1)//2,s)!=s-1,"forged prime witness rejected")
  gamma=2*p*p*(Q(t,s)-1)
  need(abs(gamma-Q(row["center_numerator"],64))<=Q(1,1<<26),"narrow interval")
  need((1-Q(1,2*p*p))*t<s<=(1-Q(1,4*p*p))*t,"original fine interval")
  need(s>=p**4 and s%2,"original source size")
  delta=t-s
  i=(-(s-1)//2)*pow(delta,-1,s)%s
  need(0<=i<s-1,"nonwrapping selector")
  need(t*i-s*nearest(s,t,i)==-(s-1)//2,"literal extremal phase")
  need(nearest(s,t,i+1)==nearest(s,t,i)+1,"literal same-cell step")
  A,B=2*delta+1,2*s-1
  need(exponent(s,t,i,i+1)==Q(A,s),"literal upper exponent")
  need(exponent(s,t,i+1,i)==Q(B,s),"literal lower exponent")
  need(A+B==2*t,"source exponent relation")
  indices.append(i)
 for first,second in combinations(fixtures,2):
  need(abs(first["s"]-second["s"])>=Q(first["t"],32*first["p"]**2),"source separation")
 # 0.69<ln2<0.70 and 3<pi<22/7 certify alpha=5 for p=2^20.
 need(16<Q(4*24*69,100)/Q(22,7),"alpha=5 lower bound")
 need(Q(4*24*70,100)/3<25,"alpha=5 upper bound")
 classes=json.loads((ROOT/"leading-classification.json").read_text())["rows"]
 special=next(row for row in classes if row["order"]==[1,2,4,0,7,6,5,3])
 u,x,r=({(1,0,0):1},{(0,1,0):1},{(0,0,1):1})
 ru=plus(r,u,-1)
 cube=times(times(ru,ru),ru)
 expected=times(times(cube,plus(times(x,x),times(r,u),-1)),plus(plus(x,r,-1),u,-1))
 expected={key:-value for key,value in expected.items()}
 actual={tuple(k):v for k,v in special["leading"]}
 need(actual==expected,"exact exceptional first-w factorization")
 taylor={tuple(k):v for k,v in special["taylor"]}
 need(evaluate(taylor,(41,49,57))==0,"separated arithmetic centers lose this leading term")
 need(evaluate(taylor,(33,47,62))!=0,"chosen asymmetric centers retain the leading term")
 linear=next(row for row in classes if row["order"]==[1,3,5,2,7,0,6,4])
 need(evaluate({tuple(k):v for k,v in linear["taylor"]},(37,59,43))==0,
      "second tempting center choice fails a leading coefficient")
 result={"status":"PASS_NARROW_PHYSICAL_SOURCE_AND_CONTROLS",
         "source_primes":3,"p":1<<20,"target_bits":1441,"alpha":5,
         "selector_indices":indices,
         "negative_controls":["forged prime witness",
            "equally spaced separated centers fail an exceptional leading term",
            "centers (37,59,43)/64 fail another leading term"],
         "scope":"Exact source fixtures and method obstructions; vanishing Taylor specializations are not physical source counterexamples."}
 (ROOT/"source-and-controls-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)

if __name__=="__main__":
 main()
