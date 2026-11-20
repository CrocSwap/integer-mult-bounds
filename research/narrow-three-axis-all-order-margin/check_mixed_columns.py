"""Independent scalar mixed-coefficient reconstruction by column multilinearity."""
from collections import defaultdict
from itertools import permutations
from pathlib import Path
from hashlib import sha256
import json
import sys
import time

ROOT=Path(__file__).resolve().parent

def multiply(a,b):
 out=defaultdict(int)
 for (w,h),x in a.items():
  for (v,k),y in b.items():
   out[(w+v,h+k)]+=x*y
 return {key:value for key,value in out.items() if value}

def source(point):
 one={(0,0):1}
 a=[[one]]
 for c in point:
  b=[[one,{(0,0):1,(0,1):-c}],[{(1,0):1},one]]
  a=[[multiply(x,y) for x in ra for y in rb] for ra in a for rb in b]
 return a

def displacement(h,order):
 a=[[h[i][j] for j in order] for i in order]
 out=[]
 for i in range(8):
  row=[]
  for j in range(8):
   value=a[i][j].copy()
   if i and j:
    for key,v in a[i-1][j-1].items():
     value[key]=value.get(key,0)-v
   row.append({key:v for key,v in value.items() if v})
  out.append(row)
 return out

def determinant_columns(cols):
 if len(set(cols))<8:
  return 0
 a=[list(row) for row in zip(*cols)]
 old,sign=1,1
 for k in range(7):
  pivot=next((i for i in range(k,8) if a[i][k]),None)
  if pivot is None:
   return 0
  if pivot!=k:
   a[pivot],a[k]=a[k],a[pivot]
   sign=-sign
  value=a[k][k]
  for i in range(k+1,8):
   for j in range(k+1,8):
    numerator=a[i][j]*value-a[i][k]*a[k][j]
    q,r=divmod(numerator,old)
    if r:
     raise RuntimeError("Bareiss nonexact division")
    a[i][j]=q
  for i in range(k+1,8):
   a[i][k]=0
  old=value
 return sign*a[7][7]

def mixed_coefficient(e,d,k):
 choices=[]
 for j in range(8):
  column=[]
  for w in range(d+1):
   for h in range(k+1):
    vector=tuple(e[i][j].get((w,h),0) for i in range(8))
    if any(vector):
     column.append((w,h,vector))
  choices.append(column)
 cols=[None]*8
 count=0
 def visit(j,w,h):
  nonlocal count
  if j==8:
   if w==0 and h==0:
    count+=1
    return determinant_columns(cols)
   return 0
  total=0
  for dw,dh,vector in choices[j]:
   if dw<=w and dh<=h:
    cols[j]=vector
    total+=visit(j+1,w-dw,h-dh)
  return total
 return visit(0,d,k),count

def main():
 data=json.loads((ROOT/"leading-classification.json").read_text())
 rows=data["rows"]
 if len(sys.argv)>1:
  rows=rows[:int(sys.argv[1])]
 cases=products=0
 digest=sha256()
 points=list(permutations((33,47,62)))
 matrices=[source(point) for point in points]
 start=time.monotonic()
 for index,row in enumerate(rows):
  for point,matrix in zip(points,matrices):
   coefficient,count=mixed_coefficient(displacement(matrix,row["order"]),
                                       row["lower_degree"],row["taylor_degree"])
   expected=sum(v*point[0]**ex[0]*point[1]**ex[1]*point[2]**ex[2]
                for ex,v in row["taylor"])
   if coefficient!=expected or not coefficient:
    raise RuntimeError(("mixed coefficient mismatch",row["order"],point,coefficient,expected))
   products+=count;cases+=1
   digest.update((str(row["order"])+str(point)+str(coefficient)+"\n").encode())
  if index%500==0:
   print(index,round(time.monotonic()-start,3),"determinants",products,flush=True)
 result={"status":"PASS_MIXED_COLUMN_LEADING_COEFFICIENTS",
         "classes":len(rows),"center_permutations":6,"coefficient_checks":cases,
         "scalar_determinants":products,"ordered_values_sha256":digest.hexdigest(),
         "scope":"Independent numeric mixed-coefficient reconstruction; symbolic lower-degree vanishing and uniform mass bounds are checked by the primary certificate."}
 (ROOT/"mixed-column-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result),flush=True)
 print("seconds",time.monotonic()-start,flush=True)

if __name__=="__main__":
 main()
