# A support–width dichotomy for native tensor programs

**Status:** local written derivation with exact finite calibration; no independent human or formal-kernel review. No new κ or admitted supplier. The classical tensor-independence theorem is credited below. The proposed contribution is its pointwise, operator-coefficient use to remove a fixed-product-set hypothesis from a concrete native-control obstruction, with explicit support bounds and matching escape examples.

## 1. Pointwise semantic completeness with moving support

Let K be a field, V a finite-dimensional K-vector space, and f a positive integer. At this particular width choose nonzero, pairwise nonproportional vectors

`v_1(f), …, v_m(f)`, spanning dimension `r(f)`.

Both the vectors and their number may change at the next width. Let W_f be any K-vector space of coefficients, also allowed to change with f. If

`f >= m(f) − r(f) + 1`,

then

`Σ_i B_i(f) ⊗ v_i(f)^⊗f = 0  =>  B_i(f) = 0 for every i`,

for arbitrary coefficients B_i(f) in W_f. In particular, the dimension-free sufficient condition is `m(f) <= f+1` when m>=2; m=1 needs only f>=1. For native operators take V=Hom(X,Y), with the usual regrouping of Hom(X,Y)^⊗f as Hom(X^⊗f,Y^⊗f).

**Proof and constructive certificate.** Fix an index i. Extend v_i to a basis of the span using r−1 other vectors from the list. A linear functional L_0 can be chosen to take value 1 on v_i and zero on those r−1 vectors. For each of the remaining m−r vectors v_j, pairwise nonproportionality gives a functional L_j taking value 1 on v_i and zero on v_j. The product of these m−r+1 functionals, evaluated on tensor factors, is 1 on v_i^⊗(m−r+1) and zero on every other listed tensor power. Pad with copies of L_0 to obtain f factors. Applying this functional to the V tensor factors in the displayed identity returns B_i=0. Repeat for every i. This works over every field and does not require an inner product.

There is no compactness or limit argument: the proof works separately at each width. It therefore allows arbitrary width-dependent matrices, phases, scalar coefficients and auxiliary coefficient spaces. A fixed finite generating alphabet or a fixed set of complete products is unnecessary for this **exact** conclusion. What matters is the support/rank bound at that width.

Proportional vectors must first be merged correctly. If A_i=λA_j then A_i^⊗f=λ^f A_j^⊗f; its contribution is combined using λ^f, not λ. Zero vectors disappear. Equality of two expansions is tested on their combined projective support, not on each side's support separately.

