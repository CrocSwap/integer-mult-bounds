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
for name,c,expected in [('classical_matrix_12_5',F(3,10),None)]:
 if name=='strassen':
  # Solve E(1+q)+q X=1+q(1-r-z), X-E(1+q)=s-c.
  E=(1+q*(1-r-z+c-s))/(1+q)**2;X=E*(1+q)+s-c
 else:
  # Solve E(1+q)+q X=1+q(1-r-z), 2X-E(1+q)=1/2+s-r-z.
  X=(F(3,2)+q+s-(1+q)*(r+z))/(2+q);E=(1+q*(1-r-z-X))/(1+q)
 B=1-r-z-X
 assert E*q==1-E+q*B
 assert (c+X-E==E*q+s) if name=='strassen' else (1-E-B-F(1,2)+X==E*q+s)
 assert F(1,2)<X<E<1 and 0<B<E
 assert 1-X-r-B==z>0 and 1-E-r>0
 assert 1-B>0 and 1-B-2*(1-E)>0
 margins={'transform':E*q,'global_router':eff,'gaussian':1-E+q*B,'group_router':1-E+eff*B,'group_scans':1-E+B,'boundary':c+X-E,'sparse_union':1-E-B-F(1,2)+X,'polynomials':E,'microfaces':4-E-B}
 if name=='strassen':margins['union_key_sort']=margins['sparse_union']-(B+1-E)
 else:assert X-B-F(1,2)>0
 K=F((E*q*10**100).__floor__(),10**100)-F(1,10**76)
 assert min(margins.values())==E*q and all(v>K for v in margins.values())
 with localcontext()as cc:cc.prec=55
 rows[name]={'epsilon':str(E),'cap':str(X),'beta':str(B),'kappa':str(K),'margin_above_kappa':str(E*q-K),'checked_margin_count':len(margins)}
report={'status':'PASS_INDEPENDENT_BALANCE_DERIVATION','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'b':str(b),'rows':rows,'scope':'Independent balance derivation and margin comparisons for this package\'s supplier endpoint; the supplier native admission is bound by verify_release.py; inherited all-size assumptions remain.'}
(D/'INDEPENDENT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
