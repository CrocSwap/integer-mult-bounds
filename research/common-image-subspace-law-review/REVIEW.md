# Review verdict and exact count-law boundary

**No gap found in PR6710's normalized tuple orbit, safe-prefix count or subspace-inversion joint law under its stated hypotheses.** This is an external written verification of SHIN09-git's existing theorem. It adds no new all-field formula, sign classification or finite census. The full target-known derivation is [reviews/DERIVATION.md](reviews/DERIVATION.md), with a separate source-aware [adversarial review](reviews/ADVERSARIAL.md). Their first drafts are sealed before cross-reading; their different source exposures are disclosed.

The exact reviewed source is head `465a0060fbd236a5e202619de4a45a694d44970a`, PROOF blob `e67bc62fc5efa61b2a184ea176c64861906b71a1`. Coverage is the first count-law sections only: orbit/denominator and which tuples pass, through the general inversion formula and its Möbius justification. Source code, finite fixtures and every later sign/pencil/flat/triple/stratum theorem are outside this review.

## Quantified statement

Let `K=F_q`, with q a prime power, `m>=2`, `k>=1`, and `u!=0` in `K^m`. Fix a k-by-m matrix V with `Vu=t=(1,...,1)`, coordinate image `S=im(V)` and rank `1<=r<=m`. Rows may repeat or be dependent, and k may exceed m. Let G be uniform on complete `GL_m(K)`, independently of the fixed family. Every event requires all leading principal minors of orders1 throughm-1 of `G(I-u*v_i)G^-1` to be nonzero; the identically zero full determinant is excluded.

For `<t> <= L <= S`, define `h(L)` as the number of vectors with every coordinate nonzero, `lambda(L)=q^dim(L)+(q-1)h(L)`, and `mu(L,S)=(-1)^c q^(c(c-1)/2)` where `c=r-dim(L)`. With

`D_r=(q^m-1)q^(m-1) product_(i=0..r-2)(q^(m-1)-q^i)`,

the source law is

`J_S=(q-1) sum_(<t><=L<=S) mu(L,S) lambda(L)^(m-1) / D_r`.

Empty products equal one. S is the actual embedded image in `K^k`, not merely its dimension. Coordinate support retains the guard-family geometry.

## Why the denominator and measure are correct

Headers act on tuples by `(u,V)->(G*u,V*G^-1)`, preserving image S and endpoint t. To compare any two such tuples, fix a basis of S beginning with t, lift t by the designated nonzero u, lift its other basis vectors, and append a kernel basis. The resulting adapted domain bases give an invertible map between the tuples. Thus the action is transitive and every tuple has a constant header fiber.

In adapted coordinates, a stabilizer has blocks `[I_r,0;A,H]`, with `H in GL_(m-r)` and the first column of A zero. Its size is `q^((r-1)(m-r))*|GL_(m-r)|`, including `|GL_0|=1`. For any fixed nonzero u, use a domain basis with u last to count maps: the last image column is fixed t; the other m-1 columns have arbitrary t-components and must span the r-1 dimensional quotient `S/<t>`. This gives the stated D_r after multiplying by `q^m-1` choices of u.

That auxiliary basis change is used **only to count the unconditional denominator**. It does not preserve the physical leading flag and cannot be applied to turn an arbitrary header into a passing one. The guard count below stays in the original coordinate order.

The tuple fixes an image vector, not just its line. Simultaneously scaling u by alpha and V by alpha^-1 gives q-1 representations of the same operator list; a projective quotient would have to divide both numerator and denominator. The final q-1 factor below is an actual terminal-coordinate choice, not an extra projective correction. Binary examples alone cannot detect that normalization error.

## Safe prefixes and contained span

For a transformed tuple `(x,W)`, let c_a be column a of W and `y_j=sum_(a<=j)x_a*c_a`. The determinant lemma gives each required minor as `1-(y_j)_i`. Consequently all proper prefixes must avoid one in every coordinate, while `y_m=t`. In particular `x_m!=0`: otherwise the last proper prefix would already equal t and fail. This condition alone is not sufficient; all earlier guards still apply.

Fix an intermediate L containing t and temporarily require only that every column lies in L. The allowed prefix set is `A_L={y in L:y_i!=1 for every i}`. Translation `y->t-y` bijects it with full-support vectors, so `|A_L|=h(L)`. It contains0 and excludes t.

