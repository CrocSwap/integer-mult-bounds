# Independent-row all-field law: pre-source-formula sketch

This is the coordinator's exploratory derivation during task feasibility, before reading PR6710's PROOF or code. Existing6701/6703/4807 statements and the scout's proposed subspace route were known. The live search then found6710's body already claiming an arbitrary-dependency-space law and sign results; the proposed new-theorem task is rejected as duplicate. This note is not a claim of a new theorem or blind independence. The6701/6703 prior work is this account's own previous contribution. No source/new scientific code was run and no finite census was performed. Any selected successor must credit SHIN09-git6710's existing law and describe external verification only. The exploratory reasoning predates a public task claim and is recorded honestly rather than retroactively relabelled.

Let F haveq elements, m>=1,1<=k<=m. Fixu!=0 and full-row-rank V withV*u=1_k. For complete uniform H inGL_m(F), write x=H^-1*u, Y=V*H. The joint orbit should be all pairs x!=0,rankY=k,Y*x=1_k, with constant fibers. For each fixedx, the number of suchY is

`D_(m,k)=q^(m-1)*product_(i=0..k-2)(q^(m-1)-q^i)`.

Every proper leading principal guard of I-x*y_i requires its partial pairing sum toavoid1. LetR=ker(Y^T) be the row-relation space; endpointYx=1 impliesR<=1_k^perp. Subspace-Möbius inversion for rankY=k gives indicator `sum_(U<=R) mu(U)` with `mu(U)=(-1)^d*q^(d*(d-1)/2)`, d=dimU.

For U<=1perp, letL=Uperp (containing1), l=k-d, and

`A(L)=#{z inL: everycoordinate z_i!=0}`.

The count of safe prefix vectors `p inL` with everyp_i!=1 is also A(L), by p->1-p. For fixedx with lastcoordinate nonzero and total support sizes, each of m-s zero coordinates permits an arbitrary column inL (q^l choices), each of s-1 earlier nonzero coordinates chooses an arbitrary safe prefix (A(L)choices), and the final nonzero coordinate has a unique column reaching1. Thus constrained columns number `q^(l*(m-s))*A(L)^(s-1)`. Ifx_m=0 there is no safe proper last prefix endingat1.

There are `binom(m-1,s-1)*(q-1)^s` suchx. Summing support first gives

`N_good=(q-1)*sum_(U<=1perp) mu(U)*[q^(k-d)+(q-1)*A(Uperp)]^(m-1)`.

Therefore proposed independent-row joint probability isN_good dividedby `(q^m-1)*D_(m,k)`. This is a finite dimension-k coefficient sum with explicitm dependence; not a tautological header sum. A(L) can itself be found by coordinate inclusion-exclusion, or as a full-support linear-code weight count. It depends on the space, not merely its dimension for oddfields.

Checks by hand: k1 gives marginal `(q-1)*(q^2-q+1)^(m-1)/[(q^m-1)q^(m-1)]`. k2 gives numerator `(q-1)*[(q^2+(q-1)^3)^(m-1)-(q+(q-1)^2)^(m-1)]` with the statedDdenominator. Forq2, A(L)=1 for every L containing1, recovering a Gaussian-binomial grouped sum, matching the shape of6701's law.

Atq3,k3,m3, U=0 contributesbase43; the fourrelation lines contribute threebases17 andonebase13; thefullrelationplane contributesmu3/base7. HenceN_good=`2*(43^2-3*17^2-13^2+3*7^2)=1920`; denominatorGL3(3)=11232, giving20/117. This is a hand-predicted calibration value, NOTa program output/new count. Collapsing allfourlines to the samefullsupport count4 would predict1680, demonstratingwhy dimension-only collapse needs checking. All these are provisional until independently reviewed and compared with actual6710 source; no theorem/census/physical admission is asserted from this sketch.
