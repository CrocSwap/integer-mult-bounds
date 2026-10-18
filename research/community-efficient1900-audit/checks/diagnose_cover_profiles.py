"""Independent small integer certificates for PR2911's new vanishing claims."""
from pathlib import Path
import json
from fractions import Fraction
P=Path('/tmp/pr-efficient1900')
# Positive integer partitions encoded by a coin-change DP, independent of the
# submission's recursive partition generation and capped profile solver.
squares=[set() for _ in range(17)];squares[0].add(0)
for part in range(1,17):
 for total in range(part,17):
  squares[total].update(x+part*part for x in list(squares[total-part]))
records=[]
for s,t in [(12,6),(10,8)]:
 eo=s*t-64; bound=s*s+t*t-128
 shapes=[(a*a,b*b,a*a*b*b) for a in range(2,s+1,2) for b in range(2,t+1,2) if a*b<=eo and a*a+b*b<=bound]
 rf=128*s-2*s*s;rg=128*t-2*t*t;u=126
 if (s,t)==(12,6):
  assert shapes==[(4,4,16),(4,16,64),(16,4,64)]
  n16f=Fraction(rf-4*u,12);n16g=Fraction(rg-4*u,12)
  counts=[u-n16f-n16g,n16g,n16f];assert counts==[48,16,62]
  rp=sum(n*c[2] for n,c in zip(counts,shapes));required=Fraction(rp+2*eo*eo,128)
  assert required==46 and required not in squares[eo]
  detail={'counts':[int(x) for x in counts],'required_rho_square_sum':int(required),'attainable_square_sums':sorted(squares[eo])}
 else:
  assert shapes==[(4,4,16),(4,16,64),(16,4,64),(16,16,256)]
  assert all(g%12==4 for _,g,_ in shapes) and rg%12!=(4*u)%12
  detail={'g_square_modulus':12,'required_remainder':rg%12,'forced_remainder':(4*u)%12}
 records.append(dict(split=[s,t],shapes=shapes,off_character_count=u,parseval=[rf,rg],contradiction=detail))
(P/'check-2911-independent.json').write_text(json.dumps(dict(status='PASS',scope='No-vanishing subcase excluded by exact integer identities; independent of the submission profile solver and all historical census receipts.',records=records),indent=2)+'\n')
print('PASS independent vanishing constraints, both splits')