At any proper position, a zero coefficient x_a leaves the prefix unchanged but allows **all** `q^dim(L)` columns. Such columns can later supply needed rank and must not be pruned. For each of q-1 nonzero coefficients, each allowed next prefix determines exactly one column. Every allowed current prefix therefore has lambda(L) continuations. Starting at the single fixed prefix0 gives `lambda(L)^(m-1)` choices. At the last position, t minus the preceding allowed prefix is nonzero, so it has exactly q-1 coefficient/column factorizations. Thus

`F(L)=(q-1)lambda(L)^(m-1)`

counts passing tuples with image **contained** in L. It has not imposed full rank. There is no extra h(L) initial-state factor and no extra independent final-column choice.

## Exact image and the inversion

Let H(M) count passing tuples with image exactly M. The endpoint forces `<t> <= M`; each matrix has a unique image. Hence `F(L)=sum_(<t><=M<=L)H(M)`. Inverting this finite subspace interval gives the numerator H(S). The interval from L to S is the ordinary subspace lattice of `S/L`, so its Möbius coefficient is the displayed codimension coefficient, including q rather than one at codimension two.

The independent derivation proves that coefficient from the Gaussian-binomial recurrence and the polynomial product `product_(i=0..c-1)(1-q^i*z)`. At z=1 its positive-dimensional sum is zero, with coefficient one in dimension zero, establishing the interval recursion. No finite census or Boolean-lattice substitution is used.

Dividing H(S) by the uniform tuple-orbit size D_r proves the source probability. Dividing F(S) directly would include lower-rank tuples; demanding exact rank while forming every F(L) would break the contained-span decomposition. The law handles all dependencies, not just equal pairs, and does not replace r by the number k of listed rows.

## Independent-row comparison and written calibrations

Before reading the actual6710 proof/code, the coordinator sealed an exploratory independent-row specialization; it already knew related6701/6703/4807 work and had seen6710's body. The [sketch](reviews/PRE-SOURCE-SKETCH.md) and [seal](reviews/PRE-SOURCE-SEAL.json) record that preclaim chronology honestly. It was a feasibility derivation, not a new theorem claim or a blind proof. Overlap had already identified6710 as the predecessor.

For independent rows, `S=K^k`. Reversing subspaces by `L=U^perp`, with `U<=t^perp`, takes the sketch's relation-space inversion to the exact source interval. Its coefficient and full-support count become the same mu and h(L). Replacing the exploratory inverse-header convention by G is a bijective change of the complete uniform header, with both vector and row actions transformed together.

The following are hand deductions, **not executed finite checks or new count claims**:

- At r=1 all normalized rows coincide, including arbitrarily many repetitions. The sole L is `<t>`, `h=q-1`, and the law is the known marginal; repeating an event cannot raise its probability to a power.
- For independent k=2 the sum has only the full space and t-line. Their bases are `q^2+(q-1)^3` and `q+(q-1)^2`, recovering the credited pair law. At q=2, every allowed L has the unique full-support vector t, recovering the binary family law.
- For q=3,m=k=r=3 there are four planes through t. Three impose equality of a coordinate pair and have four full-support vectors each; the fourth is `x_1+x_2+x_3=0`, whose only full-support vectors are111 and222. The full space has eight, and the t-line has two. Thus their bases are43, three17s,13 and7; the line's Möbius coefficient is3. The predicted numerator is `2*(43^2-3*17^2-13^2+3*7^2)=1920`, denominator `(27-1)(27-3)(27-9)=11232`, ratio20/117. Treating all four intermediate planes as equal by dimension would instead give1680. This illustrates why embedded support data matters, even at fixed dimension; it is not a new header census.

The q=3 example also allows characteristic to divide the list length. No direct-sum assumption between t and its orthogonal hyperplane is used. The general law itself uses the span interval and needs no chosen orthogonal complement.

## Review controls and remaining obligations

Eight adversarial written controls cover unmatched gauge quotients, confusing a denominator basis with a flag-preserving change, omitted last proper guards, pruning free columns at zero coefficients, contained/exact span confusion, a wrong interval or Möbius factor, repeated rows/k>m and changed header/field domains. They are unexecuted deductions about altered premises, not actual outcomes of the source's21 mutants.

No theorem or source-code correction is requested. This review does not validate implementation/censuses or the source's later sign, pencil/flat, asymptotic, triple or determinant-stratum arguments. Original formal-interface/kernel acceptance remains unmet under changed written-review scope. Physical header generation/selection/emission/ownership/restoration/stock/precision/full costs and all selected framework assumptions remain separate. No physical supplier, multiplication bound, κ/frontier/adoption change or merge follows. Source6710 and all credited predecessor/classical work retain priority.