**Classical attribution.** The scalar sufficient bound m<=f+r−1 and its optimality using only m,r are already in Anthony Chefles, [Unambiguous Discrimination Between Linearly Dependent States With Multiple Copies](https://arxiv.org/abs/quant-ph/0105016), Section II, especially Eq. (2.3). The repository's retained predecessor proof also gives the m−1 bound by separating functionals. Neither bound is claimed new. The coefficient-space extension follows directly by applying the same functionals.

## 2. Why workspace and feedback do not by themselves defeat the test

Consider a linear program whose endpoint has a declared expansion

`P_f = Σ_i B_i(f) ⊗ A_i(f)^⊗f`.

The coefficient B_i may be a rectangular register matrix or an operator on a separate auxiliary space. It need not commute with the other coefficients. Intermediate feedback and auxiliary register counts are unrestricted by the theorem; the final expansion and its support/rank are the hypotheses. Taking a subblock corresponding to an original input/output pair cannot increase its support count. Thus borrowed or owned auxiliary state cannot create an unrepresented native letter while the endpoint remains inside the separation bound.

This is **not** a bound on how cheaply a program can generate a large expansion. Auxiliary computation may increase the number of terms, and cross-column address operations may fail to have the displayed form. A supplied nonfree observation changes the input operator being represented. These are changes to hypotheses, not contradictions of the theorem. No arbitrary independent input may be replaced by zero merely to obtain a smaller expansion.

## 3. A general four-control obstruction without fixed operator sets

We now give a complete algebraic statement for the released coded-source interface. All objects below are finite one-column matrices over C; `T_f` denotes T^⊗f for address matrices. Scalar owner coefficients remain outside tensor powers.

The one-column address space has computational basis indexed by

`F2 q ⊕ U ⊕ W`.

Q is invertible, and both Q and Q^-1 have nonzero entries exactly inside complete q-coset blocks. D is invertible and has nonzero entries exactly inside complete W-coset blocks. In particular D and D^-1 act inside the join blocks q+W.

There are n original owners. Let A be an invertible n-by-n scalar matrix with zero diagonal. Let K1_j and K3_i be invertible weighted monomial maps whose underlying permutations are linear. K1 acts only on q+U, K3 only on q+W. Write their binary maps as G1_j,G3_i, and suppose the n vectors `G1_j q` are pairwise distinct.

Define two source code matrices by their owner blocks:

`(C1_f)_{s,j} = A_{s,j}(K1_s^-1 K1_j)_f`,

`(C3_f)_{i,r} = A_{i,r}(K3_i^-1 K3_r)_f`.

Both are invertible: each is an address-block-diagonal conjugate of `A ⊗ I`.

Let `T0_f` be an n-owner operator and set

`T_f = (I⊗D_f) T0_f (I⊗D_f^-1)`,

`E_f = (I⊗Q_f^-1) C3_f T_f C1_f (I⊗Q_f^-1)`.

Suppose every owner block of each of the following four controls is a scalar sum of tensor powers of invertible one-column weighted monomial maps:

1. T0_f, with at most s0 terms per block;
2. `(I⊗Q_f^-1) T0_f (I⊗Q_f)`, with at most sQ terms per block;
3. T_f, with at most sD terms per block;
4. E_f, with at most sE terms per block.

The maps, nonlinear permutations, nonzero weights and coefficients may all depend arbitrarily on f. The supports need not come from a fixed alphabet. Counts may be taken before projective merging, giving conservative upper bounds. The coefficients can also be operators on a separate auxiliary space on which the displayed source address maps act as identity: Section 1 applies with that operator space as W_f, and the source multiplications below are scalar on coefficients. This does not permit cross-column entangling maps that lack the declared expansion.

Put

`R = max_i #{r : A_ir != 0}`,

`C = max_j #{s : A_sj != 0}`,

`M = max(s0+sQ, s0+sD, R C s0+sE)`.

**Theorem.** If `f >= max(1,M−1)`, these four memberships force `T0_f=0`. Therefore there is no invertible control at any width satisfying that bound. More generally, each comparison can use its actual projective union size m and span rank r, replacing m−1 by m−r+1.

**Proof, first reduction.** Apply Section 1 to each owner block of T0 and its Q conjugate, on the union of their expansions. Conjugation is projectively injective, so each surviving monomial letter h of T0 must itself satisfy `Q^-1 h Q` monomial. Do the same for its D conjugate. Every surviving h therefore has `k=D h D^-1` monomial as well. The relevant unions have sizes at most s0+sQ and s0+sD. This reduction is pointwise and holds even when the letters change with f.

**Support-partition lemma.** If F is fully supported inside complete blocks of an equal-size partition, and h,k are invertible monomial maps with Fh=kF, then the permutations of h and k send partition blocks bijectively to blocks with the same induced map. Indeed, the support of Fh applied to a basis vector is one entire block; the support of kF is the image of an entire block. Monomial weights are nonzero, so neither side can cancel within that support. The same reasoning applies to `a F_in = F_out b`, with two different complete block partitions.

Apply this lemma to `hQ=Q(Q^-1hQ)` and `Dh=kD`. It follows that h preserves q-cosets and W-cosets. It preserves their join, the q+W-cosets. Because D and D^-1 act inside join blocks, the monomial k also maps join blocks bijectively. In particular, k cannot send a pair from different join blocks to a pair in one join block. No assertion that k preserves q-cosets is needed.

**Terminal source terms.** A term of owner block (i,j) of E has one-column address operator

`Q^-1 a k b Q^-1`,

where `a=K3_i^-1 K3_r`, `b=K1_s^-1 K1_j`, and its scalar coefficient contains `A_ir A_sj`.

If this operator were monomial m, then `a k b Q^-1=Qm`. The two-sided support lemma makes a k b carry q-cosets to q-cosets. Hence k carries pairs in direction

`v=G1_s^-1 G1_j q ∈ F2 q ⊕ U`

to pairs in direction

`w=G3_r^-1 G3_i q ∈ F2 q ⊕ W`.

If v has a nonzero U component, its pair lies in different join blocks, whereas the w-pair lies in one join block. This contradicts the join permutation of k. Thus v=q. Distinctness of the G1_j q then gives s=j, making A_sj=0. Consequently **every terminal source term with nonzero scalar coefficient is nonmonomial**.

There are at most R C s0 terminal terms in each owner block. Compare that expansion with its declared monomial E expansion, using Section 1 on a union of at most R C s0+sE projective classes. Nonmonomial classes cannot merge with monomial classes. Independence forces every coefficient on both classes to vanish, so E_f=0. Invertibility of Q,C3,C1,D gives T0_f=0. This completes the proof.

## 4. Source consequence: a linear-support escape requirement

The retained coded-source data have n=112 and exactly 52 nonzero entries in every row and column of A. The exact calibration checks all 12,544 entries against `A=I−MM^T/4`, checks `M^T M=56I`, verifies the zero diagonal and distinct normalized port directions, and hence verifies the scalar identity `A²+12A=13I` and invertibility. It does not replay the original native producer or its physical normalizer engine.

With the explicitly stated coset/columnwise source contract above, R C=2704. If all four controls have at most s(f) terms per owner block, then

`2705 s(f) <= f+1  =>  T0_f=0`.

Thus any nonzero all-width control family in this exact interface must have

`s(f) > (f+1)/2705`

at every positive width. In particular **every sublinear-support family is excluded**, even with width-dependent nonlinear weighted monomial words of unbounded length, arbitrary changing coefficients, and arbitrarily many auxiliary registers whose extracted endpoints meet the stated support counts.

The denominator 2705 is a sufficient expansion bound, not an optimal native lower bound. Actual projective unions, cancellations, owner sparsity and span ranks may improve it. The theorem is a support lower bound, not a lower bound on paid Gaussian calls, scalar instructions, physical running time or precision. Producing linearly many terms may be cheap in another ABI. Changed codes, observations, paid calls, noncolumnwise maps or productive endpoints remain outside this four-control conclusion.

This extends the inspected predecessor's fixed finite complete-product-set theorem. Its support-partition argument and source credit are retained. The new quantifier is pointwise in f; a **cardinality bound** replaces a fixed set of operator values. The original m−1 tensor lemma was already strong enough for this step, so the underlying separation method is not new.

## 5. The exact support threshold is sharp, including unitary monomials

Let `α=(3+4i)/5` and `D=diag(1,α)`. This is a Gaussian-rational unitary monomial matrix. α has infinite multiplicative order: roots of unity in Q(i) are ±1 and ±i, and α is none of these.

At width f, D_f has distinct eigenvalues `1,α,…,α^f`, according to Hamming weight. Therefore its minimal polynomial is

`p_f(z)=∏_{k=0}^f (z−α^k)=Σ_{j=0}^{f+1} c_j(f) z^j`.

It follows that

`Σ_{j=0}^{f+1} c_j(f) (D^j)^⊗f = 0`.

There are f+2 pairwise projectively distinct invertible unitary monomial letters, all powers of **one fixed generator**. Each coefficient is nonzero: a zero coefficient would give a dependence among at most f+1 projectively distinct tensor powers, contradicting Section 1. The one-column vectors span dimension two, so the identity sits exactly one term beyond the sharp universal bound. It proves that the support barrier cannot be extended merely by asserting that the alphabet, unitarity or one-column dimension is fixed.

The coefficients have Gaussian-rational bit length O(f²). Put S=f(f+1)/2. Their real and imaginary denominators divide 5^S, while after scaling by 5^S each component numerator has absolute value at most `2^(f+1)5^S`: every elementary-symmetric summand has modulus one and there are at most 2^(f+1) summands. Sequential polynomial multiplication constructs the coefficient list with O(f²) exact arithmetic operations on polynomial-size rational integers. This is an algebraic construction, not a priced physical recoding or a useful supplier.

The sharper r-dependent scalar bound is optimal as well: put f+2 distinct projective points in a two-dimensional subspace, then add r−2 independent coordinate directions. There are m=f+r points spanning rank r, with a dependence among their f-fold tensor powers. No theorem using only m,r,f can guarantee independence beyond the stated cutoff.

## 6. Exact rigidity and approximate rigidity have different hypotheses

For one-column unitaries U_i of size d, put

`g_ij = tr(U_i* U_j)/d`, `ρ=max_{i!=j}|g_ij|`.

For arbitrary n-by-n coefficient matrices B_i, the normalized Frobenius square of `Σ B_i⊗U_i^⊗f` equals the coefficient Gram form with entries g_ij^f. The Gram diagonal is one. Gershgorin therefore gives

`||Σ B_i⊗U_i^⊗f||_op² >= [1−(m−1)ρ^f] Σ ||B_i||_F² / n`

whenever the bracket is positive. This is an explicit sufficient robust bound, including moving alphabets when their actual ρ(f) is supplied. It can be checked with a small Gram matrix instead of constructing the tensor operator. A negative bracket makes the bound uninformative; it does not refute exact independence.

Without separation control, even **two** changing unitary monomial terms can approach cancellation. Set t=f², `β_f=(t+i)/(t−i)`, and `U(f)=diag(1,β_f)`. Then U(f) is nontrivial, Gaussian-rational and unitary, but

`0 < ||U(f)^⊗f−I||_op <= f|β_f−1| <= 2/f`.

The telescoping tensor expansion proves the upper bound. Exact independence still holds. Consequently the exact obstruction does not automatically exclude approximate decoding or rounding-based recovery. Those routes require conditioning and precision bounds for the actual consumer. This is a productive limit of the theorem, not an admitted approximation algorithm.

## 7. Credit and remaining obligations

The classical scalar bound is Chefles' result. The repository's retained tensor-separation, phase-quotient and support-partition proofs retain [Chris R](https://github.com/Clear1nsight), [Ali Romman](https://github.com/aliromman), [Dillon Amburgey](https://github.com/dillona), [Dugongue](https://github.com/Dugongue), [Cinna Davis](https://github.com/1337isnot1337), [Cao Yifan](https://github.com/intqwq), [zxv](https://github.com/zxv), [Jacob Alan Sussman](https://github.com/Mister-Meeseeks) and their source-specific predecessor notices. Exact local sources and hashes are in SOURCES.json. The primary new result is the moving-support native corollary and explicit growth/escape boundary; no global literature priority is asserted.

The proof needs independent mathematical review, especially the support-count quantifiers, extracted auxiliary-state semantics and source-interface application. The finite checker calibrates the algebra and source excerpts. It does not prove the universal theorem by testing, validate all 17-axis phases, or discharge the selected compiler/tape/recovery assumptions. New prose and checking code are Apache-2.0 with substantial OpenAI Codex assistance.
