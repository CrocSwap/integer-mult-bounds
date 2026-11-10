# Successor: Rohan Arun/OpenAI Codex global input rechart; predecessor attribution retained.
"""Derive a finite common grid from every exact prefix row and scalar product.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from math import lcm
from pathlib import Path
import gzip,json,sys

def derive(word):
 n=word['public'];rows=[{r:Q(1)}for r in range(n)]+[{}for _ in range(word['owned_fields'])]
 denom=1;peak=Q(1);witness=None;visits=0
 def observe(row,i,kind):
  nonlocal denom,peak,witness,visits
  for v in row.values():denom=lcm(denom,v.denominator);visits+=1
  mass=sum(map(abs,row.values()))
  if mass>peak:peak=mass;witness=[i,kind]
 for i,e in enumerate(word['program']):
  op,r=e[:2]
  if op in('INIT','CLEAR'):rows[r]={}
  elif op=='SCALE':
   rows[r]={k:Q(e[2])*v for k,v in rows[r].items()};observe(rows[r],i,'scale')
  elif op in('ADD','COPY'):
   if op=='COPY':assert not rows[r]
   product={k:Q(e[3])*v for k,v in rows[e[2]].items()};observe(product,i,'product')
   row=rows[r].copy()
   for k,v in product.items():
    value=row.get(k,Q(0))+v
    if value:row[k]=value
    else:row.pop(k,None)
   rows[r]=row;observe(row,i,'stored')
 odd=denom;frac=0
 while odd%2==0:odd//=2;frac+=1
 return dict(odd_scale=odd,fractional_bits=frac,unscaled_maximum_mass=str(peak),scaled_maximum_mass=str(peak*odd),mass_witness=witness,coefficient_visits=visits),rows
if __name__=='__main__':
 w=json.load(gzip.open(sys.argv[1],'rt'));result,rows=derive(w)
 Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n');print(result)
