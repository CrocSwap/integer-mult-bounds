"""Independent balance-equation check (PR1673, adapted: this package's supplier b and SPEC), not an execution of the ledger in check_ledger.py."""
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal,localcontext
import json,hashlib
D=Path(__file__).resolve().parent;W=D.parent
src=W/'new/SPEC.json'
BJ=json.loads((D/'B.json').read_text())
spec=json.loads(src.read_text());pinned=F(spec['expected']['complex_lower'])
b=F(BJ['b']);q=b-F(1,10**105);eff=(q+b)/2;actual_bit=F('0.001733427039589844234749')
r=F(1,10**105);z=F(1,10**107);s=F(1,10**105)
assert 0<q<eff<b<pinned<actual_bit
# Exact inequalities needed by the stopped support-local supplier.
stop=F(1,10**110);assert (1-stop)*b>eff
assert F(12,5)>F('2.3728639')  # established Le Gall bound (PR1699); tau=12/5
rows={}
# boundary c=(3-tau)/2 with tau=2.372864 > Le Gall's published omega<2.3728639; union row xi+1/2-eps (radix-distributed schedule, outer/UNION-SCHEDULE.md)
# rectangular batching: W^2 RHS columns per page, cost per column W^(omega(1,1,2)-2); tau_eff = omega(1,1,2)-2+1; fixed format exponent sigma=3.2500351 > published 3.250035 (ADVWXXZ 2024)
SIG=F('3.2500351');assert SIG>F('3.250035') and SIG>3
TAUE=SIG-2+1;assert TAUE==F('2.2500351')
for name,c,expected in [('rect_batch_k2_radix_union',(3-TAUE)/2,None)]:
 # Solve E(1+q)+q X=1+q(1-r-z)  (main = fused Gaussian) and X-E(1+q)=s-c (boundary saving = main + s).
 E=(1+q*(1-r-z+c-s))/(1+q)**2;X=E*(1+q)+s-c
 B=1-r-z-X
 assert E*q==1-E+q*B
 assert c+X-E==E*q+s
 assert F(1,2)<X<E<1 and 0<B<E
 assert 1-X-r-B==z>0 and 1-E-r>0
 assert 1-B>0 and 1-B-2*(1-E)>0
 margins={'transform':E*q,'global_router':eff,'gaussian':1-E+q*B,'group_router':1-E+eff*B,'group_scans':1-E+B,'boundary':c+X-E,'sparse_union':X+F(1,2)-E,'polynomials':E,'microfaces':4-E-B}
 old_union=1-E-B-F(1,2)+X
 K=F((E*q*10**105).__floor__(),10**105)-F(1,10**105)
 assert min(margins.values())==E*q and all(v>K for v in margins.values())
 assert old_union<K          # the old g-factor union row is violated at this point: the radix schedule is essential
 assert 1-2*B>0 and X-B-F(1,2)<0   # tag work fits the record; expected flag count g*mu>1 so the union is deliberately not assumed sparse
 rows[name]={'epsilon':str(E),'cap':str(X),'beta':str(B),'kappa':str(K),'margin_above_kappa':str(E*q-K),'checked_margin_count':len(margins),'old_union_row_margin':str(old_union)}
report={'status':'PASS_INDEPENDENT_BALANCE_DERIVATION','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'b':str(b),'rows':rows,'scope':'Independent balance derivation and margin comparisons for this package\'s supplier endpoint; the supplier native admission is bound by verify_release.py; inherited all-size assumptions remain.'}
(D/'INDEPENDENT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
