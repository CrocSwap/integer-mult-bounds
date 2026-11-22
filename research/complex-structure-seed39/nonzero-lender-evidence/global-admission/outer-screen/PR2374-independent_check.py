"""Independent balance-equation check (PR1673, adapted: this package's supplier b and SPEC), not an execution of the ledger in check_ledger.py."""
from fractions import Fraction as F
from pathlib import Path
from decimal import Decimal,localcontext
import json,hashlib,sys
sys.set_int_max_str_digits(0)
D=Path(__file__).resolve().parent;W=D.parent
src=W/'new/SPEC.json'
BJ=json.loads((D/'B.json').read_text())
spec=json.loads(src.read_text());pinned=F(spec['expected']['complex_lower'])
DIG=spec['outer_refinement']['endpoint_digits'];T=10**(DIG+80)   # all free slacks are 10^-(DIG+80) or below (fixed-grid-maximum point, PR2180 / PR2161 dataisfire)
b=F(BJ['b']);q=b-F(1,T);eff=(q+b)/2;actual_bit=F('0.001733427039589844234749')
r=F(1,T);z=F(1,T*100);s=F(1,T)
assert 0<q<eff<b<pinned<actual_bit
# Exact inequalities needed by the stopped support-local supplier.
stop=F(1,T*10**6);assert (1-stop)*b>eff
rows={}
# FINE-PRIME PADDING (outer/FINE-PADDING-COMPOSITION.md): explicit point epsilon=1-delta, beta=1-3 delta, delta=(1025/1024)*10^-(DIG+80), Strassen boundary tau=45/16 (7^16<2^45), c=3/32,
# theta in (1/(4p^2),1/(2p^2-1)], chirp guard beta+2xi-2<1, halo power 48, core power 128. Derived here WITHOUT the ledger code; the structured boundary is not used.
delta=F(1025,1024*T);E=1-delta;B=1-3*delta
assert 7**16<2**45;tau=F(45,16);c=(3-tau)/2;assert c==F(3,32)
nu=2;halo=48;core=128
X=E+E*q+s-c                      # boundary saving c+X-E = E q + s
assert c+X-E==E*q+s
# the Gaussian row has slack: 1-E+qB-Eq = delta(1-2q)
assert 1-E+q*B-E*q==delta*(1-2*q)>0
# admissible beta window for this epsilon: Gaussian row needs beta >= 1-delta(1+1/q); membership needs beta < 1-2 delta
assert 1-delta*(1+1/q)<=B<1-2*delta
assert F(1,2)<X<E<1 and 0<B<E and X<nu
assert 1-(2*X-nu)-r-B>z>0 and 1-E-r>0 and core-halo-B>0 and halo>43
assert 1-B>0 and 1-B-2*(1-E)==delta>0
costs={'transform':1-E*q,'global_router':1-eff,'gaussian':E-q*B,'group_router':E-eff*B,'group_scans':E-B,'boundary':E-X+(tau-1)/2,'sparse_union':E+F(1,2)-X,'polynomials':1-E,'microfaces':E+B+halo-core+2}
K=F((E*q*10**(DIG+46)).__floor__(),10**(DIG+46))-F(1,10**(DIG+22))
assert max(costs.values())==costs['transform'] and all(v<1-K for v in costs.values())
# earlier packages' guards fail at this point (they are rejecting controls in the ledger): linear guard 1-X-r-B<0, old theta chirp guard 1-(2X-E)-r-B<0, 2B<1 test fails
assert 1-X-r-B<0 and 1-(2*X-E)-r-B<0 and 1-2*B<0
assert K>F('0.0016797547881500489087805478664999999999999999999999999999999998000000199999')   # PR1786 exact kappa
assert K>F('0.0016797549561255445213356709939207025769983114385025802954603275201627999999999999999999999999979966404900867489109573286580121585')  # PR1828 exact kappa
assert K>F('0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263049999999997996640490086748910957328658012158594')  # PR1839 exact kappa
assert K>F('0.0016797549561255445213356709939207025769983114385025802954603275201628645482603256388263056561328446322744513169085862209720704481201654121427713006366929567157349625273906229277148454180995537563371124755588139767841405530386745578819565618798006892541712197674874836946756930569827889227573192555649999999997996640490086748910957328658012158594')  # PR1875 exact kappa
assert K>F('0.001679754956125544521335670993920702576998311438502580295460327520162864548260325638826305656132844632274451316908586220972070448120165412142771300636692956715734962527390622927714845418099553756337112475558813976784140553038674557881956561879800689254171219767487483694675693056982788922757319255565606685566411725238449650999339827075715283714270157705762309226038611771955655377501414652136546310799999999999999999997996640490086748910957328658012158594846')  # PR1876 exact kappa
assert K>F('0.001679754956125544521335670993920702576998311438502580295460327520162864548260325638826305656132844632274451316908586220972070448120165412142771300636692956715734962527390622927714845418099553756337112475558813976784140553038674557881956561879800689254171219767487483694675693056982788922757319255565606685566411725238449650999339827075715283714270157705762309226038611771955655377501414652136546310881185746917580802513640545967852810801680966856133978576162943792322682482152988532923811998938861379689883167389728443314312230815059559906903773756886872476136837071871203030423643505345473735135533')  # PR1897 exact kappa
assert K>F('0.001679745508802299051546533685199973672313473419790800679752457380932784242972585600630181672224983')  # PR1758
assert K<q
# epsilon is free: every row is strictly satisfied for every delta > r0 (beta = 1-3 delta); only kappa moves, kappa = (1-delta) q - O(1e-76)
# fixed-grid maximum: saving < C and C*FLOOR integral give K <= C-1/FLOOR-BACKOFF; this point attains it (0 < C-E*q < 1/FLOOR)
FL=10**(DIG+46);assert (pinned*FL).denominator==1 and 0<pinned-E*q<F(1,FL) and K==pinned-F(1,FL)-F(1,10**(DIG+22))
sweep=[]
for dd in [F(1,10**7),F(1,10**12),F(1,10**30),F(1,10**60),F(1025,1024*T),F(11,T*10)]:
    Ed=1-dd;Bd=1-3*dd;Xd=Ed+Ed*q+s-c
    assert 1-Ed-r>0 and 1-dd*(1+1/q)<=Bd<1-2*dd and 1-Ed+q*Bd-Ed*q>0 and Ed-Bd>0 and 1-Bd-2*(1-Ed)>0
    assert F(1,2)<Xd<Ed and 1-(2*Xd-nu)-r-Bd>0 and core-halo-Bd>0
    assert 1-Ed+eff*Bd>Ed*q and eff>Ed*q and 1-Ed+Bd>Ed*q and Ed>Ed*q and 1-(Ed+Bd+halo-core+2)>Ed*q
    sweep.append((str(dd),str(float(q-Ed*q))))
assert 1-F(1,T)<=1-r   # delta=r0 itself is rejected by 1-eps-r0>0
assert not (1-(1-r)-r>0)
rows['struct_boundary_radix_union']={'epsilon':str(E),'cap':str(X),'beta':str(B),'kappa':str(K),'margin_above_kappa':str(E*q-K),'checked_cost_powers':len(costs),'gap_to_q':str(q-K),'epsilon_free_sweep_delta_gap_to_q':sweep}
report={'status':'PASS_INDEPENDENT_BALANCE_DERIVATION','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'b':str(b),'rows':rows,'scope':'Independent balance derivation and margin comparisons for this package\'s supplier endpoint; the supplier native admission is bound by verify_release.py; inherited all-size assumptions remain.'}
(D/'INDEPENDENT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
