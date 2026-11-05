# Adversarial written audit of the common-image count law

## Verdict, reviewed statement and exposure

PASS for the orbit/denominator, all-proper-prefix predicate, span-contained count and subspace Möbius law in the first count-law sections of SHIN09-git PR6710. No material gap or source counterexample was found under the finite-field/complete-uniform-header contract. The original theorem and every reported count remain source work. This is external source-aware AI review, not discovery, blind/human review or a formal-kernel result.

Source head:465a0060fbd236a5e202619de4a45a694d44970a, with the byte-verified retained PROOF.md/README.md/NOTICE/source/LICENSE supplied in this package. The source PROOF was read before deriving this note. An initial overbroad inert `cat` returned the full PROOF and README, so later pencil, sign, affine-flat, determinant-stratum and evidence summaries were visible. This exposure is disclosed, but none of those later claims is audited or accepted here. No peer or coordinator derivation was read before this note's seal. No scientific program, finite census, constructor, source code, mutant, import, compilation, numerical experiment or proof kernel was run. Only prose and provenance byte/hash/time operations were read/performed.

Fix a finite field K of prime-power order q, m>=2, a nonzero fixed u in K^m, and a nonempty fixed list of k rows v_i with v_i*u=1. Let V:K^m→K^k be their matrix, S=im(V), r=dim(S), and t=(1,...,1)=V*u. Then 1<=r<=min(k,m), and t is nonzero. Rows may repeat and k may exceed m. G is uniform on the COMPLETE GL_m(K), with the tuple fixed before selecting G. For each i every leading minor of orders1 through m-1 of G(I-u*v_i)G^-1 must be nonzero. The full order-m determinant is zero and is not included in the passing predicate.

This note does not review positivity/independence comparisons, special pencils/flats, named pass masks, asymptotics, determinant strata, literal census/certificate numbers, source21mutants or dimensional sign windows. Prior6701/6703 and classical finite-field/subspace methods retain their exact credited scope.

## 1. Orbit: fixed vector, not merely its line

