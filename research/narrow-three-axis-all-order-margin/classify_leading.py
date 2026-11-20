from collections import Counter
from functools import lru_cache
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
from math import comb
from pathlib import Path
import json
import time

ROOT=Path(__file__).resolve().parent
COUNTS={(0,0):1277,(0,1):575,(0,2):80,(0,3):12,
        (1,0):775,(1,1):337,(1,2):84,(1,3):14,(1,4):1,
        (2,0):124,(2,1):55,(2,2):3,(2,3):4,(3,0):5,(4,0):14}

def representatives():
 maps=[]
 for axes in permutations(range(3)):
  for complement in (0,7):
   maps.append(tuple(sum(((v>>(2-axes[k]))&1)<<(2-k) for k in range(3))^complement
                     for v in range(8)))
 seen=set()
 out=[]
 for order in permutations(range(8)):
  if order in seen:
   continue
  orbit={tuple(mapping[v] for v in order) for mapping in maps}
  if len(orbit)!=12:
   raise RuntimeError("nonfree orbit")
  seen.update(orbit)
  out.append(order)
 if len(out)!=3360 or len(seen)!=40320:
  raise RuntimeError("incomplete symmetry coverage")
 return out

def packed_source():
 out=[]
 for row in range(8):
  line=[]
  for col in range(8):
   code=0
   for axis,bit in enumerate((2,1,0)):
    r,c=(row>>bit)&1,(col>>bit)&1
    if not r and c:
     code+=1<<(4*axis)
    elif r and not c:
     code+=1<<12
   line.append(code)
  out.append(line)
 return out

H=packed_source()

def polynomial(order,cap):
 e=[]
 for i in range(8):
  row=[]
  for j in range(8):
   a=H[order[i]][order[j]]
   if not i or not j:
    row.append(((a,1),) if a>>12<=cap else ())
   else:
    b=H[order[i-1]][order[j-1]]
    row.append(() if a==b else tuple((k,v) for k,v in ((a,1),(b,-1)) if k>>12<=cap))
  e.append(row)
 values=[None]*256
 values[0]={0:1}
 limit=(cap+1)<<12
 for mask in range(1,256):
  row=mask.bit_count()-1
  out={}
  for col in range(8):
   if mask>>col&1:
    sign=-1 if (mask>>(col+1)).bit_count()%2 else 1
    for a,c in values[mask^(1<<col)].items():
     for b,f in e[row][col]:
      key=a+b
      if key<limit:
       out[key]=out.get(key,0)+sign*c*f
  values[mask]={k:v for k,v in out.items() if v}
 return values[255]

def decode(code):
 return ((code&15),(code>>4)&15,(code>>8)&15,code>>12)

@lru_cache(None)
def shift_monomial(key):
 a,b,c=key
 return tuple(((i,j,k),comb(a,i)*comb(b,j)*comb(c,k)*(-1)**(i+j+k))
              for i in range(a+1) for j in range(b+1) for k in range(c+1))

def shift(poly):
 # U_l = 1 - delta_l. The returned lowest total degree is exact.
 out={}
 for key,value in poly.items():
  for powers,coefficient in shift_monomial(key):
   out[powers]=out.get(powers,0)+value*coefficient
 out={key:value for key,value in out.items() if value}
 degree=min(map(sum,out))
 return degree,{key:value for key,value in out.items() if sum(key)==degree}

def main():
 start=time.monotonic()
 rows=[]
 counts=Counter()
 unique={}
 minimum=None
 max_shift_mass=max_gradient=0
 digest=sha256()
 for n,order in enumerate(representatives()):
  # Truncation is exact; the first nonzero truncation certifies all
  # lower w coefficients vanish as complete polynomials in u,x,r.
  for cap in range(5):
   poly=polynomial(order,cap)
   if poly:
    break
  else:
   raise RuntimeError(("no degree-at-most-four term",order))
  degree=min(code>>12 for code in poly)
  leading={decode(code)[:3]:value for code,value in poly.items() if code>>12==degree}
  taylor_degree,taylor=shift(leading)
  signature=tuple(sorted(leading.items()))
  if signature not in unique:
   unique[signature]=len(unique)
  record={"order":order,"lower_degree":degree,"taylor_degree":taylor_degree,
          "leading":[[list(key),value] for key,value in sorted(leading.items())],
          "taylor":[[list(key),value] for key,value in sorted(taylor.items())],
          "poly_id":unique[signature]}
  rows.append(record)
  counts[(degree,taylor_degree)]+=1
  shift_mass=sum(abs(value)*2**sum(key) for key,value in leading.items())
  gradient=taylor_degree*sum(abs(value) for value in taylor.values())
  max_shift_mass=max(max_shift_mass,shift_mass)
  max_gradient=max(max_gradient,gradient)
  for point in permutations((33,47,62)):
   value=sum(v*point[0]**e[0]*point[1]**e[1]*point[2]**e[2]
             for e,v in taylor.items())
   if value==0:
    raise RuntimeError(("zero center coefficient",order,point))
   absolute=Fraction(abs(value),64**taylor_degree)
   minimum=absolute if minimum is None else min(minimum,absolute)
  digest.update(json.dumps(record,sort_keys=True,separators=(",",":")).encode()+b"\n")
  if n%500==0:
   print(n,round(time.monotonic()-start,3),"unique",len(unique),flush=True)
 output={"classes":len(rows),"orders":12*len(rows),"counts":[[list(key),value] for key,value in sorted(counts.items())],
         "unique_leading_polynomials":len(unique),"rows":rows}
 (ROOT/"leading-classification.json").write_text(json.dumps(output,indent=2)+"\n")
 if counts!=COUNTS or minimum!=Fraction(7,131072) or max_shift_mass!=6656 or max_gradient!=156:
  raise RuntimeError(("classification constants",counts,minimum,max_shift_mass,max_gradient))
 result={"status":"PASS_ALL_ORDER_COMMON_LOWER_CLASSIFICATION","classes":len(rows),"orders":12*len(rows),
         "counts":output["counts"],"unique_leading_polynomials":len(unique),
         "minimum_center_coefficient":str(minimum),"maximum_shifted_coefficient_mass_bound":max_shift_mass,
         "maximum_leading_gradient_bound":max_gradient,"ordered_certificate_sha256":digest.hexdigest(),
         "scope":"Complete degree-at-most-four truncated symbolic classification; no sampled parameter extrapolation."}
 (ROOT/"classification-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)
 print("DONE",dict(counts),"unique",len(unique),"seconds",time.monotonic()-start,flush=True)

if __name__=="__main__":
 main()
