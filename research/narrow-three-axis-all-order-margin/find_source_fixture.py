from fractions import Fraction
from math import isqrt
from pathlib import Path
import json
import time

ROOT=Path(__file__).resolve().parent
p=1<<20
t=1<<1440
m=720
small_primes=[n for n in range(3,2000,2) if all(n%d for d in range(2,isqrt(n)+1))]
rows=[]
start=time.monotonic()
for center in (33,47,62):
 target=Fraction(t,1+Fraction(center,128*p*p))
 k0=((target.numerator//target.denominator-1)>>m)
 k0-=((k0-1)%6)
 for offset in range(10000):
  k=k0+6*offset
  s=(k<<m)+1
  if any(s%q==0 for q in small_primes):
   continue
  if pow(3,(s-1)//2,s)==s-1:
   gamma=2*p*p*(Fraction(t,s)-1)
   if not abs(gamma-Fraction(center,64))<=Fraction(1,1<<26):
    raise RuntimeError("fixture left narrow source interval")
   if not (0<k<(1<<m) and k%2):
    raise RuntimeError("fixture Proth structure")
   rows.append({"center_numerator":center,"p":p,"t":t,"m":m,"k":k,"s":s,
                "witness":3,"search_offset":offset})
   print("found",center,"offset",offset,"seconds",time.monotonic()-start,flush=True)
   break
 else:
  raise RuntimeError("bounded prime-certificate search exhausted")
(ROOT/"source-fixture.json").write_text(json.dumps(rows,indent=2)+"\n")
print("PASS_THREE_NARROW_SOURCE_PRIMES",flush=True)
