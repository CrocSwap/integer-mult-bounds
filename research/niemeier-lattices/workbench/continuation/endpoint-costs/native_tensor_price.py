from pathlib import Path
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "paid-controller"))
from portable import WORKBENCH, output_path, source_name
from pathlib import Path
from fractions import Fraction as F
from math import isqrt
import sys,json,hashlib

import banked as b
ROOT=Path(__file__).resolve().parent
FRONTIER=F(1612722852614221,10**18)
N=2*112**2; BLOCKS=224; C=BLOCKS*64;H=17
raw=(ROOT/'sources/EXPECTED.json').read_bytes(); expected=json.loads(raw)

def row(provider,L):
 native=expected['providers'][provider]['complete_contract']
 hist={int(k):v for k,v in native['paid_profile'].items()}
 widths={int(k):v for k,v in native['width_inventory'].items()}
 b.c.require(sum(w*n for w,n in hist.items())==2*112*8+64+sum(w*n for w,n in widths.items()),'Native rank-mass identity')
 m=16*L+1;cap=isqrt((m*m-1)//2);D=(L-1)*N-L*C;W=F((L-1)*N)
 terms=[(F(L*BLOCKS*w*n),F(m,w)) for w,n in hist.items()]
 terms.append((F(2*N*L*8),F(m,8)))
 for idle in b.c.idle_slots(L,16):
  terms.extend((F(2*N*r),F(m,r)) for r in b.parts(idle,cap))
 banks={}
 for width,count in widths.items():
  spectator=H-width;q=(m-spectator)//width;pad=m-q*width
  for r in b.parts(pad,cap):terms.append((F(L*BLOCKS*count*r,q),F(m,r)))
  W+=F(L*BLOCKS*count,q)
  banks[str(width)]=dict(roles_per_invocation=count,spectators=spectator,per_bank=q,pad=pad)
 b.c.require(all(F(m,base)<=cap for _,base in terms),'Strict square shrink cap')
 b.c.require(sum(mass for mass,_ in terms)==m*W-D,'Lifted complete rank-mass identity')
 return dict(h=H,ports=N,m=m,cap=cap,stages=L,stock=W,deficit=D,terms=terms),banks

def main():
 result={}
 for provider in ('atm3','ck'):
  rows=[]
  for L in range(3,102,2):
   r,banks=row(provider,L);lo,hi=b.c.bracket(r);pl,ph=b.pressure(r,FRONTIER/(1-FRONTIER))
   rows.append(dict(stages=L,m=r['m'],stock=str(r['stock']),deficit=r['deficit'],kappa_scaled_1e18=b.c.scaled(lo/(1+lo),hi/(1+hi)),pressure_at_frontier=str(pl),pressure_exceeds_deficit=pl>r['deficit'],banks=banks))
  best=max(rows,key=lambda r:r['kappa_scaled_1e18'][0])
  result[provider]=dict(best=best,rows=rows)
  print(provider,'best L',best['stages'],'kappa',best['kappa_scaled_1e18'],'relative',float(F(best['kappa_scaled_1e18'][0],10**18)/FRONTIER-1))
 out=dict(scope='Exact rational moment invoice conditional on the inherited PR600 native contract and complement-lift interface. No new native scalar-word replay or claimed exponent.',source=dict(pr=600,head='dfb7b827990d7b586b3cd778e3d750c050dd4778',expected_sha256=hashlib.sha256(raw).hexdigest(),frontier=str(FRONTIER)),parameters=dict(ports=N,ambient=H,native_invocations=BLOCKS,helpers=BLOCKS*504,center_bill=C),models=result)
 output_path('continuation/endpoint-costs/NATIVE-TENSOR-PRICE.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