A transformed pair is `(u',V')=(G*u,V*G^-1)`. It has im(V')=S and V'*u'=t. Conversely take any such pair. Choose the same ordered basis of S beginning with t. For the original map, use u as the lift of that first basis vector, choose lifts of the remaining r-1 basis vectors, and append a basis of ker(V). These m vectors form a basis: their first r images form a basis of S, and the rest form the kernel. Do the same for the new pair, beginning with u'.

If F and F' are the two domain basis matrices, G=F'*F^-1 sends u to u' and satisfies V'*G=V, hence V'=V*G^-1. This proves transitivity on exactly the asserted pair space, including dependent/repeated rows. No independence of the k individual rows was inserted.

In adapted coordinates u=e1 and V is the coordinate inclusion of `[I_r,0]` into S. The stabilizer satisfies G*u=u and V*G=V. Its top r rows are therefore `[I_r,0]`, and it has blocks

    G = [ I_r  0 ; T  H ],

with H invertible and T's first column zero. This gives exactly q^((r-1)(m-r))*|GL_(m-r)(K)| elements. When m=r the kernel is0 and |GL_0|=1; no nonempty-kernel assumption is needed. Uniform headers consequently induce uniform pairs with this constant fiber.

There is no extra q-1 stabilizer factor here: u is fixed as a VECTOR. For α!=0, pairs `(αu',α^-1 V')` represent the same ordered rank-one operator tuple, but they are distinct pairs in this orbit count. Conversely the nonzero operators determine their common line, and each of its q-1 vector choices uniquely determines all rows, so an operator-tuple quotient would divide BOTH passing-pair and all-pair counts by q-1. The source consistently counts before this quotient. Rescaling only one count would be wrong over q>2, although binary tests would not expose it.

## 2. Denominator and boundary cases

For each of q^m-1 possible nonzero u', use an auxiliary domain basis with u' last. This is legitimate for counting all maps with V'*u'=t and image S. It does not preserve the leading flag and must not be used to simplify the passing event.

Write d=m-1 and choose coordinates of S beginning with t. The final column is t. Among the first d columns their coefficient along t is arbitrary (q^d choices), while the remaining r-1 coefficient rows must be independent in K^d. There are

    product_(i=0..r-2) (q^d-q^i)

choices for those rows. Thus

    D_r=(q^m-1)*q^d*product_(i=0..r-2)(q^d-q^i).

This is the complete pair-orbit denominator. At r=1 the product is empty and equals1. At r=m, there are exactly d lower rows, and the last factor is q^d-q^(d-1), not zero; the count agrees with the free pair action. At k>m or with repeated rows, r remains the true map rank and never becomes k by fiat.

S is the actual embedded COLUMN IMAGE in K^k, not merely an abstract r-dimensional space or the row span in K^m. The denominator depends only on r, but the numerator's coordinate-wise guard constraints retain that embedding through h(L). An arbitrary output-coordinate basis change need not preserve the event. This prevents an unsupported claim that the full probability depends on rank alone.

## 3. The exact prefix predicate and the forced final coordinate

For a pair in the original fixed coordinate order let c_a be column a of V', and put

    y_j=sum_(a<=j) u'_a*c_a.

The leading j×j block of the i-th conjugated complement is the identity minus one column times one row. The determinant lemma gives `1-(y_j)_i`. It is valid in all characteristics; the characteristic-two sign convention does not introduce an exception. The passing set for proper prefixes is therefore

    A_S={y in S: every coordinate y_i differs from1}.

Initially y0=0 is allowed. Finally y_m=t because V'*u'=t. If u'_m=0 then y_(m-1)=t and every last proper determinant is0, impossible on the joint event. Hence every passing pair has u'_m!=0. This uses the order m-1 guard; testing only a shorter prefix would not establish it. Conversely u'_m!=0 alone is not sufficient: all previous prefixes still have to lie in A_S.

This is a condition on the actual fixed coordinate flag. The auxiliary basis change in the denominator cannot be applied to the event to pretend u' always lies on the last axis.

## 4. Span-contained count: free zero-coefficient columns are essential

Fix any L with `<t> <= L <= S`, and put ell=dim(L). For a proper position, suppose the current allowed prefix y lies in L.

- If u'_a=0, the prefix stays y, and the column c_a may be ANY of q^ell elements of L. These columns need not vanish; they can be needed to make the actual image rank r.
- For a fixed nonzero u'_a, choose any next allowed prefix z in L. The column is uniquely `(z-y)/u'_a`, still in L. Because t belongs to L, the bijection z↦t-z takes the allowed prefixes precisely to full-support vectors of L. Their number is h(L). There are q-1 possible nonzero u'_a.

Thus every allowed current prefix has exactly

    lambda(L)=q^ell+(q-1)*h(L)

choices of coefficient and next column that keep it allowed. Starting from the one fixed allowed prefix0, d proper positions give lambda(L)^d choices. No additional initial h(L) factor belongs here.

At the final position, u'_m has q-1 nonzero choices and the required column is uniquely `(t-y_d)/u'_m` in L. Therefore

    F(L)=(q-1)*lambda(L)^d

counts exactly the passing pairs whose column span is CONTAINED in L. It does not impose surjectivity onto L or S. Every counted pair is nonzero in u' and has V'*u'=t, so its actual column span M automatically contains t. Conversely every passing tuple with span contained in L is represented once by this chronological choice process. There is no extra independent choice of final column or final prefix.

The q-1 factor is the actual last-coordinate choice, not a line normalization that was already divided out of the denominator. Zero choices at proper positions, nonzero choices at the last position, and rank pruning are different operations; conflating them changes the formula.

## 5. Möbius inversion recovers precisely the rank-r orbit numerator

For each intermediate M containing t, let N(M) count passing pairs with column span exactly M. The preceding construction gives, for every L in this interval,

    F(L)=sum_(<t> <= M <= L) N(M).

Inverting this finite subspace interval yields

    N(S)=(q-1)*sum_(<t> <= L <= S) mu(L,S)*lambda(L)^d,
    mu(L,S)=(-1)^c*q^(c(c-1)/2), c=r-dim(L).

The interval between L and S is the ordinary subspace lattice of S/L, so this is the classical coefficient of codimension c; restricting the global bottom to<t> does not change that local interval. The source's Gaussian-binomial product identity supplies the required zero sum at positive quotient dimensions, with mu(S,S)=1. This is not integer inclusion-exclusion over coordinate subsets or the Boolean coefficient(-1)^c alone.

N(S) now imposes the exact image S required for membership of the pair orbit. Dividing by D_r therefore gives the exact source joint law under complete uniform GL_m. It is not valid to divide F(S) directly by D_r, since F(S) includes lower-rank tuples. No further independence hypothesis on rows is needed. The interval must contain t: a subspace omitting t cannot be an actual image of a pair with V'*u'=t, and the translation argument for h(L) would fail there.

## 6. Written adversarial controls — UNEXECUTED

1. **Gauge/fiber normalization.** Over a field with q>2, change representation to `(αu,α^-1V)` for all q-1 nonzero α. The event and ordered rank-one operators are unchanged. Dividing only the denominator, or adding q-1 to the fixed-vector stabilizer while leaving the numerator untouched, changes the probability spuriously. Binary-only checks cannot discriminate that mistake.
2. **Auxiliary basis versus actual flag.** With u=e1 and v=e1^T, the identity header fails the first minor. One can choose an auxiliary basis sending u last for denominator counting, but using that re-coordination to declare the original header a pass loses the leading-flag predicate.
3. **Keep the last proper prefix.** In m=3 take u'=e2 and rows v1'=e2^T, v2'=e2^T+e3^T. Both normalize to1. The first prefix is0, but the second (last proper) prefix is t, so the event fails. Omitting the last proper minor would incorrectly allow u'_m=0. Conversely m=2,u'=(1,1),v'=(1,0) shows nonzero last coordinate alone does not ensure passing.
4. **Zero u does not mean zero column.** In m=2 with k=r=2, let u'=(0,1), c1=(1,0), c2=t=(1,1). This pair has full column span and its sole proper prefix is0, so it passes. Pruning c1 just because u'_1=0 loses a valid full-rank tuple. These coordinates are valid over any field.
5. **Contained versus exact span.** In an auxiliary target S of rank2, the passing pair u'=(0,1),c1=0,c2=t has actual image<t>. It belongs in F(S) and F(<t>), but not in N(S) or the rank2 header orbit. Requiring full rank while forming F, or using F(S) directly as the orbit numerator, breaks inversion in opposite ways.
6. **Correct interval and coefficient.** If zero space is incorrectly included, substituting ell=0,h=0 into the displayed contained formula gives q-1, even though no zero-image pair can send u' to nonzero t. The hypothesis<t> subset L is essential. At codimension2 the correct Möbius coefficient is q, not the Boolean-lattice1.
7. **Repeated/dependent rows and boundaries.** Repeat one normalized row arbitrarily many times, including k>m. The event is unchanged, r=1, S=<t> and the denominator uses the empty product1. Replacing r by k could give impossible or zero factors. Separately, m=r has GL0=1 and a positive full-row-rank product, not an undefined empty-kernel case.
8. **Header and field domain.** Choosing rows after observing G, restricting the header distribution arbitrarily or replacing the finite field by a nonfield ring removes an actual premise. Such variants are not source counterexamples. Characteristic2, row repeats and prime-power extension fields remain inside the reviewed law.

These are hand deductions about altered claims, not observed mutant outcomes, finite-census counts or executions of the source's controls. No scientific computation was used to manufacture a counterexample or establish the displayed source probability.

## Conclusion and remaining scope

The source's orbit normalization, denominator, allowed-prefix transition count and subspace inversion are consistent for every valid m,r,k,q in its contract. No code or theorem correction is requested. The result audits the count law only. It does not independently establish the source's sign, triple/pencil/full-flat/determinant-stratum claims, census entries, implementation, new21controls or dimensional windows, nor any caller/native price or selected framework obligation.

Credit remains SHIN09-git/PR6710 for the complete count law and its broader results; ToikY6701/6703 for the credited binary-family/pair-sign predecessors; Nick Petalas4227/4807 for marginal/pair methods and associated source lineage. Orbit-stabilizer, rank-one determinants, independent-row counting and subspace-lattice Möbius inversion are classical; the source cites Rota. This external note was prepared with substantial OpenAI Codex assistance. No human/kernel acceptance, new positivity theorem, physical supplier, κ/frontier or adoption change follows.
