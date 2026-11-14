# Independent continuous-box certificate and lead proof review

Reviewed PROOF.md SHA25603da374ebde2644b883b2398e80112989719c2a0edb7394cc43b2abd26fa447c. The lead independently expanded all24 determinants and checked the legal source selector, class inequalities, inverse Schur determinant identity, entry-to-norm factors, precision guards and matched periodization tail. The production-domain contradiction concerns only the named theorem.

## Separate continuous certificate

check_bernstein.py uses Python integer/Fraction arithmetic and imports no author code. It constructs tensor entries as four-variable monomials, forms the ordinary displacement and expands each determinant. It substitutes v=w*V and y=w*Y, removes the least power w^k and its limiting sign, and checks the resulting polynomial on u,x in[1023/1024,1], V,Y in[1,2], w in[0,1/2048].

An affine interval map gives a polynomial on[0,1]. For degree d, the identity x^i=sum_(k=i..d) binom(k,i)/binom(d,i) * binom(d,k)*x^k*(1-x)^(d-k) converts power coefficients to Bernstein coefficients; it follows from the binomial theorem after factoring x^i. The tensor-product Bernstein basis is nonnegative and sums to1. Thus a lower bound on every coefficient bounds the polynomial on the entire box.

All19992 exact coefficients are at least586270984563189354495/590295810358705651712, greater than1/4. Eight orders have each k=0,1,2. Therefore all determinants have absolute value at least w^k/4 and hence w^2/4 for0<w<=1/2048, stronger than the main proof needs. The w=0 endpoint is used only after polynomial division. This is a continuous certificate, not sampled parameter evidence or an external formal proof kernel. Normal/optimized receipts agree.

## Source and quantitative checks

The exact extremal exponents A=2delta+1,B=2s-1 give a nonwrapping pair. A>4 and4A+4<s establish the optional degree-four injection. For p>=4096 the retained alpha gives4ln(16p)<=a<=9ln(16p), putting the entries inside the certified box. Factor error2^-34 w^2, matrix error2^-32 w^2, inverse perturbation4096 times the matrix error, and separate inverse-entry error2^-23 w^2 include all dimension factors. The periodic tail4exp(-a t^2/8) fits the explicit two-bit allowance. Selected inverses are not sections of larger inverses.

## Controls and exclusions

The checker confirms the equal symmetric Gray counterexample outside this box and rejects a corrupted sign. It also symbolically proves the exact g3 duplicate-column obstruction: H=[[1,1],[w,1]] tensor cubed, order(0,1,2,4,3,6,7,5), columns2 and5 of the displacement both(1,w-1,0,0,0,0,0,0). This blocks unchanged full-rank tensorization of the box lemma, not the actual distinct-prime source family. The discovery finite-field screen is not used as its proof.

Coefficient construction and physical admission remain separate. All five assumptions and kappa remain unchanged. C's complementary proof/source review is in CROSS-REVIEW.md; it is distinct from the exact certificate and not a second replay of the same implementation.
