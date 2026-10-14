"""Independent balance-equation check (PR1673, adapted: this package's supplier b and SPEC), not an execution of the ledger in check_ledger.py."""
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal,localcontext
import json,hashlib
D=Path(__file__).resolve().parent;W=D.parent
src=W/'new/SPEC.json'
BJ=json.loads((D/'B.json').read_text())
spec=json.loads(src.read_text());pinned=F(spec['expected']['complex_lower'])
b=F(BJ['b']);q=b-F(1,10**64);eff=(q+b)/2;actual_bit=F('0.001733427039589844234749')
r=F(1,10**64);z=F(1,10**66);s=F(1,10**64)
assert 0<q<eff<b<pinned<actual_bit
# Exact inequalities needed by the stopped support-local supplier.
stop=F(1,10**70);assert (1-stop)*b>eff
assert F(12,5)>F('2.3728639')  # established Le Gall bound (PR1699); tau=12/5
rows={}
# boundary c=(3-tau)/2 with tau=2.372864 > Le Gall's published omega<2.3728639; union row xi+1/2-eps (radix-distributed schedule, outer/UNION-SCHEDULE.md)
# structured boundary solves: per entry polylog cost => boundary cost (V/B) W^(1+delta) for every delta>0; tau_eff = 2 + delta with delta = 1e-64 (tau_eff = 2 itself is not claimed)
DELTA=F(1,10**64);TAUE=2+DELTA;assert TAUE>2
for name,c,expected in [('struct_boundary_radix_union',(3-TAUE)/2,None)]:
 # GAUGE-FREE (outer/GAUGEFREE-INTERIORS.md): three LINEAR equations in (E,X,B), solved here by exact Gaussian elimination (independent of the closed form in check_ledger.py):
 #   main = fused Gaussian:  E(1+q) - q B = 1 ;  boundary = main + s:  X - E(1+q) = s - c ;  chirp-only guard:  E - 2X - B = -(1-r-z)  (beta + 2 xi - eps = 1-r-z)
 M=[[1+q,0,-q,F(1)],[-(1+q),1,0,s-c],[1,-2,-1,-(1-r-z)]]
 for i in range(3):
  piv=next(k for k in range(i,3) if M[k][i]!=0);M[i],M[piv]=M[piv],M[i]
  M[i]=[v/M[i][i] for v in M[i]]
  for k in range(3):
   if k!=i:M[k]=[a-M[k][i]*bb for a,bb in zip(M[k],M[i])]
 E,X,B=M[0][3],M[1][3],M[2][3]
 assert E*(1+q)-q*B==1 and X-E*(1+q)==s-c and B+2*X-E==1-r-z
 assert E*q==1-E+q*B
 assert c+X-E==E*q+s
 assert F(1,2)<X<E<1 and 0<B<E
 assert 1-(2*X-E)-r-B==z>0 and 1-E-r>0   # chirp-only precision guard (the old linear guard 1-X-r-B is NEGATIVE here)
 assert 1-X-r-B<0
 assert 1-B>0 and 1-B-2*(1-E)>0
 margins={'transform':E*q,'global_router':eff,'gaussian':1-E+q*B,'group_router':1-E+eff*B,'group_scans':1-E+B,'boundary':c+X-E,'sparse_union':X+F(1,2)-E,'polynomials':E,'microfaces':4-E-B}
 old_union=1-E-B-F(1,2)+X
 K=F((E*q*10**100).__floor__(),10**100)-F(1,10**76)
 assert min(margins.values())==E*q and all(v>K for v in margins.values())
 assert old_union<K          # the old g-factor union row is violated at this point: the radix schedule is essential
 assert 1-B>0 and X-B-F(1,2)<0 and 1-2*B<0   # tag work O(g) per visit paid by the Theta(p) visit cost: g log L<p iff beta<1 (the old 2beta<1 test is not needed); expected flag count g*mu>1
 rows[name]={'epsilon':str(E),'cap':str(X),'beta':str(B),'kappa':str(K),'margin_above_kappa':str(E*q-K),'checked_margin_count':len(margins),'old_union_row_margin':str(old_union)}
report={'status':'PASS_INDEPENDENT_BALANCE_DERIVATION','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'b':str(b),'rows':rows,'scope':'Independent balance derivation and margin comparisons for this package\'s supplier endpoint; the supplier native admission is bound by verify_release.py; inherited all-size assumptions remain.'}
(D/'INDEPENDENT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
